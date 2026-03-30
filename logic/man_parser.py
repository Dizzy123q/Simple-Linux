import subprocess
import re


def parse_query(query: str) -> dict:
    """
    Parsează input-ul utilizatorului.

    Exemple:
        "ls"      → {"command": "ls"}
        "ls -la"  → {"command": "ls", "params": ["-l", "-a"]}
    """
    query = query.strip()
    parts = query.split()
    command = parts[0]

    if len(parts) == 1:
        return {"command": command}

    # Cazul: "ls -la" sau "ls -l -a" — parametri
    params = []
    for part in parts[1:]:
        if part.startswith("-"):
            if part.startswith("--"):
                params.append(part)
            else:
                # -la → ["-l", "-a"]
                for char in part[1:]:
                    params.append(f"-{char}")
        else:
            return {"command": command, "error": f"Input invalid: '{part}'."}

    return {"command": command, "params": params}


def get_man_page(query: str) -> dict:
    parsed = parse_query(query)

    if "error" in parsed:
        return {"success": False, "error": parsed["error"]}

    command = parsed["command"]
    params = parsed.get("params")

    try:
        result = subprocess.run(
            ["man", command],
            env={"MANPAGER": "cat", "PATH": "/usr/bin:/bin:/usr/local/bin"},
            capture_output=True,
            text=True,
            timeout=5
        )
    except FileNotFoundError:
        return {"success": False, "error": "Comanda 'man' nu a fost găsită pe acest sistem."}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Timeout la căutarea manualului pentru '{command}'."}

    if result.returncode != 0:
        return {"success": False, "error": f"Nu există manual pentru '{command}'."}

    raw_text = result.stdout
    clean_text = re.sub(r'.\x08', '', raw_text)
    clean_text = re.sub(r'\x1b\[[0-9;]*m', '', clean_text)

    sections = parse_sections(clean_text)

    if not sections:
        return {"success": False, "error": f"Nu s-a putut parsa manualul pentru '{command}'."}

    if params:
        return filter_params(command, sections, params)

    return {"success": True, "command": command, "sections": sections}


def parse_sections(text: str) -> list:
    sections = []
    current_title = None
    current_lines = []

    for line in text.splitlines():
        if re.match(r'^[A-Z][A-Z0-9 _-]{1,}$', line.rstrip()):
            if current_title is not None:
                content = "\n".join(current_lines).strip()
                if content:
                    sections.append({"title": current_title, "content": content})
            current_title = line.strip()
            current_lines = []
        else:
            if current_title is not None:
                current_lines.append(line)

    if current_title is not None:
        content = "\n".join(current_lines).strip()
        if content:
            sections.append({"title": current_title, "content": content})

    return sections


def filter_params(command: str, sections: list, params: list) -> dict:
    options_section = None
    for title in ("OPTIONS", "DESCRIPTION"):
        for section in sections:
            if section["title"] == title:
                options_section = section
                break
        if options_section:
            break

    if not options_section:
        return {"success": False, "error": f"Nu există secțiunea OPTIONS pentru '{command}'."}

    blocks = parse_option_blocks(options_section["content"])

    found_sections = []
    not_found = []

    for param in params:
        matched_block = None
        for block in blocks:
            if param_matches_block(param, block["header"]):
                matched_block = block
                break

        if matched_block:
            found_sections.append({
                "title": matched_block["header"],
                "content": matched_block["body"]
            })
        else:
            not_found.append(param)

    if not found_sections:
        return {
            "success": False,
            "error": f"Parametrii {', '.join(params)} nu au fost găsiți în OPTIONS pentru '{command}'."
        }

    if not_found:
        found_sections.append({
            "title": "NEGĂSIȚI",
            "content": f"Parametrii următori nu au fost găsiți: {', '.join(not_found)}"
        })

    return {
        "success": True,
        "command": command,
        "sections": found_sections,
        "filtered_params": params
    }


def parse_option_blocks(options_text: str) -> list:
    blocks = []
    current_header = None
    current_body_lines = []

    for line in options_text.splitlines():
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        is_option_line = (
            indent <= 10
            and bool(re.match(r'-{1,2}\w', stripped))
        )

        if is_option_line:
            if current_header is not None:
                blocks.append({
                    "header": current_header,
                    "body": "\n".join(current_body_lines).strip()
                })
            current_header = stripped
            current_body_lines = []
        else:
            if current_header is not None:
                current_body_lines.append(stripped)

    if current_header is not None:
        blocks.append({
            "header": current_header,
            "body": "\n".join(current_body_lines).strip()
        })

    return blocks


def param_matches_block(param: str, header: str) -> bool:
    option_part = re.split(r'\s{2,}|\t', header)[0].strip()
    pattern = r'(^|(?<=,\s)|(?<=\s))' + re.escape(param) + r'(?=[,\s]|$)'
    return bool(re.search(pattern, option_part))


def format_output(man_data: dict) -> str:
    if not man_data["success"]:
        return f"EROARE: {man_data['error']}"

    lines = [f"MANUAL: {man_data['command'].upper()}", "=" * 50]

    for section in man_data["sections"]:
        lines.append(f"\n{section['title']}")
        lines.append("-" * len(section['title']))
        lines.append(section["content"])

    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "ls"
    result = get_man_page(query)
    print(format_output(result))
import subprocess


def get_all_services() -> list:
    """
    Returnează toate serviciile de pe sistem cu statusul lor.

    Returns:
        [{"name": str, "status": str}, ...]
        status poate fi: "active", "inactive", "failed"
    """
    try:
        # Obtinem toate unit files (pentru a avea si serviciile inactive)
        unit_files = subprocess.run(
            ["systemctl", "list-unit-files", "--type=service", "--no-pager", "--no-legend"],
            capture_output=True, text=True, timeout=10
        )

        # Obtinem serviciile care ruleaza acum (pentru status detaliat)
        units = subprocess.run(
            ["systemctl", "list-units", "--type=service", "--all", "--no-pager", "--no-legend"],
            capture_output=True, text=True, timeout=10
        )

    except FileNotFoundError:
        return []
    except subprocess.TimeoutExpired:
        return []

    # Parsam unit-files → {nume: enabled/disabled}
    unit_file_map = {}
    for line in unit_files.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 1:
            name = parts[0].replace(".service", "")
            unit_file_map[name] = parts[1] if len(parts) >= 2 else "unknown"

    # Parsam units → {nume: active/inactive/failed}
    unit_status_map = {}
    for line in units.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3:
            name = parts[0].replace(".service", "")
            active_state = parts[2]  # active/inactive/failed/activating
            unit_status_map[name] = active_state

    # Combinam rezultatele
    services = []
    for name in unit_file_map:
        status = unit_status_map.get(name, "inactive")
        services.append({"name": name, "status": status})

    # Sortam: active primul, apoi failed, apoi inactive
    order = {"active": 0, "failed": 1, "inactive": 2}
    services.sort(key=lambda s: (order.get(s["status"], 3), s["name"]))

    return services


def get_service_details(name: str) -> dict:
    """
    Returnează detalii despre un serviciu.

    Returns:
        {"success": True, "name": str, "description": str, "status": str, "pid": str, "log": str}
        {"success": False, "error": str}
    """
    try:
        result = subprocess.run(
            ["systemctl", "show", f"{name}.service",
             "--property=Description,ActiveState,SubState,MainPID,LoadState"],
            capture_output=True, text=True, timeout=5
        )
    except FileNotFoundError:
        return {"success": False, "error": "systemctl nu a fost găsit."}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout."}

    if result.returncode != 0:
        return {"success": False, "error": f"Nu s-au putut obține detalii pentru '{name}'."}

    props = {}
    for line in result.stdout.splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            props[key.strip()] = value.strip()

    status = props.get("ActiveState", "unknown")
    sub_state = props.get("SubState", "")
    full_status = f"{status} ({sub_state})" if sub_state else status

    return {
        "success": True,
        "name": name,
        "description": props.get("Description", "No description available."),
        "status": full_status,
        "pid": props.get("MainPID", "—"),
        "load_state": props.get("LoadState", "unknown"),
    }


def service_action(name: str, action: str) -> dict:
    """
    Execută o acțiune pe un serviciu (start/stop/restart).

    Returns:
        {"success": True}
        {"success": False, "error": str}
    """
    if action not in ("start", "stop", "restart"):
        return {"success": False, "error": f"Acțiune invalidă: '{action}'."}

    try:
        result = subprocess.run(
            ["systemctl", action, f"{name}.service"],
            capture_output=True, text=True, timeout=10
        )
    except FileNotFoundError:
        return {"success": False, "error": "systemctl nu a fost găsit."}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout la executarea comenzii."}

    if result.returncode != 0:
        error = result.stderr.strip()
        if "Interactive authentication required" in error or "access" in error.lower():
            return {"success": False, "error": f"Permisiuni insuficiente pentru '{action} {name}'."}
        return {"success": False, "error": error or f"Eroare la '{action} {name}'."}

    return {"success": True}
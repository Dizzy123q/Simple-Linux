from setuptools import setup, find_packages

setup(
    name="simple-linux",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["pywebview>=4.4.1"],
    entry_points={
        "console_scripts": [
            "simple-linux=main:main"  # ← modificat
        ]
    },
    python_requires=">=3.10",
)

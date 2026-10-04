import argparse
import json
import os
import platform
import shutil
import subprocess
import sys


TOOLS = ["git", "python", "pip", "gcc", "node", "npm"]


def get_tool_version(tool):
    path = shutil.which(tool)

    if not path:
        return {
            "installed": False,
            "path": None,
            "version": None
        }

    try:
        result = subprocess.run(
            [tool, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        output = (result.stdout or result.stderr).strip()
        first_line = output.splitlines()[0] if output else None

        return {
            "installed": True,
            "path": path,
            "version": first_line
        }

    except Exception:
        return {
            "installed": True,
            "path": path,
            "version": None
        }


def collect_diagnostics(min_free_gb=1.0):
    disk = shutil.disk_usage(os.getcwd())

    free_gb = disk.free / (1024 ** 3)
    total_gb = disk.total / (1024 ** 3)

    environment = {
        "PATH": os.environ.get("PATH"),
        "HOME": os.environ.get("HOME"),
        "SHELL": os.environ.get("SHELL"),
        "VIRTUAL_ENV": os.environ.get("VIRTUAL_ENV")
    }

    tools = {
        tool: get_tool_version(tool)
        for tool in TOOLS
    }

    return {
        "status": "PASS" if free_gb >= min_free_gb else "WARN",
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable
        },
        "disk": {
            "path": os.getcwd(),
            "total_gb": round(total_gb, 2),
            "free_gb": round(free_gb, 2),
            "minimum_required_gb": min_free_gb
        },
        "environment": environment,
        "developer_tools": tools
    }


def print_human_report(report):
    print("=== Packaged CLI Diagnostics Report ===")
    print(f"Status: {report['status']}")
    print()

    print("Python")
    print(f"  Version: {report['python']['version']}")
    print(f"  Implementation: {report['python']['implementation']}")
    print(f"  Executable: {report['python']['executable']}")
    print()

    print("Disk")
    print(f"  Path: {report['disk']['path']}")
    print(f"  Total: {report['disk']['total_gb']} GB")
    print(f"  Free: {report['disk']['free_gb']} GB")
    print()

    print("Environment Variables")
    for key, value in report["environment"].items():
        print(f"  {key}: {value if value else '<not set>'}")
    print()

    print("Developer Tools")
    for tool, info in report["developer_tools"].items():
        if info["installed"]:
            print(f"  {tool}: {info['version'] or 'installed'}")
        else:
            print(f"  {tool}: not found")


def main():
    parser = argparse.ArgumentParser(
        description="Packaged CLI system diagnostics tool"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output diagnostics as structured JSON"
    )

    parser.add_argument(
        "--min-free-gb",
        type=float,
        default=1.0,
        help="Minimum required free disk space in GB"
    )

    args = parser.parse_args()

    if args.min_free_gb < 0:
        print(
            "Error: --min-free-gb cannot be negative.",
            file=sys.stderr
        )
        return 2

    try:
        report = collect_diagnostics(args.min_free_gb)
    except Exception as exc:
        print(f"Diagnostic error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human_report(report)

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

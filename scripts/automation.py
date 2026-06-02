import subprocess
import sys
from pathlib import Path

SAFE_WORKFLOWS = [
    {
        "name": "Git status",
        "command": ["git", "status"],
        "description": "Read-only repository state check",
    },
    {
        "name": "Frontend lint",
        "command": ["npm", "run", "lint"],
        "description": "Frontend lint workflow",
    },
    {
        "name": "Frontend build",
        "command": ["npm", "run", "build"],
        "description": "Frontend build workflow",
    },
    {
        "name": "Frontend test",
        "command": ["npm", "test"],
        "description": "Frontend test workflow",
    },
    {
        "name": "Backend validation",
        "command": [sys.executable, "-m", "py_compile", "backend/backend/app.py"],
        "description": "Backend source validation by compiling Python code",
    },
]

UNSAFE_WORKFLOWS = [
    {
        "name": "Git push",
        "command": ["git", "push"],
        "reason": "Push operations modify remote history and require explicit approval.",
    },
    {
        "name": "Git push --force",
        "command": ["git", "push", "--force"],
        "reason": "Force pushing is destructive and unsafe without approval.",
    },
    {
        "name": "Git reset --hard",
        "command": ["git", "reset", "--hard"],
        "reason": "Resets local state and discards changes.",
    },
    {
        "name": "Git rebase",
        "command": ["git", "rebase"],
        "reason": "Rebasing history can alter commits and is unsafe without review.",
    },
    {
        "name": "Git clean -fd",
        "command": ["git", "clean", "-fd"],
        "reason": "Removes untracked files and directories.",
    },
    {
        "name": "Git stash drop",
        "command": ["git", "stash", "drop"],
        "reason": "Drops stashed changes permanently.",
    },
]

SKIPPED_WORKFLOWS = [
    {
        "name": "Dev server",
        "command": ["npm", "run", "dev"],
        "reason": "Long-running development server; skipped during synchronous automation.",
    },
    {
        "name": "Docker build",
        "command": ["docker", "build", ".", "-t", "cli-agent-poc-test"],
        "reason": "Docker validation is optional and may require Docker daemon availability.",
    },
]


def run_command(command, cwd=None):
    try:
        print(f"Running: {' '.join(command)}")

        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )

        print(f"Exit code: {result.returncode}")

        if result.stdout:
            print("stdout:")
            print(result.stdout.strip())

        if result.stderr:
            print("stderr:")
            print(result.stderr.strip())

        return result

    except FileNotFoundError:
        print(f"Command not found: {command[0]}")
        raise


def main():
    root = Path(__file__).resolve().parents[1]
    failed = []

    print("Starting synchronous CLI automation")
    print(f"Repository root: {root}")

    print("\nDetected unsafe workflows (not executed):")

    for workflow in UNSAFE_WORKFLOWS:
        print(
            f"- {workflow['name']}: {workflow['reason']}"
        )

    for workflow in SAFE_WORKFLOWS:
        print(f"\n---")
        print(f"Executing workflow: {workflow['name']}")

        try:
            result = run_command(
                workflow["command"],
                cwd=root,
            )

            if result.returncode != 0:
                failed.append(
                    (
                        workflow["name"],
                        result.returncode,
                        result.stderr.strip(),
                    )
                )

        except Exception as e:
            failed.append(
                (
                    workflow["name"],
                    "ERROR",
                    str(e),
                )
            )

    if SKIPPED_WORKFLOWS:
        print("\n---")
        print("Detected workflows skipped for synchronous automation:")

        for workflow in SKIPPED_WORKFLOWS:
            print(
                f"- {workflow['name']}: {workflow['reason']}"
            )

    if failed:
        print("\nAutomation completed with failures:")

        for name, code, error in failed:
            print(f"\n* Workflow: {name}")
            print(f"  Exit Code: {code}")

            if error:
                print(f"  Error: {error}")

        sys.exit(1)

    print("\nSynchronous automation completed successfully.")


if __name__ == "__main__":
    main()
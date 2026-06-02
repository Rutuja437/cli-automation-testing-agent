import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INDEPENDENT_WORKFLOWS = [
    {
        "name": "Git status",
        "command": ["git", "status"],
        "description": "Read-only repository state check",
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

DEPENDENT_WORKFLOWS = [
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
]

SKIPPED_WORKFLOWS = [
    {
        "name": "Dev server",
        "command": ["npm", "run", "dev"],
        "reason": "Long-running development server; skipped in async validation.",
    },
]


def format_command(command):
    return " ".join(command)


async def run_command_async(command, cwd=None, timeout=120):
    print(f"\nStarting async command: {format_command(command)}")

    process = await asyncio.create_subprocess_exec(
        *command,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        await asyncio.wait_for(process.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        print(f"Timeout reached for: {format_command(command)}")
        process.terminate()
        await process.wait()
        raise TimeoutError(f"Command timed out: {format_command(command)}")

    stdout, stderr = await process.communicate()

    stdout_text = stdout.decode().strip()
    stderr_text = stderr.decode().strip()

    print(f"Completed async command: {format_command(command)}")
    print(f"Exit code: {process.returncode}")

    if stdout_text:
        print("stdout:")
        print(stdout_text)

    if stderr_text:
        print("stderr:")
        print(stderr_text)

    return {
        "command": command,
        "returncode": process.returncode,
        "stdout": stdout_text,
        "stderr": stderr_text,
    }


async def run_dependent_workflows(root):
    failures = []

    print("\nRunning dependent workflows sequentially...")

    for workflow in DEPENDENT_WORKFLOWS:
        result = await run_command_async(workflow["command"], cwd=root)

        if result["returncode"] != 0:
            failures.append(
                (
                    workflow["name"],
                    result["returncode"],
                    result["stderr"],
                )
            )

    return failures


async def main():
    print("Starting asynchronous CLI automation")
    print(f"Repository root: {ROOT}")

    print("\nDetected unsafe workflows (not executed):")

    for workflow in UNSAFE_WORKFLOWS:
        print(
            f"- {workflow['name']} : {workflow['reason']}"
        )

    print("\nRunning independent workflows in parallel...")

    independent_tasks = [
        run_command_async(workflow["command"], cwd=ROOT)
        for workflow in INDEPENDENT_WORKFLOWS
    ]

    independent_results = await asyncio.gather(
        *independent_tasks,
        return_exceptions=True,
    )

    failed = []

    for workflow, result in zip(
        INDEPENDENT_WORKFLOWS,
        independent_results,
    ):
        if isinstance(result, Exception):
            failed.append(
                (
                    workflow["name"],
                    str(result),
                )
            )
        elif result["returncode"] != 0:
            failed.append(
                (
                    workflow["name"],
                    result["returncode"],
                )
            )

    dependent_failures = await run_dependent_workflows(ROOT)
    failed.extend(dependent_failures)

    if SKIPPED_WORKFLOWS:
        print("\nDetected workflows skipped for asynchronous automation:")

        for workflow in SKIPPED_WORKFLOWS:
            print(
                f"- {workflow['name']} : {workflow['reason']}"
            )

    if failed:
        print("\nFailure Summary:")

        for item in failed:
            print(f"* {item[0]} failed: {item[1]}")

        sys.exit(1)

    print("\nAsynchronous automation completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
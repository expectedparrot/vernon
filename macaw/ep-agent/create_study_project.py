#!/usr/bin/env python3
"""Create a study project directory structure."""

import argparse
import os
import subprocess


DIRS = [
    "refs",
    "data/raw",
    "data/cooked",
    "data/uploaded",
    "edsl_jobs",
    "analysis",
    "computed_objects",
    "writeup/tables",
    "writeup/plots",
    "writeup/numbers",
]

GITKEEPS = [
    "data/raw/.gitkeep",
    "data/cooked/.gitkeep",
    "data/uploaded/.gitkeep",
]

FILES = {
    "README.md": "",
    "requirements.txt": "",
    "Makefile": "",
    "Dockerfile": "",
    "writeup/planning.md": "",
    "writeup/report.md": "",
    "writeup/appendix.md": "",
}

JOB_FILES = [
    "study_agent_list.py",
    "study_scenario_list.py",
    "study_model_list.py",
    "run_job.py",
]


def create_project(root: str, jobs: list[str] | None = None):
    if jobs is None:
        jobs = ["job_a"]

    os.makedirs(root, exist_ok=True)

    for d in DIRS:
        os.makedirs(os.path.join(root, d), exist_ok=True)

    for path in GITKEEPS:
        open(os.path.join(root, path), "a").close()

    for path, content in FILES.items():
        full = os.path.join(root, path)
        if not os.path.exists(full):
            with open(full, "w") as f:
                f.write(content)

    for job in jobs:
        job_dir = os.path.join(root, "edsl_jobs", job)
        os.makedirs(job_dir, exist_ok=True)
        for fname in JOB_FILES:
            full = os.path.join(job_dir, fname)
            if not os.path.exists(full):
                with open(full, "w") as f:
                    f.write("")

    # Copy EP stylesheet into writeup/
    try:
        from create_css import create_css
        create_css(os.path.join(root, "writeup"))
    except Exception:
        pass  # CSS is optional

    subprocess.run(["git", "init"], cwd=root, check=True)
    print(f"Created study project at: {root}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a study project structure.")
    parser.add_argument("name", help="Project directory name")
    parser.add_argument(
        "--jobs",
        nargs="+",
        default=["job_a"],
        help="Names of edsl_jobs to create (default: job_a)",
    )
    args = parser.parse_args()
    create_project(args.name, args.jobs)

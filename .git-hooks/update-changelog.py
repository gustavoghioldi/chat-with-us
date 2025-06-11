#!/usr/bin/env python3
"""
Pre-commit hook to automatically update CHANGELOG.md with commit messages.
"""
import os
import sys
from datetime import datetime


def get_staged_files():
    """Get a list of staged files from git."""
    import subprocess

    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True
    )
    return result.stdout.strip().split("\n")


def get_commit_message():
    """Get the commit message from the COMMIT_EDITMSG file."""
    commit_msg_file = os.path.join(".git", "COMMIT_EDITMSG")
    if os.path.exists(commit_msg_file):
        with open(commit_msg_file, "r") as f:
            return f.read().strip()
    return None


def update_changelog(commit_msg, changed_files):
    """Update the CHANGELOG.md file with the new commit information."""
    if not commit_msg or commit_msg.startswith("Merge"):
        return

    changelog_path = "CHANGELOG.md"

    # Read existing changelog
    try:
        with open(changelog_path, "r") as f:
            content = f.readlines()
    except FileNotFoundError:
        content = [
            "# Changelog\n",
            "\n",
            "All notable changes to this project will be documented in this file.\n",
            "\n",
            "## [Unreleased]\n",
            "\n",
        ]

    # Find the [Unreleased] section
    unreleased_index = -1
    for i, line in enumerate(content):
        if line.strip() == "## [Unreleased]":
            unreleased_index = i
            break

    if unreleased_index == -1:
        # If no [Unreleased] section exists, create it
        content.append("## [Unreleased]\n\n")
        unreleased_index = len(content) - 2

    # Format the new entry
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = f"\n### {date_str}\n"
    new_entry += f"- {commit_msg}\n"
    if changed_files:
        new_entry += "  Changed files:\n"
        for file in changed_files:
            if file:  # Only add non-empty file paths
                new_entry += f"  - {file}\n"
    new_entry += "\n"

    # Insert the new entry after the [Unreleased] section
    content.insert(unreleased_index + 1, new_entry)

    # Write back to the file
    with open(changelog_path, "w") as f:
        f.writelines(content)


def main():
    """Main function to run the changelog updater."""
    commit_msg = get_commit_message()
    if not commit_msg:
        print("No commit message found")
        return 1

    changed_files = get_staged_files()
    update_changelog(commit_msg, changed_files)

    # Stage the updated CHANGELOG.md
    os.system("git add CHANGELOG.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())

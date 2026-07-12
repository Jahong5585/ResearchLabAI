from pathlib import Path


WORKSPACE_DIR = Path("Workspaces")


def create_workspace(name: str):

    workspace = WORKSPACE_DIR / name

    folders = [
        "literature",
        "drafts",
        "data",
        "images",
        "exports",
        "logs"
    ]

    workspace.mkdir(parents=True, exist_ok=True)

    for folder in folders:
        (workspace / folder).mkdir(exist_ok=True)

    return workspace
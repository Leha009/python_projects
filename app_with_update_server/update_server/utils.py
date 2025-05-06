import os

UPDATE_DIR = "updates"
UPDATE_FILE_EXT = ".tar.gz"

def compare_version(version1: str, version2: str) -> int:
    if not version1.strip():
        return -1
    if not version2.strip():
        return 1

    v1 = list(map(int, version1.split('.')))
    v2 = list(map(int, version2.split('.')))

    while len(v1) < len(v2):
        v1.append(0)
    while len(v2) < len(v1):
        v2.append(0)

    for a, b in zip(v1, v2):
        if a < b:
            return -1
        if a > b:
            return 1

    return 0

def get_higher_version(version1: str, version2: str) -> str:
    cmp = compare_version(version1, version2)
    if cmp > 0:
        return version1

    return version2

def get_app_file_version_path(app: str, version: str) -> str | None:
    file_path = f"{UPDATE_DIR}/{app}/{version}{UPDATE_FILE_EXT}"
    if not os.path.exists(file_path):
        return None

    return file_path

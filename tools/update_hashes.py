"""Regenerate database-hashes.json, the file TCC downloads to decide which data files to update.

On every start TCC hashes its local copy of each data file and re-downloads the ones whose
SHA-256 differs from the entry in this file. Files without an entry are never updated, so run
this after every data change and commit the result together with the data.

Usage: python tools/update_hashes.py [--check]
  --check  only report what would change, exit 1 if the hash file is out of date
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HASH_FILE = REPO / "database-hashes.json"

# Data TCC reads. ShinraMeter also uses some of these, but bundles them in its build instead of
# downloading them, so it doesn't need hashes.
ROOT_FILES = ["default-dungeon-defs.tsv", "section_images.tsv", "servers.txt"]
FOLDERS = [
    "acc_benefits", "achi_grade", "achievements", "dungeons", "equip_exp", "guild_quests",
    "hotdot", "items", "monsters", "quests", "regions", "skills", "social", "sys_msg", "world_map",
]


# .gitattributes stores these with LF endings, and TCC hashes the files as GitHub serves them,
# so hash the LF version even if the working copy has CRLF (e.g. freshly extracted data).
LF_EXTENSIONS = {".tsv", ".xml", ".txt", ".map"}


def file_hash(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix in LF_EXTENSIONS:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def compute() -> dict[str, str]:
    hashes = {}
    for name in ROOT_FILES:
        hashes[name] = file_hash(REPO / name)
    for folder in FOLDERS:
        for path in sorted((REPO / folder).rglob("*")):
            if path.is_file():
                hashes[path.relative_to(REPO).as_posix()] = file_hash(path)
    return hashes


def serialize(hashes: dict[str, str]) -> bytes:
    # Same layout as the file TCC's repo used to ship (2-space indent, CRLF, no trailing newline).
    return json.dumps(hashes, indent=2).replace("\n", "\r\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    new = compute()
    old = json.loads(HASH_FILE.read_text("utf-8-sig")) if HASH_FILE.exists() else {}

    added = sorted(new.keys() - old.keys())
    removed = sorted(old.keys() - new.keys())
    changed = sorted(k for k in new.keys() & old.keys() if new[k] != old[k])
    for label, keys in (("added", added), ("removed", removed), ("changed", changed)):
        for key in keys:
            print(f"{label}: {key}")

    if not (added or removed or changed) and HASH_FILE.exists() and HASH_FILE.read_bytes() == serialize(new):
        print("database-hashes.json is up to date")
        return 0
    if args.check:
        return 1

    HASH_FILE.write_bytes(serialize(new))
    print(f"wrote {HASH_FILE.name} ({len(new)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

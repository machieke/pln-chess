"""Prepare a lossless Cycle 14 release and rewrite only its unpublished commits.

This host-only tool creates a new branch. It never changes the checked-out branch,
deletes evidence, rewrites the published baseline, or makes a remote write.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile

from scripts.cycle14_evidence import sha256


START = "54353579e7921f9b47f43bbde1aa61cb887bc6e4"
ORIGINAL = "4a603722a73f9f0280e5034186ee4dc26b0f1bbc"
PREFIX = "artifacts/cycle14/"
LIMIT = 1024**3 - 1024**2


def git(*args, input=None, env=None):
    return subprocess.check_output(["git", *args], input=input, env=env)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def entries(commit):
    result = {}
    for record in git("ls-tree", "-r", "-z", "-l", commit, "--", PREFIX).split(b"\0"):
        if not record:
            continue
        metadata, path = record.split(b"\t", 1)
        mode, kind, blob, size = metadata.decode().split()
        if kind != "blob" or mode not in ("100644", "100755"):
            raise ValueError("Only regular evidence files may be packaged")
        result[path.decode()] = {"blob": blob, "bytes": int(size), "mode": int(mode[-3:], 8)}
    return result


def bulk(path, row):
    if "/model/" in path or path.startswith(PREFIX + "delivery/"):
        return False
    if "/learning/" in path and Path(path).name in {"model.json", "ledger.json", "checkpoint.json"}:
        return False
    return row["bytes"] > 32768 or Path(path).suffix in {".xz", ".gz", ".mp4", ".webm", ".png", ".zip"}


def prepare(root, workspace):
    root, workspace = root.resolve(), workspace.resolve()
    assets_dir = workspace / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    commits = git("rev-list", "--reverse", START + ".." + ORIGINAL).decode().splitlines()
    if len(commits) != 60 or git("rev-parse", "refs/archive/cycle14-original-20261116").decode().strip() != ORIGINAL:
        raise ValueError("Original history backup ref or expected range is missing")
    trees = {commit: entries(commit) for commit in commits}
    external = {path for tree in trees.values() for path, row in tree.items() if bulk(path, row)}
    files, objects = [], {}
    for i, (path, row) in enumerate(sorted(trees[ORIGINAL].items()), 1):
        source = root / path
        # Bind every current byte to the original Git snapshot, including its mode.
        digest = hashlib.sha256()
        blob = hashlib.sha1(f"blob {row['bytes']}\0".encode())
        if source.is_symlink() or source.stat().st_size != row["bytes"]:
            raise ValueError(f"Evidence changed since original delivery: {path}")
        with source.open("rb") as stream:
            while data := stream.read(1024 * 1024):
                digest.update(data); blob.update(data)
        if blob.hexdigest() != row["blob"]:
            raise ValueError(f"Evidence changed since original delivery: {path}")
        item = {"path": path, "bytes": row["bytes"], "mode": row["mode"],
                "sha256": digest.hexdigest(), "git_blob": row["blob"],
                "storage": "release" if path in external else "git"}
        files.append(item)
        if path in external:
            objects.setdefault(item["sha256"], item)
        if i % 1000 == 0:
            print(f"Hashed {i}/{len(trees[ORIGINAL])} original evidence files", flush=True)
    batches, batch, size = [], [], 0
    for digest, item in sorted(objects.items()):
        cost = 1024 + ((item["bytes"] + 511) // 512) * 512
        if size + cost > LIMIT and batch:
            batches.append(batch); batch, size = [], 0
        batch.append((digest, item)); size += cost
    if batch:
        batches.append(batch)
    assets, locations = [], {}
    for number, batch in enumerate(batches, 1):
        name = f"cycle14-evidence-{number:03}.tar"
        target = assets_dir / name
        if target.exists():
            raise FileExistsError(f"Refusing to overwrite a release pack: {target}")
        with tarfile.open(target, "w:", format=tarfile.USTAR_FORMAT) as archive:
            for digest, item in batch:
                info = tarfile.TarInfo("objects/" + digest)
                info.size = item["bytes"]; info.mode = 0o644; info.mtime = 0
                with (root / item["path"]).open("rb") as stream:
                    archive.addfile(info, stream)
                locations[digest] = name
        assert target.stat().st_size < 1024**3
        assets.append({"name": name, "bytes": target.stat().st_size, "sha256": sha256(target),
                       "objects": len(batch)})
        print(f"Packaged {name}: {target.stat().st_size / 2**20:.1f} MiB", flush=True)
    for item in files:
        if item["storage"] == "release":
            item["asset"] = locations[item["sha256"]]
    manifest = {"schema": "pln-chess-cycle14-release-v1", "repository": "machieke/pln-chess",
                "release_tag": "cycle14-evidence-v1", "original_commit": ORIGINAL,
                "published_baseline": START,
                "download_base_url": "https://github.com/machieke/pln-chess/releases/download/cycle14-evidence-v1",
                "files": files, "assets": assets,
                "selection": "Externalize compressed/media files and records exceeding 32 KiB in any unpublished Cycle 14 commit; retain model checkpoints, delivery manifests and named model/ledger files.",
                "counts": {"files": len(files), "bytes": sum(x["bytes"] for x in files),
                           "git_files": sum(x["storage"] == "git" for x in files),
                           "git_bytes": sum(x["bytes"] for x in files if x["storage"] == "git"),
                           "release_files": sum(x["storage"] == "release" for x in files),
                           "release_unique_objects": len(objects),
                           "release_asset_bytes": sum(x["bytes"] for x in assets)}}
    write_json(workspace / "manifest.json", manifest)
    write_json(workspace / "external-paths.json", sorted(external))
    # Rewrite trees in an isolated index, preserving metadata/messages and all other files.
    index = workspace / "rewrite.index"
    index.unlink(missing_ok=True)
    env = {**os.environ, "GIT_INDEX_FILE": str(index)}
    mapping = {}
    for commit in commits:
        git("read-tree", commit, env=env)
        git("update-index", "--force-remove", "-z", "--stdin",
            input=b"\0".join(p.encode() for p in sorted(external)) + b"\0", env=env)
        tree = git("write-tree", env=env).decode().strip()
        original = git("cat-file", "commit", commit)
        headers, message = original.split(b"\n\n", 1)
        if b"\ngpgsig " in headers or b"\nmergetag " in headers:
            raise ValueError("Signed commit requires explicit signature migration")
        lines = []
        for line in headers.splitlines():
            if line.startswith(b"tree "):
                line = b"tree " + tree.encode()
            elif line.startswith(b"parent "):
                parent = line[7:].decode()
                line = b"parent " + mapping.get(parent, parent).encode()
            lines.append(line)
        rewritten = git("hash-object", "-t", "commit", "-w", "--stdin",
                        input=b"\n".join(lines) + b"\n\n" + message).decode().strip()
        changes = git("diff-tree", "--no-commit-id", "--name-status", "-r", commit, rewritten).decode().splitlines()
        if any(not line.startswith("D\t") or line[2:] not in external for line in changes):
            raise ValueError(f"Unexpected migration change in {commit}")
        mapping[commit] = rewritten
    git("update-ref", "refs/heads/cycle14-publication", mapping[ORIGINAL])
    write_json(workspace / "commit-map.json", {"schema": "cycle14-publication-commit-map-v1",
               "baseline_unchanged": START, "original_head": ORIGINAL,
               "rewritten_head": mapping[ORIGINAL], "commits": mapping,
               "verification": "Every mapped commit preserves metadata, message and all tree entries except the explicitly externalized Cycle 14 paths. No scientific bytes were transformed."})
    print(json.dumps({"rewritten_head": mapping[ORIGINAL], **manifest["counts"]}, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    prepare(args.root, args.workspace)

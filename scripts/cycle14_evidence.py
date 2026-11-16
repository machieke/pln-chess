"""Restore frozen Cycle 14 evidence from checksummed release packs (stdlib only)."""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "publication/cycle14/manifest.json"
CHUNK = 1024 * 1024


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def safe_path(root, relative):
    name = PurePosixPath(relative)
    if (not relative or name.is_absolute() or ".." in name.parts
            or str(name) != relative or "\\" in relative
            or not relative.startswith("artifacts/cycle14/")):
        raise ValueError(f"Invalid evidence path: {relative!r}")
    root = Path(root).resolve()
    target = root.joinpath(*name.parts)
    for parent in [target, *target.parents]:
        if parent == root:
            break
        if parent.is_symlink():
            raise ValueError(f"Symlink in evidence path: {relative}")
    return target


def load_manifest(path):
    data = json.loads(Path(path).read_text())
    if data.get("schema") != "pln-chess-cycle14-release-v1":
        raise ValueError("Unsupported evidence manifest")
    assets = {}
    for asset in data["assets"]:
        name = asset["name"]
        if Path(name).name != name or not name.endswith(".tar") or name in assets:
            raise ValueError("Invalid or duplicate asset name")
        assets[name] = asset
    names = set()
    for item in data["files"]:
        safe_path(Path(tempfile.gettempdir()) / "c14-manifest-validation", item["path"])
        if item["path"] in names:
            raise ValueError("Duplicate evidence path")
        names.add(item["path"])
        digest = item["sha256"]
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Invalid evidence digest")
        if not isinstance(item["bytes"], int) or item["bytes"] < 0:
            raise ValueError("Invalid evidence size")
        if item["storage"] not in ("git", "release"):
            raise ValueError("Invalid evidence storage")
        if item["storage"] == "release" and item["asset"] not in assets:
            raise ValueError("Unknown evidence asset")
    return data


def matches(path, item):
    return path.is_file() and path.stat().st_size == item["bytes"] and sha256(path) == item["sha256"]


def verify(root, manifest):
    missing, changed = [], []
    for item in manifest["files"]:
        path = safe_path(root, item["path"])
        if not path.exists():
            missing.append(item["path"])
        elif not matches(path, item):
            changed.append(item["path"])
    return {"passed": not missing and not changed, "files": len(manifest["files"]),
            "missing": missing, "changed": changed}


def install(stream, target, item):
    """Validate a new file before publishing it; never overwrite different evidence."""
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".cycle14-", dir=target.parent)
    temporary = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as out:
            shutil.copyfileobj(stream, out, CHUNK)
        if not matches(temporary, item):
            raise ValueError(f"Evidence content mismatch: {item['path']}")
        os.chmod(temporary, item.get("mode", 0o644))
        try:
            os.link(temporary, target)
        except FileExistsError:
            if target.is_symlink() or not matches(target, item):
                raise ValueError(f"Refusing to replace existing evidence: {item['path']}")
    finally:
        temporary.unlink(missing_ok=True)


def restore_pack(pack, asset, items, root):
    if not matches(pack, asset):
        raise ValueError(f"Release pack checksum mismatch: {asset['name']}")
    by_digest = defaultdict(list)
    for item in items:
        by_digest[item["sha256"]].append(item)
    seen = set()
    with tarfile.open(pack, "r:") as archive:
        for member in archive:
            digest = member.name.removeprefix("objects/")
            if (member.name != "objects/" + digest or digest not in by_digest
                    or digest in seen or not member.isfile()
                    or any(member.size != row["bytes"] for row in by_digest[digest])):
                raise ValueError(f"Unexpected archive member: {member.name}")
            seen.add(digest)
            for item in by_digest[digest]:
                target = safe_path(root, item["path"])
                if target.exists():
                    if not matches(target, item):
                        raise ValueError(f"Refusing to replace existing evidence: {item['path']}")
                    continue
                source = archive.extractfile(member)
                if source is None:
                    raise ValueError("Missing archive payload")
                with source:
                    install(source, target, item)
    if seen != set(by_digest):
        raise ValueError("Incomplete release pack")


def download(asset, base_url, cache):
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / asset["name"]
    if target.exists():
        if not matches(target, asset):
            raise ValueError(f"Corrupt cached pack; remove it before retrying: {target}")
        return target
    fd, temporary = tempfile.mkstemp(prefix=asset["name"] + ".", suffix=".partial", dir=cache)
    try:
        request = urllib.request.Request(base_url.rstrip("/") + "/" + asset["name"],
                                         headers={"User-Agent": "pln-chess-cycle14-evidence"})
        with os.fdopen(fd, "wb") as out, urllib.request.urlopen(request, timeout=120) as response:
            shutil.copyfileobj(response, out, CHUNK)
        if not matches(Path(temporary), asset):
            raise ValueError(f"Downloaded pack checksum mismatch: {asset['name']}")
        os.replace(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return target


def fetch(root, manifest, *, asset_dir=None, cache=None, base_url=None):
    groups = defaultdict(list)
    # Check every existing file first, including files retained in Git.
    for item in manifest["files"]:
        path = safe_path(root, item["path"])
        if path.exists() and not matches(path, item):
            raise ValueError(f"Refusing to replace existing evidence: {item['path']}")
        if item["storage"] == "git":
            if not path.exists():
                raise ValueError(f"Missing Git-tracked evidence; restore the checkout: {item['path']}")
        else:
            groups[item["asset"]].append(item)
    cache = Path(cache or Path.home() / ".cache/pln-chess/cycle14-evidence-v1")
    for asset in manifest["assets"]:
        items = groups[asset["name"]]
        if all(safe_path(root, item["path"]).exists() for item in items):
            continue
        print(f"Restoring {asset['name']} ({asset['bytes'] / 2**20:.1f} MiB)", flush=True)
        pack = (Path(asset_dir) / asset["name"] if asset_dir else
                download(asset, base_url or manifest["download_base_url"], cache))
        restore_pack(pack, asset, items, root)
    result = verify(root, manifest)
    if not result["passed"]:
        raise ValueError(f"Incomplete evidence restoration: {result}")
    return result


def restore_history(root, manifest_path, *, asset_dir=None, cache=None):
    """Restore original source-bound commits without checking them out."""
    manifest = json.loads(Path(manifest_path).read_text())
    if manifest.get("schema") != "cycle14-original-history-v1":
        raise ValueError("Unsupported history manifest")
    root = Path(root).resolve()
    cache = Path(cache or Path.home() / ".cache/pln-chess/cycle14-evidence-v1")
    cache.mkdir(parents=True, exist_ok=True)
    for item in manifest["parts"]:
        if Path(item["name"]).name != item["name"]:
            raise ValueError("Invalid history part name")
    bundle = cache / "cycle14-original.bundle"
    if bundle.exists() and not matches(bundle, manifest["bundle"]):
        raise ValueError("Existing original-history bundle has a different checksum")
    if not bundle.exists():
        fd, temporary = tempfile.mkstemp(prefix="history-", suffix=".partial", dir=cache)
        try:
            with os.fdopen(fd, "wb") as out:
                for part in manifest["parts"]:
                    print(f"Reading {part['name']}", flush=True)
                    source = (Path(asset_dir) / part["name"] if asset_dir else
                              download(part, manifest["download_base_url"], cache))
                    if not matches(source, part):
                        raise ValueError(f"History part checksum mismatch: {part['name']}")
                    with source.open("rb") as stream:
                        shutil.copyfileobj(stream, out, CHUNK)
            if not matches(Path(temporary), manifest["bundle"]):
                raise ValueError("Original-history bundle checksum mismatch")
            os.replace(temporary, bundle)
        finally:
            Path(temporary).unlink(missing_ok=True)
    subprocess.run(["git", "bundle", "verify", str(bundle)], cwd=root, check=True)
    ref = "refs/archive/cycle14-original-20261116"
    result = subprocess.run(["git", "rev-parse", "--verify", ref], cwd=root, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip() != manifest["original_head"]:
        raise ValueError("Refusing to replace a different original-history archive ref")
    subprocess.run(["git", "-c", "gc.auto=0", "fetch", "--no-tags", str(bundle), f"{ref}:{ref}"],
                   cwd=root, check=True)
    actual = subprocess.check_output(["git", "rev-parse", ref], cwd=root, text=True).strip()
    if actual != manifest["original_head"]:
        raise ValueError("Restored original-history head differs")
    return {"passed": True, "original_head": actual, "archive_ref": ref,
            "bundle_sha256": manifest["bundle"]["sha256"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("fetch", "verify", "history"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--asset-dir", type=Path, help="Use previously downloaded packs without network access")
    parser.add_argument("--cache", type=Path, help="Pack cache; defaults to ~/.cache/pln-chess/cycle14-evidence-v1")
    parser.add_argument("--receipt", type=Path, help="Write a separate verification receipt")
    args = parser.parse_args()
    if args.command == "history":
        result = restore_history(args.root, args.manifest.parent / "original-history.json",
                                 asset_dir=args.asset_dir, cache=args.cache)
    else:
        manifest = load_manifest(args.manifest)
        result = (fetch(args.root, manifest, asset_dir=args.asset_dir, cache=args.cache)
                  if args.command == "fetch" else verify(args.root, manifest))
    print(json.dumps(result, indent=2))
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(result, indent=2) + "\n")
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

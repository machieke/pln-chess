"""Publication transport controls; frozen scientific tests remain separate."""
import hashlib
import io
import json
from pathlib import Path
import tarfile
import subprocess
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest

from scripts.cycle14_evidence import fetch, load_manifest, restore_history, restore_pack, sha256, verify


def fixture(tmp_path, payload=b"native evidence\x00\xff\n", *, member_name=None, member_type=None):
    assets = tmp_path / "assets"; assets.mkdir()
    root = tmp_path / "checkout"; root.mkdir()
    digest = hashlib.sha256(payload).hexdigest()
    pack = assets / "cycle14-evidence-001.tar"
    with tarfile.open(pack, "w:") as archive:
        info = tarfile.TarInfo(member_name or "objects/" + digest)
        info.size = len(payload)
        if member_type:
            info.type = member_type; info.linkname = "/tmp/escape"
        archive.addfile(info, io.BytesIO(payload))
    asset = dict(name=pack.name, bytes=pack.stat().st_size, sha256=sha256(pack))
    files = [dict(path=f"artifacts/cycle14/{name}", bytes=len(payload), sha256=digest,
                  storage="release", asset=pack.name, mode=0o644)
             for name in ("original.bin", "reproduction.bin")]
    manifest = dict(schema="pln-chess-cycle14-release-v1", assets=[asset], files=files)
    path = tmp_path / "manifest.json"; path.write_text(json.dumps(manifest))
    return root, assets, pack, asset, files, path


def test_exact_shared_payload_restore_and_idempotent_retry(tmp_path):
    root, assets, _, _, files, path = fixture(tmp_path)
    manifest = load_manifest(path)
    assert fetch(root, manifest, asset_dir=assets)["passed"]
    before = [(root / row["path"]).stat().st_mtime_ns for row in files]
    assert fetch(root, manifest, asset_dir=assets)["passed"]
    assert before == [(root / row["path"]).stat().st_mtime_ns for row in files]
    assert verify(root, manifest) == dict(passed=True, files=2, missing=[], changed=[])


def test_corrupt_pack_rejected_before_restoration(tmp_path):
    root, _, pack, asset, files, _ = fixture(tmp_path)
    with pack.open("r+b") as stream:
        stream.seek(700); stream.write(b"corruption")
    with pytest.raises(ValueError, match="pack checksum"):
        restore_pack(pack, asset, files, root)
    assert not (root / "artifacts").exists()


def test_individual_hash_checked_even_when_pack_hash_matches(tmp_path):
    root, _, pack, asset, files, _ = fixture(tmp_path)
    with pack.open("r+b") as stream:
        stream.seek(512); stream.write(b"WRONG")
    asset["sha256"] = sha256(pack)
    with pytest.raises(ValueError, match="content mismatch"):
        restore_pack(pack, asset, files, root)
    assert not (root / files[0]["path"]).exists()
    assert not list(root.rglob(".cycle14-*"))


def test_existing_different_evidence_is_never_replaced(tmp_path):
    root, assets, _, _, files, path = fixture(tmp_path)
    target = root / files[1]["path"]; target.parent.mkdir(parents=True)
    target.write_bytes(b"user-owned different evidence")
    with pytest.raises(ValueError, match="Refusing to replace"):
        fetch(root, load_manifest(path), asset_dir=assets)
    assert target.read_bytes() == b"user-owned different evidence"
    assert not (root / files[0]["path"]).exists()


@pytest.mark.parametrize("name", ["../escape", "/tmp/escape", "objects/unknown"])
def test_unlisted_and_traversing_archive_members_rejected(tmp_path, name):
    root, _, pack, asset, files, _ = fixture(tmp_path, member_name=name)
    with pytest.raises(ValueError, match="Unexpected archive member"):
        restore_pack(pack, asset, files, root)
    assert not (root / "artifacts").exists()


def test_archive_symlink_rejected(tmp_path):
    root, _, pack, asset, files, _ = fixture(tmp_path, member_type=tarfile.SYMTYPE)
    with pytest.raises(ValueError, match="Unexpected archive member"):
        restore_pack(pack, asset, files, root)


def test_existing_parent_symlink_rejected(tmp_path):
    root, assets, _, _, _, path = fixture(tmp_path)
    outside = tmp_path / "outside"; outside.mkdir()
    (root / "artifacts").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="Symlink"):
        fetch(root, load_manifest(path), asset_dir=assets)
    assert not list(outside.iterdir())


@pytest.mark.parametrize("name", ["artifacts/cycle14/../../escape", "/tmp/escape", "src/changed.py"])
def test_manifest_paths_confined_to_cycle14(tmp_path, name):
    _, _, _, _, _, path = fixture(tmp_path)
    manifest = json.loads(path.read_text()); manifest["files"][0]["path"] = name
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="Invalid evidence path"):
        load_manifest(path)


def test_incomplete_pack_rejected(tmp_path):
    root, _, pack, asset, files, _ = fixture(tmp_path)
    missing = {**files[0], "path": "artifacts/cycle14/missing.bin", "sha256": "0" * 64}
    with pytest.raises(ValueError, match="Incomplete release pack"):
        restore_pack(pack, asset, files + [missing], root)


def test_missing_git_record_requires_checkout_repair(tmp_path):
    root, assets, _, _, _, path = fixture(tmp_path)
    manifest = load_manifest(path)
    manifest["files"].append(dict(path="artifacts/cycle14/summary.json", bytes=2,
                                   sha256=hashlib.sha256(b"{}").hexdigest(), storage="git"))
    with pytest.raises(ValueError, match="Missing Git-tracked"):
        fetch(root, manifest, asset_dir=assets)
    assert not (root / "artifacts").exists()


def test_http_download_checksums_and_reuses_verified_cache(tmp_path):
    root, assets, _, _, files, path = fixture(tmp_path)

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(assets), **kwargs)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True); thread.start()
    manifest = load_manifest(path); cache = tmp_path / "cache"
    try:
        assert fetch(root, manifest, cache=cache,
                     base_url=f"http://127.0.0.1:{server.server_port}")["passed"]
    finally:
        server.shutdown(); thread.join(); server.server_close()
    for item in files:
        (root / item["path"]).unlink()
    assert fetch(root, manifest, cache=cache, base_url="http://127.0.0.1:1")["passed"]


def history_fixture(tmp_path):
    source = tmp_path / "source"; source.mkdir()
    destination = tmp_path / "destination"; destination.mkdir()

    def git(root, *args):
        return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.DEVNULL).decode().strip()

    git(source, "init", "-q")
    git(source, "config", "user.name", "Publication test")
    git(source, "config", "user.email", "test@example.invalid")
    (source / "base.txt").write_text("published baseline")
    git(source, "add", "."); git(source, "commit", "-qm", "baseline")
    baseline = git(source, "rev-parse", "HEAD")
    git(source, "branch", "baseline")
    (source / "proof.bin").write_bytes(b"original exact evidence")
    git(source, "add", "."); git(source, "commit", "-qm", "original evidence")
    original = git(source, "rev-parse", "HEAD")
    ref = "refs/archive/cycle14-original-20261116"
    git(source, "update-ref", ref, original)
    assets = tmp_path / "assets"; assets.mkdir()
    part = assets / "cycle14-original-history-001.part"
    git(source, "bundle", "create", str(part), ref, "^" + baseline)
    git(destination, "init", "-q")
    git(destination, "fetch", str(source), "refs/heads/baseline:refs/heads/baseline")
    git(destination, "checkout", "-q", "baseline")
    item = dict(name=part.name, bytes=part.stat().st_size, sha256=sha256(part))
    manifest = dict(schema="cycle14-original-history-v1", original_head=original,
                    bundle=dict(bytes=item["bytes"], sha256=item["sha256"]), parts=[item])
    path = tmp_path / "original-history.json"; path.write_text(json.dumps(manifest))
    return destination, assets, part, path, baseline, original, git


def test_original_commit_ids_restored_without_changing_checkout(tmp_path):
    root, assets, _, path, baseline, original, git = history_fixture(tmp_path)
    result = restore_history(root, path, asset_dir=assets, cache=tmp_path / "cache")
    assert result["passed"] and result["original_head"] == original
    assert git(root, "rev-parse", "HEAD") == baseline
    assert git(root, "show", original + ":proof.bin") == "original exact evidence"
    assert not (root / "proof.bin").exists()


def test_corrupt_history_part_does_not_import_or_replace_checkout(tmp_path):
    root, assets, part, path, baseline, _, git = history_fixture(tmp_path)
    part.write_bytes(b"corrupt bundle")
    with pytest.raises(ValueError, match="History part checksum mismatch"):
        restore_history(root, path, asset_dir=assets, cache=tmp_path / "cache")
    assert git(root, "rev-parse", "HEAD") == baseline
    assert not (tmp_path / "cache/cycle14-original.bundle").exists()

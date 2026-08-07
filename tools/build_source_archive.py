#!/usr/bin/env python3
"""Build a Linux-permission-safe OpenWrt source archive for this project."""

import gzip
import hashlib
import io
import os
import tarfile
from pathlib import Path, PurePosixPath


VERSION = "1.0-20"
ARCHIVE_ROOT = "mt5700webui-openwrt-server"
PACKAGE_DIRS = ("at-webserver", "luci-app-at-webserver")
EXECUTABLE_FILES = {
    "at-webserver/files/etc/init.d/at-webserver",
    "at-webserver/files/usr/bin/at-server.py",
    "at-webserver/files/www/cgi-bin/at-log-clear",
    "at-webserver/files/www/cgi-bin/at-ws-info",
}
BINARY_SUFFIXES = {".ico", ".png"}


def excluded(path: Path) -> bool:
    return (
        "__pycache__" in path.parts
        or path.suffix in {".pyc", ".pyo", ".backup", ".orig"}
        or path.name.endswith("~")
    )


def source_files(repo_root: Path):
    selected = []
    for directory in PACKAGE_DIRS:
        root = repo_root / directory
        selected.extend(
            path for path in root.rglob("*") if path.is_file() and not excluded(path)
        )
    selected.append(repo_root / "README.md")
    return sorted(set(selected))


def file_payload(path: Path) -> bytes:
    payload = path.read_bytes()
    if path.suffix.lower() not in BINARY_SUFFIXES:
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return payload


def tar_info(name: str, mode: int, epoch: int, size: int = 0) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.mode = mode
    info.uid = 0
    info.gid = 0
    info.uname = "root"
    info.gname = "root"
    info.mtime = epoch
    info.size = size
    return info


def build(repo_root: Path, destination: Path, epoch: int) -> None:
    sources = source_files(repo_root)
    names = {
        source: "{}/{}".format(
            ARCHIVE_ROOT, source.relative_to(repo_root).as_posix()
        )
        for source in sources
    }
    directories = {ARCHIVE_ROOT}
    for name in names.values():
        for parent in PurePosixPath(name).parents:
            if str(parent) != ".":
                directories.add(parent.as_posix())

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.GNU_FORMAT) as archive:
                for directory in sorted(
                    directories,
                    key=lambda item: (len(PurePosixPath(item).parts), item),
                ):
                    info = tar_info(directory + "/", 0o755, epoch)
                    info.type = tarfile.DIRTYPE
                    archive.addfile(info)

                for source in sources:
                    relative = source.relative_to(repo_root).as_posix()
                    mode = 0o755 if relative in EXECUTABLE_FILES else 0o644
                    payload = file_payload(source)
                    archive.addfile(
                        tar_info(names[source], mode, epoch, len(payload)),
                        io.BytesIO(payload),
                    )


def verify(repo_root: Path, destination: Path) -> str:
    expected = {
        "{}/{}".format(ARCHIVE_ROOT, path.relative_to(repo_root).as_posix())
        for path in source_files(repo_root)
    }
    with tarfile.open(destination, mode="r:gz") as archive:
        files = {member.name: member for member in archive.getmembers() if member.isfile()}
        if set(files) != expected:
            raise ValueError("source archive file list mismatch")

        for name, member in files.items():
            relative = name[len(ARCHIVE_ROOT) + 1 :]
            expected_mode = 0o755 if relative in EXECUTABLE_FILES else 0o644
            if member.mode != expected_mode:
                raise ValueError("mode mismatch: {}".format(name))
            if excluded(Path(relative)):
                raise ValueError("build artifact leaked into source archive: {}".format(name))

            if relative in EXECUTABLE_FILES or relative.endswith("/Makefile"):
                extracted = archive.extractfile(member)
                if extracted is None or b"\r" in extracted.read():
                    raise ValueError("non-Unix line endings: {}".format(name))

    return hashlib.sha256(destination.read_bytes()).hexdigest()


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    destination = (
        repo_root
        / "dist"
        / "mt5700webui-openwrt-server-{}-source.tar.gz".format(VERSION)
    )
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "1786075675"))
    build(repo_root, destination, epoch)
    digest = verify(repo_root, destination)
    print(destination.resolve())
    print("size={}".format(destination.stat().st_size))
    print("sha256={}".format(digest))


if __name__ == "__main__":
    main()

"""Convert qBittorrent .fastresume save paths between Windows and Linux.

Useful for dual-boot setups where the same qBittorrent data is accessed from both
Windows and Linux, but the save paths differ between the two operating systems.
"""

import argparse
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import bencodepy


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert qBittorrent .fastresume save paths between Windows and POSIX."
    )
    parser.add_argument("path", help="directory containing .fastresume files")
    parser.add_argument("-w", "--windows_path", required=True, help="Windows save path")
    parser.add_argument("-p", "--posix_path", required=True, help="POSIX save path")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--posix_to_windows", action="store_true", help="POSIX to Windows"
    )
    group.add_argument(
        "--windows_to_posix", action="store_true", help="Windows to POSIX"
    )
    return parser


def convert_path(
    path: bytes,
    windows_root: PureWindowsPath,
    posix_root: PurePosixPath,
    windows_to_posix: bool,
) -> bytes:
    """Convert relative paths or remap absolute paths under the source root.

    Unmapped absolute paths and Windows paths with an implicit drive or root
    are preserved because their destination cannot be inferred.
    """
    if not path:
        return path

    if windows_to_posix:
        source_path = PureWindowsPath(os.fsdecode(path))
        source_root, target_root = windows_root, posix_root
    else:
        source_path = PurePosixPath(os.fsdecode(path))
        source_root, target_root = posix_root, windows_root

    if source_path.is_absolute():
        try:
            relative = source_path.relative_to(source_root)
        except ValueError:
            return path
        return os.fsencode(target_root.joinpath(*relative.parts))

    if source_path.anchor:
        return path

    target_type = PurePosixPath if windows_to_posix else PureWindowsPath
    return os.fsencode(target_type(*source_path.parts))


def convert_files(
    bt_backup_dir: Path,
    windows_root: PureWindowsPath,
    posix_root: PurePosixPath,
    windows_to_posix: bool,
) -> None:
    """Convert save roots and mapped file separators in .fastresume files.

    Args:
        bt_backup_dir: Directory containing .fastresume files.
        windows_root: Parsed Windows save root.
        posix_root: Parsed POSIX save root.
        windows_to_posix: If True, convert Windows to POSIX; otherwise reverse.
    """
    files = [p.resolve() for p in bt_backup_dir.glob("*.fastresume")]

    for filepath in files:
        try:
            f = bencodepy.bread(filepath)
        except bencodepy.BencodeDecodeError:
            print(f"Skip invalid file: {filepath}")
            continue
        for key in (b"save_path", b"qBt-savePath", b"qBt-downloadPath"):
            if f.get(key):
                f[key] = convert_path(
                    f[key], windows_root, posix_root, windows_to_posix
                )
        if b"mapped_files" in f:
            f[b"mapped_files"] = [
                convert_path(
                    path, windows_root, posix_root, windows_to_posix
                )
                for path in f[b"mapped_files"]
            ]
        bencodepy.bwrite(f, filepath)


def main() -> None:
    """Parse arguments and run the conversion."""
    parser = build_parser()
    args = parser.parse_args()

    bt_backup_dir = Path(args.path)
    posix_root = PurePosixPath(args.posix_path)
    windows_root = PureWindowsPath(args.windows_path)
    if not posix_root.is_absolute() or not windows_root.is_absolute():
        parser.error("Windows and POSIX save roots must be absolute paths")
    convert_files(
        bt_backup_dir,
        windows_root,
        posix_root,
        windows_to_posix=args.windows_to_posix,
    )
    print("Success")


if __name__ == "__main__":
    main()

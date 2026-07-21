"""Convert qBittorrent .fastresume save paths between Windows and Linux.

Useful for dual-boot setups where the same qBittorrent data is accessed from both
Windows and Linux, but the save paths differ between the two operating systems.
"""

import argparse
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


def convert_files(
    bt_backup_dir: Path,
    windows_save_path: bytes,
    posix_save_path: bytes,
    windows_to_posix: bool,
) -> None:
    """Find all .fastresume files and convert their save_path field.

    Args:
        bt_backup_dir: Directory containing .fastresume files.
        windows_save_path: Target save path in Windows format (as bytes).
        posix_save_path: Target save path in POSIX format (as bytes).
        windows_to_posix: If True, set save_path to posix_save_path;
                          if False, set save_path to windows_save_path.
    """
    files = [p.resolve() for p in bt_backup_dir.glob("*.fastresume")]

    for filepath in files:
        try:
            f = bencodepy.bread(filepath)
        except bencodepy.BencodeDecodeError:
            print(f"Skip invalid file: {filepath}")
            continue
        f[b"save_path"] = posix_save_path if windows_to_posix else windows_save_path
        bencodepy.bwrite(f, filepath)


def main() -> None:
    """Parse arguments and run the conversion."""
    parser = build_parser()
    args = parser.parse_args()

    bt_backup_dir = Path(args.path)
    posix_save_path = bytes(PurePosixPath(args.posix_path))
    windows_save_path = bytes(PureWindowsPath(args.windows_path))

    convert_files(
        bt_backup_dir,
        windows_save_path,
        posix_save_path,
        windows_to_posix=args.windows_to_posix,
    )
    print("Success")


if __name__ == "__main__":
    main()

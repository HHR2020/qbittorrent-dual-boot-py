# qbittorrent-dual-boot-py

Convert qBittorrent `.fastresume` save paths between Windows and Linux(POSIX).
Useful for dual-boot setups where the same qBittorrent data directory is shared across Windows and Linux.

Inspired by [qbittorrent_dual_boot](https://github.com/Ovenoboyo/qbittorrent_dual_boot/tree/main)

## Usage

```bash
# Convert all .fastresume files from POSIX paths to Windows paths
uv run main.py /mnt/D/qBittorrent/BT_backup \
  --posix_path /mnt/D/qBittorrent \
  --windows_path "D:\\qBittorrent" \
  --posix_to_windows

# Convert from Windows paths to POSIX paths
uv run main.py /mnt/D/qBittorrent/BT_backup \
  --posix_path /mnt/D/qBittorrent \
  --windows_path "D:\\qBittorrent" \
  --windows_to_posix
```

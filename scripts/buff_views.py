"""Script to boost GitHub profile views on komarev.com counter."""

import argparse
import concurrent.futures
import io
import re
import sys
import time
import urllib.error
import urllib.request

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CAMO_USER_AGENT = "github-camo (726a45b)"


def get_current_views(username: str) -> int | None:
    """Fetch current view count from the badge."""
    url = f"https://komarev.com/ghpvc/?username={username}&_read_only=1"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            svg = response.read().decode("utf-8")
            matches = re.findall(r"<text[^>]*>(\d+)</text>", svg)
            if matches:
                return int(matches[-1])
    except Exception as e:
        print(f"[!] Loi khi doc view hien tai: {e}")
    return None


def increment_view(username: str) -> int | None:
    """Send a request simulating GitHub Camo proxy to increment view count."""
    url = f"https://komarev.com/ghpvc/?username={username}&_t={time.time_ns()}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": CAMO_USER_AGENT,
            "Accept": "image/svg+xml,image/*,*/*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            svg = response.read().decode("utf-8")
            matches = re.findall(r"<text[^>]*>(\d+)</text>", svg)
            if matches:
                return int(matches[-1])
            return 1
    except urllib.error.HTTPError as e:
        if e.code == 429:
            time.sleep(0.5)
        return None
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Buff GitHub profile views counter.")
    parser.add_argument(
        "--username",
        "-u",
        default="ldanh270",
        help="GitHub username (default: ldanh270)",
    )
    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=100,
        help="So luong view muon tang them (default: 100)",
    )
    parser.add_argument(
        "--target",
        "-t",
        type=int,
        default=None,
        help="Target tong so view mong muon dat toi (vi du: --target 1000)",
    )
    parser.add_argument(
        "--threads",
        "-w",
        type=int,
        default=10,
        help="So luong thread chay song song (default: 10)",
    )
    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=0.02,
        help="Delay giua cac request (seconds, default: 0.02s)",
    )

    args = parser.parse_args()

    print(f"[*] Dang kiem tra view hien tai cua '{args.username}'...")
    initial_views = get_current_views(args.username)

    if initial_views is None:
        print("[!] Khong the lay so view ban dau, se bat dau chay truc tiep.")
    else:
        print(f"[+] View hien tai tren Badge: {initial_views}")

    if args.target:
        if initial_views and args.target <= initial_views:
            print(f"[!] Target ({args.target}) da nho hon hoac bang view hien tai ({initial_views}). Dung.")
            return
        total_needed = args.target - (initial_views or 0)
    else:
        total_needed = args.count

    print(f"[*] Bat dau buff {total_needed} views voi {args.threads} threads...")
    start_time = time.time()
    success = 0
    failed = 0
    latest_view = initial_views

    def worker():
        nonlocal success, failed, latest_view
        res = increment_view(args.username)
        if res:
            success += 1
            if isinstance(res, int) and res > 1:
                latest_view = res
        else:
            failed += 1
        if args.delay > 0:
            time.sleep(args.delay)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []
        for _ in range(total_needed):
            futures.append(executor.submit(worker))

        for idx, _ in enumerate(concurrent.futures.as_completed(futures), 1):
            elapsed = time.time() - start_time
            rate = success / elapsed if elapsed > 0 else 0
            view_display = f" | Badge: {latest_view}" if latest_view else ""
            progress = (idx / total_needed) * 100
            sys.stdout.write(
                f"\r[{progress:5.1f}%] Tien do: {idx}/{total_needed} "
                f"(OK: {success}, Fail: {failed} | {rate:.1f} req/s{view_display})"
            )
            sys.stdout.flush()

    print()
    time.sleep(0.5)
    final_views = get_current_views(args.username)
    print(f"[✓] Hoan thanh trong {time.time() - start_time:.2f}s!")
    print(f"[✓] View truoc: {initial_views} -> View sau: {final_views}")


if __name__ == "__main__":
    main()

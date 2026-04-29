from __future__ import annotations

import argparse
import ctypes
import time
from ctypes import wintypes


user32 = ctypes.windll.user32

SW_RESTORE = 9
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
KEYEVENTF_KEYUP = 0x0002
VK_N = 0x4E


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Blender window automation helper.")
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--delay-seconds", type=float, default=2.0)
    parser.add_argument("--send-n", action="store_true")
    parser.add_argument("--skip-click", action="store_true")
    return parser.parse_args()


def find_window_for_pid(pid: int) -> int:
    result: list[int] = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def callback(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        process_id = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
        if process_id.value == pid:
            result.append(hwnd)
            return False
        return True

    user32.EnumWindows(callback, 0)
    return result[0] if result else 0


def click_viewport(hwnd: int) -> None:
    rect = RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise RuntimeError("GetWindowRect failed.")

    x = rect.left + max(240, int((rect.right - rect.left) * 0.35))
    y = rect.top + max(140, int((rect.bottom - rect.top) * 0.28))
    if not user32.SetCursorPos(x, y):
        raise RuntimeError("SetCursorPos failed.")
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def send_n_key() -> None:
    user32.keybd_event(VK_N, 0, 0, 0)
    user32.keybd_event(VK_N, 0, KEYEVENTF_KEYUP, 0)


def main() -> int:
    args = parse_args()
    print(f"prepare_blender_window: pid={args.pid} delay={args.delay_seconds}")

    deadline = time.time() + 20.0
    hwnd = 0
    while time.time() < deadline:
        hwnd = find_window_for_pid(args.pid)
        if hwnd:
            break
        time.sleep(0.2)

    if not hwnd:
        raise RuntimeError(f"Blender window not found for pid={args.pid}")

    print(f"prepare_blender_window: hwnd={hwnd}")
    time.sleep(max(0.1, args.delay_seconds))
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    print("prepare_blender_window: foreground requested")
    if not args.skip_click:
        time.sleep(0.2)
        click_viewport(hwnd)
        print("prepare_blender_window: viewport clicked")
        time.sleep(0.2)
    if args.send_n:
        send_n_key()
        print("prepare_blender_window: sent N")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

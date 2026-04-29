from __future__ import annotations

import argparse
import ctypes
import time
from ctypes import wintypes


user32 = ctypes.windll.user32

SW_RESTORE = 9
KEYEVENTF_KEYUP = 0x0002
VK_SHIFT = 0x10
VK_SPACE = 0x20
VK_F3 = 0x72
VK_RETURN = 0x0D


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reload Blender scripts in a visible Blender window.")
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--delay-seconds", type=float, default=1.0)
    parser.add_argument("--command", default="Reload Scripts")
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
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    user32.mouse_event(0x0004, 0, 0, 0, 0)


def _send_key(vk: int) -> None:
    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def _send_text(text: str) -> None:
    for char in text:
        if char == " ":
            _send_key(VK_SPACE)
            continue

        encoded = user32.VkKeyScanW(ord(char))
        if encoded == -1:
            raise RuntimeError(f"VkKeyScanW failed for character: {char!r}")

        vk = encoded & 0xFF
        shift_state = (encoded >> 8) & 0xFF
        use_shift = (shift_state & 0x01) != 0
        if use_shift:
            user32.keybd_event(VK_SHIFT, 0, 0, 0)
        user32.keybd_event(vk, 0, 0, 0)
        user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        if use_shift:
            user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.03)


def main() -> int:
    args = parse_args()
    hwnd = find_window_for_pid(args.pid)
    if not hwnd:
        raise RuntimeError(f"Blender window not found for pid={args.pid}")

    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    time.sleep(max(0.1, args.delay_seconds))
    click_viewport(hwnd)
    time.sleep(0.2)
    _send_key(VK_F3)
    time.sleep(0.4)
    _send_text(args.command)
    time.sleep(0.2)
    _send_key(VK_RETURN)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


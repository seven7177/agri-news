"""
模板截图辅助工具

运行后，把鼠标移到游戏窗口的目标元素上，按快捷键截取模板。

使用方式:
  python capture_template.py

快捷键:
  Ctrl+Shift+1  截取花盆/花朵 → 保存为 empty_pot / mature_flower
  Ctrl+Shift+2  截取按钮(播种/收获/浇水等) → 保存为 plant_btn / harvest_btn / ...
  Ctrl+Shift+Q  退出
"""

import os
import sys
import time
import logging
from datetime import datetime

import pyautogui
import cv2
import numpy as np
import keyboard
import win32gui

import config

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def get_mouse_pos():
    """获取鼠标在游戏窗口内的相对坐标"""
    hwnd = win32gui.FindWindow(None, None)
    # 找游戏窗口
    def find_game(h, _):
        nonlocal hwnd
        if config.GAME_WINDOW_TITLE.lower() in win32gui.GetWindowText(h).lower():
            hwnd = h
        return True
    win32gui.EnumWindows(find_game, None)

    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        x, y = pyautogui.position()
        rel_x = x - rect[0]
        rel_y = y - rect[1]
        return rel_x, rel_y, rect
    return None, None, None


def save_template(filename_hint: str):
    """截取鼠标周围区域并保存为模板"""
    time.sleep(0.3)  # 等待按键弹起
    mx, my, rect = get_mouse_pos()
    if mx is None:
        log.error("未找到游戏窗口")
        return

    # 截取以鼠标为中心 80x80 的区域
    size = 80
    half = size // 2

    region = {
        "left": rect[0] + mx - half,
        "top": rect[1] + my - half,
        "width": size,
        "height": size,
    }

    from mss import mss
    with mss() as sct:
        img = sct.grab(region)
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # 保存
    timestamp = datetime.now().strftime("%H%M%S")
    path = os.path.join(config.TEMPLATE_DIR, f"{filename_hint}.png")
    cv2.imwrite(path, img)
    log.info(f"已保存: {path}  ({size}x{size})")

    # 也保存一个带调试标注的版本
    show = img.copy()
    cv2.circle(show, (half, half), 3, (0, 0, 255), -1)
    debug_path = os.path.join(config.SCREENSHOT_DIR, f"template_preview_{filename_hint}_{timestamp}.png")
    cv2.imwrite(debug_path, show)
    log.info(f"预览: {debug_path}")


def main():
    os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(config.TEMPLATE_DIR, exist_ok=True)

    # 当前选中的模板名
    current_type = ["empty_pot"]  # list for mutability in closure

    print("=" * 55)
    print("  模板截图工具")
    print("  Ctrl+Shift+1  切换类型后截图")
    print("  Ctrl+Shift+2  直接截图（当前类型）")
    print("  Ctrl+Shift+Q  退出")
    print("=" * 55)
    print()
    print("请将鼠标放在目标元素上，然后按快捷键")
    print()

    def set_type_pot():
        current_type[0] = "empty_pot"
        print(f"  当前类型: empty_pot（花盆/花朵）— 把鼠标移到花盆上按 Ctrl+Shift+2")
        # 也提示成熟花朵
        print(f"  → 如果截取成熟花朵，截完后手动重命名为 mature_flower.png")

    def set_type_btn():
        current_type[0] = "plant_btn"
        print(f"  当前类型: plant_btn（按钮）— 把鼠标移到播种按钮上按 Ctrl+Shift+2")
        print(f"  → 如果截取其他按钮，截完后手动重命名为 harvest_btn/water_btn/confirm_btn.png")

    def do_capture():
        save_template(current_type[0])

    keyboard.add_hotkey("ctrl+shift+1", set_type_pot)
    keyboard.add_hotkey("ctrl+shift+2", set_type_btn)
    keyboard.add_hotkey("ctrl+shift+3", do_capture)

    # 实际上用 Alt 组合避免和 main.py 冲突
    keyboard.add_hotkey("alt+1", set_type_pot)
    keyboard.add_hotkey("alt+2", set_type_btn)
    keyboard.add_hotkey("alt+3", do_capture)

    keyboard.wait("ctrl+shift+q")
    print("退出")


if __name__ == "__main__":
    main()

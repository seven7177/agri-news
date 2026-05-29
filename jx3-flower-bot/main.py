"""
剑网三 家园种花收花 自动化脚本
================================
原理：截图 → OpenCV 模板匹配找花盆 → 分析状态 → 模拟鼠标点击执行操作

使用前：
  1. 游戏设置为"无边框窗口"模式
  2. 在 templates/ 目录下放置模板图片（见 templates/README.txt）
  3. 角色站在家园花盆附近，镜头俯视（方便识别）

快捷键：
  Ctrl+Shift+S  启动
  Ctrl+Shift+X  停止
"""

import os
import sys
import time
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List

import cv2
import numpy as np
import pyautogui
import win32gui
import win32con
import win32ui
import win32api
from mss import mss
import keyboard

import config

# ============================================================
#  日志配置
# ============================================================
os.makedirs(config.LOG_DIR, exist_ok=True)
os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
os.makedirs(config.TEMPLATE_DIR, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(config.LOG_DIR, f"flower_bot_{datetime.now():%Y%m%d}.log"),
            encoding="utf-8",
        ),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ============================================================
#  窗口管理
# ============================================================
class GameWindow:
    """管理剑网三游戏窗口的位置和尺寸"""

    def __init__(self):
        self.hwnd: Optional[int] = None
        self.rect: Optional[Tuple[int, int, int, int]] = None  # left, top, right, bottom

    def find(self) -> bool:
        """按标题模糊匹配游戏窗口"""
        def enum_callback(hwnd, _):
            title = win32gui.GetWindowText(hwnd)
            if config.GAME_WINDOW_TITLE.lower() in title.lower():
                self.hwnd = hwnd
            return True

        win32gui.EnumWindows(enum_callback, None)
        if self.hwnd is None:
            log.error(f"未找到标题包含「{config.GAME_WINDOW_TITLE}」的窗口")
            return False

        self.update_rect()
        log.info(f"找到游戏窗口: HWND={self.hwnd}, 位置={self.rect}")
        return True

    def update_rect(self):
        """刷新窗口位置信息"""
        if self.hwnd:
            self.rect = win32gui.GetWindowRect(self.hwnd)

    def bring_to_foreground(self):
        """将游戏窗口带到前台"""
        if self.hwnd:
            try:
                win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(self.hwnd)
                time.sleep(0.5)
            except Exception as e:
                log.warning(f"切换窗口失败: {e}")

    @property
    def region(self) -> dict:
        """返回 mss 截图的 region 参数: (left, top, width, height)"""
        if self.rect:
            return {
                "left": self.rect[0],
                "top": self.rect[1],
                "width": self.rect[2] - self.rect[0],
                "height": self.rect[3] - self.rect[1],
            }
        return {"left": 0, "top": 0, "width": 0, "height": 0}

    @property
    def is_active(self) -> bool:
        """窗口是否在前台"""
        return self.hwnd is not None and win32gui.GetForegroundWindow() == self.hwnd


# ============================================================
#  屏幕截图
# ============================================================
class ScreenCapture:
    """截取游戏窗口截图"""

    def __init__(self, game_window: GameWindow):
        self.window = game_window
        self.sct = mss()

    def capture(self) -> Optional[np.ndarray]:
        """截取游戏窗口区域，返回 BGR numpy 数组"""
        region = self.window.region
        if region["width"] == 0 or region["height"] == 0:
            log.warning("游戏窗口区域为空")
            return None

        try:
            screenshot = self.sct.grab(region)
            # mss 返回 BGRA，转为 BGR
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return img
        except Exception as e:
            log.error(f"截图失败: {e}")
            return None

    def save_debug(self, img: np.ndarray, prefix: str = "debug"):
        """保存调试截图"""
        if not config.SAVE_DEBUG_SCREENSHOT:
            return
        filename = f"{prefix}_{datetime.now():%H%M%S_%f}.png"
        filepath = os.path.join(config.SCREENSHOT_DIR, filename)
        cv2.imwrite(filepath, img)
        log.debug(f"截图已保存: {filepath}")


# ============================================================
#  图像识别
# ============================================================
class ImageRecognizer:
    """模板匹配和图像分析"""

    def __init__(self):
        self.templates: dict[str, Optional[np.ndarray]] = {}
        self._load_templates()

    def _load_templates(self):
        """从 templates 目录加载所有模板图片"""
        template_names = [
            "empty_pot",      # 空花盆
            "mature_flower",  # 成熟花朵
            "plant_btn",      # 播种按钮
            "harvest_btn",    # 收获按钮
            "water_btn",      # 浇水按钮
            "confirm_btn",    # 确认按钮
            "seed_bag",       # 种子袋
        ]
        for name in template_names:
            path = os.path.join(config.TEMPLATE_DIR, f"{name}.png")
            if os.path.exists(path):
                img = cv2.imread(path, cv2.IMREAD_COLOR)
                if img is not None:
                    self.templates[name] = img
                    log.info(f"已加载模板: {name}.png ({img.shape[1]}x{img.shape[0]})")
                else:
                    self.templates[name] = None
                    log.warning(f"模板文件损坏: {path}")
            else:
                self.templates[name] = None
                log.warning(f"模板不存在: {path}")

    def template_count(self) -> int:
        return sum(1 for v in self.templates.values() if v is not None)

    def find_all(
        self, screenshot: np.ndarray, template_key: str, threshold: float = None
    ) -> List[Tuple[int, int, float]]:
        """
        在截图中查找所有匹配的模板位置。

        返回: [(center_x, center_y, confidence), ...]
        """
        if threshold is None:
            threshold = config.MATCH_THRESHOLD

        template = self.templates.get(template_key)
        if template is None:
            return []

        h, w = template.shape[:2]
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)

        points = []
        for y, x in zip(*locations):
            points.append((int(x + w // 2), int(y + h // 2), float(result[y, x])))

        # 合并相邻匹配（非极大值抑制简化版
        if len(points) > 1:
            points = self._nms(points, min_dist=max(w, h) // 2)

        return points

    def find_best(
        self, screenshot: np.ndarray, template_key: str, threshold: float = None
    ) -> Optional[Tuple[int, int, float]]:
        """找到最佳匹配位置"""
        points = self.find_all(screenshot, template_key, threshold)
        if not points:
            return None
        return max(points, key=lambda p: p[2])

    def _nms(
        self, points: List[Tuple[int, int, float]], min_dist: int = 30
    ) -> List[Tuple[int, int, float]]:
        """非极大值抑制 - 合并相邻的匹配点"""
        if not points:
            return []
        points = sorted(points, key=lambda p: p[2], reverse=True)
        kept = []
        for p in points:
            if all(
                abs(p[0] - k[0]) > min_dist or abs(p[1] - k[1]) > min_dist
                for k in kept
            ):
                kept.append(p)
        return kept

    def detect_pot_state(
        self, pot_roi: np.ndarray
    ) -> str:
        """
        分析花盆区域图像，判断状态。

        返回: "empty" / "growing" / "mature" / "unknown"
        """

        # 方法1: 优先走模板匹配
        if self.templates.get("mature_flower") is not None:
            result = cv2.matchTemplate(
                pot_roi, self.templates["mature_flower"], cv2.TM_CCOEFF_NORMED
            )
            _, max_val, _, _ = cv2.minMaxLoc(result)
            if max_val >= config.MATCH_THRESHOLD:
                return "mature"

        if self.templates.get("empty_pot") is not None:
            result = cv2.matchTemplate(
                pot_roi, self.templates["empty_pot"], cv2.TM_CCOEFF_NORMED
            )
            _, max_val, _, _ = cv2.minMaxLoc(result)
            if max_val >= config.MATCH_THRESHOLD:
                return "empty"

        # 方法2: 颜色分析（当缺少模板时的备选）
        hsv = cv2.cvtColor(pot_roi, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        # 计算中心区域的颜色特征
        cy, cx = h.shape[0] // 2, h.shape[1] // 2
        center_roi_h = h[cy - 8:cy + 8, cx - 8:cx + 8]
        center_roi_s = s[cy - 8:cy + 8, cx - 8:cx + 8]
        center_roi_v = v[cy - 8:cy + 8, cx - 8:cx + 8]

        avg_sat = np.mean(center_roi_s)
        avg_val = np.mean(center_roi_v)
        avg_hue = np.mean(center_roi_h)

        log.debug(f"  颜色分析: H={avg_hue:.0f} S={avg_sat:.0f} V={avg_val:.0f}")

        # 空花盆 → 低饱和度、中等亮度、偏棕色色调
        if avg_sat < 50 and 60 < avg_val < 200:
            return "empty"
        # 成熟花朵 → 高饱和度、高亮度、色调鲜艳
        if avg_sat > config.MATURE_FLOWER_SAT_MIN and avg_val > config.MATURE_FLOWER_VAL_MIN:
            return "mature"
        # 生长期 → 中低饱和度、中等亮度（叶子是绿色但饱和度不高）
        if avg_sat < 100 and avg_val > 80:
            return "growing"

        return "unknown"


# ============================================================
#  鼠标/键盘操作
# ============================================================
class GameController:
    """对游戏窗口进行鼠标点击和键盘操作"""

    def __init__(self, game_window: GameWindow):
        self.window = game_window
        # 输入延迟保护
        self.last_click_time = 0.0

    def click(self, x: int, y: int):
        """在游戏窗口的 (x, y) 相对坐标处点击"""
        abs_x = self.window.rect[0] + x
        abs_y = self.window.rect[1] + y

        self._rate_limit()
        pyautogui.moveTo(abs_x, abs_y, duration=config.MOUSE_DURATION)
        self._rate_limit()
        pyautogui.click()
        self.last_click_time = time.time()
        log.info(f"点击: ({x}, {y}) → 屏幕 ({abs_x}, {abs_y})")

    def click_center(self):
        """点击游戏窗口中心"""
        r = self.window.rect
        cx = (r[2] - r[0]) // 2
        cy = (r[3] - r[1]) // 2
        self.click(cx, cy)

    def press_key(self, key: str):
        """在游戏窗口中按键"""
        self._rate_limit()
        if not self.window.is_active:
            self.window.bring_to_foreground()
        pyautogui.press(key)
        self.last_click_time = time.time()
        log.info(f"按键: {key}")

    def _rate_limit(self):
        """确保操作之间至少有最小间隔"""
        elapsed = time.time() - self.last_click_time
        if elapsed < config.CLICK_DELAY:
            time.sleep(config.CLICK_DELAY - elapsed)


# ============================================================
#  花盆处理工作流
# ============================================================
class FlowerWorkflow:
    """种花收花的核心工作流"""

    def __init__(
        self,
        game_window: GameWindow,
        capture: ScreenCapture,
        recognizer: ImageRecognizer,
        controller: GameController,
    ):
        self.window = game_window
        self.capture = capture
        self.recognizer = recognizer
        self.controller = controller
        self.stats = {"plant": 0, "harvest": 0, "water": 0, "skipped": 0, "errors": 0}

    def run_cycle(self) -> bool:
        """
        执行一轮种花/收花扫描。

        返回 True 表示成功完成一轮，False 表示出错需要重试。
        """
        log.info("=" * 50)
        log.info("开始新一轮扫描")
        log.info("=" * 50)

        # 1. 确保窗口可见
        self.window.bring_to_foreground()
        time.sleep(config.ENTER_HOME_DELAY)

        # 2. 截图
        screenshot = self.capture.capture()
        if screenshot is None:
            log.error("截图失败，跳过本轮")
            return False

        self.capture.save_debug(screenshot, "full_scene")

        # 3. 找花盆
        pots = self.recognizer.find_all(
            screenshot, "empty_pot", threshold=config.POT_DETECT_THRESHOLD
        )
        log.info(f"找到 {len(pots)} 个空花盆模板匹配")
        # 同时匹配成熟花朵作为补充
        mature_hits = self.recognizer.find_all(
            screenshot, "mature_flower", threshold=config.POT_DETECT_THRESHOLD
        )
        if mature_hits:
            log.info(f"找到 {len(mature_hits)} 个成熟花朵模板匹配")
            # 合并花盆位置（去重）
            for m in mature_hits:
                if not any(abs(m[0]-p[0]) < 40 and abs(m[1]-p[1]) < 40 for p in pots):
                    pots.append(m)

        if not pots:
            log.warning("未检测到任何花盆，可能视角不对或不在家园")
            return True

        # 4. 逐一处理每个花盆
        for idx, (px, py, conf) in enumerate(pots):
            log.info(f"--- 处理花盆 {idx + 1}/{len(pots)}  ({px}, {py}) conf={conf:.2f} ---")

            # 点击花盆
            self.controller.click(px, py)
            time.sleep(config.UI_DELAY)

            # 截图花盆区域
            pot_img = self.capture.capture()
            if pot_img is None:
                continue

            # 判断状态
            # 提取花盆周围的 ROI
            h, w = pot_img.shape[:2]
            x1, y1 = max(0, px - 30), max(0, py - 30)
            x2, y2 = min(w, px + 30), min(h, py + 30)
            pot_roi = pot_img[y1:y2, x1:x2]

            state = self.recognizer.detect_pot_state(pot_roi)
            log.info(f"  花盆状态: {state}")

            if state == "empty":
                self._handle_empty_pot(pot_img)
            elif state == "mature":
                self._handle_mature_pot(pot_img)
            elif state == "growing":
                self._handle_growing_pot(pot_img)
            else:
                log.info(f"  无法判断状态，尝试点击确认关闭弹窗")
                self._try_close_dialog(pot_img)

            time.sleep(config.POT_ACTION_DELAY)

        # 输出本轮统计
        log.info(f"本轮统计: {self.stats}")

        # 空花盆全部处理后, 按ESC关闭可能的交互面板
        self.controller.press_key("esc")
        time.sleep(0.5)

        return True

    def _handle_empty_pot(self, screenshot: np.ndarray):
        """处理空花盆 — 播种"""
        log.info("  空花盆 → 尝试播种")

        btn = self.recognizer.find_best(screenshot, "plant_btn", threshold=config.BUTTON_THRESHOLD)
        if btn:
            self.controller.click(btn[0], btn[1])
            time.sleep(config.UI_DELAY)
            self.stats["plant"] += 1
            log.info("  点击了播种按钮")
        else:
            # 找不到播种按钮 → 可能弹窗没出来，尝试确认
            log.info("  未检测到播种按钮，尝试确认关闭")
            self._try_close_dialog(screenshot)

    def _handle_mature_pot(self, screenshot: np.ndarray):
        """处理成熟花朵 — 收获"""
        log.info("  成熟花朵 → 尝试收获")

        btn = self.recognizer.find_best(
            screenshot, "harvest_btn", threshold=config.BUTTON_THRESHOLD
        )
        if btn:
            self.controller.click(btn[0], btn[1])
            time.sleep(config.UI_DELAY)
            self.stats["harvest"] += 1
            log.info("  点击了收获按钮")
        else:
            log.info("  未检测到收获按钮，尝试确认关闭")
            self._try_close_dialog(screenshot)

    def _handle_growing_pot(self, screenshot: np.ndarray):
        """处理生长期花盆 — 尝试浇水"""
        log.info("  生长期 → 尝试浇水")

        btn = self.recognizer.find_best(
            screenshot, "water_btn", threshold=config.BUTTON_THRESHOLD
        )
        if btn:
            self.controller.click(btn[0], btn[1])
            time.sleep(config.UI_DELAY)
            self.stats["water"] += 1
            log.info("  已浇水")
        else:
            log.info("  无需浇水或无法操作，跳过")
            self.stats["skipped"] += 1
            self._try_close_dialog(screenshot)

    def _try_close_dialog(self, screenshot: np.ndarray):
        """尝试关闭可能的弹窗（确认按钮或ESC）"""
        confirm = self.recognizer.find_best(
            screenshot, "confirm_btn", threshold=config.BUTTON_THRESHOLD
        )
        if confirm:
            self.controller.click(confirm[0], confirm[1])
            time.sleep(0.3)
        else:
            self.controller.press_key("esc")
            time.sleep(0.3)


# ============================================================
#  主程序入口
# ============================================================
class FlowerBot:
    """主控器，管理生命周期"""

    def __init__(self):
        self.running = False
        self.game_window = GameWindow()
        self.capture = ScreenCapture(self.game_window)
        self.recognizer = ImageRecognizer()
        self.controller = GameController(self.game_window)
        self.workflow = FlowerWorkflow(
            self.game_window, self.capture, self.recognizer, self.controller
        )

    def start(self):
        """启动脚本"""
        if self.running:
            log.warning("脚本已在运行中")
            return

        # 1. 检查模板
        if self.recognizer.template_count() == 0:
            log.error(
                "未加载任何模板图片！请先按 templates/README.txt 的说明截取模板。"
            )
            return

        # 2. 查找游戏窗口
        if not self.game_window.find():
            log.error("无法找到游戏窗口，请确认游戏已启动")
            return

        # 3. 注册停止热键
        keyboard.add_hotkey(config.STOP_HOTKEY, self.stop)
        log.info(f"按 {config.STOP_HOTKEY} 可随时停止脚本")

        # 4. 进入主循环
        self.running = True
        cycle_count = 0
        log.info(f"脚本启动成功 [{config.START_HOTKEY}]")
        self._print_status()

        try:
            while self.running:
                cycle_count += 1
                log.info(f"\n========== 第 {cycle_count} 轮 ==========")

                success = self.workflow.run_cycle()

                if not success and self.running:
                    log.warning("本轮执行出错，30 秒后重试")
                    time.sleep(30)
                    continue

                # 检查循环次数限制
                if 0 < config.MAX_CYCLES <= cycle_count:
                    log.info(f"达到最大循环次数 ({config.MAX_CYCLES})，自动停止")
                    self.stop()
                    break

                # 等待到下一轮扫描
                if self.running:
                    log.info(f"等待 {config.SCAN_INTERVAL:.0f} 秒后进行下一轮")
                    self._countdown(config.SCAN_INTERVAL)

        except KeyboardInterrupt:
            log.info("用户中断")
        except Exception as e:
            log.exception(f"脚本异常: {e}")
        finally:
            self.stop()

    def stop(self):
        """停止脚本"""
        if not self.running:
            return
        self.running = False
        log.info("脚本已停止")
        log.info(f"最终统计: {self.workflow.stats}")

    def _countdown(self, seconds: float):
        """倒计时等待（可被中断）"""
        for i in range(int(seconds), 0, -1):
            if not self.running:
                break
            if i % 10 == 0 or i <= 5:
                log.debug(f"  下次扫描还有 {i} 秒...")
            time.sleep(1)

    def _print_status(self):
        """打印当前状态信息"""
        log.info("--- 配置状态 ---")
        log.info(f"  模板已加载: {self.recognizer.template_count()} 个")
        log.info(f"  扫描间隔: {config.SCAN_INTERVAL} 秒")
        log.info(f"  最大轮次: {'无限' if config.MAX_CYCLES <= 0 else config.MAX_CYCLES}")
        log.info(f"  截图保存: {'开启' if config.SAVE_DEBUG_SCREENSHOT else '关闭'}")
        log.info("-----------------")


def check_dependencies():
    """启动时检查依赖是否齐全"""
    try:
        import cv2  # noqa
        import numpy  # noqa
        import pyautogui  # noqa
        import win32gui  # noqa
        from mss import mss  # noqa
        import keyboard  # noqa
    except ImportError as e:
        log.error(f"缺少依赖: {e}")
        log.error("请运行: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    log.info("=" * 60)
    log.info("  剑网三 家园种花收花 自动化脚本 v1.0")
    log.info(f"  启动热键: {config.START_HOTKEY}")
    log.info(f"  停止热键: {config.STOP_HOTKEY}")
    log.info("=" * 60)

    check_dependencies()

    bot = FlowerBot()

    # 注册启动热键
    keyboard.add_hotkey(config.START_HOTKEY, bot.start)
    log.info(f"按 {config.START_HOTKEY} 启动脚本")
    log.info(f"按 {config.STOP_HOTKEY} 停止脚本")
    log.info("程序已在后台运行，等待热键触发...")

    # 保持进程运行
    keyboard.wait()

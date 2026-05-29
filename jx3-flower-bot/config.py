"""
剑网三 家园种花收花自动化 - 配置
所有可调参数集中在此，方便修改
"""

import os

# ============ 窗口设置 ============
# 剑网三游戏窗口标题（支持模糊匹配）
GAME_WINDOW_TITLE = "剑网3"

# 游戏运行模式：borderless（无边框窗口）/ windowed（窗口模式）
# 边框窗口模式才能正常截图
GAME_MODE = "borderless"

# ============ 家园场景设置 ============
# 进入家园后的等待时间（秒）
ENTER_HOME_DELAY = 3.0
# 处理完一个花盆后的短等待
POT_ACTION_DELAY = 1.0
# 两次扫描之间的等待时间（秒）
SCAN_INTERVAL = 60.0
# 浇水后等待再次检查的时间（秒）
WATER_COOLDOWN = 120.0

# ============ 模板匹配参数 ============
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
# 模板匹配置信度阈值（0~1，越高越严格）
MATCH_THRESHOLD = 0.75
# 花盆检测置信度阈值（可以稍低，怕漏检）
POT_DETECT_THRESHOLD = 0.70
# 按钮检测置信度阈值（需要高一些，防止误点）
BUTTON_THRESHOLD = 0.80

# ============ 花盆状态颜色参考 (HSV) ============
# 用于判断花盆状态的简单颜色分析
# 空花盆 - 泥土色
EMPTY_POT_HUE_RANGE = (15, 40)
EMPTY_POT_SAT_RANGE = (30, 120)
# 成熟花朵 - 鲜艳颜色（依具体花朵而定）
MATURE_FLOWER_SAT_MIN = 100
MATURE_FLOWER_VAL_MIN = 150

# ============ 鼠标行为 ============
# 鼠标移动速度（0~1，越小越快）
MOUSE_DURATION = 0.3
# 点击后等待 UI 反应
CLICK_DELAY = 0.5
# UI 弹窗等待时间
UI_DELAY = 1.0

# ============ 日志设置 ============
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_LEVEL = "INFO"
# 调试截图保存目录
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
# 是否保存调试截图
SAVE_DEBUG_SCREENSHOT = False

# ============ 快捷键 ============
# 启动/停止脚本的热键
START_HOTKEY = "ctrl+shift+s"
STOP_HOTKEY = "ctrl+shift+x"

# ============ 运行模式 ============
# MAX_CYCLES: 最大循环次数（-1 表示无限循环）
MAX_CYCLES = -1

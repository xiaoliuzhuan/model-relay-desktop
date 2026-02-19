# 开发规范（Tauri / Legacy）

本文用于约束双平台（`tauri`、`legacy`）的代码组织方式，减少分叉与重复工作。

## 平台命名

- 平台标识固定为：`tauri`、`legacy`。
- 入口处必须设置平台变量（建议用常量注入）：
  - `mtga_app`：定义常量 `MTGA_PLATFORM = "tauri"` 并 `os.environ.setdefault(...)`
  - `mtga_gui.py`：定义常量 `MTGA_PLATFORM = "legacy"` 并 `os.environ.setdefault(...)`
- 未设置或非法值将抛出异常，避免静默落入错误平台。

## 文件命名规范

- 平台差异实现使用：`原名_平台.py`。
- 例：`log_bus_tauri.py`、`log_bus_legacy.py`。

## 平台识别助手

统一使用 `modules/platform/platform_context.py` 里的 `get_platform()`，避免各处重复读取环境变量。

## 兼容层（薄分发器）

保持一个与旧 import 兼容的“分发器”文件，负责按平台导入对应实现：

```py
# modules/runtime/log_bus.py
from modules.platform.platform_context import get_platform
if get_platform() == "tauri":
    from .log_bus_tauri import *  # noqa
else:
    from .log_bus_legacy import *  # noqa
```

约束：

- 分发器只做“选择+导入”，不写业务逻辑。
- 平台实现文件之间不能互相 import。

## 共享层是否必要（讨论）

**结论：早期可不强制引入共享层；但要满足以下条件再引入。**

### 何时需要共享层

- 同一业务逻辑在两平台中出现 2 次以上的复制。
- 两边已经开始出现“行为不一致”的风险。
- 平台差异仅在 I/O、日志、路径等“边界层”。

### 共享层的边界

共享层应当是“纯业务”，不包含：

- 平台判断（不读 `MTGA_PLATFORM`）
- UI/IPC、线程调度、路径/权限处理
- 直接输出日志（改用传入的 `log_func`）

### 共享层文件命名建议

优先使用 `*_shared.py`：

- `proxy_shared.py` 放核心业务
- `proxy_tauri.py` / `proxy_legacy.py` 只做装配与 I/O

## 迁移节奏建议（先后顺序）

1. 新增平台分发器（原名文件）
2. 拆出 `*_tauri.py` / `*_legacy.py`
3. 保持旧入口的 import 不变
4. 如有重复逻辑，再考虑引入 `*_shared.py`

## 最小例子

```
modules/runtime/
  log_bus.py            # 分发器
  log_bus_tauri.py      # Tauri 实现
  log_bus_legacy.py     # Legacy 实现
```

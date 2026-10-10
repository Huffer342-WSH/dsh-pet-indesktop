# X11 跨屏、工作区可见及输入穿透修复

差分基线：`fix/pyside612-runtime@f38c186`（前置兼容修复，上游基线`ee699c7`）；分支：`fix/x11-desktop-compat`；日期：2026-10-10。
关联：[开发交付规范](DEV-HANDOVER.md#八开发流程规范)、[打包流程](ONEDIR_PACKAGING.md)。本报告只覆盖此独立分支，集成预发布结果不能代替分支验证。

## 核心特性

Overlay 覆盖 X11 虚拟桌面，允许跨屏拖动；气泡锚点使用窗口实际坐标。输入区域仅包含桌宠可见像素，透明处不再阻挡下层应用；伴随窗口请求所有工作区可见。

## 修改文件说明

相对上述差分基线的最终文件清单（包含本报告与索引）。

| 文件 | 增删 | 修改及原因 |
|---|---|---|
| `docs/INDEX.md` | +2/−1 | 登记本报告并关联已有文档，避免孤立交付记录。 |
| `docs/PR-REPORT-X11-DESKTOP-2026-10-10.md` | +98/−0 | 记录逐文件改动、性能、实机/CI验证、失败历史与回滚；本次末尾补充最终结果。 |
| `pet/app.py` | +3/−0 | 使伴随窗口遵循 X11 工作区显示策略。 |
| `pet/linux_overlay.py` | +148/−0 | 增加 X11 虚拟桌面几何与按透明度生成的输入区域，修复跨屏和点击阻挡。 |
| `pet/overlay_shell.py` | +12/−7 | 转发气泡字段，同步虚拟桌面范围及鼠标穿透状态。 |
| `pet/overlay_window.py` | +22/−6 | 在 X11 使用虚拟桌面与原生输入区域，避免窗口管理器移动大窗口。 |
| `pet/platform_linux.py` | +105/−0 | 为 X11 桌宠及伴随窗口请求所有工作区可见。 |
| `pet/speech_bubble.py` | +2/−0 | 增加自适应 Agent 内容，普通消息保持原布局；接入 X11 工作区策略。 |
| `pet/sprite_bubble.py` | +6/−1 | 转发结构化气泡，使用实际窗口坐标计算锚点。 |
| `scripts/benchmark_linux_overlay.py` | +32/−0 | 新增可复现性能测量入口，临时数据不接触用户配置。 |
| `scripts/benchmark_overlay_paint.py` | +15/−0 | 补充对应功能的实现或回归验证，保持本报告所列契约。 |
| `tests/test_linux_overlay.py` | +187/−0 | 新增回归用例或共享辅助代码，覆盖安装隔离、hook 容错、会话增量、Qt 事件交付或原生 X11 行为。 |
| `tests/test_overlay_window.py` | +24/−1 | 补充对应功能的实现或回归验证，保持本报告所列契约。 |

## 性能分析

环境：Ubuntu 24.04、Python 3.11.16、Qt 6.11.2，16 逻辑 CPU。以下是同一实现的集成版本本轮实测；同时有全量测试运行，不用于宣称相对上游加速比例。

命令：`QT_QPA_PLATFORM=xcb .venv/bin/python scripts/benchmark_linux_overlay.py`。每项 500 次，未变区域中位数/p95 为 4.54/5.08 µs、移动缓存掩码为 9.31/11.97 µs、强制重建掩码为 57.01/62.47 µs。每次绘制检查，区域变化才发送 XShape 更新。新增一个 X11 连接，无新线程、磁盘或网络访问；每个可见 sprite 缓存一个掩码，移除后清理。整个进程 RSS 未测，不能由掩码缓存上限推断 RSS 不增长。

## 实机运行记录

本机 DP-1、DP-6 均为 1920×1080、水平排列。集成版本原生 X11 6 项测试通过，验证虚拟桌面宽度、跨屏拖动、气泡同屏、透明像素、手动穿透、隐藏及关闭连接。读取真实 XShapeGetRectangles；拖动为 Qt 事件注入，没有点击用户其他应用。此前旧实现宽度 1920/期望 3840、锚点偏移、整屏输入的断言失败，修复后通过。

## 测试与验证

开发阶段先在临时回归中复现旧实现失败再修复，本轮把必要用例整理到 tests。独立分支的聚焦、全量和满载结果在下方追加。

## 风险与回滚

Linux xcb 之外不启用新原生输入后端。混合 DPI、非矩形屏幕布局尚未实机验证，工作区使用矩形并集。回滚本分支后重启桌宠即可，无配置迁移。

## 脏区域透明擦除补充

Overlay 使用 WA_NoSystemBackground，旧绘制路径没有擦除移走 sprite 的像素。paintEvent 先以 CompositionMode_Source 把 event.region() 写回透明，再恢复 SourceOver 绘制新帧。`pet/overlay_window.py` 本轮 +8/−0；`tests/test_overlay_window.py` +24/−1，新增真实 QWidget.render 的旧区域 alpha 断言。旧提交3ab32a4红，新实现绿；本机原生X11该用例与跨屏族共7passed。

命令：`QT_QPA_PLATFORM=offscreen .venv/bin/python scripts/benchmark_overlay_paint.py`（新增测量脚本），1920×1080窗口、320×180脏区，预热100次后测1000次。旧路径中位数/p95为5.28/5.52µs，透明擦除路径11.29/11.83µs；这只测空脏区的Qt渲染成本，不代表真实动画整帧耗时。只随重绘发生，不增加线程、网络、磁盘或持久缓存。

## 独立分支最终验证

真实X11聚焦6passed；加入透明擦除回归后，集成版本原生X11相关7passed。独立分支最终 `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q` 为 **4285passed、42skipped、16warnings，228.18秒**。首轮曾遇既有并发记忆用例 shrink1，该族单独重跑33passed；最终整套通过，保留首轮现象，不声称修复了该既有用例。ruff与diffcheck通过。

## 最终交付记录（2026-10-10）

完整集成提交`6ae3519`的[三平台CI](https://github.com/Huffer342-WSH/dsh-pet-indesktop/actions/runs/38044045940)及Linux/macOS/Windows三条构建均通过；[预发布记录](https://api.github.com/repos/Huffer342-WSH/dsh-pet-indesktop/releases/408876027)已公开，包含8份产物。发布标签指向实际构建提交，后续报告更新不改变安装包来源。

最终Linux纯桌宠包在本机隔离配置、缓存、用户数据和网络后，offscreen及原生X11各运行15秒无提前退出或Traceback；frozen hook退出0、输出{}、stderr为空，无_MEI目录。独立进程加载包内两份原生库并核对/proc/self/maps后，六项单例引用探针全0。ZIP SHA256：`5abaa92b2becb6fd2233a30df0d0a42af191a469792af714b06d32eac20fef85`。Windows/macOS的原生桌面人工验收仍未完成。

独立分支按仓库CI方式分进程覆盖全套测试（没有跳过失败用例）：

| 分组 | 结果 |
|---|---|
| main | 4215 passed, 42 skipped, 20 warnings in 168.58s (0:02:48) |
| webm | 41 passed in 25.65s |
| warm | 27 passed in 31.32s |
| recovery | 5 passed in 0.26s |

聚焦、ruff和diffcheck均通过；最终提交仅追加本报告，应用、工作流及测试代码与上述验证时一致。

### 虚拟桌面内存增量

本机Qt6.12/X11下，空透明Overlay首帧绘制后读取psutil.Process().memory_info().rss，与构造窗口前比较；每种几何在独立进程测3次。单屏1920×1080增量中位数11509760B，虚拟桌面3840×1080为19750912B，增加8241152B（约7.86MiB）。这只覆盖客户端首帧窗口内存，不包含视频解码和X server/GPU显存，不能称为整个桌宠的总RSS增量。

复测命令：以`QT_QPA_PLATFORM=xcb python - single`及`QT_QPA_PLATFORM=xcb python - virtual`分别运行下列脚本，每种3次：

```python
import json,sys,time
import psutil
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication,QEvent
from pet.overlay_window import OverlayWindow
app=QApplication([]);process=psutil.Process();before=process.memory_info().rss
class Window(OverlayWindow):
 def paintEvent(self,event):
  super().paintEvent(event);self.painted=True
w=Window();w.painted=False
if sys.argv[1]=='single':w.setGeometry(app.primaryScreen().geometry())
w.show();deadline=time.monotonic()+5
while not w.painted and time.monotonic()<deadline:app.processEvents()
assert w.painted
print(json.dumps({'mode':sys.argv[1],'size':[w.width(),w.height()],'rss_delta':process.memory_info().rss-before}))
w.close();w.deleteLater();QCoreApplication.sendPostedEvents(w,QEvent.Type.DeferredDelete)
```

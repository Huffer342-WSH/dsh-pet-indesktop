# PR #245：适配 v4.3.4 主线

基线：`origin/main@147170f`；分支：`feat/pr245-main-port`；日期：2026-10-19。
本报告对应基于该主线重建的三个主题提交。原 PR 的 4328 项测试和预览包属于历史版本，
不作为本次适配的验证结果。关联：[PR #245](https://github.com/MerZlin/dsh-pet-indesktop/pull/245)。

## 核心特性

- 从菜单安装/卸载 Codex 插件，hook 负责生命周期和权限状态，文件通知增量读取公开进展与最终回复。
- 气泡区分会话名、状态和正文，保留截断、淡化和正文去重。被抑制的气泡不记为已交付；状态气泡也响应文字缩放。
- X11 窗口和气泡请求显示在所有工作区；气泡跟随实际窗口原点，局部重绘清除旧帧。
- 保留 Python 3.11 和 PySide6 6.12.0，通过原生运行库修复解除 Linux 版本上限。

## 修改文件说明

| 文件 | 状态 | 增/删行 | 修改与原因 |
|---|---|---:|---|
| `.github/workflows/build-linux.yml` | 修改 | +14/−2 | 安装 Qt 修复所需依赖并运行探针/修复；独立执行设置导航测试。 |
| `.github/workflows/build-macos.yml` | 修改 | +8/−1 | 将设置导航测试放入独立进程，保留全部断言和现有构建步骤。 |
| `.github/workflows/build-windows.yml` | 修改 | +8/−1 | 将设置导航测试放入独立进程，保留全部断言和现有构建步骤。 |
| `.github/workflows/pr-test.yml` | 修改 | +15/−2 | Linux 测试前执行 Qt 修复，三平台均独立执行设置导航测试。 |
| `README.md` | 修改 | +2/−0 | 说明 Linux 源码运行前的修复步骤。 |
| `THIRD_PARTY_NOTICES.md` | 修改 | +8/−0 | 登记 Qt 原生修改、许可与对应源码。 |
| `docs/INDEX.md` | 修改 | +2/−0 | 登记本次报告。 |
| `docs/ONEDIR_PACKAGING.md` | 修改 | +19/−0 | 记录修复依赖、入口和包内源码。 |
| `docs/PR-REPORT-PR245-MAIN-PORT-2026-10-19.md` | 新增 | +154/−0 | 记录本次适配证据与未完成验证，避免引用旧版结果。 |
| `docs/screenshots/pr245-main-port/bubble-dark-x11.png` | 新增 | 二进制，19198 字节 | 保存本机 X11 深色三行最终回复截图，支持截断与行距验收。 |
| `docs/screenshots/pr245-main-port/bubble-x11.png` | 新增 | 二进制，18814 字节 | 保存本机 X11 浅色两行进展截图，支持布局验收。 |
| `integrations/dsh-pet-codex/.codex-plugin/plugin.json` | 新增 | +17/−0 | 声明本地 Codex 插件身份与版本。 |
| `integrations/dsh-pet-codex/hooks/hooks.json` | 新增 | +100/−0 | 声明 Codex 生命周期与权限 hook。 |
| `integrations/dsh-pet-codex/scripts/bridge.py` | 新增 | +215/−0 | 把生命周期 hook 写入有界快照并保留会话身份。 |
| `integrations/dsh-pet-codex/scripts/diagnostics.py` | 新增 | +105/−0 | 限制 hook 执行时间，记录脱敏诊断。 |
| `packaging/patches/qt-for-python-6.12-singleton-refs.patch` | 新增 | +50/−0 | 修复官方源码的有限 ABI 单例返回值引用所有权。 |
| `packaging/pet_entry.py` | 修改 | +5/−1 | 在导入 GUI 前分流 hook，保留卸载、设置和 OCR 入口。 |
| `packaging/pet_entry_no_chat.py` | 修改 | +4/−0 | 在导入 GUI 前分流 hook，保留卸载、设置和 OCR 入口。 |
| `pet/__main__.py` | 修改 | +7/−0 | 在导入 GUI 前分流 hook，保留卸载、设置和 OCR 入口。 |
| `pet/agent_bubble_content.py` | 新增 | +67/−0 | 按字体度量绘制标题、状态、截断正文和淡化末行。 |
| `pet/agent_file_watch.py` | 新增 | +80/−0 | Qt 文件通知唤醒后台读取，不引入周期轮询。 |
| `pet/agent_link.py` | 修改 | +325/−16 | 接入 Codex 快照、安装和气泡去重；发送完成提示前复核开关，避免关闭后仍提醒。 |
| `pet/agent_snapshot.py` | 新增 | +139/−0 | 聚合会话快照，限制记录数量与有效期。 |
| `pet/app.py` | 修改 | +3/−0 | 为普通窗口与灵动岛安装 X11 工作区监听。 |
| `pet/codex_install.py` | 新增 | +254/−0 | 安装插件到稳定运行目录，避免缓存路径失效。 |
| `pet/codex_transcript.py` | 新增 | +251/−0 | 增量读取公开会话内容，忽略未知消息。 |
| `pet/config.py` | 修改 | +40/−3 | 增加默认关闭的 Codex 配置，迁移旧自定义通道以保留用户数据。 |
| `pet/context_menus/shared.py` | 修改 | +7/−0 | 增加 Codex 安装/关闭菜单与处理中反馈。 |
| `pet/hook_runtime.py` | 新增 | +55/−0 | 提供无 GUI hook 入口，失败仍返回成功。 |
| `pet/multi_window_shared.py` | 修改 | +19/−3 | 透传结构化气泡参数与实际交付结果，避免被抑制的进展记为已展示。 |
| `pet/overlay_shell.py` | 修改 | +6/−2 | 保留歌词 reserve 语义，透传结构化气泡字段。 |
| `pet/overlay_window.py` | 修改 | +7/−0 | 请求所有工作区显示，重绘前清透明脏区以清除旧帧。 |
| `pet/platform_linux.py` | 新增 | +105/−0 | 显示或句柄变化后重发所有工作区提示。 |
| `pet/speech_bubble.py` | 修改 | +57/−4 | 加入结构化内容并适配主线重排，修复状态气泡缩放。 |
| `pet/sprite_bubble.py` | 修改 | +11/−4 | 透传结构化内容，按实际窗口坐标定位气泡。 |
| `pet/window.py` | 修改 | +5/−2 | 保留主线优先级和交付返回值，补充结构化参数。 |
| `pet/window_optional_services.py` | 修改 | +1/−1 | 将 Codex 纳入可选服务启用判断。 |
| `requirements.txt` | 修改 | +1/−5 | 解除 Linux Qt 上限，由构建前原生修复处理缺陷。 |
| `scripts/benchmark_codex_link.py` | 新增 | +53/−0 | 测量快照读取、hook 子进程和 Python 堆增长。 |
| `scripts/build_linux.sh` | 修改 | +9/−0 | 构建前修复 Qt，随包携带对应源码与声明。 |
| `scripts/repair_pyside6.py` | 新增 | +179/−0 | 探测并修复 Qt 单例引用所有权，失败恢复原库。 |
| `tests/codex_helpers.py` | 新增 | +19/−0 | 共享临时 hook 与 Qt 事件等待夹具。 |
| `tests/test_agent_link.py` | 修改 | +3/−0 | 登记默认关闭的 Codex 配置；使 DSH 完成与多实例夹具的开关和运行状态一致。 |
| `tests/test_agent_link_subtraction.py` | 修改 | +1/−0 | 手动驱动监视器前开启 DSH 配置，保持测试前提与真实运行一致。 |
| `tests/test_codex_bubble.py` | 新增 | +160/−0 | 覆盖标题/状态分离、截断、行距、去重、交付失败、状态缩放与实际窗口锚点。 |
| `tests/test_codex_file_watch.py` | 新增 | +127/−0 | 覆盖文件创建/替换重订阅、增量通知、停止与销毁后 worker 退出。 |
| `tests/test_codex_hook_runtime.py` | 新增 | +141/−0 | 验证坏 JSON、脚本丢失、超时和日志写入失败均不阻断 hook。 |
| `tests/test_codex_install.py` | 新增 | +40/−0 | 验证本地插件安装、关闭和稳定运行目录，保护既有配置。 |
| `tests/test_codex_transcript.py` | 新增 | +270/−0 | 覆盖生命周期快照、多会话、JSONL 增量读取、最终回复与旧配置迁移。 |
| `tests/test_desktop_pet_features.py` | 修改 | +13/−1 | 允许实际 Codex 集成和本次报告使用其名称，继续禁止无关产品文案借用品牌。 |
| `tests/test_dsh_mid_attach_done.py` | 修改 | +1/−0 | 补齐模拟启用时的配置，保留中途接入和完成提醒断言。 |
| `tests/test_g2_event_delivery.py` | 修改 | +4/−2 | 构造时不启动 worker，手动摄入时开启配置；保持原有字节去重与轮转断言。 |
| `tests/test_island_alert_colors.py` | 修改 | +3/−2 | 按正屏宽搜索全部折叠状态，避免小字号字体在 200px 下仍未全折而误报失败。 |
| `tests/test_linux_workspaces.py` | 新增 | +41/−0 | 真实 Qt 显隐事件下重发工作区请求；仅替换 X11 请求边界，非 X11 不注册。 |
| `tests/test_overlay_window.py` | 修改 | +24/−1 | 通过真实绘制验证移走后的脏区 alpha 为零。 |

## 实现要点

保留主线的单合成窗、活动区矩形集合、跨屏开关、QtPerPixelInputController、
歌词不占提醒位置和气泡交付返回值。本次不移植旧 linux_overlay.py 的几何逻辑与
XShape 控制器，避免两套输入控制竞争。Codex 快照监视器复用现有 worker 停止与代次
判定；快照聚合独立于 DSH 原始事件摄入，避免把中断或等待推断为成功。
当前统一事件归一化层的消费者负责限流追踪与交互关闭；Codex 权限操作仍在原客户端完成，
本次不把聚合快照伪造成这类原始事件。

## 性能分析

环境：Linux x86_64、Python 3.11.16、已修复 PySide6 6.12.0。
命令：`python scripts/benchmark_codex_link.py`，独立临时目录、16 个活跃会话。

| 项目 | 样本量 | 实测 |
|---|---:|---|
| 未变化快照读取 | 2000 | 中位 111.23 μs；P95 115.02 μs |
| 后续读取 Python 堆变化 | 2000 | 保留增长 192 字节；峰值增量 7792 字节 |
| bridge 子进程 | 30 | 中位 23.87 ms；P95 24.19 ms |
| 16 会话状态文件 | 1 | 6147 字节 |

这些读取次数是基准循环，不是产品轮询频率。功能关闭时无 QFileSystemWatcher，
开启后新增一个读文件线程；文件变更由 Qt 通知唤醒，40 ms 合并通知，无周期轮询兜底。
活跃会话到期还有 deadline 唤醒。hook 每次事件使用子进程、文件锁和状态写入，
诊断日志限长轮换；运行期无新增网络请求。安装插件、首次下载 Qt 修复源码/SDK 需要网络。
气泡更新做字体测量和绘制，正文缓存限 128 个条目；被其他提示占用时呈现层每 200 ms 重试，不触发文件轮询。X11 工作区提示在显示或原生句柄
变化时发送，连接随请求关闭，无新增轮询线程。原有穿透轮询仍由主线控制器负责。
局部重绘仅清 event.region()，不清整个虚拟桌面；本轮未单独重测绘制成本。
堆测量不包含 Qt 原生分配和长时间运行的 RSS，不能据此宣称整进程无增长。

## 实机运行记录

命令：`QT_QPA_PLATFORM=xcb python /tmp/pr245-native.py`。探针建立临时窗口与测试精灵，
未启动真实用户配置；退出关闭窗口并恢复鼠标位置。本机 X11：DP-1 为 (0,0,1920,1080)，
DP-6 为 (1920,0,1920,1080)。真实输出：

```text
background passthrough: true
cross-screen Qt drag: 2300
bubble screen: DP-6
all workspaces: _NET_WM_DESKTOP=4294967295
pet pixels interactive: true
manual passthrough: true
```

`xprop` 确认窗口管理器设置了所有工作区属性；未自动切换用户工作区。
探针先将光标移到宠物并等待其输入状态，再向真实 X11 测试窗口发送 Qt 拖拽事件，精灵中心从主屏移到 x=2300 的副屏，气泡仍在 DP-6。穿透探针确认 QWindow 输入标志随光标位置切换，未向背后的其他应用注入点击。初轮在背景穿透状态直接发事件被丢弃，校正探针后通过。应用中的跨屏行为继续遵守主线 allow_cross_screen 开关。
已人工检查以下原生 X11 截图：标题与状态分开，正文两行完整，末尾截断淡化。

![X11 结构化气泡](screenshots/pr245-main-port/bubble-x11.png)

![深色最终回复，三行截断](screenshots/pr245-main-port/bubble-dark-x11.png)
首次在沙箱中探测 X11 失败，提升该探针的显示访问权限后成功，不能把沙箱拒绝连接视为产品故障。

Qt 命令：`python scripts/repair_pyside6.py`，六项探针输出 `[0,-1,-1,0,0,0]`，
脚本判断已有运行库正确。本轮复用此前修复的隔离环境，未重新下载编译原生库。

## 测试与未完成项

- 红→绿：真实窗口移动后的气泡锚点；脏区透明清除；被抑制气泡交付返回值；仅状态气泡文字缩放。
- Codex 原有专项：40 passed；架构与产品约束：112 passed。
- Agent、线程、穿透、工作区与气泡相关回归：319 passed、3 skipped。
- 补齐完成开关检查与夹具后，Agent/多 DSH/热更新族：297 passed、2 skipped（102.73 秒）。
- UI/Qt 相关测试：50 passed、1 skipped（后续新增测试单独通过）。
- Ruff、shell 语法与 workflow YAML 解析通过。Node v24.18.0 下 8 个 bridge 测试文件通过，零依赖导入检查通过；CI 使用 Node 20。
- 隔离 WebM 生命周期：41 passed；warm 族开放本地 IPC 后：27 passed。
- 全量首次收集因旧环境缺 NumPy 失败；补齐 requirements 后，沙箱又拒绝 HTTP socket 和用户缓存写入。改用临时 XDG 目录并开放本地 IPC。首轮完整主套件：8294 passed、79 skipped、8 failed（1150.94 秒）；五项是下述已修正的报告/夹具/字体假设，三项是设置导航在全量上下文中的失败。
- 导航测试单独运行：当前分支与未修改主线均为 30 passed、2 skipped；收集全部测试但只执行这三项也通过。四条 workflow 将整个导航测试文件移入独立进程，保留全部断言、不增加重试。
- 修正后四个相关文件合计 167 passed、2 skipped（31.81 秒）；最终按 CI 分组的主套件：8272 passed、77 skipped、19 个既有 Qt 弃用警告（1112.23 秒）；加独立导航 30 passed/2 skipped、WebM 41 passed、warm 27 passed，完整合计 **8370 passed、79 skipped**。
- 主线对照复现关闭 DSH 后仍弹完成提示：定时器约 0.844 秒触发，配置应用约 1.279 秒触发，回调时开关已为 false。补充发送前开关检查后，原回归 1 passed；未用增加延时掩盖。四份旧测试夹具原本仅把 monitor._running 置真但开关仍为 false，现同步设为 true，使测试前提与真实启用状态一致，保留全部断言。
- 初轮 16 个逻辑 CPU 忙循环：每轮 40 passed。最终将配置热更新与 G2 去重纳入后，三轮每轮 61 passed，49.79/50.30/49.70 秒；负载进程均已回收。
- 文档规范：201 passed。远端 CI 与预览包状态将在实际完成后补充，不沿用旧版结果。
- G2 事件去重夹具同步开关后：15 passed。
- 未修改主线同样复现两项灵动岛折叠测试失败：测试搜索下限固定 200px，本机较窄字体需要更小屏宽才全折。改为搜索所有正宽度，保留告警颜色与黑窗断言后：26 passed，未改灵动岛运行代码。
- 文案守卫为当前交付报告增加精确允许项，单项通过，未扩大到所有产品文案。
- Windows/macOS 原生 GUI、混合 DPI、非矩形布局仍未实测；源码 X11 探针不代表冻结包已验证。

## 回滚

原工作区与远端 PR 保持不变。部署后如需回滚，使用旧版程序；卸载菜单中的 Codex 插件，
保留用户会话文件。Qt 修复脚本验证失败会恢复原生库备份；已发布包的回滚应替换完整安装目录。

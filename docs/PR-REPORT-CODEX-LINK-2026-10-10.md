# Codex 菜单安装、会话进展与结构化气泡

差分基线：`fix/pyside612-runtime@f38c186`（前置兼容修复，上游基线`ee699c7`）；分支：`feat/codex-integration-pr`；日期：2026-10-10。
关联：[开发交付规范](DEV-HANDOVER.md#八开发流程规范)、[打包流程](ONEDIR_PACKAGING.md)。本报告只覆盖此独立分支，集成预发布结果不能代替分支验证。

## 核心特性

菜单开启 Codex 时安装本地插件，授权在 Codex 客户端完成。hook 负责生命周期与权限状态，会话 JSONL 提供公开进展和最终回复；气泡显示会话名、活动状态和截断正文。使用文件事件监听，无额外周期文件轮询。hook 超时、异常或缺失脚本返回空成功响应并写脱敏有界日志。默认关闭，兼容原自定义联动配置。

## 修改文件说明

相对上述差分基线的最终文件清单（包含本报告与索引）。

| 文件 | 增删 | 修改及原因 |
|---|---|---|
| `docs/INDEX.md` | +2/−1 | 登记本报告并关联已有文档，避免孤立交付记录。 |
| `docs/PR-REPORT-CODEX-LINK-2026-10-10.md` | +84/−0 | 记录逐文件改动、性能、实机/CI验证、失败历史与回滚；本次末尾补充最终结果。 |
| `integrations/dsh-pet-codex/.codex-plugin/plugin.json` | +17/−0 | 声明本地 Codex 插件身份与能力。 |
| `integrations/dsh-pet-codex/hooks/hooks.json` | +100/−0 | 注册生命周期、工具和权限 hook。 |
| `integrations/dsh-pet-codex/scripts/bridge.py` | +215/−0 | 将 hook 转为有界快照，维护会话、轮次及并发审批状态。 |
| `integrations/dsh-pet-codex/scripts/diagnostics.py` | +105/−0 | 隔离超时和异常，限制日志大小并避免记录敏感正文。 |
| `packaging/pet_entry.py` | +5/−1 | 打包入口在 GUI 启动前分派 hook。 |
| `packaging/pet_entry_no_chat.py` | +4/−0 | 无 Chat 变体同样支持独立 hook 入口。 |
| `pet/__main__.py` | +7/−0 | 在加载 Qt 前分派 hook 子命令。 |
| `pet/agent_bubble_content.py` | +67/−0 | 分离标题和状态，按字形基线绘制正文，提供截断、省略号和末行淡化。 |
| `pet/agent_file_watch.py` | +80/−0 | GUI 线程拥有 QFileSystemWatcher，合并通知并唤醒工作线程。 |
| `pet/agent_link.py` | +306/−16 | 接入 Codex 监控，处理公开进展、最终回复和气泡所有权，避免过期事件覆盖新会话。 |
| `pet/agent_snapshot.py` | +139/−0 | 读取有界快照，合并会话标题、活动与结束回复，提供监听路径和语义超时。 |
| `pet/codex_install.py` | +254/−0 | 发现 Codex 客户端并安装本地插件；运行脚本独立于可删除的插件缓存。 |
| `pet/codex_transcript.py` | +251/−0 | 增量读取 JSONL 与会话标题，跳过历史、私有推理和工具输出。 |
| `pet/config.py` | +40/−3 | 增加 Codex 联动配置及默认恢复、归一化处理。 |
| `pet/context_menus/shared.py` | +7/−0 | 加入 Codex 开关及安装入口。 |
| `pet/hook_runtime.py` | +55/−0 | 提供无需 Qt 的打包 hook 入口，隔离工作进程错误。 |
| `pet/multi_window_shared.py` | +18/−2 | 转发结构化气泡参数，暴露实际展示气泡供所有权判断。 |
| `pet/overlay_shell.py` | +7/−2 | 转发气泡字段，同步虚拟桌面范围及鼠标穿透状态。 |
| `pet/speech_bubble.py` | +57/−4 | 增加自适应 Agent 内容，普通消息保持原布局；接入 X11 工作区策略。 |
| `pet/sprite_bubble.py` | +8/−3 | 转发结构化气泡，使用实际窗口坐标计算锚点。 |
| `pet/window.py` | +7/−35 | 转发气泡参数；将展示辅助逻辑放到 window_alerts，遵守主窗口行数预算。 |
| `pet/window_alerts.py` | +47/−0 | 承接普通及结构化气泡展示，保留提醒优先级和持有时间。 |
| `pet/window_optional_services.py` | +1/−1 | 增加 Codex 在联动服务启用条件中的判断。 |
| `scripts/benchmark_codex_link.py` | +53/−0 | 新增可复现性能测量入口，临时数据不接触用户配置。 |
| `tests/codex_helpers.py` | +19/−0 | 新增回归用例或共享辅助代码，覆盖安装隔离、hook 容错、会话增量、Qt 事件交付或原生 X11 行为。 |
| `tests/test_agent_link.py` | +1/−0 | 更新既有集成测试的配置或支持列表，与新增 Codex 行为一致。 |
| `tests/test_codex_bubble.py` | +95/−0 | 新增回归用例或共享辅助代码，覆盖安装隔离、hook 容错、会话增量、Qt 事件交付或原生 X11 行为。 |
| `tests/test_codex_file_watch.py` | +127/−0 | 新增回归用例或共享辅助代码，覆盖安装隔离、hook 容错、会话增量、Qt 事件交付或原生 X11 行为。 |
| `tests/test_codex_hook_runtime.py` | +141/−0 | 新增回归用例或共享辅助代码，覆盖安装隔离、hook 容错、会话增量、Qt 事件交付或原生 X11 行为。 |
| `tests/test_codex_install.py` | +40/−0 | 新增回归用例或共享辅助代码，覆盖安装隔离、hook 容错、会话增量、Qt 事件交付或原生 X11 行为。 |
| `tests/test_codex_transcript.py` | +270/−0 | 新增回归用例或共享辅助代码，覆盖安装隔离、hook 容错、会话增量、Qt 事件交付或原生 X11 行为。 |
| `tests/test_desktop_pet_features.py` | +13/−1 | 更新既有集成测试的配置或支持列表，与新增 Codex 行为一致。 |

## 性能分析

环境：Ubuntu 24.04、Python 3.11.16、Qt 6.11.2，16 逻辑 CPU。以下是同一实现的集成版本本轮实测；同时有全量测试运行，不用于宣称相对上游加速比例。

命令：`.venv/bin/python scripts/benchmark_codex_link.py`。16 活跃会话、2000 次未变快照读取，中位数/p95 为 96.03/146.65 µs；直接 bridge 子进程 30 次为 24.72/26.04 ms。额外 2000 次读取消耗净保留 192 B、峰值 7792 B（tracemalloc，非 RSS）。每个 hook 启动 supervisor 和 worker，1 秒超时；工作线程等待文件事件及语义截止时间，40 ms 合并通知、0.5 秒气泡刷新间隔。没有新增网络或 Python 读取线程；有快照/日志写入及只读标题索引访问。活动解析上限 16 会话，单次读取预算及行长有界，日志 128 KiB 加一份轮转。

## 实机运行记录

本机 CLI/App/IDE 三种核心在隔离 CODEX_HOME 中安装、卸载及旧 hook 存活测试 9 passed，用户 profile 和信任未修改。真实 Qt 共享代理到 Overlay 气泡验证首条及后续更新；用户此前已确认看到气泡和动画。Windows/macOS 的原生桌面及三客户端实际授权仍需对应客户端验收。

## 测试与验证

开发阶段先在临时回归中复现旧实现失败再修复，本轮把必要用例整理到 tests。独立分支的聚焦、全量和满载结果在下方追加。

## 风险与回滚

Codex 本地 JSONL 格式可能变化；用户必须自行确认 hook 信任。日志不保存提示词和工具输出。卸载后保留不可变 hook 脚本，避免旧会话调用缺失路径。回滚程序后重启；不自动修改 Codex 信任设置。

## 最终交付记录（2026-10-10）

完整集成提交`6ae3519`的[三平台CI](https://github.com/Huffer342-WSH/dsh-pet-indesktop/actions/runs/38044045940)及Linux/macOS/Windows三条构建均通过；[预发布](https://github.com/Huffer342-WSH/dsh-pet-indesktop/releases/tag/preview-4.2.1-codex.20261010.1)已公开，包含8份产物。发布标签指向实际构建提交，后续报告更新不改变安装包来源。

最终Linux纯桌宠包在本机隔离配置、缓存、用户数据和网络后，offscreen及原生X11各运行15秒无提前退出或Traceback；frozen hook退出0、输出{}、stderr为空，无_MEI目录。独立进程加载包内两份原生库并核对/proc/self/maps后，六项单例引用探针全0。ZIP SHA256：`5abaa92b2becb6fd2233a30df0d0a42af191a469792af714b06d32eac20fef85`。Windows/macOS的原生桌面人工验收仍未完成。

独立分支按仓库CI方式分进程覆盖全套测试（没有跳过失败用例）：

| 分组 | 结果 |
|---|---|
| main | 4253 passed, 37 skipped, 21 warnings in 178.69s (0:02:58) |
| webm | 41 passed in 25.60s |
| warm | 27 passed in 31.35s |
| recovery | 5 passed in 0.26s |

聚焦、ruff和diffcheck均通过；最终提交仅追加本报告，应用、工作流及测试代码与上述验证时一致。

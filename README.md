# SkillRadar MY · 可运行第一版

SDC Hackathon 2026 **Domain 1**：AI 时代职业转型与学习规划。目标用户是希望了解自身技能差距的学习者和转岗者；沿用既有项目的马来西亚背景。最终目标地区、团队成员分工和正式项目表述待团队确定。

## 当前功能与边界

- 默认显示虚构用户“小林”，可选择 Excel、基础统计、沟通、SQL、Python、数据可视化。
- Python 服务模块将技能与 **3 个示例岗位**比较，显示覆盖率、已具备技能和缺少技能。修改选择立即重算；空选择显示 0%。
- 覆盖率 = 去重后的已具备岗位要求技能数 / 去重后的岗位要求技能总数。忽略大小写、首尾空格与空技能；拒绝异常类型及空岗位要求。计算保留精度，仅页面百分比格式化。
- **技能覆盖率不是录用概率**；不衡量熟练程度、资历或真实招聘条件。
- 用户、岗位及要求全部是模拟数据。**未接入真实 AI／就业趋势、课程、实时招聘数据或预测。**
- 侧栏保留旧版实验功能：三语言页面、仅供虚构文件使用的本地关键词解析、7 个实验岗位、模拟趋势与综合评分、估算学习顺序、SDG 标签、两种假设情景。它们不构成经过验证的职业建议。没有网页到 RunPod 的调用，没有数据库或模型训练。
- 完整产品待完成：可更新且注明出处与日期的真实趋势；有真实课程支持的个性化路线；岗位和技能的 SDG 关联理由；有依据并显著标注假设的未来情景。未新增登录、支付、真实简历上传或复杂设施。

## 技术栈与文件

保留 **Python 3.12 + Streamlit**，网页和服务逻辑在同一仓库、同一进程运行，无需 Node/Express 或独立数据库。

| 文件 | 用途 |
| --- | --- |
| `app.py` | 唯一网页入口；默认最小页面，可切换既有实验页面 |
| `src/demo.py` | 最小页面、示例校验、调用后端比较 |
| `src/utils.py` | 可独立测试的服务端去重与覆盖率；保留旧评分功能 |
| `src/main.py` | 复用同一数据和计算的 CLI 检查入口 |
| `data/demo.json` | 虚构用户、六项技能、三个示例岗位 |
| `data/experimental.json`、`data/trends/latest.json` | 旧实验数据及显著标注的模拟趋势 |
| `requirements.txt` | pip 运行依赖的完整固定版本清单，兼作锁文件 |
| `requirements-dev.txt`、`pyproject.toml`、`tests/` | 开发检查依赖、类型配置与核心测试 |
| `.replit` | Replit 运行/发布候选配置，未在 Replit 验证 |
| `runpod/` | 保留的独立规则匹配实验，未接入网页，非 GPU/模型使用证明 |
| `docs/project-record.md` | 实际决策、来源、工具、材料审核、验证和归档清单 |

未引入 JavaScript，因此不添加 `package.json` 或 npm 锁文件。没有数据库配置、迁移或持久化用户资料。

## 本地安装与开发

以下命令在**内层仓库根目录**执行：`D:\Hackathon\本地代码\sdc2026-lumina-nusantara`。安装 Python 3.12 后使用真实可执行程序；如果 `python` 仅指向 Windows 应用商店，请修正本机 Python 配置。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

浏览器访问终端显示的本地地址，默认 `http://localhost:8501`。也可在安装后双击 `启动 SkillRadar.bat`；启动脚本使用本项目 `.venv`，不依赖开发工具的私人路径，不在运行时自动安装依赖。

macOS/Linux 使用 `python3 -m venv .venv`，后续将命令中的 `.\.venv\Scripts\python.exe` 替换为 `.venv/bin/python`。本次只验证 Windows/Python 3.12。

## 构建与生产启动

Streamlit 不需要前端打包。以下编译检查生成被忽略的 Python 字节码，并检查依赖；这不等于部署：

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m compileall -q app.py src tests runpod
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
```

停止服务按 Ctrl+C。服务器正式发布时应由平台管理进程、域名和 TLS；本次没有发布，也不声明既有演示地址仍有效。

## 环境变量

最小版本无需密钥，无需复制 `.env.example`，应用也不会自动加载 `.env`。

| 变量 | 当前用途 |
| --- | --- |
| `PORT` | 仅 `python app.py` 便捷入口读取；空值或未设时为 8501。直接运行 Streamlit 请使用 `--server.port` |
| `RUNPOD_API_KEY`、`RUNPOD_ENDPOINT_ID` | 保留给历史实验；当前网页和处理器不读取，不要为运行最小版本填写 |

`.env.example` 仅保留空值和说明；真实凭证使用本地或平台秘密配置，不提交。

## Replit 运行与发布（未验证）

1. 导入这个 GitHub 仓库，选择 Python 3.12 环境。
2. 在 Replit Shell 执行 `python -m pip install -r requirements.txt`。
3. Run 使用 `.replit` 启动 Streamlit，内部端口 5000 对外映射 80；无需 Secrets。
4. 如需发布，选择支持常驻 Python/WebSocket 的部署方式，检查 `.replit` 的 build/run 和平台端口设置。生产命令支持平台注入的 `PORT`，默认 5000。
5. 团队实际验证后收集项目地址、时间、运行日志和截图；本次未登录、发布或验证 Replit，Linux 依赖兼容也待验证。

RunPod 不是第一版的依赖。`runpod/requirements.txt` 与根依赖隔离；不要将现有脚本认定为已经调用 GPU 或模型。证明材料的核验和收集说明见项目记录。

## 验证方法

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover tests -v
.\.venv\Scripts\python.exe -m mypy
.\.venv\Scripts\python.exe tests/check_cv_intake.py
.\.venv\Scripts\python.exe src/main.py
```

`tests/test_coverage.py` 覆盖双侧去重、精确分数、空输入、异常类型、无效岗位资料和更改技能后的变化；已有 6 个评分测试仍保留。网页测试方法和本次实际结果见 `docs/project-record.md`；未执行的事项不视为通过。

本次已实际完成 13 个核心测试、类型/依赖/编译检查和 Chrome 页面操作，详细范围见项目记录。浏览器复现：服务启动后在另一终端运行 `.\.venv\Scripts\python.exe tests/check_browser.py`（需要本机 Chrome）。

人工验证：默认用户覆盖率依次应为 **25%、66.7%、0%**；增加 SQL 后应为 **50%、66.7%、33.3%**；清空后全部为 **0%**。浏览器刷新会重新载入默认示例，不持久化用户资料。

## 数据、许可证与既有材料

采用现有完整 [Apache License 2.0](LICENSE) 正文。第三方库保持各自许可；不将赛事模板、截图或第三方资料一概认定为本项目原创或 Apache 授权。

所有本版岗位、用户与趋势权重为手写演示资料。旧趋势文件曾把 WEF 链接及日期附在未验证权重上；已去除这一来源暗示，无真实抓取日期。旧学习路径曾指向 HRD Corp 通用首页，未核验课程、费用或报销资格，现不再将其展示为真实课程。

旧指南和重复索引已备份到仓库外并清理；历史提案、图片和 `submission/` 保留待审，可能含与当前实现不符的数字、平台声明或个人信息。已从当前提案文本去掉队长联系方式，**Git 历史仍可能公开这些信息**；本次不改写历史。来源、授权、参与时间、正式成员与证明材料均需团队复核。避免提交签名表、联系方式、真实简历和未获许可数据。

不自动提交、推送或部署。现有 Git 提交历史完整保留。

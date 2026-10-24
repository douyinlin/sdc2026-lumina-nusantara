# Replit 运行与提交入口核验 — 2026-10-24

## 当前入口（不是发布声明）

| 用途 | 入口与限制 |
| --- | --- |
| 仓库 | https://github.com/douyinlin/sdc2026-lumina-nusantara |
| 现有 Replit 项目 | https://replit.com/@duyulin18/SkillRadar-MY-Streamlit-app |
| 开发 Preview | 在项目中点击 **Run → SkillRadar MY**。本次实际浏览器目标为 https://b9574879-d211-4067-9e3d-3ce14e31ad8e-00-1wwrcrdruvxai-n7mih400.sisko.replit.dev/ |
| 公开演示（已有） | https://sdc2026-lumina-nusantara-65cnugvuxdle5dgp9ky3fs.streamlit.app |
| Replit 公开部署 | 部署服务查询成功：`isDeployed=false`、无公开域名、无成功生产构建。本次没有发布或更改可见性。 |

开发地址属于本次工作区会话，可能变动、停止或受访问权限限制，不是永不休眠的
生产/评审地址。工作在任务分支中，须合并后才进入主工作区；不代表主项目已更新生产。
2026-10-22 的匿名 “Page not found” 记录不能证明项目不存在、被删除或为私有项目。

## 版本与改动边界

- 实施前工作区 SHA：`b2ff3d92b909641bd505cfc621d9ec729e9325aa`。
- 本次重新检查的上游 main：`73b4f344efeaaed281d7f1d0eac384f329897d04`。
- 三语浏览器验收的工作区运行代码：`88e70833b1cfdfbd26bc61593428f6ba2ae8d087`。
- 最终运行源提交：`56a803a72fa7c094dcbcf03d0146bde963187d57`；
  与上述浏览器版仅差 PolarAxes 类型标注和 SDG 局部变量更名，无评分或交互逻辑变化。
  最终版通过 mypy、单元/页面检查；文档及提交包更新不改变运行源。
- 同步原 Python app、src、data、static、测试及必需 docs 资源。
  保留此前已合并的选人后界面与 SDG 按钮 rerun 修复，不另建应用、不替换 React、
  不另启固定端口服务，不改匹配算法、权重、解析规则或业务数据。
- 上游修复以专用分支 PR 交付：https://github.com/douyinlin/sdc2026-lumina-nusantara/pull/2 。
  未直接推 main，未自动合并；Replit 专用 artifact/工作流基础设施不写入上游独立项目配置。
- Replit web artifact 继续拥有 `/` 与 `/_stcore/stream` 路由。Run 使用注入的 `PORT`，
  绑定 `0.0.0.0`。安装写入 `.pythonlibs`，不写不可变 Nix Python。

## 依赖与检查

环境：真实 Replit Linux，Python **3.11.14**。直接运行依赖：
Streamlit **1.66.0**、pandas **3.0.6**、NumPy **2.4.6**、
PyArrow **26.0.0**、Matplotlib **3.11.2**、pypdf **6.10.0**。

上游 NumPy 2.5.4 的安装元数据要求 Python >=3.12；原样安装在这里失败。
最小修复仅按 Python 版本区分 NumPy：3.11 使用可安装的 2.4.6，
3.12+ 保留上游 2.5.4，其余直接依赖精确版本不变。这不是完整传递依赖锁。
安装时 pip 曾提示预装包冲突，最终 `python -m pip check` 为
`No broken requirements found`；未通过绕过系统保护安装到 Nix。

| 检查 | 结果与范围 |
| --- | --- |
| `python -m unittest discover -s tests -p 'test_*.py' -v` | **57 passed**；包括上游测试及现有工作区导航、SDG 回归 |
| `python tests/check_cv_intake.py` | **2 passed**，合成文本与不支持的 PDF 边界 |
| `python -m pip check` | 通过 |
| `python -m mypy --config-file team/dev-env/pyproject.toml` | 通过，11 个源文件 |
| 真实开发域名浏览器 | HTTP 200；`/_stcore/stream` 收到 **3969** 帧；无捕获到的 page error |
| 三语交互 | English / Bahasa Malaysia / 中文首页，空档案禁止继续，合成 CV → 推荐结果 → 学习路径，DOSM 图表可见，SDG 展开/关闭且按钮状态一致 |
| 共享路径 | English HR 与就业中心 intake → results 烟测；三语页面覆盖另有单元集成测试 |
| Streamlit Cloud | 无痕、未登录浏览器 HTTP 200，实际 app iframe 与开场页可见；不是只检查外层健康页。不能由此确认其部署 SHA 或认定与本工作区完全同版。 |
| 门户 | `https://sdchack.my` 可达；未登录提交门户、未上传、未勾选声明、未提交 |

浏览器仅用 `Fictional profile for software testing: SQL Python Excel communication`，
没有上传真人 CV。课程价格、许可证、统计事实、用户调研及签字内容不在此次核验范围。

## 可复现方式与证据

在项目根目录：

```sh
sh scripts/install-python-deps.sh
python -m unittest discover -s tests -p 'test_*.py' -v
python tests/check_cv_intake.py
python -m pip check
```

点击现有 Run 工作流后，用已安装的 Playwright/Chromium 执行：

```sh
python tests/check_replit_preview.py --url https://<actual-development-host>/
python -m mypy --config-file team/dev-env/pyproject.toml
```

测试依赖不是应用运行依赖。本次仅在忽略的 `.cache/test-python` 安装测试工具，
通过 `PYTHONPATH` 运行；不建替代本地应用服务、不使用容器/虚拟环境。

真实截图、报告与日志保存在忽略目录
`generated-artifacts/replit-acceptance/`：
`entry.jpg`、`landing-{en,ms,zh}.png`、`intake-*.png`、
`results-*.png`、`sdg-*.png`、`p2_btn.png`、`p3_btn.png`、
`report.json`、`community-cloud.png`、`community-cloud.json`、
`unit-tests.log`、`run-console.log`。
这些是本次采集，不替换历史证明 PDF，不伪造账号或生产部署截图。

## 发布配置已准备，但必须另行确认

现有 artifact 的生产命令以 artifact 目录为工作目录：

- build：`python build.py` → 从仓库根执行 `scripts/install-python-deps.sh`；
- run：`python run.py` → 原根目录 app.py，使用注入 PORT；
- startup health：`/_stcore/health`；
- HTTP `/` 和 WebSocket `/_stcore/stream` 路由保留。

这消除了旧生产构建直接向 Nix Python 安装以及命令工作目录不匹配的问题。
配置准备不等于已经执行生产发布。

按 Replit 官方文档，**Reserved VM** 适合持续运行、长连接/有状态会话的服务；
**Autoscale** 按流量扩缩，更适合可接受启动等待和重连的演示，但必须在发布后单独验证
Streamlit 会话和 WebSocket。Static 不适用 Python 服务。当前项目保留原有 Autoscale
设置，未替用户切换产品或购买容量。

发布会使用套餐额度并可能产生额外计算/内存及流量费用；Reserved VM 为持续资源，
不是“无人访问就一定免费”。实际机器规格、地区、账户额度与费用须以本人 Publishing
面板报价为准，不提供未经核验的固定价格承诺。参考：

- https://docs.replit.com/features/publishing/deployment-types
- https://docs.replit.com/billing/about-usage-based-billing
- https://docs.replit.com/billing/managing-spend

下一步需要负责人明确确认：是否公开发布、选择的部署方式/预算，以及评审访问方式。
获批后才可发布，再匿名验证真实域名、运行版本与核心流程，最后更新 README、
CONTENTS 和门户字段。未经确认不发布、不猜 `replit.app` 地址、不改可见性。

## 门户字段与剩余人工动作

1. Repository：填写上面的 GitHub 仓库 URL。
2. Application / Demo：目前可填写已有公开 Streamlit Cloud URL；它不是 Replit 部署。
3. Replit project / proof：填写完整 Replit 项目链接，附本次真实运行报告/截图。
   若字段明确要求 **Replit deployed app URL**，目前应留待发布后补齐，不能填 Preview 冒充。
4. Proposal / Technical Declaration / Slides：使用上游已签署原件；
   本次不改 PDF、不代签。负责人须检查新文字状态与既有签署声明是否一致。
5. Video：README 的视频仍为 TODO，需本人提供最终链接。
6. 负责人登录正式门户审核材料、委员会访问权限及赞助商/真实性声明，最终上传并保存回执。
   本任务未获得门户登录方式，也未替本人作真实性承诺。GitHub PR 不等于门户提交。

提交 ZIP 的历史副本含旧 README。更新后的打包脚本将当前 README、CONTENTS、
OWNER_ACTIONS 和本报告一起打包，签字 PDF 字节保持不变；生成文件放忽略目录，
由本人核对后选择最终材料，不自动提交。

当前可下载新包由 Replit Library 的 **SkillRadar 提交材料包** 卡片交付；
原件的可访问固定版本链接见 `submission/CONTENTS.md`。工作区不含签署二进制文件，
因此重建时使用 `python team/tools/build_bundle.py --fetch-originals`（需 build-only
依赖 python-pptx），或显式传入 `--submission-dir`；不要使用缺失原件的默认目录。
下载仅写入忽略目录，且逐件核对预先固定的 SHA-256。

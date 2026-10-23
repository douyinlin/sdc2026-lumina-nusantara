# Local repair record — 2026-10-22

Baseline: `aca35ad`, `main`, clean worktree before changes. The local repair phase
performed no commits or pushes. The user subsequently authorized committing and
pushing this repair to `main`. No deployment, history rewriting or existing
team-file deletion is part of this change.

## Implementation decisions

- Keep Python/Streamlit and the existing screens. Worker target fields are separate
  from graduate study fields; workers default to an unrestricted catalogue.
- Normalize and deduplicate requirements before both weighted and count coverage.
  Reject invalid requirements and tiers instead of silently scoring them.
- Extract the existing synthetic-CV keyword parser into `src/cv.py`; include catalogue
  skill names and use word boundaries. PDF support remains limited to simple text
  streams, not scanned or arbitrary PDFs. No real CV was used for testing.
- Course duration uses ceiling(hours / weekly hours), with explicit provenance.
  Existing hours/fees were not independently reverified; no new duration or price
  was invented. Missing hours retain the old model as a labelled team estimate.
- Choose validated manual trend import rather than an unverified scraper. Preserve
  source dates, evidence and mapping notes; do not treat DOSM occupations as skills.
  Import failures preserve the active snapshot and surface a warning.
- Change claims about experience/urgency/budget/education to match actual behavior:
  these fields are recorded only. Highest score after learning can change roles.

## AI tool use and review status

Codex was used for code inspection, implementation, regression tests, local browser
checks and documentation. No additional model/API/GPU service was introduced.
Automated tests and code-diff inspection were performed by the coding assistant.
Team members still need to review the changes, validate source/course metadata and
explain the scoring assumptions. This record does not claim completed team review
or replace the official Technical & Tools Declaration.

## Executed validation

- 34 unittest tests passed, including Streamlit results across English, Chinese and
  Malay for worker, graduate, HR and career-centre flows; worker field selection,
  identity switching, study-hour changes and source switching.
- `tests/check_cv_intake.py`: both synthetic parser tests passed.
- mypy: 11 source files checked, no errors.
- `pip check`: no broken requirements.
- Local Streamlit server and real headless Chrome: empty input, synthetic upload,
  edited upload, target field, weekly hours, results, source/scenario switch, SDG
  expansion and mobile-width capture passed without page errors. Ignored artifacts:
  `test-results/browser-fixed/`.
- Manual import success/failure and last-valid preservation were tested in temporary
  directories; production evidence snapshots were not overwritten.

## Remaining manual work / limitations

No live source/course verification, Replit deployment or RunPod execution was done.
Existing Replit proofs and submission materials were left unchanged. Team should
verify the repaired commit in its own Replit project and collect matching proof.
Existing course descriptions, prices and hours require provider-by-provider review.
The UI retains Streamlit deprecated-API warnings; broad dependency ranges remain.
Per-skill SDG reasoning and advanced HR gap modelling remain outside this repair.
A tracked `team/proof/signature.png` already existed; team must check whether it
contains a signature that should not be public. No history rewriting was attempted.


## 本次提交说明

本次保留 Python／Streamlit 结构，修复推荐逻辑并补齐可复现测试：

1. 在职用户新增目标领域选择，默认不限领域；与毕业生专业独立保存，切换身份不串用。
2. 统一技能规范化与去重，修复岗位要求 `sql、SQL` 导致覆盖率低估的问题；明确数量覆盖率、加权覆盖率和综合分数的区别。
3. 提取简历关键词解析模块，识别目录中的标准技能名称及别名；替换失效的旧测试入口，修复类型检查错误。
4. 学习周数按课程小时数除以每周学习时间向上取整；总时长按顺序学习累计，区分目录估算与团队估算，提示缺少课程资源。
5. 新增趋势 JSON 人工导入工具：校验来源和资料、保留有效旧快照、原子替换、记录并显示导入失败状态；不宣称实时抓取。
6. 修正三语言文案：经验、紧迫程度、预算及部分教育资料目前仅记录；学完后的最高匹配分可能对应不同岗位。
7. 更新 README、环境变量说明及忽略规则；新增评分、时长、导入、简历与多语言页面回归测试。

验证：34 项单元及页面集成测试、2 项独立简历检查通过；mypy 检查 11 个源文件通过；依赖检查与本地 Chrome 主流程通过。

边界：未在 Replit 上运行或部署，未重新逐条核验外部来源和课程价格／时长；团队仍需人工审核。测试截图、日志、缓存及本地导入状态不纳入提交。


## 第二轮修复（基于 68559e5）

开始时：main / 68559e5，工作区干净。本地修复阶段未提交、推送或部署；用户随后明确授权总结本次修改并提交、推送到 main。未修改既有 Git 历史，保留原有来源快照、提交材料及历史记录。

- 趋势原始名称 skill、团队原始映射 model_skill 和规范化匹配键 match_key 分开保留；校验、导入、读取、评分、解释与学习排序共用匹配规则。
- 空键、异常类型及规范化重复键报错。明确未映射项使用空匹配键，只作背景；未命中目录的来源类别不影响岗位分数。导入失败保护及页面提示保留。
- 统一中／英／马来语课程标题、提示和披露；现有价格及小时数未重新核验。原 extraction_note 的历史核验声明保留为 legacy_extraction_note，不当成本次核验。
- 技能迁移百分比旁直接标明团队规则系数，不代表实测能力迁移。
- 依赖采用直接依赖精确固定版本，不导出 Windows 完整环境，也不建立第二套锁文件。传递依赖仍由 pip 解析；并非完整哈希锁定。
- 补装此前缺少的 Matplotlib 3.11.2，浏览器测试新增实际雷达图显示断言。替换弃用的 use_container_width 和组件 HTML 接口，使用 width 与 st.iframe；调整零尺寸辅助 iframe 为正尺寸。
- 因绘图依赖恢复，类型检查开始覆盖实际 Matplotlib 类型；使用明确的 PolarAxes 类型收窄，不关闭检查或忽略错误。

工具与核验：Codex 用于修改、测试和文档；Firecrawl CLI 用于只读检索 Streamlit 官方资料和查看已有 Replit 项目链接，没有成为产品运行依赖。官方接口资料和本地 1.66.0 签名均已检查。未访问课程提供方页面作本次核验，也未调用模型 API 或 GPU 服务。团队人工审核仍待完成。

实际验证：43 项单元／页面集成测试通过；独立简历检查 2 项通过；mypy 检查 11 个源文件通过；按固定版本安装依赖及 pip check 通过。本地 Chrome 验证领域、资料修改、学习时间、来源／情景切换、学习路线、SDG 展开、粒子 iframe、雷达图及手机宽度截图，无页面错误。测试产物在忽略目录 test-results/normalized-trends-browser/。

Replit：.replit 的 Python 3.12、安装和启动配置已检查。在现有 team/SLIDE_BRIEF.md 中找到具体项目 https://replit.com/@duyulin18/SkillRadar-MY-Streamlit-app 。2026-10-22 只读访问返回 Page not found，并提示联系所有者邀请访问。不能据此确定项目是否私有、改名或删除；没有进入工作区、运行、同步代码或部署，也无法核对远程运行版本。需项目所有者提供访问权限／有效 Preview，在团队项目上验收已审核提交并保存证明。Linux 环境也尚未实际运行。


## 输入状态与预检查修复（2026-10-22—23，基于 b6c0837）

开始时仓库为 main / b6c0837，工作区干净；23 日恢复任务时保留昨日六个文件的修改，未发现新增变动。本轮不提交、推送或部署，不更改历史。

- 将上传解析结果、手动草稿、确认技能分开保存。按文件内容 SHA-256 判断是否需要重新解析；同名不同内容会重新解析并替换确认技能、重置草稿，同内容不会在重跑时覆盖手动修改或清空结果。
- 搜索与分类共享草稿，通过控件回调同步。未编辑时禁用应用；主动编辑后的空草稿可应用为空。新增清空按钮，同时清除确认技能、搜索和分类选择，但保留已处理上传标记。空技能禁用继续；继续只使用已显示的确认技能。三语言同步说明此规则。
- 实际 Chrome 验证发现每轮渲染重写选择控件状态会丢失选择，而 AppTest 未捕获；改为回调同步后重新通过真实浏览器组合流程。
- 趋势预检查与正式导入共用完整校验入口，包含来源域名、日期、必填信息、规范化键、重复键及映射规则。预检查只读，不写快照、备份和状态；成功不代表外部事实或写权限已核验。正式导入失败保护及原始来源文本保持原有设计。
- 新增上传／手动修改／清空／同名新内容／搜索分类同步页面测试，以及预检查来源不匹配、只读和失败保留快照测试；扩展实际浏览器检查。

最终验证：49 项单元及页面测试通过；独立简历检查 2 项通过；按 team/dev-env/pyproject.toml 配置的 mypy 检查 11 个源文件通过；pip check 通过；本地 Streamlit 启动成功。早先省略 mypy 配置的调用失败，最终使用仓库配置重新执行成功，未通过忽略错误规避。

Chrome 英文在职用户流程通过：虚构 SQL 文件上传→手动 Excel→应用→调整学习时间→继续，结果保持 Excel；保留上传时清空并重跑不恢复；同名新内容能解析；领域、来源、情景切换、学习路线、SDG、雷达图及手机截图通过，无页面错误。三语言、在职、毕业生、HR 和职业中心的输入／结果回归由 Streamlit 页面测试覆盖，不宣称全部角色及语言都做了真实浏览器端到端测试。产物位于忽略目录 test-results/input-state-browser/，日志不提交。

工具：本轮使用 Codex 修改、测试、整理文档，Playwright 驱动本地 Chrome；未引入模型服务、数据库或保存真实简历。团队仍需审核代码和演示行为。未重新核验外部课程与趋势事实，未实际运行 Replit 或 Linux；当前结果对应 b6c0837 上的本地未提交修改，不代表远程部署验收。

提交授权补记（2026-10-23）：完成本地修复与验证后，用户明确要求总结并推送。推送前发现 origin/main 新增 881e630（全应用粒子背景），将保留该提交并合并验证；不强制推送，不更改已有历史。

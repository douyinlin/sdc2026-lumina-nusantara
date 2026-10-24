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

合并验收：已通过普通 merge 保留远程 881e630；合并后重新执行 49 项单元／页面测试、2 项简历检查、配置化 mypy（11 个文件）及 pip check，全部通过。粒子 iframe 更名导致旧浏览器定位断言失败，按实际标题更新定位后，完整 Chrome 在职用户流程通过且无页面错误。随后按用户授权普通推送 main，不部署。


## 2026-10-23 · 提交包缺口修复（技能级 SDG、课程、口径）

外部审计指出五项缺口，本轮处理其中四项数据与文案问题：

- **技能级 SDG**：新增 `data/skills_sdg.json`，把 54 个目录技能映射到 SDG 目标（按技能族，
  每个技能两个目标，主力是 4.4）。结果页第 5 节新增"这些技能对应的 SDG"区块，
  并明确标注这是团队自己的解读、不是联合国官方映射。新增测试 `tests/test_skill_sdg.py`。
- **课程覆盖**：`data/courses.json` 从 10 条扩到 36 条，覆盖 30/54 技能。所有新增链接
  都用 HTTP 请求确认过返回 200；课时标为估算（`duration_verified: false`），
  `verification_status` 保持 `pending_team_review`（团队复核仍未完成）。
  无课程的技能改为给出课程搜索入口，不编造资源。
- **中文缺口句**：`gap` 字符串参数顺序错误，渲染成"1 项必备技能中缺 3 项"，已改为
  "共 {2} 项必备技能，缺 {1} 项"。
- **WEF 口径**：4 个岗位原写 "WEF ... (Malaysia sample)"，与 README 的"全球预测"矛盾，
  统一改为 "global employer survey" 并在 note 里写明不是马来西亚实测。
- **SLIDE_BRIEF**：数据从 DOSM 2025 Q2 更新到 2026 Q2（555,509，环比 -11.4%），
  课程表述从"已核实"改为"链接真实、价格课时待复核"。

未处理：PPT 与演示视频（交付物）、赛事委员会账号、Technical Declaration 补 Codex——
需要本人在 GitHub / 门户上操作。

---

## Repair and validation — 2026-10-22 (moved from README)

## Repair and validation — 2026-10-22

Worker targets default to all fields and use separate state from graduate study
fields. Skills are deduplicated on both sides of weighted and count-based coverage.
Coverage is not a hiring probability. Scoring weights, transfer coefficients and
scenario assumptions are team heuristics, not observed hiring outcomes.

Skills, selected field and evidence/scenario affect matching. Weekly study hours
change duration. Work experience, urgency, budget, degree level, internship months
and graduation year are recorded only; they do not affect scoring or course filters.

Study steps are sequential. For a positive recorded course duration, weeks are
`ceil(course hours / weekly study hours)`. Existing catalogue hours are explicitly
labelled unverified estimates. A future verified record must include
`duration_verified: true` and `duration_source_url`. Missing/invalid hours use the
original team assumption (`round(skill cost * 6)` weeks at 8 hours/week), labelled
as a team estimate. Total weeks sum rounded step durations. Source verification
and course access/fees remain team tasks. Completing a step is a hypothetical
skill acquisition; the highest-scoring role after the plan may change.

### Updating the data from inside the app

The results page carries a **"Update the trend data with a reviewed snapshot"** panel. It accepts a
JSON file with the same schema as `data/trends/`, validates it with the same function the CLI uses,
and shows a before/after table (score shift and rank change) for the current profile. Applying it
changes the ranking for that browser session only - it never writes to the repository, so a demo
cannot fake a data update.

A sample file lives at `data/trends/sample_upload_example.json`; it is an **illustrative fixture**,
not a new measurement. A permanent update stays a maintainer step, below.

### Validated manual trend update

1. Read the original source linked in the existing WEF/Jobstreet JSON. Review its
   scope, date, skill direction and any taxonomy mapping. This is a human review,
   not an automatic claim that a page was fetched or checked.
2. Prepare a JSON file outside the repository, preserving the existing schema.
   Include `source`, HTTPS `source_url`, `published`, `retrieved_at`,
   `extraction_note`, and non-empty `skill_signals` with `skill`, `direction`,
   `evidence`. Proxy mappings must have `mapping_note`. Do not invent percentages.
   Preserve `skill` as the original source name and `model_skill` as the team's
   original mapping text, with `mapping_note` explaining proxies. The importer
   derives `match_key` using the scoring normalizer (trim + casefold). It rejects
   blank/invalid keys and normalized duplicates. Do not hand-maintain `match_key`:
   it is regenerated on import/read. `mapping_kind: "unmapped"` with no
   `model_skill` produces `match_key: null` and cannot affect scoring, even if its
   name happens to match a known skill. Other unknown catalogue keys also remain
   context only. The UI retains source names, not internal matching keys.

3. Validate, then import (replace the example input path with your reviewed file):

```powershell
python -m src.trends wef "C:\path\reviewed-wef.json" --check
python -m src.trends wef "C:\path\reviewed-wef.json"
# For the other source, replace wef with jobstreet.
```

Successful imports atomically replace only the selected source, keeping an ignored
`.json.bak` of the previous valid snapshot. Validation failure leaves it unchanged.
Ignored per-source `.*-import-status.json` records the attempt; the UI warns after
failed imports. A missing/corrupt active snapshot produces an explicit error,
not a simulated replacement. Re-run the page after importing. Review `git diff`
and the original evidence before manually committing. DOSM occupation panels
remain separate from skill scoring; update those manually and review their diff.

### Reproduce checks and run

```powershell
python -m pip install -r team/dev-env/requirements-dev.txt
python -m unittest discover tests -v
python tests/check_cv_intake.py
python -m pip check
python -m mypy --config-file team/dev-env/pyproject.toml
python -m streamlit run app.py --server.headless true
# In a second terminal, using an installed Chrome:
python tests/check_post_selection_ui.py --url http://localhost:8501 --browser "C:\Program Files\Google\Chrome\Application\chrome.exe" --output test-results/browser
```

There is no separate frontend build: Streamlit runs the Python application.
For hosted startup use `python -m streamlit run app.py --server.address 0.0.0.0
--server.port 5000 --server.headless true` on one line. `.replit` already includes
build/install and startup settings; importing and running this commit on the
team's Replit account is still required. No API key is needed. `.env` is not loaded
by the app; `PORT` is used only by the `.replit` deployment shell command. RunPod
variables are reserved for the disconnected optional experiment.

Validation performed locally: unit/integration tests, dependency consistency,
mypy and a Chrome worker flow with field selection, edited synthetic skills,
study hours, evidence/scenario switching and SDG display. See
`team/DEVELOPMENT_LOG.md` for actual results and remaining limitations.


### Follow-up validation — baseline 68559e5

The trend importer, runtime loaders, scoring, explanations and pathway ordering
now share canonical matching keys without changing source wording. Course titles,
notes and disclosures agree in all three languages: recorded provider links and
fees/hours require verification; team-estimated time is separate. Transfer
percentages are labelled team rule coefficients, not measured ability transfer.
The historical extraction note in `data/courses.json` is retained as legacy team
metadata, not treated as fresh verification.

Runtime requirements use **exact direct pins** in `requirements.txt`; development
checks use the same policy in `team/dev-env/requirements-dev.txt`, which includes
runtime requirements and only the two direct check tools. This is not a Windows
`pip freeze` export, a full transitive/hash lock, or proof of Linux compatibility.
Transitive packages are still resolved by pip. Validated environment: Windows,
Python 3.12, Streamlit 1.66.0, pandas 3.0.6, NumPy 2.5.4, PyArrow 26.0.0,
Matplotlib 3.11.2. The previously missing Matplotlib package is now installed and
the real browser test asserts the DOSM chart is visible.

Deprecated container-width arguments were replaced with `width`, and repository-owned
static HTML/JavaScript uses `st.iframe`. The API was checked against installed
Streamlit 1.66.0 and its [official iframe reference](https://docs.streamlit.io/develop/api-reference/text/st.iframe).
Only repository-authored static scripts are passed to this iframe; evidence and
uploaded content are not embedded in it. Browser checks include the particle
canvas, source/scenario controls, study plan, SDG image and mobile capture.

Previous validation (baseline 68559e5): **43 tests passed**, including normalization/import
failure protection, copy consistency, and intake/results regression across three
languages. The separate CV check, mypy (11 files), pinned dependency installation,
`pip check` and the real Chrome workflow passed. Artifacts are ignored under
`test-results/normalized-trends-browser/`.

Replit status: configuration inspected; concrete project link checked read-only;
this repair has **not run on Replit** and has not been deployed there.
No Linux runtime test was performed. Once the owner grants access, sync the reviewed
commit, install `requirements.txt`, run the configured app, and verify the same
flows in Preview. Collect a project/Preview link and screenshot that identifies
the actual tested commit. Do not assume old usage evidence covers this repair.


### Input state and import preflight repair — baseline b6c0837

Uploads are identified by a SHA-256 digest of their contents, not their filename.
Changed contents are parsed once and replace confirmed skills, resetting the
manual draft. Identical contents do not overwrite manual edits or cleared skills
on reruns. Removing an upload alone does not clear the confirmed profile.
Only fictional CVs should be used; this change adds no upload persistence.

Search and category selectors share a manual draft. Editing enables Apply, which
replaces confirmed skills (including an intentionally emptied draft). Before any
manual edit, Apply is disabled so it cannot accidentally erase uploaded skills.
Clear current skills clears the confirmed profile, draft and selectors while
retaining the consumed upload digest. Continue is disabled for an empty profile
and otherwise uses the displayed confirmed skills, never an unapplied draft.

Trend `--check` and import now share metadata/date, source-host identity, mapping
and canonical-key validation. Preflight writes no snapshots, backups or import
status. Passing means structural/source-identity validation only, not external
fact verification or guaranteed write access. Failed imports retain the last
valid snapshot and record failure status. Original source wording is preserved.

Final verification on 2026-10-25: **54 automated tests passed**; a fresh matrix of edge states (empty/unknown/all skills, invalid language, corrupt snapshot, HR and career-centre cases) is clean, and the live demo is served from Replit
CV checks passed, configured mypy passed (11 source files), and `pip check` passed.
Chrome verified synthetic upload → manual Excel override → hours change → results,
clear with the old upload retained, same-name/new-content uploads, field/source/
scenario controls, learning route and SDG display. Browser artifacts are ignored
under `test-results/input-state-browser/`. Three-language and worker/graduate/HR/
career-centre coverage uses Streamlit page tests; the Chrome flow is English worker.
These are local Windows results for the uncommitted repair based on b6c0837;
Replit/Linux execution and team human review remain unverified.

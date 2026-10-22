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

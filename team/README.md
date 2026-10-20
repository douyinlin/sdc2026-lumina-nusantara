# 团队内部资料（非提交内容）

这个文件夹里的东西**不是给评委看的**，放在这里是为了让仓库根目录保持清爽，
让评委第一眼只看到该看的东西。

## 评委实际会看的（根目录）

```
README.md          ← 项目说明（官方模板结构）
app.py             ← 应用入口
submission/        ← ★ 所有要交的文件都在这里
docs/architecture.png ← 系统框图（README 里引用）
src/ data/ tests/  ← 代码和数据
```

## 这个文件夹里是什么

| 路径 | 内容 | 为什么不给评委看 |
| --- | --- | --- |
| `docs/project-record.md` | 开发过程记录、决策日志 | 内部记录，评委不需要 |
| `docs/proposal-draft.md` | 提案的文字草稿 | 正式版已排成 PDF，放在 `submission/` |
| `docs/tech-stack.md` | 技术栈详细说明 | README 里有摘要，这里更细 |
| `docs/版本与回滚.md` | Git 分支与回滚操作指南 | 内部运维文档 |
| `tools/build_pdfs.py` | 生成两份 PDF 的脚本 | 改文字时重跑，不涉及产品 |
| `dev-env/启动 SkillRadar.bat` | 本地一键启动脚本 | 评委用线上的 demo 链接即可 |
| `dev-env/pyproject.toml` | mypy 类型检查配置 | 开发工具，不影响运行 |
| `dev-env/requirements-dev.txt` | 测试与类型检查依赖 | 开发工具，部署不需要 |
| `screenshots/*.png` | 三种语言的界面截图 | 演示视频和 README 会覆盖 |

## 改提案文字时

```bash
python team/tools/build_pdfs.py
```

重新生成的两份 PDF 会写到 `submission/`。

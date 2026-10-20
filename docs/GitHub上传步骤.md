# 上传到 GitHub 的步骤（GitHub Desktop 版）

> 仓库已经在这台电脑上初始化好并提交了第一个 commit：
> `C:\Users\45\Downloads\dsh_working_space\lumina-nusantara-repo`
> 这台电脑已经能从 GitHub 登录状态读取到你的账号 **douyinlin**。

---

## 第 1 步：在网页上建一个空仓库（1 分钟）

1. 打开 https://github.com/new
2. **Repository name**：`sdc2026-lumina-nusantara`
3. **Description**（可选）：`SDC 2026 Hackathon · Domain 1 · Lumina Nusantara`
4. 选 **Public**（评委必须能访问）
5. ⚠️ **不要勾** "Add a README file" / "Add .gitignore" / "Choose a license"（本地已有，勾了会冲突）
6. 点 **Create repository**

创建完页面会显示 `https://github.com/douyinlin/sdc2026-lumina-nusantara.git`。

---

## 第 2 步：GitHub Desktop 打开本地仓库

1. 打开 **GitHub Desktop**
2. 菜单 **File → Add local repository…**
3. 路径选：
   ```
   C:\Users\45\Downloads\dsh_working_space\lumina-nusantara-repo
   ```
4. 点 **Add repository**

> 如果提示 "This directory does not appear to be a Git repository"，说明路径选错了，
> 一定选到 `lumina-nusantara-repo` 这一层（里面有 `.git` 文件夹）。

---

## 第 3 步：发布到 GitHub

1. 顶部会出现 **Publish repository** 按钮，点它
2. **Name**：`sdc2026-lumina-nusantara`
3. **Description** 随意填
4. ⚠️ **取消勾选 "Keep this code private"**（因为我们第 1 步已经建了 public 仓库）
   - 如果第 1 步没建，这里取消勾选直接 Publish，Desktop 会帮你建 public 仓库
5. 点 **Publish repository**

---

## 第 4 步：验证（重要，别跳过）

1. 打开 https://github.com/douyinlin/sdc2026-lumina-nusantara
2. 确认：
   - 页面上能看到 **README.md** 渲染出来的内容（团队名、Techn Stack 表）
   - 文件列表有 `src/`、`tests/`、`docs/`、`submission/`
   - 仓库标着 **Public**
3. **用无痕窗口（Ctrl+Shift+N）再打开一次**，确认不登录也能看 → 评委视角

---

## 之后每次改完文件

| 在 GitHub Desktop 里 |
| --- |
| 1. 改完文件后回到 Desktop，左侧会列出变更 |
| 2. 下方 **Summary** 填一句（如 `add streamlit ui`） |
| 3. 点 **Commit to main** |
| 4. 点右上 **Push origin** |

---

## 如果 Publish 时问你要不要 push，选 yes

---

## 常见问题

**Q：第 1 步建了仓库，第 3 步 Publish 报 "repository already exists"？**
A：说明 Desktop 想新建同名仓库。改成：不点 Publish，而是
**Repository → Repository settings → Remote → Primary remote repository** 填
`https://github.com/douyinlin/sdc2026-lumina-nusantara.git`，再点 **Push origin**。

**Q：可以干脆跳过第 1 步，直接点 Publish 吗？**
A：可以，但要在 Publish 弹窗里把 "Keep this code private" **取消勾选**，
并确认仓库名就是 `sdc2026-lumina-nusantara`。

**Q：以后文件多了、仓库大了怎么办？**
A：`.gitignore` 已经挡掉了 `.env`、`__pycache__`、`*.sqlite3`。
**不要把 API key 写进任何文件**，Replit 的 key 放 Replit Secrets。

---

## 下一步告诉我

- 仓库建好了吗？把链接发我 → 我核对 README 和文件是否完整
- 要我接着做 **Streamlit 界面** → 说一声，我直接在 `lumina-nusantara-repo` 里加 `app.py`，你 Desktop 里 commit + push 就行

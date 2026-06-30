# AI Intelligence Assistant

一个面向 X/Twitter 的 AI 情报助手 MVP，用来发现可能爆火的帖子、追踪博主增长，并分析内容特征。

当前版本先支持本地 JSON 数据源，方便在没有配置 X MCP / X API 前验证流程。之后可以把采集层替换成 X MCP 工具调用。

## 能做什么

- 按关键词、作者、时间窗口分析帖子
- 计算帖子爆款潜力分数
- 识别 hook 类型、结构特征、媒体形态、互动异常
- 追踪作者粉丝增长
- 输出 Markdown 日报

## 快速运行

```bash
python3 -m ai_intel report --data samples/x_posts.json --out reports/daily.md
```

报告会生成到 `reports/daily.md`。

也可以运行每日自动化入口：

```bash
python3 -m scripts.run_daily --source sample
```

这会同时生成：

- `reports/daily.md`: 情报日报
- `data/latest_posts.json`: 本次分析快照
- `data/history.json`: 历史采集记录，用于计算粉丝增长

## 数据格式

示例见 `samples/x_posts.json`。每条帖子字段：

- `id`: 帖子 ID
- `url`: 帖子链接
- `author_handle`: 作者 handle
- `author_name`: 作者名
- `created_at`: ISO 时间
- `text`: 帖子正文
- `likes`, `reposts`, `replies`, `quotes`, `views`: 互动数据
- `author_followers`, `author_followers_prev`: 当前和上次记录的粉丝数
- `media`: `text`, `image`, `video`, `thread`, `quote`

## 下一步接 X MCP

真实版建议拆成三层：

1. Collector：通过 X MCP 搜索关键词、读取账号帖子、获取 trends/news。
2. Store：把每次采集结果存到 SQLite，形成粉丝和互动时间序列。
3. Analyst：用当前 MVP 的 scoring/analyzer 生成日报、预警和选题建议。

## GitHub Actions 自动日报

仓库里已经包含 `.github/workflows/daily-report.yml`。推到 GitHub 后，它会：

1. 每天 UTC 00:10 自动运行，也可以手动 `workflow_dispatch`。
2. 先跑测试。
3. 生成 `reports/daily.md`、`data/latest_posts.json`、`data/history.json`。
4. 自动把报告和数据快照 commit 回仓库。

### 配置真实 X 数据

在 GitHub 仓库里添加 Secret：

- Name: `X_BEARER_TOKEN`
- Value: 你的 X Developer App app-only bearer token

没有配置 `X_BEARER_TOKEN` 时，workflow 会回落到 `samples/x_posts.json`，方便先验证自动化链路。

默认搜索 query 在 `scripts/run_daily.py`：

```text
(AI OR "artificial intelligence" OR agent OR agents) lang:en -is:retweet
```

后续可以把它改成你关心的赛道，比如 AI agent、SaaS、跨境电商、crypto、机器人、独立开发等。

## 推送到 GitHub

你建好空仓库后，在本地运行：

```bash
git init
git add .
git commit -m "Add AI intelligence assistant"
git branch -M main
git remote add origin git@github.com:YOUR_NAME/YOUR_REPO.git
git push -u origin main
```

# 中医资讯早报推送

自动抓取中医行业资讯，每天 9 点推送到微信。

## 功能

- 🔍 抓取多源 RSS 资讯
- 🎯 关键词过滤（推拿/针灸/养生/政策/中医等）
- 📝 自动生成摘要
- 📱 推送到微信（Server 酱）
- ⏰ 定时运行（GitHub Actions）

## 文件结构

```
.
├── tcm_news_bot.py          # 主脚本
├── .github/workflows/       # GitHub Actions 配置
│   └── tcm-news.yml
├── venv/                    # Python 虚拟环境
└── README.md
```

## 本地运行

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行脚本
python tcm_news_bot.py
```

## 部署到 GitHub Actions

1. **Fork 或新建仓库**，上传这些文件
2. **设置 Secrets**：
   - 进入仓库 Settings → Secrets and variables → Actions
   - 添加 `SERVER_CHAN_KEY`，值为你的 Server 酱 SendKey
3. **手动测试**：
   - 进入 Actions 页面
   - 选择 "中医资讯早报推送" 工作流
   - 点击 "Run workflow"

## 自定义配置

编辑 `tcm_news_bot.py`：

```python
# 修改关键词
KEYWORDS = ["推拿", "针灸", "养生", "政策", "中医", ...]

# 添加 RSS 源
RSS_SOURCES = {
    "来源名称": "https://example.com/rss.xml",
}

# 修改推送时间（.github/workflows/tcm-news.yml）
cron: '0 1 * * *'  # UTC 时间，北京时间 = UTC + 8
```

## 注意事项

- RSS 源需要可公开访问
- 部分网站可能有反爬限制
- 建议先本地测试 RSS 源可用性

## 依赖

- Python 3.11+
- requests
- beautifulsoup4

# 图片归档（skill 摘要）

完整流程与故障排查：**[`wiki/references/image-handling-guide.md`](../../../../wiki/references/image-handling-guide.md)**  
Schema 原则：**[`wiki/WIKI_SCHEMA.md`](../../../../wiki/WIKI_SCHEMA.md)**「图片处理规范」

## 抓图策略（按输入类型）

| 输入类型 | 图片策略 | 文本 |
|----------|----------|------|
| 外链长文 | 正文信息图尽量全抓；装饰/头像/二维码/追踪像素跳过 | 摘要 + Raw |
| TrendRadar | 见 `trendradar-pointer.md`（选择性） | 月度 ≤5 行 |
| **仅截图** | 用户提供的 **全部保存** | Raw 转写 + 可选 web 互证 |
| URL 抓取失败 | 不假装有全文；`scrape-failed` 或占位说明 | 链 + 已知摘要 |

## 存放位置

| 归属 | 路径 |
|------|------|
| Raw 配图 | `references/raw/assets/<stem>/` |
| Wiki 独有图 | `wiki/<dir>/assets/<stem>/` |
| **默认** | Wiki **引用** Raw assets，避免重复 |

## 获取方式（优先级）

1. **用户 attach** → 复制到 Raw assets（见 `screenshot-only.md`）
2. **Firecrawl MCP**（`firecrawl_scrape` 等）— 网页正文与图片 URL
3. **`scripts/ingest_url_to_raw.py --fetch-images`**（若仓库已提供）
4. **curl** — Firecrawl 不可用时的 fallback

## 嵌入约定

```markdown
# Raw 内
![描述](./assets/<stem>/file.png)
*图：…*

# Wiki 引用 Raw
![描述](../../references/raw/assets/<stem>/file.png)
```

## 验收

```bash
# 可选：仓库脚本
scripts/wiki_verify_images.sh path/to/file.md [more.md ...]
```

或手动：

- `test -f` 每个图片路径
- 相对路径从当前 `.md` 算起
- alt + 必要时斜体说明

## 仅截图路由

见同目录 **`screenshot-only.md`**。

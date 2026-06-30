# 原始资料收件箱（Raw）

放 **不希望被随意改写正文** 的材料：

- 下载的 PDF 导出、文章、长文备份
- 剪藏的 Markdown / HTML
- 人类写的草稿

**约定**

- Agent **默认只读**；结构化内容写在 `wiki/`，并链回本文件。
- 结构性批量整理时，可在 `wiki/changelog.md` 记一笔。
- 单文件过大时，只在 `wiki/` 写摘要与链接。

**只有链接时**

- 对话中说「投喂 wiki」，或终端：  
  `python3 scripts/ingest_url_to_raw.py 'https://…'`  
  加 `--fetch-images` 时图片进 `assets/<剪藏名>/`。

总则：[`wiki/WIKI_SCHEMA.md`](../wiki/WIKI_SCHEMA.md)

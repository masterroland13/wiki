# 图片处理指南

> 目录级约定见 [`wiki/WIKI_SCHEMA.md`](../WIKI_SCHEMA.md) 的「图片处理规范」；本页为流程与清单的加长版。

本文档说明 wiki wiki 中图片资源的完整处理流程。

## 核心原则

**必须完整保留原文所有图片**。图片是知识的重要组成部分，包含示意图、架构图、数据图表等关键信息，不能舍弃。

## 目录结构

```
wiki/
├── references/raw/
│   ├── article-name-2026-04-30.md          # Raw 文章
│   └── assets/
│       └── article-name-2026-04/           # 该文章的图片目录
│           ├── diagram-1.png
│           ├── chart-2.png
│           └── screenshot-3.png
└── wiki/
    └── topics/
        ├── cs-topic-name.md                # Wiki 笔记（引用 Raw 的图片）
        └── assets/                         # 可选：wiki 独有图片
            └── topic-name/
                └── custom-diagram.png
```

## 完整处理流程

### 1. 提取图片 URL

对于网页文章，使用 `curl` + `grep` 提取所有图片 URL：

```bash
curl -s "https://example.com/article" | grep -oE '(src|href)="[^"]*\.(png|jpg|jpeg|gif|webp|svg)[^"]*"'
```

这会输出类似：
```
src="/path/to/image1.png"
src="/path/to/image2.jpg"
```

### 2. 创建 assets 目录

根据文章文件名创建对应的 assets 子目录：

```bash
# 文章文件名：cursor-harness-engineering-2026-04-30.md
# assets 目录名：cursor-harness-engineering-2026-04/
mkdir -p references/raw/assets/cursor-harness-engineering-2026-04
```

**命名规则**：
- 使用文章文件名的 stem（去掉日期和扩展名）
- 添加 `/` 后缀表示目录
- 保持语义化和可读性

### 3. 下载图片到本地

```bash
# 下载单张图片
curl -s "https://example.com/image.png" -o references/raw/assets/article-stem/image-name.png

# 批量下载（示例）
curl -s "https://cdn.example.com/diagram1.png" -o references/raw/assets/cursor-harness-2026-04/harness-dynamic-context.png
curl -s "https://cdn.example.com/chart.png" -o references/raw/assets/cursor-harness-2026-04/chart-tool-error-rates.png
```

**图片命名**：
- 保持原始语义化命名
- 或简化为有意义的描述性名称
- 使用小写字母和连字符分隔

### 4. 在 Markdown 中嵌入图片

#### Raw 文件中的嵌入

`references/raw/cursor-harness-engineering-2026-04-30.md`：

```markdown
## 章节标题

正文内容...

![动态上下文发现](./assets/cursor-harness-engineering-2026-04/harness-dynamic-context.png)

*图：Cursor 的动态上下文发现机制演进*

更多正文...

![工具错误率追踪](./assets/cursor-harness-engineering-2026-04/chart-tool-error-rates.png)

*图：工具调用错误率追踪，达到 99-99.9% 可靠性*
```

**要点**：
- 使用相对路径 `./assets/<stem>/`
- 添加有意义的 alt 文本（中文描述）
- 图片下方用斜体添加说明文字

#### Wiki 文件中的嵌入

`wiki/topics/cs-cursor-harness-engineering.md`：

```markdown
## 上下文窗口演进

从静态到动态的演进过程：

![动态上下文发现](../../references/raw/assets/cursor-harness-engineering-2026-04/harness-dynamic-context.png)

**启示**：随模型能力提升，Harness 应减法而非加法。
```

**要点**：
- 使用相对路径 `../../references/raw/assets/<stem>/`
- 优先引用 Raw 的图片（避免重复存储）
- 仅当 wiki 有独有图片时才放在 `wiki/*/assets/`

### 5. 验证图片路径

完成后必须验证：

```bash
# 检查图片文件是否存在
ls -lh references/raw/assets/cursor-harness-engineering-2026-04/

# 输出应显示所有下载的图片及其大小
# -rw-r--r--  1 user  staff   612K May  5 21:29 harness-dynamic-context.png
# -rw-r--r--  1 user  staff   147K May  5 21:29 chart-tool-error-rates.png
```

在 Markdown 编辑器或 GitHub 预览中检查：
- 图片能正常显示
- 相对路径正确
- alt 文本和说明清晰

## 常见场景

### 场景 1：博客文章（有配图）

```bash
# 1. 提取图片 URL
curl -s "https://blog.example.com/article" | grep -oE 'src="[^"]*\.(png|jpg)"'

# 2. 创建目录
mkdir -p references/raw/assets/article-name-2026-04

# 3. 下载图片
curl -s "https://cdn.example.com/img1.png" -o references/raw/assets/article-name-2026-04/diagram-1.png
curl -s "https://cdn.example.com/img2.png" -o references/raw/assets/article-name-2026-04/chart-2.png

# 4. 在 Raw 和 Wiki 中嵌入（见上文示例）
```

### 场景 2：论文（PDF 截图）

```bash
# 1. 手动截图保存为 PNG
# 2. 创建目录
mkdir -p references/papers/assets/paper-name-2024

# 3. 移动截图
mv ~/Downloads/paper-figure-1.png references/papers/assets/paper-name-2024/

# 4. 在论文笔记中嵌入
# wiki/papers/paper-name.md:
# ![Figure 1: Architecture](../../references/papers/assets/paper-name-2024/paper-figure-1.png)
```

### 场景 3：用户提供的截图（对话 attach / 视频帧 / 幻灯片）

**Wiki 投喂默认：Raw-first**（详见 `.agents/skills/wiki/references/screenshot-only.md`）。

```bash
# 1. 用户 attach 后，Cursor 常见落点：
#    ~/.cursor/projects/<project>/assets/image-*.png

# 2. 创建 Raw assets 并复制（勿只留在临时目录）
mkdir -p references/raw/assets/<stem>
cp ~/.cursor/projects/<project>/assets/image-*.png \
   references/raw/assets/<stem>/<semantic-name>.png

# 3. 写 Raw：嵌图 + 表格/列表转写图中清单（可检索层）
# references/raw/<topic-stem>-YYYY-MM-DD.md

# 4. Wiki 引用 Raw 图片（不重复拷贝）
# wiki/topics/....md:
# ![描述](../../references/raw/assets/<stem>/<semantic-name>.png)

# 5. 缺视频/文章 URL 时在 Raw 与 Wiki Open Questions 留坑
```

**例外**：纯项目 UI mockup、只在 project 上下文成立的图，可放在 `wiki/projects/<proj>/assets/` 并在 project 笔记内引用——仍建议关键图备份到 Raw 若需长期归档。

## 相对路径速查表

| 当前文件位置 | 目标图片位置 | 相对路径 |
|-------------|-------------|---------|
| `references/raw/article.md` | `references/raw/assets/article/img.png` | `./assets/article/img.png` |
| `wiki/topics/topic.md` | `references/raw/assets/article/img.png` | `../../references/raw/assets/article/img.png` |
| `wiki/maps/map.md` | `references/raw/assets/article/img.png` | `../../references/raw/assets/article/img.png` |
| `wiki/projects/proj/note.md` | `wiki/projects/proj/assets/img.png` | `./assets/img.png` |
| `wiki/papers/paper.md` | `references/papers/assets/paper/img.png` | `../../references/papers/assets/paper/img.png` |

## 最佳实践

1. **优先共用 Raw 的 assets**：避免图片重复存储
2. **语义化命名**：文件名和 alt 文本都要有意义
3. **添加说明文字**：复杂图表需要额外解释
4. **验证路径**：提交前确保图片能正常显示
5. **保持一致性**：同一文章的图片放在同一 assets 子目录

## 工具支持

### wiki_verify_images.sh

检查 Markdown 中相对路径图片是否存在：

```bash
chmod +x scripts/wiki_verify_images.sh
scripts/wiki_verify_images.sh references/raw/foo.md wiki/topics/bar.md
```

### 批量下载脚本（未来可选）

可以创建 `scripts/download_images.py` 辅助批量下载：

```python
#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

def download_images(urls_file, output_dir):
    """从 URL 列表文件批量下载图片"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(urls_file) as f:
        for i, url in enumerate(f, 1):
            url = url.strip()
            if not url:
                continue
            ext = url.split('.')[-1].split('?')[0]
            output_file = output_path / f"image-{i}.{ext}"
            subprocess.run(['curl', '-s', url, '-o', str(output_file)])
            print(f"Downloaded: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: download_images.py <urls.txt> <output_dir>")
        sys.exit(1)
    download_images(sys.argv[1], sys.argv[2])
```

## 故障排查

### 图片不显示

1. 检查文件是否存在：`ls -la <图片路径>`
2. 检查相对路径是否正确（从当前 .md 到图片）
3. 检查文件权限：`chmod 644 <图片路径>`

### 路径计算错误

使用 `realpath` 验证：

```bash
# 从当前 .md 文件位置
cd wiki/topics
realpath --relative-to=. ../../references/raw/assets/article/img.png
# 输出：../../references/raw/assets/article/img.png
```

### 图片过大

压缩图片（可选）：

```bash
# 使用 ImageMagick
convert input.png -quality 85 -resize 1920x output.png

# 或使用 pngquant
pngquant --quality=80-90 input.png -o output.png
```

## 参考

- `wiki/WIKI_SCHEMA.md` - 图片处理规范章节
- `.agents/skills/wiki/SKILL.md` - wiki skill（canonical）；`references/screenshot-only.md` / `image-ingest.md`
- 实际案例：`references/raw/claude-code-bashtool-20-security-checks-2026-05-31.md` 及其 assets

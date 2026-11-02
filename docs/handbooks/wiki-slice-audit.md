# Wiki 切片审查手册（slice-audit）

> 配合 [`wiki-frontier-upgrade.md`](../plans/wiki-frontier-upgrade.md)（本阶段施工计划）使用。  
> 每一刀编码结束后、开下一刀之前执行。  
> 小问题就地修；大问题只报告。不替代通用 code review / Bugbot。  
> 状态：2026-11-02 已落盘。索引见 [`docs/README.md`](../README.md)。  
> 日期：2026-11-02

---

## 1. 何时用

| 时机 | 动作 |
|------|------|
| 一刀实现 + 自测声称完成 | 跑本手册全文 |
| 用户说「认真对照计划审」 | 同左 |
| 发现可能越界（默认值、范围扩张） | 先审再决定是否继续 |

---

## 2. 固定步骤（不可跳）

### Step 1 — 定位计划条目
打开计划中该 Slice，抄出六件套：
1. 做什么  
2. 不做什么  
3. 正向验收  
4. 反向验收  
5. 落点层  
6. 测试命令  

### Step 2 — 三方对照
对**每一条**正向/反向验收：

| 验收项 | 实现位置（路径） | 测试/证据 | 结果 |
|--------|------------------|-----------|------|
| … | … | 命令输出摘要 / 收集用例数 | pass/fail |

规则：
- 必须找到对应实现；「我觉得做了」不算
- 测试必须**真被收集并运行**（看收集数）；不接受假绿
- 断言**行为**（有无报错路径、exit code、文件存在、skill 是否要求先跑脚本），不断言无关内部变量名

### Step 3 — 越界检查（checklist）
- [ ] 是否做了「不做什么」里的事？
- [ ] 是否静默改了默认值（L1/L2、检索、Obsidian、必填 frontmatter）？
- [ ] 是否把逻辑焊进错误层（根目录临时脚本、跳过 `.agents` 只改某一宿主副本、把行为偏好写入 `topics/`）？
- [ ] 根目录是否有临时脚本/测试残留/dogfood 文件？
- [ ] 该同步的文档是否同步（Schema、AGENTS、changelog、ROADMAP、skill mirrors）？
- [ ] 是否误改既有阅读笔记正文（升级刀默认不应重写《妥协社会》簇等）？
- [ ] 是否引入计划「不抄」项（GraphRAG、Mem0 正文库、Obsidian SSOT）？

### Step 4 — 小修 / 大报
- **小**：缺测试、缺反向断言、文案与 skill 不一致、mirror 未同步 → 就地修 → 重跑测试 → 记入报告  
- **大**：架构转向、默认行为变更、范围扩张、需新调研 → **只报告**，不开下一刀，不问斩先修

### Step 5 — 输出报告（固定模板）
见第 4 节。不 commit/push，除非用户明确要求。

---

## 3. 分刀审查要点（速查）

### A — 机器 Lint
- 脚本路径唯一真源在 `scripts/lint_wiki.py`
- `/lint` 是否**先跑脚本**
- 故意坏样例能打出**路径**
- exit code 与文档一致
- 未上 CI 阻断（若计划如此）
- 无全库强制改 frontmatter 造成大爆炸（可选 warn/allowlist）

### B — Query + Evals
- skill 流程：index → 页 → 引用路径；失败协议存在
- `wiki/evals/retrieval-cases` ≥10，含释义问法
- 期望路径在仓库中存在（或标明故意缺失用例）
- **无**向量库依赖
- 未默认 RAG raw

### C — Contradiction / Supersession
- 模板与可选 frontmatter 齐全
- wiki/review 明文禁止静默覆盖
- 有示例页；未自动裁判对错
- 新字段保持**可选**（全库未无故变红）

### D — Log + L2
- `wiki/log.md` 与 `changelog.md` 职责分离
- 默认仍 L1；L2 为显式可选
- 级联范围限于 entity/map/index/log
- 有一次可复核的 L2 演练记录

### E — Source-clock
- 仅 repo 内 sources 比较 mtime
- URL-only 跳过
- **不**自动写回 status（除非另授权）
- 有可复现的触发 warn 测试

### F — Memory 层
- Schema 阅读顺序含 memory
- 写入路由表：事实→topic，偏好→memory
- 无 Mem0 必选

### G — Hybrid 检索
- 门槛是否满足（页数或评测命中率）再开工
- 索引范围仅 `wiki/**`
- index-first 仍在；混合为 fallback
- 评测前后有对比数字

### H — Entity/Maps
- entity 门槛（≥2 入链或点名）
- 无空学科占位 topic
- index 无长期误导空表

### I — Skill sync
- 只改 `.agents` 的约定写清
- 故意改 mirror 能被脚本抓出

### J — 只读浏览
- 确认非写入 SSOT
- 用户曾明确要求才做

---

## 4. 报告模板（复制填写）

```markdown
# Slice X 审查报告 — YYYY-MM-DD

## ① 对齐了什么
- …

## ② 就地修了什么（附测试结果）
- 修：…
- 测试命令：…
- 收集/通过：…（如实；失败如实写）

## ③ 放下的大问题
- …（无则写「无」）
- 是否建议开调研：是/否

## ④ 对照仍成立的验收项
- 正向：…
- 反向：…

## ⑤ 下一刀建议
- 建议开 / 暂停 / 先处理大问题：…
```

---

## 5. 与其它审查的关系

| 类型 | 工具 | 何时 |
|------|------|------|
| 计划符合性 | 本手册 | 每刀必做 |
| 通用质量 | `/review`、Bugbot、PR review | 按需 |
| 知识内容语义 | wiki `/review` skill | 内容整理，不替代本手册 |

---

## 6. 完成定义（本手册本身）

用户确认施工计划后，本手册与计划一并落盘至：
- `docs/handbooks/wiki-slice-audit.md`
- 计划：`docs/plans/wiki-frontier-upgrade.md`

落盘后在 `docs/README.md` 挂链接；`wiki/changelog.md` 记结构性文档新增。

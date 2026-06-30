---
type: map
status: seed
created: 2026-06-30
updated: 2026-06-30
tags:
  - learning
  - map
sources:
  - ../WIKI_SCHEMA.md
---

# Learning Spine（跨学科主轴）

一句话：把 **文艺 / 人文 / 理工** 的学习入口编排在一张 map 上；具体笔记仍在 `topics/`，这里只负责 **阶段与链接**。

## 阶段（可按需改）

| 阶段 | 目标 | 入口建议 |
|------|------|----------|
| **1. 广度** | 建立各学科「地图感」 | 各域 1 张 map 或 3～5 篇 seed topic |
| **2. 深度** | 选 1～2 域深挖 | `topics/` + `entities/` 互链 |
| **3. 交叉** | 跨域连接 | `x-` 前缀 topic |
| **4. 复盘** | 巩固与纠错 | `/review` + `review_after` |

## 域入口（在 index 中维护链接）

| 域 | index 分区 | slug 前缀 |
|----|------------|-----------|
| 文学 | 文艺 | `lit-` |
| 电影 | 文艺 | `film-` |
| 音乐 | 文艺 | `music-` |
| 哲学 | 人文 | `phil-` |
| 计算机 | 理工 | `cs-` |
| 物理 | 理工 | `phys-` |
| 天文 | 理工 | `astro-` |

## 当前缺口

- 各域尚无 seed topic（ingest 后在此补链接）
- 可选：为单一域建 `wiki/roadmaps/<domain>/` 子路线

## Related

- [Capture → Review → Archive](./capture-review-archival-workflow.md)
- [Index](../index.md)

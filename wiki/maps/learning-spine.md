---
type: map
status: seed
created: 2026-06-30
updated: 2026-11-02
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

- 文学、电影、音乐、计算机、物理、天文还没有 topic。先记在 [Inbox](../inbox.md)，有笔记后再把链接补到本表。不要为这些空域建空页。
- 哲学已有《妥协社会》簇，入口在 [index](../index.md) 的人文区。

## Related

- [Capture → Review → Archive](./capture-review-archival-workflow.md)
- [Index](../index.md)

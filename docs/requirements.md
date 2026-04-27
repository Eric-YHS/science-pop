# 科普转化平台 - 需求文档

## 项目概述

将学术论文自动转化为科普内容（图片+文章形式），支持对内自营内容产出和对外用户自助生成两条业务线。

---

## 核心模块

### 1. 论文爬虫系统

- **调度**: 每周日定时执行
- **爬取源**（按学科分类）:

  | 学科 | 来源 |
  |------|------|
  | 人工智能/计算机科学 | arXiv.org、asXiv.org |
  | 生命科学与健康 | PubMed Central (PMC)、PLOS、SinoMed、HighWire Press、BiomedRxiv |
  | 脑科学与心理学 | Brain and Behavior、Annals of General Psychiatry、JNS、PCI Neuroscience、PhiMiSci、Open Mind |
  | 社会与行为科学 | 国家哲学社会科学文献中心、SSRN、RePEc、IMF eLibrary |
  | 经济金融 | CnOpenData/CNRDS、RePEc、国泰安CSMAR |
  | 环境与气候 | GreenFILE、OpenSky、Environment Complete |

- **输出**: 论文以 txt/pdf 文件存储
- **注意**: 部分论文 PDF 不含出处信息和 DOI 号，需以 txt 形式补充输入元数据

### 2. 科普转化工作流（COZE 平台）

- 已在 COZE 搭建完成，需导出为 API 供后端调用
- **输出形式**: 图片 + 文章（非视频）
- **两条链路**:
  - **GPT 链路**: 效果好，速度慢
  - **Banana 链路**: 速度快，效果稍逊

### 3. 对内业务线（自营内容）

- 输入: 爬虫爬取的论文
- 处理: 走 GPT 工作流
- 输出: 科普图片 + 科普文章

### 4. 对外业务线（创作中心）

- 输入: 用户通过前端上传的文件
- 处理: 用户可选择 GPT 或 Banana 链路
- 输出: 科普图片 + 科普文章

---

## 技术要点

| 项目 | 说明 |
|------|------|
| COZE 工作流 | 已搭建，需导出为 API，登录需手机验证码 |
| 分类策略 | 爬取时按学科分类存储，前端可按分类检索 |
| 文件格式 | 输入支持 txt/pdf，输出为图片+文章 |
| 定时任务 | 每周日自动爬取 |

---

## 待确认事项

- [ ] COZE API 的具体接口格式和认证方式
- [ ] Banana 链路的 API 接入方式
- [ ] 分类策略: 爬取时分类 vs 输出后分类（建议爬取时按源分类，更简单可靠）
- [ ] 前端与后端的接口协议
- [ ] 部署环境和服务器配置

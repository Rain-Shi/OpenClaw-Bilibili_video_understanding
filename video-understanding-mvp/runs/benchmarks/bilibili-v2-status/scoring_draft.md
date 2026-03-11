# Benchmark Scoring Draft (Initial Human Judgment)

> 这是基于当前两条样本的首版人工评分草稿，目的是帮助后续复核与迭代，不代表最终定稿。

## bili_commentary_case_01

- Transcript quality winner: **MVP + Refinement**
  - Notes: Plain MVP 的中文转写噪声很重；refinement 明显把解说叙事修正到了可读水平。summary-agent 本身不直接改善 transcript，所以这一项仍判给 refinement。

- Summary quality winner: **MVP + Refinement + Summary Agent**
  - Notes: summary-agent 能抓住“邋遢女人进奢侈品店—豪言买下—现金支付—身份传闻”这条叙事主线，已经明显像可展示摘要。plain/refinement 两条仍停留在模板式摘要。

- Chapter quality winner: **MVP + Refinement + Summary Agent**
  - Notes: summary-agent 生成了完整且可读的章节标题与章节摘要，例如“现金支付的秘密”“关于沙拉金的背景传闻”，远好于原来的 Chapter 1/2/3。

- Grounding / uncertainty winner: **MVP + Refinement + Summary Agent**
  - Notes: commentary case 中，summary-agent 能把“沙拉金真实身份”和“牛津/身世细节”明确标成不确定信息，而不是直接写死成事实。

- Overall winner: **MVP + Refinement + Summary Agent**
- Human notes: 当前 commentary case 已经显示出比较强的产品展示潜力。风险点主要在“传闻类信息”的事实性，需要继续保持 uncertainty 标注。

---

## bili_tutorial_case_01

- Transcript quality winner: **MVP + Refinement**
  - Notes: 这一项提升最显著。`短期视频 -> 本期视频`、`言言下日来 -> 炎炎夏日来临` 等修正说明 refinement 是核心贡献者。

- Summary quality winner: **MVP + Refinement + Summary Agent**
  - Notes: summary-agent 能把教程口播提炼成“暑期生活选择 / 兴趣发展 / 创作提升”的主题摘要，已经远比 plain/refinement 的模板拼接更可读。

- Chapter quality winner: **MVP + Refinement + Summary Agent**
  - Notes: summary-agent 把章节提升成“视频开场 / 暑期生活抉择 / 宅家与旅游 / 兴趣与就业”等主题化标题，并补全了章节摘要。

- Grounding / uncertainty winner: **MVP + Refinement + Summary Agent**
  - Notes: 这一项尤其重要。教程样本里存在 `饮食和记忆`、`口渴得不行`、`地图攻略` 等明显脏片段，summary-agent 已经能把它们从主摘要中压出去，并放进 uncertain points。

- Overall winner: **MVP + Refinement + Summary Agent**
- Human notes: 教程 case 证明当前三层结构是有效的：refinement 负责修 transcript，summary-agent 负责把输出提升到人类可读层。后续仍需继续检查 long_summary 的稳定性与格式细节。

---

## Cross-case quick judgment

- 如果看 **transcript 本身**：当前最关键的提升来源还是 **ViDove refinement**。
- 如果看 **最终可展示结果**：当前最强链路已经是 **MVP + Refinement + Summary Agent**。
- 如果看 **风险控制**：grounded summary-agent 是当前系统最有价值的新层，因为它不仅能总结，还开始学会暴露不确定性。

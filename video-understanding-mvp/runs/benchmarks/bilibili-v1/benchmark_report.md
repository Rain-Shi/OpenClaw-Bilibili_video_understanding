# Bilibili Benchmark Report v1

## Case: bili_commentary_case_01

### Sample
- Title: 2026 网飞爆剧！她编造的奢侈品卖遍全球，自己却惨死水沟《莎拉的真伪人生》
- Uploader: 正经的瓜皮酱
- BV: BV1odNgzpEm3
- Source URL: https://www.bilibili.com/video/BV1odNgzpEm3/
- Clip used: first 300 seconds
- Category: bilibili_commentary
- Goal: understanding_quality

### Engine status
- MVP: success
- ViDove: success

### Quick stats
- MVP timeline segments: 125
- MVP chapters: 5
- ViDove timeline segments: 134
- ViDove chapters: 5

### MVP summary preview
Offline MVP summary generated from transcript/timeline. Observed 125 timeline segments. Leading spoken content: 金幣繪黃的設施品店來為一座拉塔的女人 她有路逛菜市場一般隨一百弄動作一套房的名牌包 銷售好心告知不能隨意觸碰 滑壞是造假賠償 女人卻直接放下豪言 女人的騷操作不止於此 這麼多名牌包 她進全部用現金解上 原來 她那造型系的旅行代理裝的全都是草票 女人也不在乎什麼積分

### ViDove summary preview
Offline MVP summary generated from transcript/timeline. Observed 134 timeline segments. Leading spoken content: 金碧辉煌的奢侈品店来了位一桌邋遢的女人 她有路逛菜市場一般隨意擺弄 動輒一套房的名牌包 銷售好心告知不能隨意觸碰 劃壞是造价賠償 女人卻直接放下豪言 她说她要买所有我摸过的东西 女人的骚操作不止于此

### Initial judgment
- On this first Bilibili commentary sample, ViDove is clearly stronger than the current MVP in transcript/text recovery quality.
- MVP still produces many Chinese recognition errors and malformed phrases, even though the pipeline completes successfully.
- ViDove originally produced mixed Chinese/English output on this sample, but the mapping cleaner improved usability by replacing mostly-English segments with better Chinese transcribed segments where possible.
- ViDove is currently better treated as a stronger text-processing / subtitle-quality engine, while the MVP remains the more convenient future system skeleton for Bilibili understanding and live-summary expansion.

### Risks / caveats
- ViDove output still has remaining normalization issues (traditional/simplified mix, odd lexical choices).
- This benchmark case currently provides qualitative evidence, not a strict WER/CER score.
- The Bilibili sample is difficult enough to reveal weaknesses in both pipelines, which is why it is valuable.

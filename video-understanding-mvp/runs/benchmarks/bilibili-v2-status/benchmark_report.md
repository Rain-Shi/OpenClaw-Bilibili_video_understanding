# Benchmark Report

Cases: 2

## Comparison axes

- Plain MVP
- MVP + Refinement
- MVP + Refinement + Summary Agent

## bili_commentary_case_01

**Plain MVP**

- status: success
- timeline: 125
- chapters: 5
- transcript: 125

summary preview:
Offline MVP summary generated from transcript/timeline. Observed 125 timeline segments. Leading spoken content: 金幣繪黃的設施品店來為一座拉塔的女人 她有路逛菜市場一般隨一百弄動作一套房的名牌包 銷售好心告知不能隨意觸碰 滑壞是造假賠償 女人卻直接放下豪言 女人的騷操作不止於此 這麼多名牌包 她進全部用現金解上 原來 她那造型系的旅行代理裝的全都是草票 女人也不在乎

chapter preview:
- Chapter 1
- Chapter 2
- Chapter 3

timeline preview:
- 金幣繪黃的設施品店來為一座拉塔的女人
- 她有路逛菜市場一般隨一百弄動作一套房的名牌包
- 銷售好心告知不能隨意觸碰 滑壞是造假賠償

**MVP + Refinement**

- status: success
- timeline: 134
- chapters: 5
- transcript: 134

summary preview:
Offline MVP summary generated from transcript/timeline. Observed 134 timeline segments. Leading spoken content: 金碧辉煌的奢侈品店来了位一桌邋遢的女人 她有路逛菜市場一般隨意擺弄 動輒一套房的名牌包 銷售好心告知不能隨意觸碰 劃壞是造价賠償 女人卻直接放下豪言 她说她要买所有我摸过的东西 女人的骚操作不止于此 

chapter preview:
- Chapter 1
- Chapter 2
- Chapter 3

timeline preview:
- 金碧辉煌的奢侈品店来了位一桌邋遢的女人
- 她有路逛菜市場一般隨意擺弄
- 動輒一套房的名牌包

**MVP + Refinement + Summary Agent**

- status: success
- timeline: 134
- chapters: 8
- transcript: 134
- summary-agent status: success

summary preview:
视频讲述了一位邋遢的女人走进金碧辉煌的奢侈品店，随意摆弄名牌包并豪气购买所有触碰过的商品。她以现金付款，不在乎积分奖励，身份神秘，周围流传她是富豪且与多个名人政客有关。故事在奢侈品街不断传开，展示了她独特且传奇的购物方式。

chapter preview:
- 奢侈品店的邋遢女人
- 豪言买下所有触碰过的物品
- 现金支付的秘密

timeline preview:
- 金碧辉煌的奢侈品店来了一位邋遢的女人
- 她像逛菜市场一样随意摆弄
- 名牌包的价格动辄就相当于一套房子

grounding notes:
- 女人随意摆弄奢侈品、销售告知赔偿视频中多次提及。
- 沙拉金用现金结账且简单填写会员信息的细节清晰。
- 传闻她与名人、政客及顶级品牌关系的描述来自视频后半段。

uncertain points:
- 沙拉金的真实身份和背景并未完全证实。
- 视频提到她毕业于牛津及身世细节，可能属传言性质。

Delta notes:
- refinement timeline delta vs plain: 9
- summary-agent timeline delta vs refinement: 0
- refinement chapter delta vs plain: 0
- summary-agent chapter delta vs refinement: 3

## bili_tutorial_case_01

**Plain MVP**

- status: success
- timeline: 58
- chapters: 5
- transcript: 58

summary preview:
Offline MVP summary generated from transcript/timeline. Observed 58 timeline segments. Leading spoken content: 在短期视频开始之前请问门先给个三连吗 啊 你要摆票啊 那就给个免费的赞呗 谢了 这对我真的很重要 言言下日来 你为什么用什么方式填满你的手架呢 这色素旅游 

chapter preview:
- Chapter 1
- Chapter 2
- Chapter 3

timeline preview:
- 在短期视频开始之前请问门先给个三连吗
- 啊 你要摆票啊
- 那就给个免费的赞呗

**MVP + Refinement**

- status: success
- timeline: 46
- chapters: 5
- transcript: 46

summary preview:
Offline MVP summary generated from transcript/timeline. Observed 46 timeline segments. Leading spoken content: 在本期视频开始之前 请问能先给个三连吗 啊 那就给个免费的赞呗 谢啦 这对我来说真的很重要 炎炎夏日来临 你会选择哪种方式 

chapter preview:
- Chapter 1
- Chapter 2
- Chapter 3

timeline preview:
- 在本期视频开始之前
- 请问能先给个三连吗
- 啊

**MVP + Refinement + Summary Agent**

- status: success
- timeline: 46
- chapters: 8
- transcript: 46
- summary-agent status: success

summary preview:
本视频围绕暑期生活选择展开，探讨在炎热夏日中如何合理安排时间和兴趣。观众被邀请思考是旅行增长见识、宅家沉浸自媒体，还是深耕兴趣或就业接单。视频强调创作生活vlog和多样兴趣的可能性，鼓励观众多方面提升自己。

chapter preview:
- 视频开场
- 暑期生活抉择
- 宅家与旅游

timeline preview:
- 在本期视频开始之前
- 请问能先给个三连吗
- 啊

grounding notes:
- “炎炎夏日来临，你会选择哪种方式填满你的暑假呢”体现暑期生活选择主题。
- “四处旅游增长见识”、 “宅在家里沉浸在自媒体的海洋中”及“就业接单”为生活方式的具体选项。

uncertain points:
- “饮食和记忆”相关内容在字幕中出现，但上下文不明确，可能为噪声。
- “口渴得不行”及“地图攻略”语句出现，但无明确关联或展开，意义不清。

Delta notes:
- refinement timeline delta vs plain: -12
- summary-agent timeline delta vs refinement: 0
- refinement chapter delta vs plain: 0
- summary-agent chapter delta vs refinement: 3


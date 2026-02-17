# 全局公共参数

**全局Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**全局Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**全局Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**全局认证方式**

> 无需认证

# 状态码说明

| 状态码 | 中文描述 |
| --- | ---- |
| 暂无参数 |

# Manuscript

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-14 20:19:18

> 更新时间: 2026-02-14 20:19:18

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

## health测试连接

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-14 20:28:20

> 更新时间: 2026-02-15 10:58:59

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/health/test

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/health/test?apipost_id=b2f23c2730003

**请求方式**

> POST

**Content-Type**

> none

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"message": "Hello Manuscript!"
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

## novel表crud

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 10:58:06

> 更新时间: 2026-02-15 10:58:06

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

### 创建小说

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 10:58:14

> 更新时间: 2026-02-17 21:01:08

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/novel/create

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/novel/create?apipost_id=bf6a956b30038

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "title": "凡人修仙传",
    "genre": "仙侠",
    "description": "讲述凡人修仙的故事"
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "Novel created successfully",
	"data": {
		"uid": "df046ba8-704e-47e7-aafa-3e36a0f25dde",
		"title": "test_create_novel",
		"genre": "funny",
		"description": "hello create_novel"
	}
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

### 根据uid查看小说信息

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 11:15:26

> 更新时间: 2026-02-17 20:34:10

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/novel/get

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/novel/get?apipost_id=bfa923eb3009a

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "uid": "7979f212-d251-4dcd-8a74-e08479f4b6b4"
    // "uid": "7f661c01-20b8-42a2-84bc-df103e19a193"
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "Get novel successfully",
	"data": {
		"uid": "7f661c01-20b8-42a2-84bc-df103e19a193",
		"title": "凡人修仙传",
		"genre": "仙侠",
		"description": "讲述一个凡人修仙的故事",
		"latest_chapter_uid": null,
		"created_at": "2026-02-17 19:43:20",
		"updated_at": "2026-02-17 19:43:20"
	}
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

### 更新小说基本信息

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 11:17:21

> 更新时间: 2026-02-15 21:23:22

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/novel/update

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/novel/update?apipost_id=bfb009fb300cc

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "uid": "0b46d667-94f5-4f5f-a555-0b9de5094fe0",
    "title": "韩劳模猎艳记",
    "genre": "后宫",
    "description": "讲述韩劳模开后宫的故事"
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "Novel updated successfully",
	"data": {
		"uid": "df046ba8-704e-47e7-aafa-3e36a0f25dde",
		"title": "test_update_novel",
		"genre": "cool",
		"description": "hello update_novel"
	}
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

### 查看小说列表

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 11:29:33

> 更新时间: 2026-02-15 11:30:20

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/novel/list

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/novel/list?apipost_id=bfdcd1bf30100

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "page": 1,
    "size": 10
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "List novels successfully",
	"data": {
		"items": [
			{
				"uid": "df046ba8-704e-47e7-aafa-3e36a0f25dde",
				"title": "test_update_novel",
				"genre": "cool",
				"description": "hello update_novel"
			},
			{
				"uid": "7979f212-d251-4dcd-8a74-e08479f4b6b4",
				"title": "斗破苍穹",
				"genre": "玄幻",
				"description": "这里没有魔法，只有燃烧至极致的斗气"
			}
		],
		"total": 2,
		"page": 1,
		"size": 10
	}
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

### 根据uid删除小说

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 11:30:53

> 更新时间: 2026-02-17 20:55:19

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/novel/delete

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/novel/delete?apipost_id=bfe1961730130

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "uids": [
        "7349bf11-41f5-480b-adcc-88adc65df9a6",
        "dda8809a-753c-4590-9888-9a46e1aa3b65"
    ]
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "Novel deleted successfully",
	"data": null
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

## chapter表crud

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 11:46:26

> 更新时间: 2026-02-15 11:46:26

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

### 创建小说章节

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 12:16:15

> 更新时间: 2026-02-15 21:17:35

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/chapter/create

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/chapter/create?apipost_id=c0884a4b30164

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "novel_uid": "7979f212-d251-4dcd-8a74-e08479f4b6b4",
    "chapter_idx": 3,
    "title": "摆烂猎艳系统",
    "content": "越摆烂，艳福越深"
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "Chapter created successfully",
	"data": {
		"uid": "7b024f59-df53-4861-8e0e-8b1a50065e92",
		"novel_uid": "7979f212-d251-4dcd-8a74-e08479f4b6b4",
		"chapter_idx": 3,
		"title": "摆烂猎艳系统",
		"content": "越摆烂，艳福越深",
		"created_at": "2026-02-15 21:17:29",
		"updated_at": "2026-02-15 21:17:29"
	}
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

### 根据uid查看章节信息

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 12:21:39

> 更新时间: 2026-02-17 21:47:08

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/chapter/get

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/chapter/get?apipost_id=c09b82833016b

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "uid": "886e3b7d-64ab-4b1d-8a55-264f350a7949"
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "Get chapter successfully",
	"data": {
		"uid": "886e3b7d-64ab-4b1d-8a55-264f350a7949",
		"novel_uid": "8a6a6834-0e09-4660-a6f4-e03dd11b3e01",
		"chapter_idx": 1,
		"title": "凡人初入修仙界",
		"content": "山间的雾气还未散尽，露水打湿了韩立的粗布裤脚。他背着半人高的柴捆，沿着那条走了无数遍的蜿蜒小路往山下赶。天刚蒙蒙亮，七玄门山脚下的青牛镇轮廓在薄雾中若隐若现。十六岁的韩立，身形比同龄人略显单薄，但常年劳作让他的手臂和肩膀覆着一层结实的筋肉。他抿着唇，心里盘算着这担柴能换几个铜板，够不够给卧病在床的母亲抓一副便宜些的汤药。\n\n就在他转过一个山坳时，脚下被什么硬物硌了一下。他低头看去，是一块半个巴掌大小、颜色暗沉似铁非铁的牌子，半埋在湿泥里，边缘刻着些看不懂的扭曲纹路。韩立弯腰拾起，入手冰凉，沉甸甸的。他用手擦了擦上面的泥，那纹路在晨光下似乎闪过一丝极淡的、几乎错觉般的微光。他皱了皱眉，乡下孩子对不明来历的东西总带着几分警惕，但想到或许能当个稀罕物换点钱，还是将它塞进了怀里。\n\n他没注意到，身后不远处，一株老松的阴影里，立着一个穿着灰布长衫、身形瘦削的老者。老者面容枯槁，眼窝深陷，但一双眼睛却亮得惊人，正死死盯着韩立拾起铁牌又塞入怀中的动作，嘴角牵起一丝难以察觉的弧度。\n\n韩立回到镇口那间低矮的土坯房时，日头已升高了些。他将柴禾在墙角码好，进屋看了看母亲。母亲咳嗽着，脸色蜡黄，见他回来，勉强笑了笑，催他快去把柴卖了。韩立心里发酸，应了一声，揣着那块铁牌和柴禾，往镇东头的市集走去。\n\n市集喧闹，韩立的柴很快被一个熟识的饭铺伙计买走，价格却比往日又低了两文。伙计叹着气说生意难做。韩立捏着手里寥寥的铜钱，沉默地点点头。他犹豫了一下，掏出那块铁牌，向旁边一个收杂货的老头询问。老头眯着眼看了半晌，掂了掂，嗤笑道：“一块破铁片子，锈成这样，一文不值。”随手丢还给他。\n\n韩立有些失望，正要离开，一个低沉沙哑的声音在身后响起：“小友，可否将此物给老夫一观？”\n\n韩立回头，看见一个灰衣老者不知何时站在了他身后。老者正是山间松影下的那人，此刻他脸上没什么表情，但那双过于明亮的眼睛让韩立心里莫名一紧。韩立迟疑着将铁牌递过去。\n\n老者接过，指尖在那些纹路上缓缓摩挲，动作轻柔得仿佛在触碰易碎的珍宝。他看了好一会儿，才抬起眼，目光如实质般落在韩立脸上：“此物你从何处得来？”\n\n“山……山路上捡的。”韩立老实回答，下意识地后退了半步。这老者的目光让他很不舒服，像能看透他衣服底下藏着几个铜板似的。\n\n“捡的？”老者低喃一声，眼中光芒闪烁不定，似在权衡什么。片刻后，他忽然问道：“小友，你可曾想过，这世间除了生老病死、柴米油盐，或许还有另一条路？”\n\n韩立一愣，不明所以。\n\n老者也不解释，只将铁牌握在掌心，另一只手忽然抬起，对着旁边一块用来压摊布的青石虚虚一按。韩立瞪大了眼睛——那坚硬的青石表面，竟无声无息地凹陷下去一个清晰的掌印，深约半寸，边缘光滑如琢。\n\n“这……”韩立呼吸一滞，心脏怦怦直跳。他见过镇上的武师打拳踢腿，开砖裂石已是了不得，何曾见过这般隔空印石、举重若轻的手段？这已超出了他对“力气”的认知。\n\n“此非俗世武功能为。”老者收回手，声音依旧平淡，却带着一种难以言喻的诱惑力，“此乃‘灵’之力，超脱凡俗，可强身健体，延年益寿，乃至……窥探长生之门径。”\n\n长生？韩立脑子里嗡的一声。他想起母亲日益衰败的病体，想起自己每日为几文钱奔波的困窘，想起这狭小镇子外那片他从未踏足过的、想象中广阔无边的天地。一股混杂着渴望、怀疑与巨大震撼的情绪冲击着他。\n\n“你……您是仙人？”韩立的声音有些干涩。\n\n“仙人？”老者，墨大夫，嘴角扯动了一下，似笑非笑，“仙路渺渺，老夫不过先行几步罢了。我观你拾得此‘引灵牌’，也算与灵道有缘。此牌虽已灵性微失，却也是踏入此门的凭证之一。”他顿了顿，目光如钩，“你可愿随我修行？习得些许法门，至少可保身强体健，寻常病痛不侵，或许……也能让你母亲少受些苦楚。”\n\n最后那句话，像一把锤子敲在韩立心坎上。母亲痛苦的咳嗽声仿佛又在耳边响起。他紧紧攥着拳头，指甲掐进了掌心。天上不会掉馅饼，这道理他懂。这老者神秘莫测，手段惊人，所求为何？仅仅是因为一块捡来的铁牌？但对方展现的力量和那句“母亲少受些苦楚”的承诺，像黑暗中摇曳的烛火，让他无法移开目光。\n\n挣扎良久，韩立抬起头，眼中最初的震惊和迷茫渐渐被一种孤注一掷的坚定取代。他出身卑微，见识浅薄，但有一种近乎本能的谨慎和韧性。他知道，这可能是改变一切的机会，也可能是踏入未知险境的开始。\n\n“我……需要做什么？”韩立没有立刻答应，而是哑声问道。\n\n墨大夫眼中闪过一丝不易察觉的赞赏，似乎对韩立的反应颇为满意。“随我离开此地，前往一处清静之所。拜我为师，遵我教诲，修炼我传之法。至于其他，”他语气转淡，“日后你自会知晓。若不愿，此刻转身离去即可，只当从未见过老夫。”\n\n韩立回头望了望家的方向，那里有他病弱的母亲和清贫却熟悉的生活。他又看了看墨大夫手中那块暗沉的铁牌，以及青石上那个清晰的掌印。晨光渐炽，市集的嘈杂仿佛隔了一层膜。他深吸一口气，胸腔里充满了山间清冷潮湿的空气，混合着尘埃、草药和未知命运的气息。\n\n“我……愿意。”两个字吐出，轻飘飘的，却仿佛用尽了他全身的力气。\n\n墨大夫点了点头，不再多言，转身便走。韩立咬了咬牙，快步跟了上去，将那间低矮的土坯房、喧闹的市集、以及他十六年来的平凡人生，统统抛在了身后弥漫的雾气之中。他不知道前方等待他的是什么，只知道怀里的铁牌贴着胸口，传来一丝挥之不去的冰凉。\n\n山路崎岖，墨大夫步履看似不快，却异常稳当，韩立需得小跑才能勉强跟上。两人一前一后，沉默地向着深山更深处行去。只有林间鸟鸣和风吹过树叶的沙沙声，伴随着少年剧烈的心跳，敲打着通往另一个世界的序章。",
		"synopsis": "韩立偶遇墨大夫，得传修仙功法，从此踏上未知的仙途。",
		"created_at": "2026-02-17 21:01:53",
		"updated_at": "2026-02-17 21:44:59"
	}
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

### 更新章节

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 12:23:00

> 更新时间: 2026-02-17 20:38:05

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/chapter/update

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/chapter/update?apipost_id=c0a0527b3019b

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    // title和content二选一必须传一个
    "uid": "a7dde59c-fb5c-4f5e-95c1-5d3b5c65d16a",
    "title": "干柴烈火",
    "synopsis": "韩立和南宫婉一见钟情，在墨蛟助攻下直接啪啪啪"
    // "content": "越摆烂，艳福越深，御姐越来越多！"
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "Chapter updated successfully",
	"data": {
		"uid": "2eadd67d-c023-4acf-9dfb-e4cc5f9e5432",
		"novel_uid": "7979f212-d251-4dcd-8a74-e08479f4b6b4",
		"chapter_idx": 1,
		"title": "陨落的天才萧炎",
		"content": "斗之气，三段，鉴定为废物。就凭你也想娶我纳兰家的千金？我呸"
	}
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

### 根据novel_uid查看章节列表

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 12:35:16

> 更新时间: 2026-02-17 20:34:06

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/chapter/list

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/chapter/list?apipost_id=c0cd3cbf301e1

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "novel_uid": "7cf0892d-cc87-4096-a01d-f9dc1dc6a53a",
    "page": 1,
    "size": 10
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "List chapters successfully",
	"data": {
		"items": [
			{
				"title": "陨落的天才萧炎",
				"synopsis": "",
				"chapter_uid": "2eadd67d-c023-4acf-9dfb-e4cc5f9e5432",
				"chapter_idx": 1,
				"created_at": "2026-02-15 05:01:55",
				"updated_at": "2026-02-15 05:01:55"
			},
			{
				"title": "逆天摆烂升级系统",
				"synopsis": "",
				"chapter_uid": "4aefec3e-1d00-422b-94b3-76b365922d18",
				"chapter_idx": 2,
				"created_at": "2026-02-15 05:08:39",
				"updated_at": "2026-02-15 20:18:45"
			}
		],
		"total": 2,
		"page": 1,
		"size": 10
	}
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

### 根据uid删除章节

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 12:38:54

> 更新时间: 2026-02-17 20:41:09

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/chapter/delete

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/chapter/delete?apipost_id=c0da463f30213

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "uids": [
        "7dbc9c32-30c3-45f4-b30c-3c09720934cc",
        "ff22d686-ed7a-4ae6-ac5c-1b54f44a4a7f"
    ]
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "Chapter deleted successfully",
	"data": null
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

## character表crud

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 20:01:35

> 更新时间: 2026-02-15 20:01:35

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

### 创建角色

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 20:02:25

> 更新时间: 2026-02-15 21:12:47

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/character/create

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/character/create?apipost_id=c7328c8f3025b

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "novel_uid": "7979f212-d251-4dcd-8a74-e08479f4b6b4",
    "name": "假云韵",
    "description":"纳兰嫣然的师傅，云岚宗的宗主",
    "is_main": false
}

```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "Character created successfully",
	"data": {
		"uid": "eae15a0f-c85d-47f8-b78f-83f48b6c0fed",
		"novel_uid": "7979f212-d251-4dcd-8a74-e08479f4b6b4",
		"name": "萧炎",
		"description": "萧家斗气修炼天才",
		"is_main": 1,
		"created_at": "2026-02-15 20:07:34",
		"updated_at": "2026-02-15 20:07:34"
	}
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

### 根据uid查看角色信息

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 20:08:37

> 更新时间: 2026-02-17 20:32:50

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/character/get

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/character/get?apipost_id=c74970df3028d

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "uid": "9e10161e-04d9-4637-8aba-2256a8d4ddaa"
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "Get character successfully",
	"data": {
		"uid": "eae15a0f-c85d-47f8-b78f-83f48b6c0fed",
		"novel_uid": "7979f212-d251-4dcd-8a74-e08479f4b6b4",
		"name": "萧炎",
		"description": "萧家斗气修炼天才",
		"is_main": 1,
		"created_at": "2026-02-15 20:07:34",
		"updated_at": "2026-02-15 20:07:34"
	}
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

### 更新角色信息

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 20:10:00

> 更新时间: 2026-02-17 19:57:04

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/character/update

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/character/update?apipost_id=c74eac63302bd

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    // name, description, is_main必须传一个
    "uid": "d240607d-abd2-43d7-9d96-ecb25a4d05ce",
    "name": "紫灵",
    "description":"韩立的情人，妙音门门主",
    "is_main": false
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "Character updated successfully",
	"data": {
		"uid": "eae15a0f-c85d-47f8-b78f-83f48b6c0fed",
		"novel_uid": "7979f212-d251-4dcd-8a74-e08479f4b6b4",
		"name": "萧炎",
		"description": "萧家斗气修炼天才！",
		"is_main": 1,
		"created_at": "2026-02-15 20:07:34",
		"updated_at": "2026-02-15 20:20:58"
	}
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

### 根据novel_uid来查看角色列表

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 20:22:57

> 更新时间: 2026-02-17 20:54:06

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/character/list

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/character/list?apipost_id=c77df4f7302ff

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "novel_uid": "7cf0892d-cc87-4096-a01d-f9dc1dc6a53a",
    "page": 1,
    "size": 10
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "List characters successfully",
	"data": {
		"items": [
			{
				"name": "萧炎",
				"character_uid": "eae15a0f-c85d-47f8-b78f-83f48b6c0fed",
				"description": "萧家斗气修炼天才！",
				"is_main": true,
				"created_at": "2026-02-15 20:07:34",
				"updated_at": "2026-02-15 20:20:58"
			},
			{
				"name": "纳兰嫣然",
				"character_uid": "8bb16be9-5f7c-4f74-9a06-b4964cf5da17",
				"description": "萧炎的未婚妻，因嫌弃萧炎实力不够而跑去取消婚约",
				"is_main": false,
				"created_at": "2026-02-15 20:22:40",
				"updated_at": "2026-02-15 20:22:40"
			},
			{
				"name": "云韵",
				"character_uid": "b1be5a3a-382c-4ec6-940a-0c8e5a987891",
				"description": "纳兰嫣然的师傅，云岚宗的宗主",
				"is_main": false,
				"created_at": "2026-02-15 21:12:30",
				"updated_at": "2026-02-15 21:12:30"
			},
			{
				"name": "假云韵",
				"character_uid": "41939650-e320-4910-8ef7-ca5a6b651498",
				"description": "云韵的身外化身",
				"is_main": false,
				"created_at": "2026-02-15 21:12:48",
				"updated_at": "2026-02-15 21:13:47"
			}
		],
		"total": 4,
		"page": 1,
		"size": 10
	}
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

### 删除角色

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 20:24:35

> 更新时间: 2026-02-17 20:54:51

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/character/delete

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/character/delete?apipost_id=c78412133032f

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "uids": [
        "e3ea5322-8cb8-4cc4-8b94-a88ed0d30674",
        "67b5a108-ffcd-4bca-b91e-dc1329361940"
    ]
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "Character deleted successfully",
	"data": null
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

## API_key管理

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 21:32:18

> 更新时间: 2026-02-15 21:32:18

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

### 查看api_key

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 21:32:48

> 更新时间: 2026-02-17 16:48:46

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/model_providers/get

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/model_providers/get?apipost_id=c87e01e330388

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    // 支持的供应商分别有openai, deepseek
    "provider": "deepseek"
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "Get config successfully",
	"data": {
		"provider": "deepseek",
		"config": {
			"api_key": "xxxxxx"
		},
		"path": "D:\\my_projects\\personal\\Manuscript\\config\\deepseek\\config.yaml"
	}
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

### 更新api_key

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-15 21:37:36

> 更新时间: 2026-02-15 22:08:49

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/model_providers/update

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**Mock URL**

> https://mock.apipost.net/mock/40b1396c84e0000/model_providers/update?apipost_id=c88f7747303ba

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "provider": "deepseek",
    "values": {
        "api_key": "xxxxxx"
    }
}
```

**认证方式**

> 继承父级

**响应示例**

* 成功(200)

```javascript
{
	"code": 200,
	"msg": "Update config successfully",
	"data": {
		"provider": "deepseek",
		"config": {
			"api_key": "xxxxxx"
		},
		"path": "D:\\my_projects\\personal\\Manuscript\\config\\deepseek\\config.yaml"
	}
}
```

* 失败(404)

```javascript
暂无数据
```

**Query**

## 工作流

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-17 19:11:05

> 更新时间: 2026-02-17 19:11:05

```text
暂无描述
```

**目录Header参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Query参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录Body参数**

| 参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述 |
| --- | --- | ---- | ---- | ---- |
| 暂无参数 |

**目录认证信息**

> 继承父级

**Query**

### 创建角色

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-17 19:11:47

> 更新时间: 2026-02-17 21:01:27

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/working_flow/create_characters

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "novel_uid": "8a6a6834-0e09-4660-a6f4-e03dd11b3e01",
    "provider": "deepseek"
}
```

**认证方式**

> 继承父级

**响应示例**

* sse_character(200)

```javascript
"{\"type\": \"character\", \"character\": {\"uid\": \"0b89144b-4a98-4513-8c4b-ce20a5644a4b\", \"novel_uid\": \"7979f212-d251-4dcd-8a74-e08479f4b6b4\", \"name\": \"萧炎\", \"description\": \"年轻的天才斗气修炼者，性格坚毅不屈，立志成为最强斗者以保护家族与朋友。\", \"is_main\": true}, \"created_count\": 1}"
```

* 失败(404)

```javascript
暂无数据
```

* sse_start(200)

```javascript
"{\"type\": \"start\", \"character_uids\": []}"
```

* sse_done(200)

```javascript
"{\"type\": \"done\", \"character_uids\": [\"387e66e7-b48f-44b9-b3cf-b72dbd9cad96\", \"40edf5bf-e606-466e-a9ea-eae7171c7d9e\", \"8036063b-aa2b-45e3-81b1-9310759b1feb\", \"a30dc496-393f-4d37-80a4-1b142baf4115\"]}"
```

**Query**

### 创建小说大纲

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-17 20:08:48

> 更新时间: 2026-02-17 21:01:47

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/working_flow/create_chapter_outline

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "novel_uid": "8a6a6834-0e09-4660-a6f4-e03dd11b3e01",
    "provider": "deepseek",
    "target_chapters": 5  // 目标章节数，可不传
}
```

**认证方式**

> 继承父级

**响应示例**

* sse_start(200)

```javascript
"{\"type\": \"start\", \"chapter_uids\": []}"
```

* 失败(404)

```javascript
暂无数据
```

* sse_chapter(200)

```javascript
"{\"type\": \"chapter\", \"chapter\": {\"uid\": \"bbbb86b2-3a0c-4149-bc0e-c9a33a8f4dd0\", \"novel_uid\": \"7f661c01-20b8-42a2-84bc-df103e19a193\", \"index\": 1, \"title\": \"凡人初启\", \"synopsis\": \"韩立生活平凡，偶然结识师尊，开启修仙梦想的序幕。\"}, \"created_count\": 1}"
```

* sse_done(200)

```javascript
"{\"type\": \"done\", \"chapter_uids\": [\"bbbb86b2-3a0c-4149-bc0e-c9a33a8f4dd0\", \"f292918f-18d5-4682-8a2f-5aef61275721\", \"98e0f4e1-6355-4f1f-a0c4-32943b5127a1\", \"ef8d19bd-5d0f-4a37-9ef0-870c0613ec36\", \"83a9eb39-7d1d-4e24-bf51-50c340eaa7b4\", \"93f2ca4f-be3d-494a-aa4b-8569cc567874\", \"800c8432-9733-4371-827d-0a460f5df1cf\", \"3d475946-69bf-42c6-8380-0613f6b30c0c\", \"e047eefd-25d6-4266-bb12-66b69526824c\", \"2c02062c-c1b3-4ae2-9e79-0704c46f19bb\", \"f783ff6c-8bb8-4997-aebe-d1f76f40dd46\", \"8f9ffa39-70f1-4826-8f8e-ac07b2fda971\", \"1eef87e4-4941-4918-bf6c-2bbe8729044b\", \"5ecbe26f-6dd2-467c-8156-8ddcd5f4b725\", \"4481cf9a-c23b-42d5-aedd-4916c3794f92\", \"52b8fb5a-6961-4380-b738-8f26ba1d019b\", \"7bdde8c3-7d80-48f6-8ed6-bb04131fcf3f\", \"63dabdcf-2656-44f7-8135-2a1262c32b44\", \"598f2ef6-ec31-4079-817b-5603d4bbacd7\", \"7f8d4496-f86f-4e10-afc9-b3bba5f8bc8e\", \"bcbde190-fdd0-4e14-a065-55a5693fbe0b\", \"220ec7cd-c9c8-4b3c-8550-a5d3b292ed5f\", \"51deacc7-09f0-46d5-9b5d-1fbcc96cde85\", \"82b755b7-82d5-4da1-be5d-112f3d2d33c0\", \"370b3aae-692f-485c-97f4-6655086d4b43\", \"9f44e0ab-2af7-471b-8270-74eb088e3e8f\", \"a3a39906-8476-4635-a4e9-49dd1b6b408d\", \"d36bddf0-a407-4708-9b9e-07b5f735946f\", \"56b82d89-26ef-41d5-a7c4-4fc50317b9e2\", \"2e153083-3f51-46bd-bc77-7b474c2357d1\", \"910e1017-0f2a-471d-9075-ac269770218c\", \"9cb879c6-3395-48ef-8959-5e4b59744108\", \"aa7c26fe-beed-418d-b204-b19a4d937312\", \"5dd28d1f-61b1-4de7-9004-cbf268a508f0\", \"5b79aa15-5999-4773-83bc-a1fe017e8703\", \"d7beee6f-eddc-4aaa-9246-9f5c3ac82642\", \"f61f4322-22c7-4bb7-8455-3ba4b0af73f3\", \"1b5049f3-56a6-4768-a317-cbe5567dc4be\", \"9c2934fc-b489-4b2a-9016-b905bf162cc1\", \"84431a45-d9fb-456c-9289-1c53577cd29c\"]}"
```

**Query**

### 生成章节内容

> 创建人: Cash

> 更新人: Cash

> 创建时间: 2026-02-17 21:14:08

> 更新时间: 2026-02-17 21:47:25

```text
暂无描述
```

**接口状态**

> 开发中

**接口URL**

> api/working_flow/create_chapter_content

| 环境  | URL |
| --- | --- |
| Mock环境 | https://mock.apipost.net/mock/40b1396c84e0000 |

**请求方式**

> POST

**Content-Type**

> json

**请求Body参数**

```javascript
{
    "chapter_uid": "886e3b7d-64ab-4b1d-8a55-264f350a7949",
    "provider": "deepseek",
    "conversation_messages": [
        {"role": "system", "content": "你是一个专业的小说写作助手。保持角色一致性，并生成连贯的章节内容。"},
        {"role": "user", "content": "请用中文生成该章节的正文，风格偏写实，长度目标约1500-2000字。"}
    ]
}


// 多轮对话的message构建
// [
//   {"role": "system", "content": "你是一个专业的小说写作助手，保持角色人设一致，输出纯正文，不要添加标题或多余说明。"},
//   {"role": "user", "content": "请用中文生成该章节的正文，风格偏写实，长度目标约1500-2000字。先给出一句本章摘要，然后开始正文。"},
//   {"role": "assistant", "content": "<THE_GENERATED_CHAPTER_CONTENT>"},
//   {"role": "user", "content": "请基于上面的正文改写，使剧情更跌宕起伏：强化冲突与紧张感，增加人物心理刻画，插入一个突发事件以改变情势，并在结尾留下明显悬念。必须保留最顶行的一句章节摘要（不要修改摘要文本），保持人物设定一致，长度仍在1500-2000字范围内，只输出正文内容，不要任何额外解释或标记。"}
// ]
```

**认证方式**

> 继承父级

**响应示例**

* sse_start(200)

```javascript
"{\"type\": \"start\", \"chapter_uid\": \"886e3b7d-64ab-4b1d-8a55-264f350a7949\"}"
```

* 失败(404)

```javascript
暂无数据
```

* sse_content(200)

```javascript
"{\"type\": \"token\", \"token\": \"山\"}"
```

* sse_done(200)

```javascript
"{\"type\": \"done\", \"chapter_uid\": \"886e3b7d-64ab-4b1d-8a55-264f350a7949\", \"final_length\": 2294}"
```

**Query**

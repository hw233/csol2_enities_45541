# -*- coding: utf_8 -*-

# 购买界面基类
BaseBuyWindow = {
	# .lbTitle
	'lbTitle'		 : { 'color' : (222.0, 215.0, 102.0), 'text' : "摆摊", 'charSpace':2 },	# "vendwindow:BaseBuyWindow", "lbTitle"
	'rtOwnMoney'	 : { 'text' : "您的金钱" },	# "vendwindow:BaseBuyWindow", "rtOwnMoney"
	# tab buttons
	'tabBtn_2'		 : { 'color' :(236,218,157), 'text' : "店家收购" },	# "vendwindow:BaseBuyWindow", "tabBtn_2"
	'tabBtn_1'		 : { 'color' :(236,218,157), 'text' : "宠物" },	# "vendwindow:BaseBuyWindow", "tabBtn_1"
	'tabBtn_0'		 : { 'color' :(236,218,157), 'text' : "物品" },	# "vendwindow:BaseBuyWindow", "tabBtn_0"
}

# 购买界面
VendBuyWindow = {
	'stSignBoard'	 : { 'text' : "%s的专卖店" },	# "vendwindow:VendBuyWindow", "stSignBoard"
}

# 收购界面基类
BasePurchasePanel = {
	# sellBtn 0—5
	'btnSell'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "出售" },	# "vendwindow:BasePurchasePanel", "btnSell"
	# 界面提示文字
	'stBuyDsp'		 : { 'color' : (234.0, 230.0, 187.0), 'text' : "店家正在收购以下商品:" },	# "vendwindow:BasePurchasePanel", "stBuyDsp"
}

# 买家看到的收购物品界面
BuyPurchasePanel = {
	'phIBox_UnitPrice'		: { 'text' : "收购单价:" },	# "vendwindow:BuyPurchasePanel", "phIBox_UnitPrice"
	'phIBox_SellAmount'		: { 'text' : "出售数量:" },	# "vendwindow:BuyPurchasePanel", "phIBox_SellAmount"
	'phIBox_TotalEarn'		: { 'text' : "收入总额:" },	# "vendwindow:BuyPurchasePanel", "phIBox_TotalEarn"
	'phIBox_Title'			: { 'text' : "出售设置" },	# "vendwindow:BuyPurchasePanel", "phIBox_Title"
}

# 收购物品
VendPurchaseItem = {
	#'purchaseAmount'		: { 'text' : "个" },	# "vendwindow:VendPurchaseItem", "purchaseAmount"
	'purchasePrice'		: { 'text' : "单价：" },	# "vendwindow:VendPurchaseItem", "purchasePrice"
}

# 物品购买界面基类
BaseItemsPanel = {
	# sortComBox
	'type'		 : { 'text' : "类型" },	# "vendwindow:BaseItemsPanel", "type"
	'quality'	 : { 'text' : "品质" },	# "vendwindow:BaseItemsPanel", "quality"
	'price'		 : { 'text' : "价格" },	# "vendwindow:BaseItemsPanel", "price"
	'level'		 : { 'text' : "等级" },	# "vendwindow:BaseItemsPanel", "level"
	'option'	 : { 'text' : "选项" },	# "vendwindow:BaseItemsPanel", "option"
	# static text
	'stSortText'		 : { 'color' : (234.0, 230.0, 187.0), 'text' : "排序方式" },	# "vendwindow:BaseItemsPanel", "stSortText"
	'stNumberText'		 : { 'color' : (234.0, 230.0, 187.0), 'text' : "物品数量:" },	# "vendwindow:BaseItemsPanel", "stNumberText"
}

# 宠物购买界面基类
BasePetsPanel = {
	# btns
	'btnBuy'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "购 买" },	# "vendwindow:BasePetsPanel", "btnBuy"
	'btnAttr'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "查看属性" },	# "vendwindow:BasePetsPanel", "btnAttr"
	# sortComBox
	'type'		 : { 'text' : "类型" },	# "vendwindow:BasePetsPanel", "type"
	#'metier'	 : { 'text' : "职业" },	# "vendwindow:BasePetsPanel", "metier"
	'price'		 : { 'text' : "价格" },	# "vendwindow:BasePetsPanel", "price"
	'level'		 : { 'text' : "等级" },	# "vendwindow:BasePetsPanel", "level"
	'option'	 : { 'text' : "选项" },	# "vendwindow:BasePetsPanel", "option"
	# stext
	'stSortText'		 : { 'color' : (234.0, 230.0, 187.0), 'text' : "排序方式" },	# "vendwindow:BasePetsPanel", "stSortText"
	'stNumberText'		 : { 'color' : (234.0, 230.0, 187.0), 'text' : "宠物数量:" },	# "vendwindow:BasePetsPanel", "stNumberText"
}

# 购买宠物
BuyPetItem = {
	# pet type
	'surefooted'	 : { 'text' : "稳重的" },	# "vendwindow:BuyPetItem", "surefooted"
	'intelligent'	 : { 'text' : "聪慧的" },	# "vendwindow:BuyPetItem", "intelligent"
	'cannily'		 : { 'text' : "精明的" },	# "vendwindow:BuyPetItem", "cannily"
	'brave'			 : { 'text' : "勇敢的" },	# "vendwindow:BuyPetItem", "brave"
	'vivacious'		 : { 'text' : "活泼的" },	# "vendwindow:BuyPetItem", "vivacious"
	# pet gender
	'male'			 : { 'text' : "雄性" },	# "vendwindow:BuyPetItem", "male"
	'female'		 : { 'text' : "雌性" },	# "vendwindow:BuyPetItem", "female"
	# pet breed
	'procreating'		 : { 'text' : "正繁殖" },	# "vendwindow:BuyPetItem", "procreating"
	'progenitive'		 : { 'text' : "未繁殖" },	# "vendwindow:BuyPetItem", "progenitive"
	'irreproducible'	 : { 'text' : "已繁殖" },	# "vendwindow:BuyPetItem", "irreproducible"
	# resume
	'grownPet'	 : { 'text' : "成年宠物" },	# "vendwindow:BuyPetItem", "grownPet"
	'generation1'	 : { 'text' : "一代宝宝" },	# "vendwindow:BuyPetItem", "generation1"
	'generation2'	 : { 'text' : "二代宝宝" },	# "vendwindow:BuyPetItem", "generation2"
	'takeLV'	 : { 'text' : "携带:%s级" },	# "vendwindow:BuyPetItem", "takeLV"
}

# 摆摊出售窗口
VendSellWindow = {
	# stext
	'stStallName'		 : { 'color' : (6.0, 228.0, 192.0), 'text' : "%s的店铺" },	# "vendwindow:VendSellWindow", "stStallName"
	'lbTitle'		 : { 'color' : (240.0, 232.0, 110.0), 'text' : "摆摊" },	# "vendwindow:VendSellWindow", "lbTitle"
	# tbBtns
	'tbBtn_1'		 : { 'text' : "买卖记录" },	# "vendwindow:VendSellWindow", "tbBtn_1"
	'tbBtn_0'		 : { 'text' : "商品" },	# "vendwindow:VendSellWindow", "tbBtn_0"
}

# 摆摊出售面板基类
BaseSellPanel = {
	# btns
	'btnStartVend'		 : { 'text' : "开始摆摊" },	# "vendwindow:BaseSellPanel", "btnStartVend"
	'btnChangePrice'	 : { 'text' : "更改价格" },	# "vendwindow:BaseSellPanel", "btnChangePrice"
	'btnPauseVend'		 : { 'text' : "暂停摆摊" },	# "vendwindow:BaseSellPanel", "btnPauseVend"
	# stext
	'rtStallTax'		 : { 'text' : "摊税：" },	# "vendwindow:BaseSellPanel", "rtStallTax"
	'rtTotalPrice'		 : { 'text' : "总价格：" },	# "vendwindow:BaseSellPanel", "rtTotalPrice"
	'rtPurchaseCost'	 : { 'text' : "总收购价：" },	# "vendwindow:BaseSellPanel", "rtPurchaseCost"
	'stCess'		 : { 'color' : (6.0, 228.0, 192.0), 'text' : "税率：%d%%" },	# "vendwindow:BaseSellPanel", "stCess"
	# sub_tbBtns
	'subTabBtn_2'		 : { 'color' :(236,218,157), 'text' : "物品收购" },	# "vendwindow:BaseSellPanel", "subTabBtn_2"
	'subTabBtn_1'		 : { 'color' :(236,218,157), 'text' : "宠物出售" },	# "vendwindow:BaseSellPanel", "subTabBtn_1"
	'subTabBtn_0'		 : { 'color' :(236,218,157), 'text' : "物品出售" },	# "vendwindow:BaseSellPanel", "subTabBtn_0"
}

# 摆摊出售面板类
VendSellPanel = {
	# .tc.panel_0.endVendBtn.lbText
	'btnEndVend'		 : { 'text' : "收摊闪人" },	# "vendwindow:VendSellPanel", "btnEndVend"
	# .tc.panel_0.changeNameBtn.lbText
	'btnChangeSignboard'	 : { 'text' : "改 名" },	# "vendwindow:VendSellPanel", "btnChangeSignboard"
	'ipBoxClew'		 : { 'text' : "请输入新的店铺名称：" },	# "vendwindow:VendSellPanel", "ipBoxClew"
	'stOwnerName'	 : { 'text' : "店主：" },	# "vendwindow:VendSellPanel", "stOwnerName"
}

# 摆摊出售物品面板
VendGoodsPanel = {
	'ipBoxPrice'	 : { 'text' : "请输入商品售价" },	# "vendwindow:VendGoodsPanel", "ipBoxPrice"
	'ipBoxNewPrice'	 : { 'text' : "请输入新价格" },	# "vendwindow:VendGoodsPanel", "ipBoxNewPrice"
}

# 出售物品图标
VendGoodsIconItem = {
	'price'	 : { 'text' : "出售价格：" },	# "vendwindow:VendGoodsIconItem", "price"
}

# 出售记录面板
VendLogsPanel = {
	'totalIncome'	 : { 'text' : "合计收益:" },	# "vendwindow:VendLogsPanel", "totalIncome"
	'record'	 : { 'text' : "%s %s花费%s买走[%s] x %s" },	# "vendwindow:VendLogsPanel", "record"
	'record2'		: { 'text' : "%s %s花费%s获得[%s] x %s" },	
}

# 出售宠物面板基类
BasePetPanel = {
	# btns
	'btnDown'		 : { 'text' : "下架" },	# "vendwindow:BasePetPanel", "btnDown"
	'btnUp'		 : { 'text' : "上架" },	# "vendwindow:BasePetPanel", "btnUp"
	# stext
	'stSelling'		 : { 'text' : "出售中" },	# "vendwindow:BasePetPanel", "stSelling"
	'stRemain'		 : { 'text' : "携带宠物" },	# "vendwindow:BasePetPanel", "stRemain"
	# dsp
	'grownPet'	 : { 'text' : "成年宠物" },	# "vendwindow:BasePetPanel", "grownPet"
	'generation1'	 : { 'text' : "一代宝宝" },	# "vendwindow:BasePetPanel", "generation1"
	'generation2'	 : { 'text' : "二代宝宝" },	# "vendwindow:BasePetPanel", "generation2"
	'price'	 : { 'text' : "出售价格：" },	# "vendwindow:BasePetPanel", "price"
}

# 出售宠物面板
VendPetPanel = {
	'ipBoxPrice'	 : { 'text' : "请输入出售价格" },	# "vendwindow:VendPetPanel", "ipBoxPrice"
	'ipBoxNewPrice'	 : { 'text' : "请输入新价格" },	# "vendwindow:VendPetPanel", "ipBoxNewPrice"
}

# 自身宠物
MyPetItem = {
	'grownPet'	 : { 'text' : "成年宠物" },	# "vendwindow:MyPetItem", "grownPet"
	'generation1'	 : { 'text' : "一代宝宝" },	# "vendwindow:MyPetItem", "generation1"
	'generation2'	 : { 'text' : "二代宝宝" },	# "vendwindow:MyPetItem", "generation2"
}

# 摆摊收购面板基类
SellBasePurchasePanel = {
	# btns
	'btnRemove'		 : { 'text' : "下架" },	# "vendwindow:SellBasePurchasePanel", "btnRemove"
	'btnAdd'		 : { 'text' : "添加" },	# "vendwindow:SellBasePurchasePanel", "btnAdd"
	# comboBoxs
	'cbSelItem'		 : { 'text' : "选择物品" },	# "vendwindow:SellBasePurchasePanel", "cbSelItem"
	'cbSelSubType'	 : { 'text' : "选择子分类" },	# "vendwindow:SellBasePurchasePanel", "cbSelSubType"
	'cbSelType'		 : { 'text' : "选择分类" },	# "vendwindow:SellBasePurchasePanel", "cbSelType"
}

# 摆摊收购面板
VendPurchasePanel = {
	'ipBoxPrice'		 : { 'text' : "输入单价" },	# "vendwindow:VendPurchasePanel", "ipBoxPrice"
	'ipBoxPurchaseAmount'	 : { 'text' : "收购数量" },	# "vendwindow:VendPurchasePanel", "ipBoxPurchaseAmount"
	'ipBoxTotalPrice'	 : { 'text' : "收购总额" },	# "vendwindow:VendPurchasePanel", "ipBoxTotalPrice"
	'ipBoxPurchaseSetting'	 : { 'text' : "收购设置" },	# "vendwindow:VendPurchasePanel", "ipBoxPurchaseSetting"
	'ipBoxNewPrice'		 : { 'text' : "请输入新价格" },	# "vendwindow:VendPurchasePanel", "ipBoxNewPrice"
}

# 摆摊收购物品图标
VendPurchaseIconItem = {
	'dspUnitPrice'		: { 'text' : "收购单价：" },	# "vendwindow:VendPurchaseIconItem", "dspUnitPrice"
	'dspTotalPrice'		: { 'text' : "收购总价：" },	# "vendwindow:VendPurchaseIconItem", "dspTotalPrice"
}

# 宠物查看界面
espialWindow = {
	'baseAttrTitle'		 : { 'text' : "基本属性" },	# .baseAttrTitle.stTitle
	'geniusTitle'		 : { 'color' : (1.0, 255.0, 216.0), 'text' : "天赋技能" },	# .geniusTitle.stTitle
	'initiativeTitle'		 : { 'color' : (1.0, 255.0, 216.0), 'text' : "主动技能" },	# .initiativeTitle.stTitle
	'joy_item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "快乐" },	# .proPanel.joy_item.stName
	'life_item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "寿命" },	# .proPanel.life_item.stName
	'const_item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "根骨" },	# .proPanel.const_item.stName
	'spirit_item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "灵性" },	# .proPanel.spirit_item.stName
	'exp_item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "经验" },	# .proPanel.exp_item.stName
	'mp_item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "法力" },	# .proPanel.mp_item.stName
	'hp_item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "生命" },	# .proPanel.hp_item.stName
	'freepoint_Item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "自由点" },	# .baseAttr.freepoint_Item.stName
	'habitus_Item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "体质" },	# .baseAttr.habitus_Item.stName
	'agility_Item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "敏捷" },	# .baseAttr.agility_Item.stName
	'brains_Item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "智力" },	# .baseAttr.brains_Item.stName
	'force_Item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "力量" },	# .baseAttr.force_Item.stName
	'duck_Item_1'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "抗性" },	# .proCtrl.panel_1.duck_Item.stName
	'cruel_Item_1'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "暴击" },	# .proCtrl.panel_1.cruel_Item.stName
	'damage_Item_1'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "攻击" },	# .proCtrl.panel_1.damage_Item.stName
	'recovery_Item_1'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "防御" },	# .proCtrl.panel_1.recovery_Item.stName
	'btn_1'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "法 术" },	# .proCtrl.btn_1.lbText
	'damage_Item_0'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "攻击" },	# .proCtrl.panel_0.damage_Item.stName
	'recovery_Item_0'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "防御" },	# .proCtrl.panel_0.recovery_Item.stName
	'duck_Item_0'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "闪避" },	# .proCtrl.panel_0.duck_Item.stName
	'blows_Item_0'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "招架" },	# .proCtrl.panel_0.blows_Item.stName
	'cruel_Item_0'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "暴击" },	# .proCtrl.panel_0.cruel_Item.stName
	'btn_0'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "物 理" },	# .proCtrl.btn_0.lbText
	'lbTitle'		 : { 'text' : "宠物属性查看" },	# .lbTitle
	'miStrength'		 : { 'text' : "力量型" },
	'miBalanced'		 : { 'text' : "均衡型" },
	'miSmart'		 : { 'text' : "敏捷型" },
	'miIntellect'		 : { 'text' : "智力型" },
	'miSurefooted'		 : { 'text' : "稳重的" },
	'miClover'		 : { 'text' : "聪慧的" },
	'miCannily'		 : { 'text' : "精明的" },
	'miBrave'		 : { 'text' : "勇敢的" },
	'miLively'		 : { 'text' : "活泼的" },
	'miMale'		 : { 'text' : "雄性" },
	'miFemale'		 : { 'text' : "雌性" },
	'miUnprocreate'		 : { 'text' : "未繁殖" },
	'miProcreating'		 : { 'text' : "正繁殖" },
	'miProcreated'		 : { 'text' : "已繁殖" },
	'miGrownup'		 : { 'text' : "成年宠物" },
	'miInfancy1'		 : { 'text' : "一代宝宝" },
	'miInfancy2'		 : { 'text' : "二代宝宝" },
	'miUnKnown'		 : { 'text' : "未知" },
	'miTakeLevel'		 : { 'text' : "可携带等级：%s级" },
	'miAbility'		 : { 'text' : "成长度:%i" },
	'dsp_dict'		 : { 'text' : "{ 'giddy': '对眩晕状态有%s的豁免几率','sleep':'对昏睡状态有%s的豁免几率','fix':'对定身状态有%s的豁免几率','hush':'对沉默状态有%s的豁免几率'}" },
	'physicsAttrTitle'		 : { 'text' : "物理属性" },
	'magicAttrTitle'		 : { 'text' : "法术属性" },
}
# PurchaseInputBox
PurchaseInputBox = {
	'st_itemAmount'		 : { 'text' : "商品数量:" },	# .st_itemAmount
	'st_totalPrice'		 : { 'text' : "商品总价:" },	# .st_totalPrice
	'st_unitPrice'		 : { 'text' : "商品单价:" },	# .st_unitPrice
	'btnCancel'		 : { 'text' : "取 消" },	# .btnCancel.lbText
	'btnOk'		 : { 'text' : "确 定" },	# .btnOk.lbText
	'lbTitle'		 : { 'color' : 0xffffff, 'text' : "输入数量",  'limning' : 2 },	# .lbTitle
}

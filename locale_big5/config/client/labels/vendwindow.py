# -*- coding: utf_8 -*-

# 購買界面基類
BaseBuyWindow = {
	# .lbTitle
	'lbTitle'		 : { 'color' : (222.0, 215.0, 102.0), 'text' : "擺攤" },	# "vendwindow:BaseBuyWindow", "lbTitle"
	'rtOwnMoney'	 : { 'text' : "   您的金錢：  " },	# "vendwindow:BaseBuyWindow", "rtOwnMoney"
	# tab buttons
	'tabBtn_2'		 : { 'text' : "物品收購" },	# "vendwindow:BaseBuyWindow", "tabBtn_2"
	'tabBtn_1'		 : { 'text' : "寵物出售" },	# "vendwindow:BaseBuyWindow", "tabBtn_1"
	'tabBtn_0'		 : { 'text' : "物品出售" },	# "vendwindow:BaseBuyWindow", "tabBtn_0"
}

# 購買界面
VendBuyWindow = {
	'stSignBoard'	 : { 'text' : "%s的專賣店" },	# "vendwindow:VendBuyWindow", "stSignBoard"
}

# 收購界面基類
BasePurchasePanel = {
	# sellBtn 0—5
	'btnSell'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "出售" },	# "vendwindow:BasePurchasePanel", "btnSell"
	# 界面提示文字
	'stBuyDsp'		 : { 'color' : (234.0, 230.0, 187.0), 'text' : "店家正在收購以下商品:" },	# "vendwindow:BasePurchasePanel", "stBuyDsp"
}

# 買家看到的收購物品界面
BuyPurchasePanel = {
	'phIBox_UnitPrice'		: { 'text' : "收購單價:" },	# "vendwindow:BuyPurchasePanel", "phIBox_UnitPrice"
	'phIBox_SellAmount'		: { 'text' : "出售數量:" },	# "vendwindow:BuyPurchasePanel", "phIBox_SellAmount"
	'phIBox_TotalEarn'		: { 'text' : "收入總額:" },	# "vendwindow:BuyPurchasePanel", "phIBox_TotalEarn"
	'phIBox_Title'		: { 'text' : "出售設置:" },	# "vendwindow:BuyPurchasePanel", "phIBox_Title"
}

# 收購物品
VendPurchaseItem = {
	'purchaseAmount'		: { 'text' : "收購數量：" },	# "vendwindow:VendPurchaseItem", "purchaseAmount"
	'purchasePrice'		: { 'text' : "收購單價：" },	# "vendwindow:VendPurchaseItem", "purchasePrice"
}

# 物品購買界面基類
BaseItemsPanel = {
	# sortComBox
	'type'		 : { 'text' : "類型" },	# "vendwindow:BaseItemsPanel", "type"
	'quality'	 : { 'text' : "品質" },	# "vendwindow:BaseItemsPanel", "quality"
	'price'		 : { 'text' : "價格" },	# "vendwindow:BaseItemsPanel", "price"
	'level'		 : { 'text' : "等級" },	# "vendwindow:BaseItemsPanel", "level"
	'option'	 : { 'text' : "選項" },	# "vendwindow:BaseItemsPanel", "option"
	# static text
	'stSortText'		 : { 'color' : (234.0, 230.0, 187.0), 'text' : "排序方式" },	# "vendwindow:BaseItemsPanel", "stSortText"
	'stNumberText'		 : { 'color' : (234.0, 230.0, 187.0), 'text' : "物品數量:" },	# "vendwindow:BaseItemsPanel", "stNumberText"
}

# 寵物購買界面基類
BasePetsPanel = {
	# btns
	'btnBuy'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "購 買" },	# "vendwindow:BasePetsPanel", "btnBuy"
	'btnAttr'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "查看屬性" },	# "vendwindow:BasePetsPanel", "btnAttr"
	# sortComBox
	'type'		 : { 'text' : "類型" },	# "vendwindow:BasePetsPanel", "type"
	'metier'	 : { 'text' : "職業" },	# "vendwindow:BasePetsPanel", "metier"
	'price'		 : { 'text' : "價格" },	# "vendwindow:BasePetsPanel", "price"
	'level'		 : { 'text' : "等級" },	# "vendwindow:BasePetsPanel", "level"
	'option'	 : { 'text' : "選項" },	# "vendwindow:BasePetsPanel", "option"
	# stext
	'stSortText'		 : { 'color' : (234.0, 230.0, 187.0), 'text' : "排序方式" },	# "vendwindow:BasePetsPanel", "stSortText"
	'stNumberText'		 : { 'color' : (234.0, 230.0, 187.0), 'text' : "寵物數量:" },	# "vendwindow:BasePetsPanel", "stNumberText"
}

# 購買寵物
BuyPetItem = {
	# pet type
	'surefooted'	 : { 'text' : "穩重的" },	# "vendwindow:BuyPetItem", "surefooted"
	'intelligent'	 : { 'text' : "聰慧的" },	# "vendwindow:BuyPetItem", "intelligent"
	'cannily'		 : { 'text' : "精明的" },	# "vendwindow:BuyPetItem", "cannily"
	'brave'			 : { 'text' : "勇敢的" },	# "vendwindow:BuyPetItem", "brave"
	'vivacious'		 : { 'text' : "活潑的" },	# "vendwindow:BuyPetItem", "vivacious"
	# pet gender
	'male'			 : { 'text' : "雄性" },	# "vendwindow:BuyPetItem", "male"
	'female'		 : { 'text' : "雌性" },	# "vendwindow:BuyPetItem", "female"
	# pet breed
	'procreating'		 : { 'text' : "正繁殖" },	# "vendwindow:BuyPetItem", "procreating"
	'progenitive'		 : { 'text' : "未繁殖" },	# "vendwindow:BuyPetItem", "progenitive"
	'irreproducible'	 : { 'text' : "已繁殖" },	# "vendwindow:BuyPetItem", "irreproducible"
	# resume
	'grownPet'	 : { 'text' : "成年寵物" },	# "vendwindow:BuyPetItem", "grownPet"
	'generation1'	 : { 'text' : "一代寶寶" },	# "vendwindow:BuyPetItem", "generation1"
	'generation2'	 : { 'text' : "二代寶寶" },	# "vendwindow:BuyPetItem", "generation2"
	'takeLV'	 : { 'text' : "攜帶:%s級" },	# "vendwindow:BuyPetItem", "takeLV"
}

# 擺攤出售窗口
VendSellWindow = {
	# stext
	'stStallName'		 : { 'color' : (6.0, 228.0, 192.0), 'text' : "%s的店鋪" },	# "vendwindow:VendSellWindow", "stStallName"
	'lbTitle'		 : { 'color' : (240.0, 232.0, 110.0), 'text' : "擺攤" },	# "vendwindow:VendSellWindow", "lbTitle"
	# tbBtns
	'tbBtn_1'		 : { 'text' : "出售記錄" },	# "vendwindow:VendSellWindow", "tbBtn_1"
	'tbBtn_0'		 : { 'text' : "商品" },	# "vendwindow:VendSellWindow", "tbBtn_0"
}

# 擺攤出售面板基類
BaseSellPanel = {
	# btns
	'btnStartVend'		 : { 'text' : "開始擺攤" },	# "vendwindow:BaseSellPanel", "btnStartVend"
	'btnChangePrice'	 : { 'text' : "更改價格" },	# "vendwindow:BaseSellPanel", "btnChangePrice"
	'btnPauseVend'		 : { 'text' : "暫停擺攤" },	# "vendwindow:BaseSellPanel", "btnPauseVend"
	# stext
	'rtStallTax'		 : { 'text' : "攤稅：" },	# "vendwindow:BaseSellPanel", "rtStallTax"
	'rtTotalPrice'		 : { 'text' : "總價格：" },	# "vendwindow:BaseSellPanel", "rtTotalPrice"
	'rtPurchaseCost'	 : { 'text' : "總收購價：" },	# "vendwindow:BaseSellPanel", "rtPurchaseCost"
	'stCess'		 : { 'color' : (6.0, 228.0, 192.0), 'text' : "稅率：%d%%" },	# "vendwindow:BaseSellPanel", "stCess"
	# sub_tbBtns
	'subTabBtn_2'		 : { 'text' : "物品收購" },	# "vendwindow:BaseSellPanel", "subTabBtn_2"
	'subTabBtn_1'		 : { 'text' : "寵物出售" },	# "vendwindow:BaseSellPanel", "subTabBtn_1"
	'subTabBtn_0'		 : { 'text' : "物品出售" },	# "vendwindow:BaseSellPanel", "subTabBtn_0"
}

# 擺攤出售面板類
VendSellPanel = {
	# .tc.panel_0.endVendBtn.lbText
	'btnEndVend'		 : { 'text' : "收攤閃人" },	# "vendwindow:VendSellPanel", "btnEndVend"
	# .tc.panel_0.changeNameBtn.lbText
	'btnChangeSignboard'	 : { 'text' : "改 名" },	# "vendwindow:VendSellPanel", "btnChangeSignboard"
	'ipBoxClew'		 : { 'text' : "請輸入新的店鋪名稱：" },	# "vendwindow:VendSellPanel", "ipBoxClew"
	'stOwnerName'	 : { 'text' : "店主：" },	# "vendwindow:VendSellPanel", "stOwnerName"
}

# 擺攤出售物品面板
VendGoodsPanel = {
	'ipBoxPrice'	 : { 'text' : "請輸入商品售價" },	# "vendwindow:VendGoodsPanel", "ipBoxPrice"
	'ipBoxNewPrice'	 : { 'text' : "請輸入新價格" },	# "vendwindow:VendGoodsPanel", "ipBoxNewPrice"
}

# 出售物品圖標
VendGoodsIconItem = {
	'price'	 : { 'text' : "出售價格：" },	# "vendwindow:VendGoodsIconItem", "price"
}

# 出售記錄面板
VendLogsPanel = {
	'totalIncome'	 : { 'text' : "合計收益:" },	# "vendwindow:VendLogsPanel", "totalIncome"
	'record'	 : { 'text' : "%s %s花費%s買走%s" },	# "vendwindow:VendLogsPanel", "record"
}

# 出售寵物面板基類
BasePetPanel = {
	# btns
	'btnDown'		 : { 'text' : "下架" },	# "vendwindow:BasePetPanel", "btnDown"
	'btnUp'		 : { 'text' : "上架" },	# "vendwindow:BasePetPanel", "btnUp"
	# stext
	'stSelling'		 : { 'color' : (6.0, 228.0, 192.0), 'text' : "出售中" },	# "vendwindow:BasePetPanel", "stSelling"
	'stRemain'		 : { 'color' : (6.0, 228.0, 192.0), 'text' : "攜帶寵物" },	# "vendwindow:BasePetPanel", "stRemain"
	# dsp
	'grownPet'	 : { 'text' : "成年寵物" },	# "vendwindow:BasePetPanel", "grownPet"
	'generation1'	 : { 'text' : "一代寶寶" },	# "vendwindow:BasePetPanel", "generation1"
	'generation2'	 : { 'text' : "二代寶寶" },	# "vendwindow:BasePetPanel", "generation2"
	'price'	 : { 'text' : "出售價格：" },	# "vendwindow:BasePetPanel", "price"
}

# 出售寵物面板
VendPetPanel = {
	'ipBoxPrice'	 : { 'text' : "請輸入出售價格" },	# "vendwindow:VendPetPanel", "ipBoxPrice"
	'ipBoxNewPrice'	 : { 'text' : "請輸入新價格" },	# "vendwindow:VendPetPanel", "ipBoxNewPrice"
}

# 自身寵物
MyPetItem = {
	'grownPet'	 : { 'text' : "成年寵物" },	# "vendwindow:MyPetItem", "grownPet"
	'generation1'	 : { 'text' : "一代寶寶" },	# "vendwindow:MyPetItem", "generation1"
	'generation2'	 : { 'text' : "二代寶寶" },	# "vendwindow:MyPetItem", "generation2"
}

# 擺攤收購面板基類
SellBasePurchasePanel = {
	# btns
	'btnRemove'		 : { 'text' : "下架" },	# "vendwindow:SellBasePurchasePanel", "btnRemove"
	'btnAdd'		 : { 'text' : "添加" },	# "vendwindow:SellBasePurchasePanel", "btnAdd"
	# comboBoxs
	'cbSelItem'		 : { 'text' : "選擇物品" },	# "vendwindow:SellBasePurchasePanel", "cbSelItem"
	'cbSelSubType'	 : { 'text' : "選擇子分類" },	# "vendwindow:SellBasePurchasePanel", "cbSelSubType"
	'cbSelType'		 : { 'text' : "選擇分類" },	# "vendwindow:SellBasePurchasePanel", "cbSelType"
}

# 擺攤收購面板
VendPurchasePanel = {
	'ipBoxPrice'		 : { 'text' : "輸入單價" },	# "vendwindow:VendPurchasePanel", "ipBoxPrice"
	'ipBoxPurchaseAmount'	 : { 'text' : "收購數量" },	# "vendwindow:VendPurchasePanel", "ipBoxPurchaseAmount"
	'ipBoxTotalPrice'	 : { 'text' : "收購總額" },	# "vendwindow:VendPurchasePanel", "ipBoxTotalPrice"
	'ipBoxPurchaseSetting'	 : { 'text' : "收購設置" },	# "vendwindow:VendPurchasePanel", "ipBoxPurchaseSetting"
	'ipBoxNewPrice'		 : { 'text' : "請輸入新價格" },	# "vendwindow:VendPurchasePanel", "ipBoxNewPrice"
}

# 擺攤收購物品圖標
VendPurchaseIconItem = {
	'dspUnitPrice'		: { 'text' : "收購單價：" },	# "vendwindow:VendPurchaseIconItem", "dspUnitPrice"
	'dspTotalPrice'		: { 'text' : "收購總價：" },	# "vendwindow:VendPurchaseIconItem", "dspTotalPrice"
}

# 寵物查看界面
espialWindow = {
	'baseAttrTitle'		 : { 'color' : (1.0, 255.0, 216.0), 'text' : "基本屬性" },	# .baseAttrTitle.stTitle
	'geniusTitle'		 : { 'color' : (1.0, 255.0, 216.0), 'text' : "天賦技能" },	# .geniusTitle.stTitle
	'initiativeTitle'		 : { 'color' : (1.0, 255.0, 216.0), 'text' : "主動技能" },	# .initiativeTitle.stTitle
	'joy_item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "快樂" },	# .proPanel.joy_item.stName
	'life_item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "壽命" },	# .proPanel.life_item.stName
	'const_item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "根骨" },	# .proPanel.const_item.stName
	'spirit_item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "靈性" },	# .proPanel.spirit_item.stName
	'exp_item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "經驗" },	# .proPanel.exp_item.stName
	'mp_item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "法力" },	# .proPanel.mp_item.stName
	'hp_item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "生命" },	# .proPanel.hp_item.stName
	'freepoint_Item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "自由點" },	# .baseAttr.freepoint_Item.stName
	'habitus_Item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "體質" },	# .baseAttr.habitus_Item.stName
	'agility_Item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "敏捷" },	# .baseAttr.agility_Item.stName
	'brains_Item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "智力" },	# .baseAttr.brains_Item.stName
	'force_Item'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "力量" },	# .baseAttr.force_Item.stName
	'duck_Item_1'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "抗性" },	# .proCtrl.panel_1.duck_Item.stName
	'cruel_Item_1'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "暴擊" },	# .proCtrl.panel_1.cruel_Item.stName
	'damage_Item_1'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "攻擊" },	# .proCtrl.panel_1.damage_Item.stName
	'recovery_Item_1'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "防御" },	# .proCtrl.panel_1.recovery_Item.stName
	'btn_1'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "法 術" },	# .proCtrl.btn_1.lbText
	'damage_Item_0'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "攻擊" },	# .proCtrl.panel_0.damage_Item.stName
	'recovery_Item_0'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "防御" },	# .proCtrl.panel_0.recovery_Item.stName
	'duck_Item_0'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "閃避" },	# .proCtrl.panel_0.duck_Item.stName
	'blows_Item_0'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "招架" },	# .proCtrl.panel_0.blows_Item.stName
	'cruel_Item_0'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "暴擊" },	# .proCtrl.panel_0.cruel_Item.stName
	'btn_0'		 : { 'color' : (237.0, 230.0, 155.0), 'text' : "物 理" },	# .proCtrl.btn_0.lbText
	'lbTitle'		 : { 'color' : (239.0, 231.0, 110.0), 'text' : "寵物屬性查看" },	# .lbTitle
	'miStrength'		 : { 'text' : "力量型" },
	'miBalanced'		 : { 'text' : "均衡型" },
	'miSmart'		 : { 'text' : "敏捷型" },
	'miIntellect'		 : { 'text' : "智力型" },
	'miSurefooted'		 : { 'text' : "穩重的" },
	'miClover'		 : { 'text' : "聰慧的" },
	'miCannily'		 : { 'text' : "精明的" },
	'miBrave'		 : { 'text' : "勇敢的" },
	'miLively'		 : { 'text' : "活潑的" },
	'miMale'		 : { 'text' : "雄性" },
	'miFemale'		 : { 'text' : "雌性" },
	'miUnprocreate'		 : { 'text' : "未繁殖" },
	'miProcreating'		 : { 'text' : "正繁殖" },
	'miProcreated'		 : { 'text' : "已繁殖" },
	'miGrownup'		 : { 'text' : "成年寵物" },
	'miInfancy1'		 : { 'text' : "一代寶寶" },
	'miInfancy2'		 : { 'text' : "二代寶寶" },
	'miUnKnown'		 : { 'text' : "未知" },
	'miTakeLevel'		 : { 'text' : "可攜帶等級：%s級" },
	'miAbility'		 : { 'text' : "成長度:%i" },
	'dsp_dict'		 : { 'text' : "{ 'giddy': '對眩暈狀態有%s的豁免幾率','sleep':'對昏睡狀態有%s的豁免幾率','fix':'對定身狀態有%s的豁免幾率','hush':'對沉默狀態有%s的豁免幾率'}" },
}
# PurchaseInputBox
PurchaseInputBox = {
	'st_itemAmount'		 : { 'text' : "商品數量:" },	# .st_itemAmount
	'st_totalPrice'		 : { 'text' : "商品總價:" },	# .st_totalPrice
	'st_unitPrice'		 : { 'text' : "商品單價:" },	# .st_unitPrice
	'btnCancel'		 : { 'text' : "取 消" },	# .btnCancel.lbText
	'btnOk'		 : { 'text' : "確 定" },	# .btnOk.lbText
	'lbTitle'		 : { 'color' : 0xffffff, 'text' : "輸入數量",  'limning' : 2 },	# .lbTitle
}

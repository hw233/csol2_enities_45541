# -*- coding: cp950 -*-

# 寄售形象選擇界面
CommissionSale = {
	'stClew'		 : { 'color' : (1.0, 255.0, 216.0), 'text' : "請左鍵點擊選擇你喜歡的寄售NPC形象。" },	# "commissionsale:CommissionSale", "stClew"
	'btnCommiss'	 : { 'color' : (255.0, 248.0, 158.0), 'text' : "開始寄售" },	# "commissionsale:CommissionSale", "btnCommiss"
	'lbTitle'		 : { 'color' : (239.0, 231.0, 110.0), 'text' : "形象選擇" },	# "commissionsale:CommissionSale", "lbTitle"
	'shopName'		 : { 'text'	 : "的店鋪" },	# "commissionsale:CommissionSale", "shopName"
}

# 店鋪查詢主界面
CommissionViewer = {
	'tb_merchant'	 : { 'text' : "店主查詢" },	# "commissionsale:CommissionViewer", "tb_merchant"
	'tb_pet'		 : { 'text' : "寵物查詢" },	# "commissionsale:CommissionViewer", "tb_pet"
	'tb_goods'		 : { 'text' : "物品查詢" },	# "commissionsale:CommissionViewer", "tb_goods"
	'lbTitle'		 : { 'color' : (241.0, 232.0, 110.0), 'text' : "店鋪查詢" },	# "commissionsale:CommissionViewer", "lbTitle"
}

# 店主查詢面板
MerchantPanel = {
	'stClewCondition'		 : { 'color' : (0.0, 255.0, 0.0), 'text' : "請確定查詢條件後點擊“查找”按鈕進行查找！" },	# "commissionsale:MerchantPanel", "stClewCondition"
	'stClewSearching'		 : { 'color' : (0.0, 255.0, 0.0), 'text' : "正在查找..." },	# "commissionsale:MerchantPanel", "stClewSearching"
	'stClewNotFound'		 : { 'color' : (0.0, 255.0, 0.0), 'text' : "未找到相關數據" },	# "commissionsale:MerchantPanel", "stClewNotFound"
	'taxisBtn_0'	 : { 'text' : "店鋪名稱" },	# "commissionsale:MerchantPanel", "taxisBtn_0"
	'taxisBtn_1'	 : { 'text' : "店主名" },	# "commissionsale:MerchantPanel", "taxisBtn_1"
	'btnSearch'		 : { 'text' : "查 找" },	# "commissionsale:MerchantPanel", "btnSearch"
	'stKeyWord'		 : { 'color' : (6.0, 243.0, 204.0), 'text' : "按店主名查找" },	# "commissionsale:MerchantPanel", "stKeyWord"
}

# 物品查詢面板
GoodsPanel = {
	# .dirText
	'stClewCondition'		 : { 'color' : (0.0, 255.0, 0.0), 'text' : "請確定查詢條件後點擊“查找”按鈕進行查找！" },	# "commissionsale:GoodsPanel", "stClewCondition"
	'stClewSearching'		 : { 'color' : (0.0, 255.0, 0.0), 'text' : "正在查找..." },	# "commissionsale:GoodsPanel", "stClewSearching"
	'stClewNotFound'		 : { 'color' : (0.0, 255.0, 0.0), 'text' : "未找到相關數據" },	# "commissionsale:GoodsPanel", "stClewNotFound"
	# .cbMR
	'cbMR_All'		 : { 'text' : "全部職業" },	# "commissionsale:GoodsPanel", "cbMR_All"
	'cbMR_Warrior'	 : { 'text' : "戰士" },	# "commissionsale:GoodsPanel", "cbMR_Warrior"
	'cbMR_Swordman'	 : { 'text' : "劍客" },	# "commissionsale:GoodsPanel", "cbMR_Swordman"
	'cbMR_Archer'	 : { 'text' : "射手" },	# "commissionsale:GoodsPanel", "cbMR_Archer"
	'cbMR_Magician'	 : { 'text' : "法師" },	# "commissionsale:GoodsPanel", "cbMR_Magician"
	# .cbTY
	'cbTY_All'		 : { 'text' : "全部類型" },	# "commissionsale:GoodsPanel", "cbTY_All"
	'cbTY_Weapon'	 : { 'text' : "武器" },	# "commissionsale:GoodsPanel", "cbTY_Weapon"
	'cbTY_Armour'	 : { 'text' : "防具" },	# "commissionsale:GoodsPanel", "cbTY_Armour"
	'cbTY_Material'	 : { 'text' : "材料" },	# "commissionsale:GoodsPanel", "cbTY_Material"
	'cbTY_Other'	 : { 'text' : "其他" },	# "commissionsale:GoodsPanel", "cbTY_Other"
	# .cbQA
	'cbQA_All'		 : { 'text' : "全部品質" },	# "commissionsale:GoodsPanel", "cbQA_All"
	'cbQA_White'	 : { 'text' : "白色" },	# "commissionsale:GoodsPanel", "cbQA_White"
	'cbQA_Blue'		 : { 'text' : "藍色" },	# "commissionsale:GoodsPanel", "cbQA_Blue"
	'cbQA_Yellow'	 : { 'text' : "黃色" },	# "commissionsale:GoodsPanel", "cbQA_Yellow"
	'cbQA_Pink'		 : { 'text' : "粉色" },	# "commissionsale:GoodsPanel", "cbQA_Pink"
	'cbQA_Green'	 : { 'text' : "綠色" },	# "commissionsale:GoodsPanel", "cbQA_Green"
	'cbQA_Orange'	 : { 'text' : "橘色" },
	'cbQA_Purple'	 : { 'text' : "紫色" },
	# btn
	'btnSearch'		 : { 'text' : "查找" },	# "commissionsale:GoodsPanel", "btnSearch"
	'btnBuy'		 : { 'text' : "購 買" },	# "commissionsale:GoodsPanel", "btnBuy"
	# taxisBtn
	'taxisBtn_4'		 : { 'text' : "品質" },	# "commissionsale:GoodsPanel", "taxisBtn_4"
	'taxisBtn_3'		 : { 'text' : "價格" },	# "commissionsale:GoodsPanel", "taxisBtn_3"
	'taxisBtn_2'		 : { 'text' : "店主名" },	# "commissionsale:GoodsPanel", "taxisBtn_2"
	'taxisBtn_1'		 : { 'text' : "等級" },	# "commissionsale:GoodsPanel", "taxisBtn_1"
	# stext
	'stLVRange'		 : { 'color' : (6.0, 243.0, 204.0), 'text' : "等級範圍" },	# "commissionsale:GoodsPanel", "stLVRange"
	'stSplit'		 : { 'color' : (6.0, 243.0, 204.0), 'text' : "-" },	# "commissionsale:GoodsPanel", "stSplit"
	'stOwnMoney'		 : { 'color' : (6.0, 243.0, 204.0), 'text' : "您的金錢" },	# "commissionsale:GoodsPanel", "stOwnMoney"
}

# 顯示金錢的列項
MoneyCol = {
	"gold"		: { 'text' : "金" },		# "commissionsale:MoneyCol", "gold"
	"silver"	: { 'text' : "銀" },		# "commissionsale:MoneyCol", "silver"
	"coin"		: { 'text' : "銅" },		# "commissionsale:MoneyCol", "coin"
}

# 寵物查詢面板
PetPanel = {
	# .dirText
	'stClewCondition'		 : { 'color' : (0.0, 255.0, 0.0), 'text' : "請確定查詢條件後點擊“查找”按鈕進行查找！" },	# "commissionsale:PetPanel", "stClewCondition"
	'stClewSearching'		 : { 'color' : (0.0, 255.0, 0.0), 'text' : "正在查找..." },	# "commissionsale:PetPanel", "stClewSearching"
	'stClewNotFound'		 : { 'color' : (0.0, 255.0, 0.0), 'text' : "未找到相關數據" },	# "commissionsale:PetPanel", "stClewNotFound"
	# .cbGender
	'cbGender_All'		 : { 'text' : "全部性別" },	# "commissionsale:PetPanel", "cbGender_All"
	'cbGender_Male'		 : { 'text' : "雄性" },	# "commissionsale:PetPanel", "cbGender_Male"
	'cbGender_Female'	 : { 'text' : "雌性" },	# "commissionsale:PetPanel", "cbGender_Female"
	# .cbBreed
	'cbBreed_All'		 : { 'text' : "繁殖狀況" },	# "commissionsale:PetPanel", "cbBreed_All"
	'cbBreed_Progenitive'		 : { 'text' : "未繁殖" },	# "commissionsale:PetPanel", "cbBreed_Progenitive"
	'cbBreed_Irreproducible'	 : { 'text' : "已繁殖" },	# "commissionsale:PetPanel", "cbBreed_Irreproducible"
	# .cbMR
	'cbMR_All'			 : { 'text' : "全部類型" },	# "commissionsale:PetPanel", "cbMR_All"
	'cbMR_Balanced'		 : { 'text' : "均衡型" },	# "commissionsale:PetPanel", "cbMR_Balanced"
	'cbMR_Nimble'		 : { 'text' : "敏捷型" },	# "commissionsale:PetPanel", "cbMR_Nimble"
	'cbMR_Intellective'	 : { 'text' : "智力型" },	# "commissionsale:PetPanel", "cbMR_Intellective"
	'cbMR_Potent'		 : { 'text' : "力量型" },	# "commissionsale:PetPanel", "cbMR_Potent"
	# .cbEra
	'cbEra_All'			 : { 'text' : "全部規格" },	# "commissionsale:PetPanel", "cbEra_All"
	'cbEra_Grown'		 : { 'text' : "成年寵物" },	# "commissionsale:PetPanel", "cbEra_Grown"
	'cbEra_Era1'		 : { 'text' : "一代寶寶" },	# "commissionsale:PetPanel", "cbEra_Era1"
	'cbEra_Era2'		 : { 'text' : "二代寶寶" },	# "commissionsale:PetPanel", "cbEra_Era2"
	# taxisBtns
	'taxisBtn_7'		 : { 'text' : "價格" },	# "commissionsale:PetPanel", "taxisBtn_7"
	'taxisBtn_6'		 : { 'text' : "店主名" },	# "commissionsale:PetPanel", "taxisBtn_6"
	'taxisBtn_5'		 : { 'text' : "等級" },	# "commissionsale:PetPanel", "taxisBtn_5"
	'taxisBtn_4'		 : { 'text' : "繁殖" },	# "commissionsale:PetPanel", "taxisBtn_4"
	'taxisBtn_3'		 : { 'text' : "性別" },	# "commissionsale:PetPanel", "taxisBtn_3"
	'taxisBtn_2'		 : { 'text' : "類型" },	# "commissionsale:PetPanel", "taxisBtn_2"
	'taxisBtn_1'		 : { 'text' : "規格" },	# "commissionsale:PetPanel", "taxisBtn_1"
	'taxisBtn_0'		 : { 'text' : "名稱" },	# "commissionsale:PetPanel", "taxisBtn_0"
	# btns
	'btnProperty'		 : { 'text' : "查看屬性" },	# "commissionsale:PetPanel", "btnProperty"
	'btnSearch'		 : { 'text' : "查找" },	# "commissionsale:PetPanel", "btnSearch"
	'btnBuy'		 : { 'text' : "購 買" },	# "commissionsale:PetPanel", "btnBuy"
	# stext
	'stLVRange'		 : { 'color' : (6.0, 243.0, 204.0), 'text' : "等級範圍" },	# "commissionsale:PetPanel", "stLVRange"
	'stSplit'		 : { 'color' : (6.0, 243.0, 204.0), 'text' : "-" },	# "commissionsale:PetPanel", "stSplit"
	'stOwnMoney'		 : { 'color' : (6.0, 243.0, 204.0), 'text' : "您的金錢" },	# "commissionsale:PetPanel", "stOwnMoney"
	# 以下是為了以後需要到而作的記錄，例如可能會修改字體
	# .coinBox.lbText
	'textBox_Coin'		 : { 'color' : (6.0, 243.0, 204.0), 'text' : "99" },	# "commissionsale:PetPanel", "textBox_Coin"
	# .silverBox.lbText
	'textBox_Silver'	 : { 'color' : (6.0, 243.0, 204.0), 'text' : "99" },	# "commissionsale:PetPanel", "textBox_Silver"
	# .goldBox.lbText
	'textBox_Gold'		 : { 'color' : (6.0, 243.0, 204.0), 'text' : "99999999" },	# "commissionsale:PetPanel", "textBox_Gold"
	# .idxCtrl.stPgIndex
	'stPgIndex'		 : { 'text' : "5" },	# "commissionsale:PetPanel", "stPgIndex"
}

# PCBuyWindow
PCBuyWindow = {
	# .cb_3000.stext
	'cb3000'		 : { 'text' : "XXXX" },	# "commissionsale:PCBuyWindow", "cb3000"
	# .cb_1000.stext
	'cb1000'		 : { 'text' : "XXXX" },	# "commissionsale:PCBuyWindow", "cb1000"
	'btnCancel'		 : { 'text' : "取 消" },	# "commissionsale:PCBuyWindow", "btnCancel"
	'stChoose'		 : { 'text' : "面額選擇:" },	# "commissionsale:PCBuyWindow", "stChoose"
	'btnBuy'		 : { 'text' : "購 買" },	# "commissionsale:PCBuyWindow", "btnBuy"
	'taxisBtn_3'	 : { 'text' : "剩餘時間" },	# "commissionsale:PCBuyWindow", "taxisBtn_3"
	'taxisBtn_2'	 : { 'text' : "售價" },	# "commissionsale:PCBuyWindow", "taxisBtn_2"
	'taxisBtn_1'	 : { 'text' : "面額" },	# "commissionsale:PCBuyWindow", "taxisBtn_1"
	'lbTitle'		 : { 'color' : (241.0, 232.0, 110.0), 'text' : "購買點卡" },	# "commissionsale:PCBuyWindow", "lbTitle"
}

# 點卡購買窗口的時間列項
TimeCol = {
	'leaveTime_second'	: { 'text' : "%d秒" },	# "commissionsale:TimeCol", "leaveTime_second"
	'leaveTime_hour'	: { 'text' : "%d時" },	# "commissionsale:TimeCol", "leaveTime_hour"
	'leaveTime_minute'	: { 'text' : "%d分" },	# "commissionsale:TimeCol", "leaveTime_minute"
	'leaveTime_end'		: { 'text' : "寄售結束！" },	# "commissionsale:TimeCol", "leaveTime_end"
}

# 點卡出售窗口
PCSellWindow = {
	# clewText
	'explanation'	 : { 'text' : "1、寄售點卡需要支付押金，10元卡需要5金，@S{4}30元卡需要10金，押金在成功售出後退還。@S{3}若寄售點卡為無效點卡，押金將被沒收。@B{2}2、寄售點卡在24小時內無人購買，點卡將退回，@S{3}而押金將被沒收。"},	# "commissionsale:PCSellWindow", "explanation"
	'prompt'		 : { 'text' : "請輸入寄售點卡的卡號，密碼和寄售價格@F{fc=(211,175,9,255)}(請注意您的點卡不一定有人購買，所以請繼續保管好您的卡號和密碼)@D" },	# "commissionsale:PCSellWindow", "prompt"
	# btns
	'btnOK'			 : { 'text' : "確 定" },	# "commissionsale:PCSellWindow", "btnOK"
	'btnCancel'		 : { 'text' : "取 消" },	# "commissionsale:PCSellWindow", "btnCancel"
	# stText
	'lbTitle'		 : { 'color' : (241.0, 232.0, 110.0), 'text' : "寄售點卡" },	# "commissionsale:PCSellWindow", "lbTitle"
	'stResume'		 : { 'color' : (21.0, 195.0, 161.0), 'text' : "寄售說明" },	# "commissionsale:PCSellWindow", "stResume"
	'stInputTitle'	 : { 'color' : (21.0, 195.0, 161.0), 'text' : "點卡輸入" },	# "commissionsale:PCSellWindow", "stInputTitle"
	'stCardNo'		 : { 'text' : "卡    號：" },	# "commissionsale:PCSellWindow", "stCardNo"
	'stCardPsw'		 : { 'text' : "密    碼：" },	# "commissionsale:PCSellWindow", "stCardPsw"
	'stCardPrice'	 : { 'text' : "寄售價格：" },	# "commissionsale:PCSellWindow", "stCardPrice"
	'serverName'	 : { 'text' : "永恒之光" },	# "commissionsale:PCSellWindow", "serverName"
}

# TiShouSellPanel
TiShouSellPanel = {
	# 攤位形象選擇框
	'stallModel'		 : { 'text' : "攤位形象" },	# "commissionsale:TiShouSellPanel", "stallModel"
	'colouredGlazeFox'	 : { 'text' : "琉璃狐" },	# "commissionsale:TiShouSellPanel", "colouredGlazeFox"
	'blueTiger'			 : { 'text' : "藍色老虎" },	# "commissionsale:TiShouSellPanel", "blueTiger"
	'yellowTiger'		 : { 'text' : "黃色老虎" },	# "commissionsale:TiShouSellPanel", "yellowTiger"
	'lightningDog'		 : { 'text' : "閃電狗" },	# "commissionsale:TiShouSellPanel", "lightningDog"
	'bigHeadRacoon'		 : { 'text' : "大頭浣熊" },	# "commissionsale:TiShouSellPanel", "bigHeadRacoon"
	'blueMandarinDuck'	 : { 'text' : "藍色鴛鴦" },	# "commissionsale:TiShouSellPanel", "blueMandarinDuck"
	'fortunatePig'		 : { 'text' : "發財豬" },	# "commissionsale:TiShouSellPanel", "fortunatePig"
	# 剩餘時間提示
	'stRemainTime'		 : { 'color' : (6.0, 228.0, 192.0), 'text' : "寄售剩餘時間：" },	# "commissionsale:TiShouSellPanel", "stRemainTime"
	'stHour'		 : { 'color' : (6.0, 228.0, 192.0), 'text' : "%d小時" },	# "commissionsale:TiShouSellPanel", "stHour"
	'stMinute'		 : { 'color' : (6.0, 228.0, 192.0), 'text' : "%d分鐘" },	# "commissionsale:TiShouSellPanel", "stMinute"
	'stSecond'		 : { 'color' : (6.0, 228.0, 192.0), 'text' : "%d秒" },	# "commissionsale:TiShouSellPanel", "stSecond"
	# 攤主名
	'stOwnerName'	 : { 'text' : "店主：" },	# "commissionsale:TiShouSellPanel", "stOwnerName"
}

# TiShouGoodsPanel
TiShouGoodsPanel = {
	'ipBoxPrice'	 : { 'text' : "請輸入商品售價" },	# "commissionsale:TiShouGoodsPanel", "ipBoxPrice"
	'ipBoxNewPrice'	 : { 'text' : "請輸入新價格" },	# "commissionsale:TiShouGoodsPanel", "ipBoxNewPrice"
}

# TiShouPetsPanel
TiShouPetsPanel = {
	'ipBoxPrice'	 : { 'text' : "請輸入出售價格" },	# "commissionsale:TiShouPetsPanel", "ipBoxPrice"
	'ipBoxNewPrice'	 : { 'text' : "請輸入新價格" },	# "commissionsale:TiShouPetsPanel", "ipBoxNewPrice"
}

# 擺攤收購面板
TiShouPurchasePanel = {
	'ipBoxPrice'		 : { 'text' : "輸入單價" },	# "commissionsale:TiShouPurchasePanel", "ipBoxPrice"
	'ipBoxPurchaseAmount'	 : { 'text' : "收購數量" },	# "commissionsale:TiShouPurchasePanel", "ipBoxPurchaseAmount"
	'ipBoxTotalPrice'	 : { 'text' : "收購總額" },	# "commissionsale:TiShouPurchasePanel", "ipBoxTotalPrice"
	'ipBoxPurchaseSetting'	 : { 'text' : "收購設置" },	# "commissionsale:TiShouPurchasePanel", "ipBoxPurchaseSetting"
	'ipBoxNewPrice'		 : { 'text' : "請輸入新價格" },	# "commissionsale:TiShouPurchasePanel", "ipBoxNewPrice"
}

TSBuyPurchasePenel = {
	'ipBoxPrice'		 : { 'text' : "收購單價:" },	# "commissionsale:TSBuyPurchasePenel", "ipBoxPrice"
	'ipBoxPurchaseAmount'		 : { 'text' : "出售數量:" },	# "commissionsale:TSBuyPurchasePenel", "ipBoxPurchaseAmount"
	'ipBoxTotalPrice'		 : { 'text' : "收入總額:" },	# "commissionsale:TSBuyPurchasePenel", "ipBoxTotalPrice"
	'ipBoxPurchaseSetting'		 : { 'text' : "出售設置:" },	# "commissionsale:TSBuyPurchasePenel", "ipBoxPurchaseSetting"
}

TSSellWindow = {
	'shopName'		 : { 'text' : "%s的店鋪" },	# "commissionsale:TSSellWindow", "shopName"
}
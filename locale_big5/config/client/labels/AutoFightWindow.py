# -*- coding: cp950 -*-

# 主窗口
main = { "lbTitle": { "text": "自動戰鬥設置" },
		"btnCommend": {"text": "推薦設置" },
		"btnSave": { "text": "保存設置" },
		"btnPlus": { "text": "選擇增益技能" },
		"btnPickup": { "text": "自動拾取設置" },
		"bound_small": { "text": "較小範圍" },
		"bound_midd": { "text": "中等範圍" },
		"bound_big": { "text": "較大範圍" },
		"autoPickup": { "text": "開啟自動拾取" },
		"autoPlusSk": { "text": "自動施放增益技能" },
		"autoConjure": { "text": "寵物死亡後自動召喚寵物" },
		"autoResue": {"text": "角色死亡後自動使用歸命符籙"},
		"plus_0": { "text": "角色" },
		"plus_1": { "text": "寵物" },
		"plus_2": { "text": "隊友" },
		"rtWarnBeckon": { "text": "注意: 開啟自動召喚寵物功能可能會導致你寵物多次死亡" },
		"rtWarnResue": { "text": "注意: 開啟自動使用歸命符籙可能會導致你的角色多次死亡" },
		"Role_HP": { "text": "當生命值低於設置的數值時，自動使用藥品幫助人物恢復生命值。" },
		"Role_MP": { "text": "當魔法值低於設置的數值時，自動使用藥品幫助人物恢復魔法值。" },
		"Pet_HP": { "text": "當生命值低於設置的數值時，自動使用藥品幫助寵物恢復生命值。" },
		"Pet_MP": { "text": "當魔法值低於設置的數值時，自動使用藥品幫助寵物恢復魔法值。" },
		"Pet_Joyancy": { "text": "當快樂度低於設置的數值時，自動使用布娃娃幫助寵物恢復快樂度。" },
		"Equip_Repair": { "text": "當裝備耐久低於設定的數值時，自動使用天工槌恢復耐久值。"},
		"autoPick": { "text": "自動根據過濾設置拾取可拾取物品。" },
		"plusSkDsp": { "text": "自動保持指定目標身上的特定增益技能效果。" },
		"conjurDsp": { "text": "在寵物死亡後，自動召喚原先出戰的寵物。" },
		"resueDsp": { "text": "在角色死亡後，自動使用歸命符籙復活。" },
		"mediaSeting":{ "text": "藥品補充設置" },
		"assiSeting":{ "text": "輔助功能設置" },
		"choiceRange":{ "text": "請選擇自動戰鬥中角色的活動範圍" },
		"choiceTarget":{ "text": "請選擇增益技能的釋放對象(可多選)" },
		"petText": { "text": "寵物" },
		"roleText": { "text": "角色" },
		"equipText": { "text": "裝備"},
		"HPText":{ "text": "生命值<" },
		"MPText":{ "text": "魔法值<" },
		"joyText":{ "text": "快樂度<" },
		"durableText": { "text": "耐久度<"},
		"autoUseHP": { "text": "%自動使用紅藥" },
		"autoUseMP": { "text": "%自動使用藍藥" },
		"autoUseToy":{ "text": "%自動使用布娃娃" },
		"autoRepair":{ "text": "%使用天工槌"},
		}

#增益技能設置
PlusSkillSet = { "lbTitle" : { 'color' : 0xffffff, 'text' : "選擇增益技能",  'limning' : 2 },
		"btnOK": {"text": "確定" },
		"btnCancel":{"text": "取消" }

}

#自動拾取設置
PickUpSet = { "lbTitle" : { 'color' : 0xffffff, 'text' : "自動拾取設置",  'limning' : 2 },
		"btnSave": {"text": "保存" },
		"btnLoad":{"text": "加載" },
		"cbIgnore": {"text": "忽略列表"},
		"cbPickup": {"text": "拾取列表"},		
}
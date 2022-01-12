# -*- coding: UTF-8 -*-
#主窗口
main = { "lbTitle": { "color": ( 255, 241, 192, 255 ), "text": "对话", 'charSpace': 2 },
		"btnFulfill": { "font":"MSYHBD.TTF","fontSize":12, "text":"完成任务" },
		"btnAccept": { "font":"MSYHBD.TTF","fontSize":12, "text": "接受任务" },
		"btnQuit": { "font":"MSYHBD.TTF","fontSize":12, "text": "退 出" },
		"btnShut": { "font":"MSYHBD.TTF","fontSize":12, "text": "关 闭" },
		"finished": { "text": "完成" },
		"unfinished": { "text": "未完成" },
		"failure": { "text": "失败" },
		"questAim": { "text": "任务目标" },
		"followReward": { "text": "将获得下列奖励" },
		"querySubmit": { "text": "需要提交的物品" },
		}

GroupRewards = { "followReward": { "text": "你将获得以下物品奖励"},
			"groupExtrReward": { "text": "完成一组任务的额外总奖励:"},
			"randomStuff": { "text": "随机获得一件打造材料奖励。"},
			"choiceItem": { "text": "可供选择物品"},
			"randomItem": { "text": "随机奖励物品"},
			"fixedRandomItem": { "text": "固定随机物品奖励"},
		}

rewards = { "reward_fix_random" : { "text": "固定随机奖励:" },
		"reward_exp" : { "text": "人物经验奖励:" },
		"reward_money" : { "text": "金钱奖励:" },
		"reward_potential" : { "text": "潜能奖励:" },
		"reward_prestige" : { "text": "声望奖励:" },
		"reward_merchant_money" : { "text": "跑商奖励:" },
		"reward_tong_money" : { "text": "帮会资金奖励:" },
		"reward_tong_buildval" : { "text": "帮会建设度奖励:" },
		"reward_tong_contribute" : { "text": "帮会贡献度奖励:" },
		"reward_pet_exp" : { "text": "宠物经验奖励:" },
		"reward_ie_title" : { "text": "称号奖励:" },
		"reward_deposit" : { "text": "返还押金:" },
		"reward_random" : { "text": "随机奖励:" },
		"reward_tong_fete": { "text": "祭祀奖励:"},
		"petLevelTip": { "text": "请注意，如果宠物等级与任务等级差距过大，会对最终的经验获得造成影响。"},
		"sacrificeReward": { "text": "祭祀兑换奖励" },
		"reward_tongActionVal": { "text": "帮会行动力奖励" },
		"reward_daoheng" : { "text": "人物道行奖励" },
		"reward_skill" : { "text": "技能奖励:" },
		"reward_tong_exp" : { "text": "帮会经验奖励:" },
		}

submit = { "needPet": { "text": "需求宠物:" },
		"curPets": { "text": "现有宠物" },
		"questPets": { "text": "任务宠物" },
		"btnTransfer": { "text": "转 移 宠 物" },
		"pleaseInput": { "text": "请放入:%s" },
		"petLevel": { "text": "%d级" },
		}

exp2pot = {
	'cancelBtn'		 : { 'text' : "取消" },
	'okBtn'			 : { 'text' : "确定" },
	'lbExp'			 : { 'text' : "需要经验:" },
	'lbPotential'	 : { 'text' : "兑换潜能" },
	'lbTitle'		 : { 'color' : 0xffffff, 'text' : "兑换潜能",  'limning' : 2 },
}

LVReminder = {
	'btnOk' : { 'text' : "确定" },
}

ArtiRefine = {
	'lbTitle': { 'text' : "炼制神器", 'color': ( 255,241,192,255 ) },
	'btnRefine':{ 'text': "神器炼化" },
	'btnCancel':{'text':"取消" },
	'explain':{'text': "@S{4}想要炼制神器么？@B@S{4}首先，神器的胚子只能是绿色武器。@B@S{4}其次，你需要收集足够的材料。在我这里购买对应武器等级的未开光神器谱。右键点击接受任务。完成任务之后就可以获得开光的神器谱。同时，根据武器等级收集对应等级、足够数量的刑天神符。等级和神符对应如下：@B@S{10}50-59级：20个1级刑天神符；@B@S{10}60-69级：25个2级刑天神符；@B@S{10}70-79级：30个3级刑天神符；@B@S{10}80-89级：35个4级刑天神符；@B@S{10}90-99级：40个5级刑天神符。@B@S{10}100-109级：45个6级刑天神符。@B@S{4}最后，将武器放在下方的空框中，点“神器炼化”之后就可以将你的武器炼制为神器。"},
}

UnchainPrentice = {
	'lbTitle': { 'color' : (255.0, 248.0, 158.0), 'text' : "解除关系" },
}

import Language
if Language.LANG == Language.LANG_BIG5:
	ArtiRefine['explain'] = {'text': "@S{4}想要炼制神器么？@B@S{4}首先，神器的胚子只能是橘色武器。@B@S{4}其次，你需要收集足够的材料。在我这里购买对应武器等级的未开光神器谱。右键点击接受任务。完成任务之后就可以获得开光的神器谱。同时，根据武器等级收集对应等级、足够数量的刑天神符。等级和神符对应如下：@B@S{10}50-59级：20个1级刑天神符；@B@S{10}60-69级：25个2级刑天神符；@B@S{10}70-79级：30个3级刑天神符；@B@S{10}80-89级：35个4级刑天神符；@B@S{10}90-99级：40个5级刑天神符。@B@S{10}100-109级：45个6级刑天神符。@B@S{4}最后，将武器放在下方的空框中，点“神器炼化”之后就可以将你的武器炼制为神器。"}

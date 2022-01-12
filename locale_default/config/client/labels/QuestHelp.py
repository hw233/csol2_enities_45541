# -*- coding: UTF-8 -*-
main = { "btn_0": {"font":"MSYHBD.TTF","fontSize":12,"text":"已接任务" },
		"btn_1": {"font":"MSYHBD.TTF","fontSize":12,"text":"可接任务" },
		"btn_2": {"font":"MSYHBD.TTF","fontSize":12,"text":"查询" },
	}

# 已接任务日志
QuestList = { "lbTitle": {"font":"MSYHBD.TTF","fontSize":12, "text":"已接任务" },
			"questList": {"font":"MSYHBD.TTF","fontSize":12, "text":"已接任务" },
			"questCont": {"text":"任务内容" },
			"questCondi": {"text":"任务条件" },
			"questReward": {"text":"任务奖励" },
			"questTrace": {"font":"MSYHBD.TTF","fontSize":12, "text":"显示任务追踪" },
			"btnAbandon": {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF","fontSize":12, "text":"放弃任务" },
			"btnTrace": {"color":(231, 205, 140, 255), "font":"MSYHBD.TTF","fontSize":12, "text":"任务追踪" },
			"btnCommit" : {"color":(231, 205, 140, 255), "font":"MSYHBD.TTF","fontSize":12, "text":"完成任务"},
			"leadWayBee": {"text":"引路蜂" },
			"autoWayfind": {"text":"自动寻路" },
			"reWardBlessCoin": { "text": "@S{4}奖励福币" },
	}

# 可接任务
QuestCacept = { "lbTitle": {"text":"可接任务" },
			"canAcList": {"text":"可接任务" },
			"btnShut": {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF", "fontSize":12,"text":"关 闭" },
			"questArea": {"font":"MSYHBD.TTF", "fontSize":12,"text":"%s任务所在地:%s" },
			"questPublisher": {"font":"MSYHBD.TTF", "fontSize":12,"text":"%s任务发布人:%s" },
			"questLevel": {"font":"MSYHBD.TTF", "fontSize":12,"text":"%d级任务" },
			"levelInfo": {"font":"MSYHBD.TTF", "fontSize":12,"text":"%s任务等级:%s" },
			"autoFlyBtn": {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF", "fontSize":12,"text":"使用引路蜂" },
			"autoRunBtn": {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF", "fontSize":12,"text":"自动寻路" },
			"questDsp" : {"text":"任务描述" },
	}

#任务查询
QuestQuery = { "lbTitle": {"text":"查询" },
			"monster": {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF", "fontSize":12,"text":"怪物" },
			"quest": {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF", "fontSize":12,"text":"任务" },
			"level": {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF","fontSize":12, "text":"等 级" },
			"monsterName": {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF", "fontSize":12,"text":"怪物名称" },
			"area": {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF","fontSize":12,"text":"地 区" },
			"questName": {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF","fontSize":12,"text":"任务名称" },
			"TriggerNPC": {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF","fontSize":12,"text":"触发NPC" },
			"btnSearch": {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF", "fontSize":12,"text":"搜 索" },
			"selContent": {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF","fontSize":12, "text":"选择内容" },
			"keyWords": {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF","fontSize":12, "text":"关键字" },
			"preQuest" : {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF", "fontSize":12,"text":"前置任务 " },
			"nextQuest" : {"color":(231, 205, 140, 255),"font":"MSYHBD.TTF", "fontSize":12,"text":"后续任务 " },
			"btnRun":{ "color":(231, 205, 140, 255),"font":"MSYHBD.TTF", "fontSize":12,"text":"自动寻路" },
			"btnFly":{ "color":(231, 205, 140, 255),"font":"MSYHBD.TTF", "fontSize":12,"text":"引路蜂" },
	}
	
#任务Details
QuestDetails = { "lbTitle":{ "text":"任务详情" },
				"questLevel":{ "text":"任务等级:" },
				"questTitle":{ "text":"任务名称:" },
				"questArea":{ "text":"任务地区:" },
				"questNPC":{ "text":"触发NPC:" },
	}

QuestTrace = { "lbTitle": {"text":"任务追踪" },
			"fulfillText": {"text":"(完成)" },
			"dealQuest": {"text":"交任务" },
			"failQuest": {"text":"任务失败" },
			"distance": { "text":"距离" },
			"distanceUnknow": { "text":"距离未知" },
			}

dspPanel = {
	'itemTitle_1'	 : { 'text' : "任务内容" },
	'itemTitle_2'	 : { 'text' : "任务目标" },
	'itemTitle_3'	 : { 'text' : "任务条件" },
	'CRewardTitle_1'	 : { "font":"MSYHBD.TTF","fontSize":12,'text' : "你将获得以下物品奖励" },
	'CRewardTitle_2'	 : { "font":"MSYHBD.TTF","fontSize":12, 'text' : "你将获得以下随机物品奖励" },
	'CRewardTitle_3'	 : { "font":"MSYHBD.TTF","fontSize":12, 'text' : "你还可以获得以下奖励的其中一个" },
	'CRewardTitle_4'	 : { "font":"MSYHBD.TTF","fontSize":12, 'text' : "将获得下列奖励" },
	'CRewardTitle_5'	 : { "font":"MSYHBD.TTF","fontSize":12, 'text' : "你将获得一个与接任务时等级相同的物品"},
	'CRewardTitle_6'	 : { "font":"MSYHBD.TTF","fontSize":12, 'text' : "你将随机获得以下奖励中的一个"},
	'conditionTips'	 	 : { 'color':( 172,153,113,255 ), "font":"MSYHBD.TTF","fontSize":12, 'text' : "当前任务只要完成一个目标即可提交，完成更多的目标获得更丰厚的奖励。"},
	'CRewardTitle_7'	 : { "font":"MSYHBD.TTF","fontSize":12, 'text' : "你将获得以下技能奖励" },
	"conditions"		: { "font":"MSYHBD.TTF","fontSize":12, 'text' : "%s: %s  %s %s" },
}

typeNode = {
	'stComplete'	 : { 'text' : "完成" },
	'stUncomplete'	 : { 'text' : "未完成" },
	'stCollapsed'	 : { 'text' : "任务失败" },
	'stComplete_2'	 : { 'text' : "(完成)" },
	'stUncomplete_2'	 : { 'text' : "(未完成)" },
	'forceTips'	 : { 'text' : "【可选】" },
}

notify = {
	'newQuest'	 : { 'text' : "您有%i个可接取的随机触发任务" },
	'commitQuest'	 : { 'text' : "您完成了%i个可直接提交的任务" },
}

#悬赏任务
RewardQuestList = {
	'lbTitle'		: { 'text' : "悬赏" },
	'stNumberTips'	: { 'color':( 230, 227, 185 ),'text' : "今日可领取悬赏次数 %s" },
	'stRefreshTime' : { 'text' : "剩余刷新时间：%s" },
	'btnRefresh'	: { 'text' : "刷新" },
	'btnAccept'		: { 'text' : "接受" },
	'btnCompleted'	: { 'text' : "已完成" },
	'rewardsText'	: { 'text' : "奖励:" },
	'expText'		: { 'text' : "经验 %s" },


}
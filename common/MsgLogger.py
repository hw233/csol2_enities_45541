# -*- coding: gb18030 -*-
import Language
import sys
import bwdebug
from LogDefine import *

	
class MsgLogger( object ):
	_instance = None
	def __init__( self ):
		object.__init__( self )
	
	@staticmethod
	def instance():
		if MsgLogger._instance is None:
			MsgLogger._instance = MsgLogger()
		return MsgLogger._instance
	
	def getErrorMsg( self ):
		message = ""
		f = sys.exc_info()[2].tb_frame
		message += f.f_code.co_filename + "(" + str( f.f_lineno ) + ") :"
		funcName = f.f_code.co_name
		className = bwdebug._getClassName( f, funcName )
		message += "%s: %s: %s" % ( className,sys.exc_info()[0], sys.exc_info()[1] )

		return message
	
	#-----------------------------------
	# 任务
	#-----------------------------------
	def questLog( self, action, roleDBID, roleName, questID, param1 = "", param2 = "",  param3 = "", param4 = "" ):
		"""
		添加任务日志
		action:任务行为
		questID:任务ID
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_QUEST,"||%s||%s||%s||%s||%s||%s||%s||%s",action, roleDBID, roleName, questID, param1, param2, param3, param4 )
	
	def acceptQuestLog( self, roleDBID, roleName, questID, playerLevel, playerGrade ):
		""" 
		接受任务
		"""
		self.questLog( LT_QUEST_ACCEPT, roleDBID, roleName, questID, playerLevel, playerGrade )
	
	def completeQuestLog( self, roleDBID, roleName, questID, playerLevel, playerGrade, useTime ):
		"""
		接受任务
		useTime:使用多少时间
		"""
		self.questLog( LT_QUEST_COMPLETE, roleDBID, roleName, questID, playerLevel, playerGrade, useTime )
	
	def abandonQuestLog( self, roleDBID, roleName, questID, playerLevel, playerGrade):
		"""
		放弃任务
		"""
		self.questLog( LT_QUEST_ABANDON, roleDBID, roleName, questID, playerLevel, playerGrade )
	
	#-----------------------------------
	# 活动&副本
	#-----------------------------------
	def actCopyLog( self, action, activityType, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "", param6 = "", param7 = "" ):
		"""
		添加活动&副本日志
		activityType: 活动类型
		action:行为
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_ACT_COPY,"||%s||%s||%s||%s||%s||%s||%s||%s||%s", action, activityType, param1, param2 , param3, param4, param5, param6, param7 )
	
	def actStartLog( self, activityType ):
		"""
		活动开始
		"""
		self.actCopyLog( LT_AC_START, activityType )
	
	def actStopLog( self, activityType ):
		"""
		活动结束
		"""
		self.actCopyLog( LT_AC_STOP, activityType )
	
	def actKillMonsterLog( self, activityType, killDBID, killName, monsterClassName ):
		"""
		活动怪物被击杀
		"""
		self.actCopyLog( LT_AC_KILL_MONSTER, activityType, killDBID, killName, monsterClassName )
	
	def actMonsterDieLog( self, killDBID, killName, className ):
		"""
		活动怪物死亡
		"""
		activityType = 0
		for k,v in MONSTER_DIED_ABOUT_ACTIVITYS.iteritems():
			if className in v:
				activityType = k
				break
				
		if activityType:
			self.actKillMonsterLog( activityType, killDBID, killName, className )
	
	def actJoinLog( self, activityType, joinType, joinDBID, joinLevel, joinName ):
		"""
		活动参与
		joinDBID:要据joinType决定,可能是帮会DBID,可能是个人DBID
		"""
		self.actCopyLog( LT_AC_JOIN, activityType, joinType, joinDBID, joinLevel, joinName )
		
	def actJoinEnterSpaceLog( self, spaceType, joinType, joinDBID, joinLevel, joinName ):
		"""
		参与副本类活动,转换活动类型
		"""
		if COPYSPACE_ACTIVITYS.has_key( spaceType ): # 不在这个活动列表内,表示不需要记录
			self.actJoinLog( COPYSPACE_ACTIVITYS[ spaceType ], joinType, joinDBID, joinLevel, joinName )
	
	def actResultLog( self, activityType, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "" ):
		"""
		活动结果
		帮会车轮战（ param1：城市名字, param2：胜利帮会, param3：胜利队伍成员, param4：失败帮会, param5：失败帮会成员 ）
		烽火连天（ param1：城市名字, param2：胜利帮会, param3:失败帮会, param4：第几轮比赛 ）
		"""
		self.actCopyLog( LT_AC_RESULT, activityType, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "" )
	
	
	def actAnswerLog( self, activityType, roleDBID, roleName, result, param1 = "", param2 = "" ):
		"""
		活动答题
		activityType：活动类型
		roleDBID：角色DBID
		result：答题结果
		"""
		self.actCopyLog( LT_AC_ANSWER, activityType, roleDBID, roleName, result, param1, param2 )
	
	def actDistributionLog( self, activityType, param1 = "", param2 = "", param3 = "", param4 = "", param5 = ""  ):
		"""
		活动分配
		帮会掠夺战（param1：A帮会DBID,param2：A帮会名字,param3：B帮会DBID,param4：B帮会名字 ）
		"""
		self.actCopyLog( LT_AT_DISTRIBUTION, activityType, param1, param2, param3, param4, param5 )
	
	def actCopyOpenLog( self, className ):
		"""
		副本开启统计
		"""
		self.actCopyLog( LT_AT_COPY_OPEN, className )
	#-----------------------------------
	# 技能
	#-----------------------------------
	def skillLog( self, action, roleDBID, roleName, skillID, param1 = "", param2 = "", param3 = "", param4 = "" ):
		"""
		添加技能日志
		action:学或,遗忘……
		reason:获得方式
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_SKILL,"||%s||%s||%s||%s||%s||%s||%s||%s||%s",action, roleDBID, roleName, skillID, reason, param1, param2, param3, param4 )
	
	def skillLearnLog( self, roleDBID, roleName, skillID, usePotential, useMoney ):
		"""
		角色学习新技能
		"""
		self.skillLog( LT_SKILL_LEARN, roleDBID, roleName, skillID, usePotential, useMoney )
	
	def skillUpgradeLog( self, roleDBID, roleName, skillID, oldSkillID, usePotential, useMoney ):
		"""
		角色升级技能
		"""
		self.skillLog( LT_SKILL_UPGRADE, roleDBID, roleName, skillID, oldSkillID, usePotential, useMoney )
	
	def skillRemoveLog( self, roleDBID, roleName, skillID ):
		"""
		角色遗忘技能（目前只有生活技能）
		"""
		self.skillLog( LT_SKILL_REMOVE, roleDBID, roleName, skillID )
	
	def skillPGLearnLog( self, roleDBID, roleName, skillID ):
		"""
		角色学习盘古技能
		"""
		self.skillLog( LT_SKILL_PG_LEARN, roleDBID, roleName, skillID )
	
	def skillPGUpgradeLog( self, roleDBID, roleName, skillID, oldSkillID ):
		"""
		角色升级盘古技能
		"""
		self.skillLog( LT_SKILL_PG_UPGRADE, roleDBID, roleName, skillID, oldSkillID )
	
	def skillTongLearnLog( self, roleDBID, roleName, skillID, usePotential, useMoney ):
		"""
		角色学习帮会技能
		"""
		self.skillLog( LT_SKILL_TONG_LEARN, roleDBID, roleName, skillID, usePotential, useMoney )
	
	def skillTongUpgradeLog( self, roleDBID, roleName, skillID, oldSkillID, usePotential, useMoney ):
		"""
		角色升级帮会技能
		"""
		self.skillLog( LT_SKILL_TONG_UPGRADE, roleDBID, roleName, skillID, oldSkillID, usePotential, useMoney )
	
	def skillPetLearnLog( self, roleDBID, roleName, petDBID, skillID ):
		"""
		宠物学习技能
		"""
		self.skillLog( LT_SKILL_PET_LEARN, roleDBID, roleName, petDBID, skillID )
	
	def skillPetUpgradeLog( self, roleDBID, roleName, petDBID, skillID, oldSkillID ):
		"""
		宠物升级技能
		"""
		self.skillLog( LT_SKILL_PET_UPGRADE, roleDBID, roleName, petDBID, skillID, oldSkillID )
	
	def skillVehicleLearnLog( self, roleDBID, roleName, vehicleID, skillID, usePotential, useMoney ):
		"""
		骑宠学习技能
		"""
		self.skillLog( LT_SKILL_VEHICLE_LEARN, roleDBID, roleName, vehicleID, skillID, usePotential, useMoney )
	
	def skillVehicleUpgradeLog( self, roleDBID, roleName, vehicleID, skillID, oldSkillID, usePotential, useMoney ):
		"""
		骑宠升级技能
		"""
		self.skillLog( LT_SKILL_VEHICLE_UPGRADE, roleDBID, roleName, skillID, oldSkillID, usePotential, useMoney )
	
	#-----------------------------------
	# 组织
	#-----------------------------------
	def orgLog( self, orgType, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "", param6 = "", param7 = "", param8 = "", param9 = ""):
		"""
		添加组织日志
		orgType:帮会,婚姻,师徒
		原因:退帮会,换帮主,结婚,离婚……
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_ORG,"||%s||%s||%s||%s||%s||%s||%s||%s||%s||%s",orgType, param1, param2, param3, param4, param5, param6, param7, param8, param9 )
		
	# 帮会
	def tongCreateLog( self, tongDBID, tongName, creatorDBID, creatorName  ):
		"""
		帮会创建
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_CREATE, tongName, creatorDBID, creatorName )
	
	def tongDismissLog( self, tongDBID, tongName, reason ):
		"""
		帮会解散
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_DISMISS, tongDBID, tongName, reason )

	def tongMoneyChangeLog( self, tongDBID, tongName, oldValue, newValue, reason ):
		"""
		帮会金钱改变
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_MONEY_CHANGE, tongDBID, tongName, oldValue, newValue, reason )
	
	def tongBuildingChangeLog( self, tongDBID, tongName, buildingType, oldValue, newValue ):
		"""
		帮会建筑度改变
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_BUILDING_CHANGE, tongDBID, tongName, buildingType, oldValue, newValue  )
	
	def tongItemAddLog( self, tongDBID, tongName, roleDBID, roleName, itemUID, itemID, itemNum, itembagID  ):
		"""
		帮会仓库物品添加
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_ITEMBAGS_ADD, tongDBID, tongName, roleDBID, roleName, itemUID, itemID, itemNum, itembagID )
	
	def tongItemRemoveLog( self, tongDBID, tongName, roleDBID, roleName, itemUID, itemID, itemNum, itembagID  ):
		"""
		帮会仓库物品删除
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_ITEMBAGS_REMOVE, tongDBID, tongName, roleDBID, roleName, itemUID, itemID, itemNum, itembagID )
	
	def tongUpgradeLog( self, tongDBID, tongName, tongLevel, reason ):
		"""
		帮会升级
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_UPLEVEL, tongDBID, tongName, tongLevel, reason )
	
	def tongDemotionLog( self, tongDBID, tongName, tongLevel, reason ):
		"""
		帮会降级
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_DEMOTION, tongDBID, tongName, tongLevel, reason )
	
	def tongPrestigeChangeLog( self, tongDBID, tongName, oldPrestige, nowPrestige, reason ):
		"""
		帮会声望改变
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_PRESTIGE_CHANGE, tongDBID, tongName, oldPrestige, nowPrestige, reason )
	
	def tongMemberAddLog( self, tongDBID, tongName, roleDBID, roleName, count ):
		"""
		帮会加入新成员
		count:当前帮会总人数
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_MEMBER_ADD, tongDBID, tongName, roleDBID, roleName, count  )
	
	def tongMemberRemoveLog( self, tongDBID, tongName, roleDBID, roleName, count ):
		"""
		帮会删除成员
		count:当前帮会总人数
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_MEMBER_REMOVE, tongDBID, tongName, roleDBID, roleName, count )
	
	def tongLeaderChangeLog( self, tongDBID, tongName, roleDBID, roleName, reason = 0 ):
		"""
		帮会会长改变
		memNums:当前帮会总人数
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_LEADER_CHANGE, tongDBID, tongName, roleDBID, roleName, reason  )
	
	def tongSetGradeLog( self, tongDBID, tongName, doRoleDBID, doRoleName, setRoleDBID, setRoleName, oldGrade, nowGrade ):
		"""
		帮会设置成员权限
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_SET_GRADE, tongDBID, tongName, doRoleDBID, doRoleName, setRoleDBID, setRoleName, oldGrade, nowGrade  )
		
	def tongWageLog( self, tongDBID, tongName, roleName, roleGrade, money ):
		"""
		帮会工资发放
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_WAGE, tongDBID, tongName, roleName, roleGrade, money  )
	
	def tongCityWarSetMasterLog( self, tongDBID, tongName, cityName ):
		"""
		设置城主
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_CITY_WAR_SET_MASTER, tongDBID, tongName, cityName )
	
	def tongGetRevenueLog( self, tongDBID, tongName, memberDBID, money ):
		"""
		领取税收
		memberDBID:领取人的DBID
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_CITY_G_REVENUE,tongDBID, tongName, memberDBID, money )
	
	def tongReceiveRevenueLog( self, tongDBID, tongName, cityName, money ):
		"""
		收税
		tongDBID:占领城市
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_CITY_R_REVENUE, tongDBID, tongName, cityName, money )
	
	def tongExpChangeLog(  self, tongDBID, tongName, oldValue, newValue, reason ):
		"""
		帮会经验改变
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_EXP_CHANGE, tongDBID, tongName, oldValue, newValue, reason )

	#婚姻
	def sweeticBuildLog( self, roleDBID, roleName, tRoleDBID, tRoleName ):
		"""
		恋人关系的建立
		"""
		self.orgLog( LT_ORG_MARRY_SWEETIE, LT_ORG_MARRY_SWEETIE_BUILD, roleDBID, roleName, tRoleDBID, tRoleName )
	
	def sweeticRemoveLog( self, roleDBID, roleName, tRoleDBID ):
		"""
		恋人关系的解除
		"""
		self.orgLog( LT_ORG_MARRY_SWEETIE, LT_ORG_MARRY_SWEETIE_REMOVE, roleDBID, roleName, tRoleDBID )
	
	def coupleBuildLog( self, roleDBID, roleName, tRoleDBID, troleName ):
		"""
		建立夫妻关系
		"""
		self.orgLog( LT_ORG_MARRY_SWEETIE, LT_ORG_MARRY_COUPLE_BUILD, roleDBID, roleName, tRoleDBID, troleName )
	
	def coupleRemoveLog( self, roleDBID, roleName, tRoleDBID ):
		"""
		解除夫妻关系
		"""
		self.orgLog( LT_ORG_MARRY_SWEETIE, LT_ORG_MARRY_COUPLE_REMOVE, roleDBID, roleName, tRoleDBID )
	
	# 师徒
	def teachBuildLog( self, shifuDBID, shifuName, tudiDBID, tudiName ):
		"""
		建立师徒关系
		"""
		self.orgLog( LT_ORG_TEACH, LT_ORG_TEACH_BUILD, shifuDBID, shifuName, tudiDBID, tudiName )
		
	def teachRemoveLog( self, shifuDBID, shifuName, tudiDBID, tudiName ):
		"""
		解除师徒关系
		"""
		self.orgLog( LT_ORG_TEACH, LT_ORG_TEACH_REMOVE,  shifuDBID, shifuName, tudiDBID, tudiName )
		
	def teachCompleteLog( self, shifuDBID, shifuName, tudiDBID ):
		"""
		出师
		"""
		self.orgLog( LT_ORG_TEACH, LT_ORG_TEACH_COMPLETE, shifuDBID, shifuName, tudiDBID )
	
	#结拜
	def allyListChangeLog( self, nameList, DBIDList ):
		"""
		结拜列表改变
		"""
		self.orgLog( LT_ORG_ALLY, LT_ORG_ALLY_CHANGE, str( DBIDList ), str( nameList ) )
	
	#-----------------------------------
	# 功能（包括：GM,邮件等)
	#-----------------------------------
	def funcLog( self, funcType, param1 = "", param2 = "", param3 = "", param4 = "", param5  = "", param6 = "", param7 = "", param8 = "", param9 = "" ):
		"""
		功能
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_FUNC,"||%s||%s||%s||%s||%s||%s||%s||%s||%s||%s", funcType, param1, param2, param3, param4, param5, param6, param7,param8,param9 )
	
	def gmCommonLog( self, command, args, srcEntityDBID, dstEntityDBID, srcEntityGrade, extend = None ):
		"""
		使用GM指令
		"""
		self.funcLog( LT_FUNC_GM, LT_FUNC_GM_COMMAND, command, args, srcEntityDBID, dstEntityDBID, srcEntityGrade, extend )
	
	# 邮箱功能
	def mailSendLog( self, senderName, receiverName, title, itemNum, money ):
		"""
		发送邮件
		"""
		self.funcLog( LT_FUNC_MAIL, LT_FUNC_MAIL_SEND, senderName, receiverName, title, itemNum, money )

	def mailReadLog( self, senderName, receiverName, title, mailID ):
		"""
		阅读邮件
		"""
		self.funcLog( LT_FUNC_MAIL, LT_FUNC_MAIL_READ, senderName, receiverName, title, mailID )
	
	def mailReturnLog( self, senderName, receiverName, title, mailID ):
		"""
		主动退信
		"""
		self.funcLog( LT_FUNC_MAIL, LT_FUNC_MAIL_RETURN, senderName, receiverName, title, mailID )
		
	def mailRemoveLog( self, senderName, receiverName, title, mailID ):
		"""
		删除邮件
		"""
		self.funcLog( LT_FUNC_MAIL, LT_FUNC_MAIL_REMOVE, senderName, receiverName, title, mailID )
	
	def mailSysReturnLog( self, senderName, receiverName, title, mailID ):
		"""
		主动退信
		"""
		self.funcLog( LT_FUNC_MAIL, LT_FUNC_MAIL_SYS_RETURN, senderName, receiverName, title, mailID )
	
	def mailUpTimeLog( self, readedTime, readedHintTime, title, mailID ):
		"""
		更新邮件时间
		readedHintTime:提示时间
		"""
		self.funcLog( LT_FUNC_MAIL, LT_FUNC_MAIL_UP_TIME, senderName, receiverName, title, mailID )
	
	#账号
	def accountLogonLog( self, account, ip, intro ):
		"""
		账号登陆
		intro：字符介绍
		"""
		self.funcLog( LT_FUNC_ACCOUNT, LT_FUNC_ACCOUNT_LOGON, account, ip, intro )
	
	def accountLogoutLog( self, account, ip, intro ):
		"""
		账号下线
		intro：字符介绍
		"""
		self.funcLog( LT_FUNC_ACCOUNT, LT_FUNC_ACCOUNT_LOGOUT, account, ip, intro )
		
	# 角色
	def roleLogonLog( self, roleDBID, roleName, account, onlineTime, ip, intro ):
		"""
		角色上线
		intro：字符介绍
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_LOGON, roleDBID, roleName, account, onlineTime, ip, intro  )
	
	def roleLogoutLog( self, roleDBID, roleName, account, onlineTime, ip, intro ):
		"""
		角色返回角色选择
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_LOGOUT, roleDBID, roleName, account, onlineTime, ip, intro )
	
	def roleLogoffLog( self, ip, accountName, nameAndID, onlineTime, intro ):
		"""
		角色返回账号登陆
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_LOGOFF, ip, accountName, nameAndID, onlineTime, intro )
	
	def roleUpgradeLog( self, roleDBID, roleName, oldLevel, nowLevel, lifeTime ):
		"""
		角色升级
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_UPGRADE, roleDBID, roleName, oldLevel, nowLevel, lifeTime )
	
	def roleTrainingsLog( self, roleDBID, roleName, type ):
		"""
		角色经验代练
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_START_TRAININGS, roleDBID, roleName, type )
	
	def roleBeKillLog( self, killDBID, beKillDBID, killGrade ):
		"""
		角色被杀死记录
		killDBID = 0时,killer是怪物
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_BEKILL, killDBID, beKillDBID, killGrade )
	
	def roleOnLineLog( self, roleDBID, roleName, roleLevel, tongDBID, tongGrade ):
		"""
		角色创建完成
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_ONLINE, roleDBID, roleName, roleLevel, tongDBID, tongGrade )
	
	def accountRoleAddLog( self, account, roleDBID, roleName ):
		"""
		新增角色
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_ADD, account, roleDBID, roleName )
	
	def accountRoleDelLog( self, account, roleDBID, roleName ):
		"""
		删除账号上的角色
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_DELETE, account, roleDBID, roleName )
		
	def sendRumorLog( self, roleDBID, roleName, msg ):
		"""
		角色发谣言
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_SEND_RUMOR, roleDBID, roleName, "\"%s\""%msg )
		
	# 摆摊
	def roleVendLog( self, roleDBID, roleName ):
		"""
		玩家摆摊
		"""
		self.funcLog( LT_FUNC_VEND, LT_FUNC_VEND, roleDBID, roleName )
	
	# 装备
	def equipStilettoLog( self, roleDBID, roleName, itemUID, newItemUID, itemName, itemSlot, newSlot ):
		"""
		装备打孔
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_STILETTO, roleDBID, roleName, itemUID, newItemUID, itemName, itemSlot, newSlot )
			
	def equipIntensifyLog( self, roleDBID, roleName, itemUID, newItemUID, itemName, intensifyLevel, newIntensifyLevel ):
		"""
		装备强化
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_INTENSIFY, roleDBID, roleName, itemUID, newItemUID, itemName, intensifyLevel, newIntensifyLevel )
	
	def equipBindLog( self, roleDBID, roleName, itemUID, newItemUID, itemName ):
		"""
		装备认主
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_BIND, roleDBID, roleName, itemUID, newItemUID, itemName )
	
	def equipReBuildLog( self, roleDBID, roleName, itemUID, newItemUID, itemName, itemInfos, newItemInfos ):
		"""
		装备改造
		itemInfos:[品质,前缀]
		newItemInfos:[品质,前缀]
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_REBUILD, roleDBID, roleName, itemUID, newItemUID, itemName, itemInfos, newItemInfos )
	
	def equipSpecialComposeLog( self, roleDBID, roleName, newItemUID, itemName ):
		"""
		装备的特殊合成
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_SPECIAL_COMPOSE, roleDBID, roleName, newItemUID, itemName )
	
	def equipImproveLog( self, roleDBID, roleName, itemUID, newItemUID, itemName ):
		"""
		绿装升品
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_IMPROVE_QUALITY, roleDBID, roleName, itemUID, newItemUID, itemName )
	
	def equipGodLog( self, roleDBID, roleName, itemUID, newItemUID, itemName, intensifyLevel, skillID ):
		"""
		炼制神器
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_REFINE_GODWEAPON, roleDBID, roleName, itemUID, newItemUID, itemName, intensifyLevel, skillID )
	
	def equipStuffComposeLog( self, roleDBID, roleName, newItemUID, newItemName, newItemNum ):
		"""
		材料合成
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_STUFF_COMPOSE, roleDBID, roleName, newItemUID, newItemName, newItemAmount )
	
	def equipSplitLog( self, roleDBID, roleName, itemUID, itemName ):
		"""
		装备分拆
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_SPLIT, roleDBID, roleName, itemUID, itemName )
	
	def equipStuddedLog( self, roleDBID, roleName, itemUID, newItemUID, itemName, itemSlot, newItemSlot, effectAttr ):
		"""
		装备镶嵌
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_STUDDED, roleDBID, roleName, itemUID, newItemUID, itemName, itemSlot, newItemSlot, effectAttr )
	
	def equipChangePropertyLog( self, roleDBID, roleName, itemUID, newItemUID, itemName, prefix, newPrefix ):
		"""
		绿装洗前缀
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_CHANGE_PROPERTY, roleDBID, roleName, itemUID, newItemUID, itemName, prefix, newPrefix )
	
	def equipMakeLog( self, roleDBID, roleName, itemUID, itemName, oldQuality, quality, oldPrefix, prefix ):
		"""
		装备制造
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_MAKE, roleDBID, roleName, itemUID, itemName, oldQuality, quality, oldPrefix, prefix )
	
	def equipRepairNormalLog( self, roleDBID, roleName, itemUID, itemName, oldHardinessMax, newHardinessMax, repairMoney, spaceLabel,npcID ):
		"""
		装备普通修理
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_REPAIR_NORMAL, roleDBID, roleName, itemUID, itemName, oldHardinessMax, newHardinessMax, repairMoney, spaceLabel, npcID )
	
	# 水晶
	def crystalRemoveLog( self, roleDBID, roleName, itemUID, itemName, itemLevel ):
		"""
		水晶摘除
		"""
		self.funcLog( LT_FUNC_CRYSTAL, LT_FUNC_CRYSTAL_REMOVE, roleDBID, roleName, itemUID, itemName, itemLevel )
	
	# 法宝
	def talismanAddLifeLog( self, roleDBID, roleName, itemUID, itemName, itemLife ):
		"""
		法宝充值
		"""
		self.funcLog( LT_FUNC_TALISMAN, LT_FUNC_TALISMAN_ADD_LIFE, roleDBID, roleName, itemUID, itemName, itemLife )
	
	def talismanSplitLog( self, roleDBID, roleName, itemUID, itemName ):
		"""
		法宝分解
		"""
		self.funcLog( LT_FUNC_TALISMAN, LT_FUNC_TALISMAN_SPLIT, roleDBID, roleName, itemUID, itemName )
	
	def talismanIntensifyLog( self, roleDBID, roleName, itemUID, itemName, intensifyLevel):
		"""
		法宝强化
		intensifyLevel:强化等级
		"""
		self.funcLog( LT_FUNC_TALISMAN, LT_FUNC_TALISMAN_INTENSIFY, roleDBID, roleName, itemUID, oldItemName, itemName, itemLevel, intensifyLevel )
	
	#宠物
	def petAddLog( self, roleDBID, roleName, petDBID, petName, reason ):
		"""
		获得宠物
		"""
		self.funcLog( LT_FUNC_PET, LT_FUNC_PET_ADD, roleDBID, roleName, petDBID, petName, reason )
	
	def petDelLog( self, roleDBID, roleName, petDBID, petName, reason ):
		"""
		失去宠物
		"""
		self.funcLog( LT_FUNC_PET, LT_FUNC_PET_DEL, roleDBID, roleName, petDBID, petName, reason )

	def petBreedLog( self, aRoleDBID, aPetData, bRoleDBID, bPetData ):
		"""
		宠物繁殖
		"""
		self.funcLog( LT_FUNC_PET, LT_FUNC_PET_BREED, aRoleDBID, aPetData, bRoleDBID, bPetData )
	
	def petStartTrainingsLog( self, roleDBID, roleName, petDBID, trainType ):
		"""
		宠物经验代练
		"""
		self.funcLog( LT_FUNC_PET, LT_FUNC_PET_START_TRAININGS, roleDBID, roleName, petDBID, trainType )
	
	# 交易
	def tradeNpcBuyLog( self, roleDBID, roleName, itemUID, itemName, amount, payMoney, grade, chapman, spaceLabel ):
		"""
		在NPC商人处买东西
		"""
		self.funcLog( LT_FUNC_TRADE, LT_FUNC_TRADE_NPC_BUY, roleDBID, roleName, itemUID, itemName, amount, payMoney, grade, chapman, spaceLabel )
	
	def tradeNpcSellLog( self, roleDBID, roleName, itemUID, itemName, amount, getMoney, grade, chapman ):
		"""
		卖东西给NPC商人
		"""
		self.funcLog( LT_FUNC_TRADE, LT_FUNC_TRADE_NPC_SELL, roleDBID, roleName, itemUID, itemName, amount, getMoney, grade, chapman)
	
	def tradeRoleMoneyLog( self, roleDBID, roleName, tRoleDBID, tRolName, money, tradeID ):
		"""
		与玩家交易金钱
		"""
		self.funcLog( LT_FUNC_TRADE, LT_FUNC_TRADE_SWAP_MONEY, roleDBID, roleName, tRoleDBID, tRolName, money, tradeID)
	
	def tradeRoleItemLog( self, roleDBID, roleName, tRoleDBID, tRolName, itemUID, itemName, amount, tradeID ):
		"""
		与玩家交易物品
		"""
		self.funcLog( LT_FUNC_TRADE, LT_FUNC_TRADE_SWAP_ITEM, roleDBID, roleName, tRoleDBID, tRolName, itemUID, itemName, amount, tradeID  )
	
	def tradeRolePetLog( self, roleDBID, roleName, tRoleDBID, tRolName, petDBID, tradeID ):
		"""
		与玩家交易宠物
		"""
		self.funcLog( LT_FUNC_TRADE, LT_FUNC_TRADE_SWAP_PET, roleDBID, roleName, tRoleDBID, tRolName, petDBID, tradeID)
	
	# 替身寄售
	def tiShouBuyPetLog( self, roleDBID, roleName, ownerDBID, ownerName, petDBID, price ):
		"""
		从替身上购买宠物
		ownerDBID：替身主人
		"""
		self.funcLog( LT_FUNC_TI_SHOU, LT_FUNC_TI_SHOU_BUY_PET, roleDBID, roleName, ownerDBID, ownerName, petDBID, price )
	
	def tiShouBuyItemLog( self, roleDBID, roleName, ownerDBID, ownerName, itemUID, itemName, itemAmount, price ):
		"""
		从替身上购买物品
		ownerDBID：替身主人
		"""
		self.funcLog( LT_FUNC_TI_SHOU, LT_FUNC_TI_SHOU_BUY_ITEM, roleDBID, roleName, ownerDBID, ownerName, itemUID, itemName, itemAmount, price )
	
	#采集
	def collectLog( self, roleDBID, roleName, spaceLabel, collectPoint ):
		"""
		采集
		"""
		self.funcLog( LT_FUNC_COLLECT, LT_FUNC_COLLECT, roleDBID, roleName, spaceLabel, collectPoint)
	
	#点卡
	def pointCardRechargeLog( self, cardNo, price, buyerName, buyerAccount, salesName ):
		"""
		点卡充值
		"""
		self.funcLog( LT_FUNC_PC, LT_FUNC_PC_RECHARGE, cardNo, price, buyerName, buyerAccount, salesName )
	
	#反外挂
	def apexKickRoleLog( self, roleDBID, roleName, hiByte, lowByte ):
		"""
		反外挂踢玩家下线
		hiByte:操作原因
		lowByte：操作的类型 如封号 踢下线
		"""
		self.funcLog( LT_FUNC_AP, LT_FUNC_AP_KICK_ROLE, roleDBID, roleName, hiByte, lowByte )
	
	#宠物仓库
	def petStorageAddLog( self, roleDBID, roleName, petDBID, petName ):
		"""
		往宠物仓库放宠物
		"""
		self.funcLog( LT_FUNC_PET_STORAGE, LT_FUNC_PET_STORAGE_ADD, roleDBID, roleName, petDBID, petName )
	
	def petStorageTakeLog( self, roleDBID, roleName, petDBID, petName ):
		"""
		往宠物仓库取走宠物
		"""
		self.funcLog( LT_FUNC_PET_STORAGE, LT_FUNC_PET_STORAGE_TAKE, roleDBID, roleName, petDBID, petName )
	
	#道具商城
	def specialShopBuyLog( self, account, gold, silver, itemID, amount ):
		"""
		从道具商城买物品
		"""
		self.funcLog( LT_FUNC_SPECIAL_STOP, LT_FUNC_SPECIAL_STOP_BUY, account, gold, silver, itemID, amount )
	
	#仓库
	def bankStoreLog( self, roleDBID, roleName, itemUID, itemName, ItemAmount ):
		"""
		东西存入仓库
		"""
		self.funcLog( LT_FUNC_BANK, LT_FUNC_BANK_STORE, roleDBID, roleName, itemUID, itemName, ItemAmount )
		
	def bankTakeLog( self, roleDBID, roleName, itemUID, itemName, ItemAmount ):
		"""
		从仓库取东西
		"""
		self.funcLog( LT_FUNC_BANK, LT_FUNC_BANK_TAKE, roleDBID, roleName, itemUID, itemName, ItemAmount )
		
	def bankDestroyLog( self, roleDBID, roleName, itemUID, itemName, ItemAmount ):
		"""
		销毁物品
		"""
		self.funcLog( LT_FUNC_BANK, LT_FUNC_BANK_DES, roleDBID, roleName, itemUID, itemName, ItemAmount )
	
	def bankExtendLog( self, roleDBID, roleName, extNum, extGridNum ):
		"""
		仓库拓充
		extNum：拓充次数
		extGridNum：拓充多少个格子
		"""
		self.funcLog( LT_FUNC_BANK, LT_FUNC_BANK_EXTEND, roleDBID, roleName, itemUID, itemName, ItemAmount )
	
	#订单领取
	def presentBackageLog( self, account, transactionID, packageID, expiredTime ):
		"""
		奖品包
		account：账号, transactionID：订单号, packageID：礼包ID,expiredTime：过期时间
		"""
		self.funcLog( LT_FUNC_PRESENT, LT_FUNC_PRESENT_PACKAGE, account, transactionID, packageID, expiredTime )
		
	def presentSilverLog( self, account, transactionID, silver ):
		"""
		奖银元宝
		account：账号, transactionID：订单号, packageID：礼包ID,expiredTime：过期时间
		"""
		self.funcLog( LT_FUNC_PRESENT, LT_FUNC_PRESENT_SILVER, account, transactionID, silver )
	
	def presentChargeLog( self, account, transactionID , ChargeType, GoldCoins, SilverCoins ):
		"""
		充值
		ChargeType：充值类型
		GoldCoins：金元宝
		SilverCoins：银元宝
		"""
		self.funcLog( LT_FUNC_PRESENT, LT_FUNC_PRESENT_CHARGE, account, transactionID , ChargeType, GoldCoins, SilverCoins )
	
	#-----------------------------------
	# 统计
	#-----------------------------------
	def countLog( self, countType, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "", param6 = "", param7 = ""  ):
		"""
		统计
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_COUNT,"||%s||%s||%s||%s||%s||%s||%s||%s",countType, param1, param2, param3, param4, param5, param6, param7 )
	
	def countWealthLog( self, roleDBID, roleName, roleMoney, countTime ):
		"""
		玩家财富统计
		"""
		self.countLog( LT_COUNT_ROLE_WEALTH, roleDBID, roleName, roleMoney, countTime )
	
	def countLevelLog( self, level, rcmaskClass, countTime ):
		"""
		角色等级&职业统计
		"""
		self.countLog( LT_COUNT_ROLE_LEVEL, level, rcmaskClass, countTime )
		
	def countRoleLog( self, waitAccountNum, loginAccountNum, summation ):
		"""
		统计玩家的在线人数
		waitAccountNum:等待队列中的玩家数量, 
		loginAccountNum:登陆队列中的玩家数量, 
		summation:在线玩家的数量
		"""
		self.countLog( LT_COUNT_ROLE_COUNT, waitAccountNum, loginAccountNum, summation )
		
	def countTongInfoLog( self, tongName, tongLevel, tongMoney, tongMembers, averageLevel, maxLevel, minLevel ):
		"""
		帮会信息统计
		"""
		self.countLog( LT_COUNT_TONG_INFO, tongName, tongLevel, tongMoney, tongMembers, averageLevel, maxLevel, minLevel )
	
	def countTongNumLog( self, count ):
		"""
		帮会数量统计
		"""
		self.countLog( LT_COUNT_TONG_COUNT, count )
	
	def countOnlineAccountLog( self, accountNum,param1, param2, param3, param4, param5 ):
		"""
		在线账号
		"""
		self.countLog( LT_COUNT_ONLINE_ACCOUNT, accountNum, param1, param2, param3, param4, param5 )
		
	#-----------------------------------
	# 属性
	#-----------------------------------
	def proLog( self, type, roleDBID, roleName, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "", param6 = "" ):
		"""
		添加角色日志
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_PRO,"||%s||%s||%s||%s||%s||%s||%s||%s||%s",type, roleDBID, roleName, param1, param2, param3, param4, param5, param6 )
	
	def expChangeLog( self, roleDBID, roleName, oldExp, oldLevel, nowExp, nowLevel, reason ):
		"""
		角色经验改变
		"""
		self.proLog( LT_PRO_EXP_CHANGE, roleDBID, roleName, oldExp, oldLevel, nowExp, nowLevel, reason )
	
	def potentialChangeLog( self, roleDBID, roleName, oldPotential, nowPotential, reason ):
		"""
		潜能改变
		"""
		self.proLog( LT_PRO_POTENTIAL_CHANGE, roleDBID, roleName, oldPotential, nowPotential, reason )
			
	# 道行
	def daohengAddLog( self, roleDBID, roleName, curDaoheng, value, reason = 0 ):
		"""
		道行增长
		"""
		self.proLog( LT_PRO_DAOHENG_ADD, roleDBID, roleName, curDaoheng, value, reason)
	
	def daohengSetLog( self, roleDBID, roleName, value ):
		"""
		GM设置道行的值
		"""
		self.proLog( LT_PRO_DAOHENG_SET, roleDBID, roleName, value )
	
	# 积分
	def scoreHonorAddLog( self, roleDBID, roleName, score, reason ):
		"""
		个人荣誉增加
		"""
		self.proLog( LT_PRO_SCORE_HONOR_ADD, roleDBID, roleName, score, reason)
	
	def scoreHonorSubLog( self, roleDBID, roleName, score, reason ):
		"""
		个人荣誉增加
		"""
		self.proLog( LT_PRO_SCORE_HONOR_SUB, roleDBID, roleName, score, reason)
	
	def scorePersonalAddLog( self, roleDBID, roleName, score, reason ):
		"""
		增加个人竞技积分
		"""
		self.proLog( LT_PRO_SCORE_PERSONAL_ADD, roleDBID, roleName, score, reason)
	
	def scorePersonalSubLog( self, roleDBID, roleName, score, reason ):
		"""
		减少个人竞技积分
		"""
		self.proLog( LT_PRO_SCORE_PERSONAL_SUB, roleDBID, roleName, score, reason)
	
	def scoreTongAddLog( self, roleDBID, roleName, score, reason ):
		"""
		增加帮会竞技积分
		"""
		self.proLog( LT_PRO_SCORE_TONG_SCORE_ADD, roleDBID, roleName, score, reason)
	
	def scoreTongSubLog( self, roleDBID, roleName, score, reason ):
		"""
		减少帮会竞技积分
		"""
		self.proLog( LT_PRO_SCORE_TONG_SCORE_SUB, roleDBID, roleName, score, reason)
	
	def scoreTeamCompetitionAddLog( self, roleDBID, roleName, score, reason ):
		"""
		增加组队竞技积分
		"""
		self.proLog( LT_FUNC_TEAM_COMPETITION_ADD, roleDBID, roleName, score, reason)
	
	def scoreTeamCompetitionSubLog( self, roleDBID, roleName, score, reason ):
		"""
		减少组队竞技积分
		"""
		self.proLog( LT_FUNC_TEAM_COMPETITION_SUB, roleDBID, roleName, score, reason)
		
	
	#-----------------------------------
	# 物品
	#-----------------------------------
	def itemLog( self, action, roleDBID, roleName, grade, reason, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "", param6 = "" ):
		"""
		物品日志
		action:物品的操作,获得,或者失去
		reason:原因
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_ITEM,"||%s||%s||%s||%s||%s||%s||%s||%s||%s||%s||%s",action, roleDBID, roleName, grade, reason, param1, param2, param3, param4,param5, param6 )
	
	def itemAddLog( self, roleDBID, roleName, grade, reason, uid, itemName, itemNum, playerLevel ):
		"""
		添加物品日志
		"""
		self.itemLog( LT_ITEM_ADD, roleDBID, roleName, grade, reason, uid, itemName, itemNum, playerLevel )
	
	def itemDelLog( self, roleDBID, roleName, grade, reason, uid, itemName, itemNum ):
		"""
		删除物品日志
		"""
		self.itemLog( LT_ITEM_DEL, roleDBID, roleName, grade, reason, uid, itemName, itemNum )
	
	def itemSetAmountLog( self, roleDBID, roleName, grade, reason, uid, itemName, itemNum, setNum ):
		"""
		设置物品数量
		itemNum:原物品数量
		setNum:设置物品数量
		"""
		self.itemLog( LT_ITEM_SET_AMOUNT, roleDBID, roleName, grade, reason, uid, itemName, itemNum, setNum )
	
	#-----------------------------------
	# 金钱
	#-----------------------------------
	def moneyLog( self, action, roleDBID, roleName, param1 = "", param2 = "", param3 = "", param4 = "", param5  = "" ):
		"""
		添加金钱日志
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_MONEY,"||%s||%s||%s||%s||%s||%s||%s||%s",action, roleDBID, roleName, param1, param2, param3, param4, param5 )
	
	def moneyChangeLog( self, roleDBID, roleName, oldMoney, nowMoney, reason, grade ):
		"""
		玩家金钱改变
		"""
		self.moneyLog( LT_MONEY_CHANGE, roleDBID, roleName, oldMoney, nowMoney, reason, grade )
		
	#-----------------------------------
	# 银元宝
	#-----------------------------------
	def silverLog( self, action, account, roleDBID, roleName, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "" ):
		"""
		银元宝日志
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_SILVER,"||%s||%s||%s||%s||%s||%s||%s||%s||%s",action, account, roleDBID, roleName, param1, param2, param3, param4, param5 )
	
	def silverChangeLog( self, account, roleDBID, roleName, velue, silver, reason ):
		"""
		添加银元宝
		silver:当前银元宝
		"""
		self.silverLog( LT_SILVER_CHANGE, account, roleDBID, roleName, velue, silver, reason )
	
	#-----------------------------------
	# 金元宝
	#-----------------------------------
	def goldLog( self, action, account, roleDBID, roleName, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "" ):
		"""
		金元宝日志
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_GOLD,"||%s||%s||%s||%s||%s||%s||%s||%s||%s",action, account, roleDBID, roleName, param1, param2, param3, param4, param5 )
	
	def goldChangeLog( self, account, roleDBID, roleName, value, gold, reason ):
		"""
		添加金元宝
		gold：当前金元宝
		"""
		self.goldLog( LT_GOLD_CHANGE, account, roleDBID, roleName, value, gold, reason )
	
	#-----------------------------------
	# 异常
	#-----------------------------------
	def excepLog( self, type, message = "" ):
		"""
		异常信息:  将游戏里的重要调试信息写入数据库。
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_EXCEPT,"||%s||%s", type, message )
	
	def logExceptLog( self, message = "" ):
		"""
		输出日志错误
		"""
		self.excepLog( LT_EXCEPT_LOG, message )
	
	def lotteryExceptLog( self, message = "" ):
		"""
		锦囊错误
		"""
		self.excepLog( LT_EXCEPT_LOTTERY, message )
	
	def itemDropExceptLog( self, message = "" ):
		"""
		物品掉落配置错误
		"""
		self.excepLog( LT_EXCEPT_ITEM_DROP, message )
	
	def itemDropExceptLog( self, message = "" ):
		"""
		物品掉落配置错误
		"""
		self.excepLog( LT_EXCEPT_ITEM_DROP, message )
		
	def chargePresentExceptLog( self, message ):
		self.excepLog( LT_EXCEPT_CHARGE_PRESENT, message )
	
g_logger = MsgLogger.instance()
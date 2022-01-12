# -*- coding: gb18030 -*-
#
# $Id: Love3.py,v 1.103 2008-09-05 03:50:09 zhangyuxing Exp $

"""
个性化脚本。
"""

"""
主版本：一般来说应该是1，指1.0版，由于现在还没正式发布，因此置为0
次(功能)版本：一般是用于有新功能增加的版本
修正版本：主要是指在bug修正的版本
MMdd：发布日期，如0806
"""
import Version

versions = Version.getVersion()		# 主版本.次(功能)版本.修正版本.MMdd

import BigWorld
import CustomDBOperation
import Const
from bwdebug import *
from LoginAttemper import LoginAttemper
from Function import Functor
import OPRecorder
import PLMChatRecorder
import RoleMatchRecorder

g_baseApp = None
g_spawnLoader	= None							# spawnPoint 加载处理
g_antiRobotVerify = None
g_apexProxyMgr = None
g_fishingJoyLoader = None

loginAttemper = LoginAttemper.instance()		# 玩家登录调度

g_tongSignMgr = None

g_tempData = {}

# only useDefaultSpace = true
def onBaseAppReady( isBootStrap ):
	"""
	BaseApp启动完成通报，做Base初始化工作，这里当首个BaseApp启动后加载场景管理器。
		@param isBootStrap:	是否是第一个BaseApp
		@type isBootStrap:	bool
	"""
	global g_baseApp
	global g_spawnLoader
	# 在baseApp成功起来以后创建一个全局的baseapp Entity
	# 被创建的entity会自动注册为global base entity
	g_baseApp = BigWorld.createBaseLocally( "BaseappEntity" )

	g_spawnLoader	= BigWorld.createBaseLocally( "SpawnLoader" )


	#BigWorld.setMtrace()
	global g_apexProxyMgr
	# 创建反外挂系统
	g_apexProxyMgr = BigWorld.createBaseLocally( "ApexProxyMgr" )

	global g_antiRobotVerify
	g_antiRobotVerify = BigWorld.createBaseLocally( "AntiRobotVerify" )

	# 客户端初始化操作记录管理器
	OPRecorder.initialize()

	# 创建玩伴聊天离线消息数据表
	PLMChatRecorder.createOFLMsgTable()

	if isBootStrap:
		optimizeSelect()				#选择优化方式
		#服务器配置管理器
		BigWorld.createBaseLocally( "GameConfigMgr", {} )
		# 创建计划任务系统
		BigWorld.createBaseLocally( "Crond", {} )
		# 创建空间管理器
		BigWorld.createBaseLocally( "SpaceManager", {} )
		# 玩家关系管理器
		BigWorld.createBaseLocally( "RelationMgr", {} )
		# 创建帮会管理器
		BigWorld.createBaseFromDB( "TongManager", "TongManager", onCreateTongManagerBase )
		# 阵营管理器
		BigWorld.createBaseFromDB( "CampMgr", "CampMgr", onCreateCampMgrBase )
		# 创建组队系统
		BigWorld.createBaseLocally( "TeamManager", {} )
		# 创建有生命物品管理器
		BigWorld.createBaseLocally( "LifeItemMgr", {} )
		# 创建邮件系统
		BigWorld.createBaseFromDB( "Postoffice", "Postoffice", onCreatePostoffice )
		# 创建寄卖系统
		BigWorld.createBaseLocally( "CommissionSaleMgr", {} )
		#创建邮件管理系统
		BigWorld.createBaseLocally( "MailManager", {} )

		# 创建镖局信息管理器
		BigWorld.createBaseLocally( "DartManager", {} )

		# 创建怪物活动管理器
		BigWorld.createBaseLocally( "MonsterActivityMgr", {} )

		# 赛马管理器
		BigWorld.createBaseLocally( "RacehorseManager", {} )

		# 跑商管理器
		BigWorld.createBaseLocally( "MerchantMgr", {} )

		# 投机商人管理器
		BigWorld.createBaseLocally( "DarkTraderMgr", {} )

		# 变身大赛管理器
		BigWorld.createBaseLocally( "BCGameMgr", {} )

		# 千年毒蛙管理器
		BigWorld.createBaseLocally( "ToxinFrogMgr", {} )

		# 封印白蛇妖管理器
		BigWorld.createBaseLocally( "SealSnakeMgr", {} )

		# 封印巨灵魔管理器
		BigWorld.createBaseLocally( "SealJuLingMgr", {} )

		# 牛魔王管理器
		BigWorld.createBaseLocally( "BovineDevilMgr", {} )

		# 阻止堕落猎人管理器
		BigWorld.createBaseLocally( "DuoLuoHunterMgr", {} )

		# 破坏疯狂祭师的实验管理器
		BigWorld.createBaseLocally( "CrazyJiShiMgr", {} )

		# 破坏撼地大将的行动管理器
		BigWorld.createBaseLocally( "HanDiDaJiangMgr", {} )

		# 击败啸天大将管理器
		BigWorld.createBaseLocally( "XiaoTianDaJiangMgr", {} )

		# 科举管理器
		BigWorld.createBaseLocally( "ImperialExaminationsMgr", {} )

		# 天关管理器
		BigWorld.createBaseLocally( "TianguanMgr", {} )

		#组队竞赛副本管理器
		BigWorld.createBaseLocally( "TeamCompetitionMgr", {} )

		# 武道大会管理器
		BigWorld.createBaseLocally( "WuDaoMgr", {} )

		# 组队擂台管理器
		BigWorld.createBaseLocally( "TeamChallengeMgr", {} )

		# 天降宝盒活动管理器
		BigWorld.createBaseLocally( "LuckyBoxActivityMgr", {} )

		# 创建知识问答管理器
		BigWorld.createBaseLocally( "QuizGameMgr", {} )

		# 潜能乱斗管理器
		BigWorld.createBaseLocally( "PotentialMeleeMgr", {} )

		# 经验乱斗管理器
		BigWorld.createBaseLocally( "ExpMeleeMgr", {} )

		# 师徒系统远程拜师管理器
		BigWorld.createBaseLocally( "TeachMgr", {} )

		# 水晶管理器
		BigWorld.createBaseLocally( "ShuijingManager", {} )

		# 采集管理器
		BigWorld.createBaseLocally( "CollectPointManager", {} )

		# 系统多倍经验
		BigWorld.createBaseLocally( "SysMultExpMgr", {} )

		# GM行为管理
		BigWorld.createBaseLocally( "GMMgr", {} )

		# 保护帮派活动
		BigWorld.createBaseLocally( "ProtectTong", {} )

		#混沌入侵活动
		BigWorld.createBaseLocally( "HundunMgr", {} )

		#天降奇兽活动
		BigWorld.createBaseLocally( "TianjiangqishouMgr", {} )

		#嘟嘟猪活动
		BigWorld.createBaseLocally( "DuDuZhuMgr", {} )

		#定时日志
		BigWorld.createBaseLocally( "TimeLogerManager", {} )

		# 宠物繁殖
		BigWorld.createBaseLocally( "PetProcreationMgr", {} )

		# 排行榜数据管理器
		BigWorld.createBaseLocally( "GameRankingManager", {} )

		# 游戏公告管理(工具)
		BigWorld.createBaseLocally( "GameBroadcast", {} )

		#替售管理器
		BigWorld.createBaseLocally( "TiShouMgr", {} )

		#拯救猰貐活动
		BigWorld.createBaseLocally( "YayuMgr", {} )

		#点卡寄售管理器
		BigWorld.createBaseLocally( "PointCardMgr", {} )

		#活动公告管理器
		BigWorld.createBaseLocally( "ActivityBroadcastMgr", {} )

		#收购管理器
		BigWorld.createBaseLocally( "CollectionMgr", {} )

		#个人竞技
		BigWorld.createBaseLocally( "RoleCompetitionMgr", {} )

		#帮会竞技
		BigWorld.createBaseLocally( "TongCompetitionMgr", {} )

		# 潜能任务管理器
		BigWorld.createBaseLocally( "PotentialQuestMgr", {} )

		#元宝交易管理器
		BigWorld.createBaseLocally( "YuanBaoTradeMgr", {} )

		#怪物攻城管理器
		BigWorld.createBaseLocally( "MonsterAttackMgr", {} )

		# 防沉迷系统
		BigWorld.createBaseLocally( "AntiWallowBridge", {} )

		# 杂乱无章的游戏行为系统
		BigWorld.createBaseLocally( "MessyMgr", {} )

		# 非诚勿扰活动管理系统
		BigWorld.createBaseLocally( "FeichengwuraoMgr", {} )
		# 七夕情感问答活动管理系统
		BigWorld.createBaseLocally( "TanabataQuizMgr", {} )
		# 七夕魅力果树活动管理系统
		BigWorld.createBaseLocally( "FruitMgr", {} )

		# 一键换装数据管理器 by 姜毅
		BigWorld.createBaseLocally( "OneKeySuitMgr", {} )

		# 环境物件管理
		BigWorld.createBaseLocally( "EnvironmentMgr", {} )

		# 挑战副本管理
		BigWorld.createBaseLocally( "SpaceChallengeMgr", {} )
		
		# 宝藏副本管理
		BigWorld.createBaseLocally( "BaoZangCopyMgr", {} )
		
		# 副本观察者管理器
		BigWorld.createBaseLocally( "SpaceViewerMgr", {} )

		# 副本组队系统排队者管理器
		BigWorld.createBaseLocally( "CopyTeamQueuerMgr", {} )
		
		# 夜战凤栖战场
		BigWorld.createBaseLocally( "YeZhanFengQiMgr", {} )
		
		# 异界战场副本管理
		BigWorld.createBaseLocally( "YiJieZhanChangMgr", {} )
		

		# 天命轮回副本
		BigWorld.createBaseLocally( "SpaceDestinyTransMgr", {} )

		g_fishingJoyLoader.initFishingJoyMgrData()
		# 捕鱼达人全局管理器
		BigWorld.createBaseLocally( "FishingJoyMgr", {} )
		
		#地宫活动
		BigWorld.createBaseLocally( "LiuWangMuMgr", {} )
		
		# 仙魔论战活动
		BigWorld.createBaseLocally( "TaoismAndDemonBattleMgr", {} )
		
		# 鏖战群雄活动
		BigWorld.createBaseFromDB( "AoZhanQunXiongMgr", "AoZhanQunXiongMgr", onCreateAoZhanQunXiongMgrBase )
		
		BigWorld.createBaseFromDB( "DanceMgr", "DanceMgr", onCreateDanceMgrBase )
		
		# 绝地反击活动
		BigWorld.createBaseLocally( "JueDiFanJiMgr", {} )
		
		# 生成镖局声望信息查询表格 DartMessage
		query = """CREATE TABLE IF NOT EXISTS `custom_DartTable` (
				`id` BIGINT NOT NULL auto_increment,
				`sm_playerName` TEXT NOT NULL,
				`sm_dartCreditXinglong` BIGINT NOT NULL default 0,
				`sm_dartCreditChangping` BIGINT NOT NULL default 0,
				`sm_dartNotoriousXinglong` BIGINT NOT NULL default 0,
				`sm_dartNotoriousChangping` BIGINT NOT NULL default 0,
				PRIMARY KEY  ( `id` ),
				KEY `sm_playerName` ( `sm_playerName`( 255 ) )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )

		# 生成活动赠送和充值数据记录表
		query = """CREATE TABLE IF NOT EXISTS `custom_ChargePresentUnite` (
				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_transactionID`  VARCHAR(255),
				`sm_account`		VARCHAR(255),
				`sm_giftPackage`	TEXT,
				`sm_expiredTime`	TEXT,
				`sm_silverCoins`	INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_goldCoins`		INTEGER UNSIGNED NOT NULL DEFAULT 0,
				`sm_chargeType`		TINYINT UNSIGNED,
				`sm_type`			TINYINT UNSIGNED NOT NULL,
				PRIMARY KEY  ( `id` ),
				KEY `account_index` ( `sm_account` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )


		# 生成角色记录表格
		query = """CREATE TABLE IF NOT EXISTS `custom_RoleRecord` (
				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_roleDBID`		BIGINT(20)   UNSIGNED NOT NULL,
				`sm_recordKey` 		TEXT,
				`sm_recordValue` 	TEXT,
				UNIQUE KEY `sm_roleDBID` (`sm_roleDBID`,`sm_recordKey`( 255 )),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )


		# 生成帐号记录表格
		query = """CREATE TABLE IF NOT EXISTS `custom_AccountRecord` (
				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_accountDBID`	BIGINT(20)   UNSIGNED NOT NULL,
				`sm_recordKey` 		TEXT,
				`sm_recordValue` 	TEXT,
				UNIQUE KEY `sm_accountDBID` (`sm_accountDBID`,`sm_recordKey`( 255 )),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )


		# 生成webservice奖品ID列表
		query = """CREATE TABLE IF NOT EXISTS `custom_presents` (
				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`present_id` 		TEXT,
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )

		# 生成矩阵卡密报列表
		query = """CREATE TABLE IF NOT EXISTS `custom_PasswdPro_matrix` (
				`parentDBID`				BIGINT(20)   UNSIGNED,
				`matrix_value` 				VARCHAR(255),
				`passwdPro_state`			INT(8) UNSIGNED,
				PRIMARY KEY  ( `parentDBID` )
				);"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )

		# 生成排名系统数据表
		query = """CREATE TABLE IF NOT EXISTS `custom_Ranking` (
					`id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
					`type` int(8) UNSIGNED NOT NULL,
					`parentID`  bigint(20) UNSIGNED NOT NULL,
					`param1` text,
					`param2` text,
					`param3` text,
					`param4` text,
					`param5` text,
					`param6` text,
					KEY `type` (`type`),
					PRIMARY KEY  ( `id` )
				);"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )


		query = """DROP TABLE IF EXISTS `custom_lastRanking`;"""
		
		BigWorld.executeRawDatabaseCommand( query, createTableCB )
		# 生成排名系统上一次的排名状态记录 由于需要提供上一次的排名信息 所以额外增加一张表，这样比直接在entitiy身上记录
		# 更节约性能
		query = """CREATE TABLE IF NOT EXISTS `custom_oldRanking` (
					`id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
					`type` int(8) UNSIGNED NOT NULL,
					`parentID`  bigint(20) UNSIGNED NOT NULL,
					`param1` text,
					`param2` text,
					`param3` text,
					`param4` text,
					`param5` text,
					`param6` text,
					KEY `type` (`type`),
					PRIMARY KEY  ( `id` )
					);"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )

		# 生成替售行为记录表格
		query = """CREATE TABLE IF NOT EXISTS `custom_TiShouTable` (
				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_roleDBID`		BIGINT(20)   UNSIGNED NOT NULL,
				`sm_npcClassName`	text,
				`sm_tsState` 	BIGINT(20),
				`sm_startTime`		BIGINT(20),
				`sm_roleName`		VARCHAR(255),
				`sm_shopName`	 	text,
				`sm_mapName`	 	text,
				`sm_position`	 	text,
				UNIQUE KEY `sm_roleName`  (`sm_roleName`),
				KEY `sm_roleDBID` (`sm_roleDBID`),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )

		# 生成替售物品表格
		query = """CREATE TABLE IF NOT EXISTS `custom_TiShouItemTable` (
				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_roleDBID`		BIGINT(20)   UNSIGNED NOT NULL,
				`sm_itemUID` 		BIGINT(20),
				`sm_tishouItem` 	blob,
				`sm_price`		 	BIGINT(20),
				`sm_itemType`		BIGINT(20),
				`sm_level`			BIGINT(20),
				`sm_quality`		BIGINT(20),
				`sm_metier`			text,
				`sm_roleName`		text,
				`sm_shopName`	 	text,
				`sm_itemName`	 	text,
				`sm_roleProcess` 	BIGINT(20),
				`sm_delFlag` 		BIGINT(20) NOT NULL default 0,
				`sm_tsState` 		BIGINT(20),
				UNIQUE KEY `sm_itemUID`  (`sm_itemUID`),
				KEY `sm_roleDBID` (`sm_roleDBID`),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )


		# 生成替售宠物表格
		query = """CREATE TABLE IF NOT EXISTS `custom_TiShouPetTable` (
				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_roleDBID`		BIGINT(20)   UNSIGNED NOT NULL,
				`sm_petDBID` 		BIGINT(20),
				`sm_tishouPet` 		blob,
				`sm_price`		 	BIGINT(20),
				`sm_level`		 	BIGINT(20),
				`sm_era`		 	BIGINT(20),
				`sm_gender`		 	BIGINT(20),
				`sm_metier`		 	BIGINT(20),
				`sm_breed`		 	BIGINT(20),
				`sm_roleName`		VARCHAR(255),
				`sm_shopName`	 	text,
				`sm_roleProcess` 	BIGINT(20),
				`sm_delFlag` 		BIGINT(20) NOT NULL default 0,
				`sm_tsState` 		BIGINT(20),
				UNIQUE KEY `sm_petDBID`  (`sm_petDBID`),
				KEY `sm_roleDBID` (`sm_roleDBID`),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )


		# 生成替售交易记录表格
		query = """CREATE TABLE IF NOT EXISTS `custom_TiShouRecordTable` (
				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_roleName`		VARCHAR(255),
				`sm_roleDBID`		BIGINT(20)   UNSIGNED NOT NULL,
				`sm_tishouMoney` 	BIGINT(20),
				UNIQUE KEY `sm_roleDBID`  (`sm_roleDBID`),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )


		# 生成帮会会标表格	by 姜毅
		query = """CREATE TABLE IF NOT EXISTS `custom_TongSignTable` (
				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_TongDBID`		BIGINT(20),
				`sm_TongName` 		text,
				`sm_Icon` 			text,
				`sm_IconMD5` 		text,
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTongSignTableCB )

		# 创建游戏公告的数据库表
		query = """CREATE TABLE IF NOT EXISTS `custom_GameBroadcast` (
				  `id` bigint(20) NOT NULL AUTO_INCREMENT,
				  `operationstart` datetime default NULL,
				  `distance` int(11) default 0,
				  `operationend` datetime default NULL,
				  `actiontype` smallint(6) default 0,
				  `content` varchar(200) default NULL,
				  `status` smallint(6) default 0,
				  `mark` smallint(6) default 0,
				  PRIMARY KEY  (`id`)
					);"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )

		query = """CREATE TABLE IF NOT EXISTS `custom_AccountData` (
				  `parentID` bigint(20) unsigned NOT NULL,
				  `key` varchar(255) DEFAULT NULL,
				  `value` varchar(255) DEFAULT NULL,
				  KEY `key_index` (`parentID`)
					);"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )

		query = """CREATE TABLE IF NOT EXISTS `custom_ItemAwards` (
					`id` bigint(20) NOT NULL AUTO_INCREMENT,
					`account` varchar(255) DEFAULT NULL,
					`playerName` varchar(255) DEFAULT NULL,
					`orderform` varchar(255) DEFAULT NULL,
					`transactionID` varchar(255) DEFAULT NULL,
					`itemId` varchar(255) DEFAULT NULL,
					`amount`  int unsigned DEFAULT 0,
					`endTime` int unsigned DEFAULT 0,
					`remark` varchar(255) DEFAULT NULL,
					PRIMARY KEY  (`id`),
					KEY `order_index` (`account`,`orderform`),
					KEY `itemId_index` (`account`,`itemId`),
					KEY `transactionID` (`transactionID`)
					);"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )

		query = """CREATE TABLE IF NOT EXISTS `custom_oneKeySuit` (
					`id` bigint(20) NOT NULL AUTO_INCREMENT,
					`sm_roleDBID` bigint(20) unsigned NOT NULL,
					`sm_suitOrder` int unsigned DEFAULT 0,
					`sm_suitName` varchar(255) DEFAULT NULL,
					`sm_head` bigint(20) unsigned DEFAULT 0,
					`sm_neck` bigint(20) unsigned DEFAULT 0,
					`sm_body` bigint(20) unsigned DEFAULT 0,
					`sm_breach` bigint(20) unsigned DEFAULT 0,
					`sm_vola` bigint(20) unsigned DEFAULT 0,
					`sm_haunch` bigint(20) unsigned DEFAULT 0,
					`sm_cuff` bigint(20) unsigned DEFAULT 0,
					`sm_lefthand` bigint(20) unsigned DEFAULT 0,
					`sm_righthand` bigint(20) unsigned DEFAULT 0,
					`sm_feet` bigint(20) unsigned DEFAULT 0,
					`sm_leftfinger` bigint(20) unsigned DEFAULT 0,
					`sm_rightfinger` bigint(20) unsigned DEFAULT 0,
					`sm_talisman` bigint(20) unsigned DEFAULT 0,
					PRIMARY KEY  (`id`)
					) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )
	
		# 生成因服务器宕机引起的背包、仓库拥有相同uid的物品的记录表格
		query = """CREATE TABLE IF NOT EXISTS `custom_sameUIDItemTable` (
				`id`			BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_roleDBID` 		BIGINT(20),
				`sm_itemUID` 		BIGINT(20),
				`sm_recordTime`		BIGINT(20),
				`sm_Item` 	        blob,
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )


		# 生成玩家比赛日志记录表
		RoleMatchRecorder.createTable()

		CustomDBOperation.g_proceduremanager.updateProcedures()		# 刷新存储过程
		#CustomDBOperation.g_indexmanager.updateIndex()			# 创建索引  目前没有需要创建的索引 暂时屏蔽掉

		# 登录调度系统，最大允许的登录人数
		BigWorld.globalData["loginAttemper_count_limit"] = Const.LOGIN_ACCOUNT_LIMIT
		BigWorld.globalData["baseApp_player_count_limit"] = Const.BASEAPP_PLAYER_COUNT_LIMIT
		BigWorld.globalData["login_waitQueue_limit"] = Const.LOGIN_ATTEMPER_WAIT_LIMIT

		BigWorld.globalData["AntiRobotVerify_rate"] = Const.ANTI_ROBOT_RATE	# 每一次与怪物战斗触发反外挂验证的概率
		

		

	loginAttemper.onBaseAppReady()

	print "BaseApp is Ready"

def onBaseAppShuttingDown( shutdownTime ):	# wsf add,16:30 2008-8-15
	"""
	see also python_baseapp.chm BWPersonality Module Reference
	"""
	INFO_MSG( "BaseApp shutdownTime-->>>( %.2f )" % shutdownTime )
	global g_apexProxyMgr
	g_apexProxyMgr.onGetApexProxy().stopApexProxy()

def onBaseAppShutDown( stage ):
	"""
	see also python_baseapp.chm BWPersonality Module Reference
	"""
	INFO_MSG( "stage-->>>( %i )" % stage )
	global g_baseApp
	#if stage == 0:					# 0 - Before disconnecting clients
	#if stage == 1:					# 1 - Before writing entities to the database
	if stage == 2 and g_baseApp:	# 2 - After writing entities to the database
		# 在shutdown状态为“写entity结束”的时候取消注册
		INFO_MSG( "BaseApp shutdown now, it will unregister from globalBases, name = %s" % g_baseApp.globalName )
		g_baseApp.deregisterGlobally( g_baseApp.globalName )
		g_baseApp.destroy()
		g_baseApp = None


def onCreateTongManagerBase( baseRef, databaseID, wasActive ):
	"""
	createBaseFromDB回调 创建帮会管理器
	"""
	if baseRef == None:
		DEBUG_MSG(  "Create TongManager base." )
		csTongManager = BigWorld.createBaseLocally( "TongManager", {} )
		#csTongManager.writeToDB( csTongManager.onCreatedTongManager ) 模块内部有做处理

def onCreateCampMgrBase( baseRef, databaseID, wasActive ):
	"""
	createBaseFromDB回调 创建阵营管理器
	"""
	if baseRef == None:
		DEBUG_MSG(  "Create CampMgr base." )
		BigWorld.createBaseLocally( "CampMgr", {} )

def onCreateAoZhanQunXiongMgrBase( baseRef, databaseID, wasActive ):
	"""
	createBaseFromDB回调 创建鏖战群雄管理器
	"""
	if baseRef == None:
		DEBUG_MSG(  "Create AoZhanQunXiongMgr base." )
		BigWorld.createBaseLocally( "AoZhanQunXiongMgr", {} )
		
def onCreateDanceMgrBase( baseRef, databaseID, wasActive ):
	"""
	createBaseFromDB回调 创建舞厅管理器
	"""
	if baseRef == None:
		DEBUG_MSG(  "Create DanceMgr base." )
		BigWorld.createBaseLocally( "DanceMgr", {} )	

def onCreatePostoffice( baseRef, databaseID, wasActive ):
	"""
	createBaseFromDB回调 创建军团集合实体
	"""
	if baseRef == None:
		spaceBase = BigWorld.createBaseLocally( "Postoffice", {} )

def createTableCB( result, rows, errstr ):
	"""
	生成数据库表格回调函数

	param tableName:	生成的表格名字
	type tableName:		STRING
	"""
	if errstr:
		# 生成表格错误的处理
		ERROR_MSG( "Create table fault! %s" % errstr  )
		return


def createTongSignTableCB( result, rows, errstr ):
	"""
	生成会标数据库表格回调函数 by 姜毅

	param tableName:	生成的表格名字
	type tableName:		STRING
	"""
	global g_tongSignMgr
	if errstr:
		# 生成表格错误的处理
		ERROR_MSG( "Create table fault! %s" % errstr  )
		return
	DEBUG_MSG( "create tong sign table success." )
	# 帮会会标 by 姜毅
	from TongSignMgr import TongSignMgr
	g_tongSignMgr = TongSignMgr.instance()
	# 初始化图标数据
	g_tongSignMgr.userTongSignDatas()
	g_tongSignMgr.tongSignDatas()

def setAntiIndulgence( open ):
	"""
	开启/关闭防沉迷系统
	"""
	BigWorld.globalData["AntiIndulgenceOpen"] = open

# init when compile

# hyw
from LevelEXP import RoleLevelEXP
RoleLevelEXP.initialize()
from LevelEXP import PetLevelEXP
PetLevelEXP.initialize()
from LevelEXP import TongLevelEXP
TongLevelEXP.initialize()

from PetFormulas import formulas as g_petFormulas
g_petFormulas.initialize()

from ObjectScripts.GameObjectFactory import g_objFactory
g_objFactory.load( "config/server/gameObject/objPath.xml" )

from NPCExpLoader import NPCExpLoader								# 怪物经验加载器
g_npcExp = NPCExpLoader.instance()

from NPCBaseAttrLoader import NPCBaseAttrLoader					# 怪物四项基础属性加载器
g_npcBaseAttr = NPCBaseAttrLoader.instance()

import items
g_items = items.instance()

import CooldownFlyweight
g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()
g_cooldowns.load( "config/skill/CooldownType.xml" )

import SkillLoader		#加载技能的buff保存相关数据
g_skills = SkillLoader.instance()

import TongBuildingData
tongBuildingDatas = TongBuildingData.instance()

import TongSkillResearchData
tongSkillResearchData = TongSkillResearchData.instance()

import TongItemResearchData
tongItemResearchData = TongItemResearchData.instance()

from TongDatas import tongItem_instance
g_tongItems = tongItem_instance()

from TongDatas import tongSkill_instance
g_tongSkills = tongSkill_instance()

from TongSpecialItemsData import tongSpeItem_instance
g_tongSpecItems = tongSpeItem_instance()

from CrondDatas import CrondDatas
g_crondDatas = CrondDatas.instance()
g_crondDatas.load( "config/server/CrondDatas.xml" )

from DarkTraderDatas import DarkTraderDatas
g_DarkTraderDatas = DarkTraderDatas.instance()							# 投机商人可能刷出的位置坐标

from ChatProfanity import chatProfanity as g_chatProfanity				# 聊天敏感词汇及处理
g_chatProfanity.initialize()

import ShuijingManager								#水晶副本处理加载
import CollectPointManager							# 采集活动处理加载

from QuizGameLoader import quizGameLoader			# 加载知识问答配置
quizGameLoader.load()

from SpecialShopMgr import specialShop
specialShop.load( "config/server/SpecialShop.xml" )

# 积分兑换道法数据
from ZDDataLoader import g_daofaShop
g_daofaShop.load( "config/ZhengDao/ZDScoreShop.xml" )

# 骑宠配置
from VehicleDataLoader import VehicleDataLoader
g_vehicleData = VehicleDataLoader.instance()


# 骑宠数据
from LevelEXP import VehicleLevelExp
g_vehicleExp = VehicleLevelExp.instance()

# 副本组队系统资源加载
from BaseSpaceCopyFormulas import spaceCopyFormulas
spaceCopyFormulas.loadCopiesData( "config/matchablecopies.xml" )

# 捕鱼达人配置
from fishingJoy.FishingJoyDataLoader import FishingJoyDataLoader
g_fishingJoyLoader = FishingJoyDataLoader()
g_fishingJoyLoader.initFishingJoyCommonData()

from RoleCreateEquipsLoader import equipsLoader
equipsLoader.loadEquipDatas( "config/server/RoleCreateEquips.xml" )

def optimizeSelect( ):
	import ResMgr
	BigWorld.globalData["optimizeWithCPP"] = False
	BigWorld.globalData["optimizeWithAI_ShortProcess"] = False

	sect = ResMgr.openSection( "server/bw.xml" )
	if sect.has_key("optimizeWithCPP"):
		BigWorld.globalData["optimizeWithCPP"] = sect["optimizeWithCPP"].asBool
	if sect.has_key("optimizeWithAI_ShortProcess"):
		BigWorld.globalData["optimizeWithAI_ShortProcess"] = sect["optimizeWithAI_ShortProcess"].asBool



# Love3.py

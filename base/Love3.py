# -*- coding: gb18030 -*-
#
# $Id: Love3.py,v 1.103 2008-09-05 03:50:09 zhangyuxing Exp $

"""
���Ի��ű���
"""

"""
���汾��һ����˵Ӧ����1��ָ1.0�棬�������ڻ�û��ʽ�����������Ϊ0
��(����)�汾��һ�����������¹������ӵİ汾
�����汾����Ҫ��ָ��bug�����İ汾
MMdd���������ڣ���0806
"""
import Version

versions = Version.getVersion()		# ���汾.��(����)�汾.�����汾.MMdd

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
g_spawnLoader	= None							# spawnPoint ���ش���
g_antiRobotVerify = None
g_apexProxyMgr = None
g_fishingJoyLoader = None

loginAttemper = LoginAttemper.instance()		# ��ҵ�¼����

g_tongSignMgr = None

g_tempData = {}

# only useDefaultSpace = true
def onBaseAppReady( isBootStrap ):
	"""
	BaseApp�������ͨ������Base��ʼ�����������ﵱ�׸�BaseApp��������س�����������
		@param isBootStrap:	�Ƿ��ǵ�һ��BaseApp
		@type isBootStrap:	bool
	"""
	global g_baseApp
	global g_spawnLoader
	# ��baseApp�ɹ������Ժ󴴽�һ��ȫ�ֵ�baseapp Entity
	# ��������entity���Զ�ע��Ϊglobal base entity
	g_baseApp = BigWorld.createBaseLocally( "BaseappEntity" )

	g_spawnLoader	= BigWorld.createBaseLocally( "SpawnLoader" )


	#BigWorld.setMtrace()
	global g_apexProxyMgr
	# ���������ϵͳ
	g_apexProxyMgr = BigWorld.createBaseLocally( "ApexProxyMgr" )

	global g_antiRobotVerify
	g_antiRobotVerify = BigWorld.createBaseLocally( "AntiRobotVerify" )

	# �ͻ��˳�ʼ��������¼������
	OPRecorder.initialize()

	# �����������������Ϣ���ݱ�
	PLMChatRecorder.createOFLMsgTable()

	if isBootStrap:
		optimizeSelect()				#ѡ���Ż���ʽ
		#���������ù�����
		BigWorld.createBaseLocally( "GameConfigMgr", {} )
		# �����ƻ�����ϵͳ
		BigWorld.createBaseLocally( "Crond", {} )
		# �����ռ������
		BigWorld.createBaseLocally( "SpaceManager", {} )
		# ��ҹ�ϵ������
		BigWorld.createBaseLocally( "RelationMgr", {} )
		# ������������
		BigWorld.createBaseFromDB( "TongManager", "TongManager", onCreateTongManagerBase )
		# ��Ӫ������
		BigWorld.createBaseFromDB( "CampMgr", "CampMgr", onCreateCampMgrBase )
		# �������ϵͳ
		BigWorld.createBaseLocally( "TeamManager", {} )
		# ������������Ʒ������
		BigWorld.createBaseLocally( "LifeItemMgr", {} )
		# �����ʼ�ϵͳ
		BigWorld.createBaseFromDB( "Postoffice", "Postoffice", onCreatePostoffice )
		# ��������ϵͳ
		BigWorld.createBaseLocally( "CommissionSaleMgr", {} )
		#�����ʼ�����ϵͳ
		BigWorld.createBaseLocally( "MailManager", {} )

		# �����ھ���Ϣ������
		BigWorld.createBaseLocally( "DartManager", {} )

		# ��������������
		BigWorld.createBaseLocally( "MonsterActivityMgr", {} )

		# ���������
		BigWorld.createBaseLocally( "RacehorseManager", {} )

		# ���̹�����
		BigWorld.createBaseLocally( "MerchantMgr", {} )

		# Ͷ�����˹�����
		BigWorld.createBaseLocally( "DarkTraderMgr", {} )

		# �������������
		BigWorld.createBaseLocally( "BCGameMgr", {} )

		# ǧ�궾�ܹ�����
		BigWorld.createBaseLocally( "ToxinFrogMgr", {} )

		# ��ӡ������������
		BigWorld.createBaseLocally( "SealSnakeMgr", {} )

		# ��ӡ����ħ������
		BigWorld.createBaseLocally( "SealJuLingMgr", {} )

		# ţħ��������
		BigWorld.createBaseLocally( "BovineDevilMgr", {} )

		# ��ֹ�������˹�����
		BigWorld.createBaseLocally( "DuoLuoHunterMgr", {} )

		# �ƻ�����ʦ��ʵ�������
		BigWorld.createBaseLocally( "CrazyJiShiMgr", {} )

		# �ƻ����ش󽫵��ж�������
		BigWorld.createBaseLocally( "HanDiDaJiangMgr", {} )

		# ����Х��󽫹�����
		BigWorld.createBaseLocally( "XiaoTianDaJiangMgr", {} )

		# �ƾٹ�����
		BigWorld.createBaseLocally( "ImperialExaminationsMgr", {} )

		# ��ع�����
		BigWorld.createBaseLocally( "TianguanMgr", {} )

		#��Ӿ�������������
		BigWorld.createBaseLocally( "TeamCompetitionMgr", {} )

		# �����������
		BigWorld.createBaseLocally( "WuDaoMgr", {} )

		# �����̨������
		BigWorld.createBaseLocally( "TeamChallengeMgr", {} )

		# �콵���л������
		BigWorld.createBaseLocally( "LuckyBoxActivityMgr", {} )

		# ����֪ʶ�ʴ������
		BigWorld.createBaseLocally( "QuizGameMgr", {} )

		# Ǳ���Ҷ�������
		BigWorld.createBaseLocally( "PotentialMeleeMgr", {} )

		# �����Ҷ�������
		BigWorld.createBaseLocally( "ExpMeleeMgr", {} )

		# ʦͽϵͳԶ�̰�ʦ������
		BigWorld.createBaseLocally( "TeachMgr", {} )

		# ˮ��������
		BigWorld.createBaseLocally( "ShuijingManager", {} )

		# �ɼ�������
		BigWorld.createBaseLocally( "CollectPointManager", {} )

		# ϵͳ�౶����
		BigWorld.createBaseLocally( "SysMultExpMgr", {} )

		# GM��Ϊ����
		BigWorld.createBaseLocally( "GMMgr", {} )

		# �������ɻ
		BigWorld.createBaseLocally( "ProtectTong", {} )

		#�������ֻ
		BigWorld.createBaseLocally( "HundunMgr", {} )

		#�콵���޻
		BigWorld.createBaseLocally( "TianjiangqishouMgr", {} )

		#����
		BigWorld.createBaseLocally( "DuDuZhuMgr", {} )

		#��ʱ��־
		BigWorld.createBaseLocally( "TimeLogerManager", {} )

		# ���ﷱֳ
		BigWorld.createBaseLocally( "PetProcreationMgr", {} )

		# ���а����ݹ�����
		BigWorld.createBaseLocally( "GameRankingManager", {} )

		# ��Ϸ�������(����)
		BigWorld.createBaseLocally( "GameBroadcast", {} )

		#���۹�����
		BigWorld.createBaseLocally( "TiShouMgr", {} )

		#���Ȫm؅�
		BigWorld.createBaseLocally( "YayuMgr", {} )

		#�㿨���۹�����
		BigWorld.createBaseLocally( "PointCardMgr", {} )

		#����������
		BigWorld.createBaseLocally( "ActivityBroadcastMgr", {} )

		#�չ�������
		BigWorld.createBaseLocally( "CollectionMgr", {} )

		#���˾���
		BigWorld.createBaseLocally( "RoleCompetitionMgr", {} )

		#��Ὰ��
		BigWorld.createBaseLocally( "TongCompetitionMgr", {} )

		# Ǳ�����������
		BigWorld.createBaseLocally( "PotentialQuestMgr", {} )

		#Ԫ�����׹�����
		BigWorld.createBaseLocally( "YuanBaoTradeMgr", {} )

		#���﹥�ǹ�����
		BigWorld.createBaseLocally( "MonsterAttackMgr", {} )

		# ������ϵͳ
		BigWorld.createBaseLocally( "AntiWallowBridge", {} )

		# �������µ���Ϸ��Ϊϵͳ
		BigWorld.createBaseLocally( "MessyMgr", {} )

		# �ǳ����Ż����ϵͳ
		BigWorld.createBaseLocally( "FeichengwuraoMgr", {} )
		# ��Ϧ����ʴ�����ϵͳ
		BigWorld.createBaseLocally( "TanabataQuizMgr", {} )
		# ��Ϧ�������������ϵͳ
		BigWorld.createBaseLocally( "FruitMgr", {} )

		# һ����װ���ݹ����� by ����
		BigWorld.createBaseLocally( "OneKeySuitMgr", {} )

		# �����������
		BigWorld.createBaseLocally( "EnvironmentMgr", {} )

		# ��ս��������
		BigWorld.createBaseLocally( "SpaceChallengeMgr", {} )
		
		# ���ظ�������
		BigWorld.createBaseLocally( "BaoZangCopyMgr", {} )
		
		# �����۲��߹�����
		BigWorld.createBaseLocally( "SpaceViewerMgr", {} )

		# �������ϵͳ�Ŷ��߹�����
		BigWorld.createBaseLocally( "CopyTeamQueuerMgr", {} )
		
		# ҹս����ս��
		BigWorld.createBaseLocally( "YeZhanFengQiMgr", {} )
		
		# ���ս����������
		BigWorld.createBaseLocally( "YiJieZhanChangMgr", {} )
		

		# �����ֻظ���
		BigWorld.createBaseLocally( "SpaceDestinyTransMgr", {} )

		g_fishingJoyLoader.initFishingJoyMgrData()
		# �������ȫ�ֹ�����
		BigWorld.createBaseLocally( "FishingJoyMgr", {} )
		
		#�ع��
		BigWorld.createBaseLocally( "LiuWangMuMgr", {} )
		
		# ��ħ��ս�
		BigWorld.createBaseLocally( "TaoismAndDemonBattleMgr", {} )
		
		# ��սȺ�ۻ
		BigWorld.createBaseFromDB( "AoZhanQunXiongMgr", "AoZhanQunXiongMgr", onCreateAoZhanQunXiongMgrBase )
		
		BigWorld.createBaseFromDB( "DanceMgr", "DanceMgr", onCreateDanceMgrBase )
		
		# ���ط����
		BigWorld.createBaseLocally( "JueDiFanJiMgr", {} )
		
		# �����ھ�������Ϣ��ѯ��� DartMessage
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

		# ���ɻ���ͺͳ�ֵ���ݼ�¼��
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


		# ���ɽ�ɫ��¼���
		query = """CREATE TABLE IF NOT EXISTS `custom_RoleRecord` (
				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_roleDBID`		BIGINT(20)   UNSIGNED NOT NULL,
				`sm_recordKey` 		TEXT,
				`sm_recordValue` 	TEXT,
				UNIQUE KEY `sm_roleDBID` (`sm_roleDBID`,`sm_recordKey`( 255 )),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )


		# �����ʺż�¼���
		query = """CREATE TABLE IF NOT EXISTS `custom_AccountRecord` (
				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_accountDBID`	BIGINT(20)   UNSIGNED NOT NULL,
				`sm_recordKey` 		TEXT,
				`sm_recordValue` 	TEXT,
				UNIQUE KEY `sm_accountDBID` (`sm_accountDBID`,`sm_recordKey`( 255 )),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )


		# ����webservice��ƷID�б�
		query = """CREATE TABLE IF NOT EXISTS `custom_presents` (
				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`present_id` 		TEXT,
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )

		# ���ɾ����ܱ��б�
		query = """CREATE TABLE IF NOT EXISTS `custom_PasswdPro_matrix` (
				`parentDBID`				BIGINT(20)   UNSIGNED,
				`matrix_value` 				VARCHAR(255),
				`passwdPro_state`			INT(8) UNSIGNED,
				PRIMARY KEY  ( `parentDBID` )
				);"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )

		# ��������ϵͳ���ݱ�
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
		# ��������ϵͳ��һ�ε�����״̬��¼ ������Ҫ�ṩ��һ�ε�������Ϣ ���Զ�������һ�ű�������ֱ����entitiy���ϼ�¼
		# ����Լ����
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

		# ����������Ϊ��¼���
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

		# ����������Ʒ���
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


		# �������۳�����
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


		# �������۽��׼�¼���
		query = """CREATE TABLE IF NOT EXISTS `custom_TiShouRecordTable` (
				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_roleName`		VARCHAR(255),
				`sm_roleDBID`		BIGINT(20)   UNSIGNED NOT NULL,
				`sm_tishouMoney` 	BIGINT(20),
				UNIQUE KEY `sm_roleDBID`  (`sm_roleDBID`),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )


		# ���ɰ������	by ����
		query = """CREATE TABLE IF NOT EXISTS `custom_TongSignTable` (
				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_TongDBID`		BIGINT(20),
				`sm_TongName` 		text,
				`sm_Icon` 			text,
				`sm_IconMD5` 		text,
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTongSignTableCB )

		# ������Ϸ��������ݿ��
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
	
		# �����������崻�����ı������ֿ�ӵ����ͬuid����Ʒ�ļ�¼���
		query = """CREATE TABLE IF NOT EXISTS `custom_sameUIDItemTable` (
				`id`			BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_roleDBID` 		BIGINT(20),
				`sm_itemUID` 		BIGINT(20),
				`sm_recordTime`		BIGINT(20),
				`sm_Item` 	        blob,
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, createTableCB )


		# ������ұ�����־��¼��
		RoleMatchRecorder.createTable()

		CustomDBOperation.g_proceduremanager.updateProcedures()		# ˢ�´洢����
		#CustomDBOperation.g_indexmanager.updateIndex()			# ��������  Ŀǰû����Ҫ���������� ��ʱ���ε�

		# ��¼����ϵͳ���������ĵ�¼����
		BigWorld.globalData["loginAttemper_count_limit"] = Const.LOGIN_ACCOUNT_LIMIT
		BigWorld.globalData["baseApp_player_count_limit"] = Const.BASEAPP_PLAYER_COUNT_LIMIT
		BigWorld.globalData["login_waitQueue_limit"] = Const.LOGIN_ATTEMPER_WAIT_LIMIT

		BigWorld.globalData["AntiRobotVerify_rate"] = Const.ANTI_ROBOT_RATE	# ÿһ�������ս�������������֤�ĸ���
		

		

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
		# ��shutdown״̬Ϊ��дentity��������ʱ��ȡ��ע��
		INFO_MSG( "BaseApp shutdown now, it will unregister from globalBases, name = %s" % g_baseApp.globalName )
		g_baseApp.deregisterGlobally( g_baseApp.globalName )
		g_baseApp.destroy()
		g_baseApp = None


def onCreateTongManagerBase( baseRef, databaseID, wasActive ):
	"""
	createBaseFromDB�ص� ������������
	"""
	if baseRef == None:
		DEBUG_MSG(  "Create TongManager base." )
		csTongManager = BigWorld.createBaseLocally( "TongManager", {} )
		#csTongManager.writeToDB( csTongManager.onCreatedTongManager ) ģ���ڲ���������

def onCreateCampMgrBase( baseRef, databaseID, wasActive ):
	"""
	createBaseFromDB�ص� ������Ӫ������
	"""
	if baseRef == None:
		DEBUG_MSG(  "Create CampMgr base." )
		BigWorld.createBaseLocally( "CampMgr", {} )

def onCreateAoZhanQunXiongMgrBase( baseRef, databaseID, wasActive ):
	"""
	createBaseFromDB�ص� ������սȺ�۹�����
	"""
	if baseRef == None:
		DEBUG_MSG(  "Create AoZhanQunXiongMgr base." )
		BigWorld.createBaseLocally( "AoZhanQunXiongMgr", {} )
		
def onCreateDanceMgrBase( baseRef, databaseID, wasActive ):
	"""
	createBaseFromDB�ص� ��������������
	"""
	if baseRef == None:
		DEBUG_MSG(  "Create DanceMgr base." )
		BigWorld.createBaseLocally( "DanceMgr", {} )	

def onCreatePostoffice( baseRef, databaseID, wasActive ):
	"""
	createBaseFromDB�ص� �������ż���ʵ��
	"""
	if baseRef == None:
		spaceBase = BigWorld.createBaseLocally( "Postoffice", {} )

def createTableCB( result, rows, errstr ):
	"""
	�������ݿ���ص�����

	param tableName:	���ɵı������
	type tableName:		STRING
	"""
	if errstr:
		# ���ɱ�����Ĵ���
		ERROR_MSG( "Create table fault! %s" % errstr  )
		return


def createTongSignTableCB( result, rows, errstr ):
	"""
	���ɻ�����ݿ���ص����� by ����

	param tableName:	���ɵı������
	type tableName:		STRING
	"""
	global g_tongSignMgr
	if errstr:
		# ���ɱ�����Ĵ���
		ERROR_MSG( "Create table fault! %s" % errstr  )
		return
	DEBUG_MSG( "create tong sign table success." )
	# ����� by ����
	from TongSignMgr import TongSignMgr
	g_tongSignMgr = TongSignMgr.instance()
	# ��ʼ��ͼ������
	g_tongSignMgr.userTongSignDatas()
	g_tongSignMgr.tongSignDatas()

def setAntiIndulgence( open ):
	"""
	����/�رշ�����ϵͳ
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

from NPCExpLoader import NPCExpLoader								# ���ﾭ�������
g_npcExp = NPCExpLoader.instance()

from NPCBaseAttrLoader import NPCBaseAttrLoader					# ��������������Լ�����
g_npcBaseAttr = NPCBaseAttrLoader.instance()

import items
g_items = items.instance()

import CooldownFlyweight
g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()
g_cooldowns.load( "config/skill/CooldownType.xml" )

import SkillLoader		#���ؼ��ܵ�buff�����������
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
g_DarkTraderDatas = DarkTraderDatas.instance()							# Ͷ�����˿���ˢ����λ������

from ChatProfanity import chatProfanity as g_chatProfanity				# �������дʻ㼰����
g_chatProfanity.initialize()

import ShuijingManager								#ˮ�������������
import CollectPointManager							# �ɼ���������

from QuizGameLoader import quizGameLoader			# ����֪ʶ�ʴ�����
quizGameLoader.load()

from SpecialShopMgr import specialShop
specialShop.load( "config/server/SpecialShop.xml" )

# ���ֶһ���������
from ZDDataLoader import g_daofaShop
g_daofaShop.load( "config/ZhengDao/ZDScoreShop.xml" )

# �������
from VehicleDataLoader import VehicleDataLoader
g_vehicleData = VehicleDataLoader.instance()


# �������
from LevelEXP import VehicleLevelExp
g_vehicleExp = VehicleLevelExp.instance()

# �������ϵͳ��Դ����
from BaseSpaceCopyFormulas import spaceCopyFormulas
spaceCopyFormulas.loadCopiesData( "config/matchablecopies.xml" )

# �����������
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

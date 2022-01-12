# -*- coding: gb18030 -*-
#


import BigWorld
from bwdebug import *
import csdefine
import cschannel_msgs
import Love3
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
import time
import csconst


ACTIVITY_LOG_CMD = "55 23 * * *"

MID_AUTUMN_TONG_SPAWNS = []



class ActivityBroadcastMgr( BigWorld.Base ):

	def __init__(self):
		"""
		���ֻ�Ĺ��漰ˢ�ֹ�����
		"""
		BigWorld.Base.__init__( self )
		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "ActivityBroadcastMgr", self._onRegisterManager )
		
		self.spawnPointDatas = {}		# ��¼�key��Ӧˢ�µ�����
		self.startedActivityKeys = []		# ��¼�Ѿ������Ļ��key

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register ActivityBroadcastMgr Fail!" )
			# again
			self.registerGlobally( "ActivityBroadcastMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["ActivityBroadcastMgr"] = self							# ע�ᵽ���еķ�������
			INFO_MSG("ActivityBroadcastMgr Create Complete!")
			self.registerCrond()



	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"shengui_notice" 	: "onShenguiNotice",
					  	"wuyao_notice" 		: "onWuyaoNotice",
						"shiluo_notice" 	: "onShiluoNotice",
						"cms_notice_01" 	: "onCMSNotice01",
						"cms_notice_02" 	: "onCMSNotice02",
						"cms_notice_03"	: "onCMSNotice03",
						"chunjie_notice_01"	: "onChunjieNotice01",
						"chunjie_notice_02"	: "onChunjieNotice02",
						"chunjie_notice_03"	: "onChunjieNotice03",
						"chunjie_notice_04"	: "onChunjieNotice04",
						"chunjie_notice_05"	: "onChunjieNotice05",
						"chunjie_notice_06"	: "onChunjieNotice06",
						"tanabata_notice:"	: "onTanabataNotice",
						"tanabata_quiz_notice" : "onTanabataQuizNotice",
						"tanabata_fcwr_notice" : "onTanabataFcwrNotice",
						"tanabata_mlzz_notice" : "onTanabataMlzzNotice",
						"tanabata_yhxc_notice" : "onTanabataYhxcNotice",
						"tanabata_love_notice" : "onTanabataLoveNotice",
						"midAutumn_notice" : "onMidAutumnNotice",
						"midAutumn_rabbitRun_notice" : "onMidAutumnRabbitRunNotice",
						"midAutumn_rabbitRun_start" : "onMidAutumnRabbitRunStart",
						"midAutumn_rabbitRun_end" : "onMidAutumnRabbitRunEnd",
						"midAutumn_jhwsx_notice" : "onMidAutumnTongQuestNotice",
						"midAutumn_qlgcj_notice" : "onMidAutumnWordFindNotice",
						"midAutumn_ybdld_notice" : "onMidAutumnTongProtectNotice",
						"midAutumn_csznl_notice" : "onMidAutumnZhouNianGiftNotice",
						"midAutumn_zqlb_notice" : "onMidAutumnWordMakeNotice",
						"midAutumn_boss_notice" : "onMidAutumnKillMoonCakeNotice",
						"midAutumn_quest_start" : "onTongAutummQuestStart",
						"midAutumn_quest_end" : "onTongAutummQuestEnd",
						"midAutumn_monster_start" : "onTongAutummMonsterStart",
						"midAutumn_monster_end" : "onTongAutummMonsterEnd",
						"newYear_rabbitRun_notice" : "onNewYearRabbitRunNotice",
						"xmanStart" : "xmanStartCB",
						"xmanEnd" : "xmanEndCB",
						"minAutStart" : "minAutStartCB",
						"minAutEnd" : "minAutEndCB",
						"tongCityWarStart" : "tongCityWarStartCB",
						"tongCityWarEnd" : "tongCityWarEndCB",
						"yearMonsterStart" : "yearMonsterStartCB",
						"yearMonsterEnd" : "yearMonsterEndCB",
					  }
		
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )

		#����һЩ���־��ض�ʱ��¼��Ϣ
		crond.addScheme( ACTIVITY_LOG_CMD, self, "onActivityLogHandle" )


		crond.addAutoStartScheme( "midAutumn_quest_start", self, "onTongAutummQuestStart" )
		crond.addAutoStartScheme( "midAutumn_monster_start", self, "onTongAutummMonsterStart" )
		crond.addAutoStartScheme( "xmanStart", self, "xmanStartCB" )
		crond.addAutoStartScheme( "minAutStart", self, "minAutStartCB" )
		crond.addAutoStartScheme( "tongCityWarStart", self, "tongCityWarStartCB" )
		crond.addAutoStartScheme( "yearMonsterStart", self, "yearMonsterStartCB" )


	def onShenguiNotice( self ):
		"""
		define method.
		�������
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ACTIVITY_SGMJ_NOTIFY, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "shen gui" )
		

	def onWuyaoNotice( self ):
		"""
		define method.
		���������
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ACTIVITY_WYQS_NOTIFY, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "wu yao" )

	def onShiluoNotice( self ):
		"""
		define method.
		ʧ�䱦�ػ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ACTIVITY_SLBZ_NOTIFY, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "wu yao" )



	def onCMSNotice01( self ):
		"""
		define method.
		ʥ��ϵͳ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ACTIVITY_CMS_NOTICES01, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "christmas 1" )


	def onCMSNotice02( self ):
		"""
		define method.
		ʥ��ϵͳ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ACTIVITY_CMS_NOTICES02, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "christmas 2" )


	def onCMSNotice03( self ):
		"""
		define method.
		ʥ��ϵͳ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ACTIVITY_CMS_NOTICES03, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "christmas 3" )



	def onChunjieNotice01( self ):
		"""
		define method.
		���ڻ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ACTIVITY_CHUNJIE_NOTICE_01, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "chun jie 1" )


	def onChunjieNotice02( self ):
		"""
		define method.
		���ڻ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ACTIVITY_CHUNJIE_NOTICE_02, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "chun jie 2" )


	def onChunjieNotice03( self ):
		"""
		define method.
		���ڻ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ACTIVITY_CHUNJIE_NOTICE_03, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "chun jie 3" )


	def onChunjieNotice04( self ):
		"""
		define method.
		���ڻ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ACTIVITY_CHUNJIE_NOTICE_04, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "chun jie 4" )



	def onChunjieNotice05( self ):
		"""
		define method.
		���ڻ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ACTIVITY_CHUNJIE_NOTICE_05, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "chun jie 5" )


	def onChunjieNotice06( self ):
		"""
		define method.
		���ڻ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ACTIVITY_CHUNJIE_NOTICE_06, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "chun jie 6" )


	def onActivityLogHandle( self ):
		"""
		define method
		���־���Ƽ�¼
		"""
		BigWorld.globalData["TongManager"].onActivityLogHandle()

	def onTanabataNotice( self ):
		"""
		Define method.
		��Ϧϵͳ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TANABATA_START_NOTICE, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "tanabata" )

	def onTanabataQuizNotice( self ):
		"""
		Define method.
		��Ϧ����ʴ�ϵͳ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TANABATA_QUIZ_NOTICE, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "tanabata quiz" )

	def onTanabataFcwrNotice( self ):
		"""
		Define method.
		��Ϧ��зǳ����Ź���
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TANABATA_FCWR_NOTICE, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "tanabata fcwr" )

	def onTanabataMlzzNotice( self ):
		"""
		Define method.
		��Ϧ��������ϵͳ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TANABATA_MLZZ_NOTICE, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "tanabata mlzz" )

	def onTanabataYhxcNotice( self ):
		"""
		Define method.
		��Ϧ�ǳ���ϵͳ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TANABATA_YHXC_NOTICE, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "tanabata yhxc" )
	
	def onTanabataLoveNotice( self ):
		"""
		Define method
		��Ϧ���˽ڻ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TANABATA_LOVE_NOTICE, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "tanabata love" )
	
	def onTongAutummMonsterStart( self ):
		"""
		define method
		"""
		if not BigWorld.globalData.has_key("Mid_Autumn_Monster"):
			BigWorld.globalData["Mid_Autumn_Monster"] = True
		
		INFO_MSG( "ActivityBroadcastMgr", "start", "tong autumm monster" )

	def onTongAutummMonsterEnd( self ):
		"""
		define method
		"""
		if BigWorld.globalData.has_key("Mid_Autumn_Monster"):
			del BigWorld.globalData["Mid_Autumn_Monster"]
		
		INFO_MSG( "ActivityBroadcastMgr", "end", "tong autumm monster" )

	def onMidAutumnNotice( self ):
		"""
		Define method.
		����ϵͳ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MID_AUTUMIN_NOTICE, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "midautumn" )


	def onMidAutumnRabbitRunNotice( self ):
		"""
		Define method.
		����С�ÿ���ϵͳ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MID_AUTUMIN_RABBIT_RUN_NOTICE, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "midautumn Rabbit" )

	def onNewYearRabbitRunNotice( self ):
		"""
		Define method.
		����С�ÿ���ϵͳ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.NEW_YEAR_RABBIT_RUN_NOTICE, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "NewYear Rabbit" )

	def onMidAutumnRabbitRunStart( self ):
		"""
		Define method.
		����С�ÿ��ܿ�ʼ
		"""
		BigWorld.globalData["AS_RabbitRun_Start_Time"] = int( time.time() ) + csconst.RABBIT_RUN_WAIT_TIME
		BigWorld.globalData["AS_RabbitRun"] = True
		INFO_MSG( "ActivityBroadcastMgr", "notice", "midautumn Rabbit" )


	def onMidAutumnRabbitRunEnd( self ):
		"""
		Define method.
		����С�ÿ��ܽ���
		"""
		if BigWorld.globalData.has_key("AS_RabbitRun"):
			del BigWorld.globalData["AS_RabbitRun"]
		
		INFO_MSG( "ActivityBroadcastMgr", "end", "midautumn Rabbit" )


	def onMidAutumnTongQuestNotice( self ):
		"""
		Define method.
		�����Һ�������ϵͳ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MID_AUTUMIN_TONG_QUEST_NOTICE, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "midautumn tong quest" )


	def onMidAutumnWordFindNotice( self ):
		"""
		Define method.
		����ǧ�ﹲ濾�ϵͳ����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MID_AUTUMIN_WORD_FIND_NOTICE, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "midautumn WordFind" )

	def onMidAutumnTongProtectNotice( self ):
		"""
		Define method.
		�����±����Ҷ�
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MID_AUTUMIN_TONG_PROTECT_NOTICE, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "midautumn TongProtect" )


	def onMidAutumnZhouNianGiftNotice( self ):
		"""
		Define method.
		��������������
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MID_AUTUMIN_ZHOU_NIAN_GIFT_NOTICE, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "midautumn zhou nian li" )


	def onMidAutumnWordMakeNotice( self ):
		"""
		Define method.
		�����������
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MID_AUTUMIN_WORD_MAKE_NOTICE, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "midautumn WordMake" )


	def onMidAutumnKillMoonCakeNotice( self ):
		"""
		Define method.
		����BOSSϲ���
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MID_AUTUMIN_KILL_MOON_CAKE_NOTICE, [] )
		INFO_MSG( "ActivityBroadcastMgr", "notice", "midautumn KillMoonCake" )

	def registeSpawnPoint( self, activityKey, baseMailBox ):
		"""
		define method
		��ˢ�µ�ע�ᵽ��������
		"""
		if not activityKey in self.spawnPointDatas:
			self.spawnPointDatas[activityKey] = []
		self.spawnPointDatas[activityKey].append( baseMailBox )
		# �����Ѿ������Ļ����ˢ�µ�ע��ʱ�����ϴ���ˢ��
		if activityKey in self.startedActivityKeys:
			baseMailBox.cell.remoteCallScript( "startSpawn", [] )
	
	def onTongAutummQuestStart( self ):
		"""
		define method
		"""
		if not "midAutumn_quest_start" in self.startedActivityKeys:
			self.startedActivityKeys.append( "midAutumn_quest_start" )
		if not "midAutumn_quest_start" in self.spawnPointDatas:
			ERROR_MSG( "Spawn point datas(midAutumn_quest_start) not exist on start." )
			return
		for bmb in self.spawnPointDatas["midAutumn_quest_start"]:
			bmb.cell.remoteCallScript( "startSpawn", [] )
		
		INFO_MSG( "ActivityBroadcastMgr", "start", "tong autumm quest" )

	def onTongAutummQuestEnd( self ):
		"""
		define method
		"""
		if "midAutumn_quest_start" in self.startedActivityKeys:
			self.startedActivityKeys.remove( "midAutumn_quest_start" )
		if not "midAutumn_quest_end" in self.spawnPointDatas:
			ERROR_MSG( "Spawn point datas(midAutumn_quest_end) not exist on end." )
			return
		for bmb in self.spawnPointDatas["midAutumn_quest_end"]:
			bmb.cell.remoteCallScript( "stopSpawn", [] )
		
		INFO_MSG( "ActivityBroadcastMgr", "end", "tong autumm quest" )
		
	def xmanStartCB( self ):
		"""
		define method
		ʥ�����ʼ
		key = xmanStart
		key��Ϊspawn point��activityKeyStart����ֵ
		"""
		if not "xmanStart" in self.startedActivityKeys:
			self.startedActivityKeys.append( "xmanStart" )
		if not "xmanStart" in self.spawnPointDatas:
			ERROR_MSG( "Spawn point datas(xmanStart) not exist on start." )
			return
		for bmb in self.spawnPointDatas["xmanStart"]:
			bmb.cell.remoteCallScript( "startSpawn", [] )
		
	def xmanEndCB( self ):
		"""
		define method
		ʥ�������
		key = xmanEnd
		key��Ϊspawn point��activityKeyEnd����ֵ
		"""
		if "xmanStart" in self.startedActivityKeys:
			self.startedActivityKeys.remove( "xmanStart" )
		if not "xmanEnd" in self.spawnPointDatas:
			ERROR_MSG( "Spawn point datas(xmanEnd) not exist on end." )
			return
		for bmb in self.spawnPointDatas["xmanEnd"]:
			bmb.cell.stopSpawn()
			
	def minAutStartCB( self ):
		"""
		define method
		������ʼ
		key = minAutStart
		key��Ϊspawn point��activityKeyStart����ֵ
		"""
		if not "minAutStart" in self.startedActivityKeys:
			self.startedActivityKeys.append( "minAutStart" )
		if not "minAutStart" in self.spawnPointDatas:
			ERROR_MSG( "Spawn point datas(minAutStart) not exist on start." )
			return
		for bmb in self.spawnPointDatas["minAutStart"]:
			bmb.cell.remoteCallScript( "startSpawn", [] )
			
	def minAutEndCB( self ):
		"""
		define method
		��������
		key = minAutEnd
		key��Ϊspawn point��activityKeyEnd����ֵ
		"""
		if "minAutStart" in self.startedActivityKeys:
			self.startedActivityKeys.remove( "minAutStart" )
		if not "minAutEnd" in self.spawnPointDatas:
			ERROR_MSG( "Spawn point datas(minAutEnd) not exist on end." )
			return
		for bmb in self.spawnPointDatas["minAutEnd"]:
			bmb.cell.stopSpawn()
			
	def tongCityWarStartCB( self ):
		"""
		Define method.
		����ս��������
		"""
		if not "tongCityWarStart" in self.startedActivityKeys:
			self.startedActivityKeys.append( "tongCityWarStart" )
		if not "tongCityWarStart" in self.spawnPointDatas:
			ERROR_MSG( "Spawn point datas(tongCityWarStart) not exist on start." )
			return
		for bmb in self.spawnPointDatas["tongCityWarStart"]:
			bmb.cell.remoteCallScript( "startSpawn", [] )
			
	def tongCityWarEndCB( self ):
		"""
		Define method.
		����ս��������
		"""
		if "tongCityWarStart" in self.startedActivityKeys:
			self.startedActivityKeys.remove( "tongCityWarStart" )
		if not "tongCityWarEnd" in self.spawnPointDatas:
			ERROR_MSG( "Spawn point datas(tongCityWarEnd) not exist on end." )
			return
		for bmb in self.spawnPointDatas["tongCityWarEnd"]:
			bmb.cell.stopSpawn()
			
	def yearMonsterStartCB( self ):
		"""
		Define mehod
		ɱ���޻����
		"""
		if not "yearMonsterStart" in self.startedActivityKeys:
			self.startedActivityKeys.append( "yearMonsterStart" )
		if not "yearMonsterStart" in self.spawnPointDatas:
			ERROR_MSG( "Spawn point datas(yearMonsterStart) not exist on start." )
			return
		for bmb in self.spawnPointDatas["yearMonsterStart"]:
			INFO_MSG( "Year Monster come out %d"%bmb.id )
			bmb.cell.remoteCallScript( "startSpawn", [] )
		
	def yearMonsterEndCB( self ):
		"""
		Define method
		ɱ���޻�ر�
		"""
		if "yearMonsterStart" in self.startedActivityKeys:
			self.startedActivityKeys.remove( "yearMonsterStart" )
		if not "yearMonsterEnd" in self.spawnPointDatas:
			ERROR_MSG( "Spawn point datas(yearMonsterEnd) not exist on end." )
			return
		for bmb in self.spawnPointDatas["yearMonsterEnd"]:
			INFO_MSG( "Year Monster stop %d"%bmb.id )
			bmb.cell.stopSpawn()



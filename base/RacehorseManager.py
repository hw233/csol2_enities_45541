# -*- coding: gb18030 -*-
#

# $Id:  Exp $

import BigWorld
from bwdebug import *
import csdefine
import cschannel_msgs
import Love3
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
import time
import csstatus


RACEHORSE_END				= 0
TONG_RACEHORSE_END			= 1			# ����������

MAX_RACE_MAP_COUNT			= 10		# ��������ͼ��Ŀ
MAX_MEMBER_IN_COMMON_MAP	= 400		# ��ͨ��ͼ���ɲ�������Ŀ

ONE_MINUTE					= 60		#
RACE_WAIT_TIME				= 120		# ����ȴ�ʱ��

class RacehorseManager( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )

		self.racerBaseMBDict = {}												#���� { group1: [playerBaseMB, ...], }
		self.lastRaceGroupID = 0
		self.tongRacerBaseMBDict = {}											#such as { ���DBID :[��ԱbaseMailbox01,...], ... }

		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "RacehorseManager", self._onRegisterManager )
		self.raceStartTime = 0
		self.tongStartTime = {}
		BigWorld.globalData["Racehorse_member_count"] = 0
		BigWorld.globalData["RacehorseType"] = "sai_ma_chang_01"


	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register RacehorseManager Fail!" )
			self.registerGlobally( "RacehorseManager", self._onRegisterManager )
		else:
			BigWorld.globalData["RacehorseManager"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("RacehorseManager Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"RacehorseManager_start_notice" : "onStartNotice",
					  	"RacehorseManager_start" : "onStart",
					  	"RacehorseManager_end" : "onEnd",
					  	"RacehorseType_christmas_start": "onChristmasRaceHorse_Start",
					  	"RacehorseType_christmas_end": "onChristmasRaceHorse_End",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )

		crond.addAutoStartScheme( "RacehorseType_christmas_start", self, "onChristmasRaceHorse_Start" )

	def onStart( self ):
		"""
		define method. 
		���ʼ
		"""
		if BigWorld.globalData.has_key( "AS_Racehorse" ):
			curTime = time.localtime()
			ERROR_MSG( "�������ڽ����У�%i��%i����ͼ�ٴο����"%(curTime[3],curTime[4] ) )
			return
		if BigWorld.globalData["RacehorseType"] == "sai_ma_chang_01":
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_SMHD_SIGN_UP_NOTIFY, [] )
		elif BigWorld.globalData["RacehorseType"] == "sai_ma_chang_03":
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CHRISMAS_RACE_HORSE_NOTICE_02, [] )
		
		BigWorld.globalData[ "AS_Racehorse" ] = True
		self.raceStartTime = int( time.time() ) + RACE_WAIT_TIME
		self.addTimer( ONE_MINUTE * 10, 0, RACEHORSE_END )
		INFO_MSG( "RacehorseManager", "start", "" )

	def onEnd( self ):
		"""
		define method.
		�����
		"""
		# ��ֹ�������ڻ��ʼʱ��֮������ ���Ҳ����ñ��
		if BigWorld.globalData.has_key( "AS_Racehorse" ):
			del BigWorld.globalData[ "AS_Racehorse" ]
		else:
			curTime = time.localtime()
			ERROR_MSG( "�����Ѿ�������%i��%i����ͼ�ٴν���"%( curTime[3],curTime[4] ) )
			return
		for id in self.racerBaseMBDict:
			self.getRacehorseSpaceDomain().closeRacehorseSpace( id )
		self.racerBaseMBDict = {}
		self.startRace = False
		BigWorld.globalData["Racehorse_member_count"] = 0
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_SMHD_REWARD_ITEM, [] )
		INFO_MSG( "RacehorseManager", "end", "" )
		
	def onChristmasRaceHorse_Start( self ):
		"""
		ʥ������ʼ
		"""
		BigWorld.globalData["RacehorseType"] = "sai_ma_chang_03"
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CHRISMAS_START_NOTICE, [] )
		INFO_MSG( "RacehorseManager", "start", "Christmas race horse" )
	
	def onChristmasRaceHorse_End( self ):
		"""
		ʥ���������
		"""
		BigWorld.globalData["RacehorseType"] = "sai_ma_chang_01"
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CHRISMAS_END_NOTICE, [] )
		INFO_MSG( "RacehorseManager", "end", "Christmas race horse" )

	def onTimer( self, id, userArg ):
		"""
		ִ�����������ز���
		"""
		if userArg == TONG_RACEHORSE_END:
			self.getRacehorseSpaceDomain().closeRacehorseSpace( self.tongRacerBaseMBDict.pop(0) )
			self.tongStartTime.clear()

		if userArg == RACEHORSE_END:
			self.onEnd()

	def _addCommonRacer( self, playerBaseMB ):
		"""
		��������ҵ�DBID �����飨ÿ�����Ӧһ�ŵ�ͼ��
		"""
		playerID = playerBaseMB.id
		if not self.lastRaceGroupID in self.racerBaseMBDict:
			self.lastRaceGroupID = 0

 		if self.lastRaceGroupID != 0 and len( self.racerBaseMBDict[self.lastRaceGroupID] ) == MAX_MEMBER_IN_COMMON_MAP:
 			self.lastRaceGroupID = 0

		if self.lastRaceGroupID == 0:										#��������
			self.racerBaseMBDict[playerID] = [playerBaseMB]
			self.getRacehorseSpaceDomain().createRaceMap( playerID )
			self.lastRaceGroupID = playerID
		else:
			self.racerBaseMBDict[self.lastRaceGroupID].append( playerBaseMB )

	def enterRacehorseMap( self, playerBaseMB ):
		"""
		define method
		��������
		"""
		if time.time() > self.raceStartTime:
			playerBaseMB.client.onStatusMessage( csstatus.ROLE_RACE_OVER, "" )
			return
		self._addCommonRacer( playerBaseMB )
		#playerBaseMB.cell.pcg_withdrawPet( playerBaseMB.id )	# �ջس�ս����
		BigWorld.globalData["Racehorse_member_count"] = BigWorld.globalData["Racehorse_member_count"] + 1
		playerBaseMB.cell.waitForStart( self.raceStartTime )
		self.getRacehorseSpaceDomain().teleportRacer( playerBaseMB, {'spaceKey': self.lastRaceGroupID } )

	def closeRacehorseMap( self, groupID ):
		"""
		define
		ɾ��������������Ϣ
		"""
		if not groupID in self.racerBaseMBDict:
			return
		del self.racerBaseMBDict[groupID]
		if self.tongStartTime.has_key( groupID ):
			BigWorld.globalData["TongManager"].onTongRaceOver( groupID )
			del self.tongStartTime[groupID]
		self.getRacehorseSpaceDomain().closeRacehorseSpace( groupID )


	#################���������####################
	def enterTongRacehorseMap( self, playerBaseMB, tongdbid ):
		"""
		define method
		"""
		if not tongdbid in self.tongStartTime:
			playerBaseMB.client.onStatusMessage( csstatus.ROLE_RACE_NOT_CREATE_TONG_RACE, "" )
			return

		if time.time() > self.tongStartTime[tongdbid]:
			playerBaseMB.client.onStatusMessage( csstatus.ROLE_RACE_TONG_RACEING, "" )
			return

		self.racerBaseMBDict[tongdbid].append( playerBaseMB )
		self.getRacehorseSpaceDomain().teleportRacer( playerBaseMB, { 'spaceKey':tongdbid } )
		playerBaseMB.cell.waitForStart( self.tongStartTime[tongdbid] )


	def createTongRace( self, playerBaseMB, tongdbid ):
		"""
		define method
		�����������
		"""
		playerBaseMB.cell.removeTongRaceItem()

		self.racerBaseMBDict[tongdbid] = [playerBaseMB]
		self.getRacehorseSpaceDomain().createRaceMap( tongdbid )
		self.tongStartTime[tongdbid] = int( time.time() ) + RACE_WAIT_TIME

	def onStartNotice( self ):
		"""
		define method.
		���ʼ֪ͨ
		"""
		if BigWorld.globalData["RacehorseType"] == "sai_ma_chang_01":
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_SMHD_BEGIN_NOTIFY, [] )
		elif BigWorld.globalData["RacehorseType"] == "sai_ma_chang_03":
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CHRISMAS_RACE_HORSE_NOTICE_01, [] )
		
		

	def getRacehorseSpaceDomain( self ):
		"""
		��õ�ǰ�������͵�domain
		"""
		#SpaceManager �� �����������һ��base�ϡ������������ʡ�
		id = BigWorld.globalData["SpaceManager"].id
		smgr = BigWorld.entities[id]
		return smgr.getDomainItem( BigWorld.globalData["RacehorseType"] ).base


#		# ���ɰ�������¼���
#		query = """CREATE TABLE IF NOT EXISTS `custom_TongRaceRecord` (
#				`id`				BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
#				`sm_tongDBID`		BIGINT(20)   UNSIGNED NOT NULL,
#				`sm_raceTime` 		BIGINT(20)   UNSIGNED NOT NULL,
#				PRIMARY KEY  ( `id` )
#				) ENGINE=InnoDB;"""
#		BigWorld.executeRawDatabaseCommand( query, createTableCB )

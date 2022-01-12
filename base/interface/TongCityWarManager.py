# -*- coding: gb18030 -*-
#
# $Id: TongCityWarManager.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

import time
import random
import copy
import cPickle

import BigWorld
import ShareTexts as ST
import csdefine
import csstatus
import csconst
import Function
import Love3
import cschannel_msgs
from bwdebug import *
from MsgLogger import g_logger
from Function import Functor
from ObjectScripts.GameObject import GameObject
from ObjectScripts.GameObjectFactory import g_objFactory
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from items.ItemDataList import ItemDataList
g_items = ItemDataList.instance()


CONST_CITY_GET_SIGN_CLEAR_TIME 			= 24 			# ����NPC��ȡ��¼���ʱ��
SIGN_UP_TONG_LIMIT						= 8				# ÿһ��������ı����������

# ս���������
WAR_RESULT_NONE = -1
WAR_RESULT_WINNER = 1
WAR_RESULT_LOSER = 0

FINAL_TONG_COUNT = 2					# ������������Ŀ

PRE_WAR_ENTER_SPACE_PLAYER_LIMIT = 15	# ��սԤ��������ս���İ���Ա��������
FINAL_WAR_RIGHT_PLAYER_LIMIT = 20	# ��ս����������ս�����ط�����Ա��������
FINAL_WAR_HAS_MAYOR_LEFT_PLAYER_LIMIT = 15	# ��ԭ��������ս��������������ս���Ľ���������Ա��������
FINAL_WAR_NO_MAYOR_LEFT_PLAYER_LIMIT	= 20	# ûԭ�����ĳ�ս��������������ս������������

# ��ʱ�����д���
SINGUP_NOTIFY_WILL_NUM 	= 4
SINGUP_NOTIFY_NUM 		= 3
NOTIFY_WAR_START_NUM 	= 2

# time user arg
TIME_USER_ARG_NOTIFY_WILL_SIGNUP  		= 1
TIME_USER_ARG_NOTIFY_SIGNUP 			= 2
TIME_USER_ARG_NOTIFY_WAR_START			= 3
TIME_USER_ARG_NOTIFY_FINAL_RESULT		= 4
TIME_USER_ARG_WAR_END_BE_30				= 5
TIME_USER_ARG_SIGNUP_PROGRESS			= 6
TIME_USER_ARG_CLOSE_WAR_PROGRESS		= 7
TIME_USER_ARG_PRE_WAR					= 8 # Ԥ�� 
TIME_USER_ARG_FINAL_WAR					= 9 # ����

# time define 
TIME_NOTIFY_WILL_SIGNUP = 15
TIME_NOTIFY_SIGNUP		= 5
TIME_NOTIFY_WAR_START	= 1
TIME_WAR_PRE			= 20			# Ԥ��ʱ��
TIME_WAR_FINAL			= 30 			# ����ʱ��

# ĳ�׶�һ���ö���ʱ��
TIME_NOTIFY_WILL_SIGNUP_LONG		= TIME_NOTIFY_WILL_SIGNUP * SINGUP_NOTIFY_WILL_NUM
TIME_NOTIFY_SIGNUP_LONG				= TIME_NOTIFY_SIGNUP * SINGUP_NOTIFY_NUM
TIME_NOTIFY_WAR_START_LONG			= TIME_NOTIFY_WAR_START * NOTIFY_WAR_START_NUM

# city war stage
CITY_WAR_STAGE_FREE 			= 0
CITY_WAR_STAGE_NOTIFY			= 1
CITY_WAR_STAGE_SIGNUP 			= 2
CITY_WAR_STAGE_UNDERWAY			= 3
CITY_WAR_STAGE_UNDERWAY_FINAL 	= 4
CITY_WAR_STAGE_UNDERWAY_FREE	= 5

# enter num
CITY_WAR_MAX_ENTER = 15
CITY_WAR_FINAL_MAX_ENTER_HAS_MASTER = 15
CITY_WAR_FINAL_MAX_ENTER_NOT_MASTER = 20
CITY_WAR_FINAL_MAX_ENTER_MASTER		= 20

JOIN_REWAR_ITEMS = [ 60101264, 60101251 ]

class TimeControl:
	def __init__( self ):
		self.timerExRecord = {}
		self.timerExRepeat = {}
		self.timerExRecordID = {}
	
	def addTimerEx( self, key, time, func, args ):
		timerID = self.addTimer( time, 0, key )
		self.timerExRecord[ key ] = [ func, args, 0, False ]
		self.timerExRecordID[ key ] = timerID
		
	def addtimerExRepeat( self, key, time, repeatTime, repeat, func, args ):
		self.addTimer( time, repeatTime, key )
		self.timerExRecord[ key ] = [ func, args, repeat, False ]
	
	def popTimerEx( self, key ):
		if self.timerExRecord.has_key( key ):
			self.timerExRecord[ key ][ 3 ] = True
		
		if self.timerExRecordID.has_key( key ):
			self.delTimer( self.timerExRecordID[ key ] )
			
	def onTimer( self, tid, key ):
		if self.timerExRecord.has_key( key ):
			func = self.timerExRecord[ key ][ 0 ]
			args = copy.deepcopy( self.timerExRecord[ key ][ 1 ] )
			repeat = self.timerExRecord[ key ][ 2 ]
			isDel = self.timerExRecord[ key ][ 3 ]
			if isDel:
				self.delTimer( tid )
				self.timerExRecord.pop( key )
				return
				
			if repeat:
				if self.timerExRepeat.has_key( key ):
					if self.timerExRepeat[ key ] >= repeat:
						self.timerExRecord.pop( key )
						self.timerExRepeat.pop( key )
						return
					else:
						self.timerExRepeat[ key ] += 1
				else:
					self.timerExRepeat[ key ] = 1
			else:
				self.timerExRecord.pop( key )
				
			func( *args )

class TongCityWarManager( TimeControl ):
	def __init__( self ):
		TimeControl.__init__( self )
		self.cityWarCurrentStage = CITY_WAR_STAGE_FREE
		self.cityWarTmpData = {}									# ����ս����ʱ���ݻ���
		self.cwar_spaceDomains = {}									# ����ע��Ӵ����ĳ���ս���������� ս������ʱ��Ҫ֪ͨ�����������ĳ����Ϊ�����ս��
		self.cityWarStarTime = 0
		
		# ��ս�������Ƿ��ڱ��������У������������սʱ�ڱ��������У���ô��ʱ�ѱ������ݷ��뻺�������ȴ�������һ�������ٽ��Ŵ���˴����롣
		# ����ñ���˳����У����ⱨ��ʱ�������첽������ɱ������������Ƹ��������⡣
		self.signUpProgressTong = None
		self.cityWarSignUpBuffer = []		# array of (tongDBID, memberDBID, replevel, repMoney, spaceName, playerBase)
		self.cityWarEnter = {} 				# { ���ID������ }
		self.joinActivityPlayers = {}
		for cityName in csconst.TONG_CITYWAR_CITY_MAPS.iterkeys():
			self.tongCityWarFightInfos.addCity( cityName )
				
		self.cityWarReset()
	def onManagerInitOver( self ):
		"""
		virtual method.
		��������ʼ�����
		"""
		self.tongCityWarManager_registerCrond()		

	def tongCityWarManager_registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
					  	"TongCityWarManager_start" 					: "onTongCityWarStart", 					# ��ս��ʼ
					  	"TongCityWarManager_end" 					: "onTongCityWarEnd", 						# ��ս������������Ԥ����ʹ��ͬ�������
					  	"TongCityWarFinal_start"					: "onTongCityWarFinalStart",				# ��ս������ʼ
					  	"TongCityWarFinal_end"						: "onTongCityWarEnd",						# ��ս������������Ԥ����ʹ��ͬ�������
					  	"TongCityWarManager_signup_start" 			: "onTongCityWarSignUpStart", 				# ������ʼ
					  	"TongCityWarManager_signup_end" 			: "onTongCityWarSignUpEnd", 				# ��������
					  	"TongCityWarManager_signupNotify" 			: "onCityWarWillSignUpNotify",			 	# ս���ɲμӱ���ͨ��
					  	"TongCityWarManager_calcCityRevenue"		: "onCalcAllCityRevenue",					# �����������˰
					  	"TongCityWarManager_final_startNotify"		: "onCityWarFinalStartNotify",				# ����10����ǰ��ʼ��֪ͨ
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )

	def onCityWarWillSignUpNotify( self ):
		# define method.
		# ������ս�ɱ���ͨ��
		self.tongChiefRewardRecords = []
		self.cityWarStarTime = time.time()
		self.onTimerCityWarWillSignUp()
	
	def onCityWarFinalStartNotify( self ):
		# define method.
		# ����10���Ӻ�ʼ��֪ͨ
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_FINAL_START_NOTIFY, [] )

	def onTongEntityLoadMemberInfoComplete( self, tongDBID, tongEntity, chiefName ):
		"""
		virtual method.
		���ʵ��������Ա������
		"""
		for info in self.tongCityWarFightInfos.infos.itervalues():
			if self.hasTongEntity( info.master ):
				self.registerToCityManager( info.master, info.getCityName(), True )
			
	def cityWarReset( self ):
		self.cityWarTmpData[ "tong_war_data" ] = {}					# ս���и�����ս������ ������� �ж԰���ϵ �� ����Ϊ�ط��򹥷���־ �Լ�����ս����Ҫ��
		self.cityWarTmpData[ "getItem_record" ] = {}				# ��ȡ�����ʵ��¼
		self.cityWarTmpData[ "getSkill_record" ] = {}				# ��ȡ���ܼ�¼
		
		self.signUpProgressTong = None
		
		self.cityWarSignUpBuffer = []		# array of (tongDBID, memberDBID, replevel, repMoney, spaceName, playerBase)
		self.tongCityWarFightInfos.reset()
		self.cityWarCurrentStage = CITY_WAR_STAGE_FREE
				
	def registerCityWarDomain( self, domain ):
		"""
		����ע��Ӵ����ĳ���ս���������� ս������ʱ��Ҫ֪ͨ�����������ĳ����Ϊ�����ս��
		"""
		self.cwar_spaceDomains[ domain.id ] = domain

	def isRegisterCityWarDomain( self, domainID ):
		"""
		�Ƿ�ע�����domain
		"""
		return domainID in self.cwar_spaceDomains

	def onTakeCityRevenue( self, city, money ):
		"""
		define method.
		��ȡ��������˰
		"""
		DEBUG_MSG("recv Revenue:", city, money)
		for info in self.cityRevenue:
			if info[ "spaceName" ] == city:
				info[ "todayRevenue" ] += money
				try:
					tongDBID = self.getCityMasterTongDBID( city )
					item = self._tongBaseDatas.get( tongDBID )
					if item:
						tongName = item[ "tongName" ]
						g_logger.tongReceiveRevenueLog( tongDBID, tongName, city, money )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
				return

	def onRequestSetCityRevenueRate( self, playerBase, tongDBID, cityName ):
		"""
		define method.
		�����޸ĳ�������˰��
		"""
		for info in self.cityRevenue:
			if info[ "spaceName" ] == cityName:
				playerBase.client.tong_onRequestSetCityRevenueRate( info[ "revenueRate" ] )
				return

		playerBase.client.tong_onRequestSetCityRevenueRate( 0 )

	def onSetCityRevenueRate( self, playerBase, playerName, tongDBID, cityName, rate ):
		"""
		define method.
		�޸ĳ�������˰��
		"""
		if rate < 0:
			rate = 0
		elif rate > 50:
			rate = 50

		day = time.localtime()[6]
		for info in self.cityRevenue:
			if info[ "spaceName" ] == cityName:
				if info[ "modifyRevenueDay" ] != day:
					info[ "revenueRate" ] = rate
					BigWorld.globalData[cityName + ".revenueRate"] = rate
					playerBase.cell.tong_onSetCityRevenueRateSuccessfully( cityName, rate )
					Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONGCITYWAR_VOICE_2 % ( playerName, csconst.TONG_CITYWAR_CITY_MAPS[cityName], rate ), [] )
				else:
					self.statusMessage( playerBase, csstatus.TONG_CITY_REVENUE_NO )
				return

		self.writeToDB()

	def updateNewCityRevenueInfo( self, cityName ):
		"""
		�����³�������˰��Ϣ
		"""
		for info in self.cityRevenue:
			if info[ "spaceName" ] == cityName:
				#info[ "todayRevenue" ] = 0
				#info[ "yesterdayRevenue" ] = 0
				info[ "getWeek" ] = 0
				#info[ "revenueRate" ] = 10
				info[ "modifyRevenueDay" ] = 10
				return

		info = { "spaceName" : cityName,  "todayRevenue" : 0,  \
				"yesterdayRevenue" : 0, "getWeek" : 0, "revenueRate" : 10, "modifyRevenueDay" : 10 }

		self.cityRevenue.append( info )
		BigWorld.globalData[cityName + ".revenueRate"] = 10

	def onInitAllCityRevenueRate( self ):
		"""
		����������ʱ��ʼ�����е�����˰
		"""
		for info in self.cityRevenue:
			BigWorld.globalData[info[ "spaceName" ] + ".revenueRate"] = info[ "revenueRate" ]

	def onCalcAllCityRevenue( self ):
		"""
		define method.
		�������г�������˰
		"""
		for info in self.cityRevenue:
			info[ "yesterdayRevenue" ] = info[ "todayRevenue" ]
			info[ "todayRevenue" ] = 0
			DEBUG_MSG( "calc cityRevenue:%s--%d" % ( info[ "spaceName" ], info[ "yesterdayRevenue" ] ) )

		self.writeToDB()

	def onViewCityRevenue( self, playerBase, tongDBID, city, npcID ):
		"""
		define method.
		�鿴����˰��
		"""
		DEBUG_MSG( "view Revenue:", playerBase, city, npcID )
		if tongDBID <= 0 or tongDBID != self.getCityMasterTongDBID( city ):
			playerBase.client.onSetGossipText( cschannel_msgs.TONGCITYWAR_VOICE_3)
			playerBase.client.onGossipComplete( npcID )
			return

		isfind = False
		for info in self.cityRevenue:
			if info[ "spaceName" ] == city:
				playerBase.client.onSetGossipText( cschannel_msgs.TONGCITYWAR_VOICE_4 % Function.switchMoney( info[ "yesterdayRevenue" ] ) )
				isfind = True
				break

		if not isfind:
			playerBase.client.onSetGossipText( cschannel_msgs.TONGCITYWAR_VOICE_5)
		playerBase.client.onGossipComplete( npcID )

	def onGetCityTongRevenue( self, city, playerDBID, tongDBID, playerBase ):
		"""
		define method.
		��ȡ����˰��
		"""
		if tongDBID <= 0 or tongDBID != self.getCityMasterTongDBID( city ):
			self.statusMessage( playerBase, csstatus.TONG_GET_CITY_REVENUE_GRADE_VALID )
			return

		tongEntity = self.findTong( tongDBID )
		tongEntity.onGetCityTongRevenue( playerDBID )
	
	def getCityTongChiefReward( self, tongIDBID, chiefMailBox ):
		# define method
		# ������ȡ����
		if tongIDBID in self.tongChiefRewardRecords:
			chiefMailBox.client.onStatusMessage( csstatus.TONG_CITY_WAR_CHIEF_REWARD_ALREADY, "" )
			return 
		
		cityName = self.tongCityWarFightInfos.getJoinCityName( tongIDBID )
		if cityName == "":
			chiefMailBox.client.onStatusMessage( csstatus.TONG_CITY_WAR_CHIEF_NOT_JOIN, "" )
			return
			
		winNum = self.tongCityWarFightInfos[ cityName ].getTongWinNum( tongIDBID )
		chiefMailBox.cell.tong_cityWarGetChiefReward( self.tongCityWarFightInfos[ cityName ].getMaster() == tongIDBID, winNum )
	
	def onGetCityTongChiefRewardSuccess( self, tongIDBID ):
		# define method
		# ������ȡ�����ɹ�
		self.tongChiefRewardRecords.append( tongIDBID )
				
	def getCityTongItem( self, playerDBID, playerTongDBID, playerBaseMB, cityName ):
		# define method.
		# ��ȡ����ռ����ľ����ʵ
		if not self.tongCityWarFightInfos[ cityName ].isMaster( playerTongDBID ):
			playerBaseMB.client.onStatusMessage( csstatus.TONG_JYGS_ITEM_GET_INVALIDE, "" )
			return

		t = time.localtime()
		if playerDBID in self.cityWarTmpData[ "getItem_record" ]:
			if self.cityWarTmpData[ "getItem_record" ][ playerDBID ] == t[0] + t[1] + t[2]:
				playerBaseMB.client.onStatusMessage( csstatus.TONG_JYGS_ITEM_GET_OVER, "" )
				return

		playerBaseMB.cell.tong_getCityTongItem()

	def onGetCityTongItemSuccess( self, playerDBID ):
		# define method.
		# ��ȡ����ռ����ľ����ʵ�ɹ��ص�
		t = time.localtime()
		self.cityWarTmpData[ "getItem_record" ][ playerDBID ] = t[0] + t[1] + t[2]
	
	def cityWarIntegralReward( self, tongDBID, integral ):
		# define method.
		# �������ֶһ�����ʽ�
		if self._tongEntitys.has_key( tongDBID ):
			self._tongEntitys[ tongDBID ].onCityWarIntegralRewar( integral )

	def getCityTongSkill( self, playerDBID, playerTongDBID, playerBaseMB, spaceName ):
		# define method.
		# ��ȡ����ռ����ļ���
		if playerTongDBID == 0 or playerTongDBID != self.getCityMasterTongDBID( spaceName ):
			playerBaseMB.client.onStatusMessage( csstatus.TONG_CITY_SKILL_GET_NONE, "" )
			return

		t = time.localtime()
		if playerDBID in self.cityWarTmpData[ "getSkill_record" ]:
			if self.cityWarTmpData[ "getSkill_record" ][ playerDBID ] == t[0] + t[1] + t[2]:
				playerBaseMB.client.onStatusMessage( csstatus.TONG_CITY_SKILL_GET_OVER, "" )
				return

		playerBaseMB.cell.spellTarget( 730019001, playerBaseMB.id )
		self.cityWarTmpData[ "getSkill_record" ][ playerDBID ] = t[0] + t[1] + t[2]

	def getAllCityWarDomain( self ):
		"""
		��ȡ����ս��domain
		"""
		return self.cwar_spaceDomains.values()
		
	def onLoadAllTongOver( self ):
		#virtual method.
		#���а��������.
		pass
		
	def getCityMasterTongDBID( self, cityName ):
		"""
		��ȡĳ�����е����� ���DBID
		"""
		return self.tongCityWarFightInfos[ cityName ].getMaster()

	def onTongDismiss( self, tongDBID ):
		"""
		�а���ɢ�ˣ������ս�д˰����������
		
		@param tongDBID : ��ɢ����dbid
		@type tongDBID : DATABASE_ID
		"""
		self.tongCityWarFightInfos.onTongDismiss( tongDBID, self.cityWarCurrentStage == CITY_WAR_STAGE_UNDERWAY or self.cityWarCurrentStage == CITY_WAR_STAGE_UNDERWAY_FINAL )

	def updateTongChiefName( self, tongDBID ):
		"""
		��������
		"""
		self.findTong( tongDBID ).queryTongChiefInfos()  # ������������

	def cityWarQueryIsCanSignUp( self, playerBase, tongDBID, tonglevel, repMoney, cityName ):
		# define method.
		# �������ս���������
		if self.cityWarCurrentStage != CITY_WAR_STAGE_SIGNUP:
			self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_NOT_SIGN_UP_TIME )
			return
			
		if self.tongCityWarFightInfos.isMaster( tongDBID ):# ��ռ����һ������
			self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_EXIST_INVALID )
			return
		
		otherSinUpCity = self.tongCityWarFightInfos.isSignUp( tongDBID )
		if otherSinUpCity:# �Ѿ�����
			if otherSinUpCity == cityName: # �Ѿ�ͬ��ͬһ����
				self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_HAS_INVALID )
			else:
				self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_SINUP_OTHER )
			return
		
		playerBase.client.tong_onQueryContest( tonglevel, repMoney )	
	
	def requestContestCityWar( self, playerBase, tongDBID, memberDBID, replevel, repMoney, cityName ):
		"""
		define mothod.
		�������������� (���뾺��)�������������
		@param replevel		: ��ἶ������
		@param cityName	: ��������ĳ��е�ͼ����
		"""
		DEBUG_MSG( "tongDBID=%i, memberDBID=%i, cityName=%s" % ( tongDBID, memberDBID, cityName ) )
		if self.cityWarCurrentStage != CITY_WAR_STAGE_SIGNUP:
			self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_NOT_SIGN_UP_TIME )
			return
			
		if self.tongCityWarFightInfos.isMaster( tongDBID ):# ��ռ����һ������
			self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_EXIST_INVALID )
			return
		
		otherSinUpCity = self.tongCityWarFightInfos.isSignUp( tongDBID )
		if otherSinUpCity:# �Ѿ�����
			if otherSinUpCity == cityName: # �Ѿ�ͬ��ͬһ����
				self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_HAS_INVALID )
			else:
				self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_SINUP_OTHER )
			return
			
		self.cityWarSignUpBuffer.append( ( tongDBID, memberDBID, replevel, repMoney, cityName, playerBase ) )	# ��������뻺��
		self.signUpProgress()
		
		try:
			g_logger.actJoinLog( csdefine.ACTIVITY_TONG_DUO_CHENG, csdefine.ACTIVITY_JOIN_TONG, tongDBID, self.getTongNameByDBID( tongDBID ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		
	def signUpProgress( self ):
		# self.cityWarSignUpBuffer : array of (tongDBID, memberDBID, replevel, repMoney, cityName, playerBase)
		#�����������뱣֤�б�������
		if not len( self.cityWarSignUpBuffer ):
			return			
		if self.cityWarCurrentStage != CITY_WAR_STAGE_SIGNUP: # ��ǰ���ܱ���
			return
						
		info = self.cityWarSignUpBuffer.pop( 0 )
		tongDBID = info[0]
		cityName = info[4]
		playerBase = info[5]
		# �Ѿ�����
		if self.tongCityWarFightInfos.isSignUp( tongDBID ): # �Ѿ�����
			DEBUG_MSG( "tong( %i ) had been signed up." % ( tongDBID ) )
			self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_HAS_INVALID )
			self.signUpProgress()	# ������һ������
			return
		if self.tongCityWarFightInfos.isFull( cityName ):
			DEBUG_MSG( "%s �����������ﵽ���ޡ�" % cityName )
			self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_SIGN_UP_FULL )
			self.signUpProgress()	# ������һ������
			return
			
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			memberDBID = info[1]
			replevel = info[2]
			repMoney = info[3]
			self.signUpProgressTong = ( tongDBID, cityName )
			tongEntity.onContestCityWar( memberDBID, replevel, repMoney, cityName )
			self.addTimerEx( TIME_USER_ARG_SIGNUP_PROGRESS, 1, self.signUpProgress, [] )
			
	def onSignUpCityWarResult( self, tongDBID, succeeded ):
		"""
		define mothod.
		��ᱨ����ս�Ľ������
		"""
		DEBUG_MSG( "sign up result", tongDBID, succeeded )
		if succeeded:	# �����ɹ�
			self.tongCityWarFightInfos.signUp( self, self.signUpProgressTong[ 1 ], self.signUpProgressTong[ 0 ] )
			
		self.signUpProgressTong = None
		self.signUpProgress()
		
	def onQueryCityTong( self, city, playerBaseMB ):
		"""
		define method.
		��ѯ��ռ�����Ӣ�۰�
		@param city: ���е�fengming ����
		@param playerBaseMB:��ҵ�basemailbox
		"""
		for infos in self.tongCityRecords:
			if infos[ "spaceName" ] == city:
				if len( infos[ "tongInfos" ] ) <= 0:
					break
				for idx, info in enumerate( infos[ "tongInfos" ] ):
					playerBaseMB.client.tong_onQueryCityTongMasters( idx, info[ "tongName" ], info[ "date" ], info[ "chiefName" ] )
				playerBaseMB.client.tong_onQueryCityChanged( city )
				tongDBID = self.getCityMasterTongDBID( city )
				tongName = self.getTongNameByDBID( tongDBID )
				playerBaseMB.client.tong_onQueryCurMaster( tongName )
				return

		playerBaseMB.client.onStatusMessage( csstatus.TONG_QUERY_HOLD_CITY_NONE, "" )

	def onQeryCityWarVersus( self, cityName, playerBaseMB ):
		# Define method.
		# ��ѯ���ж�ս��Ϣ
		warCity = self.tongCityWarFightInfos[ cityName ]
		master = warCity.getMaster()
		cityMasterName = self.getTongNameByDBID( master )
		giveClientData = [cityMasterName]
		
		for roundWars in warCity.roundItemList:
			length = len( roundWars )
			matchLevel = csdefine.CITY_WAR_LEVEL_NONE
			if length > 2:
				matchLevel = csdefine.CITY_WAR_LEVEL_QUARTERFINAL
			elif length <= 2 and length > 1:
				matchLevel = csdefine.CITY_WAR_LEVEL_SEMIFINAL
			elif length == 1:
				matchLevel = csdefine.CITY_WAR_LEVEL_FINAL
				
			for war in roundWars:
				nameVersus = [ self.getTongNameByDBID( tongDBID ) for tongDBID in war.getTongDBIDs() ]
				winner = self.getTongNameByDBID( war.getWinner() )
				giveClientData.append( {"versus":nameVersus, "winner":winner, "matchLevel": matchLevel } )
		
		playerBaseMB.client.tong_onQueryCityWarTable( giveClientData )
		
	def onQueryCurMasterByCityName( self, cityName, playerBaseMB ):
		"""
		��ѯ���е�ǰ��ռ����
		"""
		warCity = self.tongCityWarFightInfos[ cityName ]
		master = warCity.getMaster()
		cityMasterName = self.getTongNameByDBID( master )
		playerBaseMB.client.tong_onReceiveCurMaster( cityMasterName )
		
	def onRoleSelectEnterWar( self, playerTongDBID, playerBaseMB ):
		# define mothod.
		# ����������ս�����������Ҫ����ĵ�ͼ
		if self.cityWarCurrentStage < CITY_WAR_STAGE_UNDERWAY:
			playerBaseMB.client.onStatusMessage( csstatus.TONG_CITY_WAR_NO_WAR, "" )
			return
			
		cityName = self.tongCityWarFightInfos.getJoinCityName( playerTongDBID )
		if not cityName:
			self.statusMessage( playerBaseMB, csstatus.TONG_CITY_WAR_CANNOT_ENTER )
			return 
		
		if not self.tongCityWarFightInfos[ cityName ].checkTongHasWar( playerTongDBID ):
			self.statusMessage( playerBaseMB, csstatus.TONG_CITY_WAR_CANNOT_ENTER )
			return
		
		if self.tongCityWarFightInfos[ cityName ].isWinner( playerTongDBID ):
			self.statusMessage( playerBaseMB, csstatus.TONG_CITY_WAR_IS_WIN )
			return

		if self.cityWarCurrentStage < CITY_WAR_STAGE_UNDERWAY:
			baseMailbox.client.onStatusMessage( csstatus.TONG_CITY_WAR_CLOSE, "" )
			return
		
		spaceKey = self.tongCityWarFightInfos[ cityName ].getSpaceKey( playerTongDBID )
		playerBaseMB.cell.tong_gotoCityWar( spaceKey )

	def rewardJoin( self ):
		# �����в�����Ҳ��뽱��
		mailMgr = BigWorld.globalData[ "MailMgr" ]
		itemDatas = []
		for itemID in JOIN_REWAR_ITEMS:
			item = g_items.createDynamicItem( itemID )
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
			itemData = cPickle.dumps( tempDict, 0 )
			itemDatas.append( itemData )
		
		for ename, inf in self.joinActivityPlayers.iteritems():
			mailMgr.sendWithMailbox( 
				None, \
				inf[ 0 ], \
				ename, \
				csdefine.MAIL_TYPE_QUICK, \
				csdefine.MAIL_SENDER_TYPE_NPC, \
				cschannel_msgs.TONGCITYWAR_MAIL_MAIL_SEND_NAME, \
				cschannel_msgs.TONGCITYWAR_MAIL_TITILE, \
				"", \
				0, \
				itemDatas\
			)
			
		self.joinActivityPlayers = {}
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_NOTIFY_END, [] )
	# -----------------------------------------------------
	# callback
	# -----------------------------------------------------
	def onEnterCityWarSpace( self, spaceDomain, baseMailbox, params ):
		# define method.
		# ����һ��entity��ָ����space��
		DEBUG_MSG( "params=",  params )
		# ע��Ӵ�����ս��domain
		if not self.isRegisterCityWarDomain( spaceDomain.id ):
			self.registerCityWarDomain( spaceDomain )

		islogin = params.has_key( "login" )
		tongDBID = params[ "tongDBID" ]
		ename = params[ "ename" ]
		
		if self.cityWarCurrentStage >= CITY_WAR_STAGE_UNDERWAY:
			if self.cityWarCheckFull( tongDBID ): # �ð����������Ѿ���
				if islogin:
					baseMailbox.logonSpaceInSpaceCopy()
					return
					
				baseMailbox.client.onStatusMessage( csstatus.TONG_CITY_WAR_CANT_ENTER_PLAYER_LIMIT, "" )
			else:
				cityName = self.tongCityWarFightInfos.getJoinCityName( tongDBID )
				if cityName:
					cityWarItem = self.tongCityWarFightInfos[ cityName ]
					params[ "spaceKey" ] = cityWarItem.getSpaceItemKey( tongDBID )
					war = cityWarItem.searchWar( tongDBID )
					params[ "left" ] = war.tongDBID_1  # ����Ӫ
					params[ "leftTongName" ] = self.getTongNameByDBID( war.tongDBID_1 )
					params[ "right" ] = war.tongDBID_2 # ����Ӫ
					params[ "rightTongName" ] = self.getTongNameByDBID( war.tongDBID_2 )
					if self.tongCityWarFightInfos[ cityName ].isFinal() and cityWarItem.getMaster() :
						params[ "defend" ] = cityWarItem.getMaster()  # ����
						params[ "defendTongName" ] = self.getTongNameByDBID( cityWarItem.getMaster() )
						params[ "occupyNum" ] = self._getTongOccupyCityNum( cityName, cityWarItem.getMaster() )
					
					if self.cityWarCurrentStage == CITY_WAR_STAGE_UNDERWAY_FINAL:
						params[ "isFinal" ] = True
						starTime = self.cityWarStarTime if self.cityWarStarTime else time.time()
						params[ "finalRewardTime" ] = starTime + csconst.TONG_CITY_WAR_CHAMPION_REWARD_LIVING
					else:
						params[ "isFinal" ] = False
						
					params[ "warRound" ] = cityWarItem.getRound() 
					params[ "cityName" ] = cityName
					self.joinActivityPlayers[ ename ] = [ baseMailbox, tongDBID ]
					spaceDomain.onEnterWarSpace( baseMailbox, params )
		elif not islogin:
			baseMailbox.client.onStatusMessage( csstatus.TONG_CITY_WAR_CLOSE, "" )
		else:
			baseMailbox.logonSpaceInSpaceCopy()
	
	def _getTongOccupyCityNum( self, cityName, tongDBID ):
		# ��ȡ��󼸴�ռ���Ƿ�Ϊͬһ����
		num = 0
		for infos in self.tongCityRecords:
			if infos[ "spaceName" ] == cityName:
				if len( infos[ "tongInfos" ] ) <= 0:
					break
				
				if len( infos[ "tongInfos" ] ) < 2:
					return num
					
				masterInfo_1 = infos[ "tongInfos" ][ -1 ]
				masterInfo_2 = infos[ "tongInfos" ][ -2 ]
				if masterInfo_1[ "tongDBID" ] == tongDBID:
					num += 1
					
				if masterInfo_2[ "tongDBID" ] == tongDBID:
					num += 1
		return num
	
	def onWarMessage( self, tongDBID, statusID, *args ):
		"""
		ս�����ͳһϵͳͨ�� ��ָ�����ͨ��
		"""
		args = "" if args == () else str( args )
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onStatusMessage( statusID, args )

	def onWarAllMessage( self, isAll, statusID, *args ):
		"""
		ս�����ͳһϵͳͨ�� ������ս�����ͨ��
		@param isAll:�Ƿ�����а�� �������Ƿ��Ѿ���ǰ����ս���˵İ�ᷢ����Ϣ
		"""
		for item in self.tongCityWarFightInfos.infos.itervalues():
			notifyList = []
			if isAll:
				notifyList = item.signUpList
			else:
				notifyList = item.getCurrentTong()
				
			for tongDBID in notifyList:
				self.onWarMessage( tongDBID, statusID, *args )
	
	def onCeaseMatchMessage( self, tongDBIDs ):
		# ֪ͨû�к�̱����İ�ᣬ�������콱��
		for inf in self.joinActivityPlayers.itervalues():
			if inf[ 1 ] in tongDBIDs:
				inf[ 0 ].client.onStatusMessage( csstatus.TONG_CITY_WAR_NOTIFY_JOIN, "" )
			
	def registerToCityManager( self, tongDBID, city, isInit ):
		"""
		�����п��ư����Ϣע�ᵽ���й�����
		"""
		# ���й����߻��������ȡ���ݣ� ȡ�����¼�ó��п��ư��
		BigWorld.globalData[ "holdCity.%s" % city ] = ( tongDBID, self.getTongNameByDBID( tongDBID ) )
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.setHoldCity( city, isInit )
	
	def onTongCityWarSignUpStart( self ):
		"""
		defined method.
		������ʼ
		"""
		DEBUG_MSG( "issue jingpai signup start notify!" )
		if self.cityWarCurrentStage > CITY_WAR_STAGE_SIGNUP:
			return
		self.cityWarReset()
		self.cityWarCurrentStage = CITY_WAR_STAGE_SIGNUP
		self.onTimerCityWarSignUp()
			
	def onTongCityWarSignUpEnd( self ):
		"""
		defined method.
		��������
		"""
		self.cityWarCurrentStage = CITY_WAR_STAGE_UNDERWAY_FREE
		DEBUG_MSG( "issue jingpai signup over notify!" )
			
	def onTongCityWarStart( self ):
		# defined method.
		# ����սԤ����ʼ
		if self.cityWarCurrentStage != CITY_WAR_STAGE_UNDERWAY_FREE:
			return
		self.cityWarCurrentStage = CITY_WAR_STAGE_UNDERWAY
		self.tongCityWarFightInfos.startWar( self )
		self.onCityWarStart( TIME_WAR_PRE )
		self.addTimerEx( TIME_USER_ARG_PRE_WAR, TIME_WAR_PRE * 60 , self.onTongCityWarEnd, [] )
		
	def onTongCityWarFinalStart( self ):
		# defined method.
		# ��ս������ʼ
		if self.cityWarCurrentStage != CITY_WAR_STAGE_UNDERWAY_FREE:
			return
			
		self.cityWarCurrentStage = CITY_WAR_STAGE_UNDERWAY_FINAL
		self.tongCityWarFightInfos.startFinalWar( self )
		self.onCityWarStart( TIME_WAR_FINAL )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_START_NOTIFY, [] )
		self.addTimerEx( TIME_USER_ARG_FINAL_WAR, TIME_WAR_FINAL * 60, self.onTongCityWarEnd, [] )
		
	def onCityWarStart( self, protime ):
		"""
		ս����ʼ�Ĵ���
		����timer������ȫ�ֱ�ǣ���ʷԭ�򣬾�����Ԥ��ʹ��ͬһ��timer��globalDataȫ�ֱ��
		"""
		BigWorld.globalData[ "CityWarOverTime" ] = time.time() + protime * 60
		
	def onTongCityWarEnd( self ):
		"""
		defined method.
		����ս��
		"""
		if BigWorld.globalData.has_key( "CityWarOverTime" ):
			del BigWorld.globalData[ "CityWarOverTime" ]
		
		DEBUG_MSG( "tigger citywar over event!" )
		for cityName, item in self.tongCityWarFightInfos.infos.iteritems():
			self.closeCityWarRooms( cityName )
		
		self.addTimerEx( TIME_USER_ARG_CLOSE_WAR_PROGRESS, 0, self.onTimerCloseCityWar, [ 1, ] )
		
		if self.cityWarCurrentStage == CITY_WAR_STAGE_UNDERWAY_FINAL: # ��������
			self.cityWarCurrentStage = CITY_WAR_STAGE_FREE
			self.rewardJoin()
			for tongEntity in self._tongEntitys.itervalues():
				tongEntity.onNotifyTongCityWarEnd()
		else:
			self.cityWarCurrentStage = CITY_WAR_STAGE_UNDERWAY_FREE
		
		self.popTimerEx( TIME_USER_ARG_FINAL_WAR )
		self.popTimerEx( TIME_USER_ARG_PRE_WAR )
		
			
	def onTimerCloseCityWar( self, re ):
		# define method. 
		# cityName: ������У� tongDBID�� ��ʤ���
		# �������������ñ�������ʤ��
		re += 1
		isAllOver = True
		for cityName, roundFights in self.tongCityWarFightInfos.infos.iteritems():
			if re > 3:
				roundFights.onTimerCloseWar( self )
				continue
				
			if not roundFights.isAllWarOver():
				isAllOver = False
		
		if not isAllOver:
			self.addTimerEx( TIME_USER_ARG_CLOSE_WAR_PROGRESS, 0, self.onTimerCloseCityWar, [ re, ] )
		else:
			for fights in self.tongCityWarFightInfos.infos.itervalues():
				fights.initRoundWar( fights.currentRound + 1 )
				
			self.writeToDB()
	
	def closeCityWarRooms( self, cityName ):
		"""
		�ر�ĳ����ս�ķ���
		"""
		domains = self.getAllCityWarDomain()
		for d in domains:
			d.closeCityWarRoom( cityName )
	
	def setCityNewMaster( self, cityName, tongDBID ):
		"""
		���ó��е�������
		oldCityMasterTongDBID: -1 
			��ʾ��ȷ���Ƿ���ԭ��������Ҫ��������ڲ�����
		"""
		t = 0
		oldCityMasterTongDBID = -1
		for infos in self.tongCityRecords:
			if infos[ "spaceName" ] == cityName:
				for info in infos[ "tongInfos" ]:
					if info["date"] > t:
						t = info["date"]
						oldCityMasterTongDBID = info["tongDBID"]

		DEBUG_MSG( "set City master:%s  %i %i" % ( cityName, tongDBID, oldCityMasterTongDBID ) )
		try:
			chiefName = self._tongBaseDatas[ tongDBID ][ "chiefName" ]
		except:
			chiefName = cschannel_msgs.TONGCITYWAR_VOICE_9 % tongDBID
		
		tongName = self.getTongNameByDBID( tongDBID )
		isFind = False
		d = { "tongDBID" : tongDBID, "tongName" : tongName, "chiefName" : chiefName, "date" : int( time.time() ) }
		for infos in self.tongCityRecords:
			if infos[ "spaceName" ] == cityName:
				infos[ "tongInfos" ].append( d )
				isFind = True
				break

		if not isFind:
			self.tongCityRecords.append( { "spaceName" : cityName, "tongInfos" : [ d ] } )
				
		if tongDBID != oldCityMasterTongDBID:
			tongEntity = self.findTong( oldCityMasterTongDBID )
			if tongEntity:
				tongEntity.setHoldCity("", False)

		self.registerToCityManager( tongDBID, cityName, False )
		# ���ó�������˰
		self.updateNewCityRevenueInfo( cityName )
		DEBUG_MSG( "success set to city master[%s] new master[%i]." % ( cityName, tongDBID ) )

		cityNameWord = csconst.TONG_CITYWAR_CITY_MAPS.get( cityName, "test" )
		self.onWarMessage( tongDBID, csstatus.TONG_CITY_WAR_FINAL_WIN, cityNameWord )
		tempString = cschannel_msgs.BCT_CITY_WAR_FINAL_RESULT_NOTIFY % ( tongName, cityNameWord, tongName )
		
		# ���������Ϣ
		self.findTong( tongDBID ).queryTongChiefInfos()
		
		try:
			g_logger.tongCityWarSetMasterLog( tongDBID, tongName, cityName )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
			
		self.writeToDB()
	
	def cityWarSetResult( self, cityName, winner, failure ):
		# define method.
		# ����һ��������ʤ����
		self.tongCityWarFightInfos[ cityName ].setWinner( self, winner, failure )
		g_logger.actResultLog( csdefine.ACTIVITY_TONG_DUO_CHENG, cityName, winner, failure, self.tongCityWarFightInfos[ cityName ].getRound() )
	
	def cityWarCheckFull( self, tongDBID ):
		# ���ð����������Ƿ�����
		if self.cityWarEnter.has_key( tongDBID ):
			if self.cityWarCurrentStage != CITY_WAR_STAGE_UNDERWAY_FINAL: # ���Ǿ���
				return len( self.cityWarEnter ) >= CITY_WAR_MAX_ENTER
			else:
				cityName = self.tongCityWarFightInfos.getJoinCityName( tongDBID )
				if self.tongCityWarFightInfos[ cityName ].getMaster(): # �г���
					if tongDBID == self.tongCityWarFightInfos[ cityName ].getMaster():
						return len( self.cityWarEnter ) >= CITY_WAR_FINAL_MAX_ENTER_MASTER # �سǷ�
					else:
						return len( self.cityWarEnter ) >= CITY_WAR_FINAL_MAX_ENTER_HAS_MASTER
				else:
					return len( self.cityWarEnter ) >= CITY_WAR_FINAL_MAX_ENTER_NOT_MASTER
		else:
			return False
	
	def cityWarAddEnter( self, tongDBID, playerDBID ):
		if self.cityWarEnter.has_key( tongDBID ):
			if playerDBID not in self.cityWarEnter[ tongDBID ]:
				self.cityWarEnter[ tongDBID ].append( playerDBID )
		else:
			self.cityWarEnter[ tongDBID ] = [ playerDBID, ]
		
	def cityWarLeave( self, tongDBID, playerDBID ):
		# define method
		# ����뿪��ս
		if self.cityWarEnter.has_key( tongDBID ):
			if playerDBID in self.cityWarEnter[ tongDBID ]:
				self.cityWarEnter[ tongDBID ].remove( playerDBID )
	
	def cityWarOnQueryMasterInfo( self, tongDBID, masterInfo ):
		# define method
		# �ص���ѯ������Ϣ
		self.tongCityWarFightInfos.setMasterChiefInfo( tongDBID, masterInfo )
		self.writeToDB()
	
	def cityWarDelMaster( self, cityNameCN ):
		# define method.
		# ɾ��һ�����еĳ��� for GM
		cityName = ""
		for key, value in csconst.TONG_CITYWAR_CITY_MAPS.iteritems():
			if cityNameCN == value:
				cityName = key
		
		if self.tongCityWarFightInfos.infos.has_key( cityName ):
			masterDBID = self.tongCityWarFightInfos[ cityName ].getMaster()
			tongMB = self.findTong( masterDBID )
			tongName = self.getTongNameByDBID( masterDBID )
			if tongMB:
				tongMB.setHoldCity("", False)
				tongMB.onStatusMessage( csstatus.TONG_CITY_WAR_ABANDON_HOLD_CITY, str(( cityNameCN, )) )
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_ABANDON_HOLD_CITY%( tongName, cityNameCN ), [] )
			self.tongCityWarFightInfos[ cityName ].delCityMaster()
			self.registerToCityManager( 0, cityName, False )
			self.writeToDB()
	
	def cityWarRegisterMasterSpawnPoint( self, cityName, mailbox ):
		# define method
		# ����ˢ�µ�ע��
		if self.tongCityWarFightInfos.infos.has_key( cityName ):
			self.tongCityWarFightInfos[ cityName ].addSpawnMaster( mailbox )
	
	# -----------------------------------------------------
	# time callback
	# -----------------------------------------------------
	def onTimerCityWarWillSignUp( self, notifyTime = TIME_NOTIFY_WILL_SIGNUP_LONG ):
		# ��ս��Ҫ����ʱ�����ͨ��
		if self.cityWarCurrentStage > CITY_WAR_STAGE_NOTIFY:
			return
			
		self.cityWarCurrentStage = CITY_WAR_STAGE_NOTIFY
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_WILL_SIGNUP_NOTIFY % ( notifyTime, ), [] )
		if notifyTime == 1:
			self.cityWarCurrentStage = CITY_WAR_STAGE_UNDERWAY_FREE
			return
			
		nextTime = notifyTime - TIME_NOTIFY_WILL_SIGNUP
		if nextTime <= 0:
			self.addTimerEx( TIME_USER_ARG_NOTIFY_WILL_SIGNUP, ( TIME_NOTIFY_WILL_SIGNUP -1 ) * 60, self.onTimerCityWarWillSignUp, [ 1, ] )
		else:
			self.addTimerEx( TIME_USER_ARG_NOTIFY_WILL_SIGNUP, TIME_NOTIFY_WILL_SIGNUP * 60, self.onTimerCityWarWillSignUp, [ nextTime, ] )
			
	def onTimerCityWarSignUp( self, notifyTime = TIME_NOTIFY_SIGNUP_LONG ):
		# ������ʼ
		if self.cityWarCurrentStage != CITY_WAR_STAGE_SIGNUP:
			return
		
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_SIGNUP_NOTIFY % ( notifyTime, ), [] )
		if notifyTime == 1:
			return
		
		nextTime = notifyTime - TIME_NOTIFY_SIGNUP
		if nextTime <= 0:
			self.addTimerEx( TIME_USER_ARG_NOTIFY_SIGNUP, ( TIME_NOTIFY_SIGNUP-1 )*60, self.onTimerCityWarSignUp, [ 1, ] )
		else:
			self.addTimerEx( TIME_USER_ARG_NOTIFY_SIGNUP, TIME_NOTIFY_SIGNUP * 60, self.onTimerCityWarSignUp, [ nextTime, ]  )
	
	def onTimer( self, timerID, cbID ):
		TimeControl.onTimer( self, timerID, cbID )
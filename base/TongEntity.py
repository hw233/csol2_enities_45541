# -*- coding: gb18030 -*-
#
# $Id: TongEntity.py,v 1.22 2008-08-25 09:30:09 kebiao Exp $
"""
���ͼ���Ŀ�ܺͲ���������ͬ����û�����ϵ�һ��2��ϵͳǣ����ԽСԽ��
��ᣬ����ϵͳ֧�ֶ�̬���أ������첽����ģʽ���༭�����޸ĸù��ܵ�ʱ��
���뿼������2��ģʽ�ķ����Ե��µ�һЩ����.
written by kebiao, in 2008/06/23
"""

import time
import cschannel_msgs
import ShareTexts as ST
import items
import sys
import copy
import BigWorld
import csdefine
import csstatus
import csconst
import Love3
import time
import Define
import Const
import Function
import SkillLoader
import random
import math
import cPickle
from bwdebug import *
from MsgLogger import g_logger
from Message_logger import *
from Function import Functor
from interface.TongStorage import TongStorage
from interface.TongCampaign import TongCampaign
from interface.TongTerritory import TongTerritory
from interface.TongCityWarInterface import TongCityWarInterface
from interface.TongRobWarInterface import TongRobWarInterface
from csdefine import NONE_STATUS,LUNARHALO,SUNSHINE,STARLIGHT

from Love3 import g_tongItems
from Love3 import g_tongSpecItems
from TongCityWarFightInfos import MasterChiefData
from LevelEXP import TongLevelEXP as TLevelEXP

TIME_CBID_CHECK_REQUEST_JOIN			= 1			# timeID����������tong�����ݣ� �ж���û�й�ʱ������ ��������
CONST_REQUEST_JOIN_TIMEOUT				= 60		# �������tong����ʱ��ʱ��
CONST_CHIEF_CONJURE_TIMEOUT				= 30		# �ӳ�������Ӧ��ʱʱ��
CONST_CONTRIBUTE_INIT_VAL				= 100		# ÿ������Ա�ս�����ʱ�ĳ�ʼ���ﹱ
TEMP_DATA_OVERTIME_INTERVAL				= 2			# ��ʱ���ݹ���ʱ��
COMPETITION_LEVEL_LIMIT					= 60		# �μӰ�Ὰ���ĳ�Ա�ȼ�����
COMPETITION_MEMBER_LIMIT				= 1			# �μӰ�Ὰ���İ�������������

# �첽���ݴ�����
TASK_KEY_MEMBER_DATA					= 1			# �����Ա����
TASK_KEY_PERSTIGE_DATA					= 2			# ������������
TASK_KEY_AFFICHE_DATA					= 3			# ����������
TASK_KEY_MONEY_DATA						= 4			# �����Ǯ����
TASK_KEY_LEVEL_DATA						= 5			# ����������
TASK_KEY_LEAGUES_DATA					= 8			# ������ͬ������
TASK_KEY_DUTY_NAMES_DATA				= 9			# ������ְλ��������
TASK_KEY_HOLD_CITY_DATA					= 11		# �����������Ƶĳ�������
TASK_KEY_TONG_SIGN_MD5					= 17		# �����MD5��Ϣ
TASK_KEY_TONG_EXP						= 18		# ��ᾭ��
TASK_KEY_TONG_SKILL						= 19		# ��Ἴ��
TASK_KEY_BATTLE_LEAGUES_DATA			= 20		# ������ս��ͬ������

TONG_NORMAL_QUEST_MAX_MAP = { 1:60, 2:120, 3:180, 4:240, 5:300, 6:360, 7:420, 8:480, 9:540, 10: 600 }		# ��ͬ�ȼ��İ��������ɵ��ճ��������
TONG_MERCHANT_QUEST_MAX_MAP = { 1:3, 2:4, 3:5, 4:5, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10 }        		# ���������а��ȼ��жԸ����������������

OLD_GRADE_MAPPING = { 0x00000001:1, 0x00000010: 2, 0x00000040:3, 0x00000080: 4 ,}

class MemberInfos:
	"""
	�����г�Ա��һЩ��Ϣ�ṹ
	"""
	def __init__( self ):
		"""
		��ʼ����Ա��Ϣ
		"""
		self._isOnline = False					# �ó�Ա�Ƿ�����
		self._name = ""							# �ó�Ա������
		self._grade = 0							# �ó�Ա�İ��Ȩ��
		self._class = 0							# �ó�Ա��ְҵ
		self._level = 0							# �ó�Ա�ļ���
		self._spaceID = 0						# �ó�Ա����spaceλ��
		self._lastPosition = ( 0, 0, 0 )		# �ó�Ա���һ�β�ѯ����λ��
		self._reinstateGrade = 0				# ��������ְ
		self._entityBaseMailbox = None			# �ó�Ա��baseMailbox
		self._scholium = ''						# �ó�Ա����ע
		self._contribute = 0					# �ó�Ա��ṱ�׶�
		self._totalContribute = 0				# �ó�Ա����ۻ����׶�
		
		self._lastWeekTotalContribute = 0		# �ó�Ա���ܰ���ۼưﹱֵ
		self._lastWeekSalaryReceived = 0		# �ó�Ա������ȡٺ»ֵ
		self._weekTongContribute = 0 			# �ó�Ա���ܻ�ȡ�ﹱֵ
		self._weekSalaryReceived = 0			# �ó�Ա������ȡٺ»ֵ

	def init( self, name, grade, eclass, level ):
		"""
		��ʽ�ĳ�ʼ����������
		"""
		self._name = name
		self._grade = grade
		self._class = eclass
		self._level = level

	def setReinstateGrade( self, grade ):
		self._reinstateGrade = grade

	def isOnline( self ):
		return self._isOnline

	def getName( self ):
		return self._name

	def getGrade( self ):
		return self._grade

	def getClass( self ):
		return self._class

	def getLevel( self ):
		return self._level

	def getBaseMailbox( self ):
		return self._entityBaseMailbox

	def getSpaceID( self ):
		return self._spaceID

	def getPosition( self ):
		return self._lastPosition

	def getScholium( self ):
		return self._scholium

	def getContribute( self ):
		return self._contribute

	def getTotalContribute( self ):
		return self._totalContribute

	def updateTotalContribute( self, val ):
		self._totalContribute = val

	def addTotalContribute( self, val ):
		self._totalContribute += val

	def setOnlineState( self, online ):
		"""
		��������״̬
		@param online: bool, ���߻��߲�����
		"""
		self._isOnline = online

	def setBaseMailbox( self, e ):
		"""
		���øó�Ա��baseMailbox
		@param e: entity or None
		"""
		if e == None and self.isOnline():
			ERROR_MSG( "member is online, entityMB set to None..." )
		self._entityBaseMailbox = e
		if self._entityBaseMailbox and self.isOnline():
			if self._reinstateGrade != 0 and self._grade != self._reinstateGrade:
				self._entityBaseMailbox.tong_setGrade( self._reinstateGrade )
				self._reinstateGrade = 0

	def setGrade( self, grade ):
		self._grade = grade

	def setLevel( self, level ):
		self._level = level

	def setPosition( self, pos ):
		self._lastPosition = pos

	def setSpaceID( self, spaceID ):
		self._spaceID = spaceID

	def setScholium( self, scholium ):
		self._scholium = scholium

	def setContribute( self, contribute ):
		self._contribute = contribute

	def setName( self, name ):
		self._name = name
	
	def setLastWeekTotalContribute( self, lastWeekTotalContribute ):
		self._lastWeekTotalContribute = lastWeekTotalContribute
		
	def getLastWeekTotalContribute( self ):
		return self._lastWeekTotalContribute
		
	def setLastWeekSalaryReceived( self, lastWeekSalaryReceived ):
		self._lastWeekSalaryReceived = lastWeekSalaryReceived
		
	def getLastWeekSalaryReceived( self ):
		return self._lastWeekSalaryReceived
		
	def updateWeekTongContribute( self, weekTongContribute ):
		self._weekTongContribute = weekTongContribute
		
	def addWeekTongContribute( self, val ):
		self._weekTongContribute += val
		
	def getWeekTongContribute( self ):
		return self._weekTongContribute
		
	def setWeekSalaryReceived( self, weekSalaryReceived ):
		self._weekSalaryReceived = weekSalaryReceived
		
	def getWeekSalaryReceived( self ):
		return self._weekSalaryReceived

class TongEntity(	BigWorld.Base,
					TongTerritory,
					TongCampaign,
					TongStorage,
					TongRobWarInterface,
					TongCityWarInterface
):
	"""
	���entity ������ݴ������ģ�ά��һ�а�����.
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		TongTerritory.__init__( self )
		TongCampaign.__init__( self )
		TongStorage.__init__( self )
		TongCityWarInterface.__init__( self )
		TongRobWarInterface.__init__( self )
		
		self._onlineMemberDBID = set([])
		self._requestJoinEntityList = {} 					# {������dbid:��������DBID:��������basemailbox}
		self._check_RequestJoinTimerID = 0					# ����������tong�����ݣ� �ж���û�й�ʱ������ ��������
		self._requestLeagueRecord = {} 						# {��������tongDBID}
		self._check_RequestLeagueTimerID = 0				# ����������ͬ��tong�����ݣ� �ж���û�й�ʱ������ ��������
		self._memberInfos = {}								# ��Ա�Ŀ�����Ϣ
		self._delayDataTasks = {}							# {memberDBID:[oterMemberDBID,...]}������ҿͻ��˳�ʼ����Ϣһ���Է����������������������������Ҫ�첽���ݷ��ͣ���ô��Ϣ����Ҫ�ŵ�һ������ȥ�����ĸ��ͻ���
		self._chiefCommandInfo = {}							# �����������Ϣ
		self._check_conjureTimerID	=	0					# ������������
		self._check_payChiefMoney_timerID = 0				# �������ʷ��ż��ʱ��timer
		self._startupTimerID = 0							# startup���̸�Ϊ��һ��timer�������� ������tongentity��ʼ�����̵��ã�һЩ��ɢ���ƵĲ���������⡣
		self._afterFeteTimerID = 0							# ����ȡ��������������õ�״̬
		self.basePrestige = 0								# ��ᱣ������
		self.destroyTimerID = 0								# �������timer

		self.chiefDBID = 0						# ����dbid
		self.chiefName = ""						# ��������

		# ������ң������Ҳ����ߣ���ôֱ�Ӳ������ݿ⣬�����Ұ�����ݣ����������ߣ���Ҫ�����cell��ʼ�������ݣ��������cell����������
		# ����ָ����п������cell entity�Ѿ����٣���timer����һ�������Ƿ�ɹ��ļ�⣬������ں���ҵ�����û�б��������ô������ҿ����Ѿ����٣����߷�����ͨ�ų������⡣
		# ���ﲻ���Ƿ�����ͨ�Ż�Ӳ�����⣬��������ɿ�����100%�ģ���������������û������ɹ�����ô�������entity�Ѿ����ٴ���ֱ������������ݿ��еİ�����ݡ�11:34 2010-11-6��wsf
		# �˻���ͬ��Ӧ������Ҽ��������ʱ��������
		self.tempDataCheckTimer = 0
		self.kickMemberTempInfo = {}	# ��ﴦ���е��������
		self.joinMemberTempInfo = {}	# ��ﴦ���е��������
		self.gradeChangeTempData = {}	# ���Ȩ�޸ı䴦���е��������

		## ��Ӱ�����ָ��������ٶȵĿ��ƴ�ʩ���ṩ��������Щָ�������ٶȵ����� ##
		# ������Щ������Ӧ���ɶ�ʱ���������ӵĸ�����Ӧָ���У���Ϊ�ٷֱȲ������
		# by mushuang
		# �μ���CSOL-9750
		#self._afterFeteStatus = NONE_STATUS # ���������֮���õ�״̬, persistent ����
		
		self.tongAbaGatherFlag = None
		self.tongAbaRound = 0

		self.tongCompetitionGatherFlag = None

		# �㲥һЩ�������
		self.onBroadcastData()
		
		# ս������
		self._inviteBattleLeagueRecord = {} 						# {��������tongDBID}
		self._check_inviteBattleLeagueTimerID = 0					# ����������ͬ��tong�����ݣ� �ж���û�й�ʱ������ ��������
		
		# �������г�Ա����Ϣ ��һ�δ�����ʱ�������isCreate���
		if not self.queryTemp( "isCreate", False ):
			BigWorld.globalData[ "tong.%i" % self.databaseID ] = self
			self.loadMemberInfoFromDB()
		else:
			self.writeToDB( self.onCreatedTongCallBack )


	def onCreatedTongCallBack( self, success, tongEntity ):
		"""
		���ʵ��д�����ݿ�ص�
		"""
		if not success:
			ERROR_MSG( "creator %s TongEntity %s writeToDB is failed!" % ( self.chiefName, self.playerName ) )
		else:
			self._startupTimerID = self.addTimer( 0.01, 0, 0 )
			self.creatorInfo["baseMailbox"].cell.tong_createSuccess( self.databaseID, self )

	def createSuccess( self ):
		"""
		Define method.
		��ᴴ���ɹ�

		self.creatorInfo Ϊ�������entityʱ�����һ����ʱ����
		like as:
		creatorInfo = { "databaseID":creatorDBID, \
						"playerName":creatorName, \
						"level":creatorLevel, \
						"raceclass":creatorRaceclass, \
						"baseMailbox":creator, \
						}
		"""
		creatorName = self.creatorInfo["playerName"]
		creatorDBID = self.creatorInfo["databaseID"]
		creatorRaceclass = self.creatorInfo["raceclass"]
		creatorLevel = self.creatorInfo["level"]
		creatorBase = self.creatorInfo["baseMailbox"]
		
		self.camp = ( creatorRaceclass & csdefine.RCMASK_CAMP ) >> 20
		self.chiefDBID = creatorDBID
		self.chiefName = creatorName
		self.dutyNames = copy.deepcopy( Const.TONG_DUTY_NAME )
		self.saveChiefdate = int( time.time() )
		self.initTongItems()
		self.initTongSpecialItems()

		INFO_MSG( "creator %s TongEntity %s writeToDB is successfully! " % ( creatorName, self.playerName ) )
		BigWorld.globalData[ "tong.%i" % self.databaseID ] = self
		BigWorld.globalBases["TongManager"].onRegisterTongOnCreated( creatorDBID, self, self.playerName, self.databaseID, self.chiefName, self.camp )
		# �Ѵ��������ݼ�����
		creatorBase.tong_onJoin( self.databaseID, csdefine.TONG_DUTY_CHIEF, self )

		# ������ݼ�������Ҫ��onRegisterTongOnCreatedע�ᵽ��������֮����Ϊ������Һ�����°�����ݵ�����������ʱ���뱣֤����ڹ��������Ѿ�ע��
		self.onJoin( creatorDBID, creatorName, creatorLevel, creatorRaceclass, creatorBase, csdefine.TONG_DUTY_CHIEF, csconst.JOIN_TONG_CHIEF_INIT_CONTRIBUTE )
		self.calBasePrestige()
		creatorBase.client.tong_onCreateSuccessfully( self.databaseID, self.playerName )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHGL_TONG_ESTABLISH_NOTIFY % ( creatorName, self.playerName ), [] )

	def getTongManager( self ):
		return BigWorld.globalBases["TongManager"]

	def getMailMgr( self ):
		return BigWorld.globalData[ "MailMgr" ]

	def getMemberInfos( self, memberDBID ):
		return self._memberInfos[ memberDBID ]

	def getNameAndID( self ):
		"""
		��ȡ�������ƺ�DBID
		"""
		return self.playerName + "(%s)" % self.databaseID

	def getName( self ):
		return self.playerName
	
	def getCamp( self ):
		return self.camp

	#------------------------------------------------------------------------------------------
	def onBroadcastData( self ):
		"""
		�㲥���ݱ��ı� ��Ҫ���ṩ����ɫ��½�� һЩ��Ҫ������Ҫ��������cellData��
		"""
		key = "tong.%i" % self.databaseID
		if not BigWorld.baseAppData.has_key( key ):
			BigWorld.baseAppData[ key ] = {}

		baseAppData = BigWorld.baseAppData[ key ]
		baseAppData[ "level" ] = self.level
		BigWorld.baseAppData[ key ] = baseAppData

	#------------------------------------------------------------------------------------------
	def queryTemp( self, key, default = None ):
		"""
		���ݹؼ��ֲ�ѯ��ʱmapping����֮��Ӧ��ֵ

		@return: ����ؼ��ֲ������򷵻�defaultֵ
		"""
		try:
			return self.tempMapping[key]
		except KeyError:
			return default

	def setTemp( self, key, value ):
		"""
		define method.
		��һ��key��дһ��ֵ

		@param   key: �κ�PYTHONԭ����(����ʹ���ַ���)
		@param value: �κ�PYTHONԭ����(����ʹ�����ֻ��ַ���)
		"""
		self.tempMapping[key] = value

	def popTemp( self, key, default = None ):
		"""
		�Ƴ�������һ����key���Ӧ��ֵ
		"""
		return self.tempMapping.pop( key, default )

	def removeTemp( self, key ):
		"""
		define method.
		�Ƴ�һ����key���Ӧ��ֵ
		@param   key: �κ�PYTHONԭ����(����ʹ���ַ���)
		"""
		self.tempMapping.pop( key, None )

	#------------------------------------------------------------------------------------------
	def addMemberInfos( self, memberDBID, memberInfo ):
		"""
		����Ϣ����Ӹó�Ա�Ŀ�����Ϣ
		"""
		self._memberInfos[ memberDBID ] = memberInfo
		self.addMemberTotalContributeRecord( memberDBID, memberInfo.getContribute() )

	def createMemberInfo( self, mDBID, mName, mLevel, mClass, \
						mBaseMailbox, mgrade, scholium, contribute ):
		"""
		��������Ա��Ϣʵ��
		"""
		infos = MemberInfos()
		infos.init( mName, mgrade, mClass, mLevel )
		infos.setOnlineState( mBaseMailbox is not None )
		infos.setBaseMailbox( mBaseMailbox )
		infos.setScholium( scholium )
		infos.setContribute( contribute )
		return infos

	def addMember( self, memberDBID, memberInfo ):
		"""
		�����°���Ա
		"""
		self._memberInfos[ memberDBID ] = memberInfo
		self.addMemberTotalContributeRecord( memberDBID, memberInfo.getContribute() )
		self.onMemberCountChanged()
		try:
			g_logger.tongMemberAddLog( self.databaseID, self.getName(), memberDBID, memberInfo.getName(), len(self._memberInfos) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def removeMember( self, playerDIBD ):
		"""
		�Ƴ�һ����Ա
		"""
		try:
			playerName = self._memberInfos.pop( playerDIBD )
		except KeyError:
			ERROR_MSG( "cannot find tong memeber( %i )" % playerDBID )
		if self.inDestroy():
			DEBUG_MSG( "tongEntity( %i ) is destroying..." % self.databaseID )
			return
		self.onMemberCountChanged()
		try:
			g_logger.tongMemberRemoveLog( self.databaseID, self.getName(), playerDIBD, playerName,len(self._memberInfos) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
			
	def hasMember( self, playerDIBD ):
		return playerDIBD in self._memberInfos

	def onMemberCountChanged( self ):
		"""
		��Ա�����иı�
		"""
		self.memberCount = len( self._memberInfos )
		self.calPrestige()			# ����Ա�����仯���𱣵������仯
		# �����ݸ��µ�������
		self.getTongManager().updateTongMemberCount( self.databaseID, self.memberCount )

	#------------------------------------------------------------------------------------------
	def updateTotalContributeToMemberInfos( self ):
		"""
		ͬ�����˰���ۻ����׶ȵ���Ա��Ϣ�ṹ��(һ��ֻ��Ҫ������֮������غ����һ�β���)
		"""
		for memberDBID, memberInfo in self._memberInfos.iteritems():
			for item in self.memberTotalContributes:
				if item[ "dbID" ] == memberDBID:
					memberInfo.updateTotalContribute( item[ "totalContribute" ] )
					memberInfo.setLastWeekTotalContribute( item[ "lastWeekTotalContribute" ])
					memberInfo.setLastWeekSalaryReceived( item[ "lastWeekSalaryReceived" ])
					memberInfo.updateWeekTongContribute( item[ "weekTongContribute" ])
					memberInfo.setWeekSalaryReceived( item[ "weekSalaryReceived" ])
					continue 

	def addMemberTotalContributeRecord( self, memberDBID, val ):
		"""
		��¼�����ۻ��ﹱ�� ���Ͱﹱ���ǲ����м�¼�� ֻ��¼���Ӱﹱ
		"""
		info = self.getMemberInfos( memberDBID )
		if val <= 0:
			return info.getTotalContribute()

		# ͬ������Ա��Ϣ�ṹ��
		info.addTotalContribute( val )
		info.addWeekTongContribute( val )			# ���˱��ܰﹱ�ۼ�
		self.weekTongTotalContribute += val			# ��᱾�ܰﹱ�ۼ�
		
		for item in self.memberTotalContributes:
			if item[ "dbID" ] == memberDBID:
				item[ "totalContribute" ] += val
				item[ "weekTongContribute"] += val
				return item[ "totalContribute" ]
				
		# �����û��¼������һ��
		self.memberTotalContributes.append( { "dbID" : memberDBID, "totalContribute" : val, "weekTongContribute": val, "weekSalaryReceived": 0, "lastWeekTotalContribute": 0, "lastWeekSalaryReceived": 0 } )
		return val

	def removeMemberTotalContributeRecord( self, memberDBID ):
		"""
		ɾ����Ա���ۻ��ﹱ��¼
		"""
		for item in self.memberTotalContributes:
			if item[ "dbID" ] == memberDBID:
				self.memberTotalContributes.remove( item )
				return

	#------------------------------------------------------------------------------------------
	def onDestroy( self ):
		"""
		�����ٵ�ʱ����������
		"""
		self.save()

	#------------------------------------------------------------------------------------------
	def save( self ):
		"""
		��������Ҫ����
		"""
		self.writeToDB()

	#------------------------------------------------------------------------------------------
	def loadMemberInfoFromDB( self ):
		"""
		�����ݿ���س�Ա��Ϣ
		"""
		cmd = "select id, sm_tong_grade, sm_tong_scholium, sm_playerName, sm_level, sm_raceclass, tbl_Role.sm_tong_contribute from tbl_Role where %i = tbl_Role.sm_tong_dbID;" % self.databaseID
		BigWorld.executeRawDatabaseCommand( cmd, self.loadMemberInfoFromDB_Callback )

	def loadMemberInfoFromDB_Callback( self, results, dummy, error ):
		"""
		���س�Ա��Ϣ ���ݿ�ص�
		"""
		if (error):
			ERROR_MSG( error )
			return

		if len( results ) <= 0:
			# �������ԭ�������ĳ��ɾ�����ʺ�
			DEBUG_MSG( "tong %s:%i can't found all member!" % ( self.playerName, self.databaseID ) )
		else:
			for result in results:
				entityDBID				= int( result[0] )
				tongGrade				= int( result[1] )
				tongScholium 			= result[2]
				mName					= result[3]
				mLevel					= int( result[4] )
				mClass					= int( result[5] )
				tongContribute			= int( result[6] )
				if tongGrade not in csdefine.TONG_DUTYS:
					if tongGrade in OLD_GRADE_MAPPING.keys():
						tongGrade = OLD_GRADE_MAPPING[ tongGrade ]
					else:
						tongGrade = csdefine.TONG_DUTY_MEMBER
				memberInfo = self.createMemberInfo( entityDBID, mName, mLevel, mClass, None, tongGrade, tongScholium, tongContribute )
				self.addMemberInfos( entityDBID, memberInfo )

				if tongGrade == csdefine.TONG_DUTY_CHIEF:
					self.chiefDBID = entityDBID
					self.chiefName = mName

		# ֪ͨmanager������� ��һЩ����.
		self.getTongManager().onTongEntityLoadMemberInfoComplete( self.databaseID, self, self.chiefName )
		# ����һ�°���Ա����
		self.memberCount = len( self._memberInfos )
		# ���������������
		self._startupTimerID = self.addTimer( 0.01, 0, 0 )

	def removeMemberFromDB( self, memberDBID ):
		"""
		�����ݿ���ɾ��ĳ��Ա�İ����Ϣ
		"""
		cmd = "update tbl_Role set sm_tong_dbID=0, sm_tong_grade=0, tbl_Role.sm_tong_scholium=\'\', tbl_Role.sm_tong_contribute=0 where %i = tbl_Role.id;" % memberDBID
		BigWorld.executeRawDatabaseCommand( cmd, self.removeMemberFromDB_Callback )

	def removeMemberFromDB_Callback( self, result, dummy, error ):
		"""
		ɾ����Ա��Ϣ ���ݿ�ص�
		"""
		if (error):
			ERROR_MSG( error )
			return

	#------------------------------------------------------------------------------------------
	def onTongStartup( self ):
		"""
		���ϵͳ����(ͨ����ϵͳ���������˰��entity,�������������ݺ�)
		"""
		# ÿ������һ�� �������ʷ������
		self._check_payChiefMoney_timerID = self.addTimer( ( 60 - time.localtime()[4] ) * 60, 60 * 60, 0 )
		# ͬ�����˰���ۻ����׶ȵ���Ա��Ϣ�ṹ��
		self.updateTotalContributeToMemberInfos()
		# ��ʼ����������ɺ�����õ�״̬
		self.__initAfterFeteStatus()

	#---------------------------------------------------------------------------------------------------------
	def setTID( self, tid ):
		"""
		define method.
		���ð��ID
		"""
		self.tid = tid
		self.save()

	def getTID( self ):
		"""
		��ȡ���ID
		"""
		return self.tid

	def setAD( self, ad ):
		"""
		define method.
		���ð��ID
		"""
		self.ad = ad
		self.save()
		chiefMailBox = self.getMemberInfos( self.chiefDBID ).getBaseMailbox() #������mailbox
		self.statusMessage( chiefMailBox, csstatus.TONG_AD_FINISHED )


	def initTongIDAndAD( self, tid, ad ):
		"""
		define method.
		�����Խӿڣ�  ��tid�͹����Ϣ��tongmanagerת�Ƶ��������� �°汾
		tongmanager���ٱ�����Щ��Ϣ�� �����ݿ���tong_entity���ʼ����
		"""
		self.setTID( tid )
		self.ad = ad

	#---------------------------------------------------------------------------------------------------------
	def clearMemberInfo( self, memberDBID ):
		"""
		�������Ա������
		"""
		# ɾ�������ۻ��ﹱ��¼
		self.removeMemberTotalContributeRecord( memberDBID )
		# ɾ����������Ʒ��¼
		self.removeBuyTongItemRecord( memberDBID )
		# �����������߳�Ա�Ŀͻ��˵ĳ�Ա�б���ɾ���ó�Ա
		for dbid in self._onlineMemberDBID:
			if dbid != memberDBID:
				otherMember = self.getMemberInfos( dbid ).getBaseMailbox()

				# ����һ��ڶԷ������ݸ����б�����ô ������������ٸ��µ��ͻ��� ��������Է��Ŀͻ����ϵ���
				if self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
					self.delMemberFromDelayTaskMember( dbid, memberDBID )
				else:
					if hasattr( otherMember, "client" ):
						otherMember.client.tong_onDeleteMemberInfo( memberDBID )

				if memberDBID in self._onlineMemberDBID:
					if hasattr( otherMember, "cell" ):
						otherMember.cell.tong_onMemberRemoveOL( memberDBID )

		memberMailbox = self.getMemberInfos( memberDBID ).getBaseMailbox()
		if memberMailbox:	# �����Ա���ߣ���ô���������ݺ���������
			if self.isInDelayTaskList( memberDBID ):
				self.delDelayTaskMember( memberDBID )
			self._onlineMemberDBID.remove( memberDBID )

		self.removeMember( memberDBID )

	def memberLeave( self, memberDBID ):
		"""
		Define method.
		�������ʱ�뿪���Ĵ���

		@param memberDBID : �뿪�ĳ�ԱdatabaseID
		"""
		try:
			memberMailbox = self.getMemberInfos( memberDBID ).getBaseMailbox()
		except:
			return
		DEBUG_MSG( "member( %i ) leave tong " % ( memberDBID ) )
		if self.isJoinTongCityWar: # ��ս�ڼ䲻���˰��CSOL-11589
			self.statusMessage( memberMailbox, csstatus.TONG_CITY_WAR_CANNOT_QUIT )
			return
			
		memberMailbox.client.tong_onSetTongSignMD5( "tcbh" )
		memberMailbox.cell.tong_leave()
		memberMailbox.client.tong_meQuit()

		# ��������̨����
		if self.tongAbaGatherFlag:
			memberMailbox.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TONG_ABA )
		if self.tongAbaRound:
			memberMailbox.client.receiveAbaRound( 0 )
		
		if self.tongCompetitionGatherFlag:
			memberMailbox.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TONG_COMPETITION )
		
		# ����������
		self.clearMemberInfo( memberDBID )
		self.save()
		self.memberLeaveSuccess( memberDBID )

	def startTempDataCheck( self ):
		"""
		"""
		if not self.tempDataCheckTimer:	# ������ʱ���ݼ�����
			self.tempDataCheckTimer = self.addTimer( TEMP_DATA_OVERTIME_INTERVAL, TEMP_DATA_OVERTIME_INTERVAL, 0 )

	def endTempDataCheck( self ):
		"""
		"""
		if not self.tempDataCheckTimer or len( self.kickMemberTempInfo ) or len( self.joinMemberTempInfo ):
			return
		self.delTimer( self.tempDataCheckTimer )
		self.tempDataCheckTimer = 0

	def addMemberLeaveCheck( self, memberDBID ):
		"""
		����Ա�뿪��ᴦ������
		"""
		self.kickMemberTempInfo[memberDBID] = time.time()
		self.startTempDataCheck()

	def memberLeaveSuccess( self, memberDBID ):
		"""
		����뿪���ɹ�
		"""
		try:
			del self.kickMemberTempInfo[memberDBID]
		except KeyError:
			return
		self.endTempDataCheck()

	def onTempDataCheckTimerCheck( self ):
		"""
		"""
		try:		# ��׽��������ѭ��timer�е��쳣�������жϴ����޷�ֹͣtimer
			nowTime = time.time()
			for memberDBID, leaveTime in self.kickMemberTempInfo.items():
				if nowTime - leaveTime > TEMP_DATA_OVERTIME_INTERVAL:	# ����û����ɹ�
					del self.kickMemberTempInfo[memberDBID]
					self.clearMemberInfo( memberDBID )
					#self.removeMemberFromDB( memberDBID )				# ֱ�Ӵ����ݿ����Ƴ�
			for memberDBID, joinTime in self.joinMemberTempInfo.items():
				if nowTime - joinTime > TEMP_DATA_OVERTIME_INTERVAL:	# ����û���ɹ�
					del self.joinMemberTempInfo[memberDBID]
			for memberDBID, info in self.gradeChangeTempData.items():
				if nowTime - info[1] > TEMP_DATA_OVERTIME_INTERVAL:		# �������ò��ɹ�
					del self.gradeChangeTempData[memberDBID]
					self.updateGrade2DB( memberDBID, info[0] )			# ֱ���������ݿ�
		except:
			EXCEHOOK_MSG( "��׽��������ѭ��timer�е��쳣�������жϴ����޷�ֹͣtimer��" )
		if len( self.kickMemberTempInfo ) or len( self.joinMemberTempInfo ) or len( self.gradeChangeTempData ):
			return
		self.delTimer( self.tempDataCheckTimer )
		self.tempDataCheckTimer = 0

	def addChangeGradeChek( self, memberDBID, grade ):
		"""
		��������ʱ���ݼ���������
		"""
		self.gradeChangeTempData[memberDBID] = ( grade, time.time )
		self.startTempDataCheck()

	def changeGradeSuccess( self, memberDBID ):
		"""
		Define method.
		�ı���ҵİ��ְλ�ɹ�
		"""
		try:
			del self.gradeChangeTempData[memberDBID]
		except KeyError:
			return
		self.endTempDataCheck()

	def addMemberJoinCheck( self, memberDBID ):
		"""
		"""
		self.joinMemberTempInfo[memberDBID] = time.time()
		self.startTempDataCheck()

	def memberJoinSuccess( self, memberDBID ):
		"""
		"""
		try:
			del self.joinMemberTempInfo[memberDBID]
		except KeyError:
			return
		self.endTempDataCheck()

	#---------------------------------------------------------------------------------------------------------
	def canDismiss( self ):
		"""
		�Ƿ���Խ�ɢ���
		"""
		if len( self.joinMemberTempInfo ):	# ������ڴ������������ݣ����ܽ�ɢ���
			return False
		return True

	def onDismissTong( self, memberDBID, reason ):
		"""
		define method
		��ɢ���
		"""
		DEBUG_MSG( "chief dismiss of tong. %i, %s" % ( self.databaseID, self.playerName ) )
		if memberDBID > 0:
			info = self.getMemberInfos( memberDBID )
			if not self.checkMemberDutyRights( info.getGrade(), csdefine.TONG_RIGHT_DISMISS_TONG ):
				return
			
			if self.isJoinTongCityWar:
				self.statusMessage( info.getBaseMailbox(), csstatus.TONG_CITY_WAR_CANNOT_DISMISS )
				return
				
		if not self.canDismiss():	# �����ǰ���ʽ����Զ���ɢҲ����������������Ұ�������쳣����������һ���ʽ���ļ��
			DEBUG_MSG( "( %i )i am in member joining progress..." % self.databaseID )
			return
		if self.inDestroy():
			return
		self.setTongSignMD5( "" )
		self.resetMemberDelayTaskData()

		# �������Ա���ϵİ����Ϣ�� ������ǲɢ��
		for memberDBID, info in self._memberInfos.items():
			emb = self.getMemberInfos( memberDBID ).getBaseMailbox()
			if emb is None:	# ��Ҳ�����
				# ����������
				self.clearMemberInfo( memberDBID )
				#self.removeMemberFromDB( memberDBID )
			else:
				if hasattr( emb, "cell" ):
					emb.cell.tong_leave()
				if hasattr( emb, "client" ):
					emb.client.tong_onDismissTong()
				self.addMemberLeaveCheck( memberDBID )

		self.getTongManager().onTongDismiss( self.databaseID, reason )
		# ֪ͨͬ�˰�� ���ͬ��.
		for league in self.leagues:
			self.getTongManager().leagueDispose( league[ "dbID" ], self.databaseID )
		
		# ��ɢս��ͬ��
		for battleLeague in self.battleLeagues:
			self.getTongManager().battleLeagueAutoDispose( battleLeague[ "dbID" ], self.databaseID )

		self.destroyTimerID = self.addTimer( TEMP_DATA_OVERTIME_INTERVAL + 3 )	# ��ʱ���٣�����ɢ�������Ա�������ʱ���պ����ߣ���ô��Ҫ���entity�����ݿ��������

	def inDestroy( self ):
		"""
		"""
		return self.destroyTimerID != 0

	#---------------------------------------------------------------------------------------------------------
	def kickMember( self, kickerDBID, targetDBID ):
		"""
		Define method.
		������ҳ����

		@param kickerDBID : ����ִ�п�����Ϊ�����dbid
		@param targetDBID : �����󿪳������dbid
		"""
		if not self.hasMember( targetDBID ):
			HACK_MSG( "kicker(%i) request target(%i):there is no target info." % ( kickerDBID, targetDBID ) )
			return
		DEBUG_MSG( "kickerDBID=%i, targetDBID=%i" % ( kickerDBID, targetDBID ) )
		kickerInfo = self.getMemberInfos( kickerDBID )
		kickerGrade = kickerInfo.getGrade()
		if not self.checkMemberDutyRights( kickerGrade, csdefine.TONG_RIGHT_MEMBER_MANAGE ): # û�п���Ȩ��
			DEBUG_MSG( "(%i) dont have kick Permissions." % ( kickerDBID ) )
			self.statusMessage( kickerInfo.getBaseMailbox(), csstatus.TONG_CANT_KICK_NO_GRADE )
			return
		targetInfo = self.getMemberInfos( targetDBID )
		if targetInfo.getGrade() >= kickerGrade:				# ��ֻ�ܿ��������ְ����Լ��͵���ҡ�
			DEBUG_MSG( "(%i) cant kick tong chief(%i)." % ( kickerDBID, targetDBID ) )
			self.statusMessage( kickerInfo.getBaseMailbox(), csstatus.TONG_CANT_KICK_LOW_GRADE )
			return
		
		#if targetInfo.getGrade() == csdefine.TONG_GRADE_DEALER:	# ���ܿ������� û�����������ɫ
		#	self.statusMessage( kickerInfo.getBaseMailbox(), csstatus.TONG_CANT_KICK_CHAPMAN )
		#	return

		# ����ɾ������Ա����
		targetMailbox = targetInfo.getBaseMailbox()
		if targetMailbox is None:	# ��Ҳ�����
			# ����������
			self.clearMemberInfo( targetDBID )
			#self.removeMemberFromDB( targetDBID )
		else:
			targetMailbox.cell.tong_leave()
			self.addMemberLeaveCheck( targetDBID )
			self.statusMessage( targetMailbox, csstatus.TONG_BE_KICKED, kickerInfo.getName() )
		for dbid in self._onlineMemberDBID:
			if dbid == targetDBID:
				continue
			self.statusMessage( self.getMemberInfos( dbid ).getBaseMailbox(), csstatus.TONG_KICK_MEMBER, targetInfo.getName(), kickerInfo.getName() )

	#---------------------------------------------------------------------------------------------------------
	def onPrestigeChanged( self ):
		"""
		��������ı���
		"""
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.hasDelayTaskData( dbid, TASK_KEY_PERSTIGE_DATA ):
				emb.client.tong_onSetTongPrestige( self.prestige )
				emb.client.tong_onSetVariablePrestige( self.prestige - self.basePrestige )

		# �����ݸ��µ�������
		self.getTongManager().updateTongPrestige( self.databaseID, self.prestige )

	def addPrestige( self, prestige, reason ):
		"""
		define method.
		�������
		"""
		if prestige < 0:
			self.payPrestige( abs(prestige), reason )
		else:
			oldPrestige = self.prestige
			self.prestige += prestige
			try:
				g_logger.tongPrestigeChangeLog( self.databaseID, self.getName(), oldPrestige, self.prestige, reason )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			
		self.onPrestigeChanged()
		
	def payPrestige( self, val,reason ):
		"""
		֧������
		"""
		val = int( val )
		if val <= 0:
			return
		variablePrestige = self.prestige - self.basePrestige
		if variablePrestige < val:	# ���������СֵΪ��������
			val = variablePrestige
		oldPrestige = self.prestige
		self.prestige -= val
		self.onPrestigeChanged()
		
		try:
			g_logger.tongPrestigeChangeLog( self.databaseID, self.getName(), oldPrestige, self.prestige, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def calBasePrestige( self ):
		"""
		���㱣������
		"""
		memberCount = len( self._memberInfos )
		if memberCount == 0:	# û�а���Ա
			self.basePrestige = 0
			return
		totalLevel = 0
		for info in self._memberInfos.itervalues():
			totalLevel += info.getLevel()
		self.basePrestige = int( totalLevel / memberCount )

	def calPrestige( self ):
		"""
		��������ֵ
		"""
		variablePrestige = self.prestige - self.basePrestige	# ��õ�ǰ�Ŀɱ�����
		self.calBasePrestige()									# ���¼��㱣������
		self.prestige = variablePrestige + self.basePrestige
		self.onPrestigeChanged()

	def addBasePrestige( self, prestige ):
		"""
		define method
		���Ӱ���������
		"""
		self.basePrestige += prestige
		self.onPrestigeChanged()

	#------------------------------------------------------------------------------------------
	def addExp( self, value, reason = None ):
		"""
		define method
		��������
		@type	value : int32
		@param	value : ����ֵ
		"""
		if self.spendMoney > 0:			# CSOL- 2118 Ƿά���Ѳ��üӾ���
			INFO_MSG( "Tong[%i : %s] own money( spendMoney: %s ), can't add exp!" % ( self.databaseID, self.playerName, self.spendMoney ) )
			return
		level = self.level
		oldValue = self.EXP
		if level > TLevelEXP.getMaxLevel():
			return
		
		DEBUG_MSG( "TONG: %s has gained %i exp, reason is %s" % ( self.getNameAndID(), value, reason ) )
		
		exp = value + self.EXP
		expMax = TLevelEXP.getEXPMax( self.level )		# ��ǰ�ȼ��� exp ���ֵ

		while exp >= expMax :
			exp -= expMax								# ��ȥ��Ҫ������ exp ���ֵ
			level += 1
			self.addLevel( 1, csdefine.TONG_LEVEL_CHANGE_REASON_ADD_EXP )
			expMax = TLevelEXP.getEXPMax( level )
			if expMax <= 0 :
				ERROR_MSG( "Error exp max: %d" % expMax )
				break
		
		if level > TLevelEXP.getMaxLevel() :			# ���ȼ����������Ƶȼ�����
			level = TLevelEXP.getMaxLevel()
			exp = TLevelEXP.getEXPMax( level )

		self.EXP = max( 0, exp )						# ����ʣ�µ� exp
		try:
			g_logger.tongExpChangeLog( self.databaseID, self.getName(), oldValue, self.EXP, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def onExpChanged( self, value, exp, reason ):
		"""
		��ᾭ��ı�
		"""
		# ֪ͨ�ͻ��˽��и���
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.hasDelayTaskData( dbid, TASK_KEY_TONG_EXP ):
				emb.client.tong_onSetTongExp( exp )

#------------------------------------------------------------------------------------------
	def onLevelChanged( self ):
		"""
		��ἶ��ı���
		"""
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.hasDelayTaskData( dbid, TASK_KEY_LEVEL_DATA ):
				emb.cell.tong_onSetTongLevel( self.level )

		# �����ݸ��µ�������
		self.getTongManager().updateTongLevel( self.databaseID, self.level )
		self.upgradeBuildingLevel()		# ���°�Ὠ��������Ӧ�Ĺ���
		self.onBroadcastData()
		self.initTongSpecialItems( 1 )

	def degrade( self, level, reason ):
		"""
		define method.
		��ή��
		"""
		if self.level <= 1:
			return

		oldLevel = self.level
		self.level -= level
		self.onLevelChanged()
		self.statusMessageToOnlineMember( csstatus.TONG_DEGRADE )
		try:
			g_logger.tongDemotionLog( self.databaseID, self.getName(), self.level, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def setLevel( self, level, reason ):
		"""
		define method
		���ð��ȼ�,GMָ���õ�
		"""
		if level > TLevelEXP.getMaxLevel():
			self.statusMessageToOnlineMember( csstatus.TONG_LEVEL_CAN_NOT_GAIN_EXP )
			return
		
		self.level = level
		self.onLevelChanged()
		self.statusMessageToOnlineMember( csstatus.TONG_STATE_SET_LEVEL, level )

	def addLevel( self, level, reason ):
		"""
		define method.
		��Ӽ���
		"""
		INFO_MSG( "TONG: %s add %i level, old level is %i, new level is %i , reason is %s" % ( self.getNameAndID(), level, self.level, self.level + level, reason ) )
		oldLevel = self.level
		self.level += level
		self.onLevelChanged()
		self.statusMessageToOnlineMember( csstatus.TONG_UPGRADE )
		
		try:
			g_logger.tongUpgradeLog( self.databaseID, self.getName(), self.level, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	#------------------------------------------------------------------------------------------
	def onMoneyChanged( self ):
		"""
		����Ǯ�ı���
		"""
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.hasDelayTaskData( dbid, TASK_KEY_MONEY_DATA ):
				emb.client.tong_onSetTongMoney( self.money )

		# �ص������ģ�飬 �Զ���������ά����
		TongTerritory.onMoneyChanged( self )

	def isMoneyLessKeepMoney( self, offset = 0 ):
		"""
		����ʽ��Ƿ�С�ڱ����ʽ�
		@param offset: ͨ�����ƫ���������Բ�ͬ�����
		"""
		return ( self.money + offset ) < self.getKeepMoney()

	def addMoney( self, money, reason ):
		"""
		define method.
		��ӽ�Ǯ
		"""
		money = int( money )
		if money <= 0:
			EXCEHOOK_MSG("add tongMoney[%i]<=0, reason:%i" % (money, reason))
			return

		oldValue = self.money
		currentValue = oldValue + money
		if currentValue > Const.TONG_MONEY_LIMIT[ self.jk_level ][ 1 ]:	# ������ʽ�����
			self.money = Const.TONG_MONEY_LIMIT[ self.jk_level ][ 1 ]
			self.statusMessageToOnlineMember( csstatus.TONG_MONEY_MAX )
		elif currentValue < 0:
			self.money = 0
		else:
			self.money = currentValue
			self.weekTongMoney += money 			# ͳ�ư��һ�ܵ��ʽ�����

		self.onMoneyChanged()
		try:
			g_logger.tongMoneyChangeLog( self.databaseID, self.getName(), oldValue, self.money, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def getValidMoney( self ):
		"""
		��ȡ�������ʽ𣨳�ȥ�����ʽ�
		"""
		if self.isMoneyLessKeepMoney():
			return 0
		return self.money - self.getKeepMoney()

	def getKeepMoney( self ):
		"""
		��ȡ���ı����ʽ�����
		"""
		return Const.TONG_MONEY_LIMIT[ self.jk_level ][ 0 ]

	def payMoney( self, val, islimit = True, reason = csdefine.TONG_CHANGE_MONEY_NORMAL ):
		"""
		֧������ʽ�
		"""
		val = int( val )
		if val <= 0:
			return True

		if self.money <= 0:
			return False

		if islimit:	# ������ʽ�����
			if self.isMoneyLessKeepMoney( -val ):
				return False

		oldValue = self.money
		self.money -= val
		if self.money < 0:
			self.money = 0
			self.weekTotalCost += oldValue			# �ܰ���ʽ�֧��
		else:
			self.weekTotalCost += val
		self.onMoneyChanged()

		try:
			g_logger.tongMoneyChangeLog( self.databaseID, self.getName(), oldValue, self.money, reason )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True

	def getDiscountMoney( self, money ):
		"""
		�����ռ����д����Żݺ�İ���ʽ�Ŀǰ�ǰ���
		"""
		if self.holdCity:
			money *= 0.8
		return int( math.ceil( money ) )

	#------------------------------------------ְ��Ȩ��-------------------------------------------------------
	
	def checkMemberDutyRights( self, duty, right ):
		"""
		���ĳλ�õ�Ȩ��
		"""
		dutyMapping = csdefine.TONG_DUTY_RIGHTS_MAPPING
		if duty not in dutyMapping.keys():
			return False
		
		if right not in dutyMapping[ duty ]:
			return False
		
		return True
	#------------------------------------------------------------------------------------------
	def setMemberGrade( self, userDBID, targetDBID, grade ):
		"""
		define method.
		user����targetȨ��(ְ��)
		@param userDBID   : ʹ�øýӿڵ��û�DBID
		@param targetDBID : ��������DBID
		@param grade  	  : ����Ҫ���õ�Ȩ��
		"""
		DEBUG_MSG( "%i:set to target(%i) the grade=%i" % ( userDBID, targetDBID, grade ) )
		if grade not in csdefine.TONG_DUTYS:
			return
		# ���userDBID��Ȩ�� �Ƿ�������� targetDBID��Ȩ��
		userGrade = self.getMemberInfos( userDBID ).getGrade()
		targetGrade = self.getMemberInfos( targetDBID ).getGrade()
		if not self.checkMemberDutyRights( userGrade, csdefine.TONG_RIGHT_CHANGE_DUTY ): # û�п���Ȩ��
			return
		if targetGrade == grade or userGrade <= targetGrade or userGrade <= grade:
			return

		if grade == csdefine.TONG_DUTY_DEPUTY_CHIEF:		# ������
			xcount = self.getCountByGrade( grade )
			# �����������ﵽ���
			if xcount >= csdefine.TONG_DUTY_CHIEF_SUBALTERN_COUNT:
				mb = self.getMemberInfos( userDBID ).getBaseMailbox()
				if mb:
					self.statusMessage( mb, csstatus.TONG_CHIEF_SUBALTERN_MAX )
				return
			self.saveAdjutantChiefdate.append( { "dbID": targetDBID, "time": int( time.time() ) } )		# �����¸�������ְʱ��, ��Ҫ���ṩ�����ʷ���ʹ��

		elif grade == csdefine.TONG_DUTY_TONG:					# ����
			xcount = self.getCountByGrade( grade )
			if xcount >= csdefine.TONG_DUTY_TONG_COUNT:
				# ���������ﵽ���
				mb = self.getMemberInfos( userDBID ).getBaseMailbox()
				if mb:
					self.statusMessage( mb, csstatus.TONG_GRADE_TONG_MAX )
				return

		if targetGrade == csdefine.TONG_DUTY_DEPUTY_CHIEF:	# �Ƴ�ԭ���ĸ�������ְʱ��
			for recordTime in self.saveAdjutantChiefdate:
				if recordTime[ "dbID" ] == targetDBID:
					self.saveAdjutantChiefdate.remove( recordTime )

		targetBaseMailbox = self.getMemberInfos( targetDBID ).getBaseMailbox()
		if targetBaseMailbox:
			targetBaseMailbox.tong_setGrade( grade )
			self.addChangeGradeChek( targetDBID, csdefine.TONG_DUTY_MEMBER )
		else:
			cmd = "update tbl_Role set sm_tong_grade=%i where id=%i;" % ( grade, targetDBID )
			BigWorld.executeRawDatabaseCommand( cmd )

		self.onMemberGradeChanged( userDBID, targetDBID, grade )
		try:
			g_logger.tongSetGradeLog( self.databaseID, self.getName(), userDBID, self._memberInfos[ userDBID ].getName(), targetDBID, self._memberInfos[ targetDBID ].getName(), targetGrade, grade )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		
	def getCountByGrade( self, grade ):
		"""
		��ȡĳһ��ְλ����
		"""
		xcount = 0
		for info in self._memberInfos.itervalues():
			if info.getGrade() == grade:
				xcount += 1
		return xcount

	def onMemberGradeChanged( self, userDBID, memberDBID, grade ):
		"""
		define method.
		ĳ��Ա��Ȩ�޸ı���
		"""
		ograde = self.getMemberInfos( memberDBID ).getGrade()
		if grade == ograde:
			return

		self.getMemberInfos( memberDBID ).setGrade( grade )
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
				emb.client.tong_onMemberGradeChanged( userDBID, memberDBID, grade )    # ����������Ա�Ŀͻ���

	#------------------------------------------------------------------------------------------
	def setMemberScholium( self, userDBID, targetDBID, scholium ):
		"""
		define method.
		user����target��ע
		@param userDBID   : ʹ�øýӿڵ��û�DBID
		@param targetDBID : ��������DBID
		@param grade  	  : ����Ҫ���õ�Ȩ��
		"""
		DEBUG_MSG( "%i:set to target(%i) the scholium=%s" % ( userDBID, targetDBID, scholium ) )
		if len( scholium ) > csdefine.TONG_MEMBER_SCHOLIUM_LENGTH_MAX:
			return

		# ���userDBID��Ȩ�� �Ƿ�������� targetDBID��Ȩ��
		userGrade = self.getMemberInfos( userDBID ).getGrade()
		tscholium = self.getMemberInfos( targetDBID ).getScholium()

		if not self.checkMemberDutyRights( userGrade, csdefine.TONG_RIGHT_MEMBER_SCHOLIUM ):
			return
		elif tscholium == scholium:
			return

		targetBaseMailbox = self.getMemberInfos( targetDBID ).getBaseMailbox()
		if targetBaseMailbox:
			targetBaseMailbox.tong_setScholium( scholium )
		else:
			cmd = "update tbl_Role set sm_tong_scholium=%s where id=%i;" % ( BigWorld.escape_string( scholium ), targetDBID )
			BigWorld.executeRawDatabaseCommand( cmd )

		self.onMemberScholiumChanged( targetDBID, scholium )

	def onMemberScholiumChanged( self, memberDBID, scholium ):
		"""
		ĳ��Ա����ע�ı���
		"""
		oscholium = self.getMemberInfos( memberDBID ).getScholium()
		if scholium == oscholium:
			return

		self.getMemberInfos( memberDBID ).setScholium( scholium )
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
				emb.client.tong_onMemberScholiumChanged( memberDBID, scholium )    # ����������Ա�Ŀͻ���

	#------------------------------------------------------------------------------------------
	def onMemberOnlineStateChanged( self, memberBaseMailbox, memberDBID, onlineState, updataClient = True ):
		"""
		ĳ��Ա������״̬�ı���
		@param memberBaseMailbox: ���onlineStateΪture ��ô��ΪBaseMailbox����Ϊnone
		@param onlineState		: bool ���߻�����
		"""
		currentMemberInfo = self.getMemberInfos( memberDBID )
		currentMemberInfo.setOnlineState( onlineState )
		currentMemberInfo.setBaseMailbox( memberBaseMailbox )

		if onlineState:
			try:
				for dbid in self._onlineMemberDBID:
					otherMember = self.getMemberInfos( dbid ).getBaseMailbox()
					memberBaseMailbox.cell.tong_addMemberOL( dbid, otherMember )		 	 		  # ���Լ���cell���߳�Ա�б�����������߳�Ա
					otherMember.cell.tong_addMemberOL( memberDBID, memberBaseMailbox )	  			  # ��������Ա��cell���߳�Ա�б��������
					if updataClient and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
						otherMember.client.tong_onMemberOnlineStateChanged( memberDBID, True ) 	  	  # ����������Ա�Ŀͻ��� �ҵ�״̬Ϊ����
			except:
				pass

			self._onlineMemberDBID.add( memberDBID )
			self.createSendDataTask( memberDBID )
			memberBaseMailbox.cell.tong_onSetTongName( self.playerName )
			TongCampaign.initTongQuestState( self, memberBaseMailbox )
		else:
			self._onlineMemberDBID.remove( memberDBID )
			for dbid in self._onlineMemberDBID:
				otherMember = self.getMemberInfos( dbid ).getBaseMailbox()
				otherMember.cell.tong_onMemberRemoveOL( memberDBID )			 	 	 		   # �����������߳�Ա�������� ���������˵����߳�Ա�б���ɾ����
				if updataClient and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
					otherMember.client.tong_onMemberOnlineStateChanged( memberDBID, False )    	   # ����������Ա�Ŀͻ��� �ҵ�״̬Ϊ������

			# ���첽���ݴ�����ɾ��
			if self.isInDelayTaskList( memberDBID ):
				self.delDelayTaskMember( memberDBID )

	#------------------------------------------------------------------------------------------
	def onMemberLevelChanged( self, memberDBID, level ):
		"""
		define method.
		ĳ��Ա�ļ���ı���
		"""
		olevel = self.getMemberInfos( memberDBID ).getLevel()
		if level == olevel:
			return

		self.getMemberInfos( memberDBID ).setLevel( level )
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
				emb.client.tong_onMemberLevelChanged( memberDBID, level )   						 # ����������Ա�Ŀͻ���
		self.calPrestige()			# ���������仯

	#------------------------------------------------------------------------------------------
	def onMemberNameChanged( self, memberDBID, name ):
		"""
		define method.
		ĳ��Ա�����ָı���
		"""
		oname = self.getMemberInfos( memberDBID ).getName()
		if name == oname:
			return

		self.getMemberInfos( memberDBID ).setName( name )
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
				emb.client.tong_onMemberNameChanged( memberDBID, name )   						 # ����������Ա�Ŀͻ���

	#------------------------------------------------------------------------------------------
	def setAffiche( self, userDBID, affiche ):
		"""
		define method.
		user���ù���, ��Ȩ��
		"""
		userInfo = self.getMemberInfos( userDBID )
		userGrade = userInfo.getGrade()

		if not self.checkMemberDutyRights( userGrade, csdefine.TONG_RIGHT_AFFICHE ): # û��Ȩ��
			return
		elif len( affiche ) > csdefine.TONG_AFFICHE_LENGTH_MAX or affiche == self.affiche:			# ������������ֱ�ӷ��ز������棬Ӧ���ɿͻ����Ǳ߼��󱨸���û�.
			return

		self.affiche = affiche
		self.onTongAfficheChanged()

	def onTongAfficheChanged( self ):
		"""
		define method.
		��ṫ��ı���
		"""
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.hasDelayTaskData( dbid, TASK_KEY_AFFICHE_DATA ):
				self.statusMessage( emb, csstatus.TONG_AFFICHE_CHANGED )
				self.statusMessage( emb, csstatus.TONG_AFFICHE_CHANGED_SHOW, self.affiche )
				emb.client.tong_onSetAffiche( self.affiche )    # ����������Ա�Ŀͻ���

	#------------------------------------------------------------------------------------------
	def onMemberContributeChanged( self, memberDBID, contribute ):
		"""
		define method.
		ĳ��Ա�İ�ṱ�׶ȸı���
		"""
		ocontribute = self.getMemberInfos( memberDBID ).getContribute()
		if contribute == ocontribute:
			return

		# ��¼�����ۻ��ﹱ�� ���Ͱﹱ���ǲ����м�¼�� ֻ��¼���Ӱﹱ
		totalContribute = self.addMemberTotalContributeRecord( memberDBID, contribute - ocontribute )
		self.getMemberInfos( memberDBID ).setContribute( ocontribute + ( contribute - ocontribute ) )
		contribute = self.getMemberInfos( memberDBID ).getContribute()
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
				emb.client.tong_onMemberContributeChanged( memberDBID, contribute, totalContribute )    # ����������Ա�Ŀͻ���

	#---------------------------------------------------------------------------------------------------------
	def onMemberLogin( self, memberBaseMailbox, memberDBID ):
		"""
		define method.
		��Ա��½֪ͨ
		"""
		DEBUG_MSG( "playerDBID %i login to tong(%s)." % ( memberDBID, self.playerName ) )
		if not self.hasMember( memberDBID ):		# ������Ѿ����ڱ����
			DEBUG_MSG( "%i is not in tong %i"  % ( memberBaseMailbox.id, self.tid ) )
			memberBaseMailbox.tong_reset()
			return
		
		self.onMemberOnlineStateChanged( memberBaseMailbox, memberDBID, True )
		memberBaseMailbox.tong_onLoginCB( self )

		#��ṫ��//
		if self.affiche:
			self.statusMessage( memberBaseMailbox, csstatus.TONG_AFFICHE_SHOW, self.affiche )
		memberBaseMailbox.cell.sendTongFaction( self.factionCount )
		
		if self.tongAbaGatherFlag:
			memberBaseMailbox.client.tongAbaGather( self.tongAbaGatherFlag )
			memberBaseMailbox.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TONG_ABA )
		
		if self.tongAbaRound:
			memberBaseMailbox.client.receiveAbaRound( self.tongAbaRound )

		if self.tongCompetitionGatherFlag:
			memberBaseMailbox.client.tongCompetitionGather()
			memberBaseMailbox.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TONG_COMPETITION )

		if memberDBID == self.chiefDBID:
			if not self.holdCity: return
			cityName = csconst.g_maps_info.get( self.holdCity )
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHGL_TONG_CHIEFONLINE_NOTIFY % ( self.playerName, cityName, self.chiefName ), [] )

	def onMemberLogout( self, memberDBID ):
		"""
		define method.
		��Ա����֪ͨ
		"""
		DEBUG_MSG( "playerDBID %i logout of tong(%s)." % ( memberDBID, self.playerName ) )
		self.onMemberOnlineStateChanged( None, memberDBID, False )

	#-----------------------------------------------------------------------------------------------------------
	def hasRequestJoin( self, targetDBID ):
		"""
		��ENTITY�Ƿ��б�����
		"""
		return self._requestJoinEntityList.has_key( targetDBID )

	def getRequestJoinInfo( self, targetDBID ):
		"""
		��ȡ����������һЩ��¼
		"""
		return self._requestJoinEntityList[ targetDBID ]

	def removeRequestJoinInfo( self, targetDBID ):
		"""
		ɾ��������������ļ�¼
		"""
		if self.hasRequestJoin( targetDBID ):
			self._requestJoinEntityList.pop( targetDBID )

	def checkRequestJoinTimeOut( self, time ):
		"""
		���time�Ƿ񳬹��������ʱ��
		"""
		return BigWorld.time() - time > CONST_REQUEST_JOIN_TIMEOUT

	def onAddRequestJoinInfo( self, userDBID, targetBaseMailbox, targetDBID ):
		"""
		��ӱ������˵���Ϣ
		@param userDBID			: �������빦�ܵ�ʹ����databaseID
		@param targetBaseMailbox: ���εı�����Ŀ��baseMailbox
		@param targetDBID		: ���εı�����Ŀ���databaseID
		"""
		d = {}
		d["targetBaseMailbox"] 	= targetBaseMailbox
		d["userDBID"]			= userDBID
		d["time"]				= BigWorld.time()
		self._requestJoinEntityList[ targetDBID ] = d

		# ���û��ʱ�Ӽ���� ��ô��������ʱ����
		if self._check_RequestJoinTimerID <= 0:
			self._check_RequestJoinTimerID = self.addTimer( CONST_REQUEST_JOIN_TIMEOUT, CONST_REQUEST_JOIN_TIMEOUT, TIME_CBID_CHECK_REQUEST_JOIN )

	def onCheckRequestJoinTimer( self ):
		"""
		ɾ����ʱ����������
		"""
		rme = []
		for key, info in self._requestJoinEntityList.iteritems():
			if self.checkRequestJoinTimeOut( info[ "time" ] ):
				rme.append( key )

		for key in rme:
			self._requestJoinEntityList.pop( key )

		if len( self._requestJoinEntityList ) <= 0:
			self.delTimer( self._check_RequestJoinTimerID )
			self._check_RequestJoinTimerID = 0

	def getMemberLimit( self ):
		"""
		��ð���Ա��������
		"""
		return csconst.TONG_MEMBER_LIMIT_DICT[self.level]

	def checkJoinTongConditions( self, userDBID, targetBaseMailbox, targetDBID ):
		"""
		�������������Ƿ��������
		@param userDBID			: �������빦�ܵ�ʹ����databaseID
		@param targetBaseMailbox: ���εı�����Ŀ��baseMailbox
		@param targetDBID		: ���εı�����Ŀ���databaseID
		@param targetLevel		: ���εı�����Ŀ��ļ���
		"""
		userInfo = self.getMemberInfos( userDBID )
		userBaseMailbox = userInfo.getBaseMailbox()
		userGrade = userInfo.getGrade()

		# ��������ߵ�Ȩ��
		if not self.checkMemberDutyRights( userGrade, csdefine.TONG_RIGHT_MEMBER_MANAGE ): 
			return csstatus.TONG_GRADE_INVALID 					# ���Ȩ�޲���
		elif self.isTongMemberFull():
			return csstatus.TONG_MEMBER_FULL 					# ��������ﵽ����,����ﴦ���б���Ҳ�������Ա
		elif userDBID == targetDBID:
			return csstatus.TONG_TARGET_SELF 					# �㲻�������Լ�
		elif self.hasRequestJoin( targetDBID ):
			return csstatus.TONG_WAITING_RESPONSE 				# �Ƿ����ڱ������У���ȴ��Է���Ӧ.

		return csstatus.TONG_NORMAL

	def onRequestJoin( self, userDBID, targetBaseMailbox, targetDBID ):
		"""
		define method.
		�������Ȩ��ʿ����ĳ�˼��뱾���
		@param userDBID			: �������빦�ܵ�ʹ����databaseID
		@param targetBaseMailbox: ���εı�����Ŀ��baseMailbox
		@param targetDBID		: ���εı�����Ŀ���databaseID
		@param targetLevel		: ���εı�����Ŀ��ļ���
		"""
		DEBUG_MSG( "onRequestJoin: userDBID=%i, targetDBID=%i" % ( userDBID, targetDBID ) )
		userInfo = self.getMemberInfos( userDBID )
		userBaseMailbox = userInfo.getBaseMailbox()

		# ���Ϸ������������֪ͨ
		state = self.checkJoinTongConditions( userDBID, targetBaseMailbox, targetDBID )
		if state != csstatus.TONG_NORMAL:
			self.statusMessage( userBaseMailbox, state )
			return

		self.onAddRequestJoinInfo( userDBID, targetBaseMailbox, targetDBID )
		if hasattr( targetBaseMailbox, "client" ):
			targetBaseMailbox.client.tong_onReceiveRequestJoin( userInfo.getName(), self.databaseID, self.playerName, \
			self.chiefName, self.level, self.memberCount )
		else:
			ERROR_MSG( "target %i:%i no has client."  % ( targetBaseMailbox.id, targetDBID ) )

	def onAnswerRequestJoin( self, targetDBID, agree, targetName ):
		"""
		define method.
		������� �����ش���
		@param targetDBID		: ���εı�����Ŀ���databaseID
		@param agree			: bool, true = ����
		@param targetName		: ���εı�����Ŀ�������
		"""
		DEBUG_MSG( "playerDBID %i answer to tong %i" % ( targetDBID, self.databaseID ) )
		if not self.hasRequestJoin( targetDBID ):
			DEBUG_MSG( "not of the request! may is the timeout!" ) # ���ܳ�ʱ�� ��¼�Ѿ���ϵͳɾ�� �����ش�
			return

		requestJoinInfo = self.getRequestJoinInfo( targetDBID )
		if requestJoinInfo is None:
			ERROR_MSG( "request info is Error! %i" % targetDBID )
			return

		# ɾ����������¼
		self.removeRequestJoinInfo( targetDBID )
		if self.checkRequestJoinTimeOut( requestJoinInfo[ "time" ] ):
			DEBUG_MSG( "request time out." )
			return
		userDBID = requestJoinInfo["userDBID"]
		userBaseMailbox = self.getMemberInfos( userDBID ).getBaseMailbox()
		if not agree:
			self.statusMessage( userBaseMailbox, csstatus.TONG_REJECT_JOIN_TONG, targetName )
			return
		if self.isTongMemberFull():
			self.statusMessage( userBaseMailbox, csstatus.TONG_MEMBER_FULL )
			return
		targetBaseMailbox = requestJoinInfo[ "targetBaseMailbox" ]
		self.addMemberJoinCheck( targetDBID )
		# ����ҵ�cell��ʼ����Ӱ�����̣���ֹ��������ҵ����entity�п��ܱ����ٶ��������ݲ��ɹ������
		targetBaseMailbox.cell.tong_onJoin( self.databaseID, csdefine.TONG_DUTY_MEMBER, csconst.JOIN_TONG_INIT_CONTRIBUTE, self )

	def onJoin( self, mDBID, mName, mLevel, mClass, mBaseMailbox, tongGrade, tongContribute ):
		"""
		Define method.
		��������Ϣע��
		"""
		memberInfo = self.createMemberInfo( mDBID, mName, mLevel, mClass, \
							mBaseMailbox, tongGrade, '', tongContribute )
		self.addMember( mDBID, memberInfo )
		memberDBIDList = [mDBID]
		
		
		if self.tongAbaGatherFlag:
			mBaseMailbox.client.tongAbaGather( self.tongAbaGatherFlag )
			mBaseMailbox.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TONG_ABA )
		
		if self.tongAbaRound:
			mBaseMailbox.client.receiveAbaRound( self.tongAbaRound )

		if self.tongCompetitionGatherFlag:
			mBaseMailbox.client.tongCompetitionGather()
			mBaseMailbox.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TONG_COMPETITION )

		# �����������߳�Ա�Ŀͻ��˵ĳ�Ա�б��м����³�Ա
		# ��������memberDBIDList���ܷǳ��Ķ࣬���Ҳ��һ���첽���»���
		for dbid in self._onlineMemberDBID:
			if self.isInDelayTaskList( dbid ):
				# ����ó�Ա�����첽�����У� ��ô��ó�Ա���첽����������м����¼ӵĳ�Ա
				self.addMembersToDelayTaskMember( dbid, memberDBIDList )
			else:
				# �ó�Ա��ǰ�����첽���´����У���ô�����¼�һ���첽��������֪ͨ�ͻ���������ȡ����
				d = {}
				d[ "tasks" ] = [ TASK_KEY_MEMBER_DATA ]
				d[ TASK_KEY_MEMBER_DATA ] = list( memberDBIDList )
				self._delayDataTasks[ dbid ] = d
				otherMember = self.getMemberInfos( dbid ).getBaseMailbox()
				if hasattr( otherMember, "client" ):
					otherMember.client.tong_onReceiveData()	# ���ڿͻ��˳�ʼ�������������ڽ�ɫ������Ϸ���ֹͣ�ˣ� ������Ҫ���߿ͻ������¼���һ�����ݻ�ȡ������.
				self.statusMessage( otherMember, csstatus.TONG_ADD_MEMBER, mName )
		self.onMemberOnlineStateChanged( mBaseMailbox, mDBID, True, False )# ������ע�ᵽ���߳�Ա��Ϣ����ע�ᵽ������Ա
		if hasattr( mBaseMailbox, "client" ):
			mBaseMailbox.client.tong_onReceiveData() 		# ���ڿͻ��˳�ʼ�������������ڽ�ɫ������Ϸ���ֹͣ�ˣ� ������Ҫ���߿ͻ������¼���һ�����ݻ�ȡ������.
		self.memberJoinSuccess( mDBID )
		self.writeToDB()

	#-----------------------------------------------------------------------------------------------------------
	def onStatusMessage( self, statusID, sargs ) :
		"""
		<defined/>
		���շ�������������״̬��Ϣ
		@type				statusID : MACRO DEFINATION
		@param				statusID : ״̬��Ϣ���� common/csstatus.py �ж���
		@type				sargs	 : STRING
		@param				sargs	 : ��Ϣ���Ӳ���
		@return						 : None
		"""
		args = () if sargs == "" else eval( sargs )
		self.statusMessageToOnlineMember( statusID, *args )

	def statusMessage( self, targetBaseMailbox, statusID, *args ) :
		"""
		send status message
		@type			statusID : INT32
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		args = "" if args == () else str( args )
		if hasattr( targetBaseMailbox, "client" ):
			targetBaseMailbox.client.onStatusMessage( statusID, args )

	def statusMessageToOnlineMember( self, statusID, *args ) :
		"""
		send status message
		@type			statusID : INT32
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		for dbid in self._onlineMemberDBID:
			member = self.getMemberInfos( dbid ).getBaseMailbox()
			self.statusMessage( member, statusID, *args )

	def onSendMessage( self, userName, memberDBID, msg ):
		"""
		define method.
		��ĳ��Ա������Ϣ
		"""
		info = self.getMemberInfos( memberDBID )
		if not info.isOnline():
			return
		e = info.getBaseMailbox()
		e.chat_handleMessage( csdefine.CHAT_CHANNEL_WHISPER, userName, msg, [] )

	def doAllOnlineMemberClientFunc( self, funcName, *args ) :
		"""
		send status message
		@type			statusID : INT32
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		for dbid in self._onlineMemberDBID:
			member = self.getMemberInfos( dbid ).getBaseMailbox()
			method = getattr( member.client, funcName )
			method( *args )

	def onSendChatMessageAll( self, memberDBID, msg, playerID, playerName, blobArgs ):
		"""
		Define method.
		������Ϣ�����о��ų�Ա

		@param msg	: message
		@type  msg	: STRING
		@param playerID : player's id
		@type  playerID : OBJECT_ID
		@param playerName : player's name
		@type  playerName : STRING
		"""
		info = self.getMemberInfos( memberDBID )
		grade = info.getGrade()
		if not self.checkMemberDutyRights( grade, csdefine.TONG_RIGHT_GRADE_CHAT ):
			e = info.getBaseMailbox()
			if hasattr( e, "client" ):
				e.client.onStatusMessage( csstatus.CHAT_TONG_UNPROMISE, "" )
			return

		for dbid in self._onlineMemberDBID:
			info = self.getMemberInfos( dbid )
			grade = info.getGrade()
			if not self.isInDelayTaskList( dbid ) and self.checkMemberDutyRights( grade, csdefine.TONG_RIGHT_GRADE_CHAT ):
				emb = info.getBaseMailbox()
				if hasattr( emb, "client" ):
					emb.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_TONG, playerID, playerName, msg, blobArgs )


	#-----------------------------------------------------------------------------------------------------------
	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		TongTerritory.onTimer( self, timerID, cbID )
		TongCampaign.onTimer( self, timerID, cbID )
		TongStorage.onTimer( self, timerID, cbID )

		if self._check_RequestJoinTimerID == timerID:					# ɾ����ʱ����������
			self.onCheckRequestJoinTimer()
		elif self._check_RequestLeagueTimerID == timerID:				# ɾ����ʱ����������
			self.onCheckRequestLeagueTimer()
		elif self._check_conjureTimerID == timerID:						# ������
			self.onCheckConjureTimer()
		elif self._check_payChiefMoney_timerID == timerID:				# ���������ʷ������
			self.checkPayChiefMoney()
		elif self._startupTimerID == timerID:
			self.onTongStartup()
			self._startupTimerID = 0
		elif self._afterFeteTimerID == timerID:
			self.__unapplyStatusAfterFete()						# ������������õ�״̬
			self._afterFeteTimerID = 0
		elif self.tempDataCheckTimer == timerID:
			self.onTempDataCheckTimerCheck()
		elif timerID == self.destroyTimerID:
			del BigWorld.globalData[ "tong.%i" % self.databaseID ]
			self.destroy( deleteFromDB = True, writeToDB = True )
		elif self._check_inviteBattleLeagueTimerID == timerID:			# ɾ����ʱ��ս��������������
			self.onCheckRequestBattleLeagueTimer()

	#-----------------------------------------------------------------------------------------------------------
	def checkQuitLeagueLog( self ):
		"""
		�����ڵİ���ֹͬ�˼�¼
		"""
		dels = []
		for idx, info in enumerate( self.quitLeagueLog ):
			if time.time() >= info[ "timeout" ]:
				dels.append( idx )

		dels.reverse()
		for d in dels:
			self.quitLeagueLog.pop( d )

	def checkRequestLeagueTimeOut( self, time ):
		"""
		���time�Ƿ񳬹��������ʱ��
		"""
		return BigWorld.time() - time > CONST_REQUEST_JOIN_TIMEOUT

	def onRequestTongLeague( self, userDBID, requestTongDBID, requestTongName ):
		"""
		define method.
		����Ὣ������ͬ��
		@param user				:ʹ�ù�����baseMailbox
		@param userTongName		:ʹ�ù����� ��������
		@param userTongDBID		:ʹ�ù����� ����DBID
		"""
		DEBUG_MSG( "%i request tong %s to league." % ( userDBID, requestTongName ) )
		user = self.getMemberInfos( userDBID ).getBaseMailbox()

		if requestTongDBID <= 0 :
			self.statusMessage( user, csstatus.TONG_TARGET_TONG_NO_FIND )
			return

		if len( self.leagues ) >= csdefine.TONG_LEAGUE_MAX_COUNT:
			self.statusMessage( user, csstatus.TONG_TONG_LEAGUE_FULL )
			return

		if self._requestLeagueRecord.has_key( requestTongDBID ):
			self.statusMessage( user, csstatus.TONG_WAITING_RESPONSE )
			return
		else:
			self.checkQuitLeagueLog()
			for item in self.quitLeagueLog:
				if requestTongDBID == item[ "tongDBID" ]:
					#δ��һ������ ��������ͬ��
					self.statusMessage( user, csstatus.TONG_INVALID_NO_TIMEOUT )
					return

		d = {}
		d["userDBID"] = userDBID
		d["requestTongName" ] = requestTongName
		d[ "time" ] = BigWorld.time()
		self._requestLeagueRecord[ requestTongDBID ] = d

		if self.checkMemberDutyRights( self.getMemberInfos( userDBID ).getGrade(), csdefine.TONG_RIGHT_LEAGUE_MAMAGE ):
			self.getTongManager().requestTongLeague( user, self.databaseID, requestTongName )
		else:
			self.statusMessage( user, csstatus.TONG_GRADE_INVALID )

		# ���û��ʱ�Ӽ���� ��ô��������ʱ����
		if self._check_RequestLeagueTimerID <= 0:
			self._check_RequestLeagueTimerID = self.addTimer( CONST_REQUEST_JOIN_TIMEOUT, CONST_REQUEST_JOIN_TIMEOUT, TIME_CBID_CHECK_REQUEST_JOIN )

	def onCheckRequestLeagueTimer( self ):
		"""
		ɾ����ʱ����������
		"""
		rme = []
		for key, info in self._requestLeagueRecord.iteritems():
			if self.checkRequestLeagueTimeOut( info[ "time" ] ):
				rme.append( key )

		for key in rme:
			self._requestLeagueRecord.pop( key )

		if len( self._requestLeagueRecord ) <= 0:
			self.delTimer( self._check_RequestLeagueTimerID )
			self._check_RequestLeagueTimerID = 0

	def requestTongLeague( self, user, userTongName, userTongDBID ):
		"""
		define method.
		������ͬ��
		@param user				:ʹ�ù�����baseMailbox
		@param userTongName		:ʹ�ù����� ��������
		@param userTongDBID		:ʹ�ù����� ����DBID
		"""
		if len( self.leagues ) >= csdefine.TONG_LEAGUE_MAX_COUNT:
			self.statusMessage( user, csstatus.TONG_TARGET_TONG_LEAGUE_FULL )
			self.getTongManager().onRequestTongLeagueFailed( userTongDBID, self.databaseID )
			return

		self.checkQuitLeagueLog()
		for dbid, info in self._memberInfos.iteritems():
			if self.checkMemberDutyRights( info.getGrade(), csdefine.TONG_RIGHT_LEAGUE_MAMAGE ):
				if info.isOnline():
					info.getBaseMailbox().client.tong_onRequestTongLeague( userTongName, userTongDBID )
					return

		self.statusMessage( user, csstatus.TONG_TARGET_TONG_CHIEF_OFFLINE )
		self.getTongManager().onRequestTongLeagueFailed( userTongDBID, self.databaseID )

	def onRequestTongLeagueFailed( self, targetTongDBID ):
		"""
		define method.
		����ͬ���ڶԷ����entity��ʧ���ˣ������ǰ��������ߣ������ص�
		"""
		self._requestLeagueRecord.pop( targetTongDBID )

	def onAnswerRequestTongLeague( self, answerRoleBaseEntity, requestTongDBID, agree ):
		"""
		define method.
		����Ὣ�ش����뷽�Ƿ�Ը�����ͬ�ˡ�
		"""
		if len( self.leagues ) >= csdefine.TONG_LEAGUE_MAX_COUNT:
			self.statusMessage( answerRoleBaseEntity, csstatus.TONG_TONG_LEAGUE_FULL )
			self.getTongManager().onRequestTongLeagueFailed( requestTongDBID, self.databaseID )
			return

		self.getTongManager().answerRequestTongLeague( answerRoleBaseEntity, self.databaseID, agree, requestTongDBID )

	def answerRequestTongLeague( self, answerRoleBaseEntity, requestTong, requestTongDBID, agree ):
		"""
		define method.
		�յ��Է��ش��Ƿ�Ը�����ͬ�ˡ�
		"""
		DEBUG_MSG( "%i answer tong %i to league." % ( requestTongDBID, self.databaseID ) )
		info = self._requestLeagueRecord[ requestTongDBID ]
		user = self.getMemberInfos( info[ "userDBID" ] ).getBaseMailbox()
		requestTongName = info["requestTongName" ]
		del self._requestLeagueRecord[ requestTongDBID ]

		if len( self.leagues ) >= csdefine.TONG_LEAGUE_MAX_COUNT:
			self.statusMessage( answerRoleBaseEntity, csstatus.TONG_TARGET_TONG_LEAGUE_FULL )
			return

		# ��ʱ�� ����
		if self.checkRequestLeagueTimeOut( info[ "time" ] ):
			return

		if not agree:
			if user:
				self.statusMessage( user, csstatus.TONG_LEAGUE_FAIL, requestTongName )
			return

		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHGL_ALIGNMENT_NOTIFY % ( requestTongName, self.playerName ), [] )
		requestTong.onTongLeague( self.databaseID, self.playerName )
		self.onTongLeagueNotify( requestTongDBID, requestTongName )

	def onTongLeague( self, leagueTongDBID, leagueTongName ):
		"""
		define method.
		�յ��Է��������ͬ��
		"""
		if not self.hasLeagueTong( leagueTongDBID ):
			self.onTongLeagueNotify( leagueTongDBID, leagueTongName )
		else:
			ERROR_MSG( "league %s %i is exist." % ( leagueTongName, leagueTongDBID ) )

	def onTongLeagueNotify( self, tongDBID, tongName ):
		"""
		˫����Ϊͬ�˵�ͨ��
		"""
		self.leagues.append( { "dbID" : tongDBID, "tongName" : tongName, "tid" : 0, "ad" : "" } )
		for dbid in self._onlineMemberDBID:
			member = self.getMemberInfos( dbid ).getBaseMailbox()
			if not self.isInDelayTaskList( dbid ):
				member.client.tong_addLeague( tongDBID, tongName )
			else:
				self.addLeagueToDelayTaskMember( dbid, tongDBID, tongName )

		# �����ݸ��µ�������
		self.getTongManager().updateTongLeagues( self.databaseID, self.leagues )

	def leagueDispose( self, memberDBID, leagueTongDBID ):
		"""
		define method.
		������˹�ϵ
		"""
		if memberDBID != -1:	#-1 ��ϵͳ���� ��Ҫԭ������һ������ɢ��
			if not self.checkMemberDutyRights( self.getMemberInfos( memberDBID ).getGrade(), csdefine.TONG_RIGHT_LEAGUE_MAMAGE ): # Ȩ�޼��
				return

		self.onTongLeagueDisposeNotify( leagueTongDBID, True )

	def onLeagueDispose( self, leagueTongDBID ):
		"""
		define method.
		�յ��Է��������������ͬ�˹�ϵ
		"""
		self.onTongLeagueDisposeNotify( leagueTongDBID, False )

	def onTongLeagueDisposeNotify( self, tongDBID, initiative ):
		"""
		˫�������ͬ�˵�ͨ��
		"""
		msgKey = csstatus.TONG_LEAGUE_QUIT_TO
		if not initiative:
			msgKey = csstatus.TONG_LEAGUE_QUIT

		for idx, item in enumerate( self.leagues ):
			if item[ "dbID" ] == tongDBID:
				self.leagues.pop( idx )
				d = { "tongDBID" : tongDBID, "timeout" : int( time.time() + 60 * 60 * 24 * 7 ) }
				self.quitLeagueLog.append( d )

				if initiative:
					self.getTongManager().onLeagueDispose( tongDBID, self.databaseID )

				for dbid in self._onlineMemberDBID:
					member = self.getMemberInfos( dbid ).getBaseMailbox()
					self.statusMessage( member, msgKey, item[ "tongName" ] )

					if not self.isInDelayTaskMember_LeaguesList( dbid, tongDBID ):
						member.client.tong_delLeague( tongDBID )
					else:
						self.delLeagueInDelayTaskMember( dbid, tongDBID, item[ "tongName" ] )
				break

	def hasLeagueTong( self, leagueTongDBID ):
		"""
		�Ƿ��и�ͬ�˰��
		"""
		for t in self.leagues:
			if t[ "dbID" ] == leagueTongDBID:
				return True

		return False

	#-----------------------------------------------------------------------------------------------------------
	def requestMemberMapInfo( self, baseEntity, userDBID ):
		"""
		define method.
		�ͻ��������ȡ��Ա���ڵ�ͼ��Ϣ
		"""
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			emb.cell.tong_onMemberRequestMapInfo( baseEntity )

	#-----------------------------------------------------------------------------------------------------------
	def onAbdication( self, userDBID, memberDBID ):
		"""
		define method.
		������λ
		"""
		if not self.hasMember( userDBID ) or not self.hasMember( memberDBID ):
			return

		userInfo = self.getMemberInfos( userDBID )
		userGrade = userInfo.getGrade()
		if userGrade != csdefine.TONG_DUTY_CHIEF:
			return
		DEBUG_MSG( "userDBID=%i grade=%i, memberDBID=%i" % ( userDBID, userGrade, memberDBID ) )
		memberInfo = self.getMemberInfos( memberDBID )
		memberInfo.setGrade( csdefine.TONG_DUTY_CHIEF )
		userInfo.setGrade( csdefine.TONG_DUTY_MEMBER )
		self.chiefDBID = memberDBID
		self.chiefName = memberInfo.getName()

		# ��Ȼ�ǰ�����λ,��ô�����϶�������BaseMailbox����.
		userMB = userInfo.getBaseMailbox()
		userMB.tong_setGrade( csdefine.TONG_DUTY_MEMBER )
		self.statusMessage( userMB, csstatus.TONG_CHANGE_CHIEF_TO, self.chiefName )
		self.addChangeGradeChek( userDBID, csdefine.TONG_DUTY_MEMBER )
		# ���ڽ��ܰ���λ�ӵ���ң�Ҫ�������ڲ����߷ֱ���
		emb = memberInfo.getBaseMailbox()

		if emb:
			self.addChangeGradeChek( userDBID, csdefine.TONG_DUTY_CHIEF )
			emb.tong_setGrade( csdefine.TONG_DUTY_CHIEF )
			emb.cell.sendTongFaction( self.factionCount )
			self.statusMessage( emb, csstatus.TONG_CHANGE_CHIEF_FROM, self.playerName )
		else:
			self.updateGrade2DB( memberDBID, csdefine.TONG_DUTY_CHIEF )
			content = cschannel_msgs.TONG_INFO_26 % self.playerName
			self.getMailMgr().send( None, self.chiefName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
					cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.TONG_INFO_25, content, 0, "" )
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if emb and not self.isInDelayTaskMember_MemberList( dbid, memberDBID ):
				emb.client.tong_onAbdication( userDBID, memberDBID )    # ����������Ա�Ŀͻ���

		# �����°�����ְʱ��, ��Ҫ���ṩ�����ʷ���ʹ��
		self.saveChiefdate = int( time.time() )
		try:
			g_logger.tongLeaderChangeLog( self.databaseID, self.getName(), userDBID, userInfo.getName(), 0 )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

		# �����ݸ��µ�������
		self.getTongManager().updateTongChiefName( self.databaseID, self.chiefName )
		self.save()
		self.statusMessageToOnlineMember( csstatus.TONG_CHIEF_ABDCATION, userInfo.getName(), memberInfo.getName(), self.playerName )

	def updateGrade2DB( self, memberDBID, grade ):
		"""
		��Ҳ����ߣ�������Ұ��Ȩ�޵�db
		"""
		cmd = "update tbl_Role set sm_tong_grade=%i where id=%i;" % ( grade, memberDBID )
		BigWorld.executeRawDatabaseCommand( cmd )

	def setDutyName( self, userDBID, duty, newName ):
		"""
		define method.
		����ĳְλ������
		"""
		if len( newName ) <= 0 or not self.hasMember( userDBID ) or self.getMemberInfos( userDBID ).getGrade() != csdefine.TONG_DUTY_CHIEF:
			return

		if duty not in csdefine.TONG_DUTYS:
			return
		
		# �������ͬ����������������
		for item in self.dutyNames:
			if newName == item[ "dutyName" ]:
				return

		# ����������
		for item in self.dutyNames:
			if item[ "duty" ] == duty:
				INFO_MSG( "TONG:( %i, %s ) set duty %s's name which is %s to %s" % ( userDBID, self.getMemberInfos( userDBID ).getName(), duty, item["dutyName"], newName ) )
				item[ "dutyName" ] = newName
				self.onDutyNameChanged( duty, newName )
				return

	def onDutyNameChanged( self, duty, newName ):
		"""
		ĳְλ�����Ѿ��ı�
		"""
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			if hasattr( emb, "client" ) and not self.hasDelayTaskData( dbid, TASK_KEY_DUTY_NAMES_DATA ):
				emb.client.tong_onDutyNameChanged( duty, newName )    # ����������Ա�Ŀͻ���

	def sendDailogByTongDutyName( self, duty, dailog, NPC_id, playerMB ):
		"""
		Define method
		���ݰ���Զ�����������֯NPC�Ի�����
		������
		"""
		for dn in self.dutyNames:
			dutyID, dutyName = dn.values()
			if dutyID == duty:
				playerMB.client.onSetGossipText( dailog%(dutyName) )
				playerMB.client.onGossipComplete( NPC_id )
				break
	#-----------------------------------------------------------------------------------------------------------
	def checkCommandValid_conjure( self, memberDBID ):
		"""
		����峤�Ƿ�Ըó�Աʹ�������� �Լ��Ƿ���Ȼ��Ч
		"""
		if self._chiefCommandInfo.has_key( "conjure" ) and memberDBID in self._chiefCommandInfo[ "conjure" ][ "members" ]:
			return True
		return False

	def chiefCommand_conjure( self, userDBID, lineNumber, mapName, position ):
		"""
		define mothod.
		������ �������ж�Ա���������
		"""
		# ���û��һ����Ա���� �ǻ���ʲô?
		if len( self._onlineMemberDBID ) < 2:
			return

		userInfo = self.getMemberInfos( userDBID )
		user = userInfo.getBaseMailbox()
		self._chiefCommandInfo[ "conjure" ] = {}

		if self._check_conjureTimerID > 0:
			self.delTimer( self._check_conjureTimerID )

		self._check_conjureTimerID = self.addTimer( CONST_CHIEF_CONJURE_TIMEOUT, 0, 1 )
		if not user or not self.checkMemberDutyRights( userInfo.getGrade(), csdefine.TONG_RIGHT_CALL_ALL_MEMBER ):
			return

		self._chiefCommandInfo[ "conjure" ][ "members" ] 	= list( self._onlineMemberDBID )
		self._chiefCommandInfo[ "conjure" ][ "mapName" ] 	= mapName
		self._chiefCommandInfo[ "conjure" ][ "position" ] 	= position
		self._chiefCommandInfo[ "conjure" ][ "lineNumber" ] = lineNumber

		for dbid in self._onlineMemberDBID:
			if userDBID != dbid:
				self.getMemberInfos( dbid ).getBaseMailbox().client.tong_onChiefConjure()

	def onCheckConjureTimer( self ):
		"""
		"""
		if self._chiefCommandInfo.has_key( "conjure" ):
			del self._chiefCommandInfo[ "conjure" ]
		self._check_conjureTimerID = 0

	def onAnswer_conjure( self, memberDBID ):
		"""
		define mothod.
		��Ա��Ӧ������
		"""
		if not self.checkCommandValid_conjure( memberDBID ):
			return

		info = self._chiefCommandInfo[ "conjure" ]
		info[ "members" ].remove( memberDBID )
		emb = self.getMemberInfos( memberDBID ).getBaseMailbox()

		if emb:
			mapName = info[ "mapName" ]
			position = info[ "position" ]
			lineNumber = info[ "lineNumber" ]
			emb.cell.gotoSpaceLineNumber( mapName, lineNumber, position, ( 0, 0, 0 ) )
		else:
			DEBUG_MSG( "not found member %i" % memberDBID )

	#-----------------------------------------------------------------------------------------------------------
	def checkPayChiefMoney( self ):
		"""
		�����֧�������͸������������
		"""
		tinfo = time.localtime()
		# ��������Ƿ���������
		if tinfo[6] == 6:
			if not self.querySunday:
				chiefWage = 0
				adjutantChiefWages = []

				# ����������Ĺ���
				if len( self.chiefName ) > 0:
					remainTime = int( time.time() - self.saveChiefdate )
					day = remainTime / ( 24 * 60 * 60 )
					chiefWage = int( Const.TONG_CHIEF_WAGE[ "chief" ][ self.level ] * min( 7.0, day ) )
						
				# ��ȡ�������ǵĹ���
				for memberDBID, info in self._memberInfos.items():
					if info.getGrade() != csdefine.TONG_DUTY_DEPUTY_CHIEF:
						continue
					for recordTime in self.saveAdjutantChiefdate:
						if recordTime[ "dbID" ] == memberDBID:
							remainTime = int( time.time() - recordTime[ "time" ] )
							day = remainTime / ( 24 * 60 * 60 )
							wage = int( Const.TONG_CHIEF_WAGE[ "adjutantChief" ][ self.level ] * min( 7.0, day ) )
							wageInfo = ( info.getName(), wage )
							adjutantChiefWages.append( wageInfo )
							break
						
				# ���㹤���ܶ�
				totalWage = chiefWage
				for wageInfo in adjutantChiefWages:
					totalWage += wageInfo[1]
				
				# �����ʽ�����ȡ�����η��� CSOL-2364
				if totalWage > self.getValidMoney():
					INFO_MSG( "Tong[%s : %s] valid money is not enough for wage!" % ( self.databaseID, self.getName() ) )
				else:
					# ����������
					if chiefWage >= 1:
						self.payMoney( chiefWage, True, csdefine.TONG_CHANGE_MONEY_PAYFIRSTCHIEF )
						self.getMailMgr().send( None, self.chiefName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
								cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.TONG_INFO_4, cschannel_msgs.TONG_INFO_5, chiefWage, "" )
						g_logger.tongWageLog( self.databaseID, self.getName(), self.chiefName, csdefine.TONG_DUTY_CHIEF, chiefWage )
						
					# ������������
					for wageInfo in adjutantChiefWages:
						if wageInfo[1] > 1:
							self.payMoney( wageInfo[1], True, csdefine.TONG_CHANGE_MONEY_PAYSECONDCHIEF )
							self.getMailMgr().send( None, wageInfo[0], csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
									cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.TONG_INFO_6, cschannel_msgs.TONG_INFO_7, wageInfo[1], "" )
							g_logger.tongWageLog( self.databaseID, self.getName(), wageInfo[0], csdefine.TONG_DUTY_DEPUTY_CHIEF, wageInfo[1] )
				
				# �����Ѿ������� �������
				self.querySunday = True
		else:
			self.querySunday = False

	def queryTongInfo( self, queryer, args ):
		"""
		"""
		infos = {
					cschannel_msgs.GMMGR_JIN_QIAN 		: 	self.money,
					cschannel_msgs.TONG_INFO_9	:	self.level,
					cschannel_msgs.TONG_INFO_11	:	self.prestige,
					 }

		if not args in infos:
			queryer.client.onStatusMessage( csstatus.TONG_NO_THIS_INFO_SUPPORT, "" )
			queryer.client.onStatusMessage( csstatus.TONG_INFO_SELECT, "" )
			return

		queryer.client.onStatusMessage( csstatus.MESSAGE_NONE_ONE_S_PARAM, ( args + ":" + str(infos[args]), ) )
	
	#------------------------------------�����Ʒ-----------------------------------------------------------------------

	def initTongItems( self, reset = False ):
		"""
		��ʼ�������Ʒ,resetΪ0��ʾ��ʼ����Ϊ1��ʾ����
		"""
		TongTerritory.onInitTongItems( self, reset )
		
		self.items = []
		itemDatas = g_tongItems.getDatas()

		for itemID, item in itemDatas.iteritems():
			# ��ֹ������Ʒ��󼶱�
			if self.sd_level >= item[ "repBuildingLevel" ]:
				itemData = { "itemID":itemID, "amount":item["amount"]}
				self.items.append( itemData )
		
		self.items.sort( key = lambda item : item["itemID"], reverse = False )

	def resetTongItems( self ):
		"""
		define method
		���ð����Ʒ����Ʒ������ʱ������Ʒ�з�����
		"""
		self.initTongItems( 1 )

	def removeBuyTongItemRecord( self, dbid ):
		"""
		�Ƴ���ҹ�������Ʒ��¼
		"""
		for record in self.weekMemberBuyItemRecord:
			if record[ "dbID" ] == dbid:
				self.weekMemberBuyItemRecord.remove( record )

	def resetMemberBuyItemRecord( self ):
		"""
		define method
		���ð��ڹ�����Ʒ��¼
		"""
		self.weekMemberBuyItemRecord = []
	
	def removeChiefBuyTongSpecItemRecord( self, dbid ):
		"""
		�Ƴ���������������Ʒ��¼
		"""
		for record in self.chiefBuySpecItemForMemberRecord:
			if record[ "dbID" ] == dbid:
				self.chiefBuySpecItemForMemberRecord.remove( record )

	def resetChiefBuyTongSpecItemRecord( self ):
		"""
		define method
		�����Ƴ���������������Ʒ��¼
		"""
		self.chiefBuySpecItemForMemberRecord = []
	
	#--------------------------------------------����װ��-------------------------------------------------------
	def requestRepairOneEquip( self, repairType, kitBagID, orderID, memberDBID ):
		"""
		define method.
		����ԱҪ������װ��
		"""
		if not memberDBID in self._onlineMemberDBID:
			return

		member = self.getMemberInfos( memberDBID ).getBaseMailbox()
		member.cell.tong_onRepairOneEquipBaseCB( repairType, kitBagID, orderID, csconst.TONG_TJP_REBATE[ self.tjp_level ] )

	def requestRepairAllEquip( self, repairType, memberDBID ):
		"""
		define method.
		����ԱҪ������װ��
		"""
		if not memberDBID in self._onlineMemberDBID:
			return

		member = self.getMemberInfos( memberDBID ).getBaseMailbox()
		member.cell.tong_requestRepairAllEquipBaseCB( repairType, csconst.TONG_TJP_REBATE[ self.tjp_level ] )

	#---------------------------------------------�ͻ��˴򿪰������������������-----------------------------------
	def onClientOpenTongWindow( self, playerBase ):
		"""
		define method.
		�ͻ��˴��˰����棬 ������������
		"""
		playerBase.client.tong_onSetAfterFeteStatus( self._afterFeteStatus )

		playerBase.tong_requestSignInRecord()		# ������ǩ������

		self.calBasePrestige()
		playerBase.client.tong_onSetVariablePrestige( self.prestige - self.basePrestige ) # �������������͵��ͻ���( CSOL-9992 )

	def isTongMemberFull( self ):
		"""
		��ҳ�Ա���Ƿ�ﵽ����
		"""
		return len( self._memberInfos ) + len( self.joinMemberTempInfo ) >= self.getMemberLimit()

	#--------------------------------------����ڰ���б�����������������ع���-----------------------------------
	def requestJoinToTong( self, playerBase, playerDBID, playerName, playerCamp ):
		"""
		define method.
		������뵽ĳ�����
		"""
		if self.isTongMemberFull():	# ��������ﵽ����
			self.statusMessage( playerBase, csstatus.TONG_MEMBER_FULL )
			return
		
		if playerCamp != self.getCamp():
			self.statusMessage( playerBase, csstatus.TONG_CAMP_DIFFERENT )
			return 
			
		if self.chiefDBID in self._onlineMemberDBID:
			userInfo = self.getMemberInfos( self.chiefDBID )
			userInfo.getBaseMailbox().client.tong_onReceiveiJoinInfo( playerDBID, playerName )
			self.statusMessage( playerBase, csstatus.TONG_REQUEST_JOIN_SEND_SUCCESS )
			self.onAddRequestJoinInfo( self.chiefDBID, playerBase, playerDBID )
		else:
			self.statusMessage( playerBase, csstatus.TONG_JOINGRADE_MEMBER_OFFLINE )

	def answerJoinToTong( self, targetDBID, agree ):
		"""
		define method.
		������Ҽ��뵽ĳ�����
		"""
		requestJoinInfo = self.getRequestJoinInfo( targetDBID )
		if requestJoinInfo is None:
			ERROR_MSG( "request info is Error! %i" % targetDBID )
			return
		self.removeRequestJoinInfo( targetDBID )		# ɾ����������¼
		if self.checkRequestJoinTimeOut( requestJoinInfo[ "time" ] ):
			return

		userDBID = requestJoinInfo["userDBID"]
		targetBaseMailbox = requestJoinInfo[ "targetBaseMailbox" ]
		if not agree:
			self.statusMessage( targetBaseMailbox, csstatus.TONG_REQUEST_JOIN_NO_ACCEPT )
			return
		userBaseMailbox = self.getMemberInfos( userDBID ).getBaseMailbox()
		if self.isTongMemberFull():
			self.statusMessage( userBaseMailbox, csstatus.TONG_MEMBER_FULL )
			return

		self.addMemberJoinCheck( targetDBID )
		# ����ҵ�cell��ʼ����Ӱ�����̣���ֹ��������ҵ����entity�п��ܱ����ٶ��������ݲ��ɹ������
		targetBaseMailbox.cell.tong_onJoin( self.databaseID, csdefine.TONG_DUTY_MEMBER, csconst.JOIN_TONG_INIT_CONTRIBUTE, self )

	#----------------------------------------------������------------------------------------------------------
	def requestFete( self, playerBase ):
		"""
		define method.
		���������
		"""
		if self.getValidMoney() < csconst.TONG_FETE_REQUEST_MONEY:
			playerBase.client.onStatusMessage( csstatus.TONG_OPEN_ACT_MONEY_LACK, "" )
			return
		self.onRequestFeteSuccessfully( playerBase )

	def onRequestFeteSuccessfully( self, playerBase ):
		"""
		���������ɹ�
		"""
		TongTerritory.onRequestFeteSuccessfully( self )
		self.getTongManager().onRequestFeteSuccessfully( self.databaseID )
		self.statusMessageToOnlineMember( csstatus.TONG_FETE_START )
		self.payMoney( csconst.TONG_FETE_REQUEST_MONEY, True, csdefine.TONG_CHANGE_MONEY_REQUEST_FETE  )

		for dbid in self._onlineMemberDBID:
			self.initMemberFeteData( dbid, 0 )
		try:
			g_logger.actJoinLog( csdefine.ACTIVITY_TONG_JISHI_QUEST, csdefine.ACTIVITY_JOIN_TONG, self.databaseID, self.getName() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def initMemberFeteData( self, memberDBID, value ):
		"""
		define method.
		��ʼ��ĳ��Ա�ļ�������
		@param value: ��ǰ����ֵ
		"""
		member = self.getMemberInfos( memberDBID ).getBaseMailbox()
		if member and hasattr( member, "client" ):
			member.client.tong_setFeteData( value )

	def onUpdateFeteData( self, val ):
		"""
		define method.
		���°���Ա�ļ�������
		"""
		for dbid in self._onlineMemberDBID:
			member = self.getMemberInfos( dbid ).getBaseMailbox()
			if member and hasattr( member, "client" ):
				member.client.tong_setFeteData( val )

	def onFeteComplete( self ):
		"""
		define method.
		�������ɹ������
		"""
		TongTerritory.onFeteComplete( self )
		self.addExp( csconst.TONG_EXP_REWARD_FETE, csdefine.TONG_CHANGE_EXP_FETE )
		self.statusMessageToOnlineMember( csstatus.TONG_FETE_COMPLETE )

		# �����ȡ���ǻԸ�¶�����θ�¶���չ��¶ ״̬֮һ
		self._afterFeteStatus = self.__choseStatusAfterFete()
		# ��������õ�״̬������Ӧ��ָ��
		self.__applyStatusAfterFete( self._afterFeteStatus )
		# �趨һ����ʱ����ָ��ʱ���ȡ�����״̬
		self.__setupRestoreTimerAfterFete( self._afterFeteStatus )
		# ���Ѿ���õ�״̬д�룬��ֹ������ǿ��������ʧ���״̬
		self.writeToDB()

	def __initAfterFeteStatus( self ):
		"""
		���ݰ�������Ϻ��״̬��ʼ��������ָ��������ٶ�
		"""
		# ״̬�� NONE_STATUS,LUNARHALO,SUNSHINE,STARLIGHT

		##�������������ָ���������õ�״̬
		##ע�⣬����״̬�Ļָ��ͼ��㶼���������ʱ������ȷ��
		restoreTimeInSec = None
		if self._afterFeteStatusRestoreTime == "":
			self.__unapplyStatusAfterFete()
			return
		try:
			stTime = time.strptime( self._afterFeteStatusRestoreTime, "%Y %m %d %H %M %S" )
			restoreTimeInSec = time.mktime( stTime )
		except:
			# ���û�гɹ���ȡ�������ϱ���Ļָ�ʱ�䣬ֱ�ӳ�������״̬
			self.__unapplyStatusAfterFete()
			ERROR_MSG( "Can't load restore time of status gained after fete! All status reset!" )
			return

		if not self._afterFeteStatus:
			ERROR_MSG( "Data inconsistent, reset and ignored!" )
			self.__unapplyStatusAfterFete()
			return

		currentTimeInSec = time.time()
		# if �ָ�ʱ��û�е�
		if restoreTimeInSec > currentTimeInSec:
			# ����Ӧ��״̬
			self.__applyStatusAfterFete( self._afterFeteStatus )
			# �����趨״̬��ԭ��ʱ��
			self._afterFeteTimerID = self.addTimer( restoreTimeInSec - currentTimeInSec, 0, 0 )
		# else
		else:
			# ����״̬
			self.__unapplyStatusAfterFete()


	def __choseStatusAfterFete( self ):
		"""
		@choseStatusAfterFete: �ڰ��������֮�����ѡ���ǻԸ�¶�����θ�¶���չ��¶ ״̬֮һ��CSOL-9750��
		@return: ��ѡ���״̬
		"""
		return random.choice( csconst.FETE_COMPLETE_STATUS )

	def __applyStatusAfterFete( self, status ):
		"""
		@applyStatusAfterFete: �ڰ��������֮�󣬸�������õ�״̬������Ӧ��ָ��
		"""
		return


	def __setupRestoreTimerAfterFete( self, status ):
		"""
		@setupRestoreTimerAfterFete�� �趨һ����ʱ��������������֮���õ�״̬
		"""
		## ��ȡ�����ڿ�ʼ������������24�������
		tm = time.localtime()
		year = tm[0]
		month = tm[1]
		day = tm[2]
		weekDay = tm[6] # 0 ��ʾ��һ

		daysToSun = 6 - weekDay

		# ����������ʱ��
		timeString = "%s %s %s %s %s %s"%( year, month, day + daysToSun, 0, 0, 0 )
		restoreTime = time.strptime( timeString, "%Y %m %d %H %M %S" )

		secToNextSat = time.mktime( restoreTime ) - time.time() # �����ڿ�ʼ������0�������

		# ����ԭʱ�䰴�ַ�������ʽ����
		self._afterFeteStatusRestoreTime = timeString


		# �趨�ָ���ʱ��
		self._afterFeteTimerID = self.addTimer( secToNextSat, 0, 0 )

	def __unapplyStatusAfterFete( self ):
		"""
		@unapplyStatusAfterFete: ������������ɺ��õ�״̬
		"""
		self._afterFeteStatus = NONE_STATUS
		self._afterFeteStatusRestoreTime = ""

		# д�����ݿ⣬��ֹ������ǿ��������ʧ���״̬
		self.writeToDB()

	def onOverFete( self ):
		"""
		define method.
		������������  ʱ�䵽��
		"""
		TongTerritory.onOverFete( self )
		self.statusMessageToOnlineMember( csstatus.TONG_FETE_OVER )

	#-----------------------------------------------------------------------------------------------------------
	"""#########################################################################################################
			���½ӿ�Ϊ�첽���ݴ�����ؽӿڣ� ��Ҫ�����첽���¿ͻ�������
			���˼��: ���������ݻ���.
					 һ����Ҫ�첽�������� �ͻ��˻�����������������ȡ���ݣ�����������������
					 ���첽���������б����ÿ�����������������ݣ� �������Ϊ���ˣ�������������
					 ��ʼ��һ����������ݴ��� ����������У������¼����Ա����ɾ���� ��Ա���ݸı�
					 ��Щ����Ҫ��ʱ�Ĵ������ݻ���ĸı�
	"""#########################################################################################################
	#----------------------------------------------------------------------------------------------------------
	def requestDelayDatas( self, delayTaskMemberDBID, delayTaskMemberBaseMailbox ):
		"""
		define method.
		�ͻ���������������������첽���ݴ��������
		"""
		if len( self._delayDataTasks ) <= 0:
			return

		# ����ó�Ա�����첽��������������
		if not self.isInDelayTaskList( delayTaskMemberDBID ):
			delayTaskMemberBaseMailbox.client.tong_onRequestDatasCallBack()
			return

		# ��������û�иó�Ա���������������첽�������
		if not self._memberInfos.has_key( delayTaskMemberDBID ):
			self._delayDataTasks.pop( delayTaskMemberDBID )
			delayTaskMemberBaseMailbox.client.tong_onRequestDatasCallBack()
			return

		# ��ͻ����첽���ͳ�Ա����
		datas = self._delayDataTasks[ delayTaskMemberDBID ]
		memberBaseMailbox = self.getMemberInfos( delayTaskMemberDBID ).getBaseMailbox()
		# ����Ҳ����ó�Ա��mailbox����� �����������
		if not memberBaseMailbox:
			self._delayDataTasks.pop( delayTaskMemberDBID )
			delayTaskMemberBaseMailbox.client.tong_onRequestDatasCallBack()
			return

		# ����ó�Ա���첽���������е������Ѿ�ȫ����� ��ô��������ó�Ա���첽������е���������
		if len( datas[ "tasks" ] ) <= 0:
			self._delayDataTasks.pop( delayTaskMemberDBID )
			delayTaskMemberBaseMailbox.client.tong_onRequestDatasCallBack()
			return
		else:
			key = datas[ "tasks" ][ 0 ]
			if not self.onSendClientDelayDatas( key, memberBaseMailbox, datas ):
				self._delayDataTasks.pop( delayTaskMemberDBID )
				delayTaskMemberBaseMailbox.client.tong_onRequestDatasCallBack()

	def onSendClientDelayDatas( self, key, memberBaseMailbox, datas ):
		"""
		�������ݵ��ͻ��� ��Ҫ���첽����һЩ������Ϣ
		@param key				: TASK_KEY_*** �����һЩ�������ؼ���
		@param memberBaseMailbox: ����ҵ�mailbox
		@param datas			:�������ݳ�
		@return type: �ɹ�����һ�����񷵻�True ���򷵻�false
		"""
		DEBUG_MSG( "[%i]key:%s, currentDatas:%s, delayDataTasks:%s" % ( memberBaseMailbox.id, key, datas, self._delayDataTasks ) )
		if TongTerritory.onSendClientDelayDatas( self, key, memberBaseMailbox, datas ):
			return True

		if key == TASK_KEY_MEMBER_DATA:				# �첽���ݴ���  �����Ա����
			ls = datas[ TASK_KEY_MEMBER_DATA ]
			if len(ls) > 0:
				otherMemberDBID = ls.pop( 0 )
				item = self.getMemberInfos( otherMemberDBID )
				memberBaseMailbox.client.tong_onSetMemberInfo( otherMemberDBID, \
				item.getName(), item.getLevel(), item.getClass(), item.getGrade(), item.getScholium(), item.getContribute(), \
				item.getTotalContribute(), item.isOnline() )
			else:
				ERROR_MSG( "tongDebug:this tong[%i-%i] without member!" % (self.id, self.databaseID) )

			if len( ls ) <= 0:
				datas[ "tasks" ].pop( 0 )
			return True
		elif key == TASK_KEY_PERSTIGE_DATA:				# �첽���ݴ���  ������������
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.client.tong_onSetTongPrestige( self.prestige )
			return True
		elif key == TASK_KEY_AFFICHE_DATA:				# �첽���ݴ���  ����������
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.client.tong_onSetAffiche( self.affiche )
			return True
		elif key == TASK_KEY_MONEY_DATA:				# �첽���ݴ���  �����Ǯ����
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.client.tong_onSetTongMoney( self.money )
			return True
		elif key == TASK_KEY_LEVEL_DATA:				# �첽���ݴ���  ����������
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.cell.tong_onSetTongLevel( self.level )
			return True
		elif key == TASK_KEY_LEAGUES_DATA:
			ls = datas[ TASK_KEY_LEAGUES_DATA ]
			d = ls.pop( 0 )
			if len( ls ) <= 0:
				datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.client.tong_setLeague( d[0], d[1] )
			return True
		elif key == TASK_KEY_DUTY_NAMES_DATA:
			datas[ "tasks" ].pop( 0 )
			
			# ������һ�¼����Ϊ�˼�����ǰ�����ݣ���֤�ͻ��˽��յ���ְλ�������ݵ���ȷ��
			dutys = []
			for item in self.dutyNames:
				dutys.append( item[ "duty" ] )
			interDuty = set( dutys ) & set( csdefine.TONG_DUTYS )
			if len( interDuty ) != len( csdefine.TONG_DUTYS ):
				self.dutyNames = copy.deepcopy( Const.TONG_DUTY_NAME )
			 
			for item in self.dutyNames:
				memberBaseMailbox.client.tong_initDutyName( item[ "duty" ], item[ "dutyName" ] )
			return True
		elif key == TASK_KEY_HOLD_CITY_DATA:
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.cell.tong_onSetHoldCity( self.holdCity, True )
			return True
		elif key == TASK_KEY_TONG_SIGN_MD5:
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.client.tong_onSetTongSignMD5( self.tongSignMD5 )
			return True
		elif key == TASK_KEY_TONG_EXP:
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.client.tong_onSetTongExp( self.EXP )
			return True
		elif key == TASK_KEY_TONG_SKILL:
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.cell.tong_updateTongSkills( self.yjy_level )
			return True
		elif key == TASK_KEY_BATTLE_LEAGUES_DATA:
			datas[ "tasks" ].pop( 0 )
			if memberBaseMailbox == self.getMemberInfos( self.chiefDBID ):	# ֻ�����������Ϣ
				leagues = []
				for league in self.battleLeagues:
					leagues.append( league[ "dbID" ] )
				memberBaseMailbox.client.tong_receiveBattleLeagues( self.databaseID, self.getName(), self.getCamp(), leagues )
			return True
		return False

	def resetMemberDelayTaskData( self ):
		DEBUG_MSG( "reset to table of task." )
		self._delayDataTasks = {}

	def hasDelayTaskData( self, delayTaskMemberDBID, task ):
		"""
		�Ƿ��������첽����ĳ��������
		@param key: TASK_KEY_*
		"""
		return self.isInDelayTaskList( delayTaskMemberDBID ) and task in self._delayDataTasks[ delayTaskMemberDBID ][ "tasks" ]

	def isInDelayTaskList( self, memberDBID ):
		"""
		�ó�Ա�Ƿ���һ���첽���ݴ��������
		"""
		return self._delayDataTasks.has_key( memberDBID )

	def isInDelayTaskMember_MemberList( self, delayTaskMember, memberDBID ):
		"""
		ĳ��Ա�Ƿ����첽���ݴ���ĳ�Ա�����ݴ����б���
		"""
		if not self.isInDelayTaskList( delayTaskMember ):
			return False

		info = self._delayDataTasks[ delayTaskMember ]
		if not TASK_KEY_MEMBER_DATA in info[ "tasks" ]:
			return False

		if not memberDBID in info[ TASK_KEY_MEMBER_DATA ]:
			return False

		return  True

	def isInDelayTaskMember_LeaguesList( self, delayTaskMember, tongDBID ):
		"""
		ĳͬ�������Ƿ����첽���ݴ���ĳ�Ա�����ݴ����б���
		"""
		if not self.isInDelayTaskList( delayTaskMember ):
			return False

		info = self._delayDataTasks[ delayTaskMember ]
		if not TASK_KEY_LEAGUES_DATA in info[ "tasks" ]:
			return False

		if not tongDBID in info[ TASK_KEY_LEAGUES_DATA ]:
			return False

		return  True

	def createSendDataTask( self, memberDBID ):
		"""
		����һ����Ա���첽���ݷ�������
		"""
		d = {}

		# �½�һ���������ݳ�
		d[ "tasks" ] = [
				TASK_KEY_LEVEL_DATA,			# �첽���ݴ���  ����������
				TASK_KEY_DUTY_NAMES_DATA,		# �첽���ݴ���  ������ְλ��������
				TASK_KEY_MEMBER_DATA, 			# �첽���ݴ���  �����Ա����
				TASK_KEY_PERSTIGE_DATA, 		# �첽���ݴ���  ������������
				TASK_KEY_AFFICHE_DATA, 			# �첽���ݴ���  ����������
				TASK_KEY_MONEY_DATA,			# �첽���ݴ���  �����Ǯ����
				TASK_KEY_HOLD_CITY_DATA,
				TASK_KEY_TONG_SIGN_MD5,
				TASK_KEY_TONG_EXP,				# �첽���ݴ���  ����������
				TASK_KEY_TONG_SKILL,			# �첽���ݴ���  ����������
				TASK_KEY_BATTLE_LEAGUES_DATA,	# �첽���ݴ��� ս��ͬ������
		  ]

		# ��¼ͬ����Ϣ������
		leagues = []
		for litem in self.leagues:
			leagues.append( ( litem[ "dbID" ], litem[ "tongName" ] ) )
		if len( leagues ) > 0:	# �����ͬ���������������
			d[ "tasks" ].append( TASK_KEY_LEAGUES_DATA )

		d[ TASK_KEY_MEMBER_DATA ] = self._memberInfos.keys()
		d[ TASK_KEY_LEAGUES_DATA ] = leagues
		self._delayDataTasks[ memberDBID ] = d
		
		TongTerritory.createSendDataTask( self, memberDBID )

	def addSendDataTask( self, memberDBID, taskID, taskData ):
		"""
		��������� �ýӿ���Ҫ�ṩ��createSendDataTask����д������ģ��ʱ���Ⱪ¶һЩ����
		Ҳ����˵������ģ������createSendDataTask�ӿ�ʱҪ��ײ��������ʱӦ��ʹ�ñ��ӿ����
		@param taskData: ������(taskID)����Я��һЩ��Ҫ����Ĵ���������ϵ�� ���忴�μ�tongEntity.createSendDataTask
						 ����ʹ�õ�һЩ����
		"""
		if not self.isInDelayTaskList( memberDBID ):
			return

		self._delayDataTasks[ memberDBID ][ "tasks" ].append( taskID )
		if taskData:
			self._delayDataTasks[ memberDBID ] = d

	def addMembersToDelayTaskMember( self, delayTaskMemberDBID, memberDBIDList ):
		"""
		�������첽���ݴ����entity�����б������һ���³�Ա
		"""
		if not self.isInDelayTaskList( delayTaskMemberDBID ):
			return

		if not TASK_KEY_MEMBER_DATA in self._delayDataTasks[ delayTaskMemberDBID ][ "tasks" ]:
			self._delayDataTasks[ delayTaskMemberDBID ][ "tasks" ].append( TASK_KEY_MEMBER_DATA )

		self._delayDataTasks[ delayTaskMemberDBID ][ TASK_KEY_MEMBER_DATA ].extend( memberDBIDList )

	def addLeagueToDelayTaskMember( self, delayTaskMemberDBID, tongDBID, tongName ):
		"""
		�������첽���ݴ����league�����б������һ����ͬ��
		"""
		if not self.isInDelayTaskList( delayTaskMemberDBID ):
			return

		if not TASK_KEY_LEAGUES_DATA in self._delayDataTasks[ delayTaskMemberDBID ][ "tasks" ]:
			self._delayDataTasks[ delayTaskMemberDBID ][ "tasks" ].append( TASK_KEY_LEAGUES_DATA )

		self._delayDataTasks[ delayTaskMemberDBID ][ TASK_KEY_LEAGUES_DATA ].extend( ( tongDBID, tongName ) )

	def delDelayTaskMember( self, memberDBID ):
		"""
		ɾ��һ����Ա���첽���ݷ��Ͷ���
		"""
		DEBUG_MSG( "delete a taskMember %i." % memberDBID )
		self._delayDataTasks.pop( memberDBID )

	def delDelayTaskMemberTask( self, delayTaskMember, task ):
		"""
		ɾ���첽�����Ա�������б��е�һ������
		"""
		DEBUG_MSG( "member % i remove a task % i." % ( delayTaskMember, task ) )
		for item in self._delayDataTasks.values():
			if task in item[ "tasks" ]:
				item[ "tasks" ].remove( task )

	def delMemberFromDelayTaskMembers( self, memberDBID ):
		"""
		�������첽���ݳ�Ա���ݷ��Ͷ���������ó�Ա
		"""
		DEBUG_MSG( "from allTaskMember the list remove member %i" % memberDBID )
		for item in self._delayDataTasks.values():
			if item.has_key( TASK_KEY_MEMBER_DATA ):
				ls = item[ TASK_KEY_MEMBER_DATA ]
				if memberDBID in ls:
					ls.remove( memberDBID )

	def delMemberFromDelayTaskMember( self, delayTaskMemberDBID, memberDBID ):
		"""
		�������첽���ݳ�Ա���ݷ��Ͷ���������ó�Ա
		"""
		DEBUG_MSG( "from taskMember %i the list remove member %i" % ( delayTaskMemberDBID, memberDBID ) )
		if not self.isInDelayTaskList( delayTaskMemberDBID ):
			return

		item = self._delayDataTasks[ delayTaskMemberDBID ]
		if item.has_key( TASK_KEY_MEMBER_DATA ):
			ls = item[ TASK_KEY_MEMBER_DATA ]
			if memberDBID in ls:
				ls.remove( memberDBID )

	def delLeagueInDelayTaskMember( self, memberDBID, tongDBID ):
		"""
		�������첽���ݳ�Ա���ݷ��Ͷ���������ó�Ա
		"""
		DEBUG_MSG( "from taskMember %i the list remove leagueTong %i" % ( memberDBID, tongDBID ) )
		if not self.isInDelayTaskList( memberDBID ):
			return

		if self._delayDataTasks[ memberDBID ].has_key( TASK_KEY_LEAGUES_DATA ):
			leagues = self._delayDataTasks[ memberDBID ][ TASK_KEY_LEAGUES_DATA ]
			for idx, item in enumerate( leagues ):
				if item[0] == tongDBID:
					leagues.pop( idx )
					return

	#------------------------------------------------------------------------------------------------------------
	def changeName( self, newName ):
		"""
		Define method.
		������
		"""
		self.playerName = newName
		for dbid in self._onlineMemberDBID:	# ֪ͨ�����������
			try:
				self.getMemberInfos( dbid ).getBaseMailbox().cell.onTongNameChange( newName )
			except:
				continue

	#------------------------------------------------------------------------------------------------------------
	def queryMerchantCount( self, playerMB, questID, count ):
		"""
		Define method
		��ѯ��ǰ���ȼ�������ҽ���������Ĵ���

		"""
		maxCount = TONG_MERCHANT_QUEST_MAX_MAP[self.level]  # ��ǰ���ȼ�����������������

		if count < maxCount:
			playerMB.cell.remoteQuestAccept( questID )
			return

		playerMB.client.onStatusMessage( csstatus.TONG_MERCHANT_MOST, "" )

	def queryDartCount( self, playerMB, questID ):
		"""
		Define method.
		��ѯ������ڴ���
		"""
		timeTuple = time.gmtime()
		day = str( timeTuple[0] ) + str( timeTuple[1] ) + str( timeTuple[2] )
		record = self._dartRecord.split("_")
		if len(record) == 1 or record[0] != day or int(record[1]) < ( csconst.TONG_MEMBER_LIMIT_DICT[self.level]/10):
			playerMB.cell.remoteQuestAccept( questID )
			return

		playerMB.client.onStatusMessage( csstatus.TONG_IS_DART_ONCE, "" )

	def addDartCount( self ):
		"""
		define method
		"""
		timeTuple = time.gmtime()
		day = str( timeTuple[0] ) + str( timeTuple[1] ) + str( timeTuple[2] )
		record = self._dartRecord.split( "_" )
		if len(record) == 1:
			self._dartRecord = day + "_" + "1"
		else:
			n = int(record[1]) + 1
			self._dartRecord = record[0] + "_" + str(n)

	def addTongNormalCount( self ):
		"""
		define method
		���Ӱ���ճ��������
		"""
		timeTuple = time.gmtime()
		day = str( timeTuple[0] ) + str( timeTuple[1] ) + str( timeTuple[2] )
		record = self.tongNormalRecord.split("_")
		if len(record) == 1 or record[0] != day:
			self.tongNormalRecord = day + "_" + "1"
			return
		else:
			n = int(record[1]) + 1
			self.tongNormalRecord = record[0] + "_" + str(n)

	def queryTongNormalCount(  self, playerMB, questID ):
		"""
		define method added by dqh
		��ѯ����ճ��������
		"""
		timeTuple = time.gmtime()
		day = str( timeTuple[0] ) + str( timeTuple[1] ) + str( timeTuple[2] )
		count = TONG_NORMAL_QUEST_MAX_MAP[self.level]
		record = self.tongNormalRecord.split("_")

		if len(record) == 1 or record[0] != day:
			playerMB.cell.remoteQuestAccept( questID )
			return

		if int(record[1]) < count:
			playerMB.cell.remoteQuestAccept( questID )
			return

		playerMB.client.onStatusMessage( csstatus.TONG_NORMAL_QUEST_MOST, "" )

	def clearTongDartRecord( self ):
		"""
		define method
		"""
		self._dartRecord = ""

	def setTongFactionCount( self, count ):
		"""
		define method
		���ð��ʱװ������
		"""
		self.factionCount = count

	#--------------------------------------������----------------------------------------------------------
	def onContributeToMoney( self, playerBase, playerName, money ):
		"""
		define method
		�����׽�Ǯ
		"""
		ConTimes = 100000				# ÿ���1�㹱�׶���Ҫ���׵Ľ�Ǯ��
		if money <= 0:
			return

		val = Const.TONG_MONEY_LIMIT[ self.jk_level ][ 1 ] - self.money
		val1 = money - val

		if val1 > 0:
			money -= val1

		if money <= 0:
			self.statusMessage( playerBase, csstatus.TONG_MONEY_MAX )
			return
		self.addMoney( money, csdefine.TONG_CHANGE_MONEY_CONTRIBUTE_TO )
		playerBase.cell.tong_onContributeToMoneySuccessfully( money, val1 > 0 )
		contribute = money / ConTimes 	# Ӧ�����ӵĹ��׶�
		if contribute:
			playerBase.cell.tong_addContribute( contribute )
			self.statusMessageToOnlineMember( csstatus.TONG_CONTRIBUTE_TO_MONEY_SUCCESS_2, playerName, Function.switchMoney( money ), contribute, playerName )
		else:
			self.statusMessageToOnlineMember( csstatus.TONG_CONTRIBUTE_TO_MONEY_SUCCESS, playerName, Function.switchMoney( money ), playerName )


	# -------------------------------------��� by ����--------------------------------------------
	def setTongSignMD5( self, iconMD5 ):
		"""
		define method
		"""
		self.tongSignMD5 = iconMD5
		Love3.g_tongSignMgr.changeTongSign( self.databaseID, iconMD5 )
		# ֪ͨ����Ա����
		for dbid in self._onlineMemberDBID:	# ֪ͨ�����������
			memberMB = self.getMemberInfos( dbid ).getBaseMailbox()
			if memberMB is None:
				continue
			memberMB.client.tong_onSetTongSignMD5( iconMD5 )

	def getTongSignMD5( self, tongDBID, playerMB ):
		"""
		exposed method
		����DBID��ȡ�������İ����DBID
		"""
		if not Love3.g_tongSignMgr.hasDymTongSignDatas( tongDBID ):
			return
		iconMD5 = Love3.g_tongSignMgr.getDymTongSignMD5( tongDBID )
		playerMB.client.onGetTongSignMD5( tongDBID, iconMD5 )

	def sendTongSignString( self, tongDBID, playerMB ):
		"""
		defined method
		�����귢�͸��ͻ���
		"""
		iconString = Love3.g_tongSignMgr.getTongSignStrByDBID( tongDBID )
		iconStringList = []
		iconstrlen = len( iconString )
		packs_num = int( iconstrlen/250 ) + 1
		for i in xrange( 0, packs_num ):
			index = i * 250
			end = index + 250
			sList = iconString[index:end]
			iconStringList.append( sList )
		playerMB.tongSignSendStart( self.databaseID, self.tongSignMD5, iconStringList )

	def submitTongSign( self, iconString, iconMD5, playerMB ):
		"""
		define method.
		�ϴ����ͼ��

		@param iconString : ͼ��ת���ɵ��ַ���
		@type  iconString : STRING
		@param iconMD5 : ͼ�����ɵ�MD5��
		@type  iconMD5 : INT64
		"""
		# �۷�
		cost = 1 * csconst.USER_TONG_SIGN_REQ_MONEY
		if cost != 0:
			if self.getValidMoney() < cost:
				playerMB.client.onStatusMessage( csstatus.TONG_SIGN_CHANGE_NOT_MONEY, "" )
				return
		Love3.g_tongSignMgr.submitTongSign( self.databaseID, self.getName(), iconString, iconMD5, playerMB )

	def changeTongSing( self, isSysIcon, reqMoney, iconMD5, playerMB ):
		"""
		define method.
		�������ͼ��

		@param iconMD5 : ͼ�����ɵ�MD5��
		@type  iconMD5 : INT64
		"""
		if self.tongSignMD5 == iconMD5:
			playerMB.client.onStatusMessage( csstatus.TONG_SIGN_USING_NOW, "" )
			return
		if iconMD5 == "sub":	# subΪ�����ϴ�����ָ��
			ics = Love3.g_tongSignMgr._TongSignMgr__iconDatas
			if ics.has_key( self.databaseID ):
				iconMD5 = Love3.g_tongSignMgr._TongSignMgr__datas[self.databaseID]
				if self.tongSignMD5 == iconMD5:
					playerMB.client.onStatusMessage( csstatus.TONG_SIGN_USING_NOW, "" )
					return
			else:
				playerMB.client.onStatusMessage( csstatus.TONG_SIGN_SUBMIT_PLEASE, "" )
				return
		if self.getValidMoney() < reqMoney:
			playerMB.client.onStatusMessage( csstatus.TONG_SIGN_CHANGE_NOT_MONEY, "" )
			return
		if not isSysIcon and not Love3.g_tongSignMgr.hasUserTongSignDatas( self.databaseID, iconMD5 ):
			ERROR_MSG( "Tong %s(%i) not has that user define Icon."%( self.getName(), self.databaseID ) )
			return
		# �۷�
		if reqMoney != 0:
			if not self.payMoney( reqMoney, True, csdefine.TONG_CHANGE_MONEY_SUBMIT_TONG_SIGN ):
				ERROR_MSG( "change TongSign pay Money Failed." )
				return
		self.setTongSignMD5( iconMD5 )
		playerMB.client.onStatusMessage( csstatus.TONG_SIGN_CHANGE_SUCCESS, "" )

	# ------------------------- �����̨����� ------------------------------
	def requestAbattoir( self, playerBaseEntity ):
		"""
		Define method.
		��������̨��

		@param playerBaseEntity : ������base mailbox
		@type playerBaseEntity : MAILBOX
		"""
		self.calBasePrestige()
		# variablePrestige = self.prestige - self.basePrestige
		#if variablePrestige < csconst.TONG_ABATTOIR_PRESTIGE_LIMIT:
		#	self.statusMessage( playerBaseEntity, csstatus.TONG_ABATTOIR_PRESTIGE_LIMIT )
		#	return

		# CSOL-9992 �����̨����Ҫ���޸�Ϊ������
		if self.prestige < csconst.TONG_ABATTOIR_PRESTIGE_LIMIT:
			self.statusMessage( playerBaseEntity, csstatus.TONG_ABATTOIR_PRESTIGE_LIMIT )
			return

		self.getTongManager().requestAbattoir( playerBaseEntity, self.databaseID )

	def onWarKillerPlayer( self, isKiller, memberDBID ):
		"""
		define method.
		�����̨�����˱�ɱ����ɱ��֪ͨ
		"""
		key = csstatus.TONG_WAR_KILL_TO
		if not isKiller:
			key = csstatus.TONG_WAR_KILL_FROM
		self.statusMessageToOnlineMember( key, self.getMemberInfos( memberDBID ).getName() )

	def onWarBuyItemsMessage( self, memberDBID, itemCount, itemName, payMarks ):
		"""
		define method.
		����ڸ����ڹ�����Ʒ ��������Ϣ
		"""
		name = self.getMemberInfos( memberDBID ).getName()
		self.statusMessageToOnlineMember( csstatus.TONG_WAR_BUY_INFO, name, itemCount, itemName, payMarks )
				
	def tongAbaGather( self,round ):
		"""
		֪ͨ����Ա��̨�����Ͽ�ʼ
		@param round : ��ǰ����
		@type round : UINT8
		"""
		self.tongAbaGatherFlag = round
		for dbid in self._onlineMemberDBID:			# ֪ͨ�����������
			memberMB = self.getMemberInfos( dbid ).getBaseMailbox()
			if memberMB is None:
				continue
			memberMB.client.tongAbaGather( round )
			memberMB.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TONG_ABA )
	
	def tongAbaCloseGather( self ):
		"""
		֪ͨ����Ա��̨�����Ͻ���
		"""
		self.tongAbaGatherFlag = None
		for dbid in self._onlineMemberDBID:			# ֪ͨ�����������
			memberMB = self.getMemberInfos( dbid ).getBaseMailbox()
			if memberMB is None:
				continue
			memberMB.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TONG_ABA )

	def tongCompetitionGather( self,flag ):
		"""
		define method
		֪ͨ����Ա��Ὰ�����Ͽ�ʼ
		@param round : ��־
		@type round : UINT8
		"""
		self.tongCompetitionGatherFlag = flag
		for dbid in self._onlineMemberDBID:			# ֪ͨ�����������
			memberMB = self.getMemberInfos( dbid ).getBaseMailbox()
			if memberMB is None:
				continue
			memberMB.client.tongCompetitionGather()
			memberMB.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TONG_COMPETITION )
	
	def tongCompetitionCloseGather( self ):
		"""
		define method
		֪ͨ����Ա��Ὰ�����Ͻ���
		"""
		self.tongCompetitionGatherFlag = None
		for dbid in self._onlineMemberDBID:			# ֪ͨ�����������
			memberMB = self.getMemberInfos( dbid ).getBaseMailbox()
			if memberMB is None:
				continue
			memberMB.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TONG_COMPETITION )


	def updateTongAbaRound( self,round ):
		"""
		�����̨��ǰ�����������
		"""
		self.tongAbaRound = round
		for dbid in self._onlineMemberDBID:			# ֪ͨ�����������
			memberMB = self.getMemberInfos( dbid ).getBaseMailbox()
			if memberMB is None:
				continue
			memberMB.client.receiveAbaRound( round )

	# ------------------------- ��Ὰ����� ------------------------------

	def requestCompetition( self, playerBaseEntity ):
		"""
		Define method.
		��������̨��

		@param playerBaseEntity : ������base mailbox
		@type playerBaseEntity : MAILBOX
		"""
		self.calBasePrestige()
		if self.prestige < csconst.TONG_ABATTOIR_PRESTIGE_LIMIT:
			self.statusMessage( playerBaseEntity, csstatus.TONG_ABATTOIR_PRESTIGE_LIMIT )
			return

		if not self.isTongMemberLimit():		# �������60�����������������ﵽ10��������
			self.statusMessage( playerBaseEntity, csstatus.TONG_COMPETETION_NOTICE_4 )
			return

		BigWorld.globalData["TongCompetitionMgr"].onRequestCompetition( playerBaseEntity, self.databaseID )

	def isTongMemberLimit( self ):
		"""
		ͳ���Լ����60�������������
		"""
		memberCount = len( self._memberInfos )
		if memberCount == 0:	# û�а���Ա
			return False
		if memberCount >= COMPETITION_MEMBER_LIMIT:
			k = 0
			for info in self._memberInfos.itervalues():
				tongMemberLevel = info.getLevel()
				if tongMemberLevel >= COMPETITION_LEVEL_LIMIT:
					k += 1
			return k >= COMPETITION_MEMBER_LIMIT
		else:
			return False

	def sendAwardToChief( self ):
		"""
		Define method.
		�����������ͳһ���ͽ������ھ�����������
		"""
		chiefName = self.chiefName		# ��������
		itemDatas = []
		item = g_item.createDynamicItem( 60101261, 1 )
		if item:
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
			itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )
			BigWorld.globalData["MailMgr"].send(None, chiefName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC,"", cschannel_msgs.TONGCOMPETITION_CHIEF_MAIL_REWARD_TITLE, "", 0, itemDatas)
	
	# ---------------------------------- ������ȡٺ»���--------------------------------------------
	def calTongSalary( self ):
		"""
		define mehtod
		������ٺ»�������
		"""
		self.lastWeekTongTotalMoney = self.weekTongMoney					# ���ܰ���ʽ�������
		self.weekTongMoney = 0
		
		self.lastWeekSalaryExchangeRate = self.weekSalaryExchangeRate		# ����ٺ»�һ���
		self.weekSalaryExchangeRate = self.nextWeekSalaryExchangeRate		# ����ٺ»�һ���
		
		self.lastWeekTotalExchangedSalary = self.weekTotalExchangedSalary	# ���ܰ��ʵ��ٺ»֧��
		self.weekTotalExchangedSalary = 0
		
		self.lastWeekTongTotalContribute = self.weekTongTotalContribute 	# ���ܰ��ﹱ��ֵ 
		self.weekTongTotalContribute = 0
		
		self.lastWeekTongTotalCost = self.weekTotalCost						# ���ܰ���ʽ���֧��
		self.weekTotalCost = 0
		
		self.lastWeekTongMoneyRemain = self.money							# ���ܰ���ʽ����
		
		# ����Ա�����������
		for memberDBID, memberInfo in self._memberInfos.iteritems():
			for item in self.memberTotalContributes:
				if item[ "dbID" ] == memberDBID:
					item[ "lastWeekTotalContribute" ] = memberInfo.getWeekTongContribute()
					memberInfo.setLastWeekTotalContribute( memberInfo.getWeekTongContribute() )
					item[ "weekTongContribute" ] = 0
					memberInfo.updateWeekTongContribute( 0 )
					
					item[ "lastWeekSalaryReceived" ] = memberInfo.getWeekSalaryReceived()
					memberInfo.setLastWeekSalaryReceived( memberInfo.getWeekSalaryReceived() ) 
					item[ "weekSalaryReceived" ] = 0
					memberInfo.setWeekSalaryReceived( 0 )
					
	def requestMemberContributeInfos( self, userDBID ):
		"""
		define method
		�ͻ������󱾰����ҵİﹱ��Ϣ:�ۼưﹱ��ֵ��ʣ��ﹱֵ�����ܻ�ðﹱ�����ܻ�ðﹱ
		"""
		for dbid in self._onlineMemberDBID:
			info = self.getMemberInfos( dbid )
			info.getBaseMailbox().client.tong_updateMemberContributeInfos( dbid, info.getTotalContribute(), \
							info.getContribute(), info.getWeekTongContribute(), info.getLastWeekTotalContribute() )
	
	def onRequireSalaryInfo(self, baseEntity, playerDBID ):
		"""
		define method 
		�ͻ����������ٺ»��Ϣ
		"""
		info = self.getMemberInfos( playerDBID )
		lastWeekTotalContribute = info.getLastWeekTotalContribute()			# ���ܻ�ȡ�ﹱ�ۼ���ֵ
		lastWeekSalaryChangeRate = self.lastWeekSalaryExchangeRate			# ���ܰ��ٺ»�һ���
		lastReceivedSalary = info.getLastWeekSalaryReceived()				# ������ȡٺ»�ܶ�
		thisWeelTotalContribute = info.getWeekTongContribute()				# ���ܻ�ȡ�ﹱ�ۼ���ֵ
		thisWeekSalaryChangeRate = self.weekSalaryExchangeRate				# ���ܰ��ٺ»�һ���
		baseEntity.client.tong_receiveSalaryInfo( lastWeekTotalContribute, lastWeekSalaryChangeRate, lastReceivedSalary,\
							thisWeelTotalContribute, thisWeekSalaryChangeRate )
							
	def onClientOpenTongMoneyWindow( self, playerBase ):
		"""
		define method 
		�ͻ��˴��˰���ʽ��ӽ��棬����������
		"""
		# ���ܰ���ʽ������롢����ٺ»�һ�����ܰﹱ��ֵ�����ܰ��ٺ»ʵ��֧�������ܰ���ʽ���֧�������ܰ���ʽ����
		lastWeekInfo = [ self.lastWeekTongTotalMoney, self.lastWeekSalaryExchangeRate, self.lastWeekTongTotalContribute, \
						self.lastWeekTotalExchangedSalary, self.lastWeekTongTotalCost, self.lastWeekTongMoneyRemain ]
		# ���ܰ���ʽ����롢���ܰ��ٺ»�һ�����ܰ��ﹱ��ֵ�����ܰ���ʽ�֧�������ܰ��һ���
		thisWeekInfo = [ self.weekTongMoney, self.weekSalaryExchangeRate, self.weekTongTotalContribute, self.weekTotalCost,self.nextWeekSalaryExchangeRate ]
		
		playerBase.client.tong_receiveTongMoneyInfo( lastWeekInfo, thisWeekInfo )

	def onDrawTongSalary( self, memberDBID ):
		"""
		define method
		�����ȡٺ»
		"""
		info = self.getMemberInfos( memberDBID )
		
		if info.getWeekTongContribute() == 0:			# ���ܰﹱΪ0
			self.statusMessage( info.getBaseMailbox(), csstatus.TONG_SALARY_HAVE_NO_CONTRIBUTE )
			return 
		
		if info.getWeekSalaryReceived() > 0:			# �Ѿ���ȡ��ٺ»
			self.statusMessage( info.getBaseMailbox(), csstatus.TONG_SALARY_ALREDY_RECEIVED )
			return 
			
		weekSalaryReceive = info.getWeekTongContribute() * self.weekSalaryExchangeRate 		# �����ܰﹱ * ����ÿ����һ���*ͭ/��
		
		if not self.payMoney( weekSalaryReceive, True, csdefine.TONG_CHANGE_MONEY_SALARY ):			# ����ʽ�С�ڱ����ʽ�
			self.statusMessage( info.getBaseMailbox(), csstatus.TONG_LSEE_KEEP_MONEY )
			return 
		
		info.setWeekSalaryReceived( weekSalaryReceive )
		# ������Ҫ����Ϣͬ�������ĳ�Ա�ṹ��
		for item in self.memberTotalContributes:
			if item[ "dbID" ] == memberDBID:
				item[ "weekSalaryReceived" ] = weekSalaryReceive
		self.weekTotalExchangedSalary += weekSalaryReceive												# ���ܰ��֧��ٺ»
		if self.holdCity:
			weekSalaryReceive *=2
		
		info.getBaseMailbox().cell.addMoney( weekSalaryReceive, csdefine.TONG_CHANGE_MONEY_SALARY )		# ��������ϼ�Ǯ
		self.statusMessage( info.getBaseMailbox(), csstatus.TONG_SALARY_DRAW_SUCCESS )
	
	def setContributeExchangeRate( self, memberDBID, rate ):
		"""
		define method
		�����趨���ٺ»�һ���
		"""
		info = self.getMemberInfos( memberDBID )
		if not self.checkMemberDutyRights( info.getGrade(), csdefine.TONG_RIGHT_SALARY_RATE):	# ������ǰ���������	
			return
		self.nextWeekSalaryExchangeRate = rate
		self.statusMessage( info.getBaseMailbox(), csstatus.TONG_SET_SALARY_CHANGE_RATE_SUCCESS, rate )	
		info.getBaseMailbox().client.tong_updateNextWeekExchangeRate( self.nextWeekSalaryExchangeRate )
	
	def queryTongChiefInfos( self ):
		# define method
		# ��ȡ����ģ����Ϣ
		if self.getMemberInfos( self.chiefDBID ).isOnline():
			self.getMemberInfos( self.chiefDBID ).getBaseMailbox().cell.tong_queryTongChiefInfos()
		else:
			self.queryDatabaseChiefInfos()
	
	def queryDatabaseChiefInfos( self ):
		sqlStr = "SELECT sm_raceclass, sm_hairNumber, sm_faceNumber, sm_bodyFDict_iLevel, sm_bodyFDict_modelNum, sm_volaFDict_iLevel,sm_volaFDict_modelNum, sm_breechFDict_iLevel, sm_breechFDict_modelNum, sm_feetFDict_iLevel, sm_feetFDict_modelNum, sm_lefthandFDict_iLevel, sm_lefthandFDict_modelNum, sm_lefthandFDict_stAmount, sm_righthandFDict_iLevel, sm_righthandFDict_modelNum, sm_righthandFDict_stAmount, sm_talismanNum, sm_fashionNum, sm_adornNum from tbl_Role where id =%d" % self.chiefDBID
		
		def queryTableResult( result, rows, errstr ):
			infosData = [ int( i ) for i in result[0] ]
			obj = MasterChiefData()
			obj[ "uname" ]  = self.chiefName
			obj[ "tongName" ] = self.playerName
			obj[ "raceclass" ] = infosData[ 0 ]
			obj[ "hairNumber" ] = infosData[ 1 ]
			obj[ "faceNumber" ] = infosData[ 2 ]
			obj[ "bodyFDict" ] = { "iLevel":infosData[3], "modelNum":infosData[4] }
			obj[ "volaFDict" ] = { "iLevel":infosData[5], "modelNum":infosData[6] }
			obj[ "breechFDict" ] = { "iLevel":infosData[7], "modelNum":infosData[8] }
			obj[ "feetFDict" ] = { "iLevel":infosData[9], "modelNum":infosData[10] }
			obj[ "lefthandFDict" ] = { "iLevel":infosData[11], "modelNum":infosData[12], "stAmount": infosData[13] }
			obj[ "righthandFDict" ] = { "iLevel":infosData[14], "modelNum":infosData[15], "stAmount": infosData[16] }
			obj[ "talismanNum" ] = infosData[ 17 ]
			obj[ "fashionNum" ] = infosData[ 18 ]
			obj[ "adornNum" ] = infosData[ 19 ]
			BigWorld.globalData[ "TongManager" ].cityWarOnQueryMasterInfo( self.databaseID, obj )
		
		BigWorld.executeRawDatabaseCommand( sqlStr, queryTableResult )
		
	def infoCallMember( self, userDBID, lineNumber, spaceName, position, direction, limitLevel, showMessage ):
		"""
		define method
		"""
		if len( self._onlineMemberDBID ) < 2:
			return

		userInfo = self.getMemberInfos( userDBID )
		user = userInfo.getBaseMailbox()
		
		for dbid in self._onlineMemberDBID:
			memberLevel = self.getMemberInfos( dbid ).getLevel()				# ���߰���Ա�ȼ�
			casterLevel = self.getMemberInfos( userDBID ).getLevel()			# ʩ���ߵĵȼ�
			casterName = self.getMemberInfos( userDBID ).getName()				# ʩ���ߵ�����
			if userDBID != dbid and (( memberLevel >= casterLevel - limitLevel ) and ( memberLevel <= casterLevel + limitLevel )):
				self.getMemberInfos( dbid ).getBaseMailbox().client.infoTongMember( lineNumber, casterName, showMessage, spaceName, position, direction )
				
	def addTongTurnWarPoint( self, cityName, amount ):
		"""
		define method
		
		�����ӳ���ս����
		
		@param cityName: �ĸ����еĻ���
		@param amount: ��ֵ
		"""
		for oneCityPoint in self.tongTurnWarPoint:		# tongTurnWarPoint �ṹΪ[ { "cityName", "point" } ]
			if oneCityPoint["cityName"] == cityName:
				oneCityPoint["point"] += amount
				self.getTongManager().updateTongTurnWarPoint( self.databaseID, cityName, oneCityPoint["point"] )
				self.writeToDB()
				return
				
		#����б���û�иó��еĻ�����Ϣ������Ҫ���
		info = { "cityName": cityName, "point": amount }
		self.tongTurnWarPoint.append( info )
		self.getTongManager().updateTongTurnWarPoint( self.databaseID, cityName, amount )
		self.writeToDB()
		
	def roleRequestTongExp( self, roleDBID ):
		"""
		define method
		��������ᾭ������
		"""
		if roleDBID not in self._onlineMemberDBID:
			return
		
		roleMB = self.getMemberInfos( roleDBID ).getBaseMailbox()
		if roleMB and not self.hasDelayTaskData( roleDBID, TASK_KEY_TONG_EXP ):
			roleMB.client.tong_onSetTongExp( self.EXP )

	# -------------------------------------------------ս�����˹���-------------------------------------------

	def inviteTongBattleLeague( self, inviterDBID, inviteeTongDBID, msg, maxNum ):
		"""
		define method
		���������ս������
		"""
		self.battleLeagueMaxNum = maxNum
		DEBUG_MSG( "TONG: %i invite tong %s to battle league." % ( inviterDBID, inviteeTongDBID ) )
		inviter = self.getMemberInfos( inviterDBID ).getBaseMailbox()
		inviterGrade = self.getMemberInfos( inviterDBID ).getGrade()
		# Ȩ�޼��
		if not self.checkMemberDutyRights( inviterGrade, csdefine.TONG_RIGHT_LEAGUE_MAMAGE ):
			self.statusMessage( inviter, csstatus.TONG_GRADE_INVALID )
			return
		
		if inviteeTongDBID <= 0:
			self.statusMessage( inviter, csstatus.TONG_TARGET_TONG_NO_FIND )
			return
		
		# ���ս�����˰�������ж�
		if len( self.battleLeagues ) >= self.battleLeagueMaxNum:
			self.statusMessage( inviter, csstatus.TONG_BATTLE_LEAGUE_FULL)
			return
		
		# �Ƿ��Ѿ��ύ������
		if self._inviteBattleLeagueRecord.has_key( inviteeTongDBID ):
			self.statusMessage( inviter, csstatus.TONG_WAITING_RESPONSE )
			return
		
		dict = {}
		dict[ "inviterDBID" ] = inviterDBID
		dict[ "inviteeTongDBID" ] = inviteeTongDBID
		dict[ "time" ] = BigWorld.time()
		self._inviteBattleLeagueRecord[ inviteeTongDBID ] = dict
		self.getTongManager().onInviteTongBattleLeague( inviter, self.databaseID, inviteeTongDBID, msg )

		# ���û��ʱ�Ӽ���� ��ô��������ʱ����
		if self._check_inviteBattleLeagueTimerID <= 0:
			self._check_inviteBattleLeagueTimerID = self.addTimer( CONST_REQUEST_JOIN_TIMEOUT, CONST_REQUEST_JOIN_TIMEOUT, TIME_CBID_CHECK_REQUEST_JOIN )

	def receiveBattleLeagueInvitation( self, inviter, inviterTongName, inviterTongDBID, msg, maxNum ):
		"""
		define method
		�����뷽����յ�ս���������� ���岽
		@param inviter				:ʹ�ù�����baseMailbox
		@param userTongName		:ʹ�ù����� ��������
		@param userTongDBID		:ʹ�ù����� ����DBID
		"""
		self.battleLeagueMaxNum = maxNum
		# ���ս�����˰�������ж�
		if len( self.battleLeagues ) > self.battleLeagueMaxNum:
			self.statusMessage( inviter, csstatus.TONG_TARGET_BATTLE_LEAGUE_FULL)
			self.getTongManager().onInviteTongBattleLeagueFailed( inviterTongDBID, self.databaseID )
			return

		for dbid, info in self._memberInfos.iteritems():
			if self.checkMemberDutyRights( info.getGrade(), csdefine.TONG_RIGHT_LEAGUE_MAMAGE ):
				if info.isOnline():
					info.getBaseMailbox().client.tong_receiveBattleLeagueInvitation( inviterTongName, inviterTongDBID, msg )
					return

		self.statusMessage( inviter, csstatus.TONG_BATTLE_LEAGUE_CHIEF_OFFLINE )
		self.getTongManager().onInviteTongBattleLeagueFailed( inviterTongDBID, self.databaseID )

	def onInviteTongBattleLeagueFailed( self, inviteeTongDBID ):
		"""
		define method
		����ս��ͬ�˰��ʧ��
		"""
		self._inviteBattleLeagueRecord.pop( inviteeTongDBID )

	def replyBattleLeagueInvitation( self, replierBaseMailbox, inviterTongDBID, response ):
		"""
		define method
		��������ظ�ս����������
		"""
		# ���ս�����˰�������ж�
		if len( self.battleLeagues ) > self.battleLeagueMaxNum:
			self.statusMessage( replierBaseMailbox, csstatus.TONG_TARGET_BATTLE_LEAGUE_FULL)
			self.getTongManager().onInviteTongBattleLeagueFailed( inviterTongDBID, self.databaseID )
			return
		
		self.getTongManager().replyBattleLeagueInvitation( replierBaseMailbox, self.databaseID, inviterTongDBID, response )

	def receiveBattleLeagueReply( self, replierBaseMailbox, replierTong, replierTongDBID, replierTongName, response ):
		"""
		define method
		�յ�����ظ�
		"""
		DEBUG_MSG( "TONG: %i answer tong %i to battle league." % ( replierTongDBID, self.databaseID ) )
		
		if replierTongDBID not in self._inviteBattleLeagueRecord:
			return
		
		info = self._inviteBattleLeagueRecord[ replierTongDBID ]
		# ��ʱ�� ����
		if self.checkRequestLeagueTimeOut( info[ "time" ] ):
			return
		inviter = self.getMemberInfos( info[ "inviterDBID" ] ).getBaseMailbox()
		inviteeTongDBID = info[ "inviteeTongDBID" ]
		del self._inviteBattleLeagueRecord[ replierTongDBID ]
		
		if len( self.battleLeagues ) >= self.battleLeagueMaxNum:
			self.statusMessage( replierBaseMailbox, csstatus.TONG_TARGET_BATTLE_LEAGUE_FULL )
			return
		
		if not response:	# �ܾ�
			if inviter:
				self.statusMessage( inviter, csstatus.TONG_BATTLE_LEAGUE_FAIL, replierTongName )
			return
		
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BHGL_BATTLE_ALIGNMENT_NOTIFY % ( replierTongName, self.playerName ), [] )
		replierTong.addBattleLeague( self.databaseID, self.playerName )
		self.onAddBattleLeague( replierTongDBID, replierTongName )

	def addBattleLeague( self, leagueDBID, leagueName ):
		"""
		define method
		�������ս��ͬ��
		"""
		if self.hasBattleLeaguesTong( leagueDBID ):
			ERROR_MSG( "TONG: battle league %s %i is exist." % ( leagueName, leagueDBID ) )
			return
		
		self.onAddBattleLeague( leagueDBID, leagueName  )

	def onAddBattleLeague( self, leagueDBID, leagueName ):
		"""
		������ս��ͬ��
		"""
		self.battleLeagues.append( { "dbID" : leagueDBID, "tongName" : leagueName, "tid" : 0, "ad" : "" } )
		if self.chiefDBID in self._onlineMemberDBID:
			userInfo = self.getMemberInfos( self.chiefDBID )
			userInfo.getBaseMailbox().client.tong_addBattleLeague( leagueDBID, leagueName )

		# �����ݸ��µ�������
		self.getTongManager().updateTongBattleLeagues( self.databaseID, self.battleLeagues )
	
	def hasBattleLeaguesTong( self, leagueDBID ):
		"""
		�ж��Ƿ��и�ս��ͬ�˰��
		"""
		for league in self.battleLeagues:
			if league[ "dbID" ] == leagueDBID:
				return True
		return False

	def onCheckRequestBattleLeagueTimer( self ):
		"""
		ɾ����ʱ��ս����������
		"""
		outdatedInvite = []
		for key, info in self._inviteBattleLeagueRecord.iteritems():
			if self.checkRequestLeagueTimeOut( info[ "time" ] ):
				outdatedInvite.append( key )

		for key in outdatedInvite:
			self._inviteBattleLeagueRecord.pop( key )

		if len( self._inviteBattleLeagueRecord ) <= 0:
			self.delTimer( self._check_inviteBattleLeagueTimerID )
			self._check_inviteBattleLeagueTimerID = 0

	def requestBattleLeagueDispose( self,  userDBID, battleLeagueDBID ):
		"""
		define method
		�ͻ���������ս��ͬ��
		"""
		if userDBID != -1:
			user = self.getMemberInfos( userDBID ).getBaseMailbox()
			userGrade = self.getMemberInfos( userDBID ).getGrade()
			# Ȩ���ж�
			if not self.checkMemberDutyRights( userGrade, csdefine.TONG_RIGHT_LEAGUE_MAMAGE ):
				self.statusMessage( user, csstatus.TONG_GRADE_INVALID )
				return
		
		self.onBattleLeagueDispose( battleLeagueDBID, True )

	def battleLeagueDispose( self, leagueTongDBID ):
		"""
		define method
		�������ս��ͬ�˹�ϵ
		"""
		self.onBattleLeagueDispose( leagueTongDBID, False )

	def onBattleLeagueDispose( self, battleLeagueDBID, initiative ):
		"""
		������ս��ͬ��
		@param initiative: �Ƿ��������ͬ�˹�ϵ
		"""
		msgKey = csstatus.TONG_BATTLE_LEAGUE_QUIT_TO
		if not initiative:
			msgKey = csstatus.TONG_BATTLE_LEAGUE_QUIT
		
		for idx, item in enumerate( self.battleLeagues ):
			if item[ "dbID" ] == battleLeagueDBID:
				self.battleLeagues.pop( idx )

				if initiative:
					self.getTongManager().onBattleLeagueDispose( battleLeagueDBID, self.databaseID )
				
				if self.chiefDBID in self._onlineMemberDBID:
					chiefMB = self.getMemberInfos( self.chiefDBID ).getBaseMailbox()
					chiefMB.client.tong_delBattleLeague( battleLeagueDBID )
				
				for dbid in self._onlineMemberDBID:
					member = self.getMemberInfos( dbid ).getBaseMailbox()
					self.statusMessage( member, msgKey, item[ "tongName" ] )

				break
				
	# ----------------------------------------���������Ʒ----------------------------------------------
	def initTongSpecialItems( self, reset = False ):
		"""
		��ʼ�����������Ʒ
		"""
		TongTerritory.onInitTongSpecialItems( self, reset )
		self.specItems = []
		itemDatas = g_tongSpecItems.getDatas()

		for itemID, item in itemDatas.iteritems():
			# ��ֹ������Ʒ��󼶱�
			if self.level >= item[ "reqTongLevel" ]:
				itemData = { "itemID":itemID, "amount":item["amount"], "reqMoney":item["reqMoney"]}
				self.specItems.append( itemData )
		
		self.specItems.sort( key = lambda item : item["itemID"], reverse = False )

	def resetTongSpecialItems( self ):
		"""
		define method
		���ð��������Ʒ
		"""
		self.initTongSpecialItems( 1 )

	def addSpecialItemReward( self,  itemID, amount ):
		"""
		define method
		����ᷢ��������Ʒ��������ŵ���������NPC
		û�н�Ǯ�Ͱ��ȼ�����Ҫ��
		"""
		rewardItem = { "itemID":itemID, "amount":amount, "reqMoney":0}
		copySpecItems = copy.deepcopy( self.specItems )
		copySpecItems.append( rewardItem )
		copySpecItems.sort( key = lambda item : item["itemID"], reverse = False )
		self.specItems = copySpecItems
		TongTerritory.onAddSpecialItemReward(  self, itemID, amount )

#
# $Log: not supported by cvs2svn $
# Revision 1.21  2008/08/15 07:38:22  kebiao
# add:getMemberInfos
#
# Revision 1.20  2008/08/14 09:11:34  kebiao
# ���Ӱ�Ṥ�ʹ���
#
# Revision 1.19  2008/08/12 08:52:02  kebiao
# ��Ӱ����������
#
# Revision 1.18  2008/07/24 02:04:47  kebiao
# �޸�Ȩ�޵�ʵ�ַ�ʽ
#
# Revision 1.17  2008/07/22 08:50:07  songpeifang
# ���ջƶ�Ҫ�������GUILD���ĳ���TONG����ΪTONG�ǰ�ᣬ��GUILD�Ǿɾ���
#
# Revision 1.16  2008/07/22 03:43:31  huangdong
# �޸��˰������һ���ӿ���
#
# Revision 1.15  2008/07/22 01:58:28  huangdong
# ���ư�������
#
# Revision 1.14  2008/07/02 02:36:35  kebiao
# ����һ�����ݿ�ָ��
#
# Revision 1.13  2008/07/02 02:02:18  kebiao
# ����Ȩ�����õĹ�ϵ���⣬ �������ñ��Լ�ְλ�ߵģ� Ҳ���ܰѱ�������
# �ı��Լ���
#
# Revision 1.12  2008/07/01 02:22:27  kebiao
# �������ְλ�����ж�
#
# Revision 1.10  2008/07/01 01:40:46  kebiao
# �޸�һ��Const.TONG_USE_GRADES��ַ������ɵ�һ��BUG
#
# Revision 1.9  2008/06/30 04:15:23  kebiao
# ���Ӱ��ְλ���Ʊ༭
#
# Revision 1.8  2008/06/27 09:02:25  kebiao
# ���������ٺ�ͬ�˹�ϵ�Զ���� һ��BUG����
#
# Revision 1.7  2008/06/27 08:25:52  kebiao
# ���������ٺ�ͬ�˹�ϵ�Զ����
#
# Revision 1.6  2008/06/27 07:12:31  kebiao
# �����˰��ͼ�����첽���ݴ������
#
# Revision 1.5  2008/06/23 08:11:31  kebiao
# ����ĳЩ�ط������ݿ⼰ʱ����
# ĳЩ���߳�Ա����ֵû�����ļ���һ��tick�������ݿ�,
# �������߳�Ա��ֵȴ��д����ɵĲ���Ԥ�ϵĴ���
#
# Revision 1.4  2008/06/21 03:42:50  kebiao
# �����ṱ�׶�
#
# Revision 1.3  2008/06/16 09:13:04  kebiao
# ����Ȩ���ϵ
#
# Revision 1.2  2008/06/14 09:18:51  kebiao
# ������Ṧ��
#
# Revision 1.1  2008/06/09 09:24:33  kebiao
# ���������
#
#
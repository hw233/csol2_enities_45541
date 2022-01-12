# -*- coding: gb18030 -*-
#
# $Id: TongManager.py,v 1.10 2008-08-25 09:30:09 kebiao Exp $
import sys
import cschannel_msgs
import ShareTexts as ST
import time
import BigWorld
import csdefine
import csstatus
import csconst
import Const
from bwdebug import *
from Function import Functor
from interface.TongCityWarManager import TongCityWarManager
from interface.TongTerritoryManager import TongTerritoryManager
from interface.TongRobWarManager import TongRobWarManager
from interface.TongFeteManager import TongFeteManager
from interface.TongAbattoirMgr import TongAbattoirMgr
from interface.TongTurnWarManager import TongTurnWarManager
from interface.TongFengHuoLianTianMgr import TongFengHuoLianTianMgr
from interface.TongCityWarFinalManager import TongCityWarFinalManager
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from MsgLogger import g_logger


CLEAR_CREATE_TEMP_DATA_INTERVAL = 5			# �����Ὠ����ʱ���ݵ�timer�����


def calcToPointTime( point ):
	"""
	ʼ�շ��� ��point��ʱ���  ����point=21�� ������������һ��21������Ҫ��ʱ��
	@param point: һ��ʱ��� ����21�� ֻ�������� ������24
	"""
	t = time.localtime()
	h = t[ 3 ]
	m = t[ 4 ]
	s = t[ 5 ]
	h = point - h

	if h <= 0:
		h = point + ( 24 - t[ 3 ] )

	if m > 0:
		m = 60 - m
		h -= 1

	if s > 0:
		s = 60 - s
		m -= 1
	return abs( ( h * 60 * 60 ) + ( m * 60 ) + s )

CLEAR_REQUESTJOINTONGINFO_POINT = 24

class TongManager( BigWorld.Base,
				   TongCityWarManager,
				   TongTerritoryManager,
				   TongRobWarManager,
				   TongFeteManager,
				   TongAbattoirMgr,
				   TongTurnWarManager,
				   TongFengHuoLianTianMgr,
				   TongCityWarFinalManager,
):
	def __init__( self ):
		BigWorld.Base.__init__( self )
		TongCityWarManager.__init__( self )
		TongTerritoryManager.__init__( self )
		TongRobWarManager.__init__( self )
		TongFeteManager.__init__( self )
		TongAbattoirMgr.__init__( self )
		TongTurnWarManager.__init__( self )
		TongFengHuoLianTianMgr.__init__( self )
		TongCityWarFinalManager.__init__( self )

		self._tongBaseDatas = {}										# ���������� ���� ������ơ������������������ȼ�������������������ǰ���衱����ռ����С��������ͬ�ˡ�
																		# ������ÿ�������ͻ�����ݿ��в�ѯһ�Σ� ֮����������߰��ı�ĳЩ����Ҳ����½�����
		self._enterTongMembers_temp = {}								# ��һ�����Entity��δ������ʱ ��ԱҪ��������ʱ��¼����. �ڴ�������Щ��Ա������entity�����
		self._tongEntitys = {}											# ���еİ��ʵ�� { dbid: tongEntity }
		
		self.tempCreateInfo = {}				# ���ڽ����İ����Ϣ�����������һ���첽���̣�like as:{creatorDBID:(tongName,recordTime,tongEntity), ... }����¼������ʾ�������������Ѿ�ͨ����֤��
		self.clearTempCreateInfoTimerID = 0		# ������ڽ��������ʱ���ݵ�timerID
		
		self.loadAllTongTimerID = 0										# ���ذ���timerID
		self.loadAllTongBaseDatas()										# �������еİ��Ļ�������
		self.registerGlobally( "TongManager", self.onRegisterTongManager )
		
	#--------------------------------------------------------------------------------------------------------------------------
	def onManagerInitOver( self ):
		"""
		virtual method.
		��������ʼ�����
		"""
		TongCityWarManager.onManagerInitOver( self )
		TongRobWarManager.onManagerInitOver( self )
		TongTerritoryManager.onManagerInitOver( self )
		TongFeteManager.onManagerInitOver( self )
		TongAbattoirMgr.onManagerInitOver( self )
		TongTurnWarManager.onManagerInitOver( self )
		TongFengHuoLianTianMgr.onManagerInitOver( self )
		TongCityWarFinalManager.onManagerInitOver( self )
		self.tongManagerRegisterCrond()

	#-------------------------TongManager�������س�ʼ����ע��-----------------------------------------------------------------
	def onRegisterTongManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register TongManager Failed!" )
			# again
			self.registerGlobally( "TongManager", self.onRegisterTongManager )
		else:
			DEBUG_MSG( "TongManager Register Succeed!" )
			BigWorld.globalData["TongManager"] = self					# ע�ᵽ���еķ�������
			if self.playerName == "":
				DEBUG_MSG( "TongManager Write To DB Now..." )
				self.playerName = "TongManager"
				self.writeToDB( self.onCreatedTongManager )

	def onCreatedTongManager( self, success, entity ):
		"""
		��ʵ��д�����ݿ�ص�
		"""
		if success:
			DEBUG_MSG( "TongManager Write To Data Base Succeed!" )
		else:
			ERROR_MSG( "TongManager can't write to DataBase!" )

	def statusMessage( self, targetBaseMailbox, statusID, *args ) :
		"""
		send status message
		@type			statusID : INT32
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		args = args == () and "" or str( args )
		targetBaseMailbox.client.onStatusMessage( statusID, args )

	def statusTongMessage( self, tongEntity, statusID, *args ) :
		"""
		send status message
		@type			statusID : INT32
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		args = args == () and "" or str( args )
		tongEntity.onStatusMessage( statusID, args )

	#--------------------------�����ݿ���ذ�ᡡ��ʼ��----------------------------------------------------------------
	def onLoadAllTongOver( self ):
		"""
		virtual method.
		���а��������.
		"""
		TongCityWarManager.onLoadAllTongOver( self )

	def onLoadAllTongTimer( self ):
		"""
		���ذ��timer������
		"""
		if len( self.tmpTongInfos ) <= 0:
			return

		for x in xrange( 1 ):
			dbID = self.tmpTongInfos.pop(0)
			tongInfo = self._tongBaseDatas[ dbID ]
			if dbID > 0:
				BigWorld.createBaseFromDBID( "TongEntity", dbID, Functor( self.onCreateTongEntityBaseFromDBID, dbID, tongInfo["tongName"] ) )

			if len( self.tmpTongInfos ) <= 0:
				self.delTimer( self.loadAllTongTimerID )
				self.loadAllTongTimerID = 0
				self.onLoadAllTongOver()
				DEBUG_MSG( "All tong[count=%i] is load complete! use time:%s" % ( len( self._tongBaseDatas ), time.time() - self.loadAllTongTime ) )
				del self.tmpTongInfos
				del self.loadAllTongTime
				return
		
	def onCreateTongEntityBaseFromDBID( self, tongDBID, tongName, baseRef, databaseID, wasActive ):
		"""
		���ذ��entityʱcreateBaseFromDBID�ص���
		"""
		assert wasActive is False, "%s(%i): the target entity was active, I can't do it. tongDBID %i %s" % ( self.playerName, self.id, tongDBID, tongName )
		if baseRef == None:
			ERROR_MSG( "TongEntity Create From DBID Error! tongDBID %i, tongName:%s" % ( tongDBID, tongName ) )
		else:
			pass

	def loadTongByDBIDFromDB( self, tongDBID ):
		"""
		�����ݿ���ذ��
		"""
		if tongDBID != 0:
			if hasattr( self, "tmpTongInfos" ):
				for tongDBID in self.tmpTongInfos:
					self.tmpTongInfos.remove( tongDBID )
					break
				else:
					return
			else:
				return
			BigWorld.createBaseFromDBID( "TongEntity", tongDBID, Functor( self.onCreateTongEntityBaseByDBIDFromDBID, tongDBID ) )
		else:
			ERROR_MSG( "create tong dbid=%i is failed." % ( tongDBID ) )

	def onCreateTongEntityBaseByDBIDFromDBID( self, tongDBID, baseRef, databaseID, wasActive ):
		"""
		���ذ��entityʱcreateBaseFromDBID�ص���
		"""
		assert wasActive is False, "%s(%i): the target entity was active, I can't do it. tongDBID %i" % ( self.playerName, self.id, tongDBID )
		if baseRef == None:
			ERROR_MSG( "TongEntity Create From DBID Error! tongDBID %i" % ( tongDBID ) )
		else:
			pass

	def onTongEntityLoadMemberInfoComplete( self, tongDBID, tongEntity, chiefName ):
		"""
		virtual method.
		���ʵ��������Ա������
		"""
		self._tongEntitys[ tongDBID ] = tongEntity
		self._tongBaseDatas[tongDBID]["chiefName"] = chiefName
		TongCityWarManager.onTongEntityLoadMemberInfoComplete( self, tongDBID, tongEntity, chiefName )

		if self._enterTongMembers_temp.has_key( tongDBID ):
			for info in self._enterTongMembers_temp[ tongDBID ]:
				tongEntity.onMemberLogin( info[ "baseEntity" ], info[ "dbid" ] )
			self._enterTongMembers_temp.pop( tongDBID )

	#-----------------------------�ƻ�����-------------------------------------------------------------
	def tongManagerRegisterCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
					  	"chargeSpendMoney": "onChargeSpendMoney",				# ����Ὠ��ά����
					  	"registerPreMonthRobWarPoint" : "onRegisterPreMonthRobWarPoint", 	# �Ǽ������Ӷ�ս����
					  	"CalTongSalary": "onCalTongSalary",									# ������ٺ»
					  	"ResetTongItem": "onResetTongItems",								# ���ð����Ʒ
					  	"ResetMemberBuyItemRecord" : "onResetMemberBuyItemRecord",			# ���ð��ڹ�������Ʒ��¼
					  	"resetTongQuest" : "onResetTongQuest",
					  	"ResetTongSpecialItems": "onResetTongSpecialItems",							# ���ð��������Ʒ
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )
		BigWorld.globalData["Crond"].addAutoStartScheme( "chargeSpendMoney", self, "onChargeSpendMoney" )
	
	def onCalTongSalary( self ):
		"""
		define method
		ÿ��һ��������ٺ»����������ٺ»ֵ����ձ���ٺ»
		"""
		for tongEntity in self._tongEntitys.itervalues():
			tongEntity.calTongSalary()

	def onResetTongItems( self ):
		"""
		define method
		ÿ�ܶ�ʱ���ð��������Ʒ����
		"""
		for databaseID, tongEntity in self._tongEntitys.iteritems():
			INFO_MSG( "TONG: %i reset tong items due to sys !" %databaseID )
			tongEntity.resetTongItems()
	

	def onResetMemberBuyItemRecord( self ):
		"""
		define method
		ÿ�ܶ�ʱ���ð��ڹ�������Ʒ����
		"""
		for tongEntity in self._tongEntitys.itervalues():
			tongEntity.resetMemberBuyItemRecord()
	
	def onChargeSpendMoney( self ):
		"""
		define method.
		��ά����
		"""
		for tongEntity in self._tongEntitys.itervalues():
			tongEntity.chargeSpendMoney()

	def onRegisterPreMonthRobWarPoint( self ):
		"""
		define method.
		�Ǽ������Ӷ�ս����
		"""
		TongRobWarManager.onRegisterPreMonthRobWarPoint( self )
		
	#-----------------------------���봴��һ�����-------------------------------------------------------------
	def checkTongName( self, tongName ):
		"""
		���������� �Ϸ��򷵻�ture
		"""
		# ��ʱδʵ��
		return True

	def createTong( self, tongName, creatorBase, creatorName, creatorDBID, creatorLevel, creatorRaceclass, reason ):
		"""
		define method.
		����һ�����  ����ֱ�ӵ������ �����cell.role.createTong
		@param tongName  : �������
		@param creatorBase   : �����ߵ�baseMailbox
		"""
		DEBUG_MSG( "createTong: tongName=%s, creatorName=%s" % ( tongName, creatorName ) )
		creatorND = creatorName + "(%s)" % creatorDBID
		
		if len( self._tongBaseDatas ) + len( self.tempCreateInfo ) >= csdefine.TONG_AMOUNT_MAX:
			creatorBase.cell.tong_checkCreateFail( csstatus.TONG_AMOUNT_MAX )
			return
		if self.hasTongName( tongName ):
			creatorBase.cell.tong_checkCreateFail( csstatus.TONG_NAME_EXIST )
			return
		if not self.checkTongName( tongName ): # ����������Ʋ��Ϸ���
			creatorBase.cell.tong_checkCreateFail( csstatus.TONG_NAME_INVALID )
			return

		# ���￪ʼ�������entity
		arg = {}
		arg[ "playerName" ] = tongName
		arg[ "tempMapping" ] = { "isCreate" : True }
		creatorInfo = { "databaseID":creatorDBID, \
						"playerName":creatorName, \
						"level":creatorLevel, \
						"raceclass":creatorRaceclass, \
						"baseMailbox":creatorBase, \
						}
		arg["creatorInfo"] = creatorInfo
		tongBase = BigWorld.createBaseLocally( "TongEntity", arg )

		if tongBase == None:
			ERROR_MSG( "player( %s ) create Tong failed!" % creatorName )
			# ��������һ���ص�֪ͨ
			creatorBase.client.onStatusMessage( csstatus.TONG_CREATE_FAIL, "(\'%s\',)" % tongName )
			return
			
		self.tempCreateInfo[creatorDBID] = ( tongName, time.time(), tongBase )
		if not self.clearTempCreateInfoTimerID:
			self.clearTempCreateInfoTimerID = self.addTimer( CLEAR_CREATE_TEMP_DATA_INTERVAL, CLEAR_CREATE_TEMP_DATA_INTERVAL )


	def onRegisterTongOnCreated( self, creatorDBID, baseTongEntity, tongName, tongDBID, chiefName, camp ):
		"""
		define method.
		ע����������İ��ʵ��
		"""
		# ���һ���µİ��ID
		tid = self.getNewTongID()
		DEBUG_MSG( "create Tong:%s, id:%i is successfully!" % ( tongName, tid ) )
		if self.hasTong( tongDBID ):
			ERROR_MSG( "tong %s %i is exist" % ( tongName, tongDBID ) )
			return
		data =  {
					"chiefName"		: 		chiefName,
					"dbID"			:		tongDBID,
					"tid"			:		tid,
					"ad"			:		cschannel_msgs.TONG_INFO_17,
					"tongName"		:		tongName,
					"camp"			:		camp,
					"level"			: 		1,
					"jk_level"		: 		1,
					"ssd_level"		: 		1,
					"ck_level"		: 		1,
					"tjp_level"		: 		1,
					"sd_level"		: 		1,
					"yjy_level"		: 		1,
					"memberCount"	:		0,
					"prestige"		:		0,
					"holdCity"		: 		"",
					"leagues"		:		{},
					"tongTurnWarPoint":		[],
					"battleLeagues"	:		[],
				}
		self._tongBaseDatas[ tongDBID ] = data
		# ��������������߰���¼��
		self._tongEntitys[ tongDBID ] = baseTongEntity
		# ���ð���id
		baseTongEntity.initTongIDAndAD( tid, data[ 'ad' ] )

		#������Ȼ��һ�����ݿ�д�������ʱ�������ǿ��������������ɫ�����õ�
		#ĳЩ����ֵû�����ļ���һ��tick�������ݿ�,��ɵĲ���Ԥ�ϵĴ���
		self.writeToDB()
		del self.tempCreateInfo[creatorDBID]
		if len( self.tempCreateInfo ) == 0:
			self.delTimer( self.clearTempCreateInfoTimerID )
			self.clearTempCreateInfoTimerID = 0
		
		try:
			g_logger.tongCreateLog( tongDBID, tongName, creatorDBID,chiefName )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )


	def onTongDismiss( self, tongDBID, reason ):
		"""
		define method.
		ĳ����ᱻ��ɢ�ˣ�׼�����������������
		"""
		TongTerritoryManager.onTongDismiss( self, tongDBID )
		TongCityWarManager.onTongDismiss( self, tongDBID )
		TongTurnWarManager.onTongDismiss( self, tongDBID )
		if tongDBID in self._tongBaseDatas:
			tongInfo = self._tongBaseDatas[ tongDBID ]
			self._tongEntitys.pop( tongDBID )
			self.delTongInTongBaseDatas( tongDBID )
			self.writeToDB() 										# ��ʱ����
			try:
				g_logger.tongDismissLog( tongDBID, tongInfo['tongName'], None )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			return

	#------------------------------------------------------------------------------------------
	def getNewTongID( self ):
		"""
		��ȡһ���µİ��ID
		"""
		tids = []
		for item in self._tongBaseDatas.itervalues():
			tids.append( item[ "tid" ] )

		# ����Ԥ����ô���ID�� ��ʹ�ϲ�������Ҳ�ò���
		for tid in xrange( 1, 1000000 ):
			if tid not in tids:
				return tid

		return 0

	#------------------------------------------------------------------------------------------
	def findTongByName( self, tongName ):
		"""
		ͨ����������ҵ�����mailbox
		"""
		for item in self._tongBaseDatas.itervalues():
			if item[ "tongName" ] == tongName:
				return self.findTong( item[ "dbID" ] )
		return None

	def findTongByTID( self, tid ):
		"""
		ͨ�����id�ҵ�����mailbox
		"""
		for item in self._tongBaseDatas.itervalues():
			if item[ "tid" ] == tid:
				return self.findTong( item[ "dbID" ] )
		return None

	def hasTongName( self, tongName ):
		"""
		�Ƿ���һ���˰�����Ƶİ�����
		"""
		for item in self._tongBaseDatas.itervalues():
			if item[ "tongName" ] == tongName:
				return True
		for item in self.tempCreateInfo.itervalues():
			if item[0] == tongName:	# �����ڴ����еİ��ͬ��
				return True
		return False

	def hasTongID( self, tid ):
		"""
		�Ƿ���һ���˰��id�İ�����
		"""
		for item in self._tongBaseDatas.itervalues():
			if item[ "tid" ] == tid:
				return True
		return False

	def hasTong( self, tongDBID ):
		return tongDBID in self._tongBaseDatas

	def hasTongEntity( self, tongDBID ):
		"""
		�Ƿ���һ���˰��dbid�İ�����
		"""
		return tongDBID in self._tongEntitys

	def findTong( self, tongDBID ):
		"""
		�Ƿ���һ���˰��dbid�İ�����
		"""
		if not self.hasTongEntity( tongDBID ):
			return None
		return self._tongEntitys[ tongDBID ]

	def getTongNameByDBID( self, tongDBID ):
		"""
		ͨ�����DBID��ȡ�������
		"""
		item = self._tongBaseDatas.get( tongDBID )
		if item:
			return item[ "tongName" ]
		return ""

	def getTongDBIDByName( self, tongName ):
		"""
		ͨ�����DBID��ȡ�������
		"""
		for item in self._tongBaseDatas.itervalues():
			if item[ "tongName" ] == tongName:
				return item[ "dbID" ]
		return 0
		
	def getTongSignMD5ByDBID( self, tongDBID ):
		"""
		ͨ�����DBID��ȡ�����MD5 by ����
		"""
		item = self._tongBaseDatas.get( tongDBID )
		if item:
			return item[ "tongSignMD5" ]
		return ""
	
	def getTongCampByDBID( self, tongDBID ):
		"""
		ͨ�����DBID��ȡ������Ӫ
		"""
		item = self._tongBaseDatas.get( tongDBID )
		if item:
			return item[ "camp" ]
			
		return 0

	#------------------------------------------------------------------------------------------
	def save( self ):
		"""
		��������Ҫ����
		"""
		for tongEntity in self._tongEntitys.itervalues():
			tongEntity.save()
		self.writeToDB()

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
	def onMemberLoginTong( self, tongDBID, baseEntity, baseEntityDBID ):
		"""
		define method.
		��Ա��½֪ͨ
		"""
		TongRobWarManager.onMemberLoginTong( self, tongDBID, baseEntity, baseEntityDBID )
		TongFeteManager.onMemberLoginTong( self, tongDBID, baseEntity, baseEntityDBID )
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onMemberLogin( baseEntity, baseEntityDBID )
		else:
			if not self.hasTong( tongDBID ):
				ERROR_MSG( "%i:tong %i not exist." % ( baseEntity.id, tongDBID ) )
				baseEntity.tong_reset()		# �������Ѿ������ڣ���������Ұ����ص�����
			else:
				d = {}
				d[ "dbid" ] = baseEntityDBID
				d[ "baseEntity" ] = baseEntity
				if self._enterTongMembers_temp.has_key( tongDBID ):
					self._enterTongMembers_temp[ tongDBID ].append( d )
				else:
					self._enterTongMembers_temp[ tongDBID ] = [d]
					self.loadTongByDBIDFromDB( tongDBID )

	def onMemberLogoutTong( self, tongDBID, baseEntityDBID ):
		"""
		define method.
		��Ա����֪ͨ
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onMemberLogout( baseEntityDBID )
		else:
			ERROR_MSG( "%i:tong %i not exist." % ( baseEntityDBID, tongDBID ) )

	def addPrestige( self, tongDBID, prestige ):
		"""
		define method.
		�������
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.addPrestige( prestige, csdefine.TONG_PRESTIGE_CHANGE_REST )
		else:
			ERROR_MSG( "tong %i not exist." % ( tongDBID ) )

	def onRequestTongLeague( self, userDBID, userTongDBID, requestTongName ):
		"""
		define method.
		������ͬ��
		"""
		requestTongDBID = 0
		for t in self._tongBaseDatas.itervalues():
			if t["tongName"] == requestTongName:
				requestTongDBID = t[ 'dbID' ]

		tongEntity = self.findTong( userTongDBID )
		if tongEntity:
			tongEntity.onRequestTongLeague( userDBID, requestTongDBID, requestTongName )
		else:
			ERROR_MSG( "tong %i not exist." % ( userTongDBID ) )


	def requestTongLeague( self, user, userTongDBID, requestTongName ):
		"""
		define method.
		������ͬ��
		@param user				:ʹ�ù�����baseMailbox
		@param userTongDBID		:ʹ�ù����� ����DBID
		@param requestTongName	:Ҫ�����Ŀ��������
		"""
		if not self.hasTongName( requestTongName ):
			self.statusMessage( user, csstatus.TONG_TARGET_TONG_NO_FIND )
			return

		tong = self.findTongByName( requestTongName )
		tongName = ""
		item = self._tongBaseDatas.get( userTongDBID )
		if item:
			tongName = item[ 'tongName' ]

		if tong:
			tong.requestTongLeague( user, tongName, userTongDBID )
		else:
			self.statusMessage( user, csstatus.TONG_TARGET_TONG_CHIEF_OFFLINE )

	def onRequestTongLeagueFailed( self, userTongDBID, targetTongDBID ):
		"""
		define method.
		����ͬ���ڶԷ����entity��ʧ���ˣ������ǰ��������ߣ������ص�
		"""
		tongEntity = self.findTong( userTongDBID )
		if tongEntity:
			tongEntity.onRequestTongLeagueFailed( targetTongDBID )
		else:
			ERROR_MSG( "tong %i not exist." % ( userTongDBID ) )

	def answerRequestTongLeague( self, memberBaseEntity, memberTongDBID, agree, requestByTongDBID ):
		"""
		define method.
		�Է��ش����ҵ�����
		"""
		tongEntity = self.findTong( requestByTongDBID )
		if tongEntity:
			tongEntity.answerRequestTongLeague( memberBaseEntity, self.findTong( memberTongDBID ), memberTongDBID, agree )
		else:
			ERROR_MSG( "tong %i not exist." % ( requestByTongDBID ) )

	def onLeagueDispose( self, tongDBID, leagueTongDBID ):
		"""
		define method.
		�յ��Է��������������ͬ�˹�ϵ
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onLeagueDispose( leagueTongDBID )
		else:
			ERROR_MSG( "tong %i not exist." % ( tongDBID ) )

	def leagueDispose( self, tongDBID, leagueTongDBID ):
		"""
		define method.
		һ�����֪ͨͬ�˰�� ���ͬ�˹�ϵ��  �������ɰ���ɢ���µ�
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.leagueDispose( -1, leagueTongDBID )
		else:
			if not self.hasTong( tongDBID ):
				ERROR_MSG( "%i:tong %i not exist." % ( tongDBID, leagueTongDBID ) )
			else:
				cmd = "DELETE from tbl_TongEntity_leagues where sm_dbID=%i;" % leagueTongDBID
				BigWorld.executeRawDatabaseCommand( cmd )

	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if timerID == self.loadAllTongTimerID:
			self.onLoadAllTongTimer()
		elif timerID == self.clearTempCreateInfoTimerID:
			for creatorDBID, info in self.tempCreateInfo.items():
				if time.time() - info[1] > CLEAR_CREATE_TEMP_DATA_INTERVAL:	# ������ᳬʱ�ˣ�ɾ�����entity
					tempInfo = self.tempCreateInfo.pop( creatorDBID )
					tempInfo[2].destroy( deleteFromDB = True )				# �������entityʱ��д��db����ʱҪ��db��ɾ��
					ERROR_MSG( "player( %i ) create tong( %s ) failed." % ( creatorDBID, tempInfo[0] ) )
			if len( self.tempCreateInfo ) == 0:	# ���û��������ôͣ��timer
				self.delTimer( self.clearTempCreateInfoTimerID )
				self.clearTempCreateInfoTimerID = 0
		else:
			TongCityWarManager.onTimer( self, timerID, cbID )
			TongTerritoryManager.onTimer( self, timerID, cbID )
			TongRobWarManager.onTimer( self, timerID, cbID )
			TongFeteManager.onTimer( self, timerID, cbID )
			TongAbattoirMgr.onTimer( self, timerID, cbID )
			TongFengHuoLianTianMgr.onTimer( self, timerID, cbID )
			TongCityWarFinalManager.onTimer( self, timerID, cbID )

	def onRegisterTerritory( self, tongDBID, territory ):
		"""
		define method.
		@param tongDBID: ���DBID
		@param territory:��ظ�����basemailbox
		"""
		TongTerritoryManager.onRegisterTerritory( self, tongDBID, territory )
		TongRobWarManager.onRegisterTerritory( self, tongDBID, territory )

	def requestTongItems( self, tongDBID, chapmanBase ):
		"""
		define method.
		������˱������������ȡ�����Ʒ����
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onChapmanRequestItems( chapmanBase )
		else:
			DEBUG_MSG( "tong %i not exist or offline." % ( tongDBID ) )

	def onSellItems( self, tongDBID, roleDBID, itemID, amount ):
		"""
		define method.
		�����Ʒ��������
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onSellItems( roleDBID, itemID, amount )
		else:
			ERROR_MSG( "tong %i not exist." % ( tongDBID ) )

	def onCappaign_monsterRaidComplete( self, tongDBID ):
		"""
		define method.
		ħ����Ϯ �����Ѿ����
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onCappaign_monsterRaidComplete()
		else:
			ERROR_MSG( "tong %i not exist." % ( tongDBID ) )

	def onProtectTongStart( self, tongDBID, protectType ):
		"""
		define method.
		�������ɻ��ʼ��
		"""
	  	territory = self.findTerritoryByTongDBID( tongDBID )
	  	if territory:
	  		territory.onProtectTongStart( protectType )

	def onProtectTongEnd( self, tongDBID ):
		"""
		define method.
		�������ɻ������
		"""
	  	territory = self.findTerritoryByTongDBID( tongDBID )
	  	if territory:
	  		territory.onProtectTongEnd()

	#------------------------------------------------------------------------------------------
	def loadAllTongBaseDatas( self ):
		"""
		�������а��Ļ�������
		"""
		sqlcmd = "select id, sm_level, sm_jk_level, sm_ssd_level, sm_ck_level, sm_tjp_level, sm_sd_level, sm_yjy_level, sm_memberCount, sm_prestige, sm_playerName, sm_camp, sm_tongSignMD5, sm_tid, sm_ad from tbl_TongEntity;"
		BigWorld.executeRawDatabaseCommand( sqlcmd, Functor( self.queryAllTongBaseData_Callback, 0 ) )
		sqlcmd = "select parentID, sm_dbID, sm_tongName from tbl_TongEntity_leagues;"
		BigWorld.executeRawDatabaseCommand( sqlcmd, Functor( self.queryAllTongBaseData_Callback, 1 ) )
		sqlcmd = "select parentID, sm_cityName, sm_point from tbl_TongEntity_tongTurnWarPoint;"
		BigWorld.executeRawDatabaseCommand( sqlcmd, Functor( self.queryAllTongBaseData_Callback, 2 ) )
		sqlcmd = "select parentID, sm_dbID from tbl_TongEntity_battleLeagues;"
		BigWorld.executeRawDatabaseCommand( sqlcmd, Functor( self.queryAllTongBaseData_Callback, 3 ) )

	def queryAllTongBaseData_Callback( self, queryType, result, dummy, error ):
		"""
		��ѯ���а��������� ���ݿ�ص�
		"""
		if ( error ):
			ERROR_MSG( error )
			return

		if queryType == 0:	# ��ѯ��������
			for r in result:
				tongDBID 		= int( r[ 0 ] )
				datas = self._tongBaseDatas.get( tongDBID )

				if not datas:
					datas = {}
					self._tongBaseDatas[ tongDBID ] = datas
					
				datas[ "dbID" ] 			= int( r[ 0 ] )
				datas[ "level" ] 			= int( r[ 1 ] )
				datas[ "jk_level" ] 		= int( r[ 2 ] )
				datas[ "ssd_level" ] 		= int( r[ 3 ] )
				datas[ "ck_level" ] 		= int( r[ 4 ] )
				datas[ "tjp_level" ] 		= int( r[ 5 ] )
				datas[ "sd_level" ] 		= int( r[ 6 ] )
				datas[ "yjy_level" ] 		= int( r[ 7 ] )
				datas[ "memberCount" ]		= int( r[ 8 ] )
				datas[ "prestige" ]			= int( r[ 9 ] )
				datas[ "tongName" ] 		= r[ 10 ]
				datas[ "camp" ] 			= int( r[ 11 ] )
				datas[ "tongSignMD5" ]		= r[ 12 ]
				datas[ "tid" ] 				= int( r[ 13 ] )
				datas[ "ad" ] 				= r[ 14 ]
				
				# ��ᱻ���غ�������������������Ϣ
				datas[ "holdCity" ]			= ""
				datas[ "chiefName" ] 		= ""
				
				# ��ֹĳЩ���û������ ������������Ƚ��г�ʼ��
				if not datas.has_key( "leagues" ):
					datas[ "leagues" ] = {}
					
				# ��ᳵ��ս������Ϣ
				if not datas.has_key( "tongTurnWarPoint" ):
					datas[ "tongTurnWarPoint" ] = []
				
				# ս�����˰��
				if not datas.has_key( "battleLeagues" ):
					datas[ "battleLeagues" ] = []
			
			# ��ʼ�������а��entity
			self.tmpTongInfos = self._tongBaseDatas.keys()
			self.loadAllTongTime = time.time()
			self.loadAllTongTimerID = self.addTimer( 0, 0.1, 0 )			# �������ذ���timer
			self.onManagerInitOver()
		elif queryType == 1:	# ��ѯ��������
			for r in result:
				tongDBID 		= int( r[ 0 ] )
				datas = self._tongBaseDatas.get( tongDBID )

				if not datas:
					datas = {}
					self._tongBaseDatas[ tongDBID ] = datas

				leagues = datas.get( "leagues" )
				if not leagues:
					leagues = {}	# { tongDBID:tongName }
					self._tongBaseDatas[ tongDBID ][ "leagues" ] = leagues

				leagues[  int( r[ 1 ] )  ] = r[ 2 ]
		elif queryType == 2:	# ��ѯ����ս����
			for r in result:
				tongDBID = int( r[0] )
				datas = self._tongBaseDatas.get( tongDBID )
				if not datas:
					datas = {}
					self._tongBaseDatas[ tongDBID ] = datas
					
				tongTurnWarPoint = datas.get( "tongTurnWarPoint" )
				if not tongTurnWarPoint:
					self._tongBaseDatas[ tongDBID ][ "tongTurnWarPoint" ] = []		# [ { "cityName", "point" } ]
				
				info = { "cityName": r[1], "point": int( r[2] ) }
				self._tongBaseDatas[ tongDBID ][ "tongTurnWarPoint" ].append( info )
				TongTurnWarManager.updateTurnWarTopTable( self, tongDBID, r[1], int( r[2] ) )
		elif queryType == 3:				# ��ѯս����������
			for r in result:
				tongDBID 		= int( r[ 0 ] )
				datas = self._tongBaseDatas.get( tongDBID )

				if not datas:
					datas = {}
					self._tongBaseDatas[ tongDBID ] = datas

				battleLeagues = datas.get( "battleLeagues" )
				if not battleLeagues:
					battleLeagues = []		# [ tongDBID, tongDBID ]
					self._tongBaseDatas[ tongDBID ][ "battleLeagues" ] = battleLeagues
				
				battleLeagues.append(  int( r[ 1 ] ) )

	def getTongAD( self, tongDBID ):
		"""
		��ȡĳ���Ĺ��
		"""
		item = self._tongBaseDatas.get( tongDBID )
		if item:
			return item[ 'ad' ]
		return ""

	def requestTongList( self, playerBase, index, camp = 0 ):
		"""
		define method.
		ĳ����������ȡ����б�
		@param index: �ͻ�������������������
		"""
		for idx in xrange( index, index + 5  ):
			if len( self._tongBaseDatas ) < idx + 1:
				playerBase.client.tong_receiveTongListCompleted()
				break

			t = self._tongBaseDatas.values()[ idx ]
			tongDBID = t["dbID"]
			tongName = t[ 'tongName']
			tongID = t[ 'tid' ]

			if tongDBID in self._tongBaseDatas:
				if camp and self.getTongCampByDBID( tongDBID ) != camp:
					continue
				prestige = self._tongBaseDatas[ tongDBID ][ "prestige" ]
				holdCity = self._tongBaseDatas[ tongDBID ][ "holdCity" ]
				level = self._tongBaseDatas[ tongDBID ][ "level" ]
				playerBase.client.tong_onReceiveTongList( tongDBID, tongName, tongID, level, prestige, len( holdCity ) > 0 )

	def queryTongInfo( self, playerBase, tongDBID ):
		"""
		define method.
		��ѯĳ��������Ϣ
		"""
		holdCity 		= self._tongBaseDatas[ tongDBID ][ "holdCity" ]
		memberCount 	= self._tongBaseDatas[ tongDBID ][ "memberCount" ]
		chiefName 		= self._tongBaseDatas[ tongDBID ][ "chiefName" ]
		leagues 		= self._tongBaseDatas[ tongDBID ][ "leagues" ].values()
		ad 				= self.getTongAD( tongDBID )

		# ���ظ��ͻ��˰�����Ϣ
		playerBase.client.tong_onReceiveTongInfo( tongDBID, memberCount, chiefName, holdCity, leagues, ad )

	def setTongAD( self, playerBase, tongDBID, strAD ):
		"""
		define method.
		���ð����
		@param strAD: �����
		"""
		item = self._tongBaseDatas.get( tongDBID )
		if item:
			item[ 'ad' ] = strAD
			self.findTong( tongDBID ).setAD( strAD )

	def delTongInTongBaseDatas( self, tongDBID ):
		"""
		�Ӱ�����������ɾ��ĳ�����
		"""
		self._tongBaseDatas.pop( tongDBID )

	def updateTongLevel( self, tongDBID, level ):
		"""
		define method.
		���°�ἶ��
		"""
		self._tongBaseDatas[ tongDBID ][ "level" ] = level

	def updateTongChiefName( self, tongDBID, chiefName ):
		"""
		define method.
		���°���
		"""
		self._tongBaseDatas[ tongDBID ][ "chiefName" ] = chiefName
		TongCityWarManager.updateTongChiefName( self, tongDBID )

	def updateTongMemberCount( self, tongDBID, memberCount ):
		"""
		define method.
		���°���Ա����
		"""
		if tongDBID not in self._tongBaseDatas:
			self._tongBaseDatas[ tongDBID ] = { "memberCount" : memberCount }
			return

		self._tongBaseDatas[ tongDBID ][ "memberCount" ] = memberCount

	def updateTongHoldCity( self, tongDBID, holdCity ):
		"""
		define method.
		���°��ռ�����
		"""
		self._tongBaseDatas[ tongDBID ][ "holdCity" ] = holdCity

	def updateTongPrestige( self, tongDBID, prestige ):
		"""
		define method.
		���°������
		"""
		self._tongBaseDatas[ tongDBID ][ "prestige" ] = prestige

	def updateTongBuildingLevel( self, tongDBID, jk_level, ssd_level, ck_level, tjp_level, sd_level, yjy_level ):
		"""
		define method.
		���°�Ὠ������
		"""
		self._tongBaseDatas[ tongDBID ][ "jk_level" ] = jk_level
		self._tongBaseDatas[ tongDBID ][ "ssd_level" ] = ssd_level
		self._tongBaseDatas[ tongDBID ][ "ck_level" ] = ck_level
		self._tongBaseDatas[ tongDBID ][ "tjp_level" ] = tjp_level
		self._tongBaseDatas[ tongDBID ][ "sd_level" ] = sd_level
		self._tongBaseDatas[ tongDBID ][ "yjy_level" ] = yjy_level

	def updateTongLeagues( self, tongDBID, leagues ):
		"""
		define method.
		���°��ͬ��
		"""
		datas = {}
		self._tongBaseDatas[ tongDBID ][ "leagues" ] = datas

		for league in leagues:
			datas[ league[ "dbID" ] ] = league[ "tongName" ]

	def changeTongName( self, playerBase, tongDBID, newName ):
		"""
		Define method.
		��������

		"""
		if self.hasTongName( newName ):
			playerBase.client.onStatusMessage( csstatus.TONG_NAME_EXIST, "" )
			return
		tongBase = self.findTong( tongDBID )
		if tongBase is None:
			DEBUG_MSG( "cannot find tong( tongDBID:%i ) base." % tongDBID )
			return

		tongBase.changeName( newName )
		self._tongBaseDatas[tongDBID]["tongName"] = newName
		playerBase.client.onStatusMessage( csstatus.TONG_RENAME_SUCCEED, "" )


	def onActivityLogHandle( self ):
		"""
		define method
		ͳ�ư����ػ��־
		"""
		try:
			g_logger.countTongNumLog( len( self._tongBaseDatas ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def memberNameChanged( self, dbid, playerDBID, newName ):
		"""
		define method
		��ɫ���ֱ��ı���
		"""
		tongEntity = self.findTong( dbid )
		if tongEntity:
			tongEntity.onMemberNameChanged( playerDBID, newName )

	def updateTongExp( self, tongDBID, exp ):
		"""
		define method.
		���°�ᾭ��
		"""
		self._tongBaseDatas[ tongDBID ][ "EXP" ] = exp
		
#------------------------------------------------------------
#����Ĺ
#------------------------------------------------------------		
	def findChiefNameByTongName(self, type, index, tongName):
		#define method, used in LiuWangMuMgr
		tongDBID = self.getTongDBIDByName(tongName)
		chiefName = self._tongBaseDatas[tongDBID]["chiefName"]
		BigWorld.globalData["LiuWangMuMgr"].sendLiuWangMuRewardToTongChief(type, index,  tongName, chiefName)

			
#----------------------------------------------------------------------
# ����������
#----------------------------------------------------------------------
	def onResetTongQuest( self ):
		"""
		define method
		�رհ����������
		"""
		for tongEntity in self._tongEntitys.values():
			tongEntity.resetTongQuest()
#---------------------------------------------------------------------
# ����������
#---------------------------------------------------------------------
	def onTongRaceOver( self, tongDBID ):
		"""
		define method
		����������
		"""
		tongMB = self.findTong( tongDBID )
		if tongMB:
			tongMB.onTongRaceOver()

	#-----------------------------ս������-------------------------------------------
	def reqOpenBattleLeaguesWindow( self, playerBase, camp, spaceName ):
		"""
		define method
		��������ս�����˽���
		"""
		tongRecord = self.getQuarterFinalRecord( camp, spaceName )
		if len( tongRecord ) == 0:
			self.statusMessage( playerBase, csstatus.TONG_BATTLE_LEAGUE_SPECIFIC_TIME )
			return
		
		playerBase.client.tong_openTongBattleLeagueWindow( tongRecord )
	
	def queryTongBattleLeagues( self, playerBase, index, camp, spaceName ):
		"""
		define method
		��ѯս��ͬ����Ϣ
		"""
		for idx in xrange( index, index + 5  ):
			if len( self._tongBaseDatas ) < idx + 1:
				playerBase.client.tong_receiveBattleLeagueCompleted()
				break

			t = self._tongBaseDatas.values()[ idx ]
			tongDBID = t[ "dbID" ]
			tongCamp = t[ 'camp' ]

			tongRecords = self.getQuarterFinalRecord( camp )					# ͬ��Ӫ�����пɲ����İ�ᣬ���Է������Ľ��
			qualifiedTong = self.getQuarterFinalRecord( camp, spaceName )		# ��ǰ���еĿɲ������
			if tongDBID not in qualifiedTong and tongDBID in tongRecords:
				continue
			
			if tongDBID in self._tongBaseDatas:
				if camp and tongCamp != camp:
					continue
				tongName = t[ 'tongName' ]
				battleLeagues = t[ "battleLeagues" ]
				
				playerBase.client.tong_receiveBattleLeagues( tongDBID, tongName, camp, battleLeagues )

	def getTongBattleLeagueMaxNum( self, tongDBID ):
		"""
		��ȡ��������ս�����˵������������һ��������һ�����ڶ���������������
		"""
		tongRecord = self.getQuarterFinalRecord( 0 )
		if tongDBID in tongRecord.keys():
			return tongRecord[ tongDBID ]
		return 1

	def inviteTongBattleLeague( self, inviterDBID, inviterBase, inviterTongDBID, inviteeTongDBID, msg ):
		"""
		define method
		������ս��ͬ��
		"""
		# �����ж�
		if len( self.cityWarFinalInfos ) == 0:
			self.statusMessage( inviterBase, csstatus.TONG_BATTLE_LEAGUE_SPECIFIC_TIME )
			return
		
		# ˫���ж԰�ᣬ����ս������
		tongRecord = self.getQuarterFinalRecord( 0 )
		if ( inviterTongDBID in tongRecord.keys() ) and ( inviteeTongDBID in tongRecord.keys() ):
			self.statusMessage( inviterBase, csstatus.TONG_BATTLE_LEAGUE_NOT_ENEMY )
			return
		
		# ������һ���в����ʸ�
		if ( inviterTongDBID not in tongRecord.keys() ) and ( inviteeTongDBID not in tongRecord.keys() ):
			self.statusMessage( inviterBase, csstatus.TONG_BATTLE_LEAGUE_NOT_QUALIFIED )
			return
		
		tongEntity = self.findTong( inviterTongDBID )
		if not tongEntity:
			RROR_MSG( "TONG:tong %i not exist." % ( inviterTongDBID ) )
			return
		maxNum = self.getTongBattleLeagueMaxNum( inviterTongDBID )
		tongEntity.inviteTongBattleLeague( inviterDBID, inviteeTongDBID, msg, maxNum )

	def onInviteTongBattleLeague( self, inviter, inviterTongDBID, inviteeTongDBID, msg ):
		"""
		define method
		������ս��ͬ�ˣ���ͨ�����뷽�����֤ ���Ĳ�
		@param inviter				:������baseMailbox
		@param inviterTongDBID		:�����߰���DBID
		@param inviteeTongDBID		:���������DBID
		"""
		if not self.findTong( inviterTongDBID ):
			self.statusMessage( inviter, csstatus.TONG_TARGET_TONG_NO_FIND )
			return
		inviteeTong = self.findTong( inviteeTongDBID )
		inviterTongName = self._tongBaseDatas[inviterTongDBID]["tongName"]
		
		if not inviteeTong:
			ERROR_MSG( "TONG:tong %i not exist." % ( inviterTongDBID ) )
			return
		maxNum = self.getTongBattleLeagueMaxNum( inviteeTongDBID )
		inviteeTong.receiveBattleLeagueInvitation( inviter, inviterTongName, inviterTongDBID, msg, maxNum )

	def onInviteTongBattleLeagueFailed( self, inviterTongDBID, inviteeTongDBID ):
		"""
		define method
		����ս��ͬ��ʧ�ܻص��������Ǳ����뷽���������ߣ�
		"""
		inviterTong = self.findTong( inviterTongDBID )
		if not inviterTong:
			ERROR_MSG( "TONG:tong %i not exist." % ( inviterTongDBID ) )
			return
		inviterTong.onRequestTongLeagueFailed( inviteeTongDBID )

	def replyBattleLeagueInvitation( self, replierBaseMailbox, replierTongDBID, inviterTongDBID, response ):
		"""
		define method
		�յ���������ظ�
		"""
		inviterTong = self.findTong( inviterTongDBID )
		replierTong = self.findTong( replierTongDBID )
		replierTongName = self._tongBaseDatas[replierTongDBID]["tongName"]
		if not inviterTong:
			ERROR_MSG( "TONG:tong %i not exist." % ( inviterTongDBID ) )
			return
		inviterTong.receiveBattleLeagueReply( replierBaseMailbox, replierTong, replierTongDBID, replierTongName, response )

	def updateTongBattleLeagues( self, tongDBID, leagues ):
		"""
		define method
		����ս��ͬ��
		"""
		if tongDBID in self._tongBaseDatas[ tongDBID ][ "battleLeagues" ]:
			return
		
		for league in leagues:
			if league[ "dbID" ] in self._tongBaseDatas[ tongDBID ][ "battleLeagues" ]:
				continue
			self._tongBaseDatas[ tongDBID ][ "battleLeagues" ].append( league[ "dbID" ] )

	def requestBattleLeagueDispose( self, userDBID, userBaseEntity, userTongDBID, battleLeagueDBID ):
		"""
		define method
		������ս�����˹�ϵ
		"""
		if BigWorld.globalData.has_key( "AS_TONG_CITY_WAR_FINAL"):	# ��ڼ䣬���ܽ�����˹�ϵ
			self.statusMessage( userBaseEntity, csstatus.TONG_BATTLE_LEAGUE_DISPOSE_NOT_ALLOW )
			return
		
		userTong = self.findTong( userTongDBID )
		if not userTong:
			ERROR_MSG( "TONG: tong %i not exist." % ( tongDBID ) )
			return
		userTong.requestBattleLeagueDispose( userDBID, battleLeagueDBID )

	def onBattleLeagueDispose( self, tongDBID, leagueTongDBID ):
		"""
		define metdho
		һ�����֪ͨս��ͬ�˰����ͬ�˹�ϵ
		"""
		tongEntity = self.findTong( tongDBID )
		if not tongEntity:
			ERROR_MSG( "TONG: tong %i is not exist." % ( tongDBID ) )
			return
		tongEntity.battleLeagueDispose( leagueTongDBID )

	def battleLeagueAutoDispose( self,  tongDBID, battleLeagueDBID ):
		"""
		define mtehod
		�Զ����ս��ͬ�˹�ϵ��ͬ�˰���ɢ���£�
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.requestBattleLeagueDispose( -1, battleLeagueDBID )
		else:
			if not self.hasTong( tongDBID ):
				ERROR_MSG( "TONG: %i 's tong battleLeagues  %i is not exist." % ( tongDBID, battleLeagueDBID ) )
			else:
				cmd = "DELETE from tbl_TongEntity_battleLeagues where sm_dbID=%i;" % battleLeagueDBID
				BigWorld.executeRawDatabaseCommand( cmd )

	def getBattleLeagueByTongDBID( self, tongDBID ):
		"""
		define method
		���ݰ��DBID�����ͬ�˰��
		"""
		return self._tongBaseDatas[tongDBID]["battleLeagues"]

	# --------------------------------------------------------------
	# ��������̳�
	# --------------------------------------------------------------
	def requestTongSpecialItems( self, tongDBID, chapmanBase ):
		"""
		define method.
		����������˱������������ȡ�����Ʒ����
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onChapmanRequestSpecialItems( chapmanBase )
		else:
			DEBUG_MSG( "tong %i not exist or offline." % ( tongDBID ) )

	def onResetTongSpecialItems( self ):
		"""
		define method
		ÿ�ܶ�ʱ���ð��������Ʒ����
		"""
		for databaseID, tongEntity in self._tongEntitys.iteritems():
			INFO_MSG( "TONG: %i reset tong items due to sys !" %databaseID )
			tongEntity.resetTongSpecialItems()

	def onSellSpecialItems( self, tongDBID, playerBase, memberDBID, itemID, amount ):
		"""
		define method.
		���������Ʒ������
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onSellSpecialItems( playerBase, memberDBID, itemID, amount )
		else:
			ERROR_MSG( "tong %i not exist." % ( tongDBID ) )
	
	def buyTongSpecialArrayFromNPC( self, chapmanBase, tongDBID, playerDBID, memberDBID, invoiceIDs, argAmountList ):
		"""
		��Ṻ��������Ʒ
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.buyTongSpecialArrayFromNPC( chapmanBase, playerDBID, memberDBID, invoiceIDs, argAmountList )
#
# $Log: not supported by cvs2svn $
# Revision 1.9  2008/08/07 07:10:40  phw
# BigWorld.base() -> BigWorld.createBaseLocally()
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
# Revision 1.5  2008/06/24 01:49:52  kebiao
# �޸���һ���첽���ؿ��ܴ��ڵ�һ��BUG
#
# Revision 1.4  2008/06/23 08:11:31  kebiao
# ����ĳЩ�ط������ݿ⼰ʱ����
# ĳЩ���߳�Ա����ֵû�����ļ���һ��tick�������ݿ�,
# �������߳�Ա��ֵȴ��д����ɵĲ���Ԥ�ϵĴ���
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
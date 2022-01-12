# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *

import csconst
import csdefine
import csstatus
import random
import time

class TeachInfo:
	def __init__( self, playerDBID, playerName, playerLevel, playerMetier, titleID, prenticeNum, registerTime, playerBase = None, everPrenticeNum = 0, lastWeekOnlineTime = 0.0 ):
		self.playerDBID = playerDBID
		self.playerName = playerName
		self.playerLevel = playerLevel
		self.playerMetier = playerMetier
		self.titleID = titleID
		self.prenticeNum = prenticeNum
		self.registerTime = registerTime
		self.playerBase = playerBase
		self.everPrenticeNum = everPrenticeNum
		self.lastWeekOnlineTime = lastWeekOnlineTime

	def setEverPrenticeNum( self, everPrenticeNum ):
		self.everPrenticeNum = everPrenticeNum
		
	def setLastWeekOnlineTime( self, lastWeekOnlineTime ):
		self.lastWeekOnlineTime = lastWeekOnlineTime

	def getTeachInfo( self ):
		"""
		���ע����ҵ���Ϣ
		"""
		return [ self.playerDBID, self.playerName, self.playerLevel, self.playerMetier, self.titleID, self.prenticeNum, self.everPrenticeNum,self.lastWeekOnlineTime,self.registerTime ]
		
class TeachMgr( BigWorld.Base ):
	"""
	ʦͽϵͳ������
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.registerGlobally( "TeachMgr", self._registerGloballyCB )
		self._createDatabaseTable()
		self.teacherInfo = []	# ������ͽ�����Ϣ�ļ���[ TeachInfo1, TeachInfo2, ... ]
		self.teachInfoMap = {}	# ����һ��ӳ��,�Ա����dbid���ٲ���ע��������Ϣ{ playerDBID:TeachInfo, ... }
		self.prenticeInfo = []	# ������ʦ�����Ϣ�ļ���[ TeachInfo1, TeachInfo2, ... ]
		self.timerIntervalList = []	# [ ( playerDBID, ��Ӧ��ע�ᵽ��ʱ�� ), ... ]
		self.deregisterTimerID = 0	# ����������ݵ�timerID
		
	def _registerGloballyCB( self, complete ):
		"""
		ע��ȫ�ֱ����Ļص�
		"""
		if not complete:
			ERROR_MSG( "Register TeachMgr Fail!" )
			self.registerGlobally( "TeachMgr", self._registerGloballyCB )
		else:
			BigWorld.globalData["TeachMgr"] = self		# ע�ᵽcellApp��������
			INFO_MSG( "TeachMgr Create Complete!" )
			
	def _createDatabaseTable( self ):
		"""
		�������ݿ���

		@id :			�Զ�����, ���ݿ��е�����
		@sm_playerDBID:��ɫdbid
		@sm_playerName:�Ľ�ɫ����
		@sm_level:	��ɫ�ȼ�
		@sm_metier:	��ɫְҵ
		@sm_teachCredit: ��ҵ�ʦ���ƺ�
		@sm_prenticeNum:��ͽ�ߵ�ǰͽ������
		@sm_registerTime:ע��ʱ��
		"""
		sql = """CREATE TABLE IF NOT EXISTS `custom_TeachInfo`
				(`id` BIGINT NOT NULL auto_increment,
				`sm_playerDBID` BIGINT NOT NULL,
				`sm_playerName` TEXT NOT NULL,
				`sm_level` BIGINT NOT NULL,
				`sm_metier` BIGINT NOT NULL,
				`sm_teachCredit` BIGINT NOT NULL DEFAULT 0,
				`sm_prenticeNum` TINYINT NOT NULL DEFAULT 0,
				`sm_registerTime` BIGINT NOT NULL,
				PRIMARY KEY (`id`),
				key ( sm_playerDBID )
				)
				ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( sql, self._createTableCB )

	def _createTableCB( self, result, rows, errstr ):
		"""
		�������ݿ���ص�
		"""
		if errstr:
			ERROR_MSG( "create custom_TeachInfo table error:%s." % errstr )
			return
			
		self.initialize()
		
	def initialize( self ):
		"""
		��ʼ��ʦͽϵͳ������
		"""
		sql = "select id, sm_playerDBID, sm_playerName, sm_level, sm_metier, sm_teachCredit, sm_prenticeNum, sm_registerTime from `custom_TeachInfo`;"
		BigWorld.executeRawDatabaseCommand( sql, self._initializeTeacherInfoCB )
		
	def _initializeTeacherInfoCB( self, result, rows, errstr ):
		"""
		�����ݿ��ȡcustom_TeachInfo���ݵĻص�
		"""
		if errstr:
			ERROR_MSG( "initialize custom_TeachInfo error:%s." % errstr )
			return
			
		for record in result:
			# [ id, ���dbid, ����, �ȼ�, ְҵ, ʦ���ƺ�, ͽ������, ע��ʱ�� ]
			registerTime = int( record[7] )
			now = time.time()
			deregisterTime = csconst.TEACH_REGISTER_VALID_TIME + registerTime
			playerDBID = int( record[1] )
			if deregisterTime - now <= 0:
				sql = "delete from custom_TeachInfo where sm_playerDBID = %i" % playerDBID
				BigWorld.executeRawDatabaseCommand( sql, self.deregisterTeachCB )
				continue
			playerLevel = int( record[3] )
			teachInfo = TeachInfo( playerDBID, record[2], playerLevel, int( record[4] ), int( record[5] ), int( record[6] ), registerTime )
			self.teachInfoMap[ playerDBID ] = teachInfo
			#if playerLevel >= csconst.TEACH_MASTER_MIN_LEVEL:
			#	self.teacherInfo.append( teachInfo )
			#else:
			#	self.prenticeInfo.append( teachInfo )
			self.timerIntervalList.append( ( playerDBID, deregisterTime ) )
		self.timerIntervalList.sort( cmp=lambda a,b:cmp( a[1], b[1] ) )
		self.registerTimer()
		
	def registerTimer( self ):
		"""
		ע��timer
		"""
		DEBUG_MSG( "-->>>" )
		if len( self.timerIntervalList ):
			timerInfo = self.timerIntervalList.pop()
			self.deregisterTimerID = self.addTimer( timerInfo[1]-time.time(), 0, timerInfo[0] )
			DEBUG_MSG( "-->>>222" )
	def onTimer( self, id, userArg ):
		"""
		"""
		DEBUG_MSG( "-->>>" )
		self.deregisterTimerID = 0
		try:
			teachInfo = self.teachInfoMap.pop( userArg )
		except KeyError:	# ����п����Ѿ�deregister
			pass			# ʲô������
		else:
			if teachInfo.playerBase:
				teachInfo.playerBase.cell.teach_deregisterTeachInfo()
				if teachInfo.playerLevel >= csconst.TEACH_MASTER_MIN_LEVEL:
					self.teacherInfo.remove( teachInfo )
				else:
					self.prenticeInfo.remove( teachInfo )
		self.registerTimer()
		
	def register( self, playerDBID, playerName, playerLevel, playerMetier, teachTitleID, prenticeNum, playerBase, everPrenticeNum, lastWeekOnlineTime ):
		"""
		Define method.
		����ע����ͽ
		
		@param playerDBID : ��ɫdbid
		@type playerDBID : DATABASE_ID
		@param playerName : ��ɫ����
		@type playerName : STRING
		@param playerLevel : ��ҵȼ�
		@type playerLevel : INT16
		@param playerMetier : ��ɫְҵ
		@type playerMetier : INT32
		@param teachTitleID : ��ɫ��ѫֵ
		@type teachTitleID : INT32
		@param prenticeNum : ��ɫ��ͽ�ܸ���
		@type prenticeNum : INT8
		@param everPrenticeNum : ��ʦͽ������
		@type everPrenticeNum : INT32
		@param lastWeekOnlineTime : ��������ʱ��
		@type lastWeekOnlineTime : FLOAT
		"""
		if playerDBID in self.teachInfoMap:
			return
		registerTime = int( time.time() )
		teacherInfo = TeachInfo( playerDBID, playerName, playerLevel, playerMetier, teachTitleID, prenticeNum, registerTime, playerBase, everPrenticeNum, lastWeekOnlineTime )
		self.teachInfoMap[ playerDBID ] = teacherInfo
		if playerLevel >= csconst.TEACH_MASTER_MIN_LEVEL:
			self.teacherInfo.append( teacherInfo )
		else:
			self.prenticeInfo.append( teacherInfo )
			
		# ��������������ݵ�timer
		deregisterTime = csconst.TEACH_REGISTER_VALID_TIME + registerTime
		self.timerIntervalList.append( ( playerDBID, deregisterTime ) )
		if self.deregisterTimerID == 0:
			self.registerTimer()
			
		sql = "insert into custom_TeachInfo ( sm_playerDBID, sm_playerName, sm_level, sm_metier, sm_teachCredit, sm_prenticeNum, sm_registerTime ) value( %i, \'%s\', %i, %i, %i, %i, %i )" \
			% ( playerDBID, BigWorld.escape_string( playerName ), playerLevel, playerMetier, teachTitleID, prenticeNum, registerTime )
		BigWorld.executeRawDatabaseCommand( sql, self.registerTeachCB )
		
	def registerTeachCB( self, result, rows, errstr ):
		"""
		ע��ʦ��ע����Ϣ�����ݿ�Ļص�
		"""
		if errstr:
			ERROR_MSG( errstr )
			return

	def deregister( self, playerDBID, teacherOrPrentice ):
		"""
		Define method.
		����ע�����Ϣ
		
		@param playerDBID : ���dbid
		@type playerDBID : DATABASE_ID
		"""
		try:
			teacherInfo = self.teachInfoMap[playerDBID]
		except KeyError:
			return
		deleted = False
		if teacherInfo.playerBase:
			if teacherOrPrentice == 1:	 # ע��ʦ��
				if teacherInfo in self.teacherInfo:	 # ����У���ɾ��
					teacherInfo.playerBase.client.onStatusMessage( csstatus.TEACH_LIST_LEAVE_SUCCESS, "" )
					self.teacherInfo.remove( teacherInfo )
					teacherInfo.playerBase.cell.teach_deregisterTeachInfo()
					self.teachInfoMap.pop( playerDBID )
					deleted = True
				else:
					teacherInfo.playerBase.client.onStatusMessage( csstatus.TEACH_LIST_ISNT_IN_TEACHER, "" )
			elif teacherOrPrentice == 0: # ע��ͽ��
				if teacherInfo in self.prenticeInfo: # ����У���ɾ��
					teacherInfo.playerBase.client.onStatusMessage( csstatus.LEAVE_PRENTICE_LIST_SUCCESS, "" )
					self.prenticeInfo.remove( teacherInfo )
					teacherInfo.playerBase.cell.teach_deregisterTeachInfo()
					self.teachInfoMap.pop( playerDBID )
					deleted = True
				else:
					teacherInfo.playerBase.client.onStatusMessage( csstatus.TEACH_LIST_ISNT_IN_PRENTICE, "" )

		sql = "delete from custom_TeachInfo where sm_playerDBID = %i" % playerDBID
		if deleted:	  # ע���ɹ�
			BigWorld.executeRawDatabaseCommand( sql, self.deregisterTeachCB )

	def deregisterTeachCB( self, result, rows, errstr ):
		"""
		����ע����Ϣ�����ݿ�ص�
		"""
		if errstr:
			ERROR_MSG( errstr )
			return
			
	def getTeachExtraInfo( self, playerDBID, everPrenticeNum, lastWeekOnlineTime ):
		"""
		Define method
		��һص��ú����������Լ��ĳ�ʦͽ����������������ʱ��
		"""
		if self.teachInfoMap.has_key( playerDBID ):
			teachInfo = self.teachInfoMap[playerDBID]
			teachInfo.setEverPrenticeNum( everPrenticeNum )
			teachInfo.setLastWeekOnlineTime( lastWeekOnlineTime )
		
	def queryTeachInfo( self, playerBase, playerLevel ):
		"""
		Define method.
		������ҵȼ���ѯ��ʦ��Ϣ
		
		@param playerBase : �����ѯ����ҵ�base mailbox
		@type playerBase : MAILBOX
		"""
		for record in self.teacherInfo:
			playerBase.client.teach_receiveTeachInfo( record.getTeachInfo(),1 )
		for record in self.prenticeInfo:
			playerBase.client.teach_receiveTeachInfo( record.getTeachInfo(),0 )
			
	def requestBeTeached( self, playerBase, playerName, teacherDBID ):
		"""
		Define method.
		�����ʦ

		@param targetDBID : ����Ŀ���dbid
		@type targetDBID : DATABASE_ID
		@param playerBase : ��ɫ����
		@type playerBase : STRING
		"""
		try:
			teacherInfo = self.teachInfoMap[teacherDBID]
		except KeyError:
			ERROR_MSG( "targetDBID not exist:%i." % teacherDBID )
		else:
			if teacherInfo.prenticeNum >= csconst.TEACH_PRENTICE_MAX_COUNT:
				playerBase.client.onStatusMessage( csstatus.TEACH_REQUEST_PRENTICE_NUM_LIMIT, str( (teacherInfo.playerName,) ) )
				return
			if teacherInfo.playerBase:
				teacherInfo.playerBase.prenticeRequestBeTeached( playerName, playerBase )
				playerBase.client.onStatusMessage( csstatus.TEACH_REQUEST_HAS_SENT, "" )
			else:
				playerBase.client.onStatusMessage( csstatus.TEACH_REQUEST_TARGET_OFFLINE, "" )
				
	def onPlayerGetCell( self, playerDBID, playerBase ):
		"""
		Define method.
		������ߣ����Լ���base mailboxע�ᵽ������
		"""
		try:
			playerBase.setTeachExtraInfo()
			teachInfo = self.teachInfoMap[playerDBID]
		except KeyError:
			DEBUG_MSG( "Cannot find player( %i )'s teachInfo." % playerDBID )
			playerBase.cell.teach_deregisterTeachInfo()
		else:
			teachInfo.playerBase = playerBase
			
			# ������ߣ�����Ϣ�ŵ������б���
			if teachInfo.playerLevel >= csconst.TEACH_MASTER_MIN_LEVEL:
				self.teacherInfo.append( teachInfo )
			else:
				self.prenticeInfo.append( teachInfo )
				
	def onPlayerLoseCell( self, playerDBID ):
		"""
		Define method.
		ʦ�����ߣ�֪ͨ������
		"""
		try:
			teachInfo = self.teachInfoMap[playerDBID]
		except KeyError:
			ERROR_MSG( "Cannot find player( %i )'s teacherInfo." % playerDBID )
		else:
			if teachInfo.playerLevel >= csconst.TEACH_MASTER_MIN_LEVEL:
				self.teacherInfo.remove( teachInfo )
			else:
				self.prenticeInfo.remove( teachInfo )
			teachInfo.playerBase = None
				
	def onPlayerLevelUp( self, playerDBID, playerLevel ):
		"""
		Define method.
		��Ҽ���ı䣬���°�ʦ���������

		@param playerDBID : ע����ҵ�dbid
		@type playerDBID : DATABASE_ID
		@param playerLevel : ��ҵȼ�
		@type playerLevel : INT16
		"""
		try:
			teachInfo = self.teachInfoMap[ playerDBID ]
		except KeyError:
			INFO_MSG( "playerDBID:%i not exist." % playerDBID )
			return

		# �������ͽ��Ӧ�м�����ô�ӹ�����ע����
		# �ر�ע�⣺��������ǽ�������Ҳ����������Ĺ����ϡ�
		# ���ʹ��GMָ����������ҵĵȼ�����ô���ע���Ͳ���ɹ���
		if playerLevel == csconst.TEACH_END_TEACH_LEAST_LEVEL:			#����50���ľͲ�Ӧ����ͽ���б��ˡ�BY GRL
			if teachInfo in self.prenticeInfo:
				self.deregister( playerDBID, 0 )
				return

		teachInfo.playerLevel = playerLevel
		query = "update custom_TeachInfo set sm_level = %i where sm_playerDBID = %i" % ( playerLevel, playerDBID )
		BigWorld.executeRawDatabaseCommand( query, self._updatePlayerInfoCB )
		
	def onPlayerTeachTitleChange( self, playerDBID, teachTitleID ):
		"""
		Define method.
		��Ҽ���ı䣬���°�ʦ���������

		@param playerDBID : ע����ҵ�dbid
		@type playerDBID : DATABASE_ID
		@param playerTeachCredit : ��ҹ�ѫֵ
		@type playerTeachCredit : FLOAT
		"""
		if playerDBID not in self.teachInfoMap:
			ERROR_MSG( "playerDBID:%i not exist." % playerDBID )
			return
		self.teachInfoMap[ playerDBID ].titleID = teachTitleID
		query = "update custom_TeachInfo set sm_teachCredit = %i where sm_playerDBID = %i" % ( teachTitleID, playerDBID )
		BigWorld.executeRawDatabaseCommand( query, self._updatePlayerInfoCB )
		
	def onPrenticeNumChange( self, playerDBID, prenticeNum ):
		"""
		Define method.
		��ҵ�ͽ�������ı�
		"""
		if playerDBID not in self.teachInfoMap:
			ERROR_MSG( "playerDBID:%i not exist." % playerDBID )
			return
		self.teachInfoMap[ playerDBID ].prenticeNum = prenticeNum
		query = "update custom_TeachInfo set sm_prenticeNum = %i where sm_playerDBID = %i" % ( prenticeNum, playerDBID )
		BigWorld.executeRawDatabaseCommand( query, self._updatePlayerInfoCB )
		
	def _updatePlayerInfoCB( self, result, rows, errstr ):
		"""
		����ʦ�����ݿ���Ϣ�Ļص�
		"""
		if errstr:
			ERROR_MSG( errstr )
			
	def requestTeach( self, playerBase, playerName, targetDBID ):
		"""
		Define method.
		������ͽ
		
		@param playerBase : ������ͽ��ҵ�base mailbox
		@param playerName : ������ͽ��ҵ�����
		@param targetDBID : ��ͽĿ����ҵ�dbid
		"""
		try:
			teacherInfo = self.teachInfoMap[targetDBID]
		except KeyError:
			ERROR_MSG( "targetDBID not exist:%i." % teacherDBID )
		else:
			if teacherInfo.playerBase:
				teacherInfo.playerBase.masterRequestTeach( playerName, playerBase )
				playerBase.client.onStatusMessage( csstatus.TEACH_REQUEST_HAS_SENT, "" )
			else:
				playerBase.client.onStatusMessage( csstatus.TEACH_REQUEST_TARGET_OFFLINE, "" )
				
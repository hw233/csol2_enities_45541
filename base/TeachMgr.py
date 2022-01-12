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
		获得注册玩家的信息
		"""
		return [ self.playerDBID, self.playerName, self.playerLevel, self.playerMetier, self.titleID, self.prenticeNum, self.everPrenticeNum,self.lastWeekOnlineTime,self.registerTime ]
		
class TeachMgr( BigWorld.Base ):
	"""
	师徒系统管理器
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.registerGlobally( "TeachMgr", self._registerGloballyCB )
		self._createDatabaseTable()
		self.teacherInfo = []	# 在线求徒玩家信息的集合[ TeachInfo1, TeachInfo2, ... ]
		self.teachInfoMap = {}	# 保存一个映射,以便根据dbid快速查找注册的玩家信息{ playerDBID:TeachInfo, ... }
		self.prenticeInfo = []	# 在线求师玩家信息的集合[ TeachInfo1, TeachInfo2, ... ]
		self.timerIntervalList = []	# [ ( playerDBID, 对应的注册到期时间 ), ... ]
		self.deregisterTimerID = 0	# 清理过期数据的timerID
		
	def _registerGloballyCB( self, complete ):
		"""
		注册全局变量的回调
		"""
		if not complete:
			ERROR_MSG( "Register TeachMgr Fail!" )
			self.registerGlobally( "TeachMgr", self._registerGloballyCB )
		else:
			BigWorld.globalData["TeachMgr"] = self		# 注册到cellApp服务器中
			INFO_MSG( "TeachMgr Create Complete!" )
			
	def _createDatabaseTable( self ):
		"""
		创建数据库表格

		@id :			自动增量, 数据库中的序列
		@sm_playerDBID:角色dbid
		@sm_playerName:的角色名字
		@sm_level:	角色等级
		@sm_metier:	角色职业
		@sm_teachCredit: 玩家的师父称号
		@sm_prenticeNum:收徒者当前徒弟数量
		@sm_registerTime:注册时间
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
		创建数据库表格回调
		"""
		if errstr:
			ERROR_MSG( "create custom_TeachInfo table error:%s." % errstr )
			return
			
		self.initialize()
		
	def initialize( self ):
		"""
		初始化师徒系统管理器
		"""
		sql = "select id, sm_playerDBID, sm_playerName, sm_level, sm_metier, sm_teachCredit, sm_prenticeNum, sm_registerTime from `custom_TeachInfo`;"
		BigWorld.executeRawDatabaseCommand( sql, self._initializeTeacherInfoCB )
		
	def _initializeTeacherInfoCB( self, result, rows, errstr ):
		"""
		从数据库读取custom_TeachInfo数据的回调
		"""
		if errstr:
			ERROR_MSG( "initialize custom_TeachInfo error:%s." % errstr )
			return
			
		for record in result:
			# [ id, 玩家dbid, 名字, 等级, 职业, 师父称号, 徒弟数量, 注册时间 ]
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
		注册timer
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
		except KeyError:	# 玩家有可能已经deregister
			pass			# 什么都不做
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
		申请注册收徒
		
		@param playerDBID : 角色dbid
		@type playerDBID : DATABASE_ID
		@param playerName : 角色名字
		@type playerName : STRING
		@param playerLevel : 玩家等级
		@type playerLevel : INT16
		@param playerMetier : 角色职业
		@type playerMetier : INT32
		@param teachTitleID : 角色功勋值
		@type teachTitleID : INT32
		@param prenticeNum : 角色的徒弟个数
		@type prenticeNum : INT8
		@param everPrenticeNum : 出师徒弟数量
		@type everPrenticeNum : INT32
		@param lastWeekOnlineTime : 上周在线时长
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
			
		# 运行清理过期数据的timer
		deregisterTime = csconst.TEACH_REGISTER_VALID_TIME + registerTime
		self.timerIntervalList.append( ( playerDBID, deregisterTime ) )
		if self.deregisterTimerID == 0:
			self.registerTimer()
			
		sql = "insert into custom_TeachInfo ( sm_playerDBID, sm_playerName, sm_level, sm_metier, sm_teachCredit, sm_prenticeNum, sm_registerTime ) value( %i, \'%s\', %i, %i, %i, %i, %i )" \
			% ( playerDBID, BigWorld.escape_string( playerName ), playerLevel, playerMetier, teachTitleID, prenticeNum, registerTime )
		BigWorld.executeRawDatabaseCommand( sql, self.registerTeachCB )
		
	def registerTeachCB( self, result, rows, errstr ):
		"""
		注册师父注册信息到数据库的回调
		"""
		if errstr:
			ERROR_MSG( errstr )
			return

	def deregister( self, playerDBID, teacherOrPrentice ):
		"""
		Define method.
		撤销注册的信息
		
		@param playerDBID : 玩家dbid
		@type playerDBID : DATABASE_ID
		"""
		try:
			teacherInfo = self.teachInfoMap[playerDBID]
		except KeyError:
			return
		deleted = False
		if teacherInfo.playerBase:
			if teacherOrPrentice == 1:	 # 注销师父
				if teacherInfo in self.teacherInfo:	 # 如果有，则删除
					teacherInfo.playerBase.client.onStatusMessage( csstatus.TEACH_LIST_LEAVE_SUCCESS, "" )
					self.teacherInfo.remove( teacherInfo )
					teacherInfo.playerBase.cell.teach_deregisterTeachInfo()
					self.teachInfoMap.pop( playerDBID )
					deleted = True
				else:
					teacherInfo.playerBase.client.onStatusMessage( csstatus.TEACH_LIST_ISNT_IN_TEACHER, "" )
			elif teacherOrPrentice == 0: # 注销徒弟
				if teacherInfo in self.prenticeInfo: # 如果有，则删除
					teacherInfo.playerBase.client.onStatusMessage( csstatus.LEAVE_PRENTICE_LIST_SUCCESS, "" )
					self.prenticeInfo.remove( teacherInfo )
					teacherInfo.playerBase.cell.teach_deregisterTeachInfo()
					self.teachInfoMap.pop( playerDBID )
					deleted = True
				else:
					teacherInfo.playerBase.client.onStatusMessage( csstatus.TEACH_LIST_ISNT_IN_PRENTICE, "" )

		sql = "delete from custom_TeachInfo where sm_playerDBID = %i" % playerDBID
		if deleted:	  # 注销成功
			BigWorld.executeRawDatabaseCommand( sql, self.deregisterTeachCB )

	def deregisterTeachCB( self, result, rows, errstr ):
		"""
		撤销注册信息的数据库回调
		"""
		if errstr:
			ERROR_MSG( errstr )
			return
			
	def getTeachExtraInfo( self, playerDBID, everPrenticeNum, lastWeekOnlineTime ):
		"""
		Define method
		玩家回调该函数，传回自己的出师徒弟数量和上周在线时间
		"""
		if self.teachInfoMap.has_key( playerDBID ):
			teachInfo = self.teachInfoMap[playerDBID]
			teachInfo.setEverPrenticeNum( everPrenticeNum )
			teachInfo.setLastWeekOnlineTime( lastWeekOnlineTime )
		
	def queryTeachInfo( self, playerBase, playerLevel ):
		"""
		Define method.
		根据玩家等级查询拜师信息
		
		@param playerBase : 请求查询的玩家的base mailbox
		@type playerBase : MAILBOX
		"""
		for record in self.teacherInfo:
			playerBase.client.teach_receiveTeachInfo( record.getTeachInfo(),1 )
		for record in self.prenticeInfo:
			playerBase.client.teach_receiveTeachInfo( record.getTeachInfo(),0 )
			
	def requestBeTeached( self, playerBase, playerName, teacherDBID ):
		"""
		Define method.
		申请拜师

		@param targetDBID : 申请目标的dbid
		@type targetDBID : DATABASE_ID
		@param playerBase : 角色名字
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
		玩家上线，把自己的base mailbox注册到管理器
		"""
		try:
			playerBase.setTeachExtraInfo()
			teachInfo = self.teachInfoMap[playerDBID]
		except KeyError:
			DEBUG_MSG( "Cannot find player( %i )'s teachInfo." % playerDBID )
			playerBase.cell.teach_deregisterTeachInfo()
		else:
			teachInfo.playerBase = playerBase
			
			# 玩家上线，把信息放到在线列表中
			if teachInfo.playerLevel >= csconst.TEACH_MASTER_MIN_LEVEL:
				self.teacherInfo.append( teachInfo )
			else:
				self.prenticeInfo.append( teachInfo )
				
	def onPlayerLoseCell( self, playerDBID ):
		"""
		Define method.
		师父离线，通知管理器
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
		玩家级别改变，更新拜师管理的数据

		@param playerDBID : 注册玩家的dbid
		@type playerDBID : DATABASE_ID
		@param playerLevel : 玩家等级
		@type playerLevel : INT16
		"""
		try:
			teachInfo = self.teachInfoMap[ playerDBID ]
		except KeyError:
			INFO_MSG( "playerDBID:%i not exist." % playerDBID )
			return

		# 如果超过徒弟应有级别，那么从管理器注销。
		# 特别注意：这个处理是建立在玩家不可能跳级的规则上。
		# 如果使用GM指令设置了玩家的等级，那么这个注销就不会成功。
		if playerLevel == csconst.TEACH_END_TEACH_LEAST_LEVEL:			#大于50级的就不应该在徒弟列表了。BY GRL
			if teachInfo in self.prenticeInfo:
				self.deregister( playerDBID, 0 )
				return

		teachInfo.playerLevel = playerLevel
		query = "update custom_TeachInfo set sm_level = %i where sm_playerDBID = %i" % ( playerLevel, playerDBID )
		BigWorld.executeRawDatabaseCommand( query, self._updatePlayerInfoCB )
		
	def onPlayerTeachTitleChange( self, playerDBID, teachTitleID ):
		"""
		Define method.
		玩家级别改变，更新拜师管理的数据

		@param playerDBID : 注册玩家的dbid
		@type playerDBID : DATABASE_ID
		@param playerTeachCredit : 玩家功勋值
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
		玩家的徒弟数量改变
		"""
		if playerDBID not in self.teachInfoMap:
			ERROR_MSG( "playerDBID:%i not exist." % playerDBID )
			return
		self.teachInfoMap[ playerDBID ].prenticeNum = prenticeNum
		query = "update custom_TeachInfo set sm_prenticeNum = %i where sm_playerDBID = %i" % ( prenticeNum, playerDBID )
		BigWorld.executeRawDatabaseCommand( query, self._updatePlayerInfoCB )
		
	def _updatePlayerInfoCB( self, result, rows, errstr ):
		"""
		更新师父数据库信息的回调
		"""
		if errstr:
			ERROR_MSG( errstr )
			
	def requestTeach( self, playerBase, playerName, targetDBID ):
		"""
		Define method.
		请求收徒
		
		@param playerBase : 请求收徒玩家的base mailbox
		@param playerName : 请求收徒玩家的名字
		@param targetDBID : 收徒目标玩家的dbid
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
				
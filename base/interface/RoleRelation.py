# -*- coding: gb18030 -*-

import BigWorld
import cschannel_msgs
import ShareTexts as ST
import time

import Love3
import csdefine
import csconst
import csstatus
from MsgLogger import g_logger
from bwdebug import *
from Function import Functor
import Const
import time
import ECBExtend

TEACH_REQUEST_TIME_OUT = 30		# 远程拜师申请时效
SWEETIE_INVITE_TIME_OUT = 30		# 恋人邀请时效

FRIENDLY_VALUE_INITIAL = 0			# 友好度初始值

INVITE_PERIOD_OF_VALIDITY = 20		# 邀请有效期
RELATION_STATUS_HIGH_OFFSET = 16	# 关系状态高位偏移量
RELATION_STATUS_LOW_OFFSET = 0	# 关系状态低位偏移量
MASTER_PRENTICE = csdefine.ROLE_RELATION_MASTER|csdefine.ROLE_RELATION_PRENTICE|csdefine.ROLE_RELATION_PRENTICE_EVER|csdefine.ROLE_RELATION_MASTER_EVER

class RelationItem:
	"""
	玩家关系数据
	"""
	def __init__( self, relationUID,
					playerName,
					relationStatus,
					relationOffset,
					friendlyValue,
					playerBase = None,
					playerDBID = 0,
				):
		"""
		@param playerDBID : 对方玩家dbid
		@param relationStatus : 与玩家的关系标记，INT32
		@param friendlyValue : 友好度，UINT32
		@param playerBase : 对方玩家base mailbox
		@param relationOffset : 表示对方玩家在关系标记中的位置，奇数还是偶数位

		relationStatus的详细解释：
		relationStatus为UINT32,描述每一个关系使用relationStatus的两个字节位模式。
		高位2个字节表示对应sm_playerDBID2玩家的关系状态，低位2字节表示对应sm_playerDBID1的玩家关系状态，
		约定：主动发起关系者对应sm_playerDBID1，被动者为sm_playerDBID2
		relationOffset描述了relationStatus标记位模式中，高位的2个字节还是低位的2个字节表示玩家的关系状态。
		"""
		self.relationUID = relationUID
		self.playerName = playerName
		self.relationStatus = relationStatus
		self.relationOffset = relationOffset		# 己方关系状态在关系状态中的偏移量
		self.friendlyValue = friendlyValue
		self.playerBase = playerBase
		self.playerDBID = playerDBID

		self.needSaveFriendlyValue = False	# 友好度是否发生了改变，以便在玩家下线的时候写db

	def convertRelation( self, relation ):
		"""
		转换此关系对应到玩家关系状态标志中相应的位

		@param relation : 关系定义
		"""
		return relation << self.relationOffset

	def convertTargetRelation( self, relation ):
		"""
		转换此关系对应到对方玩家关系状态标志中相应的位
		"""
		relationOffset = RELATION_STATUS_HIGH_OFFSET
		if self.relationOffset == RELATION_STATUS_HIGH_OFFSET:
			relationOffset = 0
		return relation << relationOffset

	def getTargetRelation( self ):
		"""
		获取和对方的关系状态
		"""
		return ( self.relationStatus >> self.relationOffset ) & 0xFFFF

	def targetHasRelation( self, relation ):
		"""
		对方和我是否存在关系，一般用于判断己方是否对方的黑名单、仇人
		"""
		offset = self.relationOffset == 0 and RELATION_STATUS_HIGH_OFFSET or 0
		return self.relationStatus & ( relation << offset )

	def meHasRelation( self, relation ):
		"""
		与对方是否存在某种关系
		"""
		return self.relationStatus & ( relation << self.relationOffset )

	def hasCoupleRelation( self ):
		"""
		是否存在夫妻关系
		"""
		return self.relationStatus & ( csdefine.ROLE_RELATION_COUPLE << RELATION_STATUS_HIGH_OFFSET ) and self.relationStatus & csdefine.ROLE_RELATION_COUPLE

	def hasTeachRelation( self ):
		"""
		是否存在师徒关系
		"""
	 	return ( self.relationStatus & csdefine.ROLE_RELATION_PRENTICE and self.relationStatus & ( csdefine.ROLE_RELATION_MASTER << RELATION_STATUS_HIGH_OFFSET ) ) \
		or ( self.relationStatus & csdefine.ROLE_RELATION_MASTER  and self.relationStatus & ( csdefine.ROLE_RELATION_PRENTICE << RELATION_STATUS_HIGH_OFFSET ) )

	def isRelationEmpty( self ):
		"""
		是否和对方已经无关系
		"""
		return self.relationStatus == 0

	def hasVoluntaryRelation( self ):
		"""
		是否和对方存在主动发起的关系
		"""
		return self.relationStatus & ( 0xFFFF << self.relationOffset )

	def addFriendlyValue( self, value, owner = None ):
		"""
		"""
		self.friendlyValue += value
		self.needSaveFriendlyValue = True
		if owner:
			owner.client.friendlyValueChanged( self.relationUID, self.friendlyValue )


class RoleRelation:
	"""
	"""
	def __init__( self ):
		self.relationDatas = {}		# { relationUID:relationItem, ... }

		self.blacklist = {}			# { playerDBID:relationItem, ... }，玩家黑名单
		self.targetBlacklist = {}		# { playerDBID:relationItem, ... }，玩家被加黑名单
		self.friends = {}				# { playerDBID:relationItem, ... }，玩家好友
		self.sweetieDict = {}			# { playerDBID:relationItem, ... }，玩家恋人
		self.couple_lover = None		# relationItem,玩家夫妻
		self.foeDict = {}				# { playerDBID:relationItem, ... }，仇人
		self.beFoeDict = {}			# { playerDBID:relationItem, ... }，被加为仇人
		self.allyDict = {}				# { playerDBID:relationItem, ... }，玩家结拜兄弟
		self.allyTitle = ""			# 结拜称号

		# 玩家初始话关系数据中，设置此标记是由于玩家此时base mailbox已创建完毕，对方玩家有可能已经通过
		# db获得己方的base mailbox并进行一些处理，在己方初始化关系数据时有相关操作请求，此时根据此标记
		# 进行具体的处理。
		self.relationInitializing = False

		self.inviteFriendBase = None					# 发起邀请好友的玩家base
		self.inviteFriendTime = 0.0						# 邀请成为好友的时间
		self.inviteSweetieUID = None					# 发起邀请成为恋人的玩家base
		self.sweetie_beInvitedTime = 0.0				# 邀请成为恋人的时刻

		self.relationIndexCounter = 0	# 初始化关系数据计数
		self.tempRelationList = []		# 初始化关系临时存储数据

		self.admirerNotifyTimerID = 0	# 上线通知仰慕者的timerID

		# 师徒关系
		self.teach_masterItem = None	# 师父的数据relationItem
		self.prenticeDict = {}		# 徒弟的数据{ playerName:relationItem, ... }
		self._inviteTeachBase = None	# 请求拜师的徒弟base mailbox
		self._inviteTeachTime = 0		# 发起远程拜师的时刻
		self.isTeachProgress = False		# 是否在拜师处理中

		self.masterEverDict = {}			# 曾经的师父
		self.prenticeEverDict = {}		# 曾经的徒弟

	def _removeRelation( self, relationUID ):
		"""
		移除关系
		"""
		query = "delete from `custom_Relation` where sm_uid = %i" % relationUID
		BigWorld.executeRawDatabaseCommand( query, self._removeRelationCB )

	def _removeRelationCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( errstr )

	def _createRelation2DB( self, relationUID, playerDBID, relationStatus ):
		"""
		添加一条关系记录
		"""
		#DEBUG_MSG( "--->>>player( %s ) create Relation:relationUID(%i), playerName( %s ), relationStatus( %s )" % ( self.getName(), relationUID, playerName, hex( relationStatus ) ) )
		query = "insert into custom_Relation set sm_playerDBID1= %i, sm_playerDBID2= %i, sm_relationStatus=%i, sm_uid = %i;" % ( self.databaseID, playerDBID, relationStatus, relationUID )
		BigWorld.executeRawDatabaseCommand( query, self._createRelation2DBCB )

	def _createRelation2DBCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( errstr )

	def _updateRelationStatus( self, relationItem, myRelation, targetRelation, isWriteDB ):
		"""
		更新关系状态
		@param relationItem : 关系数据
		@param relation : 针对的关系，定义在csdefine中
		@param isWriteDB : 是否需要写入数据库,BOOL，只有主动发起方才会更新到db
		"""
		tempRelation = myRelation | targetRelation
		relationItem.relationStatus |= tempRelation
		#DEBUG_MSG( "player( %s ) myRelation(%i), targetRelation(%i), relationStatus( %i )" % ( self.getName(), myRelation, targetRelation,relationItem.relationStatus) )
		if isWriteDB:
			query = "update `custom_Relation` set sm_relationStatus = sm_relationStatus | %i where sm_uid = %i;" % ( tempRelation, relationItem.relationUID )
			BigWorld.executeRawDatabaseCommand( query, self._addRelationStatusCB )
		DEBUG_MSG( "player( %s ) update relation:relationStatus(%i)" % ( self.getName(), relationItem.relationStatus ) )

	def _addRelationStatusCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( errstr )

	def _removeRelationStatus( self, relationItem, myRelation, targetRelation, isTargetDisband = False ):
		"""
		移除某一种关系

		@param relationItem : 关系数据
		@param myRelation : 针对的关系，定义在csdefine中
		@param isTargetDisband : 对方是否解除了关系
		"""
		relationItem.relationStatus &= ~myRelation
		relationItem.relationStatus &= ~targetRelation
		#DEBUG_MSG( "--->>>player( %s):myRelation(%i), targetRelation(%i),relationStatus(%i)" %( self.getName(), myRelation, targetRelation, relationItem.relationStatus ) )
		if relationItem.relationStatus == 0:
			del self.relationDatas[relationItem.relationUID]
			if isTargetDisband:
				self._removeRelation( relationItem.relationUID )
				return
		query = "update `custom_Relation` set sm_relationStatus = sm_relationStatus & %i where sm_uid = %i;" % ( ~myRelation, relationItem.relationUID )
		BigWorld.executeRawDatabaseCommand( query, self._removeRelationStatusCB )

	def _removeRelationStatusCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( errstr )

	def _saveFriendlyValue( self, relationItem ):
		"""
		保存relationItem的友好度到db
		"""
		query = "update `custom_Relation` set sm_friendlyValue = %i where sm_uid = %i;" % ( relationItem.friendlyValue, relationItem.relationUID )
		BigWorld.executeRawDatabaseCommand( query, self._saveFriendlyValueCB )
		
	def _saveFriendlyValueCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( errstr )

	def _getTeachMgr( self ):
		"""
		获得拜师管理器
		"""
		return BigWorld.globalData["TeachMgr"]

	def rlt_onLevelUp( self ):
		"""
		玩家级别改变，通知感兴趣的其他玩家
		"""
		for relationItem in self.friends.itervalues():
			if relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ) or relationItem.playerBase is None:
				continue
			relationItem.playerBase.client.rlt_onLevelChanged( relationItem.relationUID, self.level )
		if self.teach_masterItem:
			if self.teach_masterItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ) or self.teach_masterItem.playerBase is None:
				return
			self.teach_masterItem.playerBase.client.rlt_onLevelChanged( self.teach_masterItem.relationUID, self.level )
		else:
			for relationItem in self.prenticeDict.itervalues():
				if relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ) or relationItem.playerBase is None:
					continue
				relationItem.playerBase.client.rlt_onLevelChanged( relationItem.relationUID, self.level )
				
	def onLoseCell( self ):
		"""
		玩家下线通知
		"""
		for relationUID in self.relationDatas:
			relationItem = self.relationDatas[relationUID]
			try:
				relationItem.playerBase.rlt_onPlayerLogout( relationUID )
			except AttributeError:
				pass
			if relationItem.needSaveFriendlyValue:
				self._saveFriendlyValue( relationItem )

	def onGetCell( self ):
		"""
		玩家cell创建完毕
		"""
		# 初始化玩家关系
		query = """select cr.sm_playerDBID1, cr.sm_playerDBID2, cr.sm_relationStatus, cr.sm_friendlyValue,
                                        cr.sm_uid, cr.sm_param, r.sm_playerName, r.sm_roleState
                                        from custom_Relation as cr, tbl_Role as r
                                        where cr.sm_playerDBID1 = %s and
                                        cr.sm_playerDBID2 = r.id
					union
					select cr.sm_playerDBID1, cr.sm_playerDBID2, cr.sm_relationStatus, cr.sm_friendlyValue,
                                        cr.sm_uid, cr.sm_param, r.sm_playerName, r.sm_roleState from custom_Relation as cr, tbl_Role as r
                                        where cr.sm_playerDBID2 = %s and
                                        cr.sm_playerDBID1 = r.id;
				""" % ( self.databaseID, self.databaseID )
		BigWorld.executeRawDatabaseCommand( query, self._getRelationRecordCB )

	def _getRelationRecordCB( self, result, rows, errstr ):
		"""
		读取关系数据表回调

		record[0] : sm_playerDBID1
		record[1] : sm_playerDBID2
		record[2] : sm_relationStatus
		record[3] : sm_friendlyValue
		record[4] : sm_uid
		record[5] : sm_param
		record[6] : sm_playerName
		record[7] : sm_roleState
		
		"""
		if self.isDestroyed:
			INFO_MSG( "relation initialization stop since entity had been destroyed." )
			return

		if errstr:
			ERROR_MSG( "player( %s ),errstr:%s" % ( self.getName(), errstr )  )
			return

		if rows == 0:
			DEBUG_MSG( "( %s )不存在关系数据。" % self.getName() )
			return

		for record in result:
			uid = int( record[4] )
			roleState = int( record[7] )
			relationStatus = int( record[2] )
			targetName = record[6]
			if self.databaseID == int(record[0]):
				targetDBID = int( record[1] )
				relationOffset = 0
				targetStatus = relationStatus >> RELATION_STATUS_HIGH_OFFSET
				myStatus = relationStatus & 0xFFFF
			else:
				targetDBID = int( record[0] )
				relationOffset = RELATION_STATUS_HIGH_OFFSET
				targetStatus = relationStatus & 0xFFFF
				myStatus = relationStatus >> relationOffset
			relationItem = RelationItem( uid, targetName, relationStatus, relationOffset, int( record[3] ), None, targetDBID )
			self.relationDatas[uid] = relationItem
			# 处理不在线时的关系变化

			for relation in csconst.MULTI_RELATION_LIST:	# 双边关系处理
				if myStatus & relation == 0:
					continue
				if targetStatus & relation == 0:	# 对方解除了关系
					if relation == csdefine.ROLE_RELATION_FRIEND:
						myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_FRIEND )
						targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_FRIEND )
						self._removeRelationStatus( relationItem, myRelation, targetRelation, True )
						self.statusMessage( csstatus.FRIEND_TARGET_REMOVE, relationItem.playerName )
					elif relation == csdefine.ROLE_RELATION_SWEETIE:
						myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_SWEETIE )
						targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_SWEETIE )
						self._removeRelationStatus( relationItem, myRelation, targetRelation, True )
						self.statusMessage( csstatus.SWEETIE_BE_REMOVE_SUCCESS, relationItem.playerName )
					elif relation == csdefine.ROLE_RELATION_COUPLE:
						self.couple_lover = relationItem		# 手续还没办完，还算是夫妻
						self.cell.couple_dstForceDivorce()
					elif relation == csdefine.ROLE_RELATION_ALLY:
						self.cell.removeTitle( csdefine.TITLE_ALLY_ID )
						myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_ALLY )
						targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_ALLY )
						self._removeRelationStatus( relationItem, myRelation, targetRelation, True )
						self.statusMessage( csstatus.ALLY_MEMBER_QUIT, relationItem.playerName )
				else:
					if relation == csdefine.ROLE_RELATION_FRIEND:
						self.friends[targetDBID] = relationItem
					elif relation == csdefine.ROLE_RELATION_SWEETIE:
						self.sweetieDict[targetDBID] = relationItem
					elif relation == csdefine.ROLE_RELATION_COUPLE:
						self.couple_lover = relationItem
					elif relation == csdefine.ROLE_RELATION_ALLY:
						self.allyDict[targetDBID] = relationItem
						if self.allyTitle != record[5]:
							self.allyTitle = record[5]
							self.client.receiveAllyTitle( self.allyTitle, csdefine.ALLY_TITILE_CHANGE_REASON_INIT )
			if relationItem.relationStatus == 0:	# 经过处理如果此时双方已无关系
				continue
			for relation in csconst.SINGLE_RELATION_LIST:	# 单边关系处理
				if myStatus & relation == 0 and targetStatus & relation == 0:
					continue
				if relation == csdefine.ROLE_RELATION_BLACKLIST:
					if myStatus & relation:
						self.blacklist[targetDBID] = relationItem
					if targetStatus & relation:
						self.targetBlacklist[targetDBID] = relationItem
				elif relation == csdefine.ROLE_RELATION_FOE:
					if myStatus & relation:
						self.foeDict[targetDBID] = relationItem
					if targetStatus & relation:
						self.beFoeDict[targetDBID] = relationItem
				elif relation == csdefine.ROLE_RELATION_MASTER:
					if myStatus & relation:	# 己方是师父							
						self.prenticeDict[targetDBID] = relationItem
						if not targetStatus & csdefine.ROLE_RELATION_PRENTICE:	# 如果对方不是徒弟 
							# 对方解除了关系，从cell开始清除数据
							self.cell.targetDisbandTeach( relationItem.playerDBID, csdefine.ROLE_RELATION_PRENTICE )
						if roleState == 1:	#对方删号了
							self.cell.teach_disband( relationItem.playerDBID, relationItem.playerName )
							self.statusMessage( csstatus.ROLE_RELATION_NOT_EXIST, cschannel_msgs.ROLERELATION_TARGET_PRIENTICE, targetName )
				elif relation == csdefine.ROLE_RELATION_PRENTICE:
					if myStatus & relation:	# 己方是徒弟
						self.teach_masterItem = relationItem
						if not targetStatus & csdefine.ROLE_RELATION_MASTER:	# 如果对方不是师父 
							self.cell.targetDisbandTeach( relationItem.playerDBID, csdefine.ROLE_RELATION_MASTER )							
						if roleState == 1:	#对方删号了
							self.cell.teach_disband( relationItem.playerDBID, relationItem.playerName )
							self.statusMessage( csstatus.ROLE_RELATION_NOT_EXIST, cschannel_msgs.ROLERELATION_TARGET_FMASTER, targetName )
				elif relation == csdefine.ROLE_RELATION_MASTER_EVER:
					if myStatus & relation:
						self.prenticeEverDict[targetDBID] = relationItem
				elif relation == csdefine.ROLE_RELATION_PRENTICE_EVER:
					if myStatus & relation:
						self.masterEverDict[targetDBID] = relationItem

		self.admirerNotifyTimerID = self.addTimer( Const.RELATION_ADMIRE_NOTIFY_INTERVAL * 0.5, Const.RELATION_ADMIRE_NOTIFY_INTERVAL, ECBExtend.FRIEND_NOTIFY_ADMIRER_TIMER_CBID )

	def targetRemoveRelationCB( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( errstr )

	def onTimer_relationNotify( self, timerID, userData ):
		"""
		timer
		通知存在关系的玩家，我上线了
		"""
		length = len( self.relationDatas )
		count = min( Const.RELATION_ADMIRE_COUNT_NOTIFY, length - self.relationIndexCounter )
		self.tempRelationList = self.relationDatas.values()		# 生成一个临时列表
		for i in xrange( count ):
			index = i + self.relationIndexCounter
			relationItem = self.tempRelationList[index]
			Love3.g_baseApp.lookupRoleBaseByName( relationItem.playerName, Functor( self.__onNotifyCB, relationItem ) )
		self.relationIndexCounter += count

		# 通知完成
		if self.relationIndexCounter >= length:
			self.delTimer( self.admirerNotifyTimerID )
			self.relationIndexCounter = 0
			self.tempRelationList = []

	def __onNotifyCB( self, relationItem, callResult ):
		"""
		上线通知和己方有关系的玩家

		@param playerName		:	玩家名称
		@type playerName		:	string
		@param callResult	:	玩家BASE
		@type callResult	:	mailbox
		"""
		if not hasattr( self, "cell" ) or not hasattr( self, "client" ):
			return
		relationUID = relationItem.relationUID
		if not callResult is None:
			relationItem.playerBase = callResult
			callResult.rlt_onPlayerLogon( relationUID, self )
			if relationItem.hasVoluntaryRelation():
				if relationItem.meHasRelation( csdefine.ROLE_RELATION_FOE ):
					self.statusMessage( csstatus.FOE_TARGET_ONLINE, relationItem.playerName )
				if relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ) or not hasattr( callResult, "cell" ):
					self.client.rtf_receiveNameInfo( relationItem.playerName, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
				else:
					callResult.cell.rlt_sendPlayerInfo( self, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
		else:
			if relationItem.hasVoluntaryRelation():
				self.client.rtf_receiveNameInfo( relationItem.playerName, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
		if relationItem.hasCoupleRelation():
			self.cell.receiveCoupleInfo( {"playerDBID":relationItem.playerDBID,"playerBase":callResult} )
		if relationItem.hasTeachRelation():
			self.cell.receiveTeachInfo( {"playerDBID":relationItem.playerDBID,"playerBase":callResult}, relationItem.getTargetRelation() )
		if relationItem.meHasRelation( csdefine.ROLE_RELATION_ALLY ):
			self.cell.receiveAllyInfo( {"playerDBID":relationItem.playerDBID,"playerBase":callResult} )

	def relationStatusMessage( self, targetBaseMailbox, statusID, *args ):
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

	def rlt_onPlayerLogon( self, relationUID, playerBase ):
		"""
		Define method.
		有关系的玩家上线了

		@param playerDBID : 上线的玩家dbid
		@param playerBase : 上线玩家的base mailbox
		"""
		try:
			relationItem = self.relationDatas[relationUID]
		except KeyError:
			ERROR_MSG( "玩家( %s )找不到数据( %i )。" % ( self.getName(), relationUID ) )
			return
#		if relationItem.meHasRelation( csdefine.ROLE_RELATION_FOE ):
#			self.statusMessage( csstatus.FOE_TARGET_LOGON, relationItem.playerName )
		if relationItem.meHasRelation( csdefine.ROLE_RELATION_COUPLE ):
			self.cell.onHelpmateLogin( playerBase )
		if relationItem.hasTeachRelation():
			self.cell.onTeachLogin( relationItem.playerDBID, playerBase, relationItem.getTargetRelation() )

		relationItem.playerBase = playerBase
		if relationItem.hasVoluntaryRelation() and not relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ) and hasattr( playerBase, "cell" ):
			playerBase.cell.rlt_requestPlayerInfo( self, relationUID )
			
		if relationItem.hasVoluntaryRelation() and not relationItem.meHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):	# 上线提示
			relationStr = self.getPriorRelationStr( relationItem )
			if relationStr != "":
				self.statusMessage( csstatus.ROLE_RELATION_TARGET_LOGON, relationStr, relationItem.playerName )

	def rlt_onPlayerLogout( self, relationUID ):
		"""
		Define method.
		存在关系的玩家下线了
		"""
		try:
			relationItem = self.relationDatas[relationUID]
		except KeyError:
			ERROR_MSG( "player( %s ) has no relationUID( %i )." % ( self.getName(), relationUID ) )
			return
		relationItem.playerBase = None
		if relationItem.meHasRelation( csdefine.ROLE_RELATION_COUPLE ):
			self.cell.onHelpmateLogout()
		if relationItem.hasTeachRelation():
			self.cell.onTeachLogout( relationItem.playerDBID, relationItem.getTargetRelation() )
		if relationItem.hasVoluntaryRelation():
			if relationItem.needSaveFriendlyValue:	# 如果对方先下线保存了友好度，己方下线时不再需要保存
				relationItem.needSaveFriendlyValue = False
			if not relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):
				self.client.rlt_offlineUpdate( relationUID )
				
		if relationItem.hasVoluntaryRelation() and not relationItem.meHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):	# 下线线提示
			relationStr = self.getPriorRelationStr( relationItem )
			if relationStr != "":
				self.statusMessage( csstatus.ROLE_RELATION_TARGET_LOGOFF, relationStr, relationItem.playerName )
	
	def getPriorRelationStr( self, relationItem ) :
		"""
		获取优先的关系		
		"""
		relationStatus_ = ""
		if relationItem.hasVoluntaryRelation():
			if relationItem.meHasRelation( csdefine.ROLE_RELATION_COUPLE ):		# 伴侣
				relationStatus_ = cschannel_msgs.ROLERELATION_TARGET_COUPLE 
			elif relationItem.meHasRelation( csdefine.ROLE_RELATION_SWEETIE ):	# 恋人
				relationStatus_ = cschannel_msgs.ROLERELATION_TARGET_SWEETIE 
			elif relationItem.meHasRelation( csdefine.ROLE_RELATION_ALLY ):		# 结拜
				relationStatus_ = cschannel_msgs.ROLERELATION_TARGET_ALLY 
			elif relationItem.meHasRelation( csdefine.ROLE_RELATION_MASTER )\
			 	or relationItem.meHasRelation( csdefine.ROLE_RELATION_MASTER_EVER ):		# 师傅/过去的师傅
				relationStatus_ = cschannel_msgs.ROLERELATION_TARGET_PRIENTICE
			elif relationItem.meHasRelation( csdefine.ROLE_RELATION_PRENTICE )\
				 or relationItem.meHasRelation( csdefine.ROLE_RELATION_PRENTICE_EVER ):		# 徒弟/过去的徒弟
				relationStatus_ = cschannel_msgs.ROLERELATION_TARGET_FMASTER 
			elif relationItem.meHasRelation( csdefine.ROLE_RELATION_FRIEND ):	# 好友
				relationStatus_ = cschannel_msgs.ROLERELATION_TARGET_FRIEND 
			elif relationItem.meHasRelation( csdefine.ROLE_RELATION_FOE ):		# 仇人
				relationStatus_ = cschannel_msgs.ROLERELATION_TARGET_FOE 
		else:
			ERROR_MSG( "player( %s ) has no relation." % ( self.getName() ) )
		return relationStatus_

	#----------------------------------------------------------------
	#  好友
	#----------------------------------------------------------------
	def addTeamFriendlyValue( self, teammateDBIDList ):
		"""
		Define method.
		玩家组队打怪，杀死怪物，队友中如果有好友，那么友好度增加。

		@param teammateDBIDList : 玩家dbid列表
		"""
		for dbid in teammateDBIDList:
			try:
				relationItem = self.friends[dbid]
			except KeyError:
				continue
			else:
				relationItem.addFriendlyValue( 1, self )

	def addFriend( self, playerName ):
		"""
		Exposed method.
		添加好友

		@param playerName	:	玩家名称
		@type playerName	:	STRING
		"""
		if self.getName() == playerName:
			self.statusMessage( csstatus.FRIEND_NOT_ADD_SELF_FRIEND )
			return
		if self.getFriendCount() >= Const.FRIEND_FRIEND_MAX_COUNT:
			self.statusMessage( csstatus.FRIEND_FRIENDLIST_FULL )
			return
		if self.hasFriend( playerName ):
			self.statusMessage( csstatus.FRIEND_FRIEND_EXIST )
			return
		if self.hasFoe( playerName ):
			self.statusMessage( csstatus.FOE_HAS_EXIST )
			return

		Love3.g_baseApp.lookupRoleBaseByName( playerName, self.__onLookUpFriendBaseCB )

	def __onLookUpFriendBaseCB( self, callResult ):
		"""
		addFriend中lookupRoleBaseByName搜索回调

		@param callResult: 玩家名称
		@type callResult: STRING
		"""
		if callResult is None:
			self.statusMessage( csstatus.FRIEND_NOT_ON_LINE )
			return
		callResult.beInvitedForFriend( self, self.getName() )

	def beInvitedForFriend( self, playerBase, playerName ):
		"""
		Define method.
		对方邀请己方成为好友
		"""
		if self.inviteFriendBase and self.inviteFriendTime < INVITE_PERIOD_OF_VALIDITY:
			playerBase.client.onStatusMessage( csstatus.FRIEND_BEING_INVITED, "" )
			return

		if self.getFriendCount() >= Const.FRIEND_FRIEND_MAX_COUNT:
			playerBase.client.onStatusMessage( csstatus.FRIEND_FRIENDLIST_FULL, "" )
			return

		self.cell.beAskedToFriend( playerBase, playerName )

	def beInvitedToFriend( self, playerBase, playerName ):
		"""
		Define method.
		被邀请成为好友
		"""
		self.inviteFriendBase = playerBase
		self.inviteFriendTime = time.time()
		self.client.beAskedForFriend( playerName )

	def replyForFriendInvite( self, reply ):
		"""
		Exposed method.
		加好友邀请的回答
		"""
		if self.inviteFriendBase is None:
			return

		if not reply:
			self.inviteFriendBase.client.onStatusMessage( csstatus.FRIEND_REFUSE_INVITE, "" )
		else:
			if self.getFriendCount() >= Const.FRIEND_FRIEND_MAX_COUNT:
				self.inviteFriendBase.client.onStatusMessage( csstatus.FRIEND_FRIENDLIST_FULL, "" )
			else:
				self.inviteFriendBase.addFriendReplyTrue( self, self.getName(), self.databaseID )
		self.inviteFriendBase = None
		self.inviteFriendTime = 0.0

	def addFriendReplyTrue( self, playerBase, playerName, playerDBID ):
		"""
		Define method.
		对方玩家同意成为好友。
		playerName, relationStatus, relationOffset, friendlyValue, playerBase, playerDBID
		"""
		if self.getFriendCount() >= Const.FRIEND_FRIEND_MAX_COUNT:
			self.statusMessage( csstatus.FRIEND_FRIENDLIST_FULL )
			return

		# 在成为好友前，对方有可能在己方的黑名单或仇人名单中，或己方在对方的黑名单或仇人名单中
		relationItem = self.getRelationItemByName( playerName )
		if relationItem is None:
			relationUID = Love3.g_baseApp.getRelationUID()
			if relationUID == -1:
				return
			relationStatus = csdefine.ROLE_RELATION_FRIEND | ( csdefine.ROLE_RELATION_FRIEND << RELATION_STATUS_HIGH_OFFSET )
			# 约定：发起加好友者作为sm_playerName1写入db
			relationItem = RelationItem( relationUID, playerName, relationStatus, 0, 0, playerBase, playerDBID )
			self.relationDatas[relationUID] = relationItem
			self._createRelation2DB( relationUID, playerDBID, relationStatus )
			playerBase.addFriendSuccess( relationUID, self.getName(), self.databaseID, self )
		else:
			relationUID = relationItem.relationUID
			myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_FRIEND )
			targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_FRIEND )
			self._updateRelationStatus( relationItem, myRelation, targetRelation, True )
			playerBase.updateRelation2Friend( relationUID )
		self.friends[playerDBID] = relationItem
		self.statusMessage( csstatus.FRIEND_ADD_FRIEND_COMPLETE )
		if not relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):
			playerBase.cell.rlt_sendPlayerInfo( self, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
		else:
			self.client.rtf_receiveNameInfo( relationItem.playerName, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )

	def updateRelation2Friend( self, relationUID ):
		"""
		Define method.
		对方邀请己方加好友，己方同意，且之前已存在关系，那么更新关系到好友
		"""
		relationItem = self.relationDatas[relationUID]
		relationItem.relationStatus |= csdefine.ROLE_RELATION_FRIEND | ( csdefine.ROLE_RELATION_FRIEND << RELATION_STATUS_HIGH_OFFSET )
		self.friends[relationItem.playerDBID] = relationItem
		self.statusMessage( csstatus.FRIEND_ADD_FRIEND_COMPLETE )
		if not relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):
			relationItem.playerBase.cell.rlt_sendPlayerInfo( self, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
		else:
			self.client.rtf_receiveNameInfo( relationItem.playerName, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )

	def addFriendSuccess( self, relationUID, playerName, playerDBID, playerBase ):
		"""
		Define method.
		同意对方的加好友邀请，加好友成功，设置己方的好友数据
		约定：己方不是主动发起者，因此关系状态偏移量是RELATION_STATUS_HIGH_OFFSET
		"""
		relationStatus = csdefine.ROLE_RELATION_FRIEND | ( csdefine.ROLE_RELATION_FRIEND << RELATION_STATUS_HIGH_OFFSET )
		relationItem = RelationItem( relationUID, playerName, relationStatus, RELATION_STATUS_HIGH_OFFSET, 0, playerBase, playerDBID )
		self.relationDatas[relationUID] = relationItem
		self.friends[playerDBID] = relationItem
		self.statusMessage( csstatus.FRIEND_ADD_FRIEND_COMPLETE )
		if not relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):
			playerBase.cell.rlt_sendPlayerInfo( self, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
		else:
			self.client.rtf_receiveNameInfo( relationItem.playerName, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )

	def removeFriend( self, relationUID ):
		"""
		Exposed method.
		移除好友关系
		"""
		try:
			relationItem = self.relationDatas[relationUID]
		except KeyError:
			return
		if relationItem.meHasRelation( csdefine.ROLE_RELATION_SWEETIE ):
			self.statusMessage( csstatus.FRIEND_CANT_REMOVE_COS_OTHER )
			return
		if relationItem.meHasRelation( csdefine.ROLE_RELATION_ALLY ):
			self.statusMessage( csstatus.FRIEND_CANT_REMOVE_COS_OTHER )
			return
		try:
			relationItem.addFriendlyValue( -relationItem.friendlyValue )
			del self.friends[relationItem.playerDBID]
		except KeyError:
			ERROR_MSG( "friend( %s ) is not exist!" % relationItem.playerName )
			return
		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_FRIEND )
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_FRIEND )
		self._removeRelationStatus( relationItem, myRelation, targetRelation, False )
		self.statusMessage( csstatus.FRIEND_DELETE_FRIEND_COMPLETE )
		self.client.endRelationUpdate( relationUID, csdefine.ROLE_RELATION_FRIEND )
		if relationItem.playerBase:
			relationItem.playerBase.dstRemoveFriend( relationUID )

	def dstRemoveFriend( self, relationUID ):
		"""
		Define method.
		对方移除了好友关系，设置己方数据
		"""
		relationItem = self.relationDatas[relationUID]
		relationItem.addFriendlyValue( -relationItem.friendlyValue )
		del self.friends[relationItem.playerDBID]
		self.statusMessage( csstatus.FRIEND_TARGET_REMOVE, relationItem.playerName )
		#relationItem.relationStatus &= ~relationItem.convertTargetRelation( csdefine.ROLE_RELATION_FRIEND )
		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_FRIEND )
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_FRIEND )
		self._removeRelationStatus( relationItem, myRelation, targetRelation, True )
		self.client.endRelationUpdate( relationUID, csdefine.ROLE_RELATION_FRIEND )

	def getFriendCount( self ):
		"""
		返回好友数量
		"""
		return len( self.friends )

	def hasFriend( self, playerName ):
		"""
		是否已经存在好友
		"""
		for item in self.friends.itervalues():
			if item.playerName == playerName:
				return True
		return False
		

	#----------------------------------------------------------------
	#  黑名单.
	#----------------------------------------------------------------
	def hadBlacklist( self, playerName ):
		"""
		是否已经存在黑名单
		"""
		for item in self.blacklist.itervalues():
			if item.playerName == playerName:
				return True
		return False

	def addBlacklist( self, playerName ):
		"""
		Exposed method.
		把playerName添加黑名单
		"""
		if self.getName() == playerName:
			self.statusMessage( csstatus.FRIEND_NOT_ADD_SELF_BLACKlIST )
			return

		if self.hadBlacklist( playerName ):
			return

		if self.getBlacklistCount() > Const.FRIEND_BLACKLIST_MAX_COUNT:
			self.statusMessage( csstatus.FRIEND_BLACKLIST_FULL )
			return

		relationItem = self.getRelationItemByName( playerName )
		if relationItem is None:
			Love3.g_baseApp.lookupRoleBaseByName( playerName, self._addBlacklistLookUpBaseCB )
			#BigWorld.lookUpBaseByName( "Role", playerName, Functor( self._addBlacklistLookUpCB, playerName ) )
		else:
			self.statusMessage( csstatus.FRIEND_ADD_BLACKLIST_COMPLETE )
			hasVoluntary = relationItem.hasVoluntaryRelation()
			self.blacklist[relationItem.playerDBID] = relationItem
			myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_BLACKLIST )
			self._updateRelationStatus( relationItem, myRelation, 0, True )
			if hasVoluntary:	# 如果已经存在关系
				self.client.rtf_relationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_BLACKLIST )
			else:
				self.client.rtf_receiveNameInfo( playerName, relationItem.relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
			if relationItem.playerBase:
				relationItem.playerBase.beUpdated2Blacklist( relationItem.relationUID )
			self.client.rlt_offlineUpdate( relationItem.relationUID )

	def _addBlacklistLookUpBaseCB( self, result ):
		"""
		查询欲加为黑名单的好友是否在线
		"""
		if result is None:
			self.statusMessage( csstatus.CANT_ADD_BLACKLIST_OFFLINE )
			return
		result.rlt_addBlacklistRequest( self )

	def rlt_addBlacklistRequest( self, playerBase ):
		"""
		Define method.
		对方玩家把自己加为黑名单，把所需数据发给对方。
		"""
		playerBase.rlt_addBlacklistReply( self, self.databaseID, self.getName() )

	def rlt_addBlacklistReply( self, playerBase, playerDBID, playerName ):
		"""
		Define method.
		加对方为黑名单数据请求的回复
		"""
		# 此时条件有可能已经不满足
		if self.hadBlacklist( playerName ):
			return
		if self.getBlacklistCount() > Const.FRIEND_BLACKLIST_MAX_COUNT:
			return

		relationUID = Love3.g_baseApp.getRelationUID()
		if relationUID == -1:
			return
		# 低位表示主动发起关系着的关系状态
		relationStatus = csdefine.ROLE_RELATION_BLACKLIST
		relationItem = RelationItem( relationUID, playerName, relationStatus, 0, 0, playerBase, playerDBID )
		self._createRelation2DB( relationUID, playerDBID, relationStatus )
		self.relationDatas[relationUID] = relationItem
		self.blacklist[playerDBID] = relationItem
		self.statusMessage( csstatus.FRIEND_ADD_BLACKLIST_COMPLETE )
		self.client.rtf_receiveNameInfo( playerName, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
		playerBase.beAdded2BlackList( relationUID, self.getName(), self.databaseID, self )

	def beAdded2BlackList( self, relationUID, playerName, playerDBID, playerBase ):
		"""
		Define method.
		被加到黑名单中，初次建立关系
		"""
		relationStatus = csdefine.ROLE_RELATION_BLACKLIST
		relationItem = RelationItem( relationUID, playerName, relationStatus, RELATION_STATUS_HIGH_OFFSET, 0, playerBase, playerDBID )
		self.relationDatas[relationUID] = relationItem
		self.targetBlacklist[playerDBID] = relationItem

	def beUpdated2Blacklist( self, relationUID ):
		"""
		Define method.
		被加入了黑名单，之前已经建立关系了
		"""
		relationItem = self.relationDatas[relationUID]
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_BLACKLIST )
		self._updateRelationStatus( relationItem, 0, targetRelation, False )
		self.targetBlacklist[relationItem.playerDBID] = relationItem
		if relationItem.hasVoluntaryRelation():
			self.client.rlt_offlineUpdate( relationUID )

	def removeBlacklist( self, relationUID ):
		"""
		Exposed method.
		"""
		try:
			relationItem = self.relationDatas[relationUID]
		except KeyError:
			HACK_MSG( "--->>>player(%s):relation( %i ) dose not exist!!" % ( self.getName(), relationUID ) )
			return
		if not relationItem.meHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):
			HACK_MSG( "--->>>player(%s):BLACKLIST relation( %i ) dose not exist!!!" % ( self.getName(), relationUID ) )
			return
		del self.blacklist[relationItem.playerDBID]
		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_BLACKLIST )
		self._removeRelationStatus( relationItem, myRelation, 0, True )
		self.client.endRelationUpdate( relationUID, csdefine.ROLE_RELATION_BLACKLIST )
		if relationItem.playerBase:
			relationItem.playerBase.dstRemoveBlacklist( relationUID )
			if relationItem.hasVoluntaryRelation():
				relationItem.playerBase.cell.rlt_requestPlayerInfo( self, relationUID )

	def dstRemoveBlacklist( self, relationUID ):
		"""
		Define method.
		对方移除了黑名单
		"""
		try:
			relationItem = self.relationDatas[relationUID]
		except KeyError:
			HACK_MSG( "--->>>player(%s):relation( %i ) dose not exist!!" % ( self.getName(), relationUID ) )
			return
		relationItem.relationStatus &= ~relationItem.convertTargetRelation( csdefine.ROLE_RELATION_BLACKLIST )
		del self.targetBlacklist[relationItem.playerDBID]
		if relationItem.relationStatus == 0:
			del self.relationDatas[relationUID]
			return
		if relationItem.hasVoluntaryRelation():
			relationItem.playerBase.cell.rlt_requestPlayerInfo( self, relationUID )

	def getBlacklistCount( self ):
		"""
		获取黑名单长度
		"""
		return len( self.blacklist )

	def meInBlacklist( self, playerName ):
		"""
		己方在对方的黑名单中
		"""
		for item in self.targetBlacklist.itervalues():
			if item.playerName == playerName:
				return True
		return False

	# ----------------------------------------------------------------------------
	# 恋人
	# ----------------------------------------------------------------------------
	def addSweetie( self, relationUID ):
		"""
		结为恋人的申请。

		到base检测是否好友且友好度值等条件
		合法后和加好友类似，要更新relationStatus的状态。重要的是客户端表现调整
		"""
		try:
			relationItem = self.relationDatas[relationUID]
		except KeyError:
			ERROR_MSG( "player( %s )'s relation( %i ) is not exist!" % ( self.getName(), relationUID ) )
			return
		playerDBID = relationItem.playerDBID
		if self.couple_lover and playerDBID == self.couple_lover.playerDBID:
			self.statusMessage( csstatus.SWEETIE_RELATION_EXIST )
			return
		if playerDBID in self.sweetieDict:
			self.statusMessage( csstatus.SWEETIE_RELATION_EXIST )
			return
		if playerDBID in self.allyDict:
			# 已经结拜，不能结为恋人。
			self.statusMessage( csstatus.CANNOT_SWEETIE_CAUSE_ALLY )
			return
		if len( self.sweetieDict ) >= csconst.SWEETIE_NUM_LIMIT:
			self.statusMessage( csstatus.SWEETIE_SWEETIE_NUM_LIMIT )
			return
		if relationItem.friendlyValue < csconst.ADD_SWEETIE_NEED_FRIENDLY_VALUE:
			self.statusMessage( csstatus.SWEETIE_FRIENDLY_LACK )
			return
		if relationItem.playerBase:
			relationItem.playerBase.beInvitedSweetie( self.getGender(), relationUID )
		else:
			self.statusMessage( csstatus.SWEETIE_TARGET_LOGOUT )

	def beInvitedSweetie( self, inviterGender, relationUID ):
		"""
		Define method.
		被邀请成为恋人

		@param inviterGender : 邀请者的性别
		@param relationUID : 关系uid
		"""
		relationItem = self.relationDatas[relationUID]
		playerBase = relationItem.playerBase
		if self.getGender() == inviterGender:
			self.relationStatusMessage( playerBase, csstatus.SWEETIE_THE_SAME_SEX )	# 同性之间不能结交
			return
		if len( self.sweetieDict ) >= csconst.SWEETIE_NUM_LIMIT:
			self.relationStatusMessage( playerBase, csstatus.SWEETIE_SWEETIE_NUM_LIMIT )
			return
		if self.level < csconst.SWEETIE_LEVEL_LIMIT:
			self.relationStatusMessage( playerBase, csstatus.SWEETIE_TARGET_LEVEL_LACK )
			return
		if relationItem.friendlyValue < csconst.ADD_SWEETIE_NEED_FRIENDLY_VALUE:
			self.relationStatusMessage( playerBase, csstatus.SWEETIE_FRIENDLY_LACK )
			return
		#condition1 = self.inviteSweetieUID and time.time() - self.sweetie_inviteTime < SWEETIE_INVITE_TIME_OUT
		#condition2 = self.inviteSweetieUID and time.time() - self.sweetie_beInvitedTime < SWEETIE_INVITE_TIME_OUT
		if self.inviteSweetieUID and time.time() - self.sweetie_beInvitedTime < SWEETIE_INVITE_TIME_OUT:
			self.relationStatusMessage( playerBase, csstatus.SWEETIE_TARGET_BUSY )
			return

		self.cell.beInvitedToSweetie( playerBase, relationUID )

	def beInvitedToSweetie( self, relationUID ):
		"""
		Define method.
		被邀请成为恋人
		"""
		self.inviteSweetieUID = relationUID				# 以便同意结交时确定是和谁结交为恋人
		self.sweetie_beInvitedTime = time.time()
		self.client.beInvitedSweetie( relationUID )

	def replyForSweetieInvite( self, reply ):
		"""
		Exposed method.
		玩家回复结交恋人邀请的接口

		@param reply: 同意或拒绝
		@type reply: BOOL
		"""
		if not reply:
			self.relationStatusMessage( self.relationDatas[self.inviteSweetieUID].playerBase, csstatus.SWEETIE_BE_REFUSEED, self.getName() )
		else:
			self.relationDatas[self.inviteSweetieUID].playerBase.cell.addSweetieSuceeded( self.inviteSweetieUID )

	def addSweetieSuceeded( self, relationUID ):
		"""
		Define method.
		结交恋人成功，设置数据
		"""
		relationItem = self.relationDatas[relationUID]
		self.sweetieDict[relationItem.playerDBID] = relationItem
		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_SWEETIE )
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_SWEETIE )
		self._updateRelationStatus( relationItem, myRelation, targetRelation, True )
		temp = cschannel_msgs.BCT_JSGX_BECOME_LOVERS % ( self.getName(), relationItem.playerName )
		Love3.g_baseApp.anonymityBroadcast( temp, [] )
		self.client.rtf_relationUpdate( relationUID, csdefine.ROLE_RELATION_SWEETIE )
		relationItem.playerBase.updateRelation2Sweetie( relationUID )

	def updateRelation2Sweetie( self, relationUID ):
		"""
		Define method.
		结交恋人成功，更新关系数据到恋人
		"""
		relationItem = self.relationDatas[relationUID]
		self.sweetieDict[relationItem.playerDBID] = relationItem
		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_SWEETIE )
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_SWEETIE )
		self._updateRelationStatus( relationItem, myRelation, targetRelation, False )
		self.client.rtf_relationUpdate( relationUID, csdefine.ROLE_RELATION_SWEETIE )
		# 添加日志
		g_logger.sweeticBuildLog( self.databaseID, self.getName(), relationItem.playerDBID, relationItem.playerName )

	def removeSweetie( self, relationUID ):
		"""
		Exposed method.
		解除恋人关系的请求
		"""
		try:
			relationItem = self.relationDatas[relationUID]
		except KeyError:
			HACK_MSG( "player( %s )' relation( %i ) dont exist!" % ( self.getName(), relationUID ) )
			return
		if relationItem.meHasRelation( csdefine.ROLE_RELATION_COUPLE ):
			self.statusMessage( csstatus.FRIEND_CANT_REMOVE_COS_OTHER )
			return
		try:
			del self.sweetieDict[relationItem.playerDBID]
		except KeyError:
			ERROR_MSG( "sweetie( %s ) is not exist!" % relationItem.playerName )
			return
		self.statusMessage( csstatus.SWEETIE_REMOVE_SUCCESS, relationItem.playerName )
		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_SWEETIE )
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_SWEETIE )
		self._removeRelationStatus( relationItem, myRelation, targetRelation, False )
		self.client.endRelationUpdate( relationUID, csdefine.ROLE_RELATION_SWEETIE )
		if relationItem.playerBase:
			relationItem.playerBase.dstRemoveSweetie( relationUID )
		
		g_logger.sweeticRemoveLog( self.databaseID, self.getName(), relationItem.playerDBID )

	def dstRemoveSweetie( self, relationUID ):
		"""
		Define method.
		对方解除了恋人关系
		"""
		relationItem = self.relationDatas[relationUID]
		self.statusMessage( csstatus.SWEETIE_BE_REMOVE_SUCCESS, relationItem.playerName )
		del self.sweetieDict[relationItem.playerDBID]
		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_SWEETIE )
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_SWEETIE )
		self._removeRelationStatus( relationItem, myRelation, targetRelation, True )
		self.client.endRelationUpdate( relationUID, csdefine.ROLE_RELATION_SWEETIE )

	# ----------------------------------------------------------------------------
	# 夫妻
	# ----------------------------------------------------------------------------
	def requestMarriage( self, playerDBID ):
		"""
		Define method.
		请求结婚

		@param playerDBID : 结婚对象的dbid
		@type playerDBID : DATABASE_ID
		"""
		try:
			relationItem = self.sweetieDict[playerDBID]
		except KeyError:
			ERROR_MSG( "玩家( %s )不存在此恋人( dbid:%s )，不能结婚。" % ( self.getName(), playerDBID ) )
			self.statusMessage( csstatus.BE_SWEETIE_FIRST )
			return
		playerBase = relationItem.playerBase
		if relationItem.friendlyValue < csconst.ADD_COUPLE_NEED_FRIENDLY_VALUE:
			self.statusMessage( csstatus.COUPLE_FRIENDLY_LACK )
			playerBase.client.onStatusMessage( csstatus.COUPLE_FRIENDLY_LACK, "" )
			return
		self.cell.couple_canMarry( playerBase.id )
		playerBase.cell.couple_canMarry( self.id )
		relationUID = relationItem.relationUID
		self.client.askForMarriage( relationUID )
		playerBase.client.askForMarriage( relationUID )

	def couple_swear( self, playerDBID ):
		"""
		Define method.
		结婚成功,更新数据库表相关关系状态

		@param playerDBID:	玩家的dbid
		@type playerDBID:	DATABASE_ID
		"""
		relationItem = self.sweetieDict[playerDBID]
		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_COUPLE )
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_COUPLE )
		self._updateRelationStatus( relationItem, myRelation, targetRelation, True )
		self.couple_lover = relationItem
		temp = cschannel_msgs.BCT_JSGX_BECOME_COUPLE % ( self.getName(), self.couple_lover.playerName )
		Love3.g_baseApp.anonymityBroadcast( temp, [] )
		self.client.rtf_relationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_COUPLE )

	def couple_marrySuccess( self, playerDBID ):
		"""
		Define method.
		对方申请结婚，成功结婚，设置己方的base数据

		@param loverDBID: 对方的databaseID
		@type loverDBID: DATABASE_ID
		"""
		relationItem = self.sweetieDict[ playerDBID ]
		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_COUPLE )
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_COUPLE )
		self._updateRelationStatus( relationItem, myRelation, targetRelation, False )
		self.couple_lover = relationItem
		# 通知客户端
		self.client.rtf_relationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_COUPLE )

	def couple_forceDivorce( self ):
		"""
		Define method.
		单方面强制离婚

		到数据库中设置离婚状态
		"""
		relationItem = self.couple_lover
		temp = cschannel_msgs.BCT_JSGX_DIVROCE % ( self.getName(), relationItem.playerName )
		Love3.g_baseApp.anonymityBroadcast( temp, [] )
		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_COUPLE )
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_COUPLE )
		self._removeRelationStatus( relationItem, myRelation, targetRelation, False )
		if relationItem.playerBase:
			relationItem.playerBase.cell.couple_dstForceDivorce()
		self.client.endRelationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_COUPLE )
		self.couple_lover = None
		
		g_logger.conjugalRemoveLog( self.databaseID, self.getName(), relationItem.playerDBID )

	def couple_divorceSuccess( self ):
		"""
		Define method.
		和对方玩家离婚了
		"""
		myRelation = self.couple_lover.convertRelation( csdefine.ROLE_RELATION_COUPLE )
		targetRelation = self.couple_lover.convertTargetRelation( csdefine.ROLE_RELATION_COUPLE )
		self._removeRelationStatus( self.couple_lover, myRelation, targetRelation, True )
		self.client.endRelationUpdate( self.couple_lover.relationUID, csdefine.ROLE_RELATION_COUPLE )
		self.couple_lover = None

	def couple_findWeddingRing( self ):
		"""
		Define method.
		找回丢失的结婚戒指，由于玩家cell不存储伴侣名字，结婚戒指需要此信息，来base查询
		"""
		self.cell.couple_findWeddingRing( self.couple_lover.playerName )

	def rlt_queryAreaInfo( self, relation ):
		"""
		Exposed method.
		请求查询关系人所在地区

		@param relation : 定义于csdefine的玩家关系
		"""
		if relation == csdefine.ROLE_RELATION_BLACKLIST:
			relationDict = self.blacklist
		elif relation == csdefine.ROLE_RELATION_FRIEND:
			relationDict = self.friends
		elif relation == csdefine.ROLE_RELATION_SWEETIE:
			relationDict = self.sweetieDict
		elif relation == csdefine.ROLE_RELATION_COUPLE:
			relationDict = { "lover": self.couple_lover }	# 为了下面的统一处理，临时字典
		elif relation == csdefine.ROLE_RELATION_MASTER:
			relationDict = { "master": self.teach_masterItem }
		elif relation == csdefine.ROLE_RELATION_PRENTICE:
			relationDict = self.prenticeDict
		elif relation == csdefine.ROLE_RELATION_ALLY:
			relationDict = self.allyDict
		elif relation == csdefine.ROLE_RELATION_MASTER_EVER:
			relationDict = self.masterEverDict
		elif relation == csdefine.ROLE_RELATION_PRENTICE_EVER:
			relationDict = self.prenticeEverDict
		else:
			HACK_MSG( "player( %s ) relation error:%i" % ( self.getName(), relation ) )
			return
		for relationItem in relationDict.itervalues():
			if relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):
				continue
			if relationItem.playerBase:
				relationItem.playerBase.cell.rlt_sendAreaInfo( relationItem.relationUID, self )

	# -------------------------------------------------------------------------------
	# 添加仇人
	# -------------------------------------------------------------------------------
	def hasFoe( self, playerName ):
		"""
		是否存在仇人
		"""
		for item in self.foeDict.itervalues():
			if item.playerName == playerName:
				return True
		return False

	def addFoe( self, playerName ):
		"""
		Exposed method.
		添加仇人
		"""
		if self.getName() == playerName:
			self.statusMessage( csstatus.FOE_CANT_ADD_SELF )
			return

		if self.hasFoe( playerName ):
			self.statusMessage( csstatus.FOE_ALREADY_HAVE )
			return

		if len( self.foeDict ) > csconst.RELATION_FOE_NUM_LIMIT:
			self.statusMessage( csstatus.FOE_CANT_ADD_FULL )
			return

		relationItem = self.getRelationItemByName( playerName )
		if relationItem is None:
			Love3.g_baseApp.lookupRoleBaseByName( playerName, Functor( self._addFoeLookUpBaseCB, playerName ) )
			#BigWorld.lookUpBaseByName( "Role", playerName, Functor( self._addFoeLookUpCB, playerName ) )
		else:			
			playerBase = relationItem.playerBase
			hasVoluntary = relationItem.hasVoluntaryRelation()
			if hasVoluntary :	# 只有黑名单关系能和仇人关系并存，既能把一个玩家加为黑名单，也能加为仇人
				if not relationItem.meHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):
					relationStr = self.getPriorRelationStr( relationItem )
					self.statusMessage( csstatus.ROLE_ADD_FOE_FAISURE, relationStr )	
					return
				self.foeDict[relationItem.playerDBID] = relationItem
				myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_FOE )
				self._updateRelationStatus( relationItem, myRelation, 0, True )
				self.client.rtf_relationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_FOE )
			else:
				self.foeDict[relationItem.playerDBID] = relationItem
				myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_FOE )
				self._updateRelationStatus( relationItem, myRelation, 0, True )
				if playerBase and not relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):
					playerBase.cell.rlt_sendPlayerInfo( self, relationItem.relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
				else:
					self.client.rtf_receiveNameInfo( playerName, relationItem.relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
			if playerBase:
				relationItem.playerBase.updateRelation2Foe( relationItem.relationUID )

	def _addFoeLookUpBaseCB( self, playerName, result ):
		"""
		查询欲加为仇人的玩家是否在线
		"""
		if result is None:		# 玩家不在线
			self.statusMessage( csstatus.CANT_ADD_FOE_OFFLINE )
			return
		result.rlt_addFoeRequest( self )

	def rlt_addFoeRequest( self, targetBase ):
		"""
		Define method.
		对方玩家把自己加为仇人，把所需数据发给对方。
		"""
		targetBase.rlt_addFoeReply( self, self.databaseID, self.getName() )

	def rlt_addFoeReply( self, playerBase, playerDBID, playerName ):
		"""
		Define method.
		加对方为仇人数据请求的回复
		"""
		# 此时条件有可能已经不满足
		if self.hasFoe( playerName ):
			self.statusMessage( csstatus.FOE_ALREADY_HAVE )
			return
		if len( self.foeDict ) > csconst.RELATION_FOE_NUM_LIMIT:
			self.statusMessage( csstatus.FOE_CANT_ADD_FULL )
			return

		relationUID = Love3.g_baseApp.getRelationUID()
		if relationUID == -1:
			return
		# 低位表示主动发起关系着的关系状态
		relationStatus = csdefine.ROLE_RELATION_FOE
		relationItem = RelationItem( relationUID, playerName, relationStatus, 0, 0, playerBase, playerDBID )
		self._createRelation2DB( relationUID, playerDBID, relationStatus )
		self.relationDatas[relationUID] = relationItem
		self.foeDict[playerDBID] = relationItem
		playerBase.cell.rlt_sendPlayerInfo( self, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
		playerBase.beAddedFoeSuccess( relationUID, self.getName(), self.databaseID, self )

	def addKillerFoe( self, playerDBID, playerName, playerBase ):
		"""
		Define method.
		添加杀手为仇人

		@param playerDBID: 仇人的dbid
		@param playerName: 仇人的名字
		@param playerBase: 仇人的base mailbox
		"""
		if self.hasFoe( playerName ):
			return
		if self.getName() == playerName:
			return
		relationItem = self.getRelationItemByName( playerName )
		hasVoluntary = False
		if relationItem is None:
			relationUID = Love3.g_baseApp.getRelationUID()
			if relationUID == -1:
				return
			relationStatus = csdefine.ROLE_RELATION_FOE
			# 约定：发起加仇人者作为sm_playerName1写入db
			relationItem = RelationItem( relationUID, playerName, relationStatus, 0, 0, playerBase, playerDBID )
			self.relationDatas[relationUID] = relationItem
			self.foeDict[playerDBID] = relationItem
			self._createRelation2DB( relationUID, playerDBID, relationStatus )
			playerBase.beAddedFoeSuccess( relationUID, self.getName(), self.databaseID, self )
		else:
			hasVoluntary = relationItem.hasVoluntaryRelation()
			relationUID = relationItem.relationUID		
		if hasVoluntary:	# 如果已经存在关系
			if not relationItem.meHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):
				relationStr = self.getPriorRelationStr( relationItem )
				self.statusMessage( csstatus.ROLE_ADD_FOE_FAISURE, relationStr )	
				return
			self.foeDict[relationItem.playerDBID] = relationItem
			myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_FOE )
			self._updateRelationStatus( relationItem, myRelation, 0, True )
			self.client.rtf_relationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_FOE )
		else:
			self.foeDict[relationItem.playerDBID] = relationItem
			myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_FOE )
			self._updateRelationStatus( relationItem, myRelation, 0, True )
			if relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):
				self.client.rtf_receiveNameInfo( playerName, relationItem.relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
			else:
				playerBase.cell.rlt_sendPlayerInfo( self, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )

	def beAddedFoeSuccess( self, relationUID,  playerName, playerDBID, playerBase ):
		"""
		Define method.
		被添加仇人成功，初次产生关系
		"""
		relationStatus = csdefine.ROLE_RELATION_FOE
		relationItem = RelationItem( relationUID, playerName, relationStatus, RELATION_STATUS_HIGH_OFFSET, 0, playerBase, playerDBID )
		self.relationDatas[relationUID] = relationItem
		self.beFoeDict[playerDBID] = relationItem

	def updateRelation2Foe( self, relationUID ):
		"""
		Define method.
		被加仇人，关系更新
		"""
		relationItem = self.relationDatas[relationUID]
		self.beFoeDict[relationItem.playerDBID] = relationItem
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_FOE )
		self._updateRelationStatus( relationItem, 0, targetRelation, False )

	def removeFoe( self, relationUID ):
		"""
		Exposed method.
		移除仇人
		"""
		try:
			relationItem = self.relationDatas[relationUID]
		except KeyError:
			HACK_MSG( "player(%s):relation( %i ) dose not exist!!" % ( self.getName(), relationUID ) )
			return
		if not relationItem.meHasRelation( csdefine.ROLE_RELATION_FOE ):
			HACK_MSG( "player(%s):FOE relation( %i ) dose not exist!!!" % ( self.getName(), relationUID ) )
			return
		del self.foeDict[relationItem.playerDBID]

		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_FOE )
		self._removeRelationStatus( relationItem, myRelation, 0, True )
		self.client.endRelationUpdate( relationUID, csdefine.ROLE_RELATION_FOE )
		if relationItem.playerBase:
			relationItem.playerBase.dstRemoveFoe( relationUID )

	def dstRemoveFoe( self, relationUID ):
		"""
		Define method.
		对方删除了仇人
		"""
		try:
			relationItem = self.relationDatas[relationUID]
		except KeyError:
			HACK_MSG( "player(%s):relation( %i ) dose not exist!!" % ( self.getName(), relationUID ) )
			return
		relationItem.relationStatus &= ~relationItem.convertTargetRelation( csdefine.ROLE_RELATION_FOE )
		del self.beFoeDict[relationItem.playerDBID]
		if relationItem.relationStatus == 0:
			del self.relationDatas[relationUID]

	def getRelationItemByName( self, playerName ):
		"""
		根据玩家名字获得relationItem，不存在则返回None
		"""
		for relationItem in self.relationDatas.itervalues():
			if relationItem.playerName == playerName:
				return relationItem
		return None

	def rlt_checkAddFriendyValue( self, playerDBID ):
		"""
		Define method.
		是否能够与playerDBID的玩家增加友好度
		"""
		self.cell.rlt_checkAddFriendyResult( ( playerDBID in self.friends ) )

	def addItemFriendlyValue( self, playerDBID, value ):
		"""
		Define method.
		增加与好友的友好度
		"""
		self.friends[playerDBID].addFriendlyValue( value, self )

	# ------------------------------------------------------------------------
	# 师徒关系
	# ------------------------------------------------------------------------
	def setTeachExtraInfo( self ):
		"""
		Define method
		将自己的出师徒弟数量和上周在线时间传给管理器
		"""
		daysSec = 24 * 3600
		wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec) - 1
		lastWeekOnlineTime = self.weekOnlineTime.get( wT, 0.0 )		# 获取上周在线时间
		self._getTeachMgr().getTeachExtraInfo( self.databaseID, len(self.prenticeEverDict), lastWeekOnlineTime )
		
	def teach_registerTeacher( self ):
		"""
		Define method
		注册收徒
		"""
		# 将自己的出师徒弟数量和上周在线时间传给cell
		daysSec = 24 * 3600
		wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec) - 1
		lastWeekOnlineTime = self.weekOnlineTime.get( wT, 0.0 )		# 获取上周在线时间
		self.cell.teach_registerTeacher( len(self.prenticeEverDict), lastWeekOnlineTime )
	
	def teach_registerPrentice( self ):
		"""
		Define method
		注册拜师
		"""
		# 将自己的上周在线时间传给cell
		daysSec = 24 * 3600
		wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec) - 1
		lastWeekOnlineTime = self.weekOnlineTime.get( wT, 0.0 )		# 获取上周在线时间
		self.cell.teach_registerPrentice( lastWeekOnlineTime )
	
	def masterDisbandTeach( self ):
		"""
		Define method.
		师父解除了关系
		"""
		relationItem = self.teach_masterItem
		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_PRENTICE )
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_MASTER )
		self._removeRelationStatus( relationItem, myRelation, targetRelation, True )
		self.statusMessage( csstatus.TEACH_RELATION_DISBAND, relationItem.playerName )
		self.client.endRelationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_PRENTICE )
		self.teach_masterItem = None

	def prenticeDisbandTeach( self, playerDBID ):
		"""
		Define method.
		徒弟解除了关系
		"""
		relationItem = self.prenticeDict.pop( playerDBID )
		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_MASTER )
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_PRENTICE )
		self._removeRelationStatus( relationItem, myRelation, targetRelation, True )
		self.statusMessage( csstatus.TEACH_RELATION_DISBAND, relationItem.playerName )
		self.client.endRelationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_MASTER )

	def teach_beginTeach( self, prenticeDBID, prenticeName, playerBase ):
		"""
		Define method.
		师父申请结为师徒成功，写db

		param prenticeName:	徒弟的名字
		type prenticeName:	STRING
		"""
		relationItem = self.getRelationItemByName( prenticeName )
		if relationItem is None:
			relationUID = Love3.g_baseApp.getRelationUID()
			if relationUID == -1:		# 此处失败则需1秒后再次申请，目前还未实现此机制
				ERROR_MSG( "player( %s ), prentice( %s )--->>>relationUID == -1" % ( self.getName(), prenticeName ) )
				return
			relationStatus = csdefine.ROLE_RELATION_MASTER | ( csdefine.ROLE_RELATION_PRENTICE << RELATION_STATUS_HIGH_OFFSET )
			# 师父作为sm_playerName1写入db
			relationItem = RelationItem( relationUID, prenticeName, relationStatus, 0, 0, playerBase, prenticeDBID )
			self.relationDatas[relationUID] = relationItem
			self._createRelation2DB( relationUID, prenticeDBID, relationStatus )
		else:
			relationUID = relationItem.relationUID
			myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_MASTER )
			targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_PRENTICE )
			self._updateRelationStatus( relationItem, myRelation, targetRelation, True )
		playerBase.beTeachedSuccess( relationUID, self.databaseID, self.getName(), self )
		self.prenticeDict[prenticeDBID] = relationItem
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JSGX_NEW_TEACH % ( self.getName(), prenticeName ), [] )
		if not relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):
			playerBase.cell.rlt_sendPlayerInfo( self, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
		else:
			self.client.rtf_receiveNameInfo( relationItem.playerName, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )

	def beTeachedSuccess( self, relationUID, masterDBID, masterName, playerBase ):
		"""
		Define method.
		拜师成功，创建关系
		"""
		relationItem = self.getRelationItemByName( masterName )
		if relationItem:
			myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_PRENTICE )
			targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_MASTER )
			self._updateRelationStatus( relationItem, myRelation, targetRelation, False )
			try:
				g_logger.teachBuildLog( masterDBID, masterName, self.databaseID, self.getName() )
			except:
				EXCEHOOK_MSG()
		else:
			relationStatus = csdefine.ROLE_RELATION_MASTER | ( csdefine.ROLE_RELATION_PRENTICE << RELATION_STATUS_HIGH_OFFSET )
			relationItem = RelationItem( relationUID, masterName, relationStatus, RELATION_STATUS_HIGH_OFFSET, 0, playerBase, masterDBID )
			self.relationDatas[relationItem.relationUID] = relationItem
		self.teach_masterItem = relationItem
		if not relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):
			playerBase.cell.rlt_sendPlayerInfo( self, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
		else:
			self.client.rtf_receiveNameInfo( relationItem.playerName, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )

	def teach_disband( self, playerDBID ):
		"""
		Define method.
		玩家解除师徒关系的接口

		Param playerDBID:	对方玩家的dbid
		Type playerDBID:	DATABASE_ID
		"""
		if self.teach_masterItem:	# 如果玩家是徒弟
			relationItem = self.teach_masterItem
			relationUID = relationItem.relationUID
			myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_PRENTICE )
			targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_MASTER )
			self._removeRelationStatus( relationItem, myRelation, targetRelation, False )
			masterBase = relationItem.playerBase
			if masterBase and hasattr( masterBase, "cell" ):
				masterBase.cell.targetDisbandTeach( self.databaseID, csdefine.ROLE_RELATION_PRENTICE )
			self.client.endRelationUpdate( relationUID, csdefine.ROLE_RELATION_PRENTICE )
			self.teach_masterItem = None
		else:
			relationItem = self.prenticeDict.pop( playerDBID )
			relationUID = relationItem.relationUID
			myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_MASTER )
			targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_PRENTICE )
			self._removeRelationStatus( relationItem, myRelation, targetRelation, False )
			prenticeBase = relationItem.playerBase
			if prenticeBase and hasattr( prenticeBase, "cell" ):
				prenticeBase.cell.targetDisbandTeach( self.databaseID, csdefine.ROLE_RELATION_MASTER )
			self.client.endRelationUpdate( relationUID, csdefine.ROLE_RELATION_MASTER )

	def masterEndTeach( self, prenticeDBID ):
		"""
		Define method.
		师父出师
		"""
		relationItem = self.prenticeDict.pop( prenticeDBID, [] )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JSGX_AUTO_DISBAND % ( relationItem.playerName, self.getName() ), [] )
		self.prenticeEverDict[prenticeDBID] = relationItem		# 曾经的徒弟
		relationItem.relationStatus &= ~( relationItem.convertTargetRelation( csdefine.ROLE_RELATION_PRENTICE ) | relationItem.convertRelation( csdefine.ROLE_RELATION_MASTER ) )
		relationItem.relationStatus |= relationItem.convertTargetRelation( csdefine.ROLE_RELATION_PRENTICE_EVER ) | relationItem.convertRelation( csdefine.ROLE_RELATION_MASTER_EVER )
		self.client.rtf_relationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_PRENTICE_EVER )
		query = "update custom_Relation set sm_relationStatus = %i where sm_uid = %i" % ( relationItem.relationStatus, relationItem.relationUID )
		BigWorld.executeRawDatabaseCommand( query, self._updateTeachRelationCB )		#if relationItem.relationStatus == 0:
		
		g_logger.teachCompleteLog( self.databaseID, self.getName(), prenticeDBID )

	def _updateTeachRelationCB( self, result, rows, errstr ):
		"""
		玩家出师，师徒关系db更新的回调
		"""
		if errstr:
			ERROR_MSG( errstr )

	def endTeachSuccess( self, playerDBID ):
		"""
		Define method.
		出师成功，设置自身数据
		"""
		if self.teach_masterItem:	# 如果是徒弟
			relationItem = self.teach_masterItem
			relationItem.relationStatus &= ~( relationItem.convertTargetRelation( csdefine.ROLE_RELATION_MASTER ) | relationItem.convertRelation( csdefine.ROLE_RELATION_PRENTICE ) )
			relationItem.relationStatus |= relationItem.convertTargetRelation( csdefine.ROLE_RELATION_MASTER_EVER ) | relationItem.convertRelation( csdefine.ROLE_RELATION_PRENTICE_EVER )
			self.masterEverDict[relationItem.playerDBID] = relationItem
			self.client.rtf_relationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_MASTER_EVER )
			self.teach_masterItem = None
		else:
			relationItem = self.prenticeDict.pop( playerDBID )
			self.prenticeEverDict[playerDBID] = relationItem
			relationItem.relationStatus &= ~( relationItem.convertTargetRelation( csdefine.ROLE_RELATION_PRENTICE ) | relationItem.convertRelation( csdefine.ROLE_RELATION_MASTER ) )
			relationItem.relationStatus |= relationItem.convertTargetRelation( csdefine.ROLE_RELATION_PRENTICE_EVER ) | relationItem.convertRelation( csdefine.ROLE_RELATION_MASTER_EVER )
			self.client.rtf_relationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_PRENTICE_EVER )

	def teach_requestDisband( self, playerName ):
		"""
		Exposed method.
		玩家请求解除与目标玩家的师徒关系
		"""
		if self.teach_masterItem:	# 如果是徒弟
			self.cell.teach_disband( self.teach_masterItem.playerDBID, playerName )
			try:
				g_logger.teachRemoveLog( self.teach_masterItem.playerDBID, playerName, self.databaseID, self.getName() )
			except:
				EXCEHOOK_MSG()
			
			return
		
		# 查找是否是师傅
		for item in self.prenticeDict.itervalues():
			if item.playerName == playerName:
				self.cell.teach_disband( item.playerDBID, playerName )
				try:
					g_logger.teachRemoveLog( self.databaseID, self.getName(), item.playerDBID, playerName )
				except:
					EXCEHOOK_MSG()
				return

	def teach_masterRemoteTeachReply( self, agree ):
		"""
		Exposed method.
		师父回复远程拜师邀请

		@param agree : 是否同意
		@type agree : BOOL
		"""
		if len( self.prenticeDict ) >= csconst.TEACH_PRENTICE_MAX_COUNT:
			self.statusMessage( csstatus.TEACH_PRENTICE_NUM_FULL )
			self.requestBeTeachedResult( csstatus.TEACH_REQUEST_PRENTICE_NUM_LIMIT )
			return

		if agree:
			if self._inviteTeachBase is None:
				return
			if self._inviteTeachTime + TEACH_REQUEST_TIME_OUT < time.time():
				return
			self._inviteTeachBase.cell.teach_beginRemoteTeach( self, self.databaseID, self.getName(),1 )
		else:
			self.requestBeTeachedResult( csstatus.TEACH_REQUEST_MASTER_REFUSE )

	def teach_prenticeRemoteTeachReply( self, agree ):
		"""
		Exposed method.
		徒弟回复远程拜师邀请

		@param agree : 是否同意
		@type agree : BOOL
		"""
		if self.teach_masterItem is not None:
			self.statusMessage( csstatus.TEACH_MASTER_EXIST )
			self.requestBeTeachedResult( csstatus.TEACH_PRENTICE_HAS_MONSTER )
			return

		if agree:
			if self._inviteTeachBase is None:
				return
			if self._inviteTeachTime + TEACH_REQUEST_TIME_OUT < time.time():
				return
			self._inviteTeachBase.teach_prenticeReplyTrue( self )
		else:
			self.requestBeTeachedResult( csstatus.REMOTE_FIND_PRENTICE_REFUSE )

	def teach_prenticeReplyTrue( self, playerBase ):
		"""
		Define method.
		徒弟同意结为师徒，检查是否还满足收徒条件

		@param playerBase : 徒弟的base mailbox
		"""
		if len( self.prenticeDict ) >= csconst.TEACH_PRENTICE_MAX_COUNT:
			self.statusMessage( csstatus.TEACH_PRENTICE_NUM_FULL )
			self.requestBeTeachedResult( csstatus.TEACH_REQUEST_PRENTICE_NUM_LIMIT )
			return
		self._inviteTeachBase = playerBase
		self._inviteTeachTime = time.time()
		playerBase.cell.teach_beginRemoteTeach( self, self.databaseID, self.getName(),0 )

	def requestBeTeachedResult( self, statusID ):
		"""
		Define method.
		请求远程结为师徒的结果返回

		@param statusID : 状态消息id，定义于csstatus.py模块
		@type statusID : UINT16
		"""
		param = ""
		if statusID == csstatus.TEACH_REQUEST_MASTER_REFUSE or statusID == csstatus.REMOTE_FIND_PRENTICE_REFUSE or statusID == csstatus.TEACH_PRENTICE_HAS_MONSTER or status == csstatus.TEACH_REQUEST_PRENTICE_NUM_LIMIT:
			param = "(\'%s\',)" % self.getName()
		self._inviteTeachBase.client.onStatusMessage( statusID, param )
		self._inviteTeachBase = None		# 请求拜师的徒弟base mailbox
		self._inviteTeachTime = 0			# 发起远程拜师的时刻

	def prenticeRequestBeTeached( self, prenticeName, prenticeBaseMB ):
		"""
		Define method.
		玩家请求拜师

		@param prenticeName : 请求拜师玩家的名字
		@type prenticeName : STRING
		@param prenticeBaseMB : 请求拜师玩家的base mailbox
		@type prenticeBaseMB : MAILBOX
		"""
		if self._inviteTeachBase and self._inviteTeachTime + TEACH_REQUEST_TIME_OUT > time.time():
			return
		if self.hasFoe( prenticeName ):
			self.statusMessage( csstatus.FOE_HAS_EXIST )
			return

		self._inviteTeachBase = prenticeBaseMB	# 请求拜师的徒弟base mailbox
		self._inviteTeachTime = time.time()		# 发起远程拜师的时刻

		self.client.prenticeRequestBeTeached( prenticeName )

	def teach_requestBeTeached( self, masterDBID ):
		"""
		Exposed method.
		徒弟发起远程拜师请求。

		@param masterDBID : 拜师目标玩家的dbid
		@type masterDBID : DATABASE_ID
		"""
		if self.teach_masterItem is not None:
			self.statusMessage( csstatus.TEACH_MASTER_EXIST )
			return
		if self.level < csconst.TEACH_PRENTICE_LOWER_LIMIT or self.level > csconst.TEACH_PRENTICE_UPPER_LIMIT:
			return

		self._getTeachMgr().requestBeTeached( self, self.getName(), masterDBID )

	def requestTeachPrentice( self, prenticeDBID ):
		"""
		Exposed method.
		师父发起收徒请求
		"""
		if len( self.prenticeDict ) >= csconst.TEACH_PRENTICE_MAX_COUNT:
			self.statusMessage( csstatus.TEACH_PRENTICE_NUM_FULL )
			return
		self._getTeachMgr().requestTeach( self, self.getName(), prenticeDBID )

	def masterRequestTeach( self, playerName, playerBase ):
		"""
		Define method.
		对方请求收徒

		@param playerName : 对方玩家的名字
		@param playerBase : 对方玩家的base mailbox
		"""
		if self.hasFoe( playerName ):
			self.statusMessage( csstatus.FOE_HAS_EXIST )
			return
		self._inviteTeachBase = playerBase		# 请求收徒的师父base mailbox
		self._inviteTeachTime = time.time()			# 发起远程收徒的时刻
		self.client.masterRequestTeach( playerName )

	def teach_beginRemoteTeach( self, masterDBID, masterName, playerBase ):
		"""
		Define method.
		师父同意远程拜师，徒弟调用此接口

		param masterName:	师父的名字
		type masterName:	STRING
		"""
		relationItem = self.getRelationItemByName( masterName )
		if relationItem is None:
			relationUID = Love3.g_baseApp.getRelationUID()
			if relationUID == -1:		# 此处失败则需0.1秒后再次申请，目前还未实现此机制
				ERROR_MSG( "player( %s ), prentice( %s )--->>>relationUID == -1" % ( self.getName(), masterName ) )
				return
			# 徒弟作为playerName1写入db
			relationStatus = csdefine.ROLE_RELATION_PRENTICE | ( csdefine.ROLE_RELATION_MASTER << RELATION_STATUS_HIGH_OFFSET )
			relationItem = RelationItem( relationUID, masterName, relationStatus, 0, 0, playerBase, masterDBID )
			self.relationDatas[relationUID] = relationItem
			self._createRelation2DB( relationUID, masterDBID, relationStatus )
		else:
			relationUID = relationItem.relationUID
			myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_PRENTICE )
			targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_MASTER )
			self._updateRelationStatus( relationItem, myRelation, targetRelation, True )
		playerBase.remoteTeachSuccess( relationUID, self.databaseID, self.getName(), self )
		self.teach_masterItem = relationItem
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JSGX_NEW_TEACH % ( masterName, self.getName() ), [] )
		if not relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):
			playerBase.cell.rlt_sendPlayerInfo( self, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
		else:
			self.client.rtf_receiveNameInfo( relationItem.playerName, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
		
		g_logger.teachBuildLog( masterDBID, masterName, self.databaseID, self.getName() )

	def remoteTeachSuccess( self, relationUID, playerDBID, playerName, playerBase ):
		"""
		Define method.
		远程拜师成功，设置师父的关系数据
		"""
		self._inviteTeachBase = None
		self._inviteTeachTime = 0
		relationItem = self.getRelationItemByName( playerName )
		if relationItem:
			myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_MASTER )
			targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_PRENTICE )
			self._updateRelationStatus( relationItem, myRelation, targetRelation, False )
		else:
			relationStatus = csdefine.ROLE_RELATION_PRENTICE | ( csdefine.ROLE_RELATION_MASTER << RELATION_STATUS_HIGH_OFFSET )
			relationItem = RelationItem( relationUID, playerName, relationStatus, RELATION_STATUS_HIGH_OFFSET, 0, playerBase, playerDBID )
			self.relationDatas[relationItem.relationUID] = relationItem
		self.prenticeDict[playerDBID] = relationItem
		if not relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):
			playerBase.cell.rlt_sendPlayerInfo( self, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
		else:
			self.client.rtf_receiveNameInfo( relationItem.playerName, relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )

	def autoTeach_disband( self, masterDBID ):
		"""
		Define method.
		徒弟升级，触发自动出师
		"""
		relationItem = self.teach_masterItem
		self.teach_masterItem = None
		masterName = relationItem.playerName
		self.statusMessage( csstatus.TEACH_RELATION_DISBAND, masterName )	# 通知玩家
		self.statusMessage( csstatus.TEACH_AUTO_DISBAND, masterName )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JSGX_AUTO_DISBAND % ( self.getName(), masterName ), [] )

		relationItem.relationStatus &= ~( relationItem.convertTargetRelation( csdefine.ROLE_RELATION_MASTER ) | relationItem.convertRelation( csdefine.ROLE_RELATION_PRENTICE ) )
		relationItem.relationStatus |= relationItem.convertTargetRelation( csdefine.ROLE_RELATION_MASTER_EVER ) | relationItem.convertRelation( csdefine.ROLE_RELATION_PRENTICE_EVER )
		query = "update custom_Relation set sm_relationStatus = %i where sm_uid = %i" % ( relationItem.relationStatus, relationItem.relationUID )
		BigWorld.executeRawDatabaseCommand( query, self._updateTeachRelationCB )		#if relationItem.relationStatus == 0:
		self.masterEverDict[relationItem.playerDBID] = relationItem
		self.client.rtf_relationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_MASTER_EVER )
		masterBase = relationItem.playerBase
		if masterBase:
			masterBase.endTeachSuccess( self.databaseID )
			masterBase.cell.autoDisbandSuccess( self.databaseID )
		# 给师傅玩家发邮件
		mailType = csdefine.MAIL_TYPE_QUICK
		title = cschannel_msgs.ROLERELATION_INFO_3
		content = cschannel_msgs.ROLERELATION_INFO_4%self.getName()
		BigWorld.globalData["MailMgr"].send( None, masterName, mailType, csdefine.MAIL_SENDER_TYPE_NPC, self.getName(), title, content, 0, [] )
		
		g_logger.teachCompleteLog( self.databaseID, self.getName(), masterDBID )

	def onTongChangeNotifyRelation( self, tongName ):
		"""
		Define method.
		帮会改变通知
		"""
		for relationUID, relationItem in self.relationDatas.iteritems():
			if relationItem.hasVoluntaryRelation():
				playerBase = relationItem.playerBase
				if playerBase is None: continue
				playerBase.client.onRealtionTongChanged( relationUID, tongName )

	def queryTongGrade( self, relationUID ) :
		"""
		Exposed method
		获取帮会职务
		"""
		for relationUID_, relationItem in self.relationDatas.iteritems():
			if relationUID_ != relationUID : continue
			if relationItem.hasVoluntaryRelation():
				playerBase = relationItem.playerBase
				if playerBase is None:return
			 	playerBase.cell.onSendTongGrade( relationUID_, self )

	# ---------------------------------------------------------------------------------
	# 玩家结拜
	# ---------------------------------------------------------------------------------
	def rlt_requestAlly( self, captainBase, playerDBIDList ):
		"""
		Define method.
		玩家请求结拜，检查自己和参与结拜的玩家关系是否符合结拜条件

		@param captainBase: 接收检查结果的entity baseMailbox
		@param playerDBIDList: 参与结拜的玩家dbid列表
		"""
		statusID = csstatus.CAN_ALLY	# 可以结拜
		for dbid in playerDBIDList:
			try:
				relationItem = self.friends[dbid]
			except KeyError:
				statusID = csstatus.CANNOT_ALLY_LACK_FRIENDLY_VALUE	# 不是好友关系
				break
			if relationItem.friendlyValue < csconst.RELATION_ALLY_NEED_FRIENDLY_VALUE:
				statusID = csstatus.CANNOT_ALLY_LACK_FRIENDLY_VALUE	# 友好度不够
				break
			if self.sweetieDict.has_key( dbid ):
				statusID = csstatus.CANNOT_ALLY_HAD_SWEETIE	# 已经相爱，不能再结拜了！
				break
		captainBase.cell.rlt_allyCheckResult( self.databaseID, statusID, () )

	def rlt_allySuccess( self, DBIDList ):
		"""
		Define method.
		结拜成功，设置base数据
		"""
		for dbid in DBIDList:
			relationItem = self.friends[dbid]
			relationItem.relationStatus |= relationItem.convertRelation( csdefine.ROLE_RELATION_ALLY )
			relationItem.relationStatus |= relationItem.convertTargetRelation( csdefine.ROLE_RELATION_ALLY )
			self.allyDict[dbid] = relationItem
			self.cell.receiveAllyInfo( {"playerDBID":dbid,"playerBase":relationItem.playerBase} )
			self.client.rtf_relationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_ALLY )

	def rlt_startAlly( self, DBIDList ):
		"""
		Define method.
		结拜成功，开始
		"""
		self.rlt_allySuccess( DBIDList )
		DBIDList.append( self.databaseID )
		nameList = [relationItem.playerName for relationItem in self.friends.itervalues() if relationItem.playerDBID in DBIDList]
		nameList.append( self.getName() )
		strParam = str( tuple( [int( dbid ) for dbid in DBIDList] ) )	# 去掉长整型的"L"描述符
		relationStatus = csdefine.ROLE_RELATION_ALLY | csdefine.ROLE_RELATION_ALLY << RELATION_STATUS_HIGH_OFFSET
		commandString = """update `custom_Relation` set sm_relationStatus = sm_relationStatus | %i,
							sm_param = '%s' where sm_playerDBID1 in %s and
							sm_playerDBID2 in %s;
						""" % ( relationStatus, csconst.TITLE_ALLY_DEFAULT_NAME, strParam, strParam )
		BigWorld.executeRawDatabaseCommand( commandString, self._allyWriteDBCB )
		self.allyTitle = csconst.TITLE_ALLY_DEFAULT_NAME
#		self.statusMessage( csstatus.TITLE_ADDED, self.allyTitle )
		self.client.receiveAllyTitle( self.allyTitle, csdefine.ALLY_TITILE_CHANGE_REASON_ADD )
		for item in self.allyDict.itervalues():
			item.playerBase.receiveAllyTitle( self.allyTitle, csdefine.ALLY_TITILE_CHANGE_REASON_ADD )	# 结拜成功，结拜兄弟肯定在线
		self._allyBroadcast( nameList )
		
		g_logger.allyListChangeLog( str(nameList) , str(DBIDList) )

	def rlt_joinNewAllyMember( self, newDBIDList ):
		"""
		Define method.
		添加新的结拜兄弟

		@param newDBIDList: 新的结拜兄弟dbid列表
		"""
		oldDBIDList = self.allyDict.keys()
		oldDBIDList.append( self.databaseID )
		oldNameList = [item.playerName for item in self.allyDict.itervalues()]
		oldNameList.append( self.getName() )
		newNameList = [relationItem.playerName for relationItem in self.friends.itervalues() if relationItem.playerDBID in newDBIDList]
		self.rlt_allySuccess( newDBIDList )
		oldAllyDBIDParam = str( tuple( [int( dbid ) for dbid in oldDBIDList] ) )	# 去掉长整型的"L"描述符
		if len( newDBIDList ) == 1:	# 对于只有一个元素的列表，格式转换后会得到类似"('playerName',)"的格式，造成db语句出错。
			strDBIDParam = ("(" + "%i" + ")") % newDBIDList[0]
		else:
			strDBIDParam = str( tuple( [int( dbid ) for dbid in newDBIDList] ) )	# 去掉长整型的"L"描述符
		relationStatus = csdefine.ROLE_RELATION_ALLY | csdefine.ROLE_RELATION_ALLY << RELATION_STATUS_HIGH_OFFSET
		commandString = """update `custom_Relation` set sm_relationStatus = sm_relationStatus | %i, sm_param = '%s'
							where (sm_playerDBID1 in %s and sm_playerDBID2 in %s)
							or (sm_playerDBID1 in %s and sm_playerDBID2 in %s);
						""" % ( relationStatus, self.allyTitle, oldAllyDBIDParam, strDBIDParam, strDBIDParam, oldAllyDBIDParam )
		BigWorld.executeRawDatabaseCommand( commandString, self._allyWriteDBCB )
		for item in self.allyDict.itervalues():
			item.playerBase.receiveAllyTitle( self.allyTitle, csdefine.ALLY_TITILE_CHANGE_REASON_ADD_MEMBER )	# 结拜成功，结拜兄弟肯定在线
		self._allyBroadcast( oldNameList + newNameList )
		
		g_logger.allyListChangeLog( str(newNameList) , str(newDBIDList) )

	def _allyBroadcast( self, nameList ):
		"""
		玩家结拜的全服通知

		[XX]、[YY]在凤鸣烧黄纸，结义金兰，从此同闯天下。
		"""
		sParam = "[" + cschannel_msgs.ROLE_INFO_9.join( nameList ) + "]"	# 生成通知消息格式
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JSGX_NEW_ALLY % sParam, [] )

	def _allyWriteDBCB( self, result, rows, errstr ):
		"""
		玩家结拜写db的回调
		"""
		if errstr:
			ERROR_MSG( "player( %s ) write to DB error:%s." % ( self.getName(), errstr ) )

	def rlt_changeAllyTitle( self, titleName ):
		"""
		Define method.
		玩家更改结拜称号
		"""
		DBIDList = [self.databaseID]
		for playerDBID, relationItem in self.allyDict.iteritems():
			DBIDList.append( playerDBID )
			playerBase = relationItem.playerBase
			if playerBase:
				playerBase.receiveAllyTitle( titleName, csdefine.ALLY_TITILE_CHANGE_REASON_MEMBER_CHANGE )
		strDBIDParam = str( tuple( [int(dbid) for dbid in DBIDList] ) )
		sqlCommand = """update `custom_Relation` set sm_param = '%s'
						where (sm_playerDBID1 in %s and sm_playerDBID2 in %s);
					""" % ( titleName, strDBIDParam, strDBIDParam )
		BigWorld.executeRawDatabaseCommand( sqlCommand, self._allyWriteDBCB )
		self.client.receiveAllyTitle( titleName, csdefine.ALLY_TITILE_CHANGE_REASON_MEMBER_CHANGE )
		self.allyTitle = titleName
		self.cell.onAllyTitleChanged( titleName )
		self.statusMessage( csstatus.ALLY_CHANGE_TITLE_SUCCESS )

	def receiveAllyTitle( self, titleName, reason ):
		"""
		Define method.
		接收结拜称号
		"""
		self.allyTitle = titleName
		self.cell.onAllyTitleChanged( titleName )
		self.client.receiveAllyTitle( titleName, reason )
#		self.statusMessage( csstatus.TITLE_ADDED, titleName )

	def rlt_quitAlly( self ):
		"""
		Define method.
		玩家退出结拜

		"""
		for playerName, relationItem in self.allyDict.iteritems():
			playerBase = relationItem.playerBase
			if playerBase:
				playerBase.rlt_memberQuitAlly( relationItem.relationUID )
			myRelationStatus = relationItem.convertRelation( csdefine.ROLE_RELATION_ALLY )
			targetRelationStatus = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_ALLY )
			self._removeRelationStatus( relationItem, myRelationStatus, targetRelationStatus, False )
			self.client.endRelationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_ALLY )
			self.statusMessage( csstatus.ALLY_QUIT_SUCCESS, relationItem.playerName )
		DBIDList = self.allyDict.keys()
		nameList = [relationItem.playerName for relationItem in self.friends.itervalues() if relationItem.playerDBID in DBIDList]
		self.allyTitle = ""
		self.allyDict.clear()
		
		g_logger.allyListChangeLog( str(nameList) , str(DBIDList) )

	def rlt_memberQuitAlly( self, relationUID ):
		"""
		Define method.
		有人退出结拜，更新自己的结拜关系数据
		"""
		if len( self.allyDict ) <= 1:	# 如果是解散结拜，要从cellapp开始处理
			self.cell.rlt_disbandAlly()
		else:
			relationItem = self.relationDatas[relationUID]
			playerDBID = relationItem.playerDBID
			del self.allyDict[playerDBID]
			self.cell.rlt_memberQuitAlly( playerDBID )
			myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_ALLY )
			targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_ALLY )
			self._removeRelationStatus( relationItem, myRelation, targetRelation, True )
			self.client.endRelationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_ALLY )
			self.statusMessage( csstatus.ALLY_MEMBER_QUIT, relationItem.playerName )

	def rlt_disbandAlly( self ):
		"""
		Define method.
		解除结拜关系。
		"""
		for relationItem in self.allyDict.itervalues():
			myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_ALLY )
			targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_ALLY )
			self._removeRelationStatus( relationItem, myRelation, targetRelation, True )
			self.client.endRelationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_ALLY )
			self.statusMessage( csstatus.ALLY_MEMBER_QUIT, relationItem.playerName )
		DBIDList = self.allyDict.keys()
		nameList = [relationItem.playerName for relationItem in self.friends.itervalues() if relationItem.playerDBID in DBIDList]
		self.allyTitle = ""
		self.allyDict.clear()
		g_logger.allyListChangeLog( str(nameList) , str(DBIDList) )

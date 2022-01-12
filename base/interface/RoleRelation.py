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

TEACH_REQUEST_TIME_OUT = 30		# Զ�̰�ʦ����ʱЧ
SWEETIE_INVITE_TIME_OUT = 30		# ��������ʱЧ

FRIENDLY_VALUE_INITIAL = 0			# �Ѻöȳ�ʼֵ

INVITE_PERIOD_OF_VALIDITY = 20		# ������Ч��
RELATION_STATUS_HIGH_OFFSET = 16	# ��ϵ״̬��λƫ����
RELATION_STATUS_LOW_OFFSET = 0	# ��ϵ״̬��λƫ����
MASTER_PRENTICE = csdefine.ROLE_RELATION_MASTER|csdefine.ROLE_RELATION_PRENTICE|csdefine.ROLE_RELATION_PRENTICE_EVER|csdefine.ROLE_RELATION_MASTER_EVER

class RelationItem:
	"""
	��ҹ�ϵ����
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
		@param playerDBID : �Է����dbid
		@param relationStatus : ����ҵĹ�ϵ��ǣ�INT32
		@param friendlyValue : �Ѻöȣ�UINT32
		@param playerBase : �Է����base mailbox
		@param relationOffset : ��ʾ�Է�����ڹ�ϵ����е�λ�ã���������ż��λ

		relationStatus����ϸ���ͣ�
		relationStatusΪUINT32,����ÿһ����ϵʹ��relationStatus�������ֽ�λģʽ��
		��λ2���ֽڱ�ʾ��Ӧsm_playerDBID2��ҵĹ�ϵ״̬����λ2�ֽڱ�ʾ��Ӧsm_playerDBID1����ҹ�ϵ״̬��
		Լ�������������ϵ�߶�Ӧsm_playerDBID1��������Ϊsm_playerDBID2
		relationOffset������relationStatus���λģʽ�У���λ��2���ֽڻ��ǵ�λ��2���ֽڱ�ʾ��ҵĹ�ϵ״̬��
		"""
		self.relationUID = relationUID
		self.playerName = playerName
		self.relationStatus = relationStatus
		self.relationOffset = relationOffset		# ������ϵ״̬�ڹ�ϵ״̬�е�ƫ����
		self.friendlyValue = friendlyValue
		self.playerBase = playerBase
		self.playerDBID = playerDBID

		self.needSaveFriendlyValue = False	# �Ѻö��Ƿ����˸ı䣬�Ա���������ߵ�ʱ��дdb

	def convertRelation( self, relation ):
		"""
		ת���˹�ϵ��Ӧ����ҹ�ϵ״̬��־����Ӧ��λ

		@param relation : ��ϵ����
		"""
		return relation << self.relationOffset

	def convertTargetRelation( self, relation ):
		"""
		ת���˹�ϵ��Ӧ���Է���ҹ�ϵ״̬��־����Ӧ��λ
		"""
		relationOffset = RELATION_STATUS_HIGH_OFFSET
		if self.relationOffset == RELATION_STATUS_HIGH_OFFSET:
			relationOffset = 0
		return relation << relationOffset

	def getTargetRelation( self ):
		"""
		��ȡ�ͶԷ��Ĺ�ϵ״̬
		"""
		return ( self.relationStatus >> self.relationOffset ) & 0xFFFF

	def targetHasRelation( self, relation ):
		"""
		�Է������Ƿ���ڹ�ϵ��һ�������жϼ����Ƿ�Է��ĺ�����������
		"""
		offset = self.relationOffset == 0 and RELATION_STATUS_HIGH_OFFSET or 0
		return self.relationStatus & ( relation << offset )

	def meHasRelation( self, relation ):
		"""
		��Է��Ƿ����ĳ�ֹ�ϵ
		"""
		return self.relationStatus & ( relation << self.relationOffset )

	def hasCoupleRelation( self ):
		"""
		�Ƿ���ڷ��޹�ϵ
		"""
		return self.relationStatus & ( csdefine.ROLE_RELATION_COUPLE << RELATION_STATUS_HIGH_OFFSET ) and self.relationStatus & csdefine.ROLE_RELATION_COUPLE

	def hasTeachRelation( self ):
		"""
		�Ƿ����ʦͽ��ϵ
		"""
	 	return ( self.relationStatus & csdefine.ROLE_RELATION_PRENTICE and self.relationStatus & ( csdefine.ROLE_RELATION_MASTER << RELATION_STATUS_HIGH_OFFSET ) ) \
		or ( self.relationStatus & csdefine.ROLE_RELATION_MASTER  and self.relationStatus & ( csdefine.ROLE_RELATION_PRENTICE << RELATION_STATUS_HIGH_OFFSET ) )

	def isRelationEmpty( self ):
		"""
		�Ƿ�ͶԷ��Ѿ��޹�ϵ
		"""
		return self.relationStatus == 0

	def hasVoluntaryRelation( self ):
		"""
		�Ƿ�ͶԷ�������������Ĺ�ϵ
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

		self.blacklist = {}			# { playerDBID:relationItem, ... }����Һ�����
		self.targetBlacklist = {}		# { playerDBID:relationItem, ... }����ұ��Ӻ�����
		self.friends = {}				# { playerDBID:relationItem, ... }����Һ���
		self.sweetieDict = {}			# { playerDBID:relationItem, ... }���������
		self.couple_lover = None		# relationItem,��ҷ���
		self.foeDict = {}				# { playerDBID:relationItem, ... }������
		self.beFoeDict = {}			# { playerDBID:relationItem, ... }������Ϊ����
		self.allyDict = {}				# { playerDBID:relationItem, ... }����ҽ���ֵ�
		self.allyTitle = ""			# ��ݳƺ�

		# ��ҳ�ʼ����ϵ�����У����ô˱����������Ҵ�ʱbase mailbox�Ѵ�����ϣ��Է�����п����Ѿ�ͨ��
		# db��ü�����base mailbox������һЩ�����ڼ�����ʼ����ϵ����ʱ����ز������󣬴�ʱ���ݴ˱��
		# ���о���Ĵ���
		self.relationInitializing = False

		self.inviteFriendBase = None					# ����������ѵ����base
		self.inviteFriendTime = 0.0						# �����Ϊ���ѵ�ʱ��
		self.inviteSweetieUID = None					# ���������Ϊ���˵����base
		self.sweetie_beInvitedTime = 0.0				# �����Ϊ���˵�ʱ��

		self.relationIndexCounter = 0	# ��ʼ����ϵ���ݼ���
		self.tempRelationList = []		# ��ʼ����ϵ��ʱ�洢����

		self.admirerNotifyTimerID = 0	# ����֪ͨ��Ľ�ߵ�timerID

		# ʦͽ��ϵ
		self.teach_masterItem = None	# ʦ��������relationItem
		self.prenticeDict = {}		# ͽ�ܵ�����{ playerName:relationItem, ... }
		self._inviteTeachBase = None	# �����ʦ��ͽ��base mailbox
		self._inviteTeachTime = 0		# ����Զ�̰�ʦ��ʱ��
		self.isTeachProgress = False		# �Ƿ��ڰ�ʦ������

		self.masterEverDict = {}			# ������ʦ��
		self.prenticeEverDict = {}		# ������ͽ��

	def _removeRelation( self, relationUID ):
		"""
		�Ƴ���ϵ
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
		���һ����ϵ��¼
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
		���¹�ϵ״̬
		@param relationItem : ��ϵ����
		@param relation : ��ԵĹ�ϵ��������csdefine��
		@param isWriteDB : �Ƿ���Ҫд�����ݿ�,BOOL��ֻ���������𷽲Ż���µ�db
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
		�Ƴ�ĳһ�ֹ�ϵ

		@param relationItem : ��ϵ����
		@param myRelation : ��ԵĹ�ϵ��������csdefine��
		@param isTargetDisband : �Է��Ƿ����˹�ϵ
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
		����relationItem���Ѻöȵ�db
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
		��ð�ʦ������
		"""
		return BigWorld.globalData["TeachMgr"]

	def rlt_onLevelUp( self ):
		"""
		��Ҽ���ı䣬֪ͨ����Ȥ���������
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
		�������֪ͨ
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
		���cell�������
		"""
		# ��ʼ����ҹ�ϵ
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
		��ȡ��ϵ���ݱ�ص�

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
			DEBUG_MSG( "( %s )�����ڹ�ϵ���ݡ�" % self.getName() )
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
			# ��������ʱ�Ĺ�ϵ�仯

			for relation in csconst.MULTI_RELATION_LIST:	# ˫�߹�ϵ����
				if myStatus & relation == 0:
					continue
				if targetStatus & relation == 0:	# �Է�����˹�ϵ
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
						self.couple_lover = relationItem		# ������û���꣬�����Ƿ���
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
			if relationItem.relationStatus == 0:	# �������������ʱ˫�����޹�ϵ
				continue
			for relation in csconst.SINGLE_RELATION_LIST:	# ���߹�ϵ����
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
					if myStatus & relation:	# ������ʦ��							
						self.prenticeDict[targetDBID] = relationItem
						if not targetStatus & csdefine.ROLE_RELATION_PRENTICE:	# ����Է�����ͽ�� 
							# �Է�����˹�ϵ����cell��ʼ�������
							self.cell.targetDisbandTeach( relationItem.playerDBID, csdefine.ROLE_RELATION_PRENTICE )
						if roleState == 1:	#�Է�ɾ����
							self.cell.teach_disband( relationItem.playerDBID, relationItem.playerName )
							self.statusMessage( csstatus.ROLE_RELATION_NOT_EXIST, cschannel_msgs.ROLERELATION_TARGET_PRIENTICE, targetName )
				elif relation == csdefine.ROLE_RELATION_PRENTICE:
					if myStatus & relation:	# ������ͽ��
						self.teach_masterItem = relationItem
						if not targetStatus & csdefine.ROLE_RELATION_MASTER:	# ����Է�����ʦ�� 
							self.cell.targetDisbandTeach( relationItem.playerDBID, csdefine.ROLE_RELATION_MASTER )							
						if roleState == 1:	#�Է�ɾ����
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
		֪ͨ���ڹ�ϵ����ң���������
		"""
		length = len( self.relationDatas )
		count = min( Const.RELATION_ADMIRE_COUNT_NOTIFY, length - self.relationIndexCounter )
		self.tempRelationList = self.relationDatas.values()		# ����һ����ʱ�б�
		for i in xrange( count ):
			index = i + self.relationIndexCounter
			relationItem = self.tempRelationList[index]
			Love3.g_baseApp.lookupRoleBaseByName( relationItem.playerName, Functor( self.__onNotifyCB, relationItem ) )
		self.relationIndexCounter += count

		# ֪ͨ���
		if self.relationIndexCounter >= length:
			self.delTimer( self.admirerNotifyTimerID )
			self.relationIndexCounter = 0
			self.tempRelationList = []

	def __onNotifyCB( self, relationItem, callResult ):
		"""
		����֪ͨ�ͼ����й�ϵ�����

		@param playerName		:	�������
		@type playerName		:	string
		@param callResult	:	���BASE
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
		�й�ϵ�����������

		@param playerDBID : ���ߵ����dbid
		@param playerBase : ������ҵ�base mailbox
		"""
		try:
			relationItem = self.relationDatas[relationUID]
		except KeyError:
			ERROR_MSG( "���( %s )�Ҳ�������( %i )��" % ( self.getName(), relationUID ) )
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
			
		if relationItem.hasVoluntaryRelation() and not relationItem.meHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):	# ������ʾ
			relationStr = self.getPriorRelationStr( relationItem )
			if relationStr != "":
				self.statusMessage( csstatus.ROLE_RELATION_TARGET_LOGON, relationStr, relationItem.playerName )

	def rlt_onPlayerLogout( self, relationUID ):
		"""
		Define method.
		���ڹ�ϵ�����������
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
			if relationItem.needSaveFriendlyValue:	# ����Է������߱������Ѻöȣ���������ʱ������Ҫ����
				relationItem.needSaveFriendlyValue = False
			if not relationItem.targetHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):
				self.client.rlt_offlineUpdate( relationUID )
				
		if relationItem.hasVoluntaryRelation() and not relationItem.meHasRelation( csdefine.ROLE_RELATION_BLACKLIST ):	# ��������ʾ
			relationStr = self.getPriorRelationStr( relationItem )
			if relationStr != "":
				self.statusMessage( csstatus.ROLE_RELATION_TARGET_LOGOFF, relationStr, relationItem.playerName )
	
	def getPriorRelationStr( self, relationItem ) :
		"""
		��ȡ���ȵĹ�ϵ		
		"""
		relationStatus_ = ""
		if relationItem.hasVoluntaryRelation():
			if relationItem.meHasRelation( csdefine.ROLE_RELATION_COUPLE ):		# ����
				relationStatus_ = cschannel_msgs.ROLERELATION_TARGET_COUPLE 
			elif relationItem.meHasRelation( csdefine.ROLE_RELATION_SWEETIE ):	# ����
				relationStatus_ = cschannel_msgs.ROLERELATION_TARGET_SWEETIE 
			elif relationItem.meHasRelation( csdefine.ROLE_RELATION_ALLY ):		# ���
				relationStatus_ = cschannel_msgs.ROLERELATION_TARGET_ALLY 
			elif relationItem.meHasRelation( csdefine.ROLE_RELATION_MASTER )\
			 	or relationItem.meHasRelation( csdefine.ROLE_RELATION_MASTER_EVER ):		# ʦ��/��ȥ��ʦ��
				relationStatus_ = cschannel_msgs.ROLERELATION_TARGET_PRIENTICE
			elif relationItem.meHasRelation( csdefine.ROLE_RELATION_PRENTICE )\
				 or relationItem.meHasRelation( csdefine.ROLE_RELATION_PRENTICE_EVER ):		# ͽ��/��ȥ��ͽ��
				relationStatus_ = cschannel_msgs.ROLERELATION_TARGET_FMASTER 
			elif relationItem.meHasRelation( csdefine.ROLE_RELATION_FRIEND ):	# ����
				relationStatus_ = cschannel_msgs.ROLERELATION_TARGET_FRIEND 
			elif relationItem.meHasRelation( csdefine.ROLE_RELATION_FOE ):		# ����
				relationStatus_ = cschannel_msgs.ROLERELATION_TARGET_FOE 
		else:
			ERROR_MSG( "player( %s ) has no relation." % ( self.getName() ) )
		return relationStatus_

	#----------------------------------------------------------------
	#  ����
	#----------------------------------------------------------------
	def addTeamFriendlyValue( self, teammateDBIDList ):
		"""
		Define method.
		�����Ӵ�֣�ɱ���������������к��ѣ���ô�Ѻö����ӡ�

		@param teammateDBIDList : ���dbid�б�
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
		��Ӻ���

		@param playerName	:	�������
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
		addFriend��lookupRoleBaseByName�����ص�

		@param callResult: �������
		@type callResult: STRING
		"""
		if callResult is None:
			self.statusMessage( csstatus.FRIEND_NOT_ON_LINE )
			return
		callResult.beInvitedForFriend( self, self.getName() )

	def beInvitedForFriend( self, playerBase, playerName ):
		"""
		Define method.
		�Է����뼺����Ϊ����
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
		�������Ϊ����
		"""
		self.inviteFriendBase = playerBase
		self.inviteFriendTime = time.time()
		self.client.beAskedForFriend( playerName )

	def replyForFriendInvite( self, reply ):
		"""
		Exposed method.
		�Ӻ�������Ļش�
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
		�Է����ͬ���Ϊ���ѡ�
		playerName, relationStatus, relationOffset, friendlyValue, playerBase, playerDBID
		"""
		if self.getFriendCount() >= Const.FRIEND_FRIEND_MAX_COUNT:
			self.statusMessage( csstatus.FRIEND_FRIENDLIST_FULL )
			return

		# �ڳ�Ϊ����ǰ���Է��п����ڼ����ĺ���������������У��򼺷��ڶԷ��ĺ����������������
		relationItem = self.getRelationItemByName( playerName )
		if relationItem is None:
			relationUID = Love3.g_baseApp.getRelationUID()
			if relationUID == -1:
				return
			relationStatus = csdefine.ROLE_RELATION_FRIEND | ( csdefine.ROLE_RELATION_FRIEND << RELATION_STATUS_HIGH_OFFSET )
			# Լ��������Ӻ�������Ϊsm_playerName1д��db
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
		�Է����뼺���Ӻ��ѣ�����ͬ�⣬��֮ǰ�Ѵ��ڹ�ϵ����ô���¹�ϵ������
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
		ͬ��Է��ļӺ������룬�Ӻ��ѳɹ������ü����ĺ�������
		Լ���������������������ߣ���˹�ϵ״̬ƫ������RELATION_STATUS_HIGH_OFFSET
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
		�Ƴ����ѹ�ϵ
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
		�Է��Ƴ��˺��ѹ�ϵ�����ü�������
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
		���غ�������
		"""
		return len( self.friends )

	def hasFriend( self, playerName ):
		"""
		�Ƿ��Ѿ����ں���
		"""
		for item in self.friends.itervalues():
			if item.playerName == playerName:
				return True
		return False
		

	#----------------------------------------------------------------
	#  ������.
	#----------------------------------------------------------------
	def hadBlacklist( self, playerName ):
		"""
		�Ƿ��Ѿ����ں�����
		"""
		for item in self.blacklist.itervalues():
			if item.playerName == playerName:
				return True
		return False

	def addBlacklist( self, playerName ):
		"""
		Exposed method.
		��playerName��Ӻ�����
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
			if hasVoluntary:	# ����Ѿ����ڹ�ϵ
				self.client.rtf_relationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_BLACKLIST )
			else:
				self.client.rtf_receiveNameInfo( playerName, relationItem.relationUID, relationItem.friendlyValue, relationItem.getTargetRelation() )
			if relationItem.playerBase:
				relationItem.playerBase.beUpdated2Blacklist( relationItem.relationUID )
			self.client.rlt_offlineUpdate( relationItem.relationUID )

	def _addBlacklistLookUpBaseCB( self, result ):
		"""
		��ѯ����Ϊ�������ĺ����Ƿ�����
		"""
		if result is None:
			self.statusMessage( csstatus.CANT_ADD_BLACKLIST_OFFLINE )
			return
		result.rlt_addBlacklistRequest( self )

	def rlt_addBlacklistRequest( self, playerBase ):
		"""
		Define method.
		�Է���Ұ��Լ���Ϊ�����������������ݷ����Է���
		"""
		playerBase.rlt_addBlacklistReply( self, self.databaseID, self.getName() )

	def rlt_addBlacklistReply( self, playerBase, playerDBID, playerName ):
		"""
		Define method.
		�ӶԷ�Ϊ��������������Ļظ�
		"""
		# ��ʱ�����п����Ѿ�������
		if self.hadBlacklist( playerName ):
			return
		if self.getBlacklistCount() > Const.FRIEND_BLACKLIST_MAX_COUNT:
			return

		relationUID = Love3.g_baseApp.getRelationUID()
		if relationUID == -1:
			return
		# ��λ��ʾ���������ϵ�ŵĹ�ϵ״̬
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
		���ӵ��������У����ν�����ϵ
		"""
		relationStatus = csdefine.ROLE_RELATION_BLACKLIST
		relationItem = RelationItem( relationUID, playerName, relationStatus, RELATION_STATUS_HIGH_OFFSET, 0, playerBase, playerDBID )
		self.relationDatas[relationUID] = relationItem
		self.targetBlacklist[playerDBID] = relationItem

	def beUpdated2Blacklist( self, relationUID ):
		"""
		Define method.
		�������˺�������֮ǰ�Ѿ�������ϵ��
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
		�Է��Ƴ��˺�����
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
		��ȡ����������
		"""
		return len( self.blacklist )

	def meInBlacklist( self, playerName ):
		"""
		�����ڶԷ��ĺ�������
		"""
		for item in self.targetBlacklist.itervalues():
			if item.playerName == playerName:
				return True
		return False

	# ----------------------------------------------------------------------------
	# ����
	# ----------------------------------------------------------------------------
	def addSweetie( self, relationUID ):
		"""
		��Ϊ���˵����롣

		��base����Ƿ�������Ѻö�ֵ������
		�Ϸ���ͼӺ������ƣ�Ҫ����relationStatus��״̬����Ҫ���ǿͻ��˱��ֵ���
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
			# �Ѿ���ݣ����ܽ�Ϊ���ˡ�
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
		�������Ϊ����

		@param inviterGender : �����ߵ��Ա�
		@param relationUID : ��ϵuid
		"""
		relationItem = self.relationDatas[relationUID]
		playerBase = relationItem.playerBase
		if self.getGender() == inviterGender:
			self.relationStatusMessage( playerBase, csstatus.SWEETIE_THE_SAME_SEX )	# ͬ��֮�䲻�ܽύ
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
		�������Ϊ����
		"""
		self.inviteSweetieUID = relationUID				# �Ա�ͬ��ύʱȷ���Ǻ�˭�ύΪ����
		self.sweetie_beInvitedTime = time.time()
		self.client.beInvitedSweetie( relationUID )

	def replyForSweetieInvite( self, reply ):
		"""
		Exposed method.
		��һظ��ύ��������Ľӿ�

		@param reply: ͬ���ܾ�
		@type reply: BOOL
		"""
		if not reply:
			self.relationStatusMessage( self.relationDatas[self.inviteSweetieUID].playerBase, csstatus.SWEETIE_BE_REFUSEED, self.getName() )
		else:
			self.relationDatas[self.inviteSweetieUID].playerBase.cell.addSweetieSuceeded( self.inviteSweetieUID )

	def addSweetieSuceeded( self, relationUID ):
		"""
		Define method.
		�ύ���˳ɹ�����������
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
		�ύ���˳ɹ������¹�ϵ���ݵ�����
		"""
		relationItem = self.relationDatas[relationUID]
		self.sweetieDict[relationItem.playerDBID] = relationItem
		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_SWEETIE )
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_SWEETIE )
		self._updateRelationStatus( relationItem, myRelation, targetRelation, False )
		self.client.rtf_relationUpdate( relationUID, csdefine.ROLE_RELATION_SWEETIE )
		# �����־
		g_logger.sweeticBuildLog( self.databaseID, self.getName(), relationItem.playerDBID, relationItem.playerName )

	def removeSweetie( self, relationUID ):
		"""
		Exposed method.
		������˹�ϵ������
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
		�Է���������˹�ϵ
		"""
		relationItem = self.relationDatas[relationUID]
		self.statusMessage( csstatus.SWEETIE_BE_REMOVE_SUCCESS, relationItem.playerName )
		del self.sweetieDict[relationItem.playerDBID]
		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_SWEETIE )
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_SWEETIE )
		self._removeRelationStatus( relationItem, myRelation, targetRelation, True )
		self.client.endRelationUpdate( relationUID, csdefine.ROLE_RELATION_SWEETIE )

	# ----------------------------------------------------------------------------
	# ����
	# ----------------------------------------------------------------------------
	def requestMarriage( self, playerDBID ):
		"""
		Define method.
		������

		@param playerDBID : �������dbid
		@type playerDBID : DATABASE_ID
		"""
		try:
			relationItem = self.sweetieDict[playerDBID]
		except KeyError:
			ERROR_MSG( "���( %s )�����ڴ�����( dbid:%s )�����ܽ�顣" % ( self.getName(), playerDBID ) )
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
		���ɹ�,�������ݿ����ع�ϵ״̬

		@param playerDBID:	��ҵ�dbid
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
		�Է������飬�ɹ���飬���ü�����base����

		@param loverDBID: �Է���databaseID
		@type loverDBID: DATABASE_ID
		"""
		relationItem = self.sweetieDict[ playerDBID ]
		myRelation = relationItem.convertRelation( csdefine.ROLE_RELATION_COUPLE )
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_COUPLE )
		self._updateRelationStatus( relationItem, myRelation, targetRelation, False )
		self.couple_lover = relationItem
		# ֪ͨ�ͻ���
		self.client.rtf_relationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_COUPLE )

	def couple_forceDivorce( self ):
		"""
		Define method.
		������ǿ�����

		�����ݿ����������״̬
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
		�ͶԷ���������
		"""
		myRelation = self.couple_lover.convertRelation( csdefine.ROLE_RELATION_COUPLE )
		targetRelation = self.couple_lover.convertTargetRelation( csdefine.ROLE_RELATION_COUPLE )
		self._removeRelationStatus( self.couple_lover, myRelation, targetRelation, True )
		self.client.endRelationUpdate( self.couple_lover.relationUID, csdefine.ROLE_RELATION_COUPLE )
		self.couple_lover = None

	def couple_findWeddingRing( self ):
		"""
		Define method.
		�һض�ʧ�Ľ���ָ���������cell���洢�������֣�����ָ��Ҫ����Ϣ����base��ѯ
		"""
		self.cell.couple_findWeddingRing( self.couple_lover.playerName )

	def rlt_queryAreaInfo( self, relation ):
		"""
		Exposed method.
		�����ѯ��ϵ�����ڵ���

		@param relation : ������csdefine����ҹ�ϵ
		"""
		if relation == csdefine.ROLE_RELATION_BLACKLIST:
			relationDict = self.blacklist
		elif relation == csdefine.ROLE_RELATION_FRIEND:
			relationDict = self.friends
		elif relation == csdefine.ROLE_RELATION_SWEETIE:
			relationDict = self.sweetieDict
		elif relation == csdefine.ROLE_RELATION_COUPLE:
			relationDict = { "lover": self.couple_lover }	# Ϊ�������ͳһ������ʱ�ֵ�
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
	# ��ӳ���
	# -------------------------------------------------------------------------------
	def hasFoe( self, playerName ):
		"""
		�Ƿ���ڳ���
		"""
		for item in self.foeDict.itervalues():
			if item.playerName == playerName:
				return True
		return False

	def addFoe( self, playerName ):
		"""
		Exposed method.
		��ӳ���
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
			if hasVoluntary :	# ֻ�к�������ϵ�ܺͳ��˹�ϵ���棬���ܰ�һ����Ҽ�Ϊ��������Ҳ�ܼ�Ϊ����
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
		��ѯ����Ϊ���˵�����Ƿ�����
		"""
		if result is None:		# ��Ҳ�����
			self.statusMessage( csstatus.CANT_ADD_FOE_OFFLINE )
			return
		result.rlt_addFoeRequest( self )

	def rlt_addFoeRequest( self, targetBase ):
		"""
		Define method.
		�Է���Ұ��Լ���Ϊ���ˣ����������ݷ����Է���
		"""
		targetBase.rlt_addFoeReply( self, self.databaseID, self.getName() )

	def rlt_addFoeReply( self, playerBase, playerDBID, playerName ):
		"""
		Define method.
		�ӶԷ�Ϊ������������Ļظ�
		"""
		# ��ʱ�����п����Ѿ�������
		if self.hasFoe( playerName ):
			self.statusMessage( csstatus.FOE_ALREADY_HAVE )
			return
		if len( self.foeDict ) > csconst.RELATION_FOE_NUM_LIMIT:
			self.statusMessage( csstatus.FOE_CANT_ADD_FULL )
			return

		relationUID = Love3.g_baseApp.getRelationUID()
		if relationUID == -1:
			return
		# ��λ��ʾ���������ϵ�ŵĹ�ϵ״̬
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
		���ɱ��Ϊ����

		@param playerDBID: ���˵�dbid
		@param playerName: ���˵�����
		@param playerBase: ���˵�base mailbox
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
			# Լ��������ӳ�������Ϊsm_playerName1д��db
			relationItem = RelationItem( relationUID, playerName, relationStatus, 0, 0, playerBase, playerDBID )
			self.relationDatas[relationUID] = relationItem
			self.foeDict[playerDBID] = relationItem
			self._createRelation2DB( relationUID, playerDBID, relationStatus )
			playerBase.beAddedFoeSuccess( relationUID, self.getName(), self.databaseID, self )
		else:
			hasVoluntary = relationItem.hasVoluntaryRelation()
			relationUID = relationItem.relationUID		
		if hasVoluntary:	# ����Ѿ����ڹ�ϵ
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
		����ӳ��˳ɹ������β�����ϵ
		"""
		relationStatus = csdefine.ROLE_RELATION_FOE
		relationItem = RelationItem( relationUID, playerName, relationStatus, RELATION_STATUS_HIGH_OFFSET, 0, playerBase, playerDBID )
		self.relationDatas[relationUID] = relationItem
		self.beFoeDict[playerDBID] = relationItem

	def updateRelation2Foe( self, relationUID ):
		"""
		Define method.
		���ӳ��ˣ���ϵ����
		"""
		relationItem = self.relationDatas[relationUID]
		self.beFoeDict[relationItem.playerDBID] = relationItem
		targetRelation = relationItem.convertTargetRelation( csdefine.ROLE_RELATION_FOE )
		self._updateRelationStatus( relationItem, 0, targetRelation, False )

	def removeFoe( self, relationUID ):
		"""
		Exposed method.
		�Ƴ�����
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
		�Է�ɾ���˳���
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
		����������ֻ��relationItem���������򷵻�None
		"""
		for relationItem in self.relationDatas.itervalues():
			if relationItem.playerName == playerName:
				return relationItem
		return None

	def rlt_checkAddFriendyValue( self, playerDBID ):
		"""
		Define method.
		�Ƿ��ܹ���playerDBID����������Ѻö�
		"""
		self.cell.rlt_checkAddFriendyResult( ( playerDBID in self.friends ) )

	def addItemFriendlyValue( self, playerDBID, value ):
		"""
		Define method.
		��������ѵ��Ѻö�
		"""
		self.friends[playerDBID].addFriendlyValue( value, self )

	# ------------------------------------------------------------------------
	# ʦͽ��ϵ
	# ------------------------------------------------------------------------
	def setTeachExtraInfo( self ):
		"""
		Define method
		���Լ��ĳ�ʦͽ����������������ʱ�䴫��������
		"""
		daysSec = 24 * 3600
		wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec) - 1
		lastWeekOnlineTime = self.weekOnlineTime.get( wT, 0.0 )		# ��ȡ��������ʱ��
		self._getTeachMgr().getTeachExtraInfo( self.databaseID, len(self.prenticeEverDict), lastWeekOnlineTime )
		
	def teach_registerTeacher( self ):
		"""
		Define method
		ע����ͽ
		"""
		# ���Լ��ĳ�ʦͽ����������������ʱ�䴫��cell
		daysSec = 24 * 3600
		wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec) - 1
		lastWeekOnlineTime = self.weekOnlineTime.get( wT, 0.0 )		# ��ȡ��������ʱ��
		self.cell.teach_registerTeacher( len(self.prenticeEverDict), lastWeekOnlineTime )
	
	def teach_registerPrentice( self ):
		"""
		Define method
		ע���ʦ
		"""
		# ���Լ�����������ʱ�䴫��cell
		daysSec = 24 * 3600
		wT = int( time.time() - 4*daysSec + 8*3600 )/ (7*daysSec) - 1
		lastWeekOnlineTime = self.weekOnlineTime.get( wT, 0.0 )		# ��ȡ��������ʱ��
		self.cell.teach_registerPrentice( lastWeekOnlineTime )
	
	def masterDisbandTeach( self ):
		"""
		Define method.
		ʦ������˹�ϵ
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
		ͽ�ܽ���˹�ϵ
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
		ʦ�������Ϊʦͽ�ɹ���дdb

		param prenticeName:	ͽ�ܵ�����
		type prenticeName:	STRING
		"""
		relationItem = self.getRelationItemByName( prenticeName )
		if relationItem is None:
			relationUID = Love3.g_baseApp.getRelationUID()
			if relationUID == -1:		# �˴�ʧ������1����ٴ����룬Ŀǰ��δʵ�ִ˻���
				ERROR_MSG( "player( %s ), prentice( %s )--->>>relationUID == -1" % ( self.getName(), prenticeName ) )
				return
			relationStatus = csdefine.ROLE_RELATION_MASTER | ( csdefine.ROLE_RELATION_PRENTICE << RELATION_STATUS_HIGH_OFFSET )
			# ʦ����Ϊsm_playerName1д��db
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
		��ʦ�ɹ���������ϵ
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
		��ҽ��ʦͽ��ϵ�Ľӿ�

		Param playerDBID:	�Է���ҵ�dbid
		Type playerDBID:	DATABASE_ID
		"""
		if self.teach_masterItem:	# ��������ͽ��
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
		ʦ����ʦ
		"""
		relationItem = self.prenticeDict.pop( prenticeDBID, [] )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JSGX_AUTO_DISBAND % ( relationItem.playerName, self.getName() ), [] )
		self.prenticeEverDict[prenticeDBID] = relationItem		# ������ͽ��
		relationItem.relationStatus &= ~( relationItem.convertTargetRelation( csdefine.ROLE_RELATION_PRENTICE ) | relationItem.convertRelation( csdefine.ROLE_RELATION_MASTER ) )
		relationItem.relationStatus |= relationItem.convertTargetRelation( csdefine.ROLE_RELATION_PRENTICE_EVER ) | relationItem.convertRelation( csdefine.ROLE_RELATION_MASTER_EVER )
		self.client.rtf_relationUpdate( relationItem.relationUID, csdefine.ROLE_RELATION_PRENTICE_EVER )
		query = "update custom_Relation set sm_relationStatus = %i where sm_uid = %i" % ( relationItem.relationStatus, relationItem.relationUID )
		BigWorld.executeRawDatabaseCommand( query, self._updateTeachRelationCB )		#if relationItem.relationStatus == 0:
		
		g_logger.teachCompleteLog( self.databaseID, self.getName(), prenticeDBID )

	def _updateTeachRelationCB( self, result, rows, errstr ):
		"""
		��ҳ�ʦ��ʦͽ��ϵdb���µĻص�
		"""
		if errstr:
			ERROR_MSG( errstr )

	def endTeachSuccess( self, playerDBID ):
		"""
		Define method.
		��ʦ�ɹ���������������
		"""
		if self.teach_masterItem:	# �����ͽ��
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
		�����������Ŀ����ҵ�ʦͽ��ϵ
		"""
		if self.teach_masterItem:	# �����ͽ��
			self.cell.teach_disband( self.teach_masterItem.playerDBID, playerName )
			try:
				g_logger.teachRemoveLog( self.teach_masterItem.playerDBID, playerName, self.databaseID, self.getName() )
			except:
				EXCEHOOK_MSG()
			
			return
		
		# �����Ƿ���ʦ��
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
		ʦ���ظ�Զ�̰�ʦ����

		@param agree : �Ƿ�ͬ��
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
		ͽ�ܻظ�Զ�̰�ʦ����

		@param agree : �Ƿ�ͬ��
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
		ͽ��ͬ���Ϊʦͽ������Ƿ�������ͽ����

		@param playerBase : ͽ�ܵ�base mailbox
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
		����Զ�̽�Ϊʦͽ�Ľ������

		@param statusID : ״̬��Ϣid��������csstatus.pyģ��
		@type statusID : UINT16
		"""
		param = ""
		if statusID == csstatus.TEACH_REQUEST_MASTER_REFUSE or statusID == csstatus.REMOTE_FIND_PRENTICE_REFUSE or statusID == csstatus.TEACH_PRENTICE_HAS_MONSTER or status == csstatus.TEACH_REQUEST_PRENTICE_NUM_LIMIT:
			param = "(\'%s\',)" % self.getName()
		self._inviteTeachBase.client.onStatusMessage( statusID, param )
		self._inviteTeachBase = None		# �����ʦ��ͽ��base mailbox
		self._inviteTeachTime = 0			# ����Զ�̰�ʦ��ʱ��

	def prenticeRequestBeTeached( self, prenticeName, prenticeBaseMB ):
		"""
		Define method.
		��������ʦ

		@param prenticeName : �����ʦ��ҵ�����
		@type prenticeName : STRING
		@param prenticeBaseMB : �����ʦ��ҵ�base mailbox
		@type prenticeBaseMB : MAILBOX
		"""
		if self._inviteTeachBase and self._inviteTeachTime + TEACH_REQUEST_TIME_OUT > time.time():
			return
		if self.hasFoe( prenticeName ):
			self.statusMessage( csstatus.FOE_HAS_EXIST )
			return

		self._inviteTeachBase = prenticeBaseMB	# �����ʦ��ͽ��base mailbox
		self._inviteTeachTime = time.time()		# ����Զ�̰�ʦ��ʱ��

		self.client.prenticeRequestBeTeached( prenticeName )

	def teach_requestBeTeached( self, masterDBID ):
		"""
		Exposed method.
		ͽ�ܷ���Զ�̰�ʦ����

		@param masterDBID : ��ʦĿ����ҵ�dbid
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
		ʦ��������ͽ����
		"""
		if len( self.prenticeDict ) >= csconst.TEACH_PRENTICE_MAX_COUNT:
			self.statusMessage( csstatus.TEACH_PRENTICE_NUM_FULL )
			return
		self._getTeachMgr().requestTeach( self, self.getName(), prenticeDBID )

	def masterRequestTeach( self, playerName, playerBase ):
		"""
		Define method.
		�Է�������ͽ

		@param playerName : �Է���ҵ�����
		@param playerBase : �Է���ҵ�base mailbox
		"""
		if self.hasFoe( playerName ):
			self.statusMessage( csstatus.FOE_HAS_EXIST )
			return
		self._inviteTeachBase = playerBase		# ������ͽ��ʦ��base mailbox
		self._inviteTeachTime = time.time()			# ����Զ����ͽ��ʱ��
		self.client.masterRequestTeach( playerName )

	def teach_beginRemoteTeach( self, masterDBID, masterName, playerBase ):
		"""
		Define method.
		ʦ��ͬ��Զ�̰�ʦ��ͽ�ܵ��ô˽ӿ�

		param masterName:	ʦ��������
		type masterName:	STRING
		"""
		relationItem = self.getRelationItemByName( masterName )
		if relationItem is None:
			relationUID = Love3.g_baseApp.getRelationUID()
			if relationUID == -1:		# �˴�ʧ������0.1����ٴ����룬Ŀǰ��δʵ�ִ˻���
				ERROR_MSG( "player( %s ), prentice( %s )--->>>relationUID == -1" % ( self.getName(), masterName ) )
				return
			# ͽ����ΪplayerName1д��db
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
		Զ�̰�ʦ�ɹ�������ʦ���Ĺ�ϵ����
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
		ͽ�������������Զ���ʦ
		"""
		relationItem = self.teach_masterItem
		self.teach_masterItem = None
		masterName = relationItem.playerName
		self.statusMessage( csstatus.TEACH_RELATION_DISBAND, masterName )	# ֪ͨ���
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
		# ��ʦ����ҷ��ʼ�
		mailType = csdefine.MAIL_TYPE_QUICK
		title = cschannel_msgs.ROLERELATION_INFO_3
		content = cschannel_msgs.ROLERELATION_INFO_4%self.getName()
		BigWorld.globalData["MailMgr"].send( None, masterName, mailType, csdefine.MAIL_SENDER_TYPE_NPC, self.getName(), title, content, 0, [] )
		
		g_logger.teachCompleteLog( self.databaseID, self.getName(), masterDBID )

	def onTongChangeNotifyRelation( self, tongName ):
		"""
		Define method.
		���ı�֪ͨ
		"""
		for relationUID, relationItem in self.relationDatas.iteritems():
			if relationItem.hasVoluntaryRelation():
				playerBase = relationItem.playerBase
				if playerBase is None: continue
				playerBase.client.onRealtionTongChanged( relationUID, tongName )

	def queryTongGrade( self, relationUID ) :
		"""
		Exposed method
		��ȡ���ְ��
		"""
		for relationUID_, relationItem in self.relationDatas.iteritems():
			if relationUID_ != relationUID : continue
			if relationItem.hasVoluntaryRelation():
				playerBase = relationItem.playerBase
				if playerBase is None:return
			 	playerBase.cell.onSendTongGrade( relationUID_, self )

	# ---------------------------------------------------------------------------------
	# ��ҽ��
	# ---------------------------------------------------------------------------------
	def rlt_requestAlly( self, captainBase, playerDBIDList ):
		"""
		Define method.
		��������ݣ�����Լ��Ͳ����ݵ���ҹ�ϵ�Ƿ���Ͻ������

		@param captainBase: ���ռ������entity baseMailbox
		@param playerDBIDList: �����ݵ����dbid�б�
		"""
		statusID = csstatus.CAN_ALLY	# ���Խ��
		for dbid in playerDBIDList:
			try:
				relationItem = self.friends[dbid]
			except KeyError:
				statusID = csstatus.CANNOT_ALLY_LACK_FRIENDLY_VALUE	# ���Ǻ��ѹ�ϵ
				break
			if relationItem.friendlyValue < csconst.RELATION_ALLY_NEED_FRIENDLY_VALUE:
				statusID = csstatus.CANNOT_ALLY_LACK_FRIENDLY_VALUE	# �ѺöȲ���
				break
			if self.sweetieDict.has_key( dbid ):
				statusID = csstatus.CANNOT_ALLY_HAD_SWEETIE	# �Ѿ��మ�������ٽ���ˣ�
				break
		captainBase.cell.rlt_allyCheckResult( self.databaseID, statusID, () )

	def rlt_allySuccess( self, DBIDList ):
		"""
		Define method.
		��ݳɹ�������base����
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
		��ݳɹ�����ʼ
		"""
		self.rlt_allySuccess( DBIDList )
		DBIDList.append( self.databaseID )
		nameList = [relationItem.playerName for relationItem in self.friends.itervalues() if relationItem.playerDBID in DBIDList]
		nameList.append( self.getName() )
		strParam = str( tuple( [int( dbid ) for dbid in DBIDList] ) )	# ȥ�������͵�"L"������
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
			item.playerBase.receiveAllyTitle( self.allyTitle, csdefine.ALLY_TITILE_CHANGE_REASON_ADD )	# ��ݳɹ�������ֵܿ϶�����
		self._allyBroadcast( nameList )
		
		g_logger.allyListChangeLog( str(nameList) , str(DBIDList) )

	def rlt_joinNewAllyMember( self, newDBIDList ):
		"""
		Define method.
		����µĽ���ֵ�

		@param newDBIDList: �µĽ���ֵ�dbid�б�
		"""
		oldDBIDList = self.allyDict.keys()
		oldDBIDList.append( self.databaseID )
		oldNameList = [item.playerName for item in self.allyDict.itervalues()]
		oldNameList.append( self.getName() )
		newNameList = [relationItem.playerName for relationItem in self.friends.itervalues() if relationItem.playerDBID in newDBIDList]
		self.rlt_allySuccess( newDBIDList )
		oldAllyDBIDParam = str( tuple( [int( dbid ) for dbid in oldDBIDList] ) )	# ȥ�������͵�"L"������
		if len( newDBIDList ) == 1:	# ����ֻ��һ��Ԫ�ص��б���ʽת�����õ�����"('playerName',)"�ĸ�ʽ�����db������
			strDBIDParam = ("(" + "%i" + ")") % newDBIDList[0]
		else:
			strDBIDParam = str( tuple( [int( dbid ) for dbid in newDBIDList] ) )	# ȥ�������͵�"L"������
		relationStatus = csdefine.ROLE_RELATION_ALLY | csdefine.ROLE_RELATION_ALLY << RELATION_STATUS_HIGH_OFFSET
		commandString = """update `custom_Relation` set sm_relationStatus = sm_relationStatus | %i, sm_param = '%s'
							where (sm_playerDBID1 in %s and sm_playerDBID2 in %s)
							or (sm_playerDBID1 in %s and sm_playerDBID2 in %s);
						""" % ( relationStatus, self.allyTitle, oldAllyDBIDParam, strDBIDParam, strDBIDParam, oldAllyDBIDParam )
		BigWorld.executeRawDatabaseCommand( commandString, self._allyWriteDBCB )
		for item in self.allyDict.itervalues():
			item.playerBase.receiveAllyTitle( self.allyTitle, csdefine.ALLY_TITILE_CHANGE_REASON_ADD_MEMBER )	# ��ݳɹ�������ֵܿ϶�����
		self._allyBroadcast( oldNameList + newNameList )
		
		g_logger.allyListChangeLog( str(newNameList) , str(newDBIDList) )

	def _allyBroadcast( self, nameList ):
		"""
		��ҽ�ݵ�ȫ��֪ͨ

		[XX]��[YY]�ڷ����ջ�ֽ������������Ӵ�ͬ�����¡�
		"""
		sParam = "[" + cschannel_msgs.ROLE_INFO_9.join( nameList ) + "]"	# ����֪ͨ��Ϣ��ʽ
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JSGX_NEW_ALLY % sParam, [] )

	def _allyWriteDBCB( self, result, rows, errstr ):
		"""
		��ҽ��дdb�Ļص�
		"""
		if errstr:
			ERROR_MSG( "player( %s ) write to DB error:%s." % ( self.getName(), errstr ) )

	def rlt_changeAllyTitle( self, titleName ):
		"""
		Define method.
		��Ҹ��Ľ�ݳƺ�
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
		���ս�ݳƺ�
		"""
		self.allyTitle = titleName
		self.cell.onAllyTitleChanged( titleName )
		self.client.receiveAllyTitle( titleName, reason )
#		self.statusMessage( csstatus.TITLE_ADDED, titleName )

	def rlt_quitAlly( self ):
		"""
		Define method.
		����˳����

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
		�����˳���ݣ������Լ��Ľ�ݹ�ϵ����
		"""
		if len( self.allyDict ) <= 1:	# ����ǽ�ɢ��ݣ�Ҫ��cellapp��ʼ����
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
		�����ݹ�ϵ��
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

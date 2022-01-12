# -*- coding: gb18030 -*-
#

import time
from bwdebug import *
import csstatus
import csdefine
import csconst
import Define
import Const
import event.EventCenter as ECenter
import GUIFacade
from MessageBox import *
from guis.tooluis.inputbox.InputBox import InputBox
from config.client.msgboxtexts import Datas as mbmsgs
from gbref import rds
import Const

class RelationItem:
	"""
	"""
	def __init__( self, relationUID, playerName = "", level = 0, raceClass = 0, family = 0, tong = 0, online = 0, \
	friendlyValue =0, relationStatus = 0 , headTexture = "" ):
		"""
		"""
		self.relationUID = relationUID
		self.playerName		= playerName		# ��������
		self.online		= online	# �Ƿ����ߣ�TRUE ���� FALSE ������
		self.level		= level
		self.tong		= tong
		self.family		= family
		self.raceClass	= raceClass
		self.area 		= ""
		self.position   = ( 0.0, 0.0, 0.0 )
		self.friendlyValue = friendlyValue
		self.relationStatus = relationStatus
		self.headTexture = headTexture

class RoleRelation:
	"""
	"""
	def __init__( self ):
		self.relationDatas = {}	# like as { relationUID:RelationItem, ... }
		self.friends = {}			# like as { playerName:RelationItem, ..}
		self.sweetieDict = {}
		self.couple_lover = None
		self.foeDict = {}
		self.blackList = {}
		self.allyDict = {}			# ��ݹ�ϵ
		self.allyTitle = ""		# ��ݳƺ�

		# ʦͽϵͳ
		self.masterDict = {}		# keyΪdbid��valueΪRelationItem
		self.prenticeDict = {}
		self.masterEverDict = {}
		self.prenticeEverDict = {}
		self.requestTeachTime = 0.0	# ���һ�������ʦ��ʱ��

		# ȡ��ͬ���Ϊĳ�ֹ�ϵ��timerID�����磺���ͬ���Ϊ���ޣ�
		# �������ʱЧ�Է���Ӧ����Ҫ����������������ȡ��ͬ��ı�ǡ�
		self.cancelAgreeRelationTimer = 0

	def set_flags( self, old ):
		"""
		flags�ı�
		"""
		if old & ( 1 << csdefine.ROLE_FLAG_COUPLE_AGREE ) and self.cancelAgreeRelationTimer:
			BigWorld.cancelCallback( self.cancelAgreeRelationTimer )
			self.cancelAgreeRelationTimer = 0

	def addFriend( self, playerName ):
		"""
		"""
		if self.playerName == playerName:
			self.statusMessage( csstatus.FRIEND_NOT_ADD_SELF_FRIEND )
			return
		self.base.addFriend( playerName )

	def addBlacklist( self, playerName ):
		"""
		"""
		if self.playerName == playerName:
			self.statusMessage( csstatus.FRIEND_NOT_ADD_SELF_BLACKlIST )
			return
		if playerName in self.blackList:
			self.statusMessage( csstatus.BLACKLIST_NAME_REPEAT, playerName )
			return
		self.base.addBlacklist( playerName )

	def beAskedForFriend( self, playerName ):
		"""
		Define method.
		������Ӻ��ѡ�

		@param playerName : ����������������
		"""
		def notarize( id ) :
			result = False
			if id == RS_YES : result = True
			self.base.replyForFriendInvite( result )
		# "[%s]ϣ������Ϊ����һ����Ϸ�����Ƿ�ͬ�⣿"
		msg = mbmsgs[0x0141] % playerName
		showAutoHideMessage( 20.0, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )
		#showMessage( msg, "", MB_YES_NO, notarize )

	def rlt_offlineUpdate( self, relationUID ):
		"""
		Define method.
		�������ߣ�֪ͨ�ͻ��ˡ�

		@param relationUID:	���ߵĺ�������
		@type relationUID:	STRING
		"""
		#if self.friends.has_key( relationUID ):
		#	self.friends[ relationUID ].online = False
		#	self.statusMessage( csstatus.TEAM_TEAMMATER_IS_OFFLINE, playerName )
		relationItem = self.relationDatas[relationUID]
		relationItem.online = False
#		if relationItem.relationStatus&csdefine.ROLE_RELATION_FRIEND:
#			self.statusMessage( csstatus.FRIEND_IS_NOT_ONLINE, relationItem.playerName )
		ECenter.fireEvent( "EVT_ON_RELATION_OFFLINE", relationUID, 0 ) # ����֪ͨ

	def endRelationUpdate( self, relationUID, relationType ):
		"""
		Define method.
		������ϵ

		@param relationUID : ��ϵΨһid
		@type relationUID : UINT32
		@param relation : �����Ĺ�ϵ
		@type relation : UINT16
		"""
		relation = self.relationDatas.get( relationUID, None )
		if relation is None:return
		playerName = relation.playerName
		if relationType & csdefine.ROLE_RELATION_FRIEND:
			self.friends[playerName].friendlyValue = 0
			del self.friends[playerName]
		elif relationType & csdefine.ROLE_RELATION_SWEETIE:
			del self.sweetieDict[playerName]
		elif relationType & csdefine.ROLE_RELATION_COUPLE:
			self.couple_lover = None
		elif relationType & csdefine.ROLE_RELATION_BLACKLIST:
			del self.blackList[playerName]
		elif relationType & csdefine.ROLE_RELATION_FOE:
			del self.foeDict[playerName]
		elif relationType & csdefine.ROLE_RELATION_PRENTICE:
			del self.masterDict[playerName]
		elif relationType & csdefine.ROLE_RELATION_MASTER:
			del self.prenticeDict[playerName]
		elif relationType & csdefine.ROLE_RELATION_ALLY:
			del self.allyDict[playerName]
			if not self.hasAllyRelation():
				self.allyTitle = ""
		relation.relationStatus &= ~relationType
		if relation.relationStatus <= 0: #��ϵ��Ǳ���գ���ɾ��
			del self.relationDatas[relationUID]
		ECenter.fireEvent( "EVT_ON_ROLE_REMOVE_RELATION", relationUID, relationType )
		# ����relation�Թ�ϵ���д������������Ѳ����ڹ�ϵ����ô����������

	def addSweetie( self, playerName ):
		"""
		���������
		"""
		# ���ж��Ƿ��ں����б���
		if self.friends.has_key( playerName ):
			relationUID = self.friends[playerName].relationUID
			self.cell.addSweetie( relationUID )
		else :
			self.statusMessage( csstatus.SWEETIE_BE_FRIEND_BEFORE_SWEETIE )

	def rlt_receivePlayerInfo( self, relationUID, playerName, level, playerClass, playerTong, friendlyValue, headTextureID, relationStatus ):
		"""
		Define method.
		��ҵ�һ�ν������ߺ��ѡ����ˡ�������Ϣ�Ŀͻ��˽ӿ�

		@param playerName:		�������
		@type playerName:		STRING
		@param level	:		��ҵȼ�
		@type level		:		UINT8
		@param playerTong	:	��Ұ��
		@type playerTong	:	STRING
		@param playerClass	:	���ְҵ
		@type playerClass	:	INT32
		"""
		#DEBUG_MSG( "---->>>", relationUID, playerName, level, playerClass, playerTong, playerFamily, friendlyValue, relationStatus )
		online = True
		headTexture = self.getObjHeadTexture( headTextureID )
		relationItem = RelationItem( relationUID, playerName, level, playerClass, "", playerTong, online, friendlyValue, relationStatus,\
		 headTexture )
		self.relationDatas[relationUID] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_BLACKLIST:
			self.blackList[playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_FRIEND:
			self.friends[playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_SWEETIE:
			self.sweetieDict[playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_COUPLE:
			self.couple_lover = relationItem
		if relationStatus & csdefine.ROLE_RELATION_FOE:
			self.foeDict[playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_MASTER:#
			self.prenticeDict[playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_PRENTICE:
			self.masterDict[playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_ALLY:
			self.allyDict[playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_PRENTICE_EVER:
			self.masterEverDict[relationItem.playerName] = relationItem
			#self.prenticeEverDict[relationItem.playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_MASTER_EVER:
			self.prenticeEverDict[relationItem.playerName] = relationItem
			#self.masterEverDict[relationItem.playerName] = relationItem
		ECenter.fireEvent( "EVT_ON_ROLE_UPDATE_RELATION", relationUID, relationStatus )

	def rtf_receiveNameInfo( self, playerName, relationUID, friendlyValue, relationStatus ):
		"""
		Define method.
		���պ�����Ϣ�Ľӿڣ�����ڶԷ���������ʱ����Ӻ��ѵ��Է�������ʱ��
		���ڶԷ��������ʱ����Ϣ���µ������ͻ��ˡ�

		@param playerName:	�������
		@type playerName:	STRING
		"""
		DEBUG_MSG( "--->>>", playerName, relationUID, friendlyValue, relationStatus )
		relationItem = RelationItem( relationUID, playerName, friendlyValue= friendlyValue, relationStatus = relationStatus )
		self.relationDatas[relationUID] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_BLACKLIST:
			self.blackList[playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_FRIEND:
			self.friends[playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_SWEETIE:
			self.sweetieDict[playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_FOE:
			self.foeDict[playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_COUPLE:
			self.couple_lover = relationItem
		if relationStatus & csdefine.ROLE_RELATION_MASTER:
			self.prenticeDict[playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_PRENTICE:
			self.masterDict[playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_ALLY:
			self.allyDict[playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_PRENTICE_EVER:
			self.masterEverDict[relationItem.playerName] = relationItem
		if relationStatus & csdefine.ROLE_RELATION_MASTER_EVER:
			self.prenticeEverDict[relationItem.playerName] = relationItem
		ECenter.fireEvent( "EVT_ON_ROLE_UPDATE_RELATION", relationUID, relationStatus )

	def rlt_playerLogon( self, relationUID, level, raceClass, tong, headTextureID ):
		"""
		Define method.
		��ҽ������ߺ��ѡ����ˡ�������Ϣ�Ŀͻ��˽ӿ�
		"""
		relation = self.relationDatas[relationUID]
		relation.level = level
		relation.raceClass = raceClass
		relation.tong = tong
		relation.family = ""
		relation.online = True
		headTexture = self.getObjHeadTexture( headTextureID )
		relation.headTexture = headTexture
		relationStatus = relation.relationStatus
#		if not csdefine.ROLE_RELATION_FOE & relationStatus:
#			self.statusMessage( csstatus.RELATION_TARGET_LOGON, relation.playerName )
		ECenter.fireEvent( "EVT_ON_ROLE_UPDATE_RELATION", relationUID, relationStatus )

	def onShowWhisper( self, playerName, msg ):
		if not self.friends.has_key(playerName):
			self.statusMessage( csstatus.FRIEND_NOT_EXIST )
			return
		ECenter.fireEvent( "EVT_ON_FRIENDS_SHOW_WHISPER", playerName, msg )

	def removeFriend( self, relationUID ):
		"""
		�Ƴ�����
		"""
		def notarize( id ) :
			if id == RS_NO : return
			BigWorld.player().base.removeFriend( relationUID )
		# "���ɾ�����Ѻù�ϵ���Ѷ�Ҳ����������Ҫ��[%s]����ô��"
		msg = mbmsgs[0x0142] % self.relationDatas[relationUID].playerName
		showAutoHideMessage( 20.0, msg, "", MB_YES_NO, notarize )
		#showMessage( msg, "", MB_YES_NO, notarize )

	def removeBlackList( self, relationUID ):
		"""
		�Ƴ�������
		"""
		def notarize( id ) :
			result = False
			if id == RS_YES :
				result = True
				BigWorld.player().base.removeBlacklist( relationUID )
		# "�Ƿ�ɾ��������[%s]��"
		msg = mbmsgs[0x0143] % self.relationDatas[relationUID].playerName
		showAutoHideMessage( 20.0, msg, "", MB_YES_NO, notarize )
		#showMessage( msg, "", MB_YES_NO, notarize )

	def beInvitedSweetie( self, relationUID ):
		"""
		Define method.
		������ύ����

		@param relationUID����������Ҫ��Ĺ�ϵ
		"""
		try:
			inviterName = self.relationDatas[relationUID].playerName
		except KeyError:
			ERROR_MSG( "relationDatas key error:%i." % relationUID )
			return
		if inviterName not in self.friends:
			ERROR_MSG( "player( %s ) dont in friends." % inviterName )
			return

		def notarize( id ) :
			result = False
			if id == RS_YES : result = True
			self.base.replyForSweetieInvite( result )
		# "%s �������Ϊ���ˣ����Ƿ���ܣ�"
		msg = mbmsgs[0x0144] % inviterName
		showAutoHideMessage( 20.0, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )
		#showMessage( msg, "", MB_YES_NO, notarize )

	def askForMarriage( self, relationUID ):
		"""
		Define method.
		ѯ���Ƿ�ͬ��ͶԷ����

		@param relationUID : �ͶԷ���ϵ��Ψһ��ʶ
		@type relationUID : UINT32
		"""
		loverName = self.relationDatas[relationUID].playerName
		def notarize( id ) :
			result = False
			if id == RS_YES :
				result = True
				self.cancelAgreeRelationTimer = BigWorld.callback( 20.0, self.cell.cancelAgreeCouple )
			BigWorld.player().couple_replyForMarriage( result )
		# "%s �������Ϊ���ޣ����Ƿ���ܣ�"
		msg = mbmsgs[0x0145] % loverName
		showAutoHideMessage( 20.0, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )
		#showMessage( msg, "", MB_YES_NO, notarize )

	def couple_replyForMarriage( self, reply ):
		"""
		�ظ�������ĺ�����

		@param reply:	True��ʾͬ���飬False��ʾ��ͬ��
		@type reply:	BOOL
		"""
		#if reply:
		#	self.couple_timerID = BigWorld.callback( COUPLE_AGREEMENT_TIME_OUT, self.couple_cancel )
		self.cell.couple_replyForMarriage( reply )

	def couple_requestDivorce( self ):
		"""
		Define method.
		ѯ���Ƿ�ͬ�����Ľӿ�
		"""
		def notarize( id ) :
			result = False
			if id == RS_YES : result = True
			self.cell.couple_replyForDivorce( result )
		# "�Ƿ�ͬ�����"
		showAutoHideMessage( 20.0, 0x0146, "", MB_YES_NO, notarize )
		#showMessage( msg, "", MB_YES_NO, notarize )

	def couple_requestForceDivorce( self ):
		"""
		Define method.
		ѯ������Ƿ�ȷ��ǿ�����

		@param entityID : npc id
		@type entityID : OBJECT_ID
		"""
		def notarize( id ) :
			result = False
			if id == RS_YES : result = True
			BigWorld.player().couple_replyForceDivorce( result )
		# "�������ǿ������������Ч������Ҫ����50�����������ѣ���ȷ��Ҫ����"
		showAutoHideMessage( 20.0, 0x0147, "", MB_YES_NO, notarize )
		#showMessage( msg, "", MB_YES_NO, notarize )

	def couple_replyForceDivorce( self, reply ):
		"""
		��ҵ��������Ӧ��

		param reply:����Ƿ�ͬ�����
		type reply:	BOOL
		"""
		if not reply:	# �����Ҳ�ͬ�⣬ʲô������
			return
		else:
			self.cell.couple_forceDivorce( self.couple_lover.playerName )

	def rlt_receiveAreaInfo( self, relationUID, spaceType, position, lineNumber ):
		"""
		Define method.
		��ҽ������˵�ǰ���ڵ����Ľӿ�

		@param relationUID: ��ϵ��Ψһid
		@type relationUID:	UINT32
		@param spaceType:	��ͼ��
		@type spaceType:	STRING
		@param position:	���position
		@type position:		POSITION
		@param lineNumber:	�ڼ���
		@type lineNumber:	UINT16
		"""
		self.relationDatas[relationUID].area = spaceType
		ECenter.fireEvent( "EVT_ON_RELATION_AREA_UDATE", relationUID, spaceType, position, lineNumber )

	def friendlyValueChanged( self, relationUID, friendlyValue ):
		"""
		Define method.
		��Һ��Ѷȱ仯��
		"""
		self.relationDatas[relationUID].friendlyValue = friendlyValue
		ECenter.fireEvent( "EVT_ON_RELATION_FRIENDLY_UDATE", relationUID, friendlyValue )

	def rlt_onLevelChanged( self, relationUID, level ):
		"""
		Define method.
		�й�ϵ����Ҽ���ı�
		"""
		self.relationDatas[relationUID].level = level
		ECenter.fireEvent( "EVT_ON_RELATION_LEVEL_UDATE", relationUID, level )

	def rtf_relationUpdate( self, relationUID, relation ):
		"""
		Define method.
		��һ���¹�ϵ

		relation�������ǶԷ��ڴ˹�ϵ�е����
		"""
		relationItem = self.relationDatas[relationUID]
		relationItem.relationStatus |= relation
		if relation & csdefine.ROLE_RELATION_SWEETIE:
			self.sweetieDict[relationItem.playerName] = relationItem
			self.statusMessage( csstatus.SWEETIE_ADD_SUCCESS, relationItem.playerName )
		if relation & csdefine.ROLE_RELATION_FRIEND:
			self.friends[relationItem.playerName] = relationItem
		if relation & csdefine.ROLE_RELATION_BLACKLIST:
			self.blackList[relationItem.playerName] = relationItem
		if relation & csdefine.ROLE_RELATION_FOE:
			self.foeDict[relationItem.playerName] = relationItem
		if relation & csdefine.ROLE_RELATION_COUPLE:
			self.couple_lover = relationItem
		if relation & csdefine.ROLE_RELATION_ALLY:
			self.allyDict[relationItem.playerName] = relationItem
		if relation & csdefine.ROLE_RELATION_PRENTICE_EVER:
			del self.prenticeDict[relationItem.playerName]
			self.prenticeEverDict[relationItem.playerName] = relationItem
		if relation & csdefine.ROLE_RELATION_MASTER_EVER:
			del self.masterDict[relationItem.playerName]
			self.masterEverDict[relationItem.playerName] = relationItem
		ECenter.fireEvent( "EVT_ON_ROLE_UPDATE_RELATION", relationUID, relation )

	def couple_divorceSuccess( self ):
		"""
		Define method.
		�ɹ����
		"""
		BigWorld.cancelCallback( self.couple_timerID )
		if self.couple_lover:	# �п���������ҵ�½ʱ���ֶԷ�ǿ����飬��ʱcouple_loverΪNone
			ECenter.fireEvent( "EVT_ON_COUPLE_DIVORCE_SUCCESS" )
			self.couple_lover = None

	def couple_marrySuccess( self, relationUID ):
		"""
		Define method.
		���ɹ������ÿͻ�������
		"""
		relationItem = self.relationDatas[relationUID]
		self.couple_lover = relationItem

	# ------------------------------------------------------------------------
	# ʦͽ��ϵ
	# ------------------------------------------------------------------------
	def isPrentice( self ):
		"""
		�Ƿ�ͽ��
		"""
		return len( self.masterDict ) > 0

	def isMaster( self ):
		"""
		�Ƿ�ʦ��
		"""
		return len( self.prenticeDict ) > 0

	def teach_requestDisband( self ):
		"""
		Define method.
		֪ͨ�������ʦͽ��ϵ�Ķ����б��Ա����ѡ������ϵ�Ķ���
		"""
		if self.isPrentice():	# ��Ϊͽ��ֻ��һ��ʦ��,������ʾ��
			if not self.masterDict.values():return
			masterItem = self.masterDict.values()[0]
			masterName = masterItem.playerName
			def query( rs_id ):
				if rs_id == RS_YES:
					self.base.teach_requestDisband( masterName )
			# "�Ƿ�����%s��ʦͽ��ϵ?"
			showAutoHideMessage( 20.0, mbmsgs[0x0148] % masterName, "", MB_YES_NO, query, gstStatus = Define.GST_IN_WORLD )
			#showMessage( "�Ƿ�����%s��ʦͽ��ϵ?" % masterName, "", MB_OK_CANCEL, query )
		else:
			#DEBUG_MSG( "---->>>self.prenticeDict", self.prenticeDict )
			talkEntity = GUIFacade.getGossipTarget()
			ECenter.fireEvent( "EVT_ON_UNCHAIN_PRENTICE", talkEntity.id )

	def teach_receiveTeachInfo( self, record, teacherOrPrentice ):
		"""
		Define method.
		���հ�ʦ��������ʦͽ����

		@param record : list
		@type record : PYTHON
		@param teacherOrPrentice : Ϊ1��ʾ��ʦ����Ϊ0��ͽ��
		@type teacherOrPrentice : INT32
		"""
		if teacherOrPrentice == 1:
			ECenter.fireEvent( "EVT_ON_TOGGLE_ADD_MASTER_INFO", record )
		elif teacherOrPrentice == 0:
			ECenter.fireEvent( "EVT_ON_TOGGLE_ADD_PRENTICE_INFO", record )

	def showTeachInfo( self ):
		ECenter.fireEvent( "EVT_ON_TOGGLE_SEARCH_MASTER_AND_PRENTICE" )
#		currTarget = GUIFacade.getGossipTarget()
#		ECenter.fireEvent( "EVT_ON_TOGGLE_SEARCH_PRENTICE", currTarget )

	def getMasterName( self ):
		"""
		���ʦ��������
		"""
		if len( self.masterDict ) == 0:	# �п���ʦ�������ݻ�û���¹���
			return ""
		return self.masterDict.keys()[0]

	def teach_remoteTeachReply( self, agree ):
		"""
		ʦ���ظ���ʦ����

		@param agree : �Ƿ�ͬ��
		@type agree : BOOL
		@param prenticeName : ͽ������
		@type prenticeName : STRING
		"""
		if self.level >= csconst.TEACH_MASTER_MIN_LEVEL:
			self.base.teach_masterRemoteTeachReply( agree )
		else:
			self.base.teach_prenticeRemoteTeachReply( agree )

	def teach_queryTeachInfo( self ):
		"""
		��ѯʦͽ�������еİ�ʦ��Ϣ

		@param startIndex : ��ѯ�Ŀ�ʼindex
		@type startIndex : INT32
		@param endIndex : ��ѯ�Ľ���λ��
		@type endIndex : INT32
		"""
		self.cell.teach_queryTeachInfo()

	def teach_requestTeach( self, playerDBID ):
		"""
		�����Ϊʦͽ
		"""
		if playerDBID == self.databaseID:
			return
		if self.level >= csconst.TEACH_MASTER_MIN_LEVEL:
			self.requestTeachPrentice( playerDBID )
		elif self.level < csconst.TEACH_PRENTICE_LOWER_LIMIT:
			self.statusMessage( csstatus.TEACH_PLAYER_LEVEL_LACK, csconst.TEACH_MASTER_MIN_LEVEL, csconst.TEACH_END_TEACH_LEAST_LEVEL, csconst.TEACH_PRENTICE_LOWER_LIMIT )
		else:
			self.teach_requestBeTeached( playerDBID )

	def teach_requestBeTeached( self, masterDBID ):
		"""
		�����ʦ

		@param masterName : ʦ��������
		@type masterName : STRING
		"""
		if self.level < csconst.TEACH_PRENTICE_LOWER_LIMIT or self.level > csconst.TEACH_PRENTICE_UPPER_LIMIT:
			self.statusMessage( csstatus.TEACH_PLAYER_LEVEL_LACK )
			return
		if self.isPrentice():
			self.statusMessage( csstatus.TEACH_MASTER_EXIST )
			return
		now = time.time()
		if self.requestTeachTime + 7200 > now:
			self.statusMessage( csstatus.TEACH_REQUEST_TOO_MUCH )
			return
		self.requestTeachTime = now
		self.base.teach_requestBeTeached( masterDBID )
#		self.statusMessage( csstatus.TEACH_REQUEST_HAS_SENT )

	def prenticeRequestBeTeached( self, prenticeName ):
		"""
		Define method.
		��������ʦ

		@param prenticeName : �����ʦ��ҵ�����
		@type prenticeName : STRING
		"""
		def notarize( id ):
			if id == RS_YES:
				result = True
			else:
				result = False
			self.teach_remoteTeachReply( result )
		# "%sϣ���ܰ���Ϊʦ��������Ľ̵������Ƿ���ܣ� "
		msg =  mbmsgs[0x0149] % prenticeName
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def requestTeachPrentice( self, playerDBID ):
		"""
		������ͽ

		@param playerDBID : Ŀ����ҵ�dbid
		"""
		if self.level < csconst.TEACH_MASTER_MIN_LEVEL:
			self.statusMessage( csstatus.TEACH_PLAYER_LEVEL_LACK )
			return
		if len( self.prenticeDict ) > csconst.TEACH_PRENTICE_MAX_COUNT:
			self.statusMessage( csstatus.TEACH_PRENTICE_NUM_FULL )
			return
		now = time.time()
		if self.requestTeachTime + 7200 > now:
			self.statusMessage( csstatus.TEACH_REQUEST_PRENTICE_TOO_MUCH )
			return
		self.requestTeachTime = now
		self.base.requestTeachPrentice( playerDBID )
#		self.statusMessage( csstatus.TEACH_REQUEST_HAS_SENT )

	def masterRequestTeach( self, masterName ):
		"""
		Define method.
		���������ͽ��
		"""
		def notarize( id ):
			if id == RS_YES:
				result = True
			else:
				result = False
			self.teach_remoteTeachReply( result )
		# "%sϣ��������Ϊͽ�����Ƿ���ܣ� "
		msg =  mbmsgs[0x0156] % masterName
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def onRealtionTongChanged( self, relationUID, tongName ):
		"""
		Define method
		"""
		relationItem = self.relationDatas.get( relationUID, None )
		if relationItem is None:return
		relationItem.tong = tongName
		ECenter.fireEvent( "EVT_ON_RELATION_TONGNAME_CHANGED", relationUID, tongName )
		
	def onReceiveTongGrade( self, relationUID, tong_grade ) :
		"""
		Define method
		"""
		ECenter.fireEvent( "EVT_ON_RELATION_TONG_RECEIVE_TONG_GRADE", relationUID, tong_grade )

	# ----------------------------------------------------------------------------
	# ��ݹ�ϵ
	# ----------------------------------------------------------------------------
	def receiveAllyTitle( self, titleString, reason ):
		"""
		Define method.
		������ҳƺ�����

		@param titleString : �ƺ��ַ�����STRING
		"""
		if reason != csdefine.ALLY_TITILE_CHANGE_REASON_INIT:
			self.statusMessage( csstatus.TITLE_ADDED, titleString )
			if self.allyTitle != "":
				self.statusMessage( csstatus.ALLY_CHANGE_TITLE_TO, titleString )
		self.allyTitle = titleString
		ECenter.fireEvent( "EVT_ON_ROLE_ALLY_TITLE_CHANGED", csdefine.TITLE_ALLY_ID, titleString )

	def hasAllyRelation( self ):
		return len( self.allyDict ) > 0

	def rlt_askForStartAlly( self ):
		"""
		Define method.
		ѯ���Ƿ�ȷ����ʼ���
		"""
		def notarize( id ) :
			result = False
			if id == RS_YES:
				if not self.isJoinTeam():
					self.statusMessage( csstatus.CANNOT_ALLY_NO_TEAM )
					DEBUG_MSG( "��Ҫ��ݾ�����ֵ����һ��������һ���˲��ܽ�ݡ�111" )
					return
				if not self.isCaptain():
					self.statusMessage( csstatus.CANNOT_ALLY_NO_TEAM_CAPTAIN )
					DEBUG_MSG( "�öӳ�������˵�ɣ���������һȺ��һ������̫�����ˣ�" )
					return
				if self.money < csconst.RELATION_ALLY_COST:
					self.statusMessage( csstatus.CANNOT_ALLY_NO_MONEY, csconst.RELATION_ALLY_COST/10000 )
					DEBUG_MSG( "�������ֽ����ʽ��Ҫ����%i�������Ͻ�Ǯ���㣡" % ( csconst.RELATION_ALLY_COST/10000 ) )
					return
				for itemInfo in csconst.RELATION_ALLY_NEED_ITEMS:
					if not self.checkItemFromNKCK_( itemInfo[0], itemInfo[1] ):
						self.statusMessage( csstatus.CANNOT_ALLY_NO_ITEM )
						DEBUG_MSG( "�����ʽ��Ҫ�ջ�ֽ��ͬ���һ��ƣ���������Ʒ���㡣��ֽ�ڷ����ӻ��̹����һ����ڷ�����̲���ۡ�" )
						return
				self.cell.rlt_requestAlly()
		msg = mbmsgs[0x014a] % (csconst.RELATION_ALLY_COST/10000)
		showAutoHideMessage( 30.0, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def rlt_askForJoinAllyMember( self ):
		"""
		Define method.
		ѯ���Ƿ�ȷ�������µĽ�ݳ�Ա
		"""
		def notarize( id ) :
			result = False
			if id == RS_YES:
				if not self.isJoinTeam():
					self.statusMessage( csstatus.CANNOT_ALLY_NO_TEAM )
					DEBUG_MSG( "��Ҫ��ݾ�����ֵ����һ��������һ���˲��ܽ�ݡ�111" )
					return
				if not self.isCaptain():
					self.statusMessage( csstatus.CANNOT_ALLY_NO_TEAM_CAPTAIN )
					DEBUG_MSG( "�öӳ�������˵�ɣ���������һȺ��һ������̫�����ˣ�" )
					return
				if self.money < csconst.RELATION_ALLY_COST:
					self.statusMessage( csstatus.CANNOT_ALLY_NO_MONEY, csconst.RELATION_ALLY_NEW_COST/10000 )
					DEBUG_MSG( "�������ֽ����ʽ��Ҫ����%i�������Ͻ�Ǯ���㣡" % ( csconst.RELATION_ALLY_COST/10000 ) )
					return
				for itemInfo in csconst.RELATION_ALLY_NEED_ITEMS:
					if not self.checkItemFromNKCK_( itemInfo[0], itemInfo[1] ):
						self.statusMessage( csstatus.CANNOT_ALLY_NO_ITEM )
						DEBUG_MSG( "�����ʽ��Ҫ�ջ�ֽ��ͬ���һ��ƣ���������Ʒ���㡣��ֽ�ڷ����ӻ��̹����һ����ڷ�����̲���ۡ�" )
						return
				self.cell.rlt_newMemberJoinAlly()
		msg = mbmsgs[0x014d] % ( csconst.RELATION_ALLY_NEW_COST/10000)
		showAutoHideMessage( 30.0, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def rlt_askForChangeAllyTitle( self ):
		"""
		Define mehtod.
		ѯ������Ƿ���Ҫ������

		��ʾ�ı�������������µ�����
		"""
		DEBUG_MSG( "��ʾ�ı�������������µ�����" )
		def callback( res, text ):
			title = mbmsgs[0x0c22]
			if text == "" : return
			elif len( text ) > 14 :	# ������ƺϷ��Լ��
				showAutoHideMessage( 3.0, 0x014f, title )
				return
			elif self.__isHasDigit( text ):#��������
				# "��������ֻ���ɺ��ֺ���ĸ��ɣ�"
				showAutoHideMessage( 3.0, 0x0151, title )
				return
			elif not rds.wordsProfanity.isPureString( text ) :
				# "���Ʋ��Ϸ���"
				showAutoHideMessage( 3.0, 0x0152, title )
				return
			elif rds.wordsProfanity.searchNameProfanity( text ) is not None :
				# "����������н��ôʻ�!"
				showAutoHideMessage( 3.0, 0x0153, title )
				return
			self.cell.rlt_changeAllyTitle( text )
		InputBox().show( mbmsgs[0x014e], callback )

	def __isHasDigit( self, text ):
		for letter in text:
			if letter.isdigit():
				return True
			else:
				continue
		return False

	def rlt_askForQuitAlly( self ):
		"""
		Define method.
		ѯ������Ƿ�ȷ��Ҫ�����ݹ�ϵ
		"""
		def notarize( id ) :
			result = False
			if id == RS_YES:
				if self.isJoinTeam():
					self.statusMessage( csstatus.ALLY_TEAM_CANNOT_QUIT )
					DEBUG_MSG( "������������»���һ�������ĺðɣ����˳����顣" )
					return
				self.cell.rlt_quitAlly()
		showAutoHideMessage( 30.0, mbmsgs[0x0154], "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def teach_prenticeCall( self, prenticeName ):
		"""
		Define method.
		ͽ�������ٻ�ʦ��
		"""
		def notarize( id ) :
			if id == RS_YES:
				result = True
			else:
				result = False
			self.cell.teach_respondPrenticeCall( result )
		msg = mbmsgs[0x0155] % prenticeName
		showAutoHideMessage( 20.0, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

		DEBUG_MSG( "ѯ��ʦ���Ƿ���Ӧͽ��( %s )�ٻ���" % prenticeName )

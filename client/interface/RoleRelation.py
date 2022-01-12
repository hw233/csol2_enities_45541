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
		self.playerName		= playerName		# 好友名称
		self.online		= online	# 是否在线：TRUE 在线 FALSE 不在线
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
		self.allyDict = {}			# 结拜关系
		self.allyTitle = ""		# 结拜称号

		# 师徒系统
		self.masterDict = {}		# key为dbid，value为RelationItem
		self.prenticeDict = {}
		self.masterEverDict = {}
		self.prenticeEverDict = {}
		self.requestTeachTime = 0.0	# 最后一次请求拜师的时间

		# 取消同意结为某种关系的timerID，例如：玩家同意结为夫妻，
		# 如果过了时效对方无应答，需要主动触发到服务器取消同意的标记。
		self.cancelAgreeRelationTimer = 0

	def set_flags( self, old ):
		"""
		flags改变
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
		被请求加好友。

		@param playerName : 发起请求的玩家名字
		"""
		def notarize( id ) :
			result = False
			if id == RS_YES : result = True
			self.base.replyForFriendInvite( result )
		# "[%s]希望加你为好友一起游戏，您是否同意？"
		msg = mbmsgs[0x0141] % playerName
		showAutoHideMessage( 20.0, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )
		#showMessage( msg, "", MB_YES_NO, notarize )

	def rlt_offlineUpdate( self, relationUID ):
		"""
		Define method.
		好友下线，通知客户端。

		@param relationUID:	下线的好友名字
		@type relationUID:	STRING
		"""
		#if self.friends.has_key( relationUID ):
		#	self.friends[ relationUID ].online = False
		#	self.statusMessage( csstatus.TEAM_TEAMMATER_IS_OFFLINE, playerName )
		relationItem = self.relationDatas[relationUID]
		relationItem.online = False
#		if relationItem.relationStatus&csdefine.ROLE_RELATION_FRIEND:
#			self.statusMessage( csstatus.FRIEND_IS_NOT_ONLINE, relationItem.playerName )
		ECenter.fireEvent( "EVT_ON_RELATION_OFFLINE", relationUID, 0 ) # 下线通知

	def endRelationUpdate( self, relationUID, relationType ):
		"""
		Define method.
		结束关系

		@param relationUID : 关系唯一id
		@type relationUID : UINT32
		@param relation : 结束的关系
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
		if relation.relationStatus <= 0: #关系标记被清空，则删除
			del self.relationDatas[relationUID]
		ECenter.fireEvent( "EVT_ON_ROLE_REMOVE_RELATION", relationUID, relationType )
		# 根据relation对关系进行处理，如果处理后已不存在关系，那么清除相关数据

	def addSweetie( self, playerName ):
		"""
		申请加恋人
		"""
		# 先判断是否在好友列表中
		if self.friends.has_key( playerName ):
			relationUID = self.friends[playerName].relationUID
			self.cell.addSweetie( relationUID )
		else :
			self.statusMessage( csstatus.SWEETIE_BE_FRIEND_BEFORE_SWEETIE )

	def rlt_receivePlayerInfo( self, relationUID, playerName, level, playerClass, playerTong, friendlyValue, headTextureID, relationStatus ):
		"""
		Define method.
		玩家第一次接收在线好友、恋人、夫妻信息的客户端接口

		@param playerName:		玩家名称
		@type playerName:		STRING
		@param level	:		玩家等级
		@type level		:		UINT8
		@param playerTong	:	玩家帮会
		@type playerTong	:	STRING
		@param playerClass	:	玩家职业
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
		接收好友信息的接口，玩家在对方黑名单中时，或加好友但对方不在线时。
		用于对方玩家上线时把信息更新到己方客户端。

		@param playerName:	玩家名字
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
		玩家接收在线好友、恋人、夫妻信息的客户端接口
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
		移除好友
		"""
		def notarize( id ) :
			if id == RS_NO : return
			BigWorld.player().base.removeFriend( relationUID )
		# "如果删除了友好关系好友度也会清除，真的要和[%s]决裂么？"
		msg = mbmsgs[0x0142] % self.relationDatas[relationUID].playerName
		showAutoHideMessage( 20.0, msg, "", MB_YES_NO, notarize )
		#showMessage( msg, "", MB_YES_NO, notarize )

	def removeBlackList( self, relationUID ):
		"""
		移除黑名单
		"""
		def notarize( id ) :
			result = False
			if id == RS_YES :
				result = True
				BigWorld.player().base.removeBlacklist( relationUID )
		# "是否删除黑名单[%s]？"
		msg = mbmsgs[0x0143] % self.relationDatas[relationUID].playerName
		showAutoHideMessage( 20.0, msg, "", MB_YES_NO, notarize )
		#showMessage( msg, "", MB_YES_NO, notarize )

	def beInvitedSweetie( self, relationUID ):
		"""
		Define method.
		被邀请结交恋人

		@param relationUID：发起恋人要请的关系
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
		# "%s 邀请你成为恋人，你是否接受？"
		msg = mbmsgs[0x0144] % inviterName
		showAutoHideMessage( 20.0, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )
		#showMessage( msg, "", MB_YES_NO, notarize )

	def askForMarriage( self, relationUID ):
		"""
		Define method.
		询问是否同意和对方结婚

		@param relationUID : 和对方关系的唯一标识
		@type relationUID : UINT32
		"""
		loverName = self.relationDatas[relationUID].playerName
		def notarize( id ) :
			result = False
			if id == RS_YES :
				result = True
				self.cancelAgreeRelationTimer = BigWorld.callback( 20.0, self.cell.cancelAgreeCouple )
			BigWorld.player().couple_replyForMarriage( result )
		# "%s 邀请你成为夫妻，你是否接受？"
		msg = mbmsgs[0x0145] % loverName
		showAutoHideMessage( 20.0, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )
		#showMessage( msg, "", MB_YES_NO, notarize )

	def couple_replyForMarriage( self, reply ):
		"""
		回复请求结婚的函数。

		@param reply:	True表示同意结婚，False表示不同意
		@type reply:	BOOL
		"""
		#if reply:
		#	self.couple_timerID = BigWorld.callback( COUPLE_AGREEMENT_TIME_OUT, self.couple_cancel )
		self.cell.couple_replyForMarriage( reply )

	def couple_requestDivorce( self ):
		"""
		Define method.
		询问是否同意离婚的接口
		"""
		def notarize( id ) :
			result = False
			if id == RS_YES : result = True
			self.cell.couple_replyForDivorce( result )
		# "是否同意离婚"
		showAutoHideMessage( 20.0, 0x0146, "", MB_YES_NO, notarize )
		#showMessage( msg, "", MB_YES_NO, notarize )

	def couple_requestForceDivorce( self ):
		"""
		Define method.
		询问玩家是否确定强制离婚

		@param entityID : npc id
		@type entityID : OBJECT_ID
		"""
		def notarize( id ) :
			result = False
			if id == RS_YES : result = True
			BigWorld.player().couple_replyForceDivorce( result )
		# "单方面的强制离婚可马上生效，但需要付出50金的离婚手续费，你确定要离吗？"
		showAutoHideMessage( 20.0, 0x0147, "", MB_YES_NO, notarize )
		#showMessage( msg, "", MB_YES_NO, notarize )

	def couple_replyForceDivorce( self, reply ):
		"""
		玩家单方面离婚应答

		param reply:玩家是否同意离婚
		type reply:	BOOL
		"""
		if not reply:	# 如果玩家不同意，什么都不做
			return
		else:
			self.cell.couple_forceDivorce( self.couple_lover.playerName )

	def rlt_receiveAreaInfo( self, relationUID, spaceType, position, lineNumber ):
		"""
		Define method.
		玩家接收恋人当前所在地区的接口

		@param relationUID: 关系的唯一id
		@type relationUID:	UINT32
		@param spaceType:	地图名
		@type spaceType:	STRING
		@param position:	玩家position
		@type position:		POSITION
		@param lineNumber:	在几线
		@type lineNumber:	UINT16
		"""
		self.relationDatas[relationUID].area = spaceType
		ECenter.fireEvent( "EVT_ON_RELATION_AREA_UDATE", relationUID, spaceType, position, lineNumber )

	def friendlyValueChanged( self, relationUID, friendlyValue ):
		"""
		Define method.
		玩家好友度变化了
		"""
		self.relationDatas[relationUID].friendlyValue = friendlyValue
		ECenter.fireEvent( "EVT_ON_RELATION_FRIENDLY_UDATE", relationUID, friendlyValue )

	def rlt_onLevelChanged( self, relationUID, level ):
		"""
		Define method.
		有关系的玩家级别改变
		"""
		self.relationDatas[relationUID].level = level
		ECenter.fireEvent( "EVT_ON_RELATION_LEVEL_UDATE", relationUID, level )

	def rtf_relationUpdate( self, relationUID, relation ):
		"""
		Define method.
		玩家获得新关系

		relation描述的是对方在此关系中的身份
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
		成功离婚
		"""
		BigWorld.cancelCallback( self.couple_timerID )
		if self.couple_lover:	# 有可能是在玩家登陆时发现对方强制离婚，此时couple_lover为None
			ECenter.fireEvent( "EVT_ON_COUPLE_DIVORCE_SUCCESS" )
			self.couple_lover = None

	def couple_marrySuccess( self, relationUID ):
		"""
		Define method.
		结婚成功，设置客户端数据
		"""
		relationItem = self.relationDatas[relationUID]
		self.couple_lover = relationItem

	# ------------------------------------------------------------------------
	# 师徒关系
	# ------------------------------------------------------------------------
	def isPrentice( self ):
		"""
		是否徒弟
		"""
		return len( self.masterDict ) > 0

	def isMaster( self ):
		"""
		是否师父
		"""
		return len( self.prenticeDict ) > 0

	def teach_requestDisband( self ):
		"""
		Define method.
		通知弹出解除师徒关系的对象列表，以便玩家选择解除关系的对象
		"""
		if self.isPrentice():	# 因为徒弟只有一个师傅,给个提示即
			if not self.masterDict.values():return
			masterItem = self.masterDict.values()[0]
			masterName = masterItem.playerName
			def query( rs_id ):
				if rs_id == RS_YES:
					self.base.teach_requestDisband( masterName )
			# "是否解除与%s的师徒关系?"
			showAutoHideMessage( 20.0, mbmsgs[0x0148] % masterName, "", MB_YES_NO, query, gstStatus = Define.GST_IN_WORLD )
			#showMessage( "是否解除与%s的师徒关系?" % masterName, "", MB_OK_CANCEL, query )
		else:
			#DEBUG_MSG( "---->>>self.prenticeDict", self.prenticeDict )
			talkEntity = GUIFacade.getGossipTarget()
			ECenter.fireEvent( "EVT_ON_UNCHAIN_PRENTICE", talkEntity.id )

	def teach_receiveTeachInfo( self, record, teacherOrPrentice ):
		"""
		Define method.
		接收拜师管理器的师徒数据

		@param record : list
		@type record : PYTHON
		@param teacherOrPrentice : 为1表示是师傅，为0是徒弟
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
		获得师父的名字
		"""
		if len( self.masterDict ) == 0:	# 有可能师父的数据还没更新过来
			return ""
		return self.masterDict.keys()[0]

	def teach_remoteTeachReply( self, agree ):
		"""
		师父回复拜师邀请

		@param agree : 是否同意
		@type agree : BOOL
		@param prenticeName : 徒弟名字
		@type prenticeName : STRING
		"""
		if self.level >= csconst.TEACH_MASTER_MIN_LEVEL:
			self.base.teach_masterRemoteTeachReply( agree )
		else:
			self.base.teach_prenticeRemoteTeachReply( agree )

	def teach_queryTeachInfo( self ):
		"""
		查询师徒管理器中的拜师信息

		@param startIndex : 查询的开始index
		@type startIndex : INT32
		@param endIndex : 查询的结束位置
		@type endIndex : INT32
		"""
		self.cell.teach_queryTeachInfo()

	def teach_requestTeach( self, playerDBID ):
		"""
		请求结为师徒
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
		请求拜师

		@param masterName : 师父的名字
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
		玩家请求拜师

		@param prenticeName : 请求拜师玩家的名字
		@type prenticeName : STRING
		"""
		def notarize( id ):
			if id == RS_YES:
				result = True
			else:
				result = False
			self.teach_remoteTeachReply( result )
		# "%s希望能拜你为师，接受你的教导，你是否接受？ "
		msg =  mbmsgs[0x0149] % prenticeName
		showAutoHideMessage( 30, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def requestTeachPrentice( self, playerDBID ):
		"""
		请求收徒

		@param playerDBID : 目标玩家的dbid
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
		玩家请求收徒。
		"""
		def notarize( id ):
			if id == RS_YES:
				result = True
			else:
				result = False
			self.teach_remoteTeachReply( result )
		# "%s希望能收你为徒，你是否接受？ "
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
	# 结拜关系
	# ----------------------------------------------------------------------------
	def receiveAllyTitle( self, titleString, reason ):
		"""
		Define method.
		接收玩家称号名称

		@param titleString : 称号字符串，STRING
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
		询问是否确定开始结拜
		"""
		def notarize( id ) :
			result = False
			if id == RS_YES:
				if not self.isJoinTeam():
					self.statusMessage( csstatus.CANNOT_ALLY_NO_TEAM )
					DEBUG_MSG( "想要结拜就你的兄弟组队一起来啊！一个人不能结拜。111" )
					return
				if not self.isCaptain():
					self.statusMessage( csstatus.CANNOT_ALLY_NO_TEAM_CAPTAIN )
					DEBUG_MSG( "让队长来和我说吧，你们这样一群人一起来，太混乱了！" )
					return
				if self.money < csconst.RELATION_ALLY_COST:
					self.statusMessage( csstatus.CANNOT_ALLY_NO_MONEY, csconst.RELATION_ALLY_COST/10000 )
					DEBUG_MSG( "帮你主持结拜仪式需要花费%i金，你身上金钱不足！" % ( csconst.RELATION_ALLY_COST/10000 ) )
					return
				for itemInfo in csconst.RELATION_ALLY_NEED_ITEMS:
					if not self.checkItemFromNKCK_( itemInfo[0], itemInfo[1] ):
						self.statusMessage( csstatus.CANNOT_ALLY_NO_ITEM )
						DEBUG_MSG( "结拜仪式需要烧黄纸，同饮桃花酒，你身上物品不足。黄纸在凤鸣杂货商购买，桃花酒在凤鸣海滩有售。" )
						return
				self.cell.rlt_requestAlly()
		msg = mbmsgs[0x014a] % (csconst.RELATION_ALLY_COST/10000)
		showAutoHideMessage( 30.0, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def rlt_askForJoinAllyMember( self ):
		"""
		Define method.
		询问是否确定加入新的结拜成员
		"""
		def notarize( id ) :
			result = False
			if id == RS_YES:
				if not self.isJoinTeam():
					self.statusMessage( csstatus.CANNOT_ALLY_NO_TEAM )
					DEBUG_MSG( "想要结拜就你的兄弟组队一起来啊！一个人不能结拜。111" )
					return
				if not self.isCaptain():
					self.statusMessage( csstatus.CANNOT_ALLY_NO_TEAM_CAPTAIN )
					DEBUG_MSG( "让队长来和我说吧，你们这样一群人一起来，太混乱了！" )
					return
				if self.money < csconst.RELATION_ALLY_COST:
					self.statusMessage( csstatus.CANNOT_ALLY_NO_MONEY, csconst.RELATION_ALLY_NEW_COST/10000 )
					DEBUG_MSG( "帮你主持结拜仪式需要花费%i金，你身上金钱不足！" % ( csconst.RELATION_ALLY_COST/10000 ) )
					return
				for itemInfo in csconst.RELATION_ALLY_NEED_ITEMS:
					if not self.checkItemFromNKCK_( itemInfo[0], itemInfo[1] ):
						self.statusMessage( csstatus.CANNOT_ALLY_NO_ITEM )
						DEBUG_MSG( "结拜仪式需要烧黄纸，同饮桃花酒，你身上物品不足。黄纸在凤鸣杂货商购买，桃花酒在凤鸣海滩有售。" )
						return
				self.cell.rlt_newMemberJoinAlly()
		msg = mbmsgs[0x014d] % ( csconst.RELATION_ALLY_NEW_COST/10000)
		showAutoHideMessage( 30.0, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def rlt_askForChangeAllyTitle( self ):
		"""
		Define mehtod.
		询问玩家是否需要改名。

		显示文本框，让玩家输入新的名字
		"""
		DEBUG_MSG( "显示文本框，让玩家输入新的名字" )
		def callback( res, text ):
			title = mbmsgs[0x0c22]
			if text == "" : return
			elif len( text ) > 14 :	# 结拜名称合法性检测
				showAutoHideMessage( 3.0, 0x014f, title )
				return
			elif self.__isHasDigit( text ):#含有数字
				# "家族名称只能由汉字和字母组成！"
				showAutoHideMessage( 3.0, 0x0151, title )
				return
			elif not rds.wordsProfanity.isPureString( text ) :
				# "名称不合法！"
				showAutoHideMessage( 3.0, 0x0152, title )
				return
			elif rds.wordsProfanity.searchNameProfanity( text ) is not None :
				# "输入的名字有禁用词汇!"
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
		询问玩家是否确定要解除结拜关系
		"""
		def notarize( id ) :
			result = False
			if id == RS_YES:
				if self.isJoinTeam():
					self.statusMessage( csstatus.ALLY_TEAM_CANNOT_QUIT )
					DEBUG_MSG( "恩断义绝这种事还是一个人来的好吧！请退出队伍。" )
					return
				self.cell.rlt_quitAlly()
		showAutoHideMessage( 30.0, mbmsgs[0x0154], "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

	def teach_prenticeCall( self, prenticeName ):
		"""
		Define method.
		徒弟请求召唤师父
		"""
		def notarize( id ) :
			if id == RS_YES:
				result = True
			else:
				result = False
			self.cell.teach_respondPrenticeCall( result )
		msg = mbmsgs[0x0155] % prenticeName
		showAutoHideMessage( 20.0, msg, "", MB_YES_NO, notarize, gstStatus = Define.GST_IN_WORLD )

		DEBUG_MSG( "询问师父是否响应徒弟( %s )召唤？" % prenticeName )

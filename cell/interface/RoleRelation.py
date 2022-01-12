# -*- coding: gb18030 -*-
#

import time
import random
import BigWorld

import csconst
import csstatus
import csdefine
from bwdebug import *
from MsgLogger import g_logger
from Function import Functor
from TitleMgr import TitleMgr

import cschannel_msgs
import ShareTexts as ST

import Const
from Love3 import g_teachCreditLoader
from Love3 import g_chatProfanity
from Love3 import g_rewards
from VehicleHelper import isFlying

g_titleLoader = TitleMgr.instance()

INVITE_PERIOD_OF_VALIDITY = 20		# 邀请有效期

class RoleRelation:
	"""
	"""
	def __init__( self ):
		"""
		"""
		pass

	def onCellReady( self ):
		"""
		"""
		if self.query( "teach_register_teachInfo", False ):	# 去管理器查询自己是否注册收徒
			self._getTeachMgr().onPlayerGetCell( self.databaseID, self.base )

	def onDestroy( self ):
		"""
		"""
		if self.query( "teach_register_teachInfo", False ):
			self._getTeachMgr().onPlayerLoseCell( self.databaseID )

	def rlt_sendPlayerInfo( self, playerBase, relationUID, friendlyValue, relationStatus ):
		"""
		Define method.
		给mailbox为playerBase的玩家发送指定的自身信息
		用于第一次把自身的信息更新到对方的客户端
		"""
		playerBase.client.rlt_receivePlayerInfo( relationUID, self.getName(), self.level, self.raceclass, self.tongName, friendlyValue, self.headTextureID, relationStatus )

	def rlt_requestPlayerInfo( self, playerBase, relationUID ):
		"""
		Define method.
		己方玩家上线，请求更新己方信息到对方客户端
		"""
		playerBase.client.rlt_playerLogon( relationUID, self.level, self.raceclass, self.tongName, self.headTextureID )

	def beAskedToFriend( self, playerBase, playerName ):
		"""
		Define method.
		对方邀请己方成为好友
		"""
		if self.qieCuoState != csdefine.QIECUO_NONE:
			playerBase.client.onStatusMessage( csstatus.TARGET_IS_QIECUO, "" )
			return

		self.base.beInvitedToFriend( playerBase, playerName )

	def addSweetie( self, srcEntityID, relationUID ):
		"""
		Exposed method.
		恋人申请
		"""
		if self.id != srcEntityID:
			ERROR_MSG( "非法使用者, src( %i ) calling dst( %i ) method" % ( srcEntityID, self.id ) )
			return
		if self.level < csconst.SWEETIE_LEVEL_LIMIT:
			self.statusMessage( csstatus.SWEETIE_PLAYER_LEVEL_LACK )
			return
		item = self.findItemFromNKCK_( 50101001 )
		if self.iskitbagsLocked() or item is None or item.isFrozen():
			self.statusMessage( csstatus.SWEETIE_NEED_TOGETHER_ITEM )
			return
		self.base.addSweetie( relationUID )

	def beInvitedToSweetie( self, playerBase, relationUID ):
		"""
		Define method.
		被邀请成为恋人
		"""
		if self.qieCuoState != csdefine.QIECUO_NONE:
			playerBase.client.onStatusMessage( csstatus.TARGET_IS_QIECUO, "" )
			return

		self.base.beInvitedToSweetie( relationUID )

	def addSweetieSuceeded( self, relationUID ):
		"""
		Define method.
		对方同意结为恋人，再次检查同心结物品，如符合条件则删除同心结并通知base设置恋人数据
		"""
		item = self.findItemFromNKCK_( 50101001 )
		if self.iskitbagsLocked() or item is None or item.isFrozen():
			self.statusMessage( csstatus.SWEETIE_NEED_TOGETHER_ITEM )
			return
		self.removeItem_( item.order, reason = csdefine.DELETE_ITEM_COMMAND_SWEAR )
		self.base.addSweetieSuceeded( relationUID )

	def hasCouple( self ):
		"""
		是否存在夫妻关系
		"""
		return self.coupleItem["playerDBID"]

	def isCouple( self, entityID ):
		"""
		entityID的玩家是否和自己是夫妻
		"""
		playerBase = self.coupleItem["playerBase"]
		if playerBase:
			return playerBase.id == entityID
		else:
			return False

	def isCoupleOnline( self ):
		"""
		配偶是否在线
		"""
		return self.coupleItem["playerBase"] is not None

	def getCoupleMB( self ):
		"""
		"""
		return self.coupleItem["playerBase"]

	def requestMarriage( self, talkEntity ):
		"""
		玩家与npc对话，选择申请结婚的功能选项，触发请求结婚的接口
		判断双方是否符合结婚条件，给双方客户端发送请求确认。
		先检查发起者的条件，然后检查目标entity的条件，最后到base检查是否恋人。

		结婚条件：
		角色之间互为恋人；
		双方角色等级不低于20级；
		双方都是未婚状态；
		需各支付30万的结婚费用；
		双方保持组队状态，且在10米范围内。
		队伍中只有两人。
		"""
		if self.level < csconst.COUPLE_LEVEL_LIMIT:
			self.statusMessage( csstatus.COUPLE_LEVEL_LIMIT )
			return
		if self.hasCouple():
			self.statusMessage( csstatus.COUPLE_NOT_MARRY_TWICE )
			return
		if self.money < csconst.COUPLE_WEDDING_CHARGE:
			self.statusMessage( csstatus.COUPLE_WEDDING_MONEY_LACK )
			return
		if not self.isInTeam():
			self.statusMessage( csstatus.COUPLE_PLAYER_NOT_TEAM )
			return

		teammateList = talkEntity.searchTeamMember( self.teamMailbox.id, csconst.COUPLE_SWARE_DISTANCE )
		if len(teammateList) == 1:
			self.statusMessage( csstatus.COUPLE_ONE_PLAYER_TEAM )
			return
		elif len( teammateList ) > 2:
			self.statusMessage( csstatus.COUPLE_TWO_PLAYER_TEAM )
			return
		lover = teammateList[0].id == self.id and teammateList[1] or teammateList[0]
		if self.getGender() == lover.getGender():
			self.statusMessage( csstatus.COUPLE_TWO_PLAYER_TEAM )
			return
		if lover.level < csconst.COUPLE_LEVEL_LIMIT:
			self.statusMessage( csstatus.COUPLE_LEVEL_LIMIT )
			return
		self.base.requestMarriage( lover.databaseID )

	def couple_canMarry( self, loverID ):
		"""
		Define method.
		在base上检察对方是己方恋人，可以结婚，调用此接口设置结婚前的数据，以便结婚时判断2者是否能够结婚。
		"""
		self.setTemp( "couple_targetID", loverID )

	def isInMarriageAffair( self ):
		"""
		是否在处理婚姻事宜
		"""
		return self.queryTemp( "couple_targetID" )

	def couple_replyForMarriage( self, srcEntityID, reply ):
		"""
		Exposed mehtod.
		回复结婚邀请

		@param reply : 是否同意，BOOL
		"""
		if self.id != srcEntityID:
			ERROR_MSG( "非法使用者, src( %i ) calling dst( %i ) method" % ( srcEntityID, self.id ) )
			return
		if not self.isInTeam():
			self.statusMessage( csstatus.COUPLE_PLAYER_NOT_TEAM )
			return
		if self.getTeamCount() != 2:
			self.statusMessage( csstatus.COUPLE_TWO_PLAYER_TEAM )
			return
		if self.level < csconst.COUPLE_LEVEL_LIMIT:
			self.statusMessage( csstatus.COUPLE_LEVEL_LIMIT )
			return
		if self.hasCouple():
			self.statusMessage( csstatus.COUPLE_NOT_MARRY_TWICE )
			return
		lover = [ e for e in self.entitiesInRangeExt( csconst.COUPLE_SWARE_DISTANCE, 'Role' ) if e.teamMailbox is not None and e.teamMailbox.id == self.teamMailbox.id ]
		if len(lover) == 0:
			self.statusMessage( csstatus.COUPLE_TARGET_NOT_TOGETHER )
			return
		lover = lover[0]
		if not lover.isInMarriageAffair():
			return
		if not reply:
			self.removeTemp( "couple_targetID" )
			lover.couple_dstMarryFalse( self.id )
			return
		if self.getNormalKitbagFreeOrder() == -1:
			self.statusMessage( csstatus.COUPLE_CANT_KITBAG_FULL )
			return
		if self.money < csconst.COUPLE_WEDDING_CHARGE:
			self.statusMessage( csstatus.COUPLE_WEDDING_MONEY_LACK )
			lover.client.onStatusMessage( csstatus.COUPLE_WEDDING_MONEY_LACK, "" )
			return
		if lover.hasFlag( csdefine.ROLE_FLAG_COUPLE_AGREE ):
			if lover.level < csconst.COUPLE_LEVEL_LIMIT:
				self.statusMessage( csstatus.COUPLE_LEVEL_LIMIT )
				return
			if lover.hasCouple():
				self.statusMessage( csstatus.COUPLE_NOT_MARRY_TWICE )
				return
			if self.position.flatDistTo( lover.position ) > csconst.TEACH_COMMUNICATE_DISTANCE:		# 10米限制
				self.statusMessage( csstatus.COUPLE_TARGET_NOT_TOGETHER )
				return
			if lover.money < csconst.COUPLE_WEDDING_CHARGE:
				self.statusMessage( csstatus.COUPLE_WEDDING_MONEY_LACK )
				return
			# 可以结婚了
			playerName = lover.getName()
			playerDBID = lover.databaseID
			self.coupleItem = { "playerDBID":playerDBID,"playerBase":lover.base}
			self.base.couple_swear( playerDBID )
			lover.couple_marrySuccess( self.base, self.getName(), self.databaseID )
			self.removeTemp( "couple_targetID" )
			self.payMoney( csconst.COUPLE_WEDDING_CHARGE, csdefine.CHANGE_MONEY_REPLYFORMARRIAGE )
			titleID = self.getGender() == csdefine.GENDER_FEMALE and csdefine.TITLE_COUPLE_FEMALE_ID \
											or csdefine.TITLE_COUPLE_MALE_ID
			self.addTitle( titleID )
			self.statusMessage( csstatus.TITLE_ADDED, g_titleLoader.getName( titleID ) % playerName )
			awarder = g_rewards.fetch( csdefine.RCG_MARRY_RING, self )
			if awarder is None or len( awarder.items ) <= 0:
				self.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
				return
			item = awarder.items[0]		# 理论上只有一个物品
			item.set( "creator", playerName )
			awarder.award( self, csdefine.ADD_ITEM_REPLYFORMARRIAGE )
			try:
				g_logger.coupleBuildLog( self.databaseID, self.getName(), playerDBID, playerName )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG()  )
		else:
			self.addFlag( csdefine.ROLE_FLAG_COUPLE_AGREE )

	def couple_marrySuccess( self, loverBase, loverName, loverDBID ):
		"""
		Define method.
		恋人结婚,通过此接口设置结婚数据

		@param loverBase:	结婚对象的base mailbox
		@type loverBase:	MAILBOX
		@param loverName:	结婚对象的名字
		@type loverName:	STRING
		@param loverDBID:	结婚对象的dbid
		@type loverDBID:	DATABASE_ID
		"""
		self.coupleItem = { "playerDBID":loverDBID, "playerBase":loverBase }
		self.base.couple_marrySuccess( loverDBID )
		self.removeTemp( "couple_targetID" )
		self.removeFlag( csdefine.ROLE_FLAG_COUPLE_AGREE )
		self.payMoney( csconst.COUPLE_WEDDING_CHARGE, csdefine.CHANGE_MONEY_REPLYFORMARRIAGE )
		titleID = self.getGender() == csdefine.GENDER_FEMALE and csdefine.TITLE_COUPLE_FEMALE_ID \
										or csdefine.TITLE_COUPLE_MALE_ID
		self.addTitle( titleID )
		self.statusMessage( csstatus.TITLE_ADDED, g_titleLoader.getName( titleID ) % loverName )
		awarder = g_rewards.fetch( csdefine.RCG_MARRY_RING, self )
		if awarder is None or len( awarder.items ) <= 0:
			self.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
			return
		item = awarder.items[0]		# 理论上只有一个物品
		item.set( "creator", loverName )
		awarder.award( self, csdefine.ADD_ITEM_MARRYSUCCESS )

	def couple_dstMarryFalse( self, entityID ):
		"""
		Define method.
		对方不同意结婚
		
		@param entityID:结婚对象的entity id
		@type entityID:	OBJECT_ID
		"""
		if self.queryTemp( "couple_targetID", 0 ) != entityID:
			ERROR_MSG( "%i 不是 %s 的结婚对象" % ( entityID, self.getName() ) )
			return
		self.statusMessage( csstatus.COUPLE_NOT_AGREE_WEDDING )
		self.removeTemp( "couple_targetID" )
		if self.hasFlag( csdefine.ROLE_FLAG_COUPLE_AGREE ):
			self.removeFlag( csdefine.ROLE_FLAG_COUPLE_AGREE )

	def couple_requestDivorce( self, talkEntity ):
		"""
		离婚，被npc的cell调用，for real
		"""
		if not self.hasCouple():
			self.statusMessage( csstatus.COUPLE_BE_MARRY_FIRST )
			return

		if not self.isCoupleOnline() or not self.isInTeam():
			if self.money < csconst.COUPLE_FORCE_DIVORCE_CHARGE:
				self.statusMessage( csstatus.COUPLE_DIVORCE_MONEY_LACK )
			else:				# 询问是否要强制离婚.
				self.client.couple_requestForceDivorce()
		else:
			teammateList = talkEntity.searchTeamMember( self.teamMailbox.id, 10 )
			if len(teammateList) == 1:
				self.statusMessage( csstatus.COUPLE_ONE_PLAYER_TEAM )
				return
			elif len( teammateList ) > 2:
				self.statusMessage( csstatus.COUPLE_TWO_PLAYER_TEAM )
				return
			lover = teammateList[0].id == self.id and teammateList[1] or teammateList[0]
			if not self.isCouple( lover.id ):
				self.statusMessage( csstatus.COUPLE_BE_COUPLE_FIRST )
				return
			if self.position.flatDistTo( lover.position ) > csconst.TEACH_COMMUNICATE_DISTANCE:		# 10米限制
				self.statusMessage( csstatus.COUPLE_TARGET_NOT_TOGETHER )
				return
			self.setTemp( "couple_divorce_manage", True )
			lover.setTemp( "couple_divorce_manage", True )
			self.client.couple_requestDivorce()
			lover.client.couple_requestDivorce()

	def couple_replyForDivorce( self, srcEntityID, reply ):
		"""
		Exposed method.
		玩家对离婚请求的回复

		@param reply:	True表示同意结婚，False表示不同意
		@type reply:	BOOL
		"""
		if self.id != srcEntityID:
			ERROR_MSG( "非法使用者, src( %i ) calling dst( %i ) method" % ( srcEntityID, self.id ) )
			return
		if not self.hasCouple():
			self.statusMessage( csstatus.COUPLE_BE_MARRY_FIRST )
			return
		if not self.queryTemp( "couple_divorce_manage", False ):	# 已经不在离婚处理中
			DEBUG_MSG( "已经不在离婚处理中." )
			return
		if reply:
			if not self.isInTeam():
				self.statusMessage( csstatus.COUPLE_PLAYER_NOT_TEAM )
				return
			teammateList = [ e for e in self.entitiesInRangeExt( 10, 'Role' ) if e.teamMailbox is not None and e.teamMailbox.id == self.teamMailbox.id ]
			if len( teammateList ) != 1:
				self.statusMessage( csstatus.COUPLE_TWO_PLAYER_TEAM )
				return
			lover = teammateList[0]
			if not self.isCouple( lover.id ):
				self.statusMessage( csstatus.COUPLE_BE_COUPLE_FIRST )
				return
			if not lover.hasFlag( csdefine.ROLE_FLAG_COUPLE_AGREE ):	# 对方还没同意离婚
				self.addFlag( csdefine.ROLE_FLAG_COUPLE_AGREE )		# 设置同意离婚标记
			else:	# 离婚处理
				self.coupleItem = { "playerDBID":0, "playerBase":None }
				titleID = self.getGender() == csdefine.GENDER_FEMALE and csdefine.TITLE_COUPLE_FEMALE_ID \
												or csdefine.TITLE_COUPLE_MALE_ID
				self.removeTitle( titleID )
				try:
					g_logger.coupleRemoveLog( self.databaseID, self.getName(), lover.databaseID )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG()  )
				self.base.couple_divorceSuccess()
				lover.couple_divorceSuccess()
				msg = cschannel_msgs.BCT_JSGX_DIVROCE % ( self.getName(), lover.getName() )
				BigWorld.globalData[csconst.C_PREFIX_GBAE].anonymityBroadcast( msg, [] )
				self.removeTemp( "couple_divorce_manage" )
				lover.removeTemp( "couple_divorce_manage" )
		else:
			self.statusMessage( csstatus.COUPLE_AGREE_DIVORCE_FAIL )
			self.removeTemp( "couple_divorce_manage" )
			self.coupleItem["playerBase"].cell.couple_dstDivorceFalse()

	def couple_dstDivorceFalse( self ):
		"""
		Define method.
		对方不同意离婚
		"""
		self.removeFlag( csdefine.ROLE_FLAG_COUPLE_AGREE )
		self.removeTemp( "couple_divorce_manage" )

	def couple_divorceSuccess( self ):
		"""
		Define method.
		离婚成功
		"""
		self.removeFlag( csdefine.ROLE_FLAG_COUPLE_AGREE )
		#self.removeTemp( "couple_divorceReply" )
		self.coupleItem = { "playerDBID":0, "playerBase":None }
		titleID = self.getGender() == csdefine.GENDER_FEMALE and csdefine.TITLE_COUPLE_FEMALE_ID \
										or csdefine.TITLE_COUPLE_MALE_ID
		self.removeTitle( titleID )
		self.base.couple_divorceSuccess()

	def couple_dstForceDivorce( self ):
		"""
		Define method.
		对方单方面强制离婚

		设置自身数据，从base到cell的一个调用，有可能cell已销毁设置不成功，但下次再上线依然可触发此行为
		"""
		titleID = self.getGender() == csdefine.GENDER_FEMALE and csdefine.TITLE_COUPLE_FEMALE_ID \
										or csdefine.TITLE_COUPLE_MALE_ID
		self.removeTitle( titleID )
		self.base.couple_divorceSuccess()
		self.coupleItem = { "playerDBID":0, "playerBase":None }

	def couple_forceDivorce( self, srcEntityID, dstPlayerName ):
		"""
		Exposed method.
		玩家同意单方面离婚，如果玩家不同意，那么不需要通知服务器
		"""
		if self.id != srcEntityID:
			return
		if not self.hasCouple():
			self.statusMessage( csstatus.COUPLE_BE_MARRY_FIRST )
			return
		if self.money < csconst.COUPLE_FORCE_DIVORCE_CHARGE:
			self.statusMessage( csstatus.COUPLE_DIVORCE_MONEY_LACK )
			return

		self.payMoney( csconst.COUPLE_FORCE_DIVORCE_CHARGE, csdefine.CHANGE_MONEY_FORCEDIVORCE )
		titleID = self.getGender() == csdefine.GENDER_FEMALE and csdefine.TITLE_COUPLE_FEMALE_ID \
										or csdefine.TITLE_COUPLE_MALE_ID
		self.removeTitle( titleID )
		self.base.couple_forceDivorce()
		title = cschannel_msgs.ROLERELATION_INFO_1
		content = self.getName() + cschannel_msgs.ROLERELATION_INFO_2
		self.mail_send_on_air( dstPlayerName, csdefine.MAIL_TYPE_QUICK, title, content )
		self.coupleItem = { "playerDBID":0, "playerBase":None }

	def cancelAgreeCouple( self, srcEntityID ):
		"""
		Exposed method.
		玩家取消结婚或离婚同意标记
		"""
		self.removeTemp( "couple_divorce_manage" )
		self.removeFlag( csdefine.ROLE_FLAG_COUPLE_AGREE )

	def rlt_sendAreaInfo( self, relationUID, playerBase ):
		"""
		Define method.
		发送自己所在的地区数据给请求玩家
		"""
		playerBase.client.rlt_receiveAreaInfo( relationUID, self.spaceType, self.position, self.getCurrentSpaceLineNumber() )

	def couple_requestPosition( self ):
		"""
		Define method.
		伴侣使用了 形影不离 技能，通过此接口请求己方的位置信息
		判断己方是否在副本中，在则各对方输出提示信息，对方使用技能不成功，不在则把己方的位置信息发送给对方。
		"""
		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
			#self.coupleItem["playerBase"].client.onStatusMessage( csstatus.COUPLE_CANT_TELEPORT_SPECIAL_SPACE, "" )
			return
		
		# 如果自己正在飞行，则不允许对方传送到自己身边 by mushuang
		if isFlying( self ):
			self.coupleItem["playerBase"].cell.interruptSpell( csstatus.CANT_TELEPORT_WHEN_TARGET_FLYING ) # 打断吟唱，提示对方
			return
		
		spaceName = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		lineNumber = self.getCurrentSpaceLineNumber()
		self.coupleItem["playerBase"].cell.couple_teleport( spaceName, lineNumber, self.position, self.direction, self.getName() )

	def couple_teleport( self, spaceName, lineNumber, position, direction, playerName ):
		"""
		Define method.
		伴侣通过此接口把位置信息发送给己方，设置传送数据，吟唱结束时会使用此数据传送
		"""
		self.setTemp( "couple_ringTeleport", ( spaceName, lineNumber, position, direction, playerName ) )

	def receiveCoupleInfo( self, relationItem ):
		"""
		Define method.
		接收伴侣信息

		@param helpmateBase : 玩家mailbox，有可能为None
		@type helpmateBase : MAILBOX
		"""
		self.coupleItem = relationItem

	def onHelpmateLogin( self, helpmateBase ):
		"""
		Define method.
		伴侣上线
		"""
		self.coupleItem["playerBase"] = helpmateBase

	def onHelpmateLogout( self ):
		"""
		Define method.
		伴侣下线
		"""
		self.coupleItem["playerBase"] = None

	def couple_findWeddingRing( self, loverName ):
		"""
		Define method.
		玩家申请找回结婚戒指。
		"""
		if self.payMoney( csconst.COUPLE_WEDDING_RING_PRICE, csdefine.CHANGE_MONEY_FINDWEDDINGRING ):
			awarder = g_rewards.fetch( csdefine.RCG_MARRY_RING, self )
			if awarder is None or len( awarder.items ) <= 0:
				self.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
				return
			item = awarder.items[0]		# 理论上只有一个物品
			item.set( "creator", loverName )
			awarder.award( self, csdefine.ADD_ITEM_FINDWEDDINGRING )
		else:
			self.statusMessage( csstatus.COUPLE_LACK_MONEY_FOR_RING )

	def rlt_checkAddFriendyResult( self, canAdd ):
		"""
		Define method.
		是否能够增加友好度检查回调
		"""
		if not self.queryTemp( "addFriendlyRequesting", False ):	# 如果不在使用技能中
			return
		if not canAdd: # 案策划要求，这里增加提示信息 (MB):您与 %s 没有友好关系，不能使用该物品！
			name = self.queryTemp( "addFriendlyName", "未知玩家" )
			self.statusMessage( csstatus.FRIEND_ITEM_ADD_NOT_FRIEND, name )
			
			self.interruptSpell( csstatus.FRIEND_ADD_VALUE_NOT_FRIEND )

	# ------------------------------------------------------------------------
	# 师徒关系
	# ------------------------------------------------------------------------
	def iAmMaster( self ):
		"""
		自己是否是师傅
		"""
		return len( self.prenticeList ) > 0

	def isPrentice( self, playerDBID ):
		"""
		for real
		对方是否徒弟
		"""
		for prentice in self.prenticeList:
			if prentice["playerDBID"] == playerDBID:
				return True
		return False

	def getPrenticeMbByDBID( self, playerDBID ):
		for prentice in self.prenticeList:
			if prentice["playerDBID"] == playerDBID:
				return prentice["playerBase"]
		return None

	def hasShiTuRelation( self ):
		"""
		玩家是否拥有师徒关系(即：玩家是否是师傅或者徒弟)
		"""
		return len( self.prenticeList ) > 0 or self.masterItem["playerDBID"]

	def teach_isTeaching( self ):
		"""
		是否在拜师中
		由于可以远程拜师,且有多种拜师方式.设置此临时标记避免在异步情况下拜师冲突.
		"""
		return self.queryTemp( "teaching" ) is not None

	def getPrenticeNum( self ):
		return len( self.prenticeList )

	def _getTeachMgr( self ):
		"""
		获得拜师管理器
		"""
		return BigWorld.globalData["TeachMgr"]

	def hasMaster( self ):
		"""
		是否存在师父
		for real & ghost
		"""
		return self.masterItem["playerDBID"]

	def getMasterMB( self ):
		"""
		获得师父的base mailbox
		"""
		return self.masterItem["playerBase"]

	def receiveTeachInfo( self, relationItem, targetRelationStatus ):
		"""
		Define method.
		接收师徒信息

		@param relationItem : 玩家师徒数据
		@type relationItem : RELATION_ITEM
		@param relation : 师父/徒弟关系
		@type relation : UINT16
		"""
		if targetRelationStatus & csdefine.ROLE_RELATION_MASTER:
			self.prenticeList.append( relationItem )
		else:
			self.masterItem = relationItem
			# 由于存在远程拜师，有可能在拜师成功时徒弟没能获得称号(关系写db成功，但是远程通知徒弟加称号时徒弟销毁)，
			# 此时不妨检查一下，如果没有则补上。
			if not self.hasTitle( csdefine.TITLE_TEACH_PRENTICE_ID ):
				self.addTitle( csdefine.TITLE_TEACH_PRENTICE_ID )
		if self.query( "teachSpaceKillMonsterTime" ) is None:
			self._setTeachData()

	def teach_onLevelUp( self ):
		"""
		自身级别改变，如果存在师徒关系，则通知师/徒
		"""
		if self.hasMaster():
			if self.level >= csconst.TEACH_END_TEACH_AWARD_LIMIT:
				self.autoTeach_disband()	# 徒弟达到55级自动出师 by姜毅
			else:
				masterMB = self.getMasterMB()
				if masterMB and self.level < csconst.TEACH_END_TEACH_AWARD_LIMIT - 4:	# 大于50级师父不再能获得奖励
					masterMB.cell.teach_receiveAward( self.level )
			if self.level % 5 == 0:	# 徒弟等级提升为15、20、25、30、35、40、45、50时，系统会在弟子升级到指定等级时发送物品奖励（勉励状，ID为60101107）
				self._addTeachRewardItems( csdefine.RCG_TEACH_LEVEL_UP )
		if self.query( "teach_register_teachInfo", False ):	# 如果注册了收徒，更新自己的收徒信息
			self._getTeachMgr().onPlayerLevelUp( self.databaseID, self.level )

	def teach_receiveAward( self, level ):
		"""
		Define method.
		师父在线，徒弟等级提升，师父接受奖励的接口，根据level计算奖励

		Param level:徒弟的等级
		Type level:	UINT8
		"""
		teachCredit = g_teachCreditLoader.getTeachCredit( level )
		exp = g_teachCreditLoader.getExp( level )
		money = g_teachCreditLoader.getMoney( level )
		self.gainMoney( money, csdefine.CHANGE_MONEY_TEACH_REWARD )
		self.addExp( exp, csdefine.CHANGE_EXP_TEACH_REWARD )
		self.addTeachCredit( teachCredit, csdefine.CHANGE_TEACH_CREDIT_REWARD )
		self.statusMessage( csstatus.TEACH_PRENTICE_LEVEL_UP, exp, money, teachCredit )

	def autoTeach_disband( self ):
		"""
		参照teach_disband的自动出师接口
		在徒弟升级时被调用 by姜毅
		"""
		self.removeTitle( csdefine.TITLE_TEACH_PRENTICE_ID )		# 删除相应称号
		self._removeTeachData()
		self.base.autoTeach_disband( self.masterItem["playerDBID"] )
		self.masterItem = {"playerDBID":0,"playerBase":None}

		# 徒弟自动出师，按50级给奖励
		money = 50 * csconst.TEACH_END_MASTER_MONEY_AWARD
		self.gainMoney( money, csdefine.CHANGE_MONEY_PRENTICEENDTEACH )
		self.addExp( int( 50 * csconst.TEACH_END_MASTER_EXP_AWARD ), csdefine.CHANGE_EXP_PRENTICEENDTEACH )
		self._addTeachRewardItems( csdefine.RCG_TEACH_END_SUC )
		
	def teachEveryDayReward( self ):
		"""
		师徒每日奖励
		"""
		self._addTeachRewardItems( csdefine.RCG_TEACH_EVERY_DAY )

	def _addTeachRewardItems( self, rewardID ):
		"""
		获得成功出师的物品
		"""
		awarder = g_rewards.fetch( rewardID, self )
		if awarder is None or len( awarder.items ) <= 0:
			self.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
			return
		if self.checkItemsPlaceIntoNK_( awarder.items ) != csdefine.KITBAG_CAN_HOLD:
			title = cschannel_msgs.ROLERELATION_INFO_10
			content = cschannel_msgs.ROLERELATION_INFO_11
			if rewardID == csdefine.RCG_TEACH_SUC:		# 拜师的邮件信息会有所不同
				title = cschannel_msgs.ROLERELATION_INFO_8
				content = cschannel_msgs.ROLERELATION_INFO_9
			elif rewardID == csdefine.RCG_TEACH_EVERY_DAY:
				title = cschannel_msgs.ROLERELATION_INFO_8
				content = cschannel_msgs.ROLERELATION_INFO_11
			self.mail_send_on_air_withItems( self.getName(), csdefine.MAIL_TYPE_QUICK, title, content, awarder.items )
			self.statusMessage( csstatus.CANT_ADD_TEACH_DONATE_ITEM )
		else:
			awarder.award( self, csdefine.ADD_ITEM_TEACH_SUCCESS )

	def teach_teachPrentice( self, talkEntity ):
		"""
		被拜师npc的调用，判断与同组的队友是否满足建立师徒关系的条件并处理，如果成功则设置自己的prenticeBaseMBList数据，同时增加一个相应称号。

		talkEntity:npc entity
		"""
		if self.level < csconst.TEACH_MASTER_MIN_LEVEL:					# 师父等级检查
			self.statusMessage( csstatus.TEACH_PLAYER_LEVEL_LACK, csconst.TEACH_MASTER_MIN_LEVEL, csconst.TEACH_END_TEACH_LEAST_LEVEL, csconst.TEACH_PRENTICE_LOWER_LIMIT )
			return
		if self.teach_isTeaching():
			HACK_MSG( "player( %s )-->>>teaching" % self.getName() )
			return
		if not self.isInTeam() or self.getTeamCount() != 2:						# 师父与徒弟组队检查
			self.statusMessage( csstatus.TEACH_PLAYER_NOT_TEAM )
			return
		if self.getPrenticeNum() >= csconst.TEACH_PRENTICE_MAX_COUNT:	# 徒弟数量上限检查
			self.statusMessage( csstatus.TEACH_PRENTICE_NUM_FULL )
			return

		teammateMBs = self.getTeamMemberMailboxs()
		prenticeID = teammateMBs[0].id  == self.id and teammateMBs[1].id or teammateMBs[0].id
		prentice = BigWorld.entities.get( prenticeID )
		if prentice is None:
			self.statusMessage( csstatus.TEACH_PRENTICE_TOO_FAR )
			return
		if self.position.flatDistTo( prentice.position ) > csconst.TEACH_COMMUNICATE_DISTANCE:		# 10米限制
			self.statusMessage( csstatus.TEACH_PRENTICE_TOO_FAR )
			return
		if prentice.hasMaster():	# 徒弟是否已有师父的检查
			self.statusMessage( csstatus.TEACH_PRENTICE_HAS_MONSTER ,prentice.getName() )
			return
		prenticeLevel = prentice.level						# 徒弟级别检查
		if prenticeLevel < csconst.TEACH_PRENTICE_LOWER_LIMIT or prenticeLevel > csconst.TEACH_PRENTICE_UPPER_LIMIT:
			self.statusMessage( csstatus.TEACH_PLAYER_LEVEL_LACK, csconst.TEACH_MASTER_MIN_LEVEL, csconst.TEACH_END_TEACH_LEAST_LEVEL, csconst.TEACH_PRENTICE_LOWER_LIMIT )
			return
		if prentice.teach_isTeaching():
			return

		prenticeDBID = prentice.databaseID
		prenticeName = prentice.getName()
		self.prenticeList.append( { "playerDBID":prenticeDBID, "playerBase":prentice.base } )
		self._setTeachData()
		prentice.teach_beTeached()							# 通知徒弟cell设置师徒关系
		self.base.teach_beginTeach( prenticeDBID, prenticeName, prentice.base )	# 设置base数据并写数据库
		self.statusMessage( csstatus.TEACH_BE_MASTER_SUCCESS, prenticeName )	# 通知客户端
		if self.query( "teach_register_teachInfo", False ):
			self._getTeachMgr().onPrenticeNumChange( self.databaseID, self.getPrenticeNum() )
	
	def onSendTongGrade( self, relationUID, baseMailbox ) :
		"""
		Define method
		"""
		print "cell onReceiveTongGrade"
		baseMailbox.client.onReceiveTongGrade( relationUID, self.tong_grade )

	def teach_beTeached( self ):
		"""
		Define method.
		被师父的cell调用，师父申请建立师徒关系成功，通过此接口通知徒弟设置表示师徒关系状态的数据，增加一个相应称号。
		"""
		teammateMBs = self.getTeamMemberMailboxs()
		masterID = teammateMBs[0].id == self.id and teammateMBs[1].id or teammateMBs[0].id
		master = BigWorld.entities.get( masterID )
		masterName = master.getName()
		self.masterItem = { "playerDBID":master.databaseID,"playerBase":master.base }
		self.addTitle( csdefine.TITLE_TEACH_PRENTICE_ID )
		self._setTeachData()
		self.statusMessage( csstatus.TITLE_ADDED, g_titleLoader.getName( csdefine.TITLE_TEACH_PRENTICE_ID ) % masterName )
		self.statusMessage( csstatus.TEACH_BE_PRENTICE_SUCCESS, masterName )
		self._addTeachRewardItems( csdefine.RCG_TEACH_SUC )
		if self.query( "teach_register_teachInfo", False ):
			self.teach_deregisterPrentice()
			
	def teach_disband( self, playerDBID, playerName ):
		"""
		Define method.
		玩家解除师徒关系的接口
		玩家设置自身师徒关系数据。

		Param playerName:	对方玩家的名字
		Type playerName:	STRING
		Param playerDBID:	对方玩家的dbid
		Type playerDBID:	DATABASE_ID
		"""
		if self.hasMaster():	# 如果是徒弟单方面解除关系
			self.removeTitle( csdefine.TITLE_TEACH_PRENTICE_ID )		# 删除相应称号
			self.masterItem = {"playerDBID":0,"playerBase":None}
			self._removeTeachData()
		else:																# 如果对象是徒弟
			self.removePrentice( playerDBID )
		self.base.teach_disband( playerDBID )
		self.statusMessage( csstatus.TEACH_RELATION_DISBAND, playerName )	# 通知玩家
		title = cschannel_msgs.ROLERELATION_INFO_3
		content = cschannel_msgs.ROLERELATION_INFO_5 + self.getName() + cschannel_msgs.ROLERELATION_INFO_6
		self.mail_send_on_air( playerName, csdefine.MAIL_TYPE_QUICK, title, content )

	def removePrentice( self, prenticeDBID ):
		"""
		移除一个徒弟数据。
		"""
		for prenticeItem in self.prenticeList:
			if prenticeItem["playerDBID"] == prenticeDBID:
				self.prenticeList.remove( prenticeItem )
				break
		if len( self.prenticeList ) == 0:
			self._removeTeachData()
		if self.query( "teach_register_teachInfo", False ):
			self._getTeachMgr().onPrenticeNumChange( self.databaseID, self.getPrenticeNum() )

	def targetDisbandTeach( self, playerDBID, relation ):
		"""
		Define method.
		对方解除师徒关系

		@param playerDBID : 对方玩家的dbid
		@type playerDBID : DATABASE_ID
		@param relation: 对方玩家的身份定义
		"""
		if relation & csdefine.ROLE_RELATION_MASTER:
			self.removeTitle( csdefine.TITLE_TEACH_PRENTICE_ID )
			self._removeTeachData()
			self.masterItem = { "playerDBID":0, "playerBase":None }
			self.base.masterDisbandTeach()
		else:
			self.removePrentice( playerDBID )
			self.base.prenticeDisbandTeach( playerDBID )

	# ---------------------------------------------------------------------------------
	# 远程收徒功能
	# ---------------------------------------------------------------------------------
	def hadRegisteredTeacher( self ):
		"""
		Define method.
		去管理器查询自己是否注册收徒的返回，有返回则表示有注册。
		"""
		self.addFlag( csdefine.ROLE_FLAG_REGISTER_MASTER )

	def teach_registerTeacher( self, everPrenticeNum, lastWeekOnlineTime ):
		"""
		注册收徒
		@param everPrenticeNum : 出师徒弟数
		@type everPrenticeNum : INT32
		@param lastWeekOnlineTime : 上周在线时间
		@type lastWeekOnlineTime : FLOAT
		"""
		if self.hasMaster():
			self.statusMessage( csstatus.TEACH_LIST_MASTER_LEVEL_LACK )
			return
		if self.level < csconst.TEACH_MASTER_MIN_LEVEL:						# 师父等级检查
			self.statusMessage( csstatus.TEACH_LIST_MASTER_LEVEL_LACK )
			return
		if self.getPrenticeNum() >= csconst.TEACH_PRENTICE_MAX_COUNT:		# 徒弟数量上限检查
			self.statusMessage( csstatus.TEACH_PRENTICE_NUM_FULL )
			return
		if self.query( "teach_register_teachInfo", False ):		# 已经注册过了
			self.statusMessage( csstatus.TEACH_LIST_ALREADY_IN )
			return

		self.set( "teach_register_teachInfo", True )
		self.statusMessage( csstatus.TEACH_LIST_ADD_SUCCESS )
		self._getTeachMgr().register( self.databaseID, self.getName(), self.level, self.raceclass, self.getMyTeachTitle(), self.getPrenticeNum(), self.base, everPrenticeNum,lastWeekOnlineTime )

	def teach_deregisterTeacher( self ):
		"""
		注销收徒
		"""
		if not self.query( "teach_register_teachInfo", False ):
			self.statusMessage( csstatus.TEACH_LIST_ISNT_IN )
			return
		self._getTeachMgr().deregister( self.databaseID, 1 )

	def teach_registerPrentice( self, lastWeekOnlineTime ):
		"""
		玩家想要拜师，注册到拜师管理器
		
		@param lastWeekOnlineTime : 上周在线时间
		@type lastWeekOnlineTime : FLOAT
		"""
		if self.level < csconst.TEACH_PRENTICE_LOWER_LIMIT or self.level > csconst.TEACH_PRENTICE_UPPER_LIMIT:
			self.statusMessage( csstatus.FIND_MASTER_LEVEL_LACK, csconst.TEACH_END_TEACH_LEAST_LEVEL, csconst.TEACH_PRENTICE_LOWER_LIMIT )
			return
		if self.hasMaster():
			self.statusMessage( csstatus.CANT_REGISTER_HAD_MASTER )
			return
		if self.query( "teach_register_teachInfo", False ):
			self.statusMessage( csstatus.TEACH_LIST_ALREADY_IN )
			return

		self.set( "teach_register_teachInfo", True )
		self.statusMessage( csstatus.PRENTICE_REGISTER_SUCCESS )
		playerName = self.getName()
		BigWorld.globalData[csconst.C_PREFIX_GBAE].anonymityBroadcast( cschannel_msgs.BCT_JSGX_FIND_TEACHER % ( playerName, playerName ), [] )
		self._getTeachMgr().register(  self.databaseID, self.getName(), self.level, self.raceclass, self.getMyTeachTitle(), 0, self.base, 0, lastWeekOnlineTime )

	def teach_deregisterPrentice( self ):
		"""
		注销徒弟公告到拜师管理器
		"""
		if not self.query( "teach_register_teachInfo", False ):
			self.statusMessage( csstatus.TEACH_LIST_ISNT_IN )
			return
		self._getTeachMgr().deregister( self.databaseID, 0 )

	def teach_deregisterTeachInfo( self ):
		"""
		Define method.
		管理器通知注销拜师信息
		"""
		self.remove( "teach_register_teachInfo" )

	def teach_queryTeachInfo( self, srcEntityID ):
		"""
		Exposed method.
		查询师徒管理器中的相应信息
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法调用者，%i调用了%i的远程方法。" % ( srcEntityID, self.id ) )
			return
		self._getTeachMgr().queryTeachInfo( self.base, self.level )

	def teach_remoteTeachReply( self, srcEntityID, agree, prenticeName ):
		"""
		Exposed method.
		师父回复拜师邀请的暴露函数

		@param agree : 是否同意
		@type agree : BOOL
		@param prenticeName : 徒弟名字
		@type prenticeName : STRING
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法调用者，%i调用了%i的远程方法。" % ( srcEntityID, self.id ) )
			return
		if self.getPrenticeNum() >= csconst.TEACH_PRENTICE_MAX_COUNT:
			self.statusMessage( csstatus.TEACH_PRENTICE_NUM_FULL )
			self.base.requestBeTeachedResult( csstatus.TEACH_REQUEST_PRENTICE_NUM_LIMIT )
			return

		if agree:	# 把徒弟的数据写到徒弟数据库,如果徒弟在线再通知他,在cell访问数据库的原因是,可以同步处理师父和徒弟的数据
			self.setTemp( "teaching", True )	# 设置一个正在拜师的标记
			self.base.masterAgreeRemoteTeach( prenticeName )
		else:
			self.base.requestBeTeachedResult( csstatus.TEACH_REQUEST_BE_REFUSED )

	def teach_beginRemoteTeach( self, masterBase, masterDBID, masterName, teacherOrPrenticeAccept ):
		"""
		Define method.
		开始远程拜师。检查徒弟条件是否能够拜师
		@param teacherOrPrenticeAccept: 1 表示师父接受请求，0表示徒弟接受请求
		@type teacherOrPrenticeAccept : INT32
		"""
		if self.hasMaster():	# 徒弟是否已有师父的检查
			masterBase.requestBeTeachedResult( csstatus.TEACH_MASTER_EXIST )
			return
		if self.level < csconst.TEACH_PRENTICE_LOWER_LIMIT or self.level > csconst.TEACH_PRENTICE_UPPER_LIMIT:
			masterBase.requestBeTeachedResult( csstatus.TEACH_REQUEST_LEVEL_LIMIT )
			return

		if teacherOrPrenticeAccept == 1:	# 师父接受请求，提示徒弟拜师成功
			self.statusMessage( csstatus.TEACH_TEACHER_ECCEPT_REQUEST, masterName )
		self.masterItem = { "playerDBID":masterDBID, "playerBase":masterBase }
		self.addTitle( csdefine.TITLE_TEACH_PRENTICE_ID )
		self._setTeachData()
		self.statusMessage( csstatus.TITLE_ADDED, g_titleLoader.getName( csdefine.TITLE_TEACH_PRENTICE_ID ) % masterName )
		#self.statusMessage( csstatus.TEACH_BE_PRENTICE_SUCCESS, masterName )
		self.base.teach_beginRemoteTeach( masterDBID, masterName, masterBase )
		# 有可能师父cell已经被销毁，称号数据没加入成功，因此玩家上线初始化师徒数据，那么需要补上师徒称号
		masterBase.cell.teach_remoteTeachForMaster( self.databaseID, self.base, self.getName(), teacherOrPrenticeAccept )
		self._addTeachRewardItems( csdefine.RCG_TEACH_SUC )
		if self.query( "teach_register_teachInfo", False ):
			self.teach_deregisterPrentice()
			
	def _setTeachData( self ):
		"""
		玩家有师徒关系后设置一些临时标记，以实现一些师徒关系才能进行的活动
		"""
		self.set( "teachSpaceKillMonsterTime", 0 )	# 上次师徒杀怪副本的参与时间
		self.set( "teachEveryDayRewardTime", 0 )	# 上次领取每日师徒奖励时间

	def _removeTeachData( self ):
		"""
		移除师徒关系临时标记
		"""
		self.remove( "teachSpaceKillMonsterTime" )	# 上次师徒杀怪副本的参与时间
		self.remove( "teachEveryDayRewardTime" )	# 上次领取每日师徒奖励时间

	def teach_remoteTeachForMaster( self, prenticeDBID, prenticeBase, prenticeName, teacherOrPrenticeAccept ):
		"""
		Define method.
		远程拜师成功,通知师父设置数据

		@param prenticeBase : 徒弟的base mailbox
		@type prenticeBase : MAILBOX
		"""
		self.prenticeList.append( { "playerDBID":prenticeDBID, "playerBase":prenticeBase } )	# 把徒弟base加入徒弟base列表
		self._setTeachData()
		if teacherOrPrenticeAccept == 0:	# 徒弟接受请求，提示徒弟拜师成功
			self.statusMessage( csstatus.TEACH_PRENTICE_ACCEPT_REQUEST, prenticeName )
		if self.query( "teach_register_teachInfo", False ):
			self._getTeachMgr().onPrenticeNumChange( self.databaseID, self.getPrenticeNum() )

	def teach_masterEndTeach( self, talkEntity ):
		"""
		被拜师npc的cell调用，解除与自己组队的徒弟的关系。

		@Param entityID:	npc的id
		@Type entityID:	OBJECT_ID
		"""
		if not self.iAmMaster():
			self.statusMessage( csstatus.TEACH_PRENTICE_NOT_REQUEST )
			return
		if not self.isInTeam():						# 师父与徒弟组队检查
			self.statusMessage( csstatus.TEACH_PLAYER_NOT_TEAM )
			return
		teamMembers = self.getTeamMemberMailboxs()
		if len( teamMembers ) < 2:				# 师父与徒弟组队检查
			self.statusMessage( csstatus.TEACH_PLAYER_NOT_TEAM )
			return
		if len( teamMembers ) > 2:
			self.statusMessage( csstatus.TEACH_END_TEAM_MORE_PEOPLE )
			return
		prenticeID = teamMembers[0].id  == self.id and teamMembers[1].id or teamMembers[0].id
		prentice = BigWorld.entities.get( prenticeID )
		if prentice is None:
			self.statusMessage( csstatus.TEACH_PRENTICE_TOO_FAR )
			return
		prenticeDBID = prentice.databaseID
		if not self.isPrentice( prenticeDBID ):
			self.statusMessage( csstatus.TEACH_PRENTICE_NOT_YOUR_PRENTICE )
			return
		if self.position.flatDistTo( prentice.position ) > csconst.TEACH_COMMUNICATE_DISTANCE:		# 10米限制
			self.statusMessage( csstatus.TEACH_PRENTICE_TOO_FAR )
			return
		prenticeLevel = prentice.level
		if prenticeLevel < csconst.TEACH_END_TEACH_LEAST_LEVEL:			# 徒弟等级必须达到50级才能出师
			self.statusMessage( csstatus.TEACH_PRENTICE_NOT_GROW_UP )
			return
		self.removePrentice( prenticeDBID )
		if prenticeLevel <= csconst.TEACH_END_TEACH_AWARD_LIMIT:		# 如果徒弟等级小于55级，可获得出师奖励
			money = prenticeLevel * csconst.TEACH_END_MASTER_MONEY_AWARD
			self.gainMoney( money, csdefine.CHANGE_MONEY_MASTERENDTEACH )
			self.addExp( int( prenticeLevel * csconst.TEACH_END_MASTER_EXP_AWARD ), csdefine.CHANGE_EXP_MASTERENDTEACH )
			self.addTeachCredit( prenticeLevel * csconst.TEACH_END_MASTER_CREDIT_AWARD )
			awarder = g_rewards.fetch( csdefine.RCG_D_TEACH, self )
			if awarder is None or len( awarder.items ) <= 0:
				self.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
				return
			awarder.award( self, csdefine.ADD_ITEM_MASTERENDTEACH )	# 随机获得物品奖励

		else:
			self.statusMessage( csstatus.TEACH_PRENTICE_LEVEL_NOT_REWARD )
		self.base.masterEndTeach( prenticeDBID )
		prentice.endTeachSuccess()
		self._addTeachRewardItems( csdefine.RCG_TEACH_END_SUC_THK )

	def endTeachSuccess( self ):
		"""
		Define method.
		师父出师成功，通知徒弟设置数据

		@param master : 师父entity
		"""
		self.removeTitle( csdefine.TITLE_TEACH_PRENTICE_ID )
		self._removeTeachData()
		if self.level < csconst.TEACH_END_TEACH_AWARD_LIMIT:	# 如果徒弟等级小于55级，可获得出师奖励
			money = self.level * csconst.TEACH_END_MASTER_MONEY_AWARD
			self.gainMoney( money, csdefine.CHANGE_MONEY_PRENTICEENDTEACH )
			self.addExp( int( self.level * csconst.TEACH_END_MASTER_EXP_AWARD ), csdefine.CHANGE_EXP_PRENTICEENDTEACH )
			
		self.base.endTeachSuccess( self.masterItem["playerDBID"] )
		self.masterItem = { "playerDBID":0, "playerBase":None }
		self._addTeachRewardItems( csdefine.RCG_TEACH_END_SUC )

	def autoDisbandSuccess( self, prenticeDBID ):
		"""
		Define mehtod.
		徒弟自动出师成功，通知师傅
		"""
		self.removePrentice( prenticeDBID )
		
	def onTeachLogin( self, playerDBID, playerBase, relationStatus ):
		"""
		Define method.
		有师徒关系的玩家上线了

		@param playerDBID : 玩家dbid
		@param playerBase : 玩家base mailbox
		@param relationStatus : 与对方玩家关系
		"""
		if relationStatus & csdefine.ROLE_RELATION_MASTER:
			for prenticeItem in self.prenticeList:
				if prenticeItem["playerDBID"] == playerDBID:
					prenticeItem["playerBase"] = playerBase
					break
		elif relationStatus & csdefine.ROLE_RELATION_PRENTICE:
			self.masterItem["playerBase"] = playerBase

	def onTeachLogout( self, playerDBID, relationStatus ):
		"""
		Define method.
		有师徒关系的玩家上线了

		@param playerDBID : 玩家dbid
		@param relationStatus : 与对方玩家关系
		"""
		if relationStatus & csdefine.ROLE_RELATION_MASTER:
			for prenticeItem in self.prenticeList:
				if prenticeItem["playerDBID"] == playerDBID:
					prenticeItem["playerBase"] = None
					break
		else:
			self.masterItem["playerBase"] = None

	def teach_prenticeCall( self, prenticeName, prenticeDBID, spaceName, lineNumber, position, direction ):
		"""
		Define method
		徒弟召唤师父
		"""
		prenticeMB = self.getPrenticeMbByDBID( prenticeDBID )
		if prenticeMB is None:
			DEBUG_MSG( "prentice( name:%s, dbid:%i )'s mailbox is None" % ( prenticeName, prenticeDBID ) )
			return
		if self.queryTemp( "prenticeCalling", () ):	# 如果正在被别的徒弟召唤中
			prenticeMB.client.onStatusMessage( csstatus.CANT_CALL_MASTER_BUSY, "" )
			return
		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
			prenticeMB.client.onStatusMessage( csstatus.CANT_CALL_MASTER_BUSY, "" )
			return
		self.setTemp( "prenticeCalling", ( prenticeName, prenticeDBID, spaceName, lineNumber, position, direction ) )
		self.client.teach_prenticeCall( prenticeName )

	def teach_respondPrenticeCall( self, srcEntityID, answer ):
		"""
		Exposed method.
		师父响应徒弟的召唤
		"""
		if self.id != srcEntityID:
			HACK_MSG( "玩家(%s) srcEntityID(%i) != self.id." % ( self.getName(), srcEntityID ) )
			return
		teleportData = self.popTemp( "prenticeCalling", () )
		if not teleportData:
			return
		prenticeMB = self.getPrenticeMbByDBID( teleportData[1] )
		if prenticeMB is None:
			DEBUG_MSG( "prentice( name:%s, dbid:%i )'s mailbox is None" % ( prenticeName, prenticeDBID ) )
			return
		if not answer:
			prenticeMB.client.onStatusMessage( csstatus.CANT_CALL_MASTER_BUSY, "" )
			return
		self.gotoSpaceLineNumber( teleportData[2], teleportData[3], teleportData[4], teleportData[5] )

	def tong_onChanged( self ):
		"""
		角色帮会改变通知其他关系
		"""
		self.base.onTongChangeNotifyRelation( self.tongName )

	def tong_onSetTongName( self, tongName ):
		"""
		角色帮会名称改变
		"""
		self.base.onTongChangeNotifyRelation( tongName )


	# ---------------------------------------------------------------------------------
	# 玩家结拜
	# ---------------------------------------------------------------------------------
	def hasAllyRelation( self ):
		"""
		玩家是否有结拜关系
		"""
		return len( self.allyPlayers ) > 0

	def rlt_requestAlly( self, srcEntityID ):
		"""
		Exposed mehtod.
		玩家请求结拜兄弟
		"""
		if srcEntityID != self.id:
			return

		if self.queryTemp( "ally_player_count", 0 ):
			#DEBUG_MSG( "---->>>正在申请结拜中" )
			return
		if not self.isInTeam():
			#DEBUG_MSG( "想要结拜就你的兄弟组队一起来啊！一个人不能结拜。111" )
			return
		if not self.isTeamCaptain():
			#DEBUG_MSG( "让队长来和我说吧，你们这样一群人一起来，太混乱了！" )
			return
		if self.hasAllyRelation():
			#DEBUG_MSG( "结义金兰要成心真意，每人只能结拜一次。请检查队伍中谁拥有结拜关系。" )
			return
		teammateList = [ e for e in self.entitiesInRangeExt( csconst.RELATION_ALLY_SWEAR_DISTANCE, 'Role' ) \
							if e.teamMailbox is not None \
							and e.teamMailbox.id == self.teamMailbox.id \
						]
		teammateList.append( self )
		memberNum = len( teammateList )
		if memberNum < 2:
			self.statusMessage( csstatus.CANNOT_ALLY_NO_PLAYER )
			#DEBUG_MSG( "想要结拜就带你的兄弟们来啊！一个人怎么结拜？222" )
			return
		if self.getTeamCount() > memberNum:
			self.statusMessage( csstatus.CANNOT_ALLY_LACK_SOME_PLAYER )
			#DEBUG_MSG( "队伍里有人没来，让他赶快过来！" )
			return

		DBIDList = []	# 玩家的dbid列表，发到base去验证各个玩家之间是否可以结义。
		for player in teammateList:
			if player.level < csconst.RELATION_ALLY_LEVEL_LACK:
				self.statusMessage( csstatus.CANNOT_ALLY_LACK_LEVEL, player.getName(), csconst.RELATION_ALLY_LEVEL_LACK )
				#DEBUG_MSG( "[%s]等级太低了，%i级以上的人才能结拜！" % ( player.getName(), csconst.RELATION_ALLY_LEVEL_LACK ) )
				return
			if player.hasAllyRelation():
				self.statusMessage( csstatus.CANNOT_ALLY_HAD_ALREADY )
				#DEBUG_MSG( "义结金兰要成心真意，每人只能结拜一次。请检查队伍中谁拥有结拜关系。" )
				return
			DBIDList.append( player.databaseID )

		for player in teammateList:
			tempDBIDList = DBIDList[:]
			tempDBIDList.remove( player.databaseID )
			player.base.rlt_requestAlly( self.base, tempDBIDList )
		self.setTemp( "ally_player_count", memberNum )	# 结拜的玩家数
		self.setTemp( "ally_player_dbid_list", DBIDList )		# 参与申请结拜的玩家名字列表

	def rlt_allyCheckResult( self, playerDBID, statusID, statusArg ):
		"""
		Define method.
		检查结拜条件的回调
		再次检查，如果满足结拜条件则启动结拜流程处理，否则结拜不成功。

		@param playerDBID : 玩家dbid，用于区别是哪个玩家的检查结果
		@param statusID : 检查结果，uint16
		@param statusArg : status信息的额外参数，python
		"""
		ally_player_count = self.queryTemp( "ally_player_count", 0 )
		if ally_player_count == 0:
			#DEBUG_MSG( "---->>>结拜流程已经停止。" )
			self.rlt_removeAllyTempData()
			return
		DBIDList = self.queryTemp( "ally_player_dbid_list", [] )
		if playerDBID not in DBIDList:
			self.rlt_removeAllyTempData()
			return
		if not self.isTeamCaptain():
			self.rlt_removeAllyTempData()
			return

		if statusID != csstatus.CAN_ALLY:
			teammateList = [ e for e in self.entitiesInRangeExt( csconst.RELATION_ALLY_SWEAR_DISTANCE, 'Role' ) \
								if e.teamMailbox is not None \
								and e.teamMailbox.id == self.teamMailbox.id \
							]
			self.statusMessage( statusID )	# 通知所有玩家
			for player in teammateList:
				player.client.onStatusMessage( statusID, "" )
				#DEBUG_MSG( "statusID(%i)检查条件不通过，把原因通知玩家(%s)" % (statusID, player.getName()))
			self.rlt_removeAllyTempData()
			return

		ally_player_count -= 1
		if ally_player_count > 0:
			self.setTemp( "ally_player_count", ally_player_count )
		else:	# 如果是最后一个检查结果，那么进入结拜流程
			teammateList = [ e for e in self.entitiesInRangeExt( csconst.RELATION_ALLY_SWEAR_DISTANCE, 'Role' ) \
								if e.teamMailbox is not None \
								and e.teamMailbox.id == self.teamMailbox.id \
							]
			if len( DBIDList ) != len( teammateList ) + 1:
				#DEBUG_MSG( "--->>>玩家数量不对了，结拜不成功。" )
				self.rlt_removeAllyTempData()
				return

			if self.money < csconst.RELATION_ALLY_COST:
				#DEBUG_MSG( "帮你主持结拜仪式需要花费%i金，你身上金钱不足！" % ( csconst.RELATION_ALLY_COST/10000 ) )
				self.rlt_removeAllyTempData()
				return
			for itemInfo in csconst.RELATION_ALLY_NEED_ITEMS:
				item = self.findItemFromNKCK_( itemInfo[0] )
				if self.iskitbagsLocked() or item is None or item.isFrozen():
					#DEBUG_MSG( "---->>>>findItemFromNKCK_" )
					self.statusMessage( csstatus.CANNOT_ALLY_NO_ITEM )
					self.rlt_removeAllyTempData()
					return

			# 区别 新建结拜 和 加入新的结拜成员，不同的处理
			newPlayerDBIDList = self.queryTemp( "allyNewPlayerDBIDlist", [] )
			if newPlayerDBIDList:
				#DEBUG_MSG( "--->>>join new member..." )
				newAllyPlayer = []
				oldAllyPlayer = []
				for player in teammateList:
					playerDBID = player.databaseID
					if not self.checkAllyByDBID( playerDBID ):
						if player.databaseID not in newPlayerDBIDList:
							#DEBUG_MSG( "--->>>新玩家数据不匹配。" )
							self.rlt_removeAllyTempData()
							return
						if player.hasAllyRelation():
							self.statusMessage( csstatus.CANNOT_ALLY_HAD_ALREADY )
							#DEBUG_MSG( "义结金兰要诚心真意，每人只能结拜一次，新成员已经结拜过了。" )
							self.rlt_removeAllyTempData()
							return
						newAllyPlayer.append( player )
					else:
						oldAllyPlayer.append( player )
				if len( newAllyPlayer ) != len( newPlayerDBIDList ):
					self.rlt_removeAllyTempData()
					return
				for player in newAllyPlayer:
					tempDBIDList = DBIDList[:]
					tempDBIDList.remove( player.databaseID )
					player.rlt_allySuccess( tempDBIDList )
				for player in oldAllyPlayer:
					player.rlt_allySuccess( newPlayerDBIDList )
				self.base.rlt_joinNewAllyMember( newPlayerDBIDList )
				self.rlt_removeAllyTempData()
				self.payMoney( csconst.RELATION_ALLY_NEW_COST, csdefine.CHANGE_MONEY_ALLY )
			else:
				#DEBUG_MSG( "---->>>add new relation" )
				# 检查是否还满足条件
				for player in teammateList:
					if player.databaseID not in DBIDList:
						#DEBUG_MSG( "玩家对不上。" )
						self.rlt_removeAllyTempData()
						return
					if player.hasAllyRelation():
						#DEBUG_MSG( "义结金兰要成心真意，每人只能结拜一次。请检查队伍中谁拥有结拜关系。" )
						self.rlt_removeAllyTempData()
						return

				# 所有条件检查通过，此时结拜成功
				for player in teammateList:
					tempDBIDList = DBIDList[:]
					tempDBIDList.remove( player.databaseID )
					player.rlt_allySuccess( tempDBIDList )
				self.addTitle( csdefine.TITLE_ALLY_ID )	# 获得结义称号
				#DEBUG_MSG( "--->>>喊出我们的口号。" )
				DBIDList.remove( self.databaseID )
				self.base.rlt_startAlly( DBIDList )	# 由队长把结拜关系写入db
				self.rlt_removeAllyTempData()
				self.payMoney( csconst.RELATION_ALLY_COST, csdefine.CHANGE_MONEY_ALLY )
			for itemInfo in csconst.RELATION_ALLY_NEED_ITEMS:
				self.removeItemTotal( itemInfo[0], itemInfo[1], csdefine.DELETE_ITEM_ALLY )

	def rlt_removeAllyTempData( self ):
		"""
		清除结拜临时数据
		"""
		self.removeTemp( "ally_player_count" )
		self.removeTemp( "ally_player_dbid_list" )
		self.removeTemp( "allyNewPlayerDBIDlist" )

	def rlt_allySuccess( self, DBIDList ):
		"""
		Define method.
		结拜成功，设置cell数据
		"""
		self.addTitle( csdefine.TITLE_ALLY_ID )	# 获得结义称号
		#DEBUG_MSG( "--->>>喊出我们的口号。" )
		self.base.rlt_allySuccess( DBIDList )

	def rlt_newMemberJoinAlly( self, srcEntityID ):
		"""
		Exposed method.
		请求加入新的结拜成员
		"""
		if self.id != srcEntityID:
			return

		if self.queryTemp( "ally_player_count", 0 ):
			#DEBUG_MSG( "---->>>正在申请结拜中" )
			return
		if not self.isInTeam():
			#DEBUG_MSG( "想要结拜就你的兄弟组队一起来啊！一个人不能结拜。111" )
			return
		if not self.isTeamCaptain():
			#DEBUG_MSG( "让队长来和我说吧，你们这样一群人一起来，太混乱了！" )
			return
		teammateList = [ e for e in self.entitiesInRangeExt( csconst.RELATION_ALLY_SWEAR_DISTANCE, 'Role' ) \
							if e.teamMailbox is not None \
							and e.teamMailbox.id == self.teamMailbox.id \
						]
		nearMemberNum = len( teammateList )
		if nearMemberNum < 2:
			self.statusMessage( csstatus.CANNOT_ADD_NEW_LACK_MEMBER )
			#DEBUG_MSG( "人员不齐整啊你们，召集所有兄弟再过来。" )
			return
		if self.getTeamCount() > nearMemberNum+1 or nearMemberNum <= len( self.allyPlayers ):
			self.statusMessage( csstatus.CANNOT_ADD_NEW_LACK_MEMBER )
			#DEBUG_MSG( "人员不齐整啊你们，召集所有兄弟再过来。" )
			return

		oldAllyDBIDList = []
		oldAllyPlayer = []
		allyDBIDList = []
		newAllyDBIDList = []
		newAllyPlayer = []
		for player in teammateList:
			playerDBID = player.databaseID
			if self.checkAllyByDBID( playerDBID ):
				oldAllyDBIDList.append( playerDBID )
				oldAllyPlayer.append( player )
			else:
				newAllyDBIDList.append( playerDBID )
				newAllyPlayer.append( player )
				if player.level < csconst.RELATION_ALLY_LEVEL_LACK:
					self.statusMessage( csstatus.CANNOT_ALLY_LACK_LEVEL, player.getName(), csconst.RELATION_ALLY_LEVEL_LACK )
					#DEBUG_MSG( "[%s]等级太低了，%i级以上的人才能结拜！" % ( player.getName(), csconst.RELATION_ALLY_LEVEL_LACK ) )
					return
				if player.hasAllyRelation():
					self.statusMessage( csstatus.CANNOT_ALLY_HAD_ALREADY )
					#DEBUG_MSG( "义结金兰要诚心真意，每人只能结拜一次，新成员(%s)已经结拜过了。" % player.getName() )
					return
			allyDBIDList.append( playerDBID )
		if len( oldAllyDBIDList ) != len( self.allyPlayers ):
			self.statusMessage( csstatus.CANNOT_ADD_NEW_LACK_MEMBER )
			#DEBUG_MSG( "人员不齐整啊你们，召集所有兄弟再过来。" )
			return

		oldAllyPlayer.append( self )	# 加入自己
		allyDBIDList.append( self.databaseID )
		for player in oldAllyPlayer:
			player.base.rlt_requestAlly( self.base, newAllyDBIDList )
		for player in newAllyPlayer:
			DBIDList = allyDBIDList[:]
			DBIDList.remove( player.databaseID )
			player.base.rlt_requestAlly( self.base, DBIDList )

		self.setTemp( "allyNewPlayerDBIDlist", newAllyDBIDList )
		self.setTemp( "ally_player_count", len( allyDBIDList ) )
		self.setTemp( "ally_player_dbid_list", allyDBIDList )

	def checkAllyByDBID( self, playerDBID ):
		"""
		是否我的盟友
		"""
		for item in self.allyPlayers:
			if item["playerDBID"] == playerDBID:
				return True
		return False

	def checkAllyByID( self, entityID ):
		for item in self.allyPlayers:
			playerBase = item["playerBase"]
			if playerBase and playerBase.id == entityID:
				return True
		return False

	def receiveAllyInfo( self, relationItem ):
		"""
		Define method.
		接收玩家结拜数据

		@param relationItem: {"playerDBID":playerDBID,"playerBase":baseMailbox}
		"""
		self.allyPlayers.append( relationItem )

	def rlt_changeAllyTitle( self, srcEntityID, newTitleName ):
		"""
		Exposed method.
		玩家申请更改结拜称号
		"""
		if srcEntityID != self.id:
			return

		if not self.hasAllyRelation():
			return
		if not self.isTeamCaptain():
			return
		if self.money < csconst.ALLY_CHANGE_TITLE_COST:
			#DEBUG_MSG( "办手续是要交费的！请准备好5金再来改名！" )
			return
		teammateList = [ e for e in self.entitiesInRangeExt( csconst.RELATION_ALLY_SWEAR_DISTANCE, 'Role' ) \
							if e.teamMailbox is not None \
							and e.teamMailbox.id == self.teamMailbox.id \
						]
		if len( self.allyPlayers ) > len( teammateList ):
			self.statusMessage( csstatus.CANNOT_ADD_NEW_LACK_MEMBER )
			#DEBUG_MSG( "是不是有兄弟没来啊，让他赶快过来。" )
			return
		if set( [player.databaseID for player in teammateList] ) != set( [item["playerDBID"] for item in self.allyPlayers] ):
			self.statusMessage( csstatus.ALLY_CANNOT_WRONG_PLAYER )
			#DEBUG_MSG( "队伍里怎么有不相干的人？" )
			return

		# 是否有违禁词汇的检查，客户端先检查
		if not g_chatProfanity.isPureString( newTitleName ) :
			# "名称不合法！"
			return
		elif g_chatProfanity.searchNameProfanity( newTitleName ) is not None :
			# "输入的名字有禁用词汇!"
			return

		self.payMoney( csconst.ALLY_CHANGE_TITLE_COST, csdefine.CHANGE_MONEY_ALLY )
		self.base.rlt_changeAllyTitle( newTitleName )

	def rlt_quitAlly( self, srcEntityID ):
		"""
		Exposed method.
		退出结拜
		"""
		if self.id != srcEntityID:
			return

		if not self.hasAllyRelation():
			return

		self.removeTitle( csdefine.TITLE_ALLY_ID )
		self.allyPlayers = []
		self.base.rlt_quitAlly()

	def rlt_memberQuitAlly( self, playerDBID ):
		"""
		Define method.
		有人退出结拜，更新自己的结拜关系数据
		"""
		for index, relationItem in enumerate( self.allyPlayers ):
			if relationItem["playerDBID"] == playerDBID:
				self.allyPlayers.pop( index )
				break

	def rlt_disbandAlly( self ):
		"""
		Define method.
		结拜关系解散了。
		"""
		self.removeTitle( csdefine.TITLE_ALLY_ID )
		self.allyPlayers = []
		self.base.rlt_disbandAlly()

	def onAllyTitleChanged( self, newTitleName ):
		"""
		Define method.
		结拜称号改变了
		"""
		if self.title == csdefine.TITLE_ALLY_ID:
			self.titleName = newTitleName

	def teach_enterKillMonsterSpaceSuccess( self ):
		"""
		Define method.
		"""
		localtime = time.localtime()
		# 下次能参与副本活动的时间
		canJoinTime = 24*3600 - localtime[3] * 3600 - localtime[4] * 60 - localtime[5] + time.time()
		self.set( "teachSpaceKillMonsterTime", int(canJoinTime) )

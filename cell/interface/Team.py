# -*- coding: gb18030 -*-
#
# $Id: Team.py,v 1.40 2008-08-20 01:23:03 zhangyuxing Exp $

import BigWorld
import csstatus
from bwdebug import *
import csconst
import Const
import csdefine
from TeamRegulation import *
from SlaveDart import SlaveDart
from ObjectScripts.GameObjectFactory import g_objFactory
import ECBExtend
import random


class Team:
	def __init__( self ):
		self.teamMembers = []		# 队伍成员：[{"dbID" : 12345, "mailbox" : MAILBOX}, ... ]
		self.captainID = 0			# 队长ID
		self.teamMailbox = None		# 队伍的MAILBOX
		self.pickUpState = csdefine.TEAM_PICKUP_STATE_FREE

		self.pickRegulation = g_pRMgr.createRegulaiton( TEAM_FREE_PICK )
		self.pickRegulation.init( self )
		self.leaveTeamTimer = 0

	# ---------------------------------------------------------------------
	# protected
	# ---------------------------------------------------------------------
	def onAddBuff( self, buff ) :
		"""
		当增加一个 buff 时被调用(将我添加的 buff 发送给所有队友）
		by hyw -- 2008.09.23
		"""
		for member in self.teamMembers :
			member["mailbox"].client.team_onMemberAddBuff( self.id, buff )

	def onRemoveBuff( self, buff ) :
		"""
		删除一个 buff 时被调用（将我删除的 buff 通知告诉所有队友）
		by hyw -- 2008.09.23
		"""
		for member in self.teamMembers :
			member["mailbox"].client.team_onMemberRemoveBuff( self.id, buff[ "index" ] )

	def onUpdateBuff( self, index, buff ) :
		"""
		当某个 buff 更新时被调用（将我更新的 buff 告诉所有队友）
		by hyw -- 2008.09.23
		"""
		for member in self.teamMembers :
			member["mailbox"].client.team_onMemberUpdateBuff( self.id, index, buff )

	def onPetAddBuff( self, buff ):
		"""
		当增加一个 buff 时被调用(将我的宠物添加的 buff 发送给所有队友）
		"""
		for member in self.teamMembers :
			member["mailbox"].client.team_onMemberPetAddBuff( self.id, buff )

	def onPetRemoveBuff( self, buff ):
		"""
		当增加一个 buff 时被调用(将我的宠物移除的 buff 通知所有队友）
		"""
		for member in self.teamMembers :
			member["mailbox"].client.team_onMemberPetRemoveBuff( self.id, buff )

	def onPetConjureNotifyTeam( self, id, uname, name, modelNumber, species ):
		"""
		宠物召唤出，通知队友
		"""
		for member in self.teamMembers :
			member["mailbox"].client.team_onPetConjureNotify( self.id, id, uname, name, modelNumber, species )

	def onPetWithdrawNotifyTeam( self ):
		"""
		宠物收回通知队友
		"""
		for member in self.teamMembers :
			member["mailbox"].client.team_onPetWithdrawNotify( self.id )

	# ---------------------------------------------------------------------
	# public
	# ---------------------------------------------------------------------
	def teamInviteFC( self, srcEntityID, playerID ):
		"""
		exposed method.
		邀请玩家组队

		过程：
		　查找玩家CELL，邀请玩家组队

		@param playerID: 玩家的EntityID
		@type playerID: OBJECT_ID
		"""
		if srcEntityID != self.id:
			return

		# 挑战副本的条件限制
		if self.isInSpaceChallenge():
			if self.query( "challengeSpaceType", 0 ) == csconst.SPACE_CHALLENGE_TYPE_MANY:
				if len( self.teamMembers ) >= csconst.SPACE_CHALLENGE_TEAM_MEMBER_MAX:
					self.statusMessage( csstatus.CHALLENGE_SPACE_MANY_MEM_FULL )
					return

			elif self.query( "challengeSpaceType", 0 ) == csconst.SPACE_CHALLENGE_TYPE_SINGLE:
				self.statusMessage( csstatus.CHALLENGE_SPACE_PERSONAL_INVITE_TEAM )
				return

		objPlayer = BigWorld.entities.get( playerID )
		if objPlayer is None:
			#ERROR_MSG( "Not Find Player Entity!")
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_EXIST )		# defined in Role.py
			return

		if objPlayer.isState( csdefine.ENTITY_STATE_PENDING ):
			return

		if objPlayer.isState( csdefine.ENTITY_STATE_QUIZ_GAME ):
			return

		if objPlayer.qieCuoState != csdefine.QIECUO_NONE:
			self.statusMessage( csstatus.TARGET_IS_QIECUO )
			return
		
		if not self.getCurrentSpaceScript().isDiffCampTeam and objPlayer.getCamp() != self.getCamp():
			self.statusMessage( csstatus.TEAMATE_CAMP_DIFFERENT )
			return

		if csconst.TEAM_MEMBER_MAX <= len( self.teamMembers ):
			self.statusMessage( csstatus.TEAM_FULL )
			return

		# 不允许邀请自己
		if self.id == playerID:
			self.statusMessage( csstatus.TEAM_NOT_INVITE_SELF )
			return

		if objPlayer.isInTeam():
			return

		if not self.isInTeam() or self.isTeamCaptain():
			objPlayer.base.teamInviteBy( self.base, self.getName(), self.getCamp() )
		else:
			captainMB = self.getTeamCaptainMailBox()
			if captainMB:
				captainMB.client.teamInviteByTeammate( objPlayer.getName(), objPlayer.id, self.getName(), self.id )

	def requestJoinTeamNear( self, srcEntityID ):
		"""
		Exposed method.
		对方请求加队
		"""
		if self.id == srcEntityID:
			HACK_MSG( "player( %s ) cannot join own team." % self.getName() )
			return

		if not self.isInTeam():
			return

		objPlayer = BigWorld.entities.get( srcEntityID )
		if objPlayer is None:
			return
		
		if not self.getCurrentSpaceScript().isDiffCampTeam and objPlayer.getCamp() != self.getCamp():
			objPlayer.client.onStatusMessage( csstatus.TEAMATE_CAMP_DIFFERENT, "" )
			return

		if not self.isTeamCaptain():
			captainMB = self.getTeamCaptainMailBox()
			if captainMB:
				captainMB.receiveJoinTeamRequest( objPlayer.getName(), objPlayer.raceclass, objPlayer.getLevel(), objPlayer.base )
		else:
			self.base.receiveJoinTeamRequest( objPlayer.getName(), objPlayer.raceclass, objPlayer.getLevel(), objPlayer.base )

	def acceptTeamRequestNear( self, srcEntityID, targetID ):
		"""
		Exposed method.
		接受对方的加队请求，对方和自己在同一个cellApp

		@param targetID : 发起加队请求的玩家id
		@type targetID : OBJECT_ID
		"""
		if srcEntityID != self.id:
			return
		if targetID == self.id:
			return
		if not self.isTeamCaptain():
			return
		try:
			targetPlayer = BigWorld.entities[targetID]
		except KeyError:
			return
		targetPlayer.base.captainAcceptTeamRequest( self.base )

	def refusePlayerJoinTeam( self, srcEntityID, targetID ):
		"""
		Exposed method.
		拒绝对方的加队请求，对方和自己在同一个cellApp

		@param targetID : 发起加队请求的玩家id
		@type targetID : OBJECT_ID
		"""
		if srcEntityID != self.id:
			return
		if self.targetID == self.id:
			return
		if not self.isTeamCaptain():
			return
		try:
			targetPlayer = BigWorld.entities[targetID]
		except KeyError:
			return
		targetPlayer.client.onStatusMessage( csstatus.TEAM_REQUEST_FORBID, "( \'%s\', )" % self.getName() )
		self.base.addFobidTeamPlayer( targetPlayer.id )

	#---------------------------------------------------------------------------------
	def teamInviteBy( self, inviterBase, inviterName, inviterCamp ):
		"""
		define method.
		被某玩家邀请组队
		"""
		if self.qieCuoState != csdefine.QIECUO_NONE:
			inviterBase.client.onStatusMessage( csstatus.TARGET_IS_QIECUO, "" )
			return
		
		if not self.getCurrentSpaceScript().isDiffCampTeam and inviterCamp != self.getCamp():
			inviterBase.client.onStatusMessage( csstatus.TEAMATE_CAMP_DIFFERENT, "" )
			return

		self.base.teamInvitedToBy( inviterBase, inviterName )

	def teamInviteByTeammate( self, name, target ):
		"""
		define method.
		队友邀请目标玩家入队
		"""
		try:
			targetPlayer = BigWorld.entities[target.id]
		except KeyError:
			return
		if targetPlayer.qieCuoState != csdefine.QIECUO_NONE:
			self.client.onStatusMessage( csstatus.TARGET_IS_QIECUO, "" )
			return

		self.base.teamInviteByTeammate( name, target )

	def addTeamMember( self, dbid, playerBase ):
		"""
		define method.
		发送成员数据

		过程：
		　向成员列表里添加成员

		@param dbid: player.databaseID
		@type dbid: DATABASE_ID
		@param playerBase: 玩家BASE
		@type playerBase: mailbox
		"""
		# 添加成员
		self.teamMembers.append( { "dbID" : dbid, "mailbox" : playerBase } )
		for buff in self.attrBuffs :											# 将我的 buff 列表发送给新进来队友（hyw--2008.09.24）
			playerBase.client.team_onMemberAddBuff( self.id, buff )
		actPet = self.pcg_getActPet()
		if actPet:
			pet = actPet.entity
			playerBase.client.addTeamMemberPet( self.id, pet.id, pet.uname, pet.name, pet.modelNumber, pet.species )
			for buff in pet.attrBuffs:		# 将自己宠物buff发送给新进来的队友
				playerBase.client.team_onMemberPetAddBuff( self.id, buff )
		self.cmi_onTeammateJoin( playerBase )

	def removeTeamMember( self, playerID ):
		"""
		define method.
		玩家离开
		playerID为自己时,disemploy为True自己被开除,False队伍解散

		过程：
			从成员列表中删除玩家记录
			通知cell，指定玩家离开

		@param playerID: 玩家的EntityID
		@type playerID: OBJECT_ID
		"""
		if playerID == self.id:
			# 如果玩家在天关里面，要判断是否要退出天关
			#spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
			#g_objFactory.getObject( spaceLabel ).onLeaveTeam( self )

			# 自己离队，等于队伍解散
			self.disbandTeamNotify()
		else:
			# 成员离队
			for index, e in enumerate( self.teamMembers ):
				if e["mailbox"].id == playerID:
					self.teamMembers.pop( index )
					return



	def disbandTeamNotify( self ):
		"""
		define method.
		队伍解散通知，此方法由self.base调用
		"""
		if self.isTeamFollowing():
			self.cancelTeamFollow()
			
		spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		g_objFactory.getObject( spaceLabel ).onLeaveTeam( self )
		self.teamInfoNotify( 0, None )
		self.teamMembers = []
		self.pft_onLeaveTeam()
		self.ei_onLevelTeam()
		self.cmi_onLeaveTeam()
		self.dt_onLeaveTeam()	# 天命轮回副本

	def teamInfoNotify( self, captainID, teamMailbox ):
		"""
		define method.
		通知队伍信息

		@param captainID: 队长玩家的EntityID
		@type captainID: OBJECT_ID
		@param teamMailbox: 队伍BASE
		@type teamMailbox: mailbox
		"""
		self.teamMailbox = teamMailbox
		self.captainID = captainID
		if self.teamMailbox:
			self.addFlag( csdefine.ROLE_FLAG_TEAMMING )
		else:
			self.removeFlag( csdefine.ROLE_FLAG_TEAMMING )
		# 通过设置标记，通知客户端玩家头顶标记发生变化
		if self.id == captainID:
			if not self.hasFlag( csdefine.ROLE_FLAG_CAPTAIN ) :
				self.addFlag( csdefine.ROLE_FLAG_CAPTAIN )			# 设置队长标记
		elif self.hasFlag( csdefine.ROLE_FLAG_CAPTAIN ) :
			self.removeFlag( csdefine.ROLE_FLAG_CAPTAIN )			# 去掉队长标记
		if self.teamMailbox:
			self.ei_joinTeam()
		else:
			self.ei_onLevelTeam()

	def changeCaptainNotify( self, captainID ):
		"""
		define method.
		队长改变

		@param captainID: 队长ID
		@type captainID: OBJECT_ID
		"""
		self.captainID = captainID
		if self.isTeamCaptain():
			self.removeFlag( csdefine.ROLE_FLAG_CAPTAIN )
			if self.isTeamFollowing():
				self.effectStateDec( csdefine.EFFECT_STATE_LEADER )		# 队长改变后，原队长清除引导效果状态
				newCaptain = BigWorld.entities.get( captainID )
				if newCaptain is not None and newCaptain.isTeamFollowing():
					self.effectStateInc( csdefine.EFFECT_STATE_FOLLOW )
					self.actCounterInc( Const.FOLLOW_STATES_ACT_WORD )
					self.spellTarget( csconst.FOLLOW_SKILL_ID, self.id )
					return
		elif self.id == captainID:
			self.addFlag( csdefine.ROLE_FLAG_CAPTAIN )
			if self.isTeamFollowing():
				self.removeAllBuffByID( csconst.FOLLOW_BUFF_ID, [ csdefine.BUFF_INTERRUPT_ON_DIE ] )
				self.effectStateDec( csdefine.EFFECT_STATE_FOLLOW )
				self.effectStateInc( csdefine.EFFECT_STATE_LEADER )
				self.actCounterDec( Const.FOLLOW_STATES_ACT_WORD )

	#---------------------------------------------------------------------------------
	# msg request
	def requestTeammateInfo( self, objPlayerBase ):
		"""
		取状态

		过程：
		　反回状态给玩家

		@param objPlayerBase: 玩家BASE
		@type objPlayerBase: mailbox
		"""
		spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		objPlayerBase.client.teammateInfoNotify( self.id, self.level, self.HP, self.HP_Max, self.MP, self.MP_Max, 0, spaceLabel, self.position, self.spaceID )# buff

	def requestTeammatePetInfo( self, objPlayerBase ):
		"""
		取状态

		过程：
		　反回状态给玩家

		@param objPlayerBase: 玩家BASE
		@type objPlayerBase: mailbox
		"""
		spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		actPet = self.pcg_getActPet()
		if actPet:
			if actPet.etype == "MAILBOX":
				return
			pet = actPet.entity
			objPlayerBase.client.teammatePetInfoNotify( self.id, pet.id, pet.uname, pet.name, pet.level, pet.HP, pet.HP_Max, pet.MP, pet.MP_Max, 0, pet.modelNumber, pet.species )

	#---------------------------------------------------------------------------------
	# interface
	def teamMemberName2client( self, baseMailbox ):
		"""
		发送自身名字给队伍成员

		@param baseMailbox: 目标队友base mailbox
		@type  baseMailbox: MAILBOX
		@return:            None
		"""
		baseMailbox.client.teammateNameChange( self.id, self.playerName )

	def teamMemberLevel2client( self, baseMailbox ):
		"""
		发送自身等级给队伍成员

		@param baseMailbox: 目标队友base mailbox
		@type  baseMailbox: MAILBOX
		@return:            None
		"""
		baseMailbox.client.teammateLevelChange( self.id, self.level )

	def isTeamCaptain( self ):
		"""
		判断我是否队长，
		非声明方法。

		@return: 是队长则返回True，否则返回False；未加入队伍视为非队长
		@rtype:  BOOL
		"""
		return self.hasFlag( csdefine.ROLE_FLAG_CAPTAIN )

	def getTeamCount( self ):
		"""
		取得队伍成员数量

		@return: 队伍成员数量
		@rtype:  UINT8
		"""
		return len( self.teamMembers )

	def getAllMemberInRange( self, range, position = None ):
		"""
		判断是否所有的队员都在同一范围内

		@param    range: 范围(半径)
		@type     range: FLOAT
		@param position: 位置中心点，该位置和半径所组合出的范围不能超过玩家的AOI，否则结果不一定是正确的；
		                 如果该值为None则表示以自己为中心。
		@type  position: VECTOR3
		@return:         同一范围内所有队伍成员列表，如果没有队伍则返回一个空列表
		@rtype:          ARRAY of Entity
		"""
		if len( self.teamMembers ) == 0:
			return []

		if position is None:
			position = self.position
		members = []
		for e in self.teamMembers:
			entityID = e["mailbox"].id
			entity = BigWorld.entities.get( entityID )
			if not entity or entity.spaceID != self.spaceID:
				continue
			if entity.position.flatDistTo( position ) <= range:
				members.append( entity )
		return members

	def getAllIDNotInRange( self, range, position = None ):
		"""
		返回不在同一个范围内成员的id
		"""
		teamMemberIDs = self.getTeamMemberIDs()
		allMemberInRange = self.getAllMemberInRange( range, position )

		for member in allMemberInRange:
			teamMemberIDs.remove( member.id )

		return teamMemberIDs

	def allMemberIsInRange( self, range, position = None ):
		"""
		判断是否所有的队员都在同一范围内

		@param    range: 范围(半径)
		@type     range: FLOAT
		@param position: 位置中心点，该位置和半径所组合出的范围不能超过玩家的AOI，否则结果不一定是正确的；
		                 如果该值为None则表示以自己为中心。
		@type  position: VECTOR3
		@return:         有队伍且所有队员在同一范围内则返回True，否则返回False
		@rtype:          BOOL
		"""
		return len( self.getAllMemberInRange(range, position) ) == self.getTeamCount()

	def getTeamCaptain( self ):
		"""
		取得队长的entity

		@return: 如果已经组队则在被调用者当前所在的cellApp上找到了队长的entity则返回队长的Entity实例，否则返回None
		@rtype:  Entity/None
		"""
		return BigWorld.entities.get( self.captainID )

	def getTeamCaptainDBID( self ):
		"""
		取得队长的dbid
		@return: DATABASE_ID
		"""
		for e in self.teamMembers:
			if e["mailbox"].id == self.captainID:
				return e["dbID"]
		return 0L

	def getTeamCaptainMailBox( self ):
		"""
		"""
		for e in self.teamMembers:
			if e["mailbox"].id == self.captainID:
				return e["mailbox"]

		return None


	def getTeamMemberDBIDs( self ):
		"""
		获取队伍所有人的dbid
		@return: ARRAY of DATABASE_ID
		"""
		return [ e["dbID"] for e in self.teamMembers ]

	def getTeamMemberIDs( self ):
		"""
		获取队伍所有人的id
		@return: ARRAY of OBJECT_ID
		"""
		return [ e["mailbox"].id for e in self.teamMembers ]

	def getTeamMemberMailboxs( self ):
		"""
		获取队伍所有人的mailbox
		@return: ARRAY of MAILBOX
		"""
		return [ e["mailbox"] for e in self.teamMembers ]

	def getTeamMailbox( self ) :
		"""
		获取所在队伍( hyw )
		"""
		return self.teamMailbox

	def isInTeam( self ):
		"""
		判断自己是否在队伍里

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.hasFlag( csdefine.ROLE_FLAG_TEAMMING )

	def isCaptain( self ):
		"""
		是不是队长
		"""
		return self.captainID == self.id

	def isTeamMember( self, entity ):
		"""
		判断一个entity是否为我的队友
		"""
		return self.teamMailbox != None and entity.teamMailbox != None and entity.teamMailbox.id == self.teamMailbox.id

	def getTeamMemberJoinOrder( self, entityID ):
		"""
		获取队友加入顺序
		"""
		for index, e in enumerate( self.teamMembers ):
			if e["mailbox"].id == entityID:
				return index
		return None

	def changePickUpStateNotify( self, state ):
		"""
		define method.
		更改物品拾取方式通知

		@param state: 更改的拾取方式 define in csdefine.py
		@type state: INT8
		"""
		self.pickUpState = state
		if self.pickUpState == csdefine.TEAM_PICKUP_STATE_ORDER:
			self.rollState = True
		self.pickRegulation = g_pRMgr.createRegulaiton( state )

	def onChangeLastPickerNotify( self, teamMembers, entityID ):
		"""
		通知范围内的所有entity，最后一个拾取者属性改变
		"""
		for e in teamMembers:
			e.onChangePickUpOrder( entityID )

	def onChangePickUpOrder( self, entityID ):
		"""
		Define Method
		更新队伍最后一次拾取者的ID，
		此方法并不是所有的队伍成员都会调用，在怪物死亡后，怪物一定范围内的队伍
		成员都会调用此方法。而不在范围内的队伍成员是不会调用此方法。
		@param entityID: 队伍成员ID
		@type entityID: entityID
		"""
		self.lastPickUpID = entityID

	def getFreePickerIDs( self ):
		"""
		获取自由拾取方式下拥有者
		"""
		return self.getTeamMemberIDs()

	def getOrderPickerID( self, teamMembers ):
		"""
		获取顺序拾取方式下拥有者
		获取范围内队友顺序拾取者ID
		"""
		nextIndex = None
		for index, e in enumerate( self.teamMembers ):
			if e["mailbox"].id == self.lastPickUpID:
				nextIndex = index + 1
				if nextIndex >= len( self.teamMembers ):
					nextIndex = 0
				break
		# 如果记录的ID不在队伍里，则重新设置起始顺序为队长
		if nextIndex is None:
			return self.captainID
		newTeamMembers = self.teamMembers[nextIndex:] + self.teamMembers[:nextIndex]
		for e in newTeamMembers:
			entityID = e["mailbox"].id
			entity = BigWorld.entities.get( entityID )
			if entity is None: continue
			if entity not in teamMembers: continue
			return entityID

		# 一般不会执行到这里，如果执行到这里，那么拾取者为自身
		return self.id

	def statusTeamMessage( self, *args ) :
		"""
		"""
		teammates = self.getAllMemberInRange( csconst.ROLE_AOI_RADIUS )	# 只给自己AOI范围内的玩家发送消息
		for entity in teammates:
			if entity.isReal():
				entity.statusMessage( *args )
			else:
				entity.remoteCall( "statusMessage", args )

	def team_notifyKillMessage( self, victim ) :
		"""
		通知队伍的其他人victim被我杀了
		@param		victim : 被杀者
		@type		cictim : entity
		"""
		teammates = self.getAllMemberInRange( csconst.ROLE_AOI_RADIUS )	# 只给自己AOI范围内的玩家发送消息
		for entity in teammates :
			if entity.id == self.id : continue					# 不给自己发送
			if entity.id == victim.id : continue				# 不给受害者发送
			if entity.isReal() :
				if victim.isEntityType( csdefine.ENTITY_TYPE_ROLE ):	# 如果死亡的是玩家
					entity.statusMessage( csstatus.ROLE_STATE_KILL_DEAD_BY_TEAMMATE, victim.getName(), self.getName() )
				else:
					entity.statusMessage( csstatus.ACCOUNT_STATE_KILL_BY, victim.getName(), self.getName() )
			else:
				if victim.isEntityType( csdefine.ENTITY_TYPE_ROLE ):	# 如果死亡的是玩家
					entity.remoteCall( "statusMessage", ( csstatus.ROLE_STATE_KILL_DEAD_BY_TEAMMATE, victim.getName(), self.getName() ) )
				else:
					entity.remoteCall( "statusMessage", ( csstatus.ACCOUNT_STATE_KILL_BY, victim.getName(), self.getName() ) )

	def team_notifyKilledMessage( self, killer ) :
		"""
		通知队伍里的人，我被killer杀了
		@param		killer : killer entity
		"""
		if not self.isInTeam() : return
		statusMsgID = 0
		msgParam = ""
		if killer is None :
			msgParam = "(\'%s\',)" % self.getName()
			statusMsgID = csstatus.ACCOUNT_STATE_DEAD
		else :
			msgParam = "(\'%s\',\'%s\')" % ( self.getName(), killer.getName() )
			if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
				statusMsgID = csstatus.ROLE_BE_KILLED_BY_ROLE
			else :
				statusMsgID = csstatus.ROLE_BE_KILLED_BY_MONSTER

		for tmDict in self.teamMembers :
			if tmDict["dbID"] == self.databaseID : continue		# 不给自己发送
			tmMailbox = tmDict["mailbox"]
			if tmMailbox is None or ( killer is not None and tmMailbox.id == killer.id ): continue				# 不给杀手发送
			if hasattr( tmMailbox, "client" ) :
				tmMailbox.client.onStatusMessage( statusMsgID, msgParam )

	def setTeamPickRegulationVal1( self, val ):
		"""
		"""
		self.pickRegulation.val1 = val


	def setTeamPickRegulationVal2( self, val ):
		"""
		"""
		self.pickRegulation.val2 = val


	def selectTeamPickRegulation( self, srcEntityID, pType ):
		"""
		exposed method

		选择队伍拾取规则
		"""
		if srcEntityID != self.id:
			return
		if not self.isInTeam():
			return
		if not self.isTeamCaptain():
			return

		self.teamMailbox.selectTeamPickRegulation( pType )


	def addTeamMembersTasksItem( self, id, className ):
		"""
		define method
		增加组队人员任务物品处理
		"""
		if not self.isInTeam():
			return
		membersID = []
		for member in self.getAllMemberInRange( DISTANCE_ATTENTION ):
			membersID.append( member.id )
  			entity = BigWorld.entities.get(member.id, None)
  			if entity is not None:
				entity.addTasksItem( id, className )
		entity = BigWorld.entities.get( id, None )
		if entity is not None:
			entity.addTeamMembersID( membersID )


	def buildBoxOwners( self, id, itemBox ):
		"""
		define method
		建立物品和对应的所有者关系
		"""
		self.pickRegulation.setItemsOwners( id, self, itemBox )


	def changePickUpQualityNotify( self, val ):
		"""
		define method
		修改拾取规则中的品质限定
		"""
		self.pickRegulation.val2 = val
		self.client.changePickUpQuality( val )


	def changeRollQualityNotify( self, val ):
		"""
		define method
		修改Roll拾取规则中的品质限定
		"""
		self.pickRegulation.val2 = val
		self.client.changeRollQuality( val )

	# -----------------------------------------------------------------------------------------
	# 组队跟随，13:50 2009-3-13，wsf
	# -----------------------------------------------------------------------------------------
	def leadTeam( self, srcEntityID ):
		"""
		Exposed method.
		队长发起组队跟随。
		"""
		if not self.hackVerify_( srcEntityID ):
			return

		if not self.isTeamCaptain():
			HACK_MSG( "--->>>Player( %s ) isn't captain!" % self.getName() )
			return

		if not self.isTeamFollowing():
			self.effectStateInc( csdefine.EFFECT_STATE_LEADER )
			#self.spellTarget( csconst.FOLLOW_SKILL_ID, self.id )
			self.getTeamMailbox().startFollow()

		for entity in self.entitiesInRangeExt( csconst.TEAM_FOLLOW_DISTANCE, "Role", self.position ):
			if entity.captainID == self.id and entity.spaceID == self.spaceID and not entity.isTeamFollowing():
				if entity.vehicle and entity.vehicle.__class__ == SlaveDart:
					continue

				entity.client.team_requestFollow()



	def team_replyForFollowRequest( self, srcEntityID, reply ):
		"""
		Exposed method.
		组队跟随的回复

		@param reply : True or False
		"""
		if not self.hackVerify_( srcEntityID ):
			return

		captainEntity = self.getTeamCaptain()
		if captainEntity is None or self.id == self.captainID:
			return
		if not captainEntity.isLeadTeam():
			return
		if self._isVend():
			reply = False
			self.statusMessage( csstatus.TEAM_FOLLOW_CANT_VEND )
		elif self.effect_state & csdefine.EFFECT_STATE_SLEEP:
			reply = False
			self.statusMessage( csstatus.TEAM_FOLLOW_CANT_SLEEP )
		elif self.effect_state & csdefine.EFFECT_STATE_VERTIGO:
			reply = False
			self.statusMessage( csstatus.TEAM_FOLLOW_CANT_VERTIGO )
		elif self.effect_state & csdefine.EFFECT_STATE_FIX:
			reply = False
			self.statusMessage( csstatus.TEAM_FOLLOW_CANT_FIX )
		elif self.position.distTo( captainEntity.position ) > csconst.TEAM_FOLLOW_DISTANCE:	# 有可能队长此时已经远去
			reply = False

		if not reply:
			self.teamStatusMessage( captainEntity, csstatus.TEAMATE_FOLLOW_REPLY_FALSE, self.getName() )
			return

		entity = BigWorld.entities.get( srcEntityID, None)
		if entity and entity.vehicle and entity.vehicle.__class__ == SlaveDart:
			return

		self.effectStateInc( csdefine.EFFECT_STATE_FOLLOW )
		self.actCounterInc( Const.FOLLOW_STATES_ACT_WORD )
		self.spellTarget( csconst.FOLLOW_SKILL_ID, self.id )
		self.getTeamMailbox().followCaptain( self.id )
		self.teamStatusMessage( captainEntity, csstatus.TEAMATE_FOLLOW_SUCCESS, self.getName() )

	def teamStatusMessage( self, targetBase, statusID, *args ):
		"""
		队伍系统消息提示
		"""
		args = args == () and "" or str( args )
		targetBase.client.onStatusMessage( statusID, args )

	def team_cancelFollow( self, srcEntityID ):
		"""
		Exposed method.
		玩家退出跟随
		"""
		if not self.isInTeam():
			return
		if not self.hackVerify_( srcEntityID ):
			return
		if self.isTeamCaptain():
			return
		if not self.isTeamFollowing():
			return

		self.cancelTeamFollow()
		self.getTeamMailbox().cancelFollow( self.id )	# 主动退出需通知TeamEntity

	def cancelTeamFollow( self ):
		"""
		Define method.
		退出组队跟随
		"""
		if not self.isTeamFollowing():
			self.removeAllBuffByID( csconst.FOLLOW_BUFF_ID, [ csdefine.BUFF_INTERRUPT_ON_DIE ] )
			return
		if self.isTeamCaptain():
			self.effectStateDec( csdefine.EFFECT_STATE_LEADER )
		else:
			self.actCounterDec( Const.FOLLOW_STATES_ACT_WORD )
			self.effectStateDec( csdefine.EFFECT_STATE_FOLLOW )
		self.removeAllBuffByID( csconst.FOLLOW_BUFF_ID, [ csdefine.BUFF_INTERRUPT_ON_DIE ] )

	def isTeamFollowing( self ):
		"""
		是否在组队跟随中
		"""
		return csdefine.EFFECT_STATE_FOLLOW & self.effect_state or csdefine.EFFECT_STATE_LEADER & self.effect_state

	def isFollowing( self ):
		"""
		是否在跟随状态（仅对队员而言）
		"""
		return self.effect_state & csdefine.EFFECT_STATE_FOLLOW

	def isLeadTeam( self ):
		"""
		是否引导队伍中
		"""
		return csdefine.EFFECT_STATE_LEADER & self.effect_state

	def captainStopFollow( self, srcEntityID ):
		"""
		Exposed method.

		队长停止了跟随，13:50 2009-3-13，wsf
		"""
		if not self.hackVerify_( srcEntityID ):
			return

		if not self.isTeamCaptain():
			return

		self.effectStateDec( csdefine.EFFECT_STATE_LEADER )
		self.removeAllBuffByID( csconst.FOLLOW_BUFF_ID, [ csdefine.BUFF_INTERRUPT_ON_DIE ] )
		self.getTeamMailbox().stopFollow()

	def effectStateChanged( self, effectState, disabled ):
		"""
		效果改变.13:58 2009-3-13，wsf
			@param effectState		:	效果标识(非组合)
			@type effectState		:	integer
			@param disabled		:	效果是否生效
			@param disabled		:	bool
		"""
		if not disabled:
			return
		if self.isTeamCaptain():	# 不影响队长
			return
		if not self.isTeamFollowing():
			return
		if not effectState in Const.TEAM_FOLLOW_EFFECT_LIST:
			return

		self.cancelTeamFollow()
		self.getTeamMailbox().cancelFollow( self.id )  # 通知TeamEntity后面的人更换跟随对象

	def onStateChanged( self, old, new ):
		"""
		状态切换
		"""
		if self.isTeamCaptain():	# 不影响队长
			return
		if not self.isTeamFollowing():
			return

		if new == csdefine.ENTITY_STATE_DEAD:	# 如果死亡，则退出组队跟随
			self.cancelTeamFollow()
			self.getTeamMailbox().cancelFollow( self.id )  # 通知TeamEntity后面的人更换跟随对象

	def beforeEnterSpaceDoor( self, destPosition, destDirection ):
		"""
		进传送门之前做点事情
		"""
		if not self.isTeamFollowing():
			return
		if not self.isTeamCaptain():
			return

		for entity in self.entitiesInRangeExt( Const.TEAM_FOLLOW_TRANSPORT_DISTANCE, "Role", self.position ):
			if entity.captainID == self.id and entity.isTeamFollowing():
				entity.followCaptainTransport()

	def npcTeamFollowTransport( self, talkFunc ):
		"""
		组队跟随传送

		@param talkFunc : 传送对话功能实例
		"""
		for entity in self.entitiesInRangeExt( Const.TEAM_FOLLOW_TRANSPORT_DISTANCE, "Role", self.position ):
			if entity.captainID == self.id and entity.isTeamFollowing() and entity.isReal() and entity.spaceID == self.spaceID:	# 如果是ghost，不能传送
				talkFunc.do( entity )

	def followCaptainTransport( self ):
		"""
		Define method.
		队长过传送门，队员跟随传送
		"""
		if not self.isTeamFollowing():
			return

		self.addTimer( 0.5, 0, ECBExtend.TEAM_FOLLOW_TRANSPORT )

	def team_followTransportCB( self, controllerID, userData ):
		"""
		组队传送timer回调
		"""
		if BigWorld.entities.has_key( self.captainID ):
			captainEntity = BigWorld.entities[ self.captainID ]
			self.teleport( captainEntity, captainEntity.position + ( random.randint( -2, 2 ), 0, random.randint( -2, 2 ) ), captainEntity.direction )
		else:
			captainMB = self.getTeamCaptainMailBox()
			if captainMB:
				captainMB.cell.requestCaptainPosition( self )

	def requestCaptainPosition( self, cellMailbox ):
		"""
		Define method.
		传送门跟随传送，请求队长的位置
		"""
		cellMailbox.receiveCaptainPosition( self, self.position )

	def receiveCaptainPosition( self, cellMailbox, position ):
		"""
		Define method.
		组队跟随接收队长的位置信息
		"""
		self.teleport( cellMailbox, position, ( 0, 0, 0 ) )

	def onLeaveTeamTimer( self, timerID, cbID ):
		"""
		处理离开队伍，需要执行退出空间等问题
		"""
		newTime = self.queryTemp( 'leaveSpaceTime', 0 ) - 5
		if newTime <= 0:
			spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
			g_objFactory.getObject( spaceLabel ).onLeaveTeamProcess( self )
			self.removeTemp( 'leaveSpaceTime')
		else:
			self.setTemp( 'leaveSpaceTime', newTime )
			self.leaveTeamTimer = self.addTimer( 5, 0, ECBExtend.LEAVE_TEAM_TIMER )
			if not self.isInTeam():
				pass

	def backToLastSpace( self, srcEntityID ):
		"""
		exposed method
		玩家手动确认需要退出空间
		"""
		if srcEntityID != self.id:
			return
		spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		g_objFactory.getObject( spaceLabel ).onLeaveTeamProcess( self )

#
# $Log: not supported by cvs2svn $
# Revision 1.39  2008/08/13 09:08:21  huangdong
# 加入了队长邀请所有队员跟随的功能
#
# Revision 1.38  2008/08/09 10:04:09  huangdong
# 加入了邀请跟随的模块
#
# Revision 1.37  2008/05/12 05:12:20  zhangyuxing
# 加入队伍信息通知
#
# Revision 1.36  2008/03/15 09:22:19  yangkai
# 修正队伍信息通知参数
#
# Revision 1.35  2008/03/14 08:49:34  yangkai
# 修正组队轮流拾取的Bug
#
# Revision 1.34  2008/03/14 00:58:47  yangkai
# 修正了顺序拾取的方式
#
# Revision 1.33  2008/02/29 02:05:42  zhangyuxing
# 往client端发送的 队员信息的 spaceID 改为了 spaceLabel.主要是client
# 并不能通过spaceID获得远距离玩家的空间位置
#
# Revision 1.32  2008/02/01 04:11:51  wangshufeng
# 给队友发送自身信息时，加入发送等级数据
#
# Revision 1.31  2007/12/11 10:31:44  huangyongwei
# 添加了 getTeamMailbox 函数
#
# Revision 1.30  2007/12/08 08:18:34  yangkai
# 成员加入时更新物品拾取数据与队长一样
#
# Revision 1.29  2007/12/08 07:56:37  yangkai
# 添加:
# 队伍分配方式设置接口
# 队伍分配顺序处理等接口
#
# Revision 1.28  2007/11/16 03:51:09  zhangyuxing
# 接口更改：client.onStatusMessage  to  statusMessage
# 修改BUG：在teamInviteFC组队邀请中，把
# “if self.captainID != self.id :”改为
# “if self.captainID != self.id and self.captainID != 0:”
# 意思是说当玩家没有组队状态时也可以邀请其他玩家
#
# Revision 1.27  2007/10/09 07:51:55  phw
# 队伍代码调整，方法改名，优化实现方式，修正隐含的bug
#
# Revision 1.26  2007/10/07 07:23:09  phw
# method added:
# 	getTeamMemberDBIDs()
# 	getTeamMemberMailboxs()
# 	getTeamCaptainDBID()
#
# method modified:
# 	getAllMemberInRange()
# 	addTeamMember()
# 	teamMembers属性类型改变，修改相关代码
#
# Revision 1.25  2007/07/26 03:32:09  phw
# 去掉了“if hasattr( self, "client" )”相关代码
#
# Revision 1.24  2007/07/23 05:57:44  phw
# method added: isTeamMember()
#
# Revision 1.23  2007/06/19 09:28:03  kebiao
# 休正了无法获取队长entity的BUG
#
# Revision 1.22  2007/06/19 08:33:27  huangyongwei
# self.client.teamNotify( csstatus.TEAM_PLAYER_NOT_EXIST )
#
# --->
# self.statusMessage( csstatus.TEAM_PLAYER_NOT_EXIST )
#
# Revision 1.21  2007/06/14 09:29:16  huangyongwei
# TEAM_PLAYER_NOT_EXIST 的定义被移动到 csstatus 中
#
# Revision 1.20  2007/06/14 09:20:34  panguankong
# 添加部分变量的说明信息
#
# Revision 1.19  2007/06/14 03:07:29  panguankong
# 添加注解
#
# Revision 1.18  2007/04/02 02:51:46  yangkai
# 修正队伍成员离开玩家AOI时大地图不显示图标的BUG
#
# Revision 1.17  2007/01/17 09:06:09  phw
# method modified: getAllMemberInRange(), 优化了队友查找方式
# method removed:
#     getTeamTask()
#     setTeamTaskFB()
#
# Revision 1.16  2006/11/29 09:01:58  panguankong
# no message
#
# Revision 1.15  2006/11/29 08:18:03  panguankong
# 修改信息
#
# Revision 1.14  2006/11/29 03:38:28  panguankong
# 修改改了常量的位置
#
# Revision 1.13  2006/11/29 02:06:30  panguankong
# 添加了队伍系统
#

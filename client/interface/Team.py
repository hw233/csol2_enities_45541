# -*- coding: gb18030 -*-
#
# $Id: Team.py,v 1.105 2008-08-21 09:59:25 huangyongwei Exp $

import time
import BigWorld
import csdefine
import csstatus
import csconst
import Define
import Const
import keys
import GUIFacade
from bwdebug import *
from cscollections import MapList
from Function import Functor
from gbref import rds
from ItemsFactory import BuffItem
from event import EventCenter as ECenter
from config.client.msgboxtexts import Datas as mbmsgs
from MessageBox import *


#队友头像路径定义

HEADERS_OUTLINE = ""		#下线默认头像(类似于HEADERS_ONLINE,需要给定资源)
REQUEST_TEAM_INTERVAL = 30

class TeamMember( object ):
	"""
	队伍成员类，每个实例就是一个成员；当结构用
	"""
	def __init__( self ):
		self.DBID = 0 # DBID
		self.raceclass = -1
		self.name = ""
		self.level = 0
		self.hp = 0
		self.hpMax = 0
		self.mp = 0
		self.mpMax = 0
		self.online = False
		self.objectID = 0
		self.title = []						#队友的称号
		self.spaceLabel = 0					#队友的空间名字
		self.position = ( 0.0, 0.0, 0.0 )	#队友的位置
		self.header = None					#队友的头像
		self.gender = None					#队友的性别
		self.spaceID = 0					#队友的空间ID
		self.petID = 0					#队友宠物信息

	def getName( self ) :
		return self.name

	def getPosition( self ) :
		return self.position
	
	def getCamp( self ):
		return self.camp


# --------------------------------------------------------------------
# --------------------------------------------------------------------
class Team:
	def __init__( self ):
		self.captainID = 0 				# entityID，队长ID
		self.teamID = 0					# 队伍ID
		self.teamMember = MapList()		# [TeamMember,...] 队伍成员的ID集合
		self.__teammemberBuffs = {}		# 队友 buff 列表：{ 队友 ID : [buff 列表] }  ( hyw -- 2008.9.24 )
		self.pickUpState = csdefine.TEAM_PICKUP_STATE_FREE

		self.followTargetID = 0				# 跟随对象的id
		self.teamFollowTimerID = 0			# 队伍跟随侦测的timeID
		self.teamOutSapceTimerID = 0		# 离开space倒计时timeID
		self.captainStartPosition = ( 0, 0, 0 )	# 开始跟随时队长的初始位置
		self.copyInterfaceBox = None 		# 消息确认框
		self.followWaitTime = 0				# 跟随等待时间

		self.requestTeamClearTimer = 0		# 清理请求组队数据的timer
		self.requestTeamPlayerDict = {}		# 申请入队的玩家集合

	def onBecomePlayer( self ) :
		"""
		只有是 PlayerRole 时，才会被调用
		"""
		rds.shortcutMgr.setHandler( "PREPARE_FOR_TEAM_INVITE", self.prepareForTeamInvite )			# 进入准备邀请组队状态

	#---------------------------------------------------------------------------------
	# private
	def _addMember( self, playerDBID, playerName, objectID, playerRaceclass, onlineState, headTextureID ):
		"""
		添加玩家数据

		@param objectID: 玩家的EntityID
		@type  objectID: OBJECT_ID
		@param playerName: 玩家名称
		@type  playerName: string
		@param playerRaceclass: 
		@type  playerRaceclass: INT32
		@param onlineState: 是否在线
		@type  onlineState: BOOL
		"""
		info = TeamMember()

		info.raceclass = playerRaceclass & csdefine.RCMASK_CLASS
		info.camp = ( playerRaceclass & csdefine.RCMASK_CAMP ) >> 20
		info.gender    = playerRaceclass & csdefine.RCMASK_GENDER
		info.DBID = playerDBID
		info.name = playerName
		info.level = 0
		info.hp = 0
		info.hpMax = 0
		info.mp = 0
		info.mpMax = 0
		info.online = onlineState
		info.objectID = objectID
		info.title = []
		info.spaceLabel = ""
		info.spaceID = 0
		info.position = ( 0.0, 0.0, 0.0 )
		headTexturePath = rds.iconsSound.getHeadTexturePath( headTextureID )
		if not headTexturePath is None:
			info.header = headTexturePath		#队友自定义头像
		else:
			info.header = Const.ROLE_HEADERS[ info.raceclass ][ info.gender ]	#根据职业获取头像

		self.teamMember[objectID] = info

	def _removeMember( self, objectID ):
		"""
		删除一个成员
		@param objectID: 玩家OBJECTID
		@type objectID: OBJECTID
		"""
		self.teamMember.pop( objectID )

	#---------------------------------------------------------------------------------
	def isCaptain( self ):
		"""
		是不是队长
		"""
		return self.captainID == self.id

	#---------------------------------------------------------------------------------
	def inviteJoinTeamNear( self, playerEntity ):
		"""
		近距离组队
		@param playerEntity: 玩家实体
		@type playerEntity: Entity

		在客户端处理不同的邀请组队情况
		"""
		if self.isInSpaceChallenge():
			self.statusMessage( csstatus.CHALLENGE_SPACE_PERSONAL_CREATE_TEAM )
			return

		# 当前地图是否允许组队
		if self.isInTeamInviteForbidSpace():
			self.statusMessage( csstatus.TEAM_INVITE_IS_FORBID )
			return

		# 异界战场中不能组队
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG :
			self.statusMessage( csstatus.YI_JIE_ZHAN_CHANG_CANNOT_INVITE_TEAM )
			return

		if playerEntity == self:
			#self.statusMessage( csstatus.TEAM_NOT_INVITE_SELF )
			if self.isInTeam():
				self.statusMessage( csstatus.TEAM_IN_TEAM_NOT_CREATE_SELF )
			else:
				self.base.createTeamBySelf()
			return

		if self.isInTeam():
			if self.isCaptain() and self.turnWar_isJoin:		# 车轮战期间不让加队友
				self.statusMessage( csstatus.TONG_TURN_WAR_ON_JOIN_TEAM )
				return

			if self.isTeamFull():
				self.statusMessage( csstatus.TEAM_FULL )
				return

			if playerEntity.hasFlag( csdefine.ROLE_FLAG_TEAMMING ):
				self.statusMessage( csstatus.TEAM_PLAYER_IN_TEAM )
			else:
				self.cell.teamInviteFC( playerEntity.id )
		else:
			if playerEntity.hasFlag( csdefine.ROLE_FLAG_TEAMMING ):
				self.requestJoinTeamNear( playerEntity )
			else:
				self.cell.teamInviteFC( playerEntity.id )

	def requestJoinTeamNear( self, playerEntity ):
		"""
		请求加入对方的队伍
		"""
		playerName = playerEntity.getName()
		if playerName in self.requestTeamPlayerDict:
			self.statusMessage( csstatus.TEAM_REQUEST_TOO_FREQUENT )
			return
		self.requestTeamPlayerDict[playerName] = time.time()
		if not self.requestTeamClearTimer:	# 5分钟清理一次请求入队的数据
			 self.requestTeamClearTimer = BigWorld.callback( REQUEST_TEAM_INTERVAL, self.clearRequestTeamData )
		playerEntity.cell.requestJoinTeamNear()
#		self.statusMessage( csstatus.TEAM_REQUEST_HAD_BEEN_SEND )

	def clearRequestTeamData( self ):
		"""
		清理请求加队的数据
		"""
		BigWorld.cancelCallback( self.requestTeamClearTimer )
		self.requestTeamClearTimer = 0
		for key, value in self.requestTeamPlayerDict.items():
			if value + REQUEST_TEAM_INTERVAL < time.time():
				del self.requestTeamPlayerDict[key]

		if len( self.requestTeamPlayerDict ) > 0:
			self.requestTeamClearTimer = BigWorld.callback( REQUEST_TEAM_INTERVAL, self.clearRequestTeamData )

	def allowPlayerJoinTeam( self, playerID, targetName ):
		"""
		同意对方的入队请求
		"""
		if not self.isCaptain():
			return

		if self.turnWar_isJoin:		# 车轮战期间不让加队友
			self.statusMessage( csstatus.TONG_TURN_WAR_ON_JOIN_TEAM )
			return

		# 当前地图是否允许组队
		if self.isInTeamInviteForbidSpace():
			self.statusMessage( csstatus.TEAM_INVITE_IS_FORBID )
			return

		if self.isTeamFull():
			self.statusMessage( csstatus.TEAM_FULL_REFUSE_JOIN )
			return

		try:
			targetEntity = BigWorld.entities[playerID]
		except KeyError:
			self.base.acceptTeamRequset( targetName )
		else:
			self.cell.acceptTeamRequestNear( playerID )

	def refusePlayerJoinTeam( self, playerID, playerName ):
		"""
		拒绝玩家的入队请求
		"""
		if not self.isCaptain():
			return
		try:
			BigWorld.entities[playerID]
		except KeyError:
			self.base.refusePlayerJoinTeam( playerName )
		else:
			self.cell.refusePlayerJoinTeam( playerID )

	def receiveJoinTeamRequest( self, playerName, raceclass, level, entityID ):
		"""
		Define method.
		接收加队请求

		@param playerName 	: 发起申请玩家的名字
		@type playerName 	: STRING
		@param metier 		: 发起申请玩家的职业
		@type metier 		: INT32
		@param level 		: 发起申请玩家的等级
		@type level 		: UINT16
		@param entityID 	: 发起申请玩家的entity id
		@type entityID 		: OBJECT_ID
		"""
		# 当前地图是否允许组队，不能组队则屏蔽组队请求
		if self.isInTeamInviteForbidSpace():
			return
			
		metier = raceclass & csdefine.RCMASK_CLASS
		ECenter.fireEvent( "EVT_ON_APPLIED_JOIN_TEAM", playerName, metier, level, entityID )

	def teamInviteByTeammate( self, targetName, targetID, teammateName, teammateID ):
		"""
		Define method.
		队友邀请目标玩家入队，队长收到请求信息
		"""
		def query( response ) :
			self.replyTeammateInvite( response == RS_YES, targetName, targetID, teammateID )
		if not rds.statusMgr.isInWorld() :
			query( RS_NO )
			return
		# "您的队员%s欲邀请%s加入队伍，您是否同意？"
		msg = mbmsgs[0x0181] % ( teammateName, targetName )
		showMessage( msg, "", MB_YES_NO, query, gstStatus = Define.GST_IN_WORLD )

	def replyTeammateInvite( self, agree, targetName, targetID, teamateID ):
		"""
		队长同意队友邀请的玩家入队。
		"""
		if not agree:
			self.base.refuseTeammateInvite( targetName, teamateID )
			return
		try:
			targetEntity = BigWorld.entities[targetID]
		except KeyError:
			self.base.teamRemoteInviteFC( targetName )
		else:
			self.cell.teamInviteFC( targetEntity.id )

	def inviteJoinTeam( self, playerName ):
		"""
		远距离组队
		@param playerName: 玩家名称
		@type playerName: String
		"""
		if self.isCaptain() and self.turnWar_isJoin:		# 车轮战期间不让加队友
			self.statusMessage( csstatus.TONG_TURN_WAR_ON_JOIN_TEAM )
			return

		# 当前地图是否允许组队
		if self.isInTeamInviteForbidSpace():
			self.statusMessage( csstatus.TEAM_INVITE_IS_FORBID )
			return

		# 异界战场中不能组队
		if self.getCurrentSpaceType() == csdefine.SPACE_TYPE_YI_JIE_ZHAN_CHANG :
			self.statusMessage( csstatus.YI_JIE_ZHAN_CHANG_CANNOT_INVITE_TEAM )
			return

		if self.isTeamFull():
			self.statusMessage( csstatus.TEAM_FULL )
			return

		if self.isInSpaceChallenge():
			if self.challengeType == csconst.SPACE_CHALLENGE_TYPE_SINGLE:
				self.statusMessage( csstatus.CHALLENGE_SPACE_PERSONAL_CREATE_TEAM )
				return

		if playerName == self.getName():
			self.statusMessage( csstatus.TEAM_NOT_INVITE_SELF )
			return
		if self.isTeamMemberByName( playerName ):
			self.statusMessage( csstatus.TEAM_PLAYER_IN_TEAM )
			return
		if playerName in self.requestTeamPlayerDict:
			self.statusMessage( csstatus.TEAM_REQUEST_TOO_FREQUENT )
			return
		self.requestTeamPlayerDict[playerName] = time.time()
		if not self.requestTeamClearTimer:	# 5分钟清理一次请求入队的数据
			 self.requestTeamClearTimer = BigWorld.callback( REQUEST_TEAM_INTERVAL, self.clearRequestTeamData )
		self.base.teamRemoteInviteFC( playerName )
		#self.statusMessage( csstatus.TEAM_REQUEST_HAD_BEEN_SEND )

	def isTeamFull( self ):
		"""
		是否队伍满员
		"""
		return len( self.teamMember ) >= csconst.TEAM_MEMBER_MAX

	def teamDisemploy( self, playerID ):
		"""
		队伍开除
		@param playerID: 玩家ID
		@type playerID: OBJECT_ID
		"""
		if not self.teamMember.has_key( playerID ):
			self.statusMessage( csstatus.TEAM_IS_NOT_MEMBER )
			return

		# 不能开除自己
		if self.id == playerID:
			self.statusMessage( csstatus.TEAM_CAN_NOT_DISEMPLOY_SELF )
			return

		# 不是队长
		if not self.isCaptain():
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_CAPTAIN )
			return

		if self.getSpaceLabel() == "fu_ben_bang_hui_che_lun_zhan":			# 帮会车轮战副本中不能解散队伍
			self.statusMessage( csstatus.TONG_TURN_WAR_ON_DISPLOY_TEAMMEMBER )
			return

		if self.isInSpaceChallenge():
			def kickMember( rs_id ):
				if rs_id == RS_YES:
					self.base.leaveTeamFC( playerID )

			showMessage( 0x0186, "", MB_YES_NO, kickMember )
			return

		self.base.leaveTeamFC( playerID )

	#---------------------------------------------------------------------------------
	def teamInviteBy( self, inviterName ):
		"""
		define method.
		邀请玩家
		条件：
		　邀请通知client

		过程：
		　让client邀请玩家

		@param inviterName: 邀请者的名称
		@type  inviterName: STRING
		"""
		# 提示有玩家要求组队
		if not self.allowInvite:
			self.revertInviteJoinTeam( False )
			return

		if self.state == csdefine.ENTITY_STATE_PENDING:
			self.revertInviteJoinTeam( False )
			return

		if not rds.statusMgr.isInWorld() :
			self.revertInviteJoinTeam( False )
			return

		GUIFacade.onAskJoinTeam( inviterName, 1 )
		if rds.ruisMgr.copyTeamSys.visible :
			rds.ruisMgr.copyTeamSys.visible = False

	def revertInviteJoinTeam( self, agree ):
		"""
		回复组队
		参数：
		　agree：同意加入

		过程：
		　条件判断
		　1、邀请记录不存在，中断操作
		　删除邀请记录
		　记录玩家为组队状态
		　通知邀请者同意组队

		@param agree: 同意加入
		@type agree: INT8
		"""
		if self.isInSpaceChallenge():
			if self.challengeType == csconst.SPACE_CHALLENGE_TYPE_SINGLE:
				self.statusMessage( csstatus.CHALLENGE_SPACE_PERSONAL_JOIN_TEAM )
				self.base.replyTeamInviteByFC( False )
				return

		self.base.replyTeamInviteByFC( agree )

	#---------------------------------------------------------------------------------
	def addTeamMember( self, playerID, playerDBID, playerName, playerRaceclass, onlineState, headTextureID ):
		"""
		define method.
		发送成员数据

		过程：
		　向成员列表里添加成员

		@param playerID: 玩家的EntityID
		@type  playerID: OBJECT_ID
		@param playerName: 玩家名称
		@type  playerName: string
		@param playerRaceclass: 玩家职业
		@type  playerRaceclass: INT32
		@param onlineState: 当前是否在线
		@type  onlineState: INT8
		@param onlineState: 拾取方式
		@type  onlineState: INT8
		"""
		# 添加成员
		self._addMember( playerDBID, playerName, playerID, playerRaceclass, onlineState, headTextureID )

		if self.id == playerID:
			if self.copyInterfaceBox: #退出队伍副本时，确认框没有消失又重新加入队伍
				self.copyInterfaceBox.hide()
			return

		self.__teammemberBuffs[playerID] = []					# 添加 buff 列表( hyw -- 2008.9.24 )
	#	self.team_requestMemberBuffs( playerID )				# 申请队友的 buff

		BigWorld.callback( csconst.TEAM_DATA_UPDATE_TIME, self.updataMemberData )
		BigWorld.callback( csconst.TEAM_DATA_UPDATE_TIME_NEAR, self.updataMemberDataNear )

		GUIFacade.onTeamMemberAdded( self.teamMember[playerID] )
		self.onTeamMemberChange()

	def updataMemberData( self ):
		"""
		更新玩家数据
		"""
		player = BigWorld.player()
		if ( not player ) or ( not player.inWorld ) : return	#防止角色下线时没有captainID导致下面报错
		if self.captainID == 0:
			return

		for key in self.teamMember.keys():
			if BigWorld.entities.has_key(key):
				continue
			self.requestTeammateInfo( key )

		if len(self.teamMember) != 0:
			BigWorld.callback( csconst.TEAM_DATA_UPDATE_TIME, self.updataMemberData )

	def updataMemberDataNear( self ):
		"""
		更新玩家数据
		"""
		player = BigWorld.player()
		if ( not player ) or ( not player.inWorld ) : return	#防止角色下线时没有captainID导致下面报错
		if self.captainID == 0:
			return
		e = BigWorld.entities
		spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		for key in self.teamMember.keys():
			if e.has_key(key):
				self.teammateInfoNotify( key, e[key].level, e[key].HP, e[key].HP_Max, e[key].MP, e[key].MP_Max, 0, spaceLabel, e[key].position, e[key].spaceID )
		if len(self.teamMember) != 0:
			BigWorld.callback( csconst.TEAM_DATA_UPDATE_TIME_NEAR, self.updataMemberDataNear )

	def addTeamMemberPet( self, playerID, petID, uname, name, modelNumber, species ):
		"""
		defined method
		队友宠物信息
		"""
		if playerID == self.id:return
		if playerID in self.teamMember:
			self.teamMember[playerID].petID = petID
			ECenter.fireEvent( "EVT_ON_TEAM_ADD_MEMBER_PET", playerID, petID, uname, name, modelNumber, species )
			BigWorld.callback( csconst.TEAM_DATA_UPDATE_PET, self.updateMemberPetData )
			BigWorld.callback( csconst.TEAM_DATA_UPDATE_TIME_NEAR, self.updateMemberPetDataNear )

	def updateMemberPetData( self ):
		"""
		远距离请求队友宠物信息
		"""
		player = BigWorld.player()
		if ( not player ) or ( not player.inWorld ) : return	#防止角色下线时没有captainID导致下面报错
		if self.captainID == 0:
			return
		for key in self.teamMember.keys():
			if BigWorld.entities.has_key(key):
				continue
			self.requestTeammatePetInfo( key )

		if len(self.teamMember) != 0:
			BigWorld.callback( csconst.TEAM_DATA_UPDATE_PET, self.updateMemberPetData )

	def updateMemberPetDataNear( self ):
		"""
		更新附近队友宠物数据
		"""
		player = BigWorld.player()
		if ( not player ) or ( not player.inWorld ) : return	#防止角色下线时没有captainID导致下面报错
		if self.captainID == 0:
			return
		es = BigWorld.entities
		for key, member in self.teamMember.items():
			if key == self.id:continue
			petID = member.petID
			if es.has_key( petID ):
				pet = es[petID]
				self.teammatePetInfoNotify( key, petID, pet.uname, pet.name, pet.level, pet.HP, pet.HP_Max, pet.MP, pet.MP_Max, None, pet.modelNumber, pet.species )
		if len(self.teamMember) != 0:
			BigWorld.callback( csconst.TEAM_DATA_UPDATE_TIME_NEAR, self.updateMemberPetDataNear )

	def requestTeammatePetInfo( self, playerID ):
		"""
		请求队友宠物信息
		"""
		if not self.teamMember.has_key( playerID ):
			self.statusMessage( csstatus.TEAM_IS_NOT_MEMBER )
			return
		if not self.teamMember[playerID].online:
			return
		self.base.requestTeammatePetInfoFC( playerID )

	def disbandTeamNotify( self ):
		"""
		define method.
		队伍解散通知，此方法由base调用
		"""
		self.captainID = 0 				# entityID，队长ID
		self.teamID = 0					# 队伍ID
		self.teamMember.clear()			# [TeamMember,...] 队伍成员的ID集合
		self.__teammemberBuffs = {}		# 清空所有队友 buff 列表
		self.statusMessage( csstatus.TEAM_HAS_DISBAND )
		GUIFacade.onTeamDisbanded()
		self.onTeamMemberChange()
		self.cmi_onLeaveTeam()

	def teamInfoNotify( self, teamID, captainID ):
		"""
		define method.
		通知队伍信息

		@param teamID: 队伍的EntityID
		@type teamID: OBJECT_ID
		@param captainID: 队长ID
		@type captainID: OBJECT_ID
		"""
		self.teamID = teamID
		self.captainID = captainID
		self.followTargetID = captainID								# 初始化跟随目标id，16:38 2009-3-12,wsf
		GUIFacade.onTeamCaptainChanged( captainID )
		rds.helper.courseHelper.interactive( "jiaruduiwu_caozuo" )	# 加入队伍时，触发过程帮助( hyw--2009.06.13 )

	# ----------------------------------------------------------------
	def leaveTeamNotify( self, playerID, disemploy ):
		"""
		define method.
		玩家离开通知

		@param playerID: 玩家ID
		@type playerID: OBJECT_ID
		@param disemploy: 开除标记
		@type disemploy: INT8
		"""
		if playerID == self.id:
			# 自身
			self.captainID = 0 #entityID
			self.teamID = 0

			for key in self.teamMember.keys():
				del self.teamMember[ key ]
				GUIFacade.onTeamMemberLeft( key )
			self.__teammemberBuffs = {}						# 清空队友 buff 列表 ( hyw -- 2008.9.24 )

			if disemploy:
				self.statusMessage( csstatus.TEAM_HAVE_KICKED_OUT )
			else:
				self.statusMessage( csstatus.TEAM_TEAMMATER_LEAVE_TEAM, self.getName() ) #原来这里被写了TEAM_HAS_DISBAND 修改信息 by姜毅
				GUIFacade.onTeamDisbanded()
			self.cmi_onLeaveTeam()
		else:
			# 其它成员
			if disemploy:
				self.statusMessage( csstatus.TEAM_TEAMMATER_TICKED_OUT, self.teamMember[playerID].name )
			else:
				self.statusMessage( csstatus.TEAM_TEAMMATER_LEAVE_TEAM, self.teamMember[playerID].name )

			self._removeMember( playerID )
			if playerID in self.__teammemberBuffs :
				self.__teammemberBuffs.pop( playerID )			# 清空离队队友的 buff 列表（hyw -- 2008.9.24）
			GUIFacade.onTeamMemberLeft( playerID )
			self.cmi_onTeammateLeave( playerID )

		self.onTeamMemberChange()

	def changeCaptain( self, playerID ):
		"""
		移交队长权限
		"""
		if not self.teamMember.has_key( playerID ):
			self.statusMessage( csstatus.TEAM_NOT_IN_TEAM )
			return

		if self.teamMember[playerID].objectID == self.id:
			return

		self.base.changeCaptainFC( playerID )

	def changeCaptainNotify( self, playerID ):
		"""
		define method.

		过程：
		　设置新队长
		  提示队长已经改变

		@param playerID: 玩家ID
		@type playerID: OBJECT_ID
		"""
		if self.teamMember.has_key( playerID ):
			self.statusMessage( csstatus.TEAM_TEAMMATER_IS_CAPTAIN, self.teamMember[playerID].name )
			self.captainID = playerID
		else:
			self.statusMessage( csstatus.TEAM_TEAMMATER_IS_CAPTAIN, self.playerName )
			self.captainID = self.id
		GUIFacade.onTeamCaptainChanged( self.captainID )
		if self.isFollowing():
			self.team_followDetect()

	def changePickUpStateNotify( self, state ):
		"""
		define method.
		更改物品拾取方式通知

		@param state: 更改的拾取方式 define in csdefine.py
		@type state: INT8
		"""
		self.pickUpState = state
		if state == csdefine.TEAM_PICKUP_STATE_FREE:
			self.statusMessage( csstatus.TEAM_FREE_PICK )
		elif state == csdefine.TEAM_PICKUP_STATE_ORDER:
			self.statusMessage( csstatus.TEAM_ORDER_PICK )
		elif state == csdefine.TEAM_PICKUP_STATE_SPECIFY:
			self.statusMessage( csstatus.TEAM_LEADER_PICK )
		GUIFacade.onPickUpStateChange( state )

	def rejoinTeam( self, oldEntityID, newEntityID ):
		"""
		define method.
		队伍成员上线，重新加入队伍中

		@param oldEntityID: 玩家旧的entityID
		@type  oldEntityID: OBJECT_ID
		@param newEntityID: 玩家新的entityID
		@type  newEntityID: OBJECT_ID
		"""
		info = self.teamMember[oldEntityID]
		info.online = True
		info.objectID = newEntityID
		self.teamMember[newEntityID] = info
		self.teamMember.pop( oldEntityID )

		self.__teammemberBuffs[ newEntityID ] = []					# 重新创建队友buff列表

		GUIFacade.onTeamMemberRejoin( oldEntityID, newEntityID )
		header_path = info.header
		GUIFacade.onTeamMemberChangeIcon( newEntityID, header_path )#通知GUI头像改变事件触发

		#self.statusMessage( csstatus.TEAM_TEAMMATER_IS_ONLINE, info.name )	# 队友上线不通知，17:55 2009-3-6，wsf
		self.onTeamMemberChange()
		self.cmi_onTeammateLogon( oldEntityID, newEntityID )

	def logoutNotify( self, playerID ):
		"""
		define method.
		队员下线

		过程：
		　在成员列表里设置玩家为下线状态

		@param playerID: 玩家ID
		@type playerID: OBJECT_ID
		"""
		if self.teamMember.has_key( playerID ):
			self.teamMember[playerID].online = False

		header_path = HEADERS_OUTLINE
		GUIFacade.onTeamMemberLogOut( playerID )#

		if playerID in self.__teammemberBuffs :				# 队友下线时，将其 buff 列表清空（hyw--2008.09.25）
			self.__teammemberBuffs.pop( playerID )

	def teamlogout( self ):
		"""
		下线
		"""
		self.captainID = 0
		BigWorld.cancelCallback( self.teamFollowTimerID )
		BigWorld.cancelCallback( self.requestTeamClearTimer )
		self.requestTeamClearTimer = 0

	# -------------------------------------------------
	def team_onMemberAddBuff( self, memberID, buff ) :
		"""
		defined method.
		当一个队友添加了 buff 时被调用
		hyw -- 2008.09.24
		"""
		if memberID not in self.__teammemberBuffs :
			ERROR_MSG( "buff list doesn't contain teammate member: %i" % memberID )
		else :
			self.__teammemberBuffs[memberID].append( buff )
			buffItem = BuffItem( buff )
			ECenter.fireEvent( "EVT_ON_TEAMMEMBER_ADD_BUFF", memberID, buffItem )

	def team_onMemberRemoveBuff( self, memberID, index ) :
		"""
		defined method.
		当一个队友删除了 buff 时被调用
		hyw -- 2008.09.24
		"""
		if memberID not in self.__teammemberBuffs :
			ERROR_MSG( "buff list doesn't contain teammate member: %i" % memberID )
		else :
			for buff in self.__teammemberBuffs[memberID]:
				if buff["index"] == index:
					buffItem = BuffItem( buff )
					ECenter.fireEvent( "EVT_ON_TEAMMEMBER_REMOVE_BUFF", memberID, buffItem )
					return

	def team_onMemberUpdateBuff( self, memberID, index, buff ) :
		"""
		defined method.
		当一个队友更新了某个 buff 时被调用
		hyw -- 2008.09.24
		"""
		if memberID not in self.__teammemberBuffs :
			ERROR_MSG( "buff list doesn't contain teammate member: %i" % memberID )
		else :
			self.__teammemberBuffs[memberID][index] = buff
			buffItem = BuffItem( buff )
			ECenter.fireEvent( "EVT_ON_TEAMMEMBER_UPDATE_BUFF", memberID, index, buffItem )

	def team_onMemberPetAddBuff( self, memberID, buff ):
		"""
		define method
		队友宠物添加buff时调用
		"""
		if memberID not in self.teamMember :
			ERROR_MSG( "team list doesn't contain teammate member: %i" % memberID )
			return
		if self.id == memberID:return
		buffItem = BuffItem( buff )
		ECenter.fireEvent( "EVT_ON_TEAMMEMBER_PET_ADD_BUFF", memberID, buffItem )

	def team_onMemberPetRemoveBuff( self, memberID, buff ):
		"""
		define method
		队友宠物移除buff时调用
		"""
		if memberID not in self.teamMember :
			ERROR_MSG( "team list doesn't contain teammate member: %i" % memberID )
			return
		if self.id == memberID:return
		buffItem = BuffItem( buff )
		ECenter.fireEvent( "EVT_ON_TEAMMEMBER_PET_REMOVE_BUFF", memberID, buffItem )
	#---------------------------------------------------------------------------------
	def requestTeammateInfo( self, playerID ):
		"""
		向队友申请状态

		@param playerID: 玩家ID
		@type playerID: OBJECT_ID
		"""
		# 玩家不是队员
		#print "TeamClient..........requestTeammateInfo"

		if not self.teamMember.has_key( playerID ):
			self.statusMessage( csstatus.TEAM_IS_NOT_MEMBER )
			return
		if not self.teamMember[playerID].online:
			return
		self.base.requestTeammateInfoFC( playerID )

	def teammateInfoNotify( self, playerID, level, hp, hpMax, mp, mpMax, buff, spaceLabel, position, spaceID ):
		"""
		define method.
		状态返回

		过程：
		　更新玩家的显示状态

		@param playerID: 玩家ID
		@type playerID: OBJECT_ID
		@param level: 玩家等级
		@type level: UINT8
		@param hp: 玩家ID
		@type hp: INT32
		@param hpMax: 玩家ID
		@type hpMax: INT32
		@param mp: 玩家ID
		@type mp: INT32
		@param mpMax: 玩家ID
		@type mpMax: INT32
		@param buff: 玩家ID
		@type buff: INT32
		"""
		if playerID == self.id:
			return

		if playerID:
			self.teamMember[playerID].hp = hp
			self.teamMember[playerID].level = level
			self.teamMember[playerID].hpMax = hpMax
			self.teamMember[playerID].mp = mp
			self.teamMember[playerID].mpMax = mpMax
			self.teamMember[playerID].spaceLabel = spaceLabel
			self.teamMember[playerID].position = position
			self.teamMember[playerID].spaceID = spaceID

			GUIFacade.onTeamMemberChangeLevel( playerID, level )	# 等级改变
			GUIFacade.onTeamMemberChangeHP( playerID, hp, hpMax )
			GUIFacade.onTeamMemberChangeMP( playerID, mp, mpMax )

	def teammatePetInfoNotify( self, playerID, petID, uname, name, petLevel, petHP, petHP_Max, petMP, petMP_Max, buff, modelNumber, species ):
		"""
		define method.
		更新玩家宠物的显示状态
		"""
		if playerID == self.id:
			return
		if playerID:
			petInfos = ( petID, uname, name, petLevel, petHP, petHP_Max, petMP, petMP_Max, buff, modelNumber, species )
			self.teamMember[playerID].petID = petID
			ECenter.fireEvent( "EVT_ON_TEAM_MEMBER_PET_INFO_RECEIVE", playerID, petInfos )

	def team_onPetConjureNotify( self, playerID, petID, uname, name, modelNumber, species ):
		"""
		队友宠物出战通知
		"""
		if playerID == self.id:
			return
		self.addTeamMemberPet( playerID, petID, uname, name, modelNumber, species )

	def team_onPetWithdrawNotify( self, playerID ):
		"""
		队友召回宠物通知
		"""
		if playerID == self.id:
			return
		if not playerID in self.teamMember:return
		self.teamMember[playerID].petID = 0
		ECenter.fireEvent( "EVT_ON_TEAM_MEMBER_PET_WITHDRAWED", playerID )

	def teammateLevelChange( self, playerID, level ):
		"""
		define method.
		玩家等级改变

		@param playerID: 玩家ID
		@type playerID: OBJECT_ID
		@param level: 玩家等级
		@type level: INT16
		"""
		if playerID != 0:
			self.teamMember[playerID].level = level

			GUIFacade.onTeamMemberChangeLevel( playerID, level )

	def teammatePetLevelChange( self, playerID, petLevel ):
		"""
		队友宠物等级改变
		"""
		if playerID != 0:
			ECenter.fireEvent( "EVT_ON_TEAM_MEMBER_PET_LEVEL_CHANGE", playerID, petLevel )

	def teammateNameChange( self, entityID, playerName ):
		"""
		由服务器告诉客户端，队伍里某个队员的名称是什么

		@param   entityID: 队员entity id
		@type    entityID: OBJECT_ID
		@param playerName: 队员名称
		@type  playerName: STRING
		@return:           无
		"""
		if entityID != 0:
			self.teamMember[entityID].name = playerName
			GUIFacade.onTeamMemberChangeName( entityID, playerName )

	def teammateNameChange( self, playerID, petName ):
		"""
		队友宠物名称改变
		"""
		if playerID != 0:
			ECenter.fireEvent( "EVT_ON_TEAM_MEMBER_PET_NAME_CHANGE", playerID, petName )

	def teammateSpaceChange( self, playerID, spaceLabel ):
		"""
		define method.
		玩家空间位置改变

		@param playerID: 玩家ID
		@type playerID: DATABASE_ID
		@param spaceLabel: 玩家成在空间
		@type spaceLabel: STRING
		"""

		if self.teamMember.has_key( playerID ):
			self.teamMember[playerID].spaceLabel = spaceLabel

			GUIFacade.onTeamMemberChangeSpace( playerID, spaceLabel )

	def disbandTeam( self ):
		"""
		解散队伍
		"""
		if self.isCaptain():
			if self.getSpaceLabel() == "fu_ben_bang_hui_che_lun_zhan":			# 帮会车轮战副本中不能解散队伍
				self.statusMessage( csstatus.TONG_TURN_ON_DISBAND_TEAM )
				return
			if self.isInSpaceChallenge():
				def disband( rs_id ):
					if rs_id == RS_YES:
						self.base.disbandTeamFC()

				showMessage( 0x0184, "", MB_YES_NO, disband )
				return
			self.base.disbandTeamFC()
		else:
			self.statusMessage( csstatus.TEAM_TEAMMATER_NOT_CAPTAIN )

	def leaveTeam( self ):
		"""
		玩家离队
		"""
		if self.getSpaceLabel() == "fu_ben_bang_hui_che_lun_zhan":			# 帮会车轮战副本中不能解散队伍
			self.statusMessage( csstatus.TONG_TURN_WAR_ON_LEAVE_TEAM )
			return
		if self.isInSpaceChallenge():
			def leave( rs_id ):
				if rs_id == RS_YES:
					self.base.leaveTeamFC( self.id )

			showMessage( 0x0185, "", MB_YES_NO, leave )
			return

		self.base.leaveTeamFC( self.id )

	def isTeamMemberByName( self, playerName ):
		"""
		通过名字判断对方是否队友
		"""
		for teammateInfo in self.teamMember.values():
			if teammateInfo.name == playerName:
				return True
		return False

	def isJoinTeam( self ):
		"""
		玩家是否在队伍中
		"""
		return self.teamID != 0

	def isTeamMember( self, ID ):
		"""
		玩家是否在队伍中

		@param ID: 玩家ID
		@type ID: OBJECT_ID
		"""
		return self.teamMember.has_key( ID )

	def isInTeam( self ):
		"""
		判断自己是否在队伍里

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.teamID != 0

	def changePickUpQuality( self, quality ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_PICKUP_QUALITY_CHANGE", quality )

	def changeRollQuality( self, quality ):
		"""
		define method
		"""
		pass


	def teamNotifyWithMemberName( self, statusID, id ):
		"""
		提示信息，包含队伍成员名称
		"""
		self.onStatusMessage( statusID, "(\'%s\',)" % self.teamMember[id].name )

	def allcateDropItem( self, index ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_CAPTAIN_ALLOCATE_ITEM", index )

	# ---------------------------------------------------------------------------------
	# 组队跟随
	# ---------------------------------------------------------------------------------
	def team_leadTeam( self ):
		"""
		队长发起组队跟随
		"""
		if not self.isCaptain():
			return
		self.statusMessage( csstatus.TEAM_CAPTAIN_LEAD_TEAM )
		nameList = []
		if self.isTeamLeading():
			for entity in self.entitiesInRange( csconst.TEAM_FOLLOW_DISTANCE, lambda entity : self.teamMember.has_key( entity.id ) and entity.isFollowing() ):
				nameList.append( entity.getName() )
			if len( nameList ):
				self.statusMessage( csstatus.TEAM_FOLLOW_ALREADY_PLAYER, ",".join( nameList ) )

		self.cell.leadTeam()

	def team_requestFollow( self ):
		"""
		Define method.
		询问是否要跟随队长
		"""
		if not rds.statusMgr.isInWorld() : return
		def query( rs_id ):
			"""
			"""
			if self.isCaptain():
				return
			captain = BigWorld.entities.get( self.captainID )
			if captain is None or not self.isSamePlanes( captain ):	# 如果队长不在AOI，那么视作没收到邀请
				return

			if rs_id == RS_OK and time.time() - requestTime < Const.TEAM_FOLLOW_REQUEST_VALIDITY:
				reply = True
				if self._isVend():
					self.statusMessage( csstatus.TEAM_FOLLOW_CANT_VEND )
					return
				if self.effect_state & csdefine.EFFECT_STATE_SLEEP:
					self.statusMessage( csstatus.TEAM_FOLLOW_CANT_SLEEP )
					return
				if self.effect_state & csdefine.EFFECT_STATE_VERTIGO or self.effect_state & csdefine.EFFECT_STATE_BE_HOMING:
					self.statusMessage( csstatus.TEAM_FOLLOW_CANT_VERTIGO )
					return
				if self.effect_state & csdefine.EFFECT_STATE_FIX:
					self.statusMessage( csstatus.TEAM_FOLLOW_CANT_FIX )
					return
				if self.position.flatDistTo( captain.position ) > csconst.TEAM_FOLLOW_DISTANCE:
					self.statusMessage( csstatus.FOLLOW_FORBID_TOO_FAR )
					return
				if not self.getState() in [ csdefine.ENTITY_STATE_FREE, csdefine.ENTITY_STATE_FIGHT ]:
					self.statusMessage( csstatus.FOLLOW_FORBID_STATE )
					return
			else:
				reply = False

			self.cell.team_replyForFollowRequest( reply )

		requestTime = time.time()	# 收到邀请的时刻，回复请求不能超过一分钟否则视作拒绝邀请
		# "是否要跟随队长行动?"
		showAutoHideMessage( Const.TEAM_FOLLOW_REQUEST_VALIDITY, 0x0183, "", MB_OK_CANCEL, query, gstStatus = Define.GST_IN_WORLD )

	def team_startFollow( self ):
		"""
		开始跟随队长行动
		"""
		captainEntity = BigWorld.entities.get( self.captainID )
		if captainEntity is None:
			self.cell.team_cancelFollow()
			return

		pet = self.pcg_getActPet()
		if pet is not None:
			pet.setActionMode( csdefine.PET_ACTION_MODE_FOLLOW )
		self.captainStartPosition = captainEntity.position[:]		# 保存队长的初始位置，如果队长不动那么队员就不开始跟随
		self.pursueEntity( captainEntity, Const.TEAM_FOLLOW_START_DISTANCE )
		#self.moveTo( self.__followPositionConvert( captainEntity.position, Const.TEAM_FOLLOW_START_DISTANCE ) )
		self.statusMessage( csstatus.TEAMATE_START_FOLLOW )
		self.team_followDetect()

	def team_stopFollow( self ):
		"""
		停止跟随
		"""
		self.resetTeamFollow()

	def isFollowing( self ):
		"""
		是否在跟随状态
		"""
		return self.effect_state & csdefine.EFFECT_STATE_FOLLOW

	def isTeamLeading( self ):
		"""
		是否在引导队伍状态
		"""
		return self.effect_state & csdefine.EFFECT_STATE_LEADER

	def team_checkFollow( self ):
		"""
		判断是否还能跟随

		这个检查的目的是
		"""
		if time.time() > self.followWaitTime + Const.TEAM_FOLLOW_WAIT_TIEM:	# 等待时间到
			self.followWaitTime = 0
			return False
		return True

	def team_followDetect( self ):
		"""
		跟随侦测
		"""
		BigWorld.cancelCallback( self.teamFollowTimerID )

		# 由于如果处于传送中触发了跟随检测，那么有可能找不到队长或队长的位置距离不合适，因此在找不到队长或
		# 队长位置太远时做一个Const.TEAM_FOLLOW_WAIT_TIEM的缓冲，如果Const.TEAM_FOLLOW_WAIT_TIEM后
		# 还不能符合跟随条件，那么退出跟随。
		captainEntity = BigWorld.entities.get( self.captainID )
		if self.followWaitTime == 0:
			self.followWaitTime = time.time()		# 记录不合法的开始时间
		if captainEntity is None:
			if not self.team_checkFollow():		# 等待时间到
				self.team_cancelFollow( csstatus.TEAM_FOLLOW_FAIL )
			else:
				self.teamFollowTimerID = BigWorld.callback( Const.TEAM_FOLLOW_DETECT_INTERVAL, self.team_followDetect )
			return
		if self.position.flatDistTo( captainEntity.position ) > csconst.TEAM_FOLLOW_DISTANCE:
			if not self.team_checkFollow():		# 等待时间到
				self.team_cancelFollow( csstatus.TEAM_FOLLOW_FAIL )
			else:
				self.teamFollowTimerID = BigWorld.callback( Const.TEAM_FOLLOW_DETECT_INTERVAL, self.team_followDetect )
			return
		self.followWaitTime = 0					# 合法则重置，否则会累计

		if self.captainStartPosition == captainEntity.position:	# 队长还没开始行动，继续等待
			self.teamFollowTimerID = BigWorld.callback( Const.TEAM_FOLLOW_DETECT_INTERVAL, self.team_followDetect )
			return

		followTarget = BigWorld.entities.get( self.followTargetID )
		if followTarget is None:
			followTarget = captainEntity

		if self.position.flatDistTo( captainEntity.position ) <= Const.TEAM_FOLLOW_BEHIND_DISTANCE:
			self.teamFollowTimerID = BigWorld.callback( Const.TEAM_FOLLOW_DETECT_INTERVAL, self.team_followDetect )
			return

		self.pursueEntity( followTarget, Const.TEAM_FOLLOW_BEHIND_DISTANCE )
		self.teamFollowTimerID = BigWorld.callback( Const.TEAM_FOLLOW_DETECT_INTERVAL, self.team_followDetect )

	def team_followPlayer( self, playerID ):
		"""
		Define method.
		接收跟随目标开始跟随侦测
		"""
		DEBUG_MSG( "------->>>playerID", playerID )
		self.followTargetID = playerID
		self.team_followDetect()

	def __followPositionConvert( self, targetPosition, distance = Const.TEAM_FOLLOW_BEHIND_DISTANCE ):
		"""
		跟随位置转换

		@param targetPosition : 目标当前位置，Vector3
		rType : 与targetPosition路程为Const.TEAM_FOLLOW_BEHIND_DISTANCE米的position，Vector3

		计算出self.position到targetPosition的单位向量的反向量，然后乘模Const.TEAM_FOLLOW_BEHIND_DISTANCE
		"""
		return ( -( targetPosition - self.position ) / self.position.flatDistTo( targetPosition ) ) * distance

	def team_cancelFollow( self, statusID ):
		"""
		请求退出跟随
		"""
		self.resetTeamFollow()
		if self.isCaptain():
			self.cell.captainStopFollow()
			return
		self.statusMessage( statusID )
		self.cell.team_cancelFollow()

	def team_leaveSpace( self ):
		"""
		离开一个空间
		"""
		if not self.isJoinTeam():
			return
		if not self.isFollowing():
			return
		if self.isCaptain():
			return
		BigWorld.cancelCallback( self.teamFollowTimerID )

	def team_enterSpace( self ):
		"""
		进入空间
		"""
		if not self.isJoinTeam():
			return
		if not self.isFollowing():
			return
		if self.isCaptain():
			return
		self.team_followDetect()

	def resetTeamFollow( self ):
		"""
		重置客户端跟随数据
		"""
		BigWorld.cancelCallback( self.teamFollowTimerID )
		self.followTargetID = 0				# 跟随对象的id
		self.teamFollowTimerID = 0			# 队伍跟随侦测的timeID
		self.captainStartPosition = ( 0, 0, 0 )	# 开始跟随时队长的初始位置
		self.followWaitTime = 0				# 跟随等待时间
		self.stopMove()

	def getTeamFollowList( self ):
		"""
		获得跟随列表
		"""
		verifyFunction = lambda entity:entity.effect_state & csdefine.EFFECT_STATE_FOLLOW or entity.effect_state & csdefine.EFFECT_STATE_LEADER and entity.id in self.teamMember
		return [ entity.id for entity in self.entitiesInRange( csconst.TEAM_FOLLOW_DISTANCE, verifyFunction ) ]

	def onLeaveTeamInSpecialSpace( self, remainTime ):
		"""
		define method
		"""
		if self.teamOutSapceTimerID != 0:
			BigWorld.cancelCallback( self.teamOutSapceTimerID )
			self.teamOutSapceTimerID = 0

		if self.copyInterfaceBox:
			self.copyInterfaceBox.dispose()

		# 你已不在该副本的队伍中，将在%s秒后离开此副本。点击确定可以立刻离开。
		self.copyInterfaceBox = showMessage( mbmsgs[0x0182] %( remainTime ), "", MB_OK, self.backToLastSpace )

		def setBoxMsg( remainTime, msg ):
			"""
			"""
			self.copyInterfaceBox.setMessage( msg )
			if remainTime <= 0:
				self.copyInterfaceBox.dispose()
			
			if remainTime > 0:
				remainTime -= 1
				self.teamOutSapceTimerID = BigWorld.callback( 1, Functor( setBoxMsg, remainTime, mbmsgs[0x0182] %( remainTime ) ) )

		BigWorld.callback( 0, Functor( setBoxMsg, remainTime, mbmsgs[0x0182] %( remainTime ) ) )

	def backToLastSpace( self, rs_id ):
		"""
		"""
		self.cell.backToLastSpace()

	# -------------------------------------------------
	def prepareForTeamInvite( self ) :
		"""
		改变鼠标形状，进入准备邀请组队状态
		"""
		rds.statusMgr.setToSubStatus( Define.GST_IN_WORLD, PreInviteTemmateStatus() )

# --------------------------------------------------------------------
# 邀请组队状态
# --------------------------------------------------------------------
from StatusMgr import BaseStatus

class PreInviteTemmateStatus( BaseStatus ) :
	def __init__( self ) :
		BaseStatus.__init__( self )
		rds.ccursor.lock( "banner" )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __leave( self ) :
		"""
		离开准备邀请组队状态
		"""
		rds.statusMgr.leaveSubStatus( Define.GST_IN_WORLD, self.__class__ )
		rds.ccursor.unlock( "banner", "normal" )

	def __invite( self ) :
		"""
		发送组队邀请
		"""
		player = BigWorld.player()
		target = BigWorld.target.entity
		if target :
			#rds.targetMgr.bindTarget( target )
			if rds.targetMgr.isVehicleTarget( target ) :					# 判断是否是坐骑
				horseman = target.getHorseMan()
				if horseman is not None :
					player.inviteJoinTeamNear( horseman )
			elif rds.targetMgr.isRoleTarget( target ) :						# 并且目标是玩家
				player.inviteJoinTeamNear( target )							# 则发送组队邀请


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods  ) :
		"""
		准备邀请组队状态按键消息在此处理
		"""
		if rds.worldCamHandler.handleKeyEvent( down, key, mods ) :			# 允许移动镜头
			return True

		if key == keys.KEY_LEFTMOUSE and mods == 0 :
			if down :
				if rds.ruisMgr.isMouseHitScreen() :
					self.__invite()
			else :
				self.__leave()
			return True
		elif key == keys.KEY_ESCAPE :
			self.__leave()
			return True
		return False


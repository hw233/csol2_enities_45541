# -*- coding: gb18030 -*-
#
# $Id: Team.py,v 1.44 2008-08-07 07:10:40 phw Exp $

import time
import BigWorld
from bwdebug import *
import csdefine
import csstatus
import csconst
import ECBExtend

TEAM_INVITE_TIME_OUT = 30
CLEAR_FOBID_TEAM_TEIM = 300


class Functor:
	def __init__( self, fn, *args ):
		self._fn = fn
		self._args = args

	def __call__( self, *args ):
		self._fn( *( self._args + args ) )

class Team:
	def __init__( self ):
		#self.teamID				# 记录自己所属的队伍ID，用于玩家上线时从新找回队伍
		self.captainID = 0			# 队长ID
		self.teamMailBox = None		# 队伍mailbox
		self._teamMembers = {}		# 队伍成员列表：{ playerDBID : playerBaseMailbox, ... }
		self._teamMembersID = {}	# 队伍成员列表附加：{ playerDBID : playerID, ... }
		self.pickUpState = csdefine.TEAM_PICKUP_STATE_ORDER

		#self.headTextureID = 0		# 被邀请者的头像ID				这个属性在Role.def中定义，不需要在这个接口里重写

		self._inviteTeamTime = 0.0	# 被邀请的时间
		self._inviterBase = None	# 邀请者的BASE MAILBOX，用于记录当前我是被谁邀请加入队伍

		self.clearFobidTeamTimerID = 0	# 清理拒绝组队玩家数据的timerID
		self.refuseTeamPlayerDict = {}		# 被拒绝加队的玩家数据，例如：{ 玩家id:拒绝时间, ... }

	def getTeamMailbox(self):
		"""
		取队伍MailBox
		"""
		return self.teamMailBox

	def getTeamMemberDBID( self, entityID ):
		"""
		根据队员的entityID获取相对应的dbid

		@return: databaseID
		"""
		for dbid, id in self._teamMembersID.iteritems():
			if id == entityID:
				return dbid
		return 0

	def getTeamMemberMailbox( self, entityID ):
		"""
		通过玩家的entity ID获取相应的mailbox
		"""
		for e in self._teamMembers.itervalues():
			if e == None:
				continue
			if entityID == e.id:
				return e
		return None

	def isInTeam( self ):
		"""
		判断玩家是否已在队伍中
		"""
		# 使用teamID来判断而不是使用teamMailBox是因此只有teamID才会在玩家下线的时候存储
		return self.teamID != 0

	def isCaptain( self ):
		"""
		是不是队长
		"""
		return self.captainID == self.id

	def isTeamFull( self ):
		"""
		是否队伍满员
		"""
		return self.teammateAmount() >= csconst.TEAM_MEMBER_MAX

	def teammateAmount( self ) :
		"""
		队员数量
		"""
		return len( self._teamMembers )

	def teamInviteBy( self, inviterBase, inviterName, inviterCamp ):
		"""
		define method.
		被某玩家邀请组队，这里是邀请组队的最终入口，无论是近程邀请还是远程邀请。

		@param inviterBase: 邀请者BASE
		@type inviterBase: mailbox
		@param inviterName: 邀请者名称
		@type inviterName: string
		"""
		if not inviterBase:
			ERROR_MSG("invite player base is none.")
			return

		# 如果已经组队
		if self.isInTeam():
			inviterBase.client.onStatusMessage( csstatus.TEAM_PLAYER_IN_TEAM, "" )
			return

		# 已经被其他玩家邀请，且没过邀请时效
		if self._inviterBase and time.time() - self._inviteTeamTime < TEAM_INVITE_TIME_OUT:
			inviterBase.client.onStatusMessage( csstatus.TEAM_PLAYER_IN_TEAM_INVITE, "" )
			return

		self.cell.teamInviteBy( inviterBase, inviterName, inviterCamp )

	def teamInvitedToBy( self, inviterBase, inviterName ):
		"""
		define method.
		被某玩家邀请组队
		"""
		# 记录邀请者及邀请时间，以避免其他的邀请者邀请
		
		self._inviterBase = inviterBase
		self._inviteTeamTime = time.time()

		self.client.teamInviteBy( inviterName )
		#向发送邀请的玩家发送消息
		targetName = self.getName()
		inviterBase.client.onStatusMessage( csstatus.TEAM_INVITE_PLAYER, "(\'%s\',)" % targetName )

	def teamRemoteInviteFC( self, playerName ):
		"""
		exposed method.
		发起远程组队请求

		@param playerName	: 玩家名称
		@type playerName	: string
		"""
		if self.getName() == playerName:
			self.statusMessage( csstatus.TEAM_NOT_INVITE_SELF )
			return
		if self.isInTeam():
			if self.isTeamFull() :
				self.statusMessage( csstatus.TEAM_FULL )
				return

		BigWorld.lookUpBaseByName( "Role", playerName, Functor( self.teamFindPlayerCallback, playerName ) )

	def teamFindPlayerCallback( self, name, target ):
		"""
		找到目标且已上线，target == BASE MAILBOX;
		找到目标但未上线，target == True;
		其它原因（如无此角色等），target == False;

		@param name: 玩家名称
		@type name: string
		@param target:目标实体Base
		@type target: mailbox
		"""
		if not isinstance( target, bool ):
			if self.isInTeam():
				if self.isCaptain():
					target.teamInviteBy( self, self.playerName, self.getCamp() )
				else:
					self.cell.teamInviteByTeammate( name, target )
			else:
				target.teamRequestRemote( self, self.getName(), self.level, self.raceclass,self.isInTeam() )
		elif target:# target offline
			#ERROR_MSG( "player offline! Name:", name )
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_EXIST )
		else:	# target not in database
			#ERROR_MSG( "not find player! Name:", name )
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_EXIST )

	def teamInviteByTeammate( self, name, target ):
		"""
		Define method.
		队友邀请目标玩家入队
		"""
		captianMB = self.getTeamMemberMailbox( self.captainID )
		if captianMB:
			captianMB.client.teamInviteByTeammate( name, target.id, self.getName(), self.id )

	def teamRequestRemote( self, inviterMailbox, inviterName, inviterLevel, inviterRaceclass, isInTeam ):
		"""
		Define method.
		远程组队请求

		@param inviterMailbox : 发起者的mailbox
		@type inviterMailbox : MAILBOX
		@param inviterName : 发起者的名字
		@type inviterName : STRING
		@param isInTeam : 发起者是否已有队伍
		@type isInTeam : BOOL
		"""
		if self.isInTeam():
			if self.isTeamFull():
				inviterMailbox.client.onStatusMessage( csstatus.TEAM_FULL_REFUSE_JOIN, "" )
				return	
			if isInTeam:							
				inviterMailbox.client.onStatusMessage( csstatus.TEAM_PLAYER_IN_TEAM, "" )
				return
			if self.isCaptain():
				self.client.receiveJoinTeamRequest( inviterName, inviterRaceclass, inviterLevel, inviterMailbox.id )
				inviterMailbox.client.onStatusMessage( csstatus.TEAM_REQUEST_HAD_BEEN_SEND, "" )
			else:
				captianMB = self.getTeamMemberMailbox( self.captainID )
				if captianMB:
					captianMB.client.receiveJoinTeamRequest( inviterName, inviterRaceclass, inviterLevel, inviterMailbox.id )
		else:
			inviterCamp = ( inviterRaceclass & csdefine.RCMASK_CAMP ) >> 20
			self.teamInviteBy( inviterMailbox, inviterName, inviterCamp )

	def receiveJoinTeamRequest( self, playerName, raceclass, level, playerBase ):
		"""
		Define method.
		队长收到加队申请
		"""
		
		if playerBase.id in self.refuseTeamPlayerDict:
			playerBase.client.onStatusMessage( csstatus.TEAM_REQUEST_FORBID, "( \'%s\', )" % self.getName() )
			return
			
		if self.isTeamFull():
			# 通知申请者，所加入的队伍已满，无法加入
			playerBase.client.onStatusMessage( csstatus.TEAM_FULL_REFUSE_JOIN, "" )
			return
		playerBase.client.onStatusMessage( csstatus.TEAM_REQUEST_HAD_BEEN_SEND, "" )	
		self.client.receiveJoinTeamRequest( playerName, raceclass, level, playerBase.id )

	def refusePlayerJoinTeam( self, playerName ):
		"""
		Exposed method.
		拒绝玩家的加队申请

		@param playerID : 被拒绝玩家的playerName
		@type playerID : STRING
		"""
		if not self.isCaptain():
			return
		BigWorld.lookUpBaseByName( "Role", playerName, self.lookUpRefuseTeamPlayerCB )

	def lookUpRefuseTeamPlayerCB( self, playerBase ):
		"""
		通过名字查找被拒绝组队玩家名字的回调
		"""
		if isinstance( playerBase, bool ):
			return
		playerBase.client.onStatusMessage( csstatus.TEAM_REQUEST_FORBID, "( \'%s\', )" % self.getName() )
		self.addFobidTeamPlayer( playerBase.id )

	def addFobidTeamPlayer( self, playerID ):
		"""
		Define method.
		增加被拒绝玩家数据
		"""
		self.refuseTeamPlayerDict[playerID] = time.time()
		if not self.clearFobidTeamTimerID:
			self.clearFobidTeamTimerID = self.addTimer( CLEAR_FOBID_TEAM_TEIM, CLEAR_FOBID_TEAM_TEIM, ECBExtend.TEAM_CLEAR_REFUSE_PLAYER_CBID )

	def onTemer_clearFobidTeamPlayer( self, timerID, userData ):
		"""
		清理被拒绝加队玩家timer回调
		"""
		for playerID, refuseTime in self.refuseTeamPlayerDict.items():
			if refuseTime + CLEAR_FOBID_TEAM_TEIM > time.time():
				del self.refuseTeamPlayerDict[playerID]

		if len( self.refuseTeamPlayerDict ) == 0:
			self.delTimer( self.clearFobidTeamTimerID )
			self.clearFobidTeamTimerID = 0

	def captainAcceptTeamNear( self, captainBase, captainName ):
		"""
		Define method.
		队长接受了加队申请
		"""
		# 如果已经组队
		if self.isInTeam():
			captainBase.client.onStatusMessage( csstatus.TEAM_PLAYER_IN_TEAM, "" )
			return

		# 已经被其他玩家邀请，且没过邀请时效
		if self._inviterBase and time.time() - self._inviteTeamTime < TEAM_INVITE_TIME_OUT:
			captainBase.client.onStatusMessage( csstatus.TEAM_PLAYER_IN_TEAM_INVITE, "" )
			return

		# 记录邀请者及邀请时间，以避免其他的邀请者邀请
		self._inviterBase = captainBase
		self._inviteTeamTime = time.time()

		captainBase.replyTeamInvite( True, self.getName(), self )

	def acceptTeamRequset( self, targetName ):
		"""
		Exposed method.
		队长接收加队请求

		@param targetName : 同意的目标名字
		@type targetName : STRING
		"""
		if not self.isCaptain():
			return
		if self.isTeamFull():
			return

		BigWorld.lookUpBaseByName( "Role", targetName, self.acceptTeamLookUpCB )

	def acceptTeamLookUpCB( self, playerMailbox ):
		"""
		队长接受玩家加队请求，根据名字查找玩家base mailbox的回调
		"""
		playerMailbox.captainAcceptTeamRequest( self )

	def captainAcceptTeamRequest( self, captainMailbox ):
		"""
		Define method.
		队长接受了加队请求，根据申请者情况判断是否可以组队

		@param captainMailbox : 申请加队的目标队长base mailbox
		@type captainMailbox : MAILBOX
		"""
		# 如果已经组队
		if self.isInTeam():
			captainMailbox.client.onStatusMessage( csstatus.TEAM_PLAYER_IN_TEAM, "" )
			return

		# 已经被其他玩家邀请，且没过邀请时效
		if self._inviterBase and time.time() - self._inviteTeamTime < TEAM_INVITE_TIME_OUT:
			captainMailbox.client.onStatusMessage( csstatus.TEAM_PLAYER_IN_TEAM_INVITE, "" )
			return

		# 记录邀请者及邀请时间，以避免其他的邀请者邀请
		self._inviterBase = captainMailbox
		self._inviteTeamTime = time.time()

		captainMailbox.replyTeamInvite( True, self.getName(), self )

	#---------------------------------------------------------------------------------
	def replyTeamInviteByFC( self, agree ):
		"""
		exposed method.
		由客户端调用，答复组队邀请，因此此方法会在被邀请者的base上执行。

		@param agree:同意加入
		@type agree:INT8
		"""
		if self._inviterBase:
			# 在异步下这是有可能的，
			# 因此我并不知道玩家被邀请时是否也邀请了别人，因此必须要分个先来后到
			# 如果确实需要限制邀请了别人时不允许别人邀请，
			# 可以在客户端的被邀请接口中直接判断
			if self.isInTeam():
				# 已加入队伍
				self.statusMessage( csstatus.TEAM_SELF_IN_TEAM )
				self._inviterBase.replyTeamInvite( False, self.getName(), self )
				self._inviterBase = None
				self._inviteTeamTime = 0.0
			else:
				# 没有加入队伍
				self._inviterBase.replyTeamInvite( agree, self.getName(), self )
				if not agree:
					self._inviterBase = None
					self._inviteTeamTime = 0.0
		else:
			WARNING_MSG( "not invite join to team! name:", self.getName() )

	def replyTeamInvite( self, agree, replierName, replierBase ):
		"""
		define method.
		被邀请者回复邀请者关于组队的邀请，因此此方法会在邀请者的base上执行。

		@param replierName: 回复者的名称
		@type  replierName: string
		@param playerBase: 回复者的BASE
		@type  playerBase: mailbox
		"""
		if not agree:
			self.statusMessage( csstatus.TEAM_PLAYER_REFUSE_JOIN )
			return

		# 能走到这一步，没有队伍mailbox就表示队伍不存在，创建队伍
		if self.teamMailBox == None:
			self.createSelfTeamLocally()
			# 通知副本组队系统进行处理
			self.cmi_onJoinTeam()

		if self.isTeamFull():
			# 通知被邀请者，所加入的队伍已满，无法加入
			replierBase.joinFullTeamNotify()
			return
		# 通知玩家加入
		replierBase.joinTeamNotify( self.id, self.teamMailBox )

	def joinFullTeamNotify( self ):
		"""
		define method.
		通知加入的队伍已满，同时清除邀请信息。
		"""
		self._inviterBase = None
		self._inviteTeamTime = 0.0
		self.statusMessage(csstatus.TEAM_FULL_REFUSE_JOIN)

	def joinTeamNotify( self, captainID, teamMailBox ):
		"""
		define method.
		通知被邀请者加入队伍，因此此方法会在被邀请者的base上执行

		@param captainID: 队长的EntityID
		@type  captainID: OBJECT_ID
		@param teamMailBox: 队伍BASE
		@type  teamMailBox: mailbox
		"""
		if self.isInTeam():
			# 如果我已经加入队伍，当前什么事情都不做
			return

		# 在这里我们假设已经加入了队伍
		# 因此会设置队伍mailbox，并去掉邀请者的记录
		self.teamMailBox = teamMailBox
		self.teamID = teamMailBox.id
		self.captainID = captainID
		self._inviterBase = None
		self._inviteTeamTime = 0.0

		# 通知
		#if hasattr( self, "cell" ):
		#	self.cell.teamInfoNotify( captainDBID, teamMailBox )
		#self.client.teamInfoNotify( teamID, captainID )

		# 把自己添加到队伍
		self.teamMailBox.join( self.databaseID, self.playerName, self, self.raceclass, self.headTextureID )
		# 通知副本组队系统进行处理
		self.cmi_onJoinTeam()

	#---------------------------------------------------------------------------------

	def addTeamMember( self, playerDBID, entityID, playerName, playerBase, playerRaceclass, headTextureID ):
		"""
		define method.
		添加成员数据

		过程：
		　向成员列表里添加成员
		@param entityID:   玩家的ID
		@type  entityID:   object_id
		@param playerDBID: 玩家DBID
		@type  playerDBID: DATABASE_ID
		@param   entityID: 队员的entityID，有此值的原因是新加入的队员也需要知道已下线的队员的entityID(已下线的队员的mailbox为None)
		@type    entityID: OBJECT_ID
		@param playerBase: 玩家BASE
		@type  playerBase: mailbox
		@param playerName: 玩家名称
		@type  playerName: string
		@param playerRaceclass: 玩家职业
		@type  playerRaceclass: INT32
		"""
		# 添加成员
		self._teamMembers[playerDBID] = playerBase
		self._teamMembersID[playerDBID] = entityID
		# 通知cell和client
		if hasattr( self, "cell" ) and playerBase:		# 只有playerBase不为None（在线）时才会通知cell
			self.cell.addTeamMember( playerDBID, playerBase )
		if hasattr( self, "client" ):
			self.client.addTeamMember( entityID, playerDBID, playerName, playerRaceclass, int( playerBase is not None ), headTextureID )

	#---------------------------------------------------------------------------------
	# 玩家离队、开除、队伍解散
	def leaveTeamNotify( self, srcEntityID, dstEntityID ):
		"""
		define method.
		玩家离开通知，此接口由TeamEntity调用

		@param srcEntityID: 玩家的EntityID
		@type  srcEntityID: OBJECT_ID
		@param dstEntityID: 玩家DBID
		@type  dstEntityID: DATABASE_ID
		"""
		# 在异步的情况下，不存在cell或client是有可能出现的
		if hasattr( self, "cell" ):
			self.cell.removeTeamMember( dstEntityID )
		if hasattr( self, "client" ) and self.client:
			self.client.leaveTeamNotify( dstEntityID, int( srcEntityID != dstEntityID ) )

		if dstEntityID == self.id:
			# 自己离开
			self.clearTeamInfo()
			self._teamMembers.clear()
			self._teamMembersID.clear()
			self.cmi_onLeaveTeam()
		else:
			# 队友离开
			playerDBID = self.getTeamMemberDBID( dstEntityID )
			if playerDBID != 0:
				self._teamMembers.pop( playerDBID )
				self._teamMembersID.pop( playerDBID )

	def leaveTeamFC( self, playerID ):
		"""
		exposed method.
		玩家自己离队或开除玩家离队。
		1、如果playerID是自己则是离队；
		2、如果playerID不是自己且自己是队长则开除playerID出队伍
		@param playerID: 开除的玩家ID
		@type  playerID: OBJECT_ID
		"""
		if not self.isInTeam():
			# 未加入任何队伍
			return

		if self.id != playerID and self.id != self.captainID:
			# 既不是自己离队，也不是队长开除，直接忽略
			return

		self.teamMailBox.leave( self.id, playerID )

	#---------------------------------------------------------------------------------
	def disbandTeamFC( self ):
		"""
		exposed method.
		请求解散队伍，此方法用于客户端

		过程：
		　条件判断
		　1、玩家不是队长，中断操作

		　调用队伍的解散队伍
		"""
		if not self.isCaptain():
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_CAPTAIN )
			return
		if self.teamMailBox == None:
			return
		self.teamMailBox.disband()

	def disbandTeamNotify( self ):
		"""
		define method.
		队伍解散通知，此方法由TeamEntity调用
		"""
		self.clearTeamInfo()
		self._teamMembers.clear()
		self._teamMembersID.clear()
		if hasattr( self, "cell" ):
			self.cell.disbandTeamNotify()
			self.client.disbandTeamNotify()
		self.cmi_onLeaveTeam()

	def clearTeamInfo( self ):
		"""
		define method.
		清除队伍信息，此方法一般会用于队伍解散或加入队伍失败时。
		如：调用teamMailbox.join()尝试加入队伍失败时就会调用此方法。
		"""
		self.teamID = 0
		self.captainID = 0
		self.teamMailBox = None

	def changeCaptainFC( self, playerID ):
		"""
		exposed method.
		移交队长权限，此接口由client调用

		@param playerID: 玩家DBID
		@type playerID: DATABASE_ID
		"""
		# 移交的目标不能是自己
		if self.id == playerID:
			return

		# 没有加入任何队伍
		if not self.isInTeam():
			self.statusMessage( csstatus.TEAM_NOT_IN_TEAM )
			return

		# 不是队长
		if not self.isCaptain():
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_CAPTAIN )
			return

		# 队伍中没有此玩家
		if self.getTeamMemberDBID( playerID ) == 0:
			self.statusMessage( csstatus.TEAM_NOT_IN_TEAM )
			return

		# 该队员不在线
		if not self.getTeamMemberMailbox( playerID ):
			self.statusMessage( csstatus.TEAM_NOT_ON_LINE )
			return

		self.teamMailBox.changeCaptain( playerID )

	def changeCaptainNotify( self, captainID ):
		"""
		define method.
		队长改变

		过程：
		　改变队长标记，设置新队长
		　通知cell，队长改变

		@param captainID: 队长玩家DBID
		@type  captainID: DATABASE_ID
		"""
		self.captainID = captainID
		# 在异步的情况下，不存在cell或client是有可能出现的
		if hasattr( self, "cell" ):
			self.cell.changeCaptainNotify( captainID )
		if hasattr( self, "client" ):
			self.client.changeCaptainNotify( captainID )

	#---------------------------------------------------------------------------------
	# 玩家上线
	def logonForTeam( self ):
		"""
		玩家上线
		"""
		# 取队伍管理器
		try:
			teamManager = BigWorld.globalBases["TeamManager"]
		except:
			teamManager = None
			ERROR_MSG( "get team manager entity error!" )
			return

		teamManager.rejoinTeam( self.teamID, self.databaseID, self )

	def team_onLogout( self ):
		"""
		玩家自已下线处理
		在这里必须清除玩家对自身的引用，否则会有交叉引用问题，从而导致内存泄漏
		"""
		if self.teamMailBox:
			self.teamMailBox.logout( self.databaseID )
		self.teamMailBox = None
		self._teamMembers.clear()	# 这个不清除，会引发内存泄漏

	def teamInfoNotify( self, captainID, teamEntity ):
		"""
		define method.
		设置队伍信息
		@param captainID: 玩家BASE
		@type  captainID: mailbox
		@param teamEntity: 玩家BASE，如果值为None，则表示队伍不再存在
		@type  teamEntity: mailbox
		"""
		self.teamMailBox = teamEntity
		self.captainID = captainID
		if teamEntity:
			self.teamID = teamEntity.id
		else:
			self.teamID = 0
		self.cell.teamInfoNotify( captainID, teamEntity )
		self.client.teamInfoNotify( teamEntity.id, captainID )

	def rejoinTeam( self, oldEntityID, playerDBID, playerBase ):
		"""
		define method.
		成员上线

		过程：
		　修改成员列表的成员在线状态
		　通知cell，成员上线

		@param playerDBID: 玩家DBID
		@type playerDBID: DATABASE_ID
		@param playerBase: 玩家BASE
		@type playerBase: mailbox
		"""
		self._teamMembers[playerDBID] = playerBase
		self._teamMembersID[playerDBID] = playerBase.id


		# 在异步的情况下，不存在cell或client是有可能出现的
		if hasattr( self, "cell" ):
			self.cell.addTeamMember( playerDBID, playerBase )
		if hasattr( self, "client" ):
			self.client.rejoinTeam( oldEntityID, playerBase.id )

	def logoutNotify( self, playerDBID ):
		"""
		define method.
		队员下线

		过程：
		　在成员列表里设置玩家为下线状态
		　通知cell，该玩家离线

		@param playerDBID: 玩家DBID
		@type playerDBID: DATABASE_ID
		"""
		# 在异步的情况下，不存在cell或client是有可能出现的
		if hasattr( self, "cell" ):
			self.cell.removeTeamMember( self._teamMembers[playerDBID].id )
		if hasattr( self, "client" ):
			self.client.logoutNotify( self._teamMembers[playerDBID].id )

		self._teamMembers[playerDBID] = None

	def changePickUpState( self, state ):
		"""
		exposed method.
		更改物品拾取方式，此接口由client队长调用

		@param state: 更改的拾取方式 define in csdefine.py
		@type state: INT8
		"""
		# 没有加入任何队伍
		if not self.isInTeam():
			self.statusMessage( csstatus.TEAM_NOT_IN_TEAM )
			return

		# 不是队长
		if not self.isCaptain():
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_CAPTAIN )
			return

		if self.pickUpState == state: return

		self.teamMailBox.onChangePickUpState( state )


	def changePickUpQuality( self, val ):
		"""
		exposed method.
		"""
		# 没有加入任何队伍
		if not self.isInTeam():
			self.statusMessage( csstatus.TEAM_NOT_IN_TEAM )
			return

		# 不是队长
		if not self.isCaptain():
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_CAPTAIN )
			return

		self.teamMailBox.onChangePickUpQuality( val )


	def changeRollQuality( self, val ):
		"""
		exposed method.
		改变ROLL规则的判定品质
		"""
		# 没有加入任何队伍
		if not self.isInTeam():
			self.statusMessage( csstatus.TEAM_NOT_IN_TEAM )
			return

		# 不是队长
		if not self.isCaptain():
			self.statusMessage( csstatus.TEAM_PLAYER_NOT_CAPTAIN )
			return

		self.teamMailBox.onChangeRollQuality( val )



	def changePickUpStateNotify( self, state ):
		"""
		define method.
		更改物品拾取方式通知

		@param state: 更改的拾取方式 define in csdefine.py
		@type state: INT8
		"""
		self.pickUpState = state

		# 在异步的情况下，不存在cell或client是有可能出现的
		if hasattr( self, "cell" ):
			self.cell.changePickUpStateNotify( state )
		if hasattr( self, "client" ):
			self.client.changePickUpStateNotify( state )



	#---------------------------------------------------------------------------------
	def requestTeammateInfoFC( self, playerID ):
		"""
		exposed method.
		更新指定玩家的信息

		@param playerID: 玩家ID
		@type  playerID: OBJECT_ID
		"""
		mailbox = self.getTeamMemberMailbox( playerID )
		if mailbox is None:
			ERROR_MSG("other player get member data!")
			return
		mailbox.cell.requestTeammateInfo( self )

	def requestTeammatePetInfoFC( self, playerID ):
		"""
		exposed method.
		更新指定队友宠物的信息

		@param playerID: 玩家ID
		@type  playerID: OBJECT_ID
		"""
		mailbox = self.getTeamMemberMailbox( playerID )
		if mailbox is None:
			ERROR_MSG("other player get member data!")
			return
		mailbox.cell.requestTeammatePetInfo( self )

	def teamChat( self, msg, blobArgs ):
		"""
		defined method
		队聊，被RoleChat.py调用

		@param       msg: 聊天的内容
		@type        msg: STRING
		@param		blobArgs : 消息参数列表
		@type		blobArgs : BLOB_ARRAY
		@return:          无
		"""
		if self.teamMailBox is None:
			DEBUG_MSG( "not in team." )
			return

		# 如果需要对聊天的速度进行限制，例如每秒只能发一句对聊，可以在这里插入相关代码
		# in here, to do

		for mailbox in self._teamMembers.itervalues():
			if mailbox:
				mailbox.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_TEAM, self.id, self.playerName, msg, blobArgs )

	def getTeamMemberIDs( self ):
		"""
		"""
		return self._teamMembersID.values()

	def refuseTeammateInvite( self, targetName, teammateID ):
		"""
		Exposed method.
		拒绝队友邀请其他玩家的入队请求

		@param taregetName : 队友邀请的目标玩家名字
		@type taregetName : STRING
		@param teammateID : 队友的entity id
		@type teammateID : OBJECT_ID
		"""
		teammateMailBox = self.getTeamMemberMailbox( teammateID )
		if teammateMailBox:
			teammateMailBox.client.onStatusMessage( csstatus.TEAM_CAPTAIN_REFUSE_INVITE, "(\'%s\',)" % targetName )

	def createTeamBySelf( self ):
		"""
		Exposed method.
		自建队伍
		"""
		if self.teamMailBox == None:
			self.createSelfTeamLocally()
			self.statusMessage( csstatus.TEAM_CREATE_SELF_NOTICE )
			# 通知副本组队系统进行处理
			self.cmi_onJoinTeam()
		else:
			self.statusMessage( csstatus.TEAM_IN_TEAM_NOT_CREATE_SELF )

	def createSelfTeamLocally( self ) :
		"""
		在本地base上创建自己的队伍
		"""
		if self.teamMailBox is not None :
			WARNING_MSG( "[%s(id:%i)]: I am still in a team(ID:%i)." % ( self.getName(), self.id, self.teamMailBox.id ) )
		teamArg = {	"captainDBID"	: self.databaseID,
					"captainName"	: self.getName(),
					"captainBase"	: self,
					"captainRaceclass"	: self.raceclass,
					"pickUpState"	: csdefine.TEAM_PICKUP_STATE_ORDER,
					"captainHeadTextureID"	: self.headTextureID
					}
		self.teamMailBox = BigWorld.createBaseLocally( "TeamEntity", { "teamArg":teamArg } )
		self.teamID = self.teamMailBox.id
		self.captainID = self.id

# end of method: teamChat()

# -*- coding: gb18030 -*-
#


"""
"""
from FuncTeleport import FuncTeleport
import csdefine
import csconst
import BigWorld
import time
import csstatus
from Function import Function

ENTERN_YAYU_MENBER_DISTANCE = 30.0
class FuncEnterYayu( FuncTeleport ):
	"""
	进入猰貐副本
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		FuncTeleport.__init__( self, section )
		self.recordKey = "yayu_record"

	def checkTeamMembers( self, player ):
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyYayuType", csconst.SPACE_COPY_YE_WAI_EASY )
	
	def do( self, player, talkEntity = None ):
		"""
		进入猰貐副本。
		规则：
			创建条件：（把队员都拉进来）
				这个队伍当前没有副本。
				要求进入者是队长。
				达到等级要求。
				队伍人数大于3人。
				队伍成员没有进入过副本的。
			进入条件：（只有自己一个人进去）
				有组队。
				有队伍副本存在。

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )

		#if not BigWorld.globalData.has_key('AS_yayuStart') or not BigWorld.globalData["AS_yayuStart"]:
		#	#猰貐活动没有开启
		#	player.statusMessage( csstatus.YAYU_IS_NOT_OPEN )
		#	return	
		if self.repLevel > player.level:
			#玩家等级不够
			player.statusMessage( csstatus.YAYU_LEVEL_NOT_ARRIVE, self.repLevel )
			return
			
		if not player.isInTeam():
			#玩家没有组队
			player.statusMessage( csstatus.YAYU_NEED_TEAM )
			return

		if BigWorld.globalData.has_key( 'Yayu_%i'%player.getTeamMailbox().id ):
			#玩家的队伍拥有一个猰貐副本
			if player.isActivityCanNotJoin( csdefine.ACTIVITY_ZHENG_JIU_YA_YU )  and player.query( "lastYayuTeamID", 0 ) != player.getTeamMailbox().id:
				player.client.onStatusMessage( csstatus.YAYU_IN_ALREADY, "" )
				return
			player.gotoSpace( self.spaceName, self.position, self.direction )
		else:
			#队伍没有副本，则走创建流程
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return
			pList = player.getAllMemberInRange( ENTERN_YAYU_MENBER_DISTANCE )
			
			if not self.checkTeamMembers( player ) :
				return
			
			lowLevelMembersStr = ""
			enteredMembersStr = ""
			for i in pList:
				if i.level < self.repLevel:
					lowLevelMembersStr += ( i.getName() + "," )
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_ZHENG_JIU_YA_YU ) :
					enteredMembersStr += ( i.getName() + "," )
			# 队伍中有人级别不够
			if lowLevelMembersStr != "":
				player.statusMessage( csstatus.ROLE_MEMBER_HAS_NOT_YAYU_LEVEL, lowLevelMembersStr, self.repLevel )
				return
			# 队伍中有人已经参加过猰貐活动
			if enteredMembersStr != "":
				player.statusMessage( csstatus.YAYU_HAS_ENTERED_TODAY, enteredMembersStr )
				return

			for i in pList:
				i.set( "lastYayuTeamID", player.getTeamMailbox().id )
				self.setMemberFlags( i )
				i.gotoSpace( self.spaceName, self.position, self.direction )

class FuncEnterYayuEasy( FuncEnterYayu ):
	# 进入猰貐副本简单模式
	def __init__( self, section ):
		FuncEnterYayu.__init__( self, section )
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() != csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_EASY ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyYayuType", csconst.SPACE_COPY_YE_WAI_EASY )

class FuncEnterYayuDefficulty( FuncEnterYayu ):
	# 进入猰貐副本困难模式
	def __init__( self, section ):
		FuncEnterYayu.__init__( self, section )
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_DIFFICULTY ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyYayuType", csconst.SPACE_COPY_YE_WAI_DIFFICULTY )

class FuncEnterYayuNightmare( FuncEnterYayu ):
	# 进入猰貐副本噩梦模式
	def __init__( self, section ):
		FuncEnterYayu.__init__( self, section )
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_NIGHTMARE ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyYayuType", csconst.SPACE_COPY_YE_WAI_NIGHTMARE )


class FuncHelpYayu( Function ):
	"""
	帮助猰貐，进入战斗
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )

	def do( self, player, talkEntity = None ):
		"""
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		talkEntity.onActived()

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		if talkEntity == None:
			return False
		return talkEntity.queryTemp( "yayuCanTalk", False )


class FuncYayuThanks( Function ):
	"""
	帮助猰貐，进入战斗
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )

	def do( self, player, talkEntity = None ):
		"""
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		talkEntity.onThankOver()

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		if talkEntity == None:
			return False
		return talkEntity.queryTemp( "yayuFinishTalk", False )

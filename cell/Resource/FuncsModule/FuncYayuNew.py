# -*- coding: gb18030 -*-
#

from FuncTeleport import FuncTeleport
from Function import Function
import csdefine
import csconst
import BigWorld
import time
import csstatus

ENTERN_YAYU_MENBER_DISTANCE = 30.0
ENTER_YAYU_POSITION	= (4, 2, 4)				#进入猰狳的位置

class FuncEnterYayuNew( FuncTeleport ):
	"""
	进入猰貐副本
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		FuncTeleport.__init__( self, section )
		self.recordKey = "yayu_record_new"

	def checkTeamMembers( self, player ):
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyYayuType", csconst.SPACE_COPY_YE_WAI_DIFFICULTY )
	
	def do( self, player, talkEntity = None ):
		"""
		进入猰貐副本。
		规则：
			创建条件：（把队员都拉进来）
				这个队伍当前没有副本。
				要求进入者是队长。
				达到等级要求。
				队伍人数不能大于副本模式对应人数
				队伍成员没有进入过副本的。
		只有自己一个人不能进入副本
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )

		if self.repLevel > player.level:
			#玩家等级不够
			player.statusMessage( csstatus.YAYU_LEVEL_NOT_ARRIVE, self.repLevel )
			return
			
		if not player.isInTeam():
			#玩家没有组队
			player.statusMessage( csstatus.YAYU_NEW_NEED_TEAM )
			return
		
		if BigWorld.globalData.has_key( 'Yayu_%i'%player.getTeamMailbox().id ):
			#玩家的队伍拥有一个猰貐副本，不能再进入
			player.client.onStatusMessage( csstatus.YAYU_NEW_HAS_ENTERED_TODAY, "" )
			return
		
		#队伍没有副本，则走创建流程
		if not player.isTeamCaptain():
			player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
			return
			
		# 判断是否队伍成员都在
		teamMemberIDs = player.getAllIDNotInRange( ENTERN_YAYU_MENBER_DISTANCE )
		if len( teamMemberIDs ) > 0:
			for id in teamMemberIDs:
				player.client.teamNotifyWithMemberName( csstatus.TEAM_MEMBER_NOT_IN_RANGE, id )
			return
		
		if not self.checkTeamMembers( player ) :
			return
		
		# 队员条件判断	
		pList = player.getAllMemberInRange( ENTERN_YAYU_MENBER_DISTANCE )
		lowLevelMembersStr = ""
		enteredMembersStr = ""
		for i in pList:
			if i.level < self.repLevel:
				lowLevelMembersStr += ( i.getName() + "," )
			if i.isActivityCanNotJoin( csdefine.ACTIVITY_ZHENG_JIU_YA_YU_NEW ) :
				enteredMembersStr += ( i.getName() + "," )
		
		if lowLevelMembersStr != "":
			# 队伍中有人级别不够
			player.statusMessage( csstatus.ROLE_MEMBER_HAS_NOT_YAYU_LEVEL, lowLevelMembersStr, self.repLevel )
			return
		
		"""
		为了方便测试，暂时不做次数判断
		if enteredMembersStr != "":
			# 队伍中有人已经参加过猰貐活动
			player.statusMessage( csstatus.YAYU_NEW_HAS_FINISHED_TODAY, enteredMembersStr )
			return
		"""
		
		# 进入副本
		pList.remove( player )
		self.setMemberFlags( player )
		player.gotoSpace( self.spaceName, self.position, self.direction )
		
		for i in pList:
			self.setMemberFlags( i )
			i.gotoSpace( self.spaceName, self.position, self.direction )

class FuncEnterYayuNewDifficulty( FuncEnterYayuNew ):
	# 进入猰貐副本困难模式
	def __init__( self, section ):
		FuncEnterYayuNew.__init__( self, section )
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_DIFFICULTY ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyYayuType", csconst.SPACE_COPY_YE_WAI_DIFFICULTY )

class FuncEnterYayuNewNightmare( FuncEnterYayuNew ):
	# 进入猰貐副本噩梦模式
	def __init__( self, section ):
		FuncEnterYayuNew.__init__( self, section )
	
	def checkTeamMembers( self, player ):
		if player.getTeamCount() > csconst.SPACE_COPY_YE_WAI_ENTER_MAP[ csconst.SPACE_COPY_YE_WAI_NIGHTMARE ] :
			player.statusMessage( csstatus.SPACE_COOY_YE_WAI_RESTRICT_TEAM_NUM )
			return False
			
		return True
	
	def setMemberFlags( self, member ):
		member.setTemp( "EnterSpaceCopyYayuType", csconst.SPACE_COPY_YE_WAI_NIGHTMARE )
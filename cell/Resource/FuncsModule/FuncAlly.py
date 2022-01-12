# -*- coding: gb18030 -*-

from bwdebug import *
from Function import Function
import csconst
import csstatus

class FuncAllyRequest( Function ):
	"""
	我们要一起闯天下，请求结拜
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		对话选项有效性检查
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		触发对话选项要做的事情
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		#DEBUG_MSG( "-->>rlt_askForStartAlly" )
		player.endGossip( talkEntity )
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		if player.hasAllyRelation():
			player.statusMessage( csstatus.CANNOT_ALLY_HAD_ALREADY )
			return
		player.client.rlt_askForStartAlly()
		
		
class FuncAllyJoinNewMember( Function ):
	"""
	我们有新兄弟了，请求加入
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		对话选项有效性检查
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		触发对话选项要做的事情
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		#DEBUG_MSG( "-->>rlt_askForJoinAllyMember" )
		player.endGossip( talkEntity )
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		if not player.hasAllyRelation():
			player.statusMessage( csstatus.CANNOT_ADD_MEMBER_NO_ALLY )
			#DEBUG_MSG( "您没有结拜，怎么添加新兄弟？我很忙的，不要玩我啊！" )
			return
		player.client.rlt_askForJoinAllyMember()
		
class FuncAllyChangeTitle( Function ):
	"""
	更改结拜称号
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		对话选项有效性检查
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		触发对话选项要做的事情
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		#DEBUG_MSG( "-->>FuncAllyChangeTitle" )
		player.endGossip( talkEntity )
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		# 判断是否所有的兄弟都在，判断是否有钱
		if not player.isInTeam():
			player.statusMessage( csstatus.CANNOT_CHANGE_TITLE_NO_TEAM )
			#DEBUG_MSG( "想要更改结拜称号必须和你的兄弟们组成一队，一起来完成。" )
			return
		if not player.hasAllyRelation():
			player.statusMessage( csstatus.CANNOT_CHANGE_TITLE_NO_ALLY )
			#DEBUG_MSG( "您没有结拜，怎么改称号？我很忙的，不要玩我啊！" )
			return
		if not player.isTeamCaptain():
			player.statusMessage( csstatus.CANNOT_ALLY_NO_TEAM_CAPTAIN )
			#DEBUG_MSG( "让队长来和我说吧，你们这样一群人一起来，太混乱了！" )
			return
		if player.money < csconst.ALLY_CHANGE_TITLE_COST:
			player.statusMessage( csstatus.CANNOT_CHANGE_TITLE_NO_MONEY, csconst.ALLY_CHANGE_TITLE_COST/10000 )
			#DEBUG_MSG( "办手续是要交费的！请准备好5金再来改名！" )
			return
		tammateList = talkEntity.searchTeamMember( player.teamMailbox.id, csconst.RELATION_ALLY_SWEAR_DISTANCE )
		if len( player.allyPlayers ) > len( tammateList ):
			player.statusMessage( csstatus.CANNOT_ADD_NEW_LACK_MEMBER )
			#DEBUG_MSG( "是不是有兄弟没来啊，让他赶快过来。" )
			return
		if len( player.allyPlayers ) + 1 < len( tammateList ):
			player.statusMessage( csstatus.ALLY_CANNOT_WRONG_PLAYER )
			#DEBUG_MSG( "队伍里怎么有不相干的人？" )
			return
		tempDBIDList = [item["playerDBID"] for item in player.allyPlayers]
		tempDBIDList.append( player.databaseID )
		if set( [entity.databaseID for entity in tammateList] ) != set( tempDBIDList ):
			player.statusMessage( csstatus.ALLY_CANNOT_WRONG_PLAYER )
			#DEBUG_MSG( "队伍里怎么有不相干的人？" )
			return
		player.client.rlt_askForChangeAllyTitle()
		
		
class FuncQuitAlly( Function ):
	"""
	恩断义绝，玩家退出结拜
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		对话选项有效性检查
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		触发对话选项要做的事情
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		player.endGossip( talkEntity )
		if not player.hasAllyRelation():
			player.statusMessage( csstatus.CANNOT_QUIT_NO_ALLY )
			#DEBUG_MSG( "您没有结拜，何来退出？我很忙的，不要玩我啊！" )
			return
		player.client.rlt_askForQuitAlly()
		
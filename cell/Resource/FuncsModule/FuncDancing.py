# -*- coding: gb18030 -*-

from bwdebug import *
from Function import Function
import csconst
import csstatus


class FuncDancePractice( Function ):
	"""
	练习斗舞
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
		if not player.queryTemp("danceType"):
			return True
		return False
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		触发对话选项要做的事情
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		#DEBUG_MSG( "-->>rlt_askForStartAlly" )
		chellengeIndex = player.queryTemp("challengeIndex", 0)
		talkEntity.startDancePractice(chellengeIndex)
		player.endGossip( talkEntity )
		
class FuncDanceChallenge( Function ):
	"""
	挑战斗舞
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
		if player.queryTemp("danceType"):
			return True
		return False
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		触发对话选项要做的事情
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		#DEBUG_MSG( "-->>rlt_askForStartAlly" )
		chellengeIndex = player.queryTemp("challengeIndex", 0)
		if not chellengeIndex :
			ERRO_MSG("can't find challengeIndex in role %s"%player.playerName)
		talkEntity.startDanceChallenge(chellengeIndex)
		player.endGossip( talkEntity )

class FuncPlayAction( Function ):
	"""
	播放动作，param1为播放动作技能ID，param2为要说的话(为空时，只播放动作，不说话)，说话是以头顶气泡形式和在聊天框中显示的
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.param1 = section['param1'].asInt  #技能ID（此技能让自己播放动作）
		self.param2 = section['param2'].asString  #要说的话
		
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
		DEBUG_MSG( "DanceNPC dance and say!" )
		if self.param2:
			talkEntity.say(self.param2)
		talkEntity.planesOtherClients( "playAction", (self.param1,) )
		DEBUG_MSG( "DanceNPC dance and say over!" )
		player.endGossip( talkEntity )
		
class FuncQueryDanceExp(Function):
	"""
	查询当前获得的舞厅或舞王经验
	"""
	def __init__( self, section ):
		Function.__init__( self, section )
		self.param1 = section['param1'].asInt  #0表示舞厅中普通经验，1为舞王经验
		
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
		BigWorld.globalData["DanceMgr"].queryDanceExp(player.playerName, player.base , self.param1, player.level)
		player.endGossip( talkEntity )
		
class FuncGetDanceExp(Function):
	"""
	查询当前获得的舞厅或舞王经验
	"""
	def __init__( self, section ):
		Function.__init__( self, section )
		self.param1 = section['param1'].asInt   #0表示舞厅中普通经验，1为舞王经验
		
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
		BigWorld.globalData["DanceMgr"].getDanceExp(player.playerName, player.base , self.param1, player.level)
		player.endGossip( talkEntity )	
# -*- coding: gb18030 -*-


import time
import BigWorld
from Function import Function
import csdefine
import csstatus

TEAM_MEMBER_NEED 	= 3																	#需要的队伍成员
MAX_LEVEL 			= 110																#最大等级

class FuncKuafuRemain( Function ):
	"""
	进入夸父神殿
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.level = section.readInt( "param1" )										#进入等级
		self.recordKey = "kuafu_record"
		self.spaceName = "fu_ben_kua_fu_shen_dian"
		self.questID = section.readInt( "param2" )										#任务ID


	def do( self, player, talkEntity = None ):
		"""
		进入夸父神殿规则。
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
		
		if self.level > player.level:
			#玩家等级不够
			player.statusMessage( csstatus.KUA_FU_REMAIN_LEVEL_NOT_ARRIVE, self.level )
			return
			
		#if not player.hasPersistentFlag( csdefine.ENTITY_FLAG_KUA_FU_QUEST ):
			#没有相关任务。
			#player.statusMessage( csstatus.KUA_FU_REMAIN_QUEST_NOT_HAS, player.playerName )
			#return

		if not player.isInTeam():
			#玩家没有组队
			player.statusMessage( csstatus.KUA_FU_REMAIN_NEED_TEAM )
			return

		if BigWorld.globalData.has_key( 'KuafuRemain_%i'%player.getTeamMailbox().id ):
			if player.isActivityCanNotJoin( csdefine.ACTIVITY_KUA_FU )  and player.query( "lastKuafuRemainTeamID", 0 ) != player.getTeamMailbox().id:
				player.statusMessage( csstatus.KUA_FU_REMAIN_HAS_ENTERED_TODAY, player.playerName )
				return
			player.gotoSpace(self.spaceName, (60.049, 24.756, 150.834), (0,0,0))
		else:
			#队伍没有副本，则走创建流程
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return
			pList = player.getAllMemberInRange( 30 )
			
			if not len( pList ) >= 3 :
				player.statusMessage( csstatus.KUA_FU_REMAIN_ROLE_IS_ENOUGH_MEMBER )
				return

			for i in pList:
				if i.level < self.level:
					player.statusMessage( csstatus.KUA_FU_REMAIN_MEMBER_LEVEL_NOT_ARRIVE, i.playerName )
					return
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_KUA_FU ) :
					player.statusMessage( csstatus.KUA_FU_REMAIN_HAS_ENTERED_TODAY, i.playerName )
					return
				#if not i.hasPersistentFlag( csdefine.ENTITY_FLAG_KUA_FU_QUEST ):
					#没有相关任务
					#player.statusMessage( csstatus.KUA_FU_REMAIN_QUEST_NOT_HAS, i.playerName )
					#return

			pList.remove( player )
			player.gotoSpace(self.spaceName, (60.049, 24.756, 150.834), (0,0,0))
			player.set( "lastKuafuRemainTeamID", player.getTeamMailbox().id )
			for i in pList:
				i.set( "lastKuafuRemainTeamID", player.getTeamMailbox().id )
				i.gotoSpace(self.spaceName, (60.049, 24.756, 150.834), (0,0,0))

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
		return True




class FuncKuafuBossTalk( Function ):
	"""
	后卿对话
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass


	def do( self, player, talkEntity = None ):
		"""
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		
		talkEntity.setNextRunAILevel( 0 )
		talkEntity.removeFlag( csdefine.ENTITY_FLAG_SPEAKER )


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
		return True


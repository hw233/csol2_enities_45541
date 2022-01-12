# -*- coding: gb18030 -*-

# 方案一脚本

import time
import Math
import random
import csdefine
import csstatus
import cschannel_msgs
import ECBExtend
from bwdebug import *
from CopyContent import NEXT_CONTENT
from CopyContent import CopyContent
from CopyContent import CCKickPlayersProcess

from SpaceCopyTeamTemplate import SpaceCopyTeamTemplate

START_TIMER = 111
CHANGE_PK_MODEL_TIMER = 222

STATE_SKILL = 860021001			# 战斗状态技能ID

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_JUMP

class CCPrepareProcess( CopyContent ):
	"""
	30秒准备时间
	"""
	def __init__( self ):
		self.key = "prepareProcess"
		self.val = 1
	
	def onContent( self, spaceEntity ):
		"""
		内容执行
		"""
		spaceEntity.addTimer( 40, 0, NEXT_CONTENT )
		spaceEntity.setTemp( "beforeStartWar", True )
		
class CCWarProcess( CopyContent ):
	"""
	对局阶段（三个小局）
	"""
	def __init__( self ):
		self.key = "warProcess"
		self.val = 1
		
	def onContent( self, spaceEntity ):
		teamIDs = spaceEntity.queryTemp( "teamIDs", ( 0, 0 ) )
		if len( spaceEntity._players ) == 0:			# 没人进来就结束副本
			spaceEntity.base.allWarOver( teamIDs[0], teamIDs[1], False )
			return
		
		dbids = []
		findLeftPlayer = False
		findRightPlayer = False
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", ([],[]) )
		
		for e in spaceEntity._players:
			player = BigWorld.entities.get( e.id )
			if player:
				dbids.append( player.databaseID )
				if player.teamMailbox.id == teamIDs[0]:
					findLeftPlayer = True
				elif player.teamMailbox.id == teamIDs[1]:
					findRightPlayer = True
		
		# 看看是不是有一个队伍没人进来
		if not findLeftPlayer:																		# 找不到左队玩家，右队直接获胜
			spaceEntity.base.allWarOver( teamIDs[0], teamIDs[1], True )
			return
		if not findRightPlayer:																		# 找不到右队玩家，左队直接获胜
			spaceEntity.base.allWarOver( teamIDs[1], teamIDs[0], True )
			return
		
		# 看看是不是首局的玩家没有进来
		for dbid in currentFightPlayer[0]:
			if dbid not in dbids:
				spaceEntity.base.onPlayerLeave( dbid )
		for dbid in currentFightPlayer[1]:
			if dbid not in dbids:
				spaceEntity.base.onPlayerLeave( dbid )
		
		spaceEntity.addTimer( 3, 0, START_TIMER )
	
	def startWar( self, spaceEntity ):
		"""
		正式开战
		"""
		spaceEntity.removeTemp( "beforeStartWar" )
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", ([],[]) )
		
		fightPlayers = []
		for i in currentFightPlayer[0]:
			fightPlayers.append( i )
		for i in currentFightPlayer[1]:
			fightPlayers.append( i )
			
		for e in spaceEntity._players:
			player = BigWorld.entities.get( e.id )
			if player:
				if player.databaseID in fightPlayers:
					player.client.turnWar_showPrepareTime( 3 )
		
		spaceEntity.addTimer( 3, 0, CHANGE_PK_MODEL_TIMER )		# 一段时间后改变PK模式为组队模式
		
	def telportPlayer( self, spaceEntity, playerDBID, position ):
		"""
		传送玩家到出战点
		"""
		player = self.findPlayerByDBID( spaceEntity, playerDBID )
		if player:
			player.changePosAndDir( position, Math.Vector3( spaceEntity.getScript().centerPoint ) )
			if spaceEntity.queryTemp( "beforeStartWar", False ) and not player.popTemp( "isFixed"):		# 还未开始对战
				player.actCounterInc( STATES )
				player.setTemp( "isFixed", True )
			else:
				player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TEAMMATE )
				player.setTemp( "turnWar_isFightPlayer", True )
				player.spellTarget( STATE_SKILL, player.id )
		else:
			spaceEntity.base.onPlayerLeave( playerDBID )
		
	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		内容期间，角色离开
		"""
		# 离开副本，对方队伍获胜
		losePlayer = BigWorld.entities.get( baseMailbox.id )
		if not losePlayer:
			return
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", ([],[]) )
		if params["databaseID"] in currentFightPlayer[0] or params["databaseID"] in currentFightPlayer[1]:				# 正在对局的玩家离开
			spaceEntity.base.onPlayerLeave( params["databaseID"] )
		
	def onTimer( self, spaceEntity, id, userArg ):
		if userArg == START_TIMER:
			self.startWar( spaceEntity )
		elif userArg == CHANGE_PK_MODEL_TIMER:
			for e in spaceEntity._players:
				player = BigWorld.entities.get( e.id )
				if player:
					if player.popTemp( "isFixed" ):
						player.actCounterDec( STATES )			# 移除定身
					currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", ([],[]) )
					if player.databaseID in currentFightPlayer[0] or player.databaseID in currentFightPlayer[1]:
						player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TEAMMATE )
						if not player.queryTemp( "turnWar_isFightPlayer", False ):						# 新上场的玩家要加战斗状态buff
							player.setTemp( "turnWar_isFightPlayer", True )
							player.spellTarget( STATE_SKILL, player.id )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )
	
	def findPlayerByDBID( self, spaceEntity, dbID ):
		"""
		根据dbid找副本玩家
		"""
		for e in spaceEntity._players:
			player = BigWorld.entities.get( e.id )
			if not player:
				continue
			if player.databaseID == dbID:
				return player
		return None
			
	def onActivityOver( self, spaceEntity ):
		"""
		活动时间结束
		"""
		player1 = None
		player2 = None
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", ([],[]) )
		for e in spaceEntity._players:
			player = BigWorld.entities.get(e.id)
			if not player:
				return
			if player.databaseID in currentFightPlayer[0]:
				player1 = player
			elif player.databaseID in currentFightPlayer[1]:
				player2 = player
		
		if player1 and player2:
			if player1.HP > player2.HP:
				spaceEntity.base.resultOnActivityOver( player2.teamMailbox.id, player1.teamMailbox.id )
			elif player1.HP < player2.HP:
				spaceEntity.base.resultOnActivityOver( player1.teamMailbox.id, player2.teamMailbox.id )
			else:			# 平局
				spaceEntity.base.resultOnActivityOver( None, None )
		else:
			spaceEntity.getScript().onConditionChange( spaceEntity, {} )
		
class CCShowRestTime( CopyContent ):
	"""
	显示10秒钟倒计时
	"""
	def __init__( self ):
		self.key = "showRestTime"
		self.val = 1
		
	def onContent( self, spaceEntity ):
		spaceEntity.addTimer( 10, 0, NEXT_CONTENT )
		for e in spaceEntity._players:
			e.client.turnWar_showTelportTime( 10 )
	
class SpaceCopyTongTurnWar_FS( SpaceCopyTeamTemplate ):
	"""
	帮会车轮战空间
	"""
	def __init__( self ):
		SpaceCopyTeamTemplate.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True
		
	def load( self, section ):
		"""
		从配置中加载数据

		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopyTeamTemplate.load( self, section )
		
		spaceData = section[ "Space" ]
		# 队伍1出场位置
		self.left_watchPoint = eval( spaceData[ "leftTeam_watchPoint" ].asString )
		#self.left_watchDirection = tuple( [ float(x) for x in spaceData[ "leftTeam_watchPoint" ]["position"].asString.split() ] )
		self.left_fightPoint = eval( spaceData[ "leftTeam_fightPoint" ].asString )
		
		# 队伍2出场位置
		self.right_watchPoint = eval( spaceData[ "rightTeam_watchPoint" ].asString )
		self.right_fightPoint = eval( spaceData[ "rightTeam_fightPoint" ].asString )
		
		# 战败观战区
		self.loser_watchPoint = eval( spaceData[ "loser_watchPoint" ].asString )
		self.centerPoint = eval( spaceData[ "centerPoint" ].asString )
		
	def initContent( self ):
		"""
		"""
		self.contents.append( CCPrepareProcess() )
		self.contents.append( CCWarProcess() )
		self.contents.append( CCShowRestTime() )
		self.contents.append( CCKickPlayersProcess() )
		
	def packedDomainData( self, player ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		return { "teamID" : player.teamMailbox.id, "databaseID": player.databaseID ,"spaceKey": player.teamMailbox.id}
	
	def packedSpaceDataOnEnter( self, player ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		dict = SpaceCopyTeamTemplate.packedSpaceDataOnEnter( self, player )
		if player.teamMailbox:
			dict["teamID"] = player.teamMailbox.id
		return dict
		
	def packedSpaceDataOnLeave( self, player ):
		"""
		"""
		packDict = SpaceCopyTeamTemplate.packedSpaceDataOnLeave( self, player )
		packDict[ "isWatchState" ] = player.effect_state & csdefine.EFFECT_STATE_DEAD_WATCHER
		packDict["databaseID"] = player.databaseID
		return packDict
	
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopyTeamTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		player = BigWorld.entities.get( baseMailbox.id )
		if player:
			player.reduce_role_damage_extra += 6000
			player.calcReduceRoleDamage()
			player.HP_Max *= 2							# 血量上限翻倍
			player.addHP( player.HP_Max - player.HP )
			player.addHP( player.MP_Max - player.MP )
			
			player.setTemp( "forbid_revert_hp", False)
			player.lockPkMode()
			player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )
			player.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )		# 加免战
		
			currentFightPlayer = selfEntity.queryTemp( "currentFightPlayer", ([],[]) )
			if player.databaseID in selfEntity.queryTemp( "losedPlayer", [] ):			# 已战败，传到战败观战区
				player.changePosAndDir( Math.Vector3( self.loser_watchPoint ), Math.Vector3( self.centerPoint ) )
			elif player.databaseID in currentFightPlayer[0] or player.databaseID in currentFightPlayer[1]:								# 如果是当前对阵玩家
				player.changePosAndDir( self.randomPosition( player ), Math.Vector3( self.centerPoint ) )			# 随机散开，避免开始的时候堆在一起
				player.setTemp( "turnWar_isFightPlayer", True )
				player.spellTarget( STATE_SKILL, player.id )							# 加战斗状态的Buff，与上一句不能交换顺序，否则可能buff会马上移除
				if selfEntity.queryTemp( "beforeStartWar", False ) and not player.popTemp( "isFixed"):
					player.actCounterInc( STATES )											# 添加定身
					player.setTemp( "isFixed", True )
			else:																		# 否则传到等待区
				teamIDs = selfEntity.queryTemp( "teamIDs", ( 0, 0 ) )
				if params["teamID"] == teamIDs[0]:																	# 自己属于左队传到左观战点
					player.changePosAndDir( Math.Vector3( self.left_watchPoint ), Math.Vector3( self.centerPoint ) )
				else:																								# 自己属于右队传到右观战点
					player.changePosAndDir( Math.Vector3( self.right_watchPoint ), Math.Vector3( self.centerPoint ) )
	
	def randomPosition( self, player ):
		"""
		
		"""
		pos = Math.Vector3( player.position )
		pos.x = player.position.x  +  random.random() * random.randint( -3, 3 )
		pos.z = player.position.z  +  random.random() * random.randint( -3, 3 )
		collide = BigWorld.collide( player.spaceID, ( pos.x, pos.y + 10, pos.z ), ( pos.x, pos.y - 10, pos.z ) )
		if collide != None:
			pos.y = collide[0].y
		return pos
		
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		isWatchState = params[ "isWatchState" ]
		if isWatchState:
			baseMailbox.cell.onLeaveWatchMode()
		
		player = BigWorld.entities.get( baseMailbox.id )
		if player:
			player.reduce_role_damage_extra -= 6000
			player.calcReduceRoleDamage()
			player.calcHPMax()
			
			player.unLockPkMode()
			player.setSysPKMode( 0 )
			player.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )			# 减免战
			player.removeTemp( "turnWar_isFightPlayer" )
			player.removeTemp( "forbid_revert_hp" )
			currentFightPlayer = selfEntity.queryTemp( "currentFightPlayer", ([],[]) )
			if player.popTemp( "isFixed"):
				player.actCounterDec( STATES )			# 移除定身
		SpaceCopyTeamTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
		
	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
		role.addTimer( 3, 0, ECBExtend.ROLE_REVIVE_TIMER )
		role.getCurrentSpaceBase().onPlayerWin( role.databaseID, role.teamMailbox.id, role.base, killer.databaseID )
		
	def allWarOver( self, spaceEntity ):
		"""
		所有对局结束
		"""
		currentContent = self.getCurrentContent( spaceEntity )
		if currentContent.key == "warProcess":
			self.onConditionChange( spaceEntity, {} )
	
	def onActivityOver( self, spaceEntity ):
		currentContent = self.getCurrentContent( spaceEntity )
		if currentContent.key == "warProcess":
			currentContent.onActivityOver( spaceEntity )
			
	def telportPlayer( self, spaceEntity, playerDBID, position ):
		"""
		传送玩家到出战点
		"""
		currentContent = self.getCurrentContent( spaceEntity )
		if currentContent.key == "warProcess":
			currentContent.telportPlayer( spaceEntity, playerDBID, position )
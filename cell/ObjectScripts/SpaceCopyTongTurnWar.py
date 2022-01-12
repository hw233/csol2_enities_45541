# -*- coding: gb18030 -*-

import time
import Math
import csdefine
import csstatus
import cschannel_msgs
import ECBExtend
from bwdebug import *
from CopyContent import NEXT_CONTENT
from CopyContent import CopyContent
from CopyContent import CCKickPlayersProcess

from SpaceCopyTemplate import SpaceCopyTemplate

PROCESS_OVER_TIMER = 111
CHANGE_PK_MODEL_TIMER = 222
SKILL_ID = 860020001		# 定身技能ID
STATE_SKILL = 860021001			# 战斗状态技能ID

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
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", (0,0) )
		
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
		if currentFightPlayer[0] not in dbids:
			spaceEntity.base.onPlayerLeave( currentFightPlayer[0] )
			return
		if currentFightPlayer[1] not in dbids:
			spaceEntity.base.onPlayerLeave( currentFightPlayer[1] )
			return
			
		for e in spaceEntity._players:
			player = BigWorld.entities.get( e.id )
			if player:
				if player.databaseID in currentFightPlayer:
					player.client.turnWar_showPrepareTime( 3 )
					player.spellTarget( SKILL_ID, player.id )
		
		spaceEntity.addTimer( 3, 0, CHANGE_PK_MODEL_TIMER )		# 一段时间后改变PK模式为组队模式
			
		spaceEntity.setTemp( "processOverTimer", spaceEntity.addTimer( 3 * 60, 0, PROCESS_OVER_TIMER ) )
		
	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		内容期间，角色离开
		"""
		# 离开副本，对方队伍获胜
		losePlayer = BigWorld.entities.get( baseMailbox.id )
		if not losePlayer:
			return
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", (0,0) )
		if params["databaseID"] in currentFightPlayer:				# 正在对局的玩家离开
			teamIDs = spaceEntity.queryTemp( "teamIDs", ( 0, 0 ) )
			if params["databaseID"] == currentFightPlayer[0]:
				teamID = teamIDs[0]
				anotherPlayer = self.findPlayerByDBID( spaceEntity, currentFightPlayer[1] )
				if anotherPlayer:
					spaceEntity.revert_HpMp( anotherPlayer )
			else:
				teamID = teamIDs[1]
				anotherPlayer = self.findPlayerByDBID( spaceEntity, currentFightPlayer[0] )
				if anotherPlayer:
					spaceEntity.revert_HpMp( anotherPlayer )
					
			spaceEntity.base.onPlayerLeave( params["databaseID"] )
			self.oneWarOver( spaceEntity )
		
	def onTimer( self, spaceEntity, id, userArg ):
		if userArg == PROCESS_OVER_TIMER:
			self.onWarTimeOver( spaceEntity )
		if userArg == CHANGE_PK_MODEL_TIMER:
			for e in spaceEntity._players:
				player = BigWorld.entities.get( e.id )
				if player:
					currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", (0,0) )
					if player.databaseID in currentFightPlayer:
						player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TEAMMATE )
						if not player.queryTemp( "turnWar_isFightPlayer", False ):						# 新上场的玩家要加战斗状态buff
							player.setTemp( "turnWar_isFightPlayer", True )
							player.spellTarget( STATE_SKILL, player.id )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )
		
	def onWarTimeOver( self, spaceEntity ):
		"""
		一局时间到
		"""
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", (0,0) )
		player1 = self.findPlayerByDBID( spaceEntity, currentFightPlayer[0] )
		player2 = self.findPlayerByDBID( spaceEntity, currentFightPlayer[1] )
		if not player1 or not player2:
			ERROR_MSG( "SpaceTongTurnWar(%i) can't find player when one war time over!"%spaceEntity.id )
			return
		if player1.HP > player2.HP:
			spaceEntity.base.onPlayerWin( player2.databaseID, player2.teamMailbox.id, player2.base )
			spaceEntity.revert_HpMp( player1 )
		elif player1.HP < player2.HP:
			spaceEntity.base.onPlayerWin( player1.databaseID, player1.teamMailbox.id, player1.base )
			spaceEntity.revert_HpMp( player2 )
		else:			# 平局
			spaceEntity.base.onBothPlayerLoseOrLeave( True, [ player1.base, player2.base ] )
		
		self.oneWarOver( spaceEntity )
	
	def startNextWar( self, spaceEntity ):
		"""
		开始新一轮对局
		"""
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", (0,0) )
		leftPlayer = self.findPlayerByDBID( spaceEntity, currentFightPlayer[0] )
		rightPlayer = self.findPlayerByDBID( spaceEntity, currentFightPlayer[1] )
		
		# 一大串的判断，为了保证两个对战玩家都在副本内
		if not leftPlayer and not rightPlayer:
			spaceEntity.base.onBothPlayerLoseOrLeave( False, [] )
			return
		elif not leftPlayer:
			spaceEntity.base.onPlayerLeave( currentFightPlayer[0] )
			return
		elif not rightPlayer:
			spaceEntity.base.onPlayerLeave( currentFightPlayer[1] )
			return
		
		leftPlayer.changePosition( Math.Vector3( spaceEntity.getScript().left_fightPoint ) )	# 变化位置到左出战点
		leftPlayer.client.turnWar_showPrepareTime( 3 )
		leftPlayer.spellTarget( SKILL_ID, leftPlayer.id )
		
		rightPlayer.changePosition( Math.Vector3( spaceEntity.getScript().right_fightPoint ) ) 	# 变化位置到右出战点
		rightPlayer.client.turnWar_showPrepareTime( 3 )
		rightPlayer.spellTarget( SKILL_ID, rightPlayer.id )
		
		spaceEntity.setTemp( "processOverTimer", spaceEntity.addTimer( 3 * 60, 0, PROCESS_OVER_TIMER ) )
		spaceEntity.addTimer( 3, 0, CHANGE_PK_MODEL_TIMER )		# 一段时间后改变PK模式为组队模式
	
	def findPlayerByDBID( self, spaceEntity, dbID ):
		"""
		根据dbid找副本玩家
		"""
		for e in spaceEntity._players:
			player = BigWorld.entities.get( e.id )
			if not player:
				return None
			if player.databaseID == dbID:
				return player
		return None
			
	def onActivityOver( self, spaceEntity ):
		"""
		活动时间结束
		"""
		player1 = None
		player2 = None
		currentFightPlayer = spaceEntity.queryTemp( "currentFightPlayer", (0,0) )
		for e in spaceEntity._players:
			player = BigWorld.entities.get(e.id)
			if not player:
				return
			if player.databaseID == currentFightPlayer[0]:
				player1 = player
			elif player.databaseID == currentFightPlayer[1]:
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
	
	def endContent( self, spaceEntity ):
		if spaceEntity.queryTemp( "processOverTimer", None):
			spaceEntity.cancel( spaceEntity.popTemp( "processOverTimer") )
		CopyContent.endContent( self, spaceEntity )
	
	def oneWarOver( self, spaceEntity ):
		if spaceEntity.queryTemp( "processOverTimer", None):
			spaceEntity.cancel( spaceEntity.popTemp( "processOverTimer") )
		
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
	
class SpaceCopyTongTurnWar( SpaceCopyTemplate ):
	"""
	帮会车轮战空间
	"""
	def __init__( self ):
		SpaceCopyTemplate.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True
		
	def load( self, section ):
		"""
		从配置中加载数据

		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopyTemplate.load( self, section )
		
		spaceData = section[ "Space" ]
		# 队伍1出场位置
		self.left_watchPoint = tuple( [ float(x) for x in spaceData[ "leftTeam_watchPoint" ].asString.split() ] )
		self.left_fightPoint = tuple( [ float(x) for x in spaceData[ "leftTeam_fightPoint" ].asString.split() ] )
		
		# 队伍2出场位置
		self.right_watchPoint = tuple( [ float(x) for x in spaceData[ "rightTeam_watchPoint" ].asString.split() ] )
		self.right_fightPoint = tuple( [ float(x) for x in spaceData[ "rightTeam_fightPoint" ].asString.split() ] )
		
		# 战败观战区
		self.loser_watchPoint = tuple( [ float(x) for x in spaceData[ "loser_watchPoint" ].asString.split() ] )
		
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
		return { "teamID" : player.teamMailbox.id, "databaseID": player.databaseID, "spaceKey" : player.teamMailbox.id }
	
	def packedSpaceDataOnEnter( self, player ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		dict = SpaceCopyTemplate.packedSpaceDataOnEnter( self, player )
		if player.teamMailbox:
			dict["teamID"] = player.teamMailbox.id
		return dict
		
	def packedSpaceDataOnLeave( self, player ):
		"""
		"""
		packDict = SpaceCopyTemplate.packedSpaceDataOnLeave( self, player )
		packDict[ "isWatchState" ] = player.effect_state & csdefine.EFFECT_STATE_DEAD_WATCHER
		packDict["databaseID"] = player.databaseID
		return packDict
	
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )
		player = BigWorld.entities.get( baseMailbox.id )
		if player:
			player.setTemp( "forbid_revert_hp", False)
			player.setTemp( "forbid_revert_mp", False)
			player.lockPkMode()
			player.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )
			player.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )		# 加免战
		
			currentFightPlayer = selfEntity.queryTemp( "currentFightPlayer", (0,0) )
			if player.databaseID in selfEntity.queryTemp( "losedPlayer", [] ):			# 已战败，传到战败观战区
				player.changePosition( Math.Vector3( self.loser_watchPoint ) )
			elif player.databaseID in currentFightPlayer:								# 如果是当前对阵玩家，不管
				player.setTemp( "turnWar_isFightPlayer", True )
				player.spellTarget( STATE_SKILL, player.id )							# 加战斗状态的Buff，与上一句不能交换顺序，否则可能buff会马上移除
			else:																		# 否则传到等待区
				teamIDs = selfEntity.queryTemp( "teamIDs", ( 0, 0 ) )
				if params["teamID"] == teamIDs[0]:																	# 自己属于左队传到左观战点
					player.changePosition( Math.Vector3( self.left_watchPoint ) )
				else:																								# 自己属于右队传到右观战点
					player.changePosition( Math.Vector3( self.right_watchPoint ) )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		isWatchState = params[ "isWatchState" ]
		if isWatchState:
			baseMailbox.cell.onLeaveWatchMode()
		
		player = BigWorld.entities.get( baseMailbox.id )
		if player:
			player.unLockPkMode()
			player.setSysPKMode( 0 )
			player.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )			# 减免战
			player.removeTemp( "turnWar_isFightPlayer" )
			player.removeTemp( "forbid_revert_hp" )
			player.removeTemp( "forbid_revert_mp" )
		SpaceCopyTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )
		
	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
		role.addTimer( 3, 0, ECBExtend.ROLE_REVIVE_TIMER )
		role.getCurrentSpaceBase().onPlayerWin( role.databaseID, role.teamMailbox.id, role.base )
		
		spaceEntity = BigWorld.entities.get( role.getCurrentSpaceBase().id )
		if spaceEntity:
			spaceEntity.revert_HpMp( killer )
			currentContent = self.getCurrentContent( spaceEntity )
			if currentContent.key == "warProcess":
				currentContent.oneWarOver( spaceEntity )
	
	def startNextWar( self, spaceEntity ):
		"""
		开始下一对局
		"""
		currentContent = self.getCurrentContent( spaceEntity )
		currentContent.startNextWar( spaceEntity )
		
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
			
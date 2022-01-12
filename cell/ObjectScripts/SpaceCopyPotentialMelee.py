# -*- coding: gb18030 -*-

import BigWorld
import cschannel_msgs
import csstatus
import csdefine
import random
import csconst
import Const
import ECBExtend
import time
from bwdebug import *
from SpaceCopyTeam import SpaceCopyTeam
from Resource.CopyPotentialMeleeLoader import CopyPotentialMeleeLoader
from Resource.CopyPotentialMeleeLoader import BOSS_CLASS_NAME
g_config = CopyPotentialMeleeLoader.instance()

TIMER_SPACE_LIfE		= 40 * 60
TIMER_SPAWN_NEXT		= 30
TIMER_SPAWN_START		= 10

TIMER_ARG_NEXT_CONTENT		= 1
TIMER_ARG_CLOSE_SPACE		= 2


class SpaceCopyPotentialMelee( SpaceCopyTeam ):
	"""
	注：此脚本只能用于匹配SpaceDomainCopy、SpaceCopy或继承于其的类。
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyTeam.__init__( self )
		
	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopyTeam.load( self, section )
		point = section[ "Space" ][ "BossPoint" ]
		self.bossPoint = ( eval( point["pos"].asString ), eval( point["direction"].asString ), eval( point["randomWalkRange"].asString ) )

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		用我自己的数据初始化参数 selfEntity 的数据
		"""
		SpaceCopyTeam.initEntity( self, selfEntity )
		selfEntity.addTimer( TIMER_SPACE_LIfE, 0, TIMER_ARG_CLOSE_SPACE )
		selfEntity.setTemp( "copyStartTime", time.time() )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, TIMER_SPACE_LIfE )

	def onOneTypeMonsterDie( self, selfEntity, monsterID, monsterClassName ):
		"""
		怪物通知其所在副本自己挂了，根据怪物的className处理不同怪物死亡
		"""
		if monsterClassName not in BOSS_CLASS_NAME:
			selfEntity.liveMonsterNum -= 1
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, selfEntity.liveMonsterNum )
		else:
			selfEntity.liveBossNum -= 1
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, selfEntity.liveBossNum  )
		
		selfEntity.checkDoPass()
				
	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == TIMER_ARG_CLOSE_SPACE:
			self.onOverMelee( selfEntity, True )
		
		elif userArg == TIMER_ARG_NEXT_CONTENT:
			if selfEntity.isLastBatch():
				return
				
			selfEntity.startNextBatch()
		else:
			SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )
	
	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		if entity.isTeamCaptain():
			packDict[ "teamLevel" ] = entity.level
			
		return packDict
						
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		if params.has_key( "teamLevel" ):
			BigWorld.globalData['potentialMelee_%i' % selfEntity.params['dbID'] ] = True
			selfEntity.setTemp('globalkey','potentialMelee_%i' % selfEntity.params['dbID'] )
			
			selfEntity.base.spawnFlagEntity( { "level": params[ "teamLevel" ] } ) # 刷旗子
			selfEntity.teamLevel = params[ "teamLevel" ]
			selfEntity.addTimer( TIMER_SPAWN_START, 0, TIMER_ARG_NEXT_CONTENT )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, g_config.getBatchTotal() )
			#BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_LEVEL_TIME, TIMER_SPAWN_START )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, g_config.getMonsterCount() )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, g_config.getBossCount() )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_POTENTIAL_FLAG_HP, 100 )
			baseMailbox.client.startCopyTime( TIMER_SPACE_LIfE- int( time.time() - selfEntity.queryTemp( "copyStartTime" ) ) )
			
	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		
	def statusMessageAllPlayer( self, selfEntity, msgKey, *args ):
		"""
		通知所有人 指定的信息
		"""
		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				p = BigWorld.entities[ e.id ]
				p.statusMessage( msgKey, *args )
			else:
				ERROR_MSG( "player %i not found" % e.id )

	def onLeaveTeam( self, playerEntity ):
		"""
		"""
		SpaceCopyTeam.onLeaveTeam( self, playerEntity )
		playerEntity.getCurrentSpaceBase().cell.setLeaveTeamPlayerMB( playerEntity.base )
	
	def passBatch( self, selfEntity ):
		"""
		通关
		"""
		if selfEntity.isLastBatch():
			self.onOverMelee( selfEntity, False )
		else:
			ntid = selfEntity.popTemp( "SPAWN_NEXT", 0 )
			if ntid:
				selfEntity.cancel( ntid )
				
		selfEntity.addTimer( 0, 0, TIMER_ARG_NEXT_CONTENT )

	def onFlagDie( self, selfEntity ):
		"""
		圣魂旗被摧毁
		"""
		selfEntity.addTimer( 10.0, 0, TIMER_ARG_CLOSE_SPACE )
		
	def onOverMelee( self, selfEntity, isTimeout ):
		"""
		活动结束
		"""
		if isTimeout:
			for e in selfEntity._players:
				if BigWorld.entities.has_key( e.id ):
					BigWorld.entities[ e.id ].gotoForetime()
				else:
					e.cell.gotoForetime()
			
			# 开始倒计时30秒关闭副本
			selfEntity.addTimer( 30, 0, Const.SPACE_TIMER_ARG_CLOSE  )
		else:
			#刷NPC 10111201	玄天武尊 npcm0208_1
			elist = []
			for e in selfEntity._players:
				player = BigWorld.entities.get( e.id )
				if player is not None and player.spaceID == selfEntity.spaceID:
					elist.append( player.databaseID )
			
			DEBUG_MSG( "can get rewardPlayers:%s" % elist )
			dict = { "tempMapping" : { "playerLevel": selfEntity.teamLevel, "rewardPlayers" : elist } }
			selfEntity.createNPCObject( "10111201", self.bossPoint[0], self.bossPoint[1], dict ) 
			self.statusMessageAllPlayer( selfEntity, csstatus.POTENTIAL_MELEE_ALERT_OVER )
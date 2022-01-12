# -*- coding: gb18030 -*-

# ------------------------------------------------
# from python
import time
# ------------------------------------------------
# from engine
import BigWorld
# ------------------------------------------------
# from common
import csdefine
import csstatus
import csconst
# ------------------------------------------------
# from locale_default
import cschannel_msgs
# ------------------------------------------------
# from cell
import Const
# ------------------------------------------------
# from current directory
from CopyTeamTemplate import CopyTeamTemplate

# ------------------------------------------------



class CopyFangShou( CopyTeamTemplate ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		CopyTeamTemplate.__init__( self )

	def onFangShouGearStarting( self, selfEntity, areaName ) :
		"""
		防守副本机关开启回调
		"""
		currentStage = self.getCurrentStage( selfEntity )
		params = {}
		params["areaName"] = areaName
		currentStage.doAllEvent( selfEntity, csdefine.COPY_EVENT_FANG_SHOU_ON_GEAR_STARTING, params )
	
	def onFangShouTowerCreate( self, selfEntity, currentArea, towerID ) :
		"""
		防守副本防御塔创建回调
		"""
		currentStage = self.getCurrentStage( selfEntity )
		params = {}
		params["currentArea"] = currentArea
		params["towerID"] = towerID
		currentStage.doAllEvent( selfEntity, csdefine.COPY_EVENT_FANG_SHOU_ON_TOWER_CREATE, params )
	
	def onFangShouNpcHPChanged( self, selfEntity, hp, hp_max ) :
		"""
		防守NPC血量改变回调
		"""
		currentStage = self.getCurrentStage( selfEntity )
		params = {}
		params["hp"] = hp
		params["hp_max"] = hp_max
		currentStage.doAllEvent( selfEntity, csdefine.COPY_EVENT_FANG_SHOU_ON_NPC_HP_CHANGED, params )
	
	def onTimer( self, selfEntity, timerID, userArg, params ) :
		"""
		"""
		if userArg == Const.SPACE_TIMER_ARG_FANG_SHOU_DELAY_SPAWN_MONSTER :		# 防守副本延迟 1 秒刷怪timer
			selfEntity.base.spawnMonsters( { "monsterType" : 3, "level": selfEntity.params["copyLevel"] } )
		CopyTeamTemplate.onTimer( self, selfEntity, timerID, userArg, params )
	
	def packedDomainData( self, player ):
		"""
		"""
		data = CopyTeamTemplate.packedDomainData( self, player )
		copyLevel = player.level
		if player.getTeamCaptain() :
			copyLevel = player.getTeamCaptain().level
		data["copyLevel"] = copyLevel

		return data

	def shownDetails( self ):
		"""
		shownDetails 副本内容显示规则：
		[ 
			0: 剩余时间
			1: 剩余小怪
			2: 剩余小怪批次
			3: 剩余BOSS
			4: 蒙蒙数量
			5: 剩余魔纹虎数量
			6: 剩余真鬼影狮数量
		]
		"""
		# 显示剩余小怪，剩余BOSS。 
		return [ 0, 1, 3, 21, 12, 22 ]
# -*- coding: gb18030 -*-

import csdefine
from bwdebug import *
from MonsterCityWarBase import MonsterCityWarBase

class MonsterCityWarBase_HeroMonu( MonsterCityWarBase ):
	"""
	英灵碑
	"""
	def __init__( self ):
		MonsterCityWarBase. __init__( self )
		self.baseType = csdefine.CITY_WAR_FINAL_BASE_HEROMONU		# 据点类型

	def onCreated( self, selfEntity ):
		"""	
		资源点创建
		"""
		if not selfEntity.belong:
			selfEntity.belong = csdefine.CITY_WAR_FINAL_FACTION_DEFEND	# 属于攻城方
		MonsterCityWarBase.onCreated( self, selfEntity )

	def onActivated( self, selfEntity ):
		"""
		被激活（移除不可被攻击标志位）
		"""
		selfEntity.removeFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE )

	def reset( self, selfEntity ):
		"""
		重置
		"""
		selfEntity.belong = csdefine.CITY_WAR_FINAL_FACTION_DEFEND

	def dieNotify( self, selfEntity, killerID ):
		"""
		死亡通知；当selfEntity的die()被触发时被调用
		"""
		MonsterCityWarBase.dieNotify( self, selfEntity, killerID )
		
		spaceBase = selfEntity.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: ( %s, %i ) can't find spaceBase!" % ( selfEntity.className, selfEntity.id ) )
			return
		spaceBase.cell.onHeroMonuDied( selfEntity.id, killerID )

	def onOccupied( self, selfEntity, belong ):
		"""
		被占领
		"""
		MonsterCityWarBase.onOccupied( self, selfEntity, belong )
		# 通知副本
		spaceBase = selfEntity.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: ( %s, %i ) can't find spaceBase!" % ( selfEntity.className, selfEntity.id ) )
			return
		spaceBase.cell.onHeroMonuOccupied( self.baseType, selfEntity.id, belong  )
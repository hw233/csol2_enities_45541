# -*- coding: gb18030 -*-

import BigWorld
import csdefine
from bwdebug import *
from MonsterCityWarBase import MonsterCityWarBase

class MonsterCityWarBase_FlagGuard( MonsterCityWarBase ):
	"""
	护旗将
	"""
	def __init__( self ):
		MonsterCityWarBase. __init__( self )
		self.baseType = csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD		# 据点类型

	def receiveDamage( self, selfEntity, killerID, skillID, damageType, damage ):
		"""
		接收到伤害
		"""
		if selfEntity.belong:		# 护旗无归属情况下，作伤害统计
			return
			
		spaceBase = selfEntity.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: ( %s, %i ) can't find spaceBase!" % ( selfEntity.className, selfEntity.id ) )
			return
		changeDamage = min( selfEntity.HP, damage )
		spaceBase.cell.recordFlagGuardDamage(  selfEntity.id, killerID, changeDamage )

	def dieNotify( self, selfEntity, killerID ):
		"""
		死亡通知；当selfEntity的die()被触发时被调用
		"""
		MonsterCityWarBase.dieNotify( self, selfEntity, killerID )
		
		spaceBase = selfEntity.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: ( %s, %i ) can't find spaceBase!" % ( selfEntity.className, selfEntity.id ) )
			return
		spaceBase.cell.onFlagGuardDied( selfEntity.id, selfEntity.integral, killerID )

	def reset( self, selfEntity ):
		"""
		重置
		"""
		selfEntity.destroy()
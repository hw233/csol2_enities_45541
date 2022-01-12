# -*- coding: gb18030 -*-

import csdefine
from bwdebug import *
from MonsterCityWarBase import MonsterCityWarBase

class MonsterCityWarBase_Battle( MonsterCityWarBase ):
	"""
	战斗据点
	"""
	def __init__( self ):
		MonsterCityWarBase. __init__( self )
		self.baseType = csdefine.CITY_WAR_FINAL_BASE_BATTLE		# 据点类型

	def onOccupied( self, selfEntity, belong ):
		"""
		被占领
		"""
		MonsterCityWarBase.onOccupied( self, selfEntity, belong )
		# 通知Space
		spaceBase = selfEntity.getCurrentSpaceBase()
		if spaceBase:
			spaceBase.cell.onBattleBaseOccupied( self.baseType, selfEntity.id, selfEntity.className, belong, selfEntity.getResourceBaseBelong( belong ) )
		
		# 添加Buff，消耗能量
		# 清空敌对方的能量
		for key, value in selfEntity.energy.iteritems():
			if key != belong:
				selfEntity.energy[ key ] = 0

	def reset( self, selfEntity ):
		"""
		重置( 同时需要通知资源点重置 )
		"""
		MonsterCityWarBase.reset( self, selfEntity )
		selfEntity.energy = {}
		resourceList = selfEntity.queryTemp( "resourceList", [] )
		for resourceMB in resourceList:
			resourceMB.cityWarBaseReset()
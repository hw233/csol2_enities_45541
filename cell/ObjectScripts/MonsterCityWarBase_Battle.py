# -*- coding: gb18030 -*-

import csdefine
from bwdebug import *
from MonsterCityWarBase import MonsterCityWarBase

class MonsterCityWarBase_Battle( MonsterCityWarBase ):
	"""
	ս���ݵ�
	"""
	def __init__( self ):
		MonsterCityWarBase. __init__( self )
		self.baseType = csdefine.CITY_WAR_FINAL_BASE_BATTLE		# �ݵ�����

	def onOccupied( self, selfEntity, belong ):
		"""
		��ռ��
		"""
		MonsterCityWarBase.onOccupied( self, selfEntity, belong )
		# ֪ͨSpace
		spaceBase = selfEntity.getCurrentSpaceBase()
		if spaceBase:
			spaceBase.cell.onBattleBaseOccupied( self.baseType, selfEntity.id, selfEntity.className, belong, selfEntity.getResourceBaseBelong( belong ) )
		
		# ���Buff����������
		# ��յжԷ�������
		for key, value in selfEntity.energy.iteritems():
			if key != belong:
				selfEntity.energy[ key ] = 0

	def reset( self, selfEntity ):
		"""
		����( ͬʱ��Ҫ֪ͨ��Դ������ )
		"""
		MonsterCityWarBase.reset( self, selfEntity )
		selfEntity.energy = {}
		resourceList = selfEntity.queryTemp( "resourceList", [] )
		for resourceMB in resourceList:
			resourceMB.cityWarBaseReset()
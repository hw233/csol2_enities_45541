# -*- coding: gb18030 -*-

import csdefine
from bwdebug import *
from MonsterCityWarBase import MonsterCityWarBase

class MonsterCityWarBase_Flag( MonsterCityWarBase ):
	"""
	�����
	"""
	def __init__( self ):
		MonsterCityWarBase. __init__( self )
		self.baseType = csdefine.CITY_WAR_FINAL_BASE_FLAG		# �ݵ�����

	def onActivated( self, selfEntity ):
		"""
		������
		"""
		# ֪ͨ����ˢ�»��콫
		spaceBase = selfEntity.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: ( %s, %i ) can't find spaceBase!" % ( selfEntity.className, selfEntity.id ) )
			return
		spaceBase.cell.onFlagActivated( self.baseType )

	def onOccupied( self, selfEntity, belong ):
		"""
		��ռ��
		"""
		MonsterCityWarBase.onOccupied( self, selfEntity, belong )
		spaceBase = selfEntity.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: ( %s, %i ) can't find spaceBase!" % ( selfEntity.className, selfEntity.id ) )
			return
		spaceBase.cell.onBaseFlagOccupied(  self.baseType, selfEntity.id, belong  )
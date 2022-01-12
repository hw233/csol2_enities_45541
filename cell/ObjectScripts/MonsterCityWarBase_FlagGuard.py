# -*- coding: gb18030 -*-

import BigWorld
import csdefine
from bwdebug import *
from MonsterCityWarBase import MonsterCityWarBase

class MonsterCityWarBase_FlagGuard( MonsterCityWarBase ):
	"""
	���콫
	"""
	def __init__( self ):
		MonsterCityWarBase. __init__( self )
		self.baseType = csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD		# �ݵ�����

	def receiveDamage( self, selfEntity, killerID, skillID, damageType, damage ):
		"""
		���յ��˺�
		"""
		if selfEntity.belong:		# �����޹�������£����˺�ͳ��
			return
			
		spaceBase = selfEntity.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: ( %s, %i ) can't find spaceBase!" % ( selfEntity.className, selfEntity.id ) )
			return
		changeDamage = min( selfEntity.HP, damage )
		spaceBase.cell.recordFlagGuardDamage(  selfEntity.id, killerID, changeDamage )

	def dieNotify( self, selfEntity, killerID ):
		"""
		����֪ͨ����selfEntity��die()������ʱ������
		"""
		MonsterCityWarBase.dieNotify( self, selfEntity, killerID )
		
		spaceBase = selfEntity.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: ( %s, %i ) can't find spaceBase!" % ( selfEntity.className, selfEntity.id ) )
			return
		spaceBase.cell.onFlagGuardDied( selfEntity.id, selfEntity.integral, killerID )

	def reset( self, selfEntity ):
		"""
		����
		"""
		selfEntity.destroy()
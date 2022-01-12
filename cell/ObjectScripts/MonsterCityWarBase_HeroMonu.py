# -*- coding: gb18030 -*-

import csdefine
from bwdebug import *
from MonsterCityWarBase import MonsterCityWarBase

class MonsterCityWarBase_HeroMonu( MonsterCityWarBase ):
	"""
	Ӣ�鱮
	"""
	def __init__( self ):
		MonsterCityWarBase. __init__( self )
		self.baseType = csdefine.CITY_WAR_FINAL_BASE_HEROMONU		# �ݵ�����

	def onCreated( self, selfEntity ):
		"""	
		��Դ�㴴��
		"""
		if not selfEntity.belong:
			selfEntity.belong = csdefine.CITY_WAR_FINAL_FACTION_DEFEND	# ���ڹ��Ƿ�
		MonsterCityWarBase.onCreated( self, selfEntity )

	def onActivated( self, selfEntity ):
		"""
		������Ƴ����ɱ�������־λ��
		"""
		selfEntity.removeFlag( csdefine.ENTITY_FLAG_CANT_BE_HIT_BY_ROLE )

	def reset( self, selfEntity ):
		"""
		����
		"""
		selfEntity.belong = csdefine.CITY_WAR_FINAL_FACTION_DEFEND

	def dieNotify( self, selfEntity, killerID ):
		"""
		����֪ͨ����selfEntity��die()������ʱ������
		"""
		MonsterCityWarBase.dieNotify( self, selfEntity, killerID )
		
		spaceBase = selfEntity.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: ( %s, %i ) can't find spaceBase!" % ( selfEntity.className, selfEntity.id ) )
			return
		spaceBase.cell.onHeroMonuDied( selfEntity.id, killerID )

	def onOccupied( self, selfEntity, belong ):
		"""
		��ռ��
		"""
		MonsterCityWarBase.onOccupied( self, selfEntity, belong )
		# ֪ͨ����
		spaceBase = selfEntity.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: ( %s, %i ) can't find spaceBase!" % ( selfEntity.className, selfEntity.id ) )
			return
		spaceBase.cell.onHeroMonuOccupied( self.baseType, selfEntity.id, belong  )
# -*- coding: gb18030 -*-

import csdefine
from bwdebug import *
from Monster import Monster

class MonsterCityWarBase(  Monster ):
	"""
	��Դ�ݵ�
	"""
	def __init__( self ):
		Monster.__init__( self )
		self.baseType = csdefine.CITY_WAR_FINAL_BASE_NONE		# �ݵ�����
	
	def onCreated( self, selfEntity ):
		"""	
		��Դ�㴴��
		"""
		selfEntity.baseType == self.baseType
		spaceBase = selfEntity.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: ( %s, %i ) can't find spaceBase!" % ( selfEntity.className, selfEntity.id ) )
			return
		spaceBase.cell.onCityWarBaseCreated( selfEntity.base, self.baseType, selfEntity.belong, selfEntity.className )

	def onActivated( self, selfEntity ):
		"""
		������
		"""
		pass

	def onOccupied( self, selfEntity, belong ):
		"""
		��ռ��
		"""
		if self.baseType in [ csdefine.CITY_WAR_FINAL_BASE_BATTLE, csdefine.CITY_WAR_FINAL_BASE_FLAG,\
		 csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD, csdefine.CITY_WAR_FINAL_BASE_HEROMONU ]:
			spaceBase = selfEntity.getCurrentSpaceBase()
			if spaceBase:
				spaceBase.cell.baseOccupiedNotice( self.baseType, selfEntity.getName(), belong )

	def reset( self, selfEntity ):
		"""
		����
		"""
		selfEntity.belong = csdefine.CITY_WAR_FINAL_FACTION_NONE

	def receiveDamage( self, selfEntity, casterID, damage ):
		"""
		���յ��˺�
		"""
		pass

 	def onReceiveSpell( self, selfEntity, caster, spell ):
 		"""
 		��������Ļص�����ĳЩ���⼼�ܵ���
 		"""
 		pass
 
 	def taskStatus( self, selfEntity, playerEntity ):
		"""
		�������ӽ��뵽ĳ��ҵ���Ұ������������������������������ҵĹ�ϵ
		"""
		pass


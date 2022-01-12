# -*- coding: gb18030 -*-

import BigWorld
import csdefine
import csstatus
from bwdebug import *
from MonsterCityWarBase import MonsterCityWarBase

SPELL_INTONE_TIME = 3.0
RESOURCE_SPELLID = 313100002

class MonsterCityWarBase_Resource(  MonsterCityWarBase ):
	"""
	��Դ�ݵ�
	����ʹ�ü���Spell_313100002 ����ʰȡ����
	"""
	def __init__( self ):
		MonsterCityWarBase. __init__( self )
		self.baseType = csdefine.CITY_WAR_FINAL_BASE_RESOURCE		# �ݵ�����

	def onCreated( self, selfEntity ):
		"""	
		��Դ�㴴��( ��Դ��û��base )
		"""
		spaceBase = selfEntity.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "TONG_CITY_WAR_FINAL: ( %s, %i ) can't find spaceBase!" % ( selfEntity.className, selfEntity.id ) )
			return
		spaceBase.cell.onCityWarBaseCreated( selfEntity, self.baseType, selfEntity.belong, selfEntity.className )

	def onOccupied( self, selfEntity, belong ):
		"""
		��ռ��
		"""
		spaceBase = selfEntity.getCurrentSpaceBase()
		if spaceBase:
			spaceBase.cell.onResourceBaseOccupied( self.baseType, selfEntity.id, selfEntity.ownerID, belong )

	def gossipWith(self, selfEntity, playerEntity, dlgKey):
		"""
		@param playerEntity: ���ʵ��
		@type  playerEntity: entity
		"""
		# �����жϸ�entity�Ƿ�Ϊreal����������queryTemp()һ��Ĵ��뽫������ȷִ�С�
		if not selfEntity.isReal():
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return

		playerEntity.setTemp( "quest_box_intone_time", SPELL_INTONE_TIME )	# ������ʱ���������������ȷ��������
		print "quest_box_intone_time:",SPELL_INTONE_TIME
		playerEntity.spellTarget( RESOURCE_SPELLID, selfEntity.id )

 	def onReceiveSpell( self, selfEntity, caster, spell ):
 		"""
 		��������Ļص�����ĳЩ���⼼�ܵ���
 		"""
		# �����жϸ�entity�Ƿ�Ϊreal����������queryTemp()һ��Ĵ��뽫������ȷִ�С�
		if not selfEntity.isReal():
			caster.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return
		
		# ȥ����ʱ��־
		caster.removeTemp( "quest_box_intone_time" )
		# ָʾ�ͻ��˲��Ź�Ч����
		#selfEntity.playEffect = self.effectName
		
		spaceBase = selfEntity.getCurrentSpaceBase()
		if spaceBase:
			spaceBase.cell.onRoleOccupyResource( caster.id, selfEntity )

 	def taskStatus( self, selfEntity, playerEntity ):
		"""
		��Դ����뵽ĳ��ҵ���Ұ����Դ����������������������ҵĹ�ϵ( Ĭ����Һ���Դ����һ��cell��)
		"""
		if not selfEntity.isReal():
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return

		if selfEntity.belong == playerEntity.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ):
			playerEntity.statusMessage( csstatus.TONG_CITY_WAR_BASE_OCCUPIED )
			return

		playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 1 )
# -*- coding: gb18030 -*-
#
from Spell_BuffNormal import Spell_BuffNormal
import random
import csdefine
import csstatus
import BigWorld
from Domain_Fight import g_fightMgr

class Spell_322416( Spell_BuffNormal ):
	"""
	���μ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_BuffNormal.__init__( self )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		self.receiveLinkBuff( caster, receiver )

		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			actPet = receiver.pcg_getActPet()
			petEntiy = None
			if actPet:
				petEntiy = actPet.entity
				if not petEntiy.isReal():
					petEntiy.receiveOnReal( caster.id, self )
				else:
					self.receiveLinkBuff( caster, petEntiy )

			# ֪ͨ����ս���б���Ҷ��γɹ���ȷ���ͻ��˱����������ʵ��Ч��һ��
			for entityID in receiver.enemyList.keys():
				entity = BigWorld.entities.get( entityID )
				if entity is None: continue
				state = entity.isRealLook( receiver.id )
				if state:
					# ��ʾ��Ŀ����⵽
					if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
						entity.clientEntity( receiver.id ).onSnakeStateChange( False )
				else:
					g_fightMgr.breakEnemyRelation( entity, receiver )
					
					# ֪ͨ�ͻ��˸���ģ�ͱ���
					if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
						entity.clientEntity( receiver.id ).onSnakeStateChange( True )


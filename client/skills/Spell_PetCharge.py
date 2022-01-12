# -*- coding: gb18030 -*-

import BigWorld
import csdefine
from SpellBase import *

class Spell_PetCharge( Spell ):
	"""
	�����漼�ܿͻ��˽ű�
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.config_movespeed = 0.0		# ����ٶȣ�����Ĭ�ϼ��ܷ����ٶ�

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		if dict["param1"]:
			self.config_movespeed = float( dict["param1"] )
		else:
			self.config_movespeed = self.getFlySpeed()

	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )

		target = targetObject.getObject()
		if caster.isEntityType( csdefine.ENTITY_TYPE_PET ):
			def onChargeOver( caster, target, result ):
				caster.onChargeOver()	# ������

			caster.cancelHeartBeat()	# ��濪ʼ��ֹͣ����
			caster.isCharging = True
			caster.navigator.chasePosition( target.position, 1.0, self.config_movespeed, onChargeOver )

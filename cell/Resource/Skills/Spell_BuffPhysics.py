# -*- coding: gb18030 -*-
#
# $Id: Spell_BuffPhysics.py,v 1.3 2008-07-04 03:50:57 kebiao Exp $

"""
"""

import csdefine
from SpellBase import *
import csstatus
from Spell_Item import Spell_Item
from Spell_PhysSkill import Spell_PhysSkill2
from Spell_PhysSkill import Spell_PhyVolley2
import random

class Spell_BuffPhysics( Spell_PhysSkill2 ):
	"""
	�ͷ������˺���BUFF�� ������ܱ����������˺��� �������������� ���� ����·��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhysSkill2.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhysSkill2.init( self, dict )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		#�����Ĭ��һ�༼�ܵ�ʩ���ж�
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
		if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ):
			return csstatus.SKILL_CANT_CAST
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		return Spell_PhysSkill2.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if receiver is None:
			return
			
		damageType = self._damageType
		# ����������
		hit = self.calcHitProbability( caster, receiver )
		if receiver.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0 or not random.random() < hit:
			# ���㿪�˲���������û���㣬��˳�����п��ܴ��ڵģ���Ҫ֪ͨ�ܵ�0���˺�
			receiver.receiveSpell( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0, 0 )
			receiver.receiveDamage( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0 )
			caster.doAttackerOnDodge( receiver, damageType )
			receiver.doVictimOnDodge( caster, damageType )
			return

		self.receiveLinkBuff( caster, receiver )
		# ִ�����к����Ϊ
		caster.doAttackerOnHit( receiver, damageType )	#�����ߴ���
		receiver.doVictimOnHit( caster, damageType )   #�ܻ��ߴ���
		

class Spell_BuffPhyVolley2( Spell_PhyVolley2 ):
	"""
	�ͷ������˺���BUFF�� ������ܱ����������˺��� �������������� ���� ����·��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhyVolley2.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhyVolley2.init( self, dict )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		damageType = self._damageType
		# ����������
		hit = self.calcHitProbability( caster, receiver )
		if receiver.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0 or not random.random() < hit:
			# ���㿪�˲���������û���㣬��˳�����п��ܴ��ڵģ���Ҫ֪ͨ�ܵ�0���˺�
			receiver.receiveSpell( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0, 0 )
			receiver.receiveDamage( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0 )
			caster.doAttackerOnDodge( receiver, damageType )
			receiver.doVictimOnDodge( caster, damageType )
			return

		self.receiveLinkBuff( caster, receiver )
		# ִ�����к����Ϊ
		caster.doAttackerOnHit( receiver, damageType )	#�����ߴ���
		receiver.doVictimOnHit( caster, damageType )    #�ܻ��ߴ���
		
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/07/03 02:49:39  kebiao
# �ı� ˯�� �����Ч����ʵ��
#
# Revision 1.1  2008/05/27 02:10:37  kebiao
# no message
#
#
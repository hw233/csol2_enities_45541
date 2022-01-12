# -*- coding: gb18030 -*-
#
# $Id:  Exp $


from SpellBase import *
import random
import csdefine
import csstatus
from bwdebug import *
from Spell_Magic import *

class Spell_SunBurn( Spell_MagicVolley ):
	"""
	��������
	"""
	def __init__( self ):
		"""
		"""
		Spell_MagicVolley.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_MagicVolley.init( self, dict )
		self.param1 = float( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0.0 )
	
	
	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		�����ִ�Ŀ��ͨ�档��Ĭ������£��˴�ִ�п�������Ա�Ļ�ȡ��Ȼ�����receive()�������ж�ÿ���������߽��д���
		ע���˽ӿ�Ϊ�ɰ��е�receiveSpell()

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""

		# ��ȡ����������
		receivers = self.getReceivers( caster, target )
		for receiver in receivers:
			receiver.clearBuff( self._triggerBuffInterruptCode )
			receiver.setTemp( "SunFire_Count", len(receivers) )
			self._skill.cast( caster, SkillTargetObjImpl.createTargetObjEntity( receiver ) )
			self.receiveEnemy( caster, receiver )
		# ���Լ���ʹ�ô���
		caster.doOnUseMaligSkill( self )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if caster is not None:
			casterID = caster.id
		else:
			casterID = 0
		if not receiver.isReal():
			receiver.receiveOnReal( casterID, self )
			return
		value = self.param1/receiver.queryTemp( "SunFire_Count", 1.0 )
		#�������С��Ƶд�����ʵ�ʼ��� 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		value *= rm
			
		#receiver.receiveDamage( caster.id, self.getID(), csdefine.DAMAGE_TYPE_MAGIC, value )
		self.persentDamage( caster, receiver, csdefine.DAMAGE_TYPE_MAGIC, value )
		receiver.removeTemp( "SunFire_Count" )
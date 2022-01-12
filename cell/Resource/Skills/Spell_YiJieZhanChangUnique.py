# -*- coding: gb18030 -*-

import csdefine
from SpellBase import *

class Spell_YiJieZhanChangUnique( CombatSpell ):
	"""
	��ɵ�ǰĿ������ֵ���޵�һ�������������˺������ӷ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		CombatSpell.__init__( self )
		self._damageType = csdefine.DAMAGE_TYPE_PHYSICS		# �˺����
		self._percentage = 0								# �˺��ٷֱ�

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		CombatSpell.init( self, dict )
		self._percentage = int( dict["param1"] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		if receiver.isDestroyed:
			return

		finiDamage = int( receiver.HP_Max * self._percentage / 100 )
		#�������С��Ƶд�����ʵ�ʼ��� 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		finiDamage *= rm

		self.persentDamage( caster, receiver, self._damageType, max( 1, int( finiDamage ) ) )
		self.receiveLinkBuff( caster, receiver )

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
		CombatSpell.onArrive( self, caster, target )
		if hasattr( caster, "yiJieOnUniqueSpellArrive" ) :
			caster.yiJieOnUniqueSpellArrive()
	

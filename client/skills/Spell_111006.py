# -*- coding:gb18030 -*-

"""
Spell������
"""
from Spell_Item import Spell_Item
import BigWorld
import csdefine

class Spell_111006( Spell_Item ):
	"""
    ��Ŀ�굥λ����൱��������ֵ����xx%���˺�
	"""
	def __init__( self ):
		"""
		���캯��
		"""
		Spell_Item.__init__( self )
		self.damage = 0

	def init( self, dict ):
		"""
		��ȡ����
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.param1 = int( dict["param1"] if len( dict["param1"] ) > 0 else 0 )  / 100.0

	def cast( self, caster, targetObject ):
		"""
		virtual method.
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell_Item.cast( self, caster, targetObject )
		target = targetObject.getObject()
		self.damage = int( target.HP_Max * self.param1 )
		target.onReceiveDamage( caster.id, self, csdefine.DAMAGE_TYPE_PHYSICS_NORMAL, self.damage )

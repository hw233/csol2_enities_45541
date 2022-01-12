# -*- coding: gb18030 -*-
#
# ʹ����Ʒʹ�Լ��޵еĿͻ��˼��� by pengju
#
from Spell_Item import Spell_Item
import csstatus

class Spell_Item_Cannot_PK( Spell_Item ):
	"""
	ʹ����Ʒʹ�Լ��޵еĿͻ��˼���
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		self._castLvMax = dict[ "CastObjLevelMax" ] if dict[ "CastObjLevelMax" ] else 0
		Spell_Item.init( self, dict )

	def useableCheck( self, caster, target ):
		"""
		У�鼼���Ƿ����ʹ�á�

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		targetEntity = target.getObject()
		if targetEntity.level > self._castLvMax:
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return Spell_Item.useableCheck( self, caster, target )


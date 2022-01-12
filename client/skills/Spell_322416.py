# -*- coding: gb18030 -*-

"""
Spell�����ࡣ
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csstatus
import csdefine

class Spell_322416( Spell ):
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell.init( self, dict )

	def spell( self, caster, target ):
		"""
		�����������Spell����

		@param caster:		ʩ����Entity
		@type  caster:		Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: INT, see also csdefine.SKILL_*
		"""
		buffs = caster.attrBuffs
		for buff in buffs:
			skill = buff["skill"]
			if skill.getBuffID() == "020002":
				index = buff["index"]
				caster.requestRemoveBuff( index )
				return

		Spell.spell( self, caster, target )
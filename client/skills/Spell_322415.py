# -*- coding: gb18030 -*-
#
# $Id: Spell_311101.py,v 1.3 2008-03-10 01:01:25 kebiao Exp $

"""
Spell�����ࡣ
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csstatus
import csdefine

class Spell_322415( Spell ):
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Spell.__init__( self )
		self._isCanFight = 0  #�Ƿ��ս��״̬��ʹ��

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		if dict["param1"] != "":
			self._isCanFight = int( dict["param1"] )

	def useableCheck( self, caster, receiver ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ��
		"""
		if self._isCanFight:
			if caster.state != csdefine.ENTITY_STATE_FREE:
				return csstatus.SKILL_NEED_STATE_FREE
		return Spell.useableCheck( self, caster, receiver )

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
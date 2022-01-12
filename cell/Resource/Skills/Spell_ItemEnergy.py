# -*- coding: gb18030 -*-
#
#

import Const
import csstatus
from Spell_ItemCure import Spell_ItemCure

class Spell_ItemEnergy( Spell_ItemCure ):
	"""
	�����ָ� ��Ѫ��
	"""
	def __init__( self ):
		"""
		"""
		Spell_ItemCure.__init__( self )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		#�����������ǰ�� ��ο��ײ�
		Spell_ItemCure.receive( self, caster, receiver )
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		lostEN = Const.ROLE_EN_MAX_VALUE - receiver.energy
		curEN = min( self._effect_max, max( self._effect_min, lostEN ) )
		item.setTemp( "sd_usePoint", curEN )
		receiver.gainEnergy( lostEN, False )
		receiver.statusMessage( csstatus.SKILL_ENERGY_CURE, item.name(), lostEN )

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
		if target.getObject().energy == Const.ROLE_EN_MAX_VALUE:
			return csstatus.SKILL_CURE_NONEED
		return Spell_ItemCure.useableCheck( self, caster, target)

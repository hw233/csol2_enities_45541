# -*- coding: gb18030 -*-

# ϵͳ���ܣ�����һ��AreaRestrictTransducer��entity(���幦��entity)����ʩ����λ��

import BigWorld
import csdefine
import csstatus
from SpellBase import *
from Spell_CastTotem import Spell_CastTotem

class Spell_311139( Spell_CastTotem ):
	"""
	ϵͳ����
	��Ӧ��Χ2�ף����÷�Χ3��5�ˣ�����ʩ���߳���50��ʧЧ��	����30�����ʧ��������4��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_CastTotem.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_CastTotem.init( self, dict )
		
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
		state = Spell_CastTotem.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:	# �ȼ��cooldown������
			return state
			
		count = 0
		for entity in caster.entitiesInRangeExt( 50.0, "SkillTrap", caster.position ):
			if entity.casterID == caster.id and entity.originSkill == self.getID():
				count += 1
				
		if count >= 4:
			return csstatus.SKILL_UNKNOW
		
		return state
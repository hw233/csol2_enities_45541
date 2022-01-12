# -*- coding: gb18030 -*-

# ϵͳ���ܣ�����һ��AreaRestrictTransducer��entity(���幦��entity)����ʩ����λ��

import BigWorld
import csdefine
import csstatus
from SpellBase import *
from Spell_BuffNormal import Spell_BuffNormal
import csarithmetic

class Spell_730001( Spell_BuffNormal ):
	"""
	����ǿ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_BuffNormal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )
		
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
		state = Spell_BuffNormal.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:	# �ȼ��cooldown������
			return state
				
		if not target.getObject().isDarting():
			return csstatus.SKILL_CANT_CAST
		
		dartVehicle = BigWorld.entities.get( caster.queryTemp( "dart_id", 0 ), None )
		if not dartVehicle or dartVehicle.spaceID != caster.spaceID or csarithmetic.distancePP3( caster.position, dartVehicle.position ) > 10.0:
			return csstatus.SKILL_CANT_CAST
			
		return state
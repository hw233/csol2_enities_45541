# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *
from SpellBase import *
from event.EventCenter import *
import ItemTypeEnum
import csstatus
from Function import Functor
import csdefine

class Spell_Item( Spell ):
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
		
	def useableCheck( self, caster, target ):
		"""
		У�鼼���Ƿ����ʹ�á�

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		
		# ���������Ʒ�ͷţ���ô�����жϵ�ǰ���ܣ����Դ˲��費���жϣ����ͻ��ˣ���
#		if caster.intonating():
#			return csstatus.SKILL_ITEM_INTONATING
		if caster.actionSign( csdefine.ACTION_FORBID_USE_ITEM ):
			return csstatus.CIB_MSG_TEMP_CANT_USE_ITEM	
			
		state = self.validCaster( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ���Ŀ���Ƿ����
		state = self.validTarget( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ���ʩ���ߵ������Ƿ��㹻
		state = self._checkRequire( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ��鼼��cooldown ���ݿ������ɫ��������������������ж�˳�� ���ֻ�ܷ����
		if not self.isCooldown( caster ):
			return csstatus.SKILL_ITEM_NOT_READY

		if self.getIntonateTime() > 0.1 and caster.isJumping(): # ��Ծ����ʾ����������ϡ���csol-899
			return csstatus.SKILL_IN_ATTACK
		return csstatus.SKILL_GO_ON	
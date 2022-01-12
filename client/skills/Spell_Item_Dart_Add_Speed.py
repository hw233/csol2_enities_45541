# -*- coding: gb18030 -*-
#
# ����Ŀͻ��˼��� 2009-01-10 SongPeifang & LinQing
#
from Spell_Item import Spell_Item
import GUIFacade
import BigWorld
import random
import csdefine
import csstatus

class Spell_Item_Dart_Add_Speed( Spell_Item ):
	"""
	��޵Ŀͻ��˼���
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )


	def useableCheck( self, caster, target ):
		"""
		У�鼼���Ƿ����ʹ�á�

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		
		if caster.getSlaveDart() is None and caster.actionSign( csdefine.ACTION_FORBID_USE_ITEM ):
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


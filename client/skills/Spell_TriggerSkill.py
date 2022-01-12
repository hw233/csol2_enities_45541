# -*- coding: gb18030 -*-
#
# edit by wuxo

"""
�������������ࡣ
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import skills as Skill

class Spell_TriggerSkill( Spell ):
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Spell.__init__( self )
		self.parentID = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		if dict[ "param2" ] != "":
			self.parentID = int ( dict[ "param2" ] )

	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		
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
		return Spell.useableCheck( self, caster, target )
		
		
	def isTriggerSkill( self ):
		"""
		�ж��Ƿ񴥷��������� 	
		@return: BOOL
		"""
		return True
	
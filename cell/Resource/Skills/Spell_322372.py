# -*- coding: gb18030 -*-
#
# $Id: Spell_CatchPet.py,v 1.20 2008-07-04 03:50:57 kebiao Exp $

"""
"""

from SpellBase import *
import csstatus
import csconst
from PetFormulas import formulas
from Spell_CatchPet import Spell_CatchPet

class Spell_322372( Spell_CatchPet ):
	"""
	ʹ�ã�ץ�����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_CatchPet.__init__( self )
		self.canCatchs = []

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_CatchPet.init( self, dict )
		self.canCatchs = ( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else "" ) .split( "|" )	

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csstatus.SKILL_*
		@rtype:            INT
		"""
		bool = Spell_CatchPet.useableCheck( self, caster, target )
		if bool != csstatus.SKILL_GO_ON:
			return bool
		if target.getObject().className in self.canCatchs:
			return csstatus.SKILL_GO_ON
		else:
			return csstatus.SKILL_CAST_OBJECT_INVALID

# $Log: not supported by cvs2svn $
#
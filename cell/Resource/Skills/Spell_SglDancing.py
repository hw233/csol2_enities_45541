# -*- coding: gb18030 -*-
#
# $Id: Spell_Physics.py,v 1.28 2008-08-13 07:55:41 kebiao Exp $

"""
������
2009.07.16: by huangyongwei
"""

import BigWorld
import csdefine
import csstatus
import Const
from SpellBase import *
from bwdebug import *

class Spell_SglDancing( Spell ):
	def __init__( self ):
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )

	def getType( self ):
		"""
		ȡ�û�����������
		��Щֵ��BASE_SKILL_TYPE_*֮һ
		"""
		return csdefine.BASE_SKILL_TYPE_ACTION

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
		if caster.getState() != csdefine.ENTITY_STATE_FREE:
			if caster.getState() == csdefine.ENTITY_STATE_DANCE or caster.getState() == csdefine.ENTITY_STATE_DOUBLE_DANCE:
				return csstatus.JING_WU_SHI_KE_IN_DANCE
			return csstatus.JING_WU_SHI_KE_NOT_FREE
		return csstatus.SKILL_GO_ON

	def receive( self, caster, receiver ) :
		caster.singleDance()

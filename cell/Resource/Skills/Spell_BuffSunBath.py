# -*- coding: gb18030 -*-
#
# �չ�ԡ�ļ���

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from SpellBase import *
from Spell_BuffNormal import Spell_BuffNormal


class Spell_BuffSunBath( Spell_BuffNormal ):
	"""
	�չ�ԡbuff����
	"""
	def __init__( self ):
		"""
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
		# �ܷ�ʹ��������ܵ������ж�
		# Ŀǰ�ǲ��������������������
		return csstatus.SKILL_GO_ON
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		receiver = caster	# ��Ϊʩ����������Լ������ǽ�����ȷ�п�����npc
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		self.receiveLinkBuff( caster, receiver )
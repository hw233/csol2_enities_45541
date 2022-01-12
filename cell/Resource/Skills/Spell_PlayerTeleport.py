# -*- coding: gb18030 -*-
#
# $Id: Spell_PlayerTeleport.py,v 1.1 2008-04-26 04:04:50 kebiao Exp $

"""
���ͼ��ܻ���
"""
import BigWorld
import csstatus
import csdefine
from SpellBase import *
from Spell_TeleportBase import Spell_TeleportBase

class Spell_PlayerTeleport( Spell_TeleportBase ):
	"""
	��ҳ������еĴ��ͼ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_TeleportBase.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_TeleportBase.init( self, dict )

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
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		return Spell_TeleportBase.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		receiver.gotoSpace( receiver.reviveSpace, receiver.revivePosition, receiver.reviveDirection )

# $Log: not supported by cvs2svn $
#
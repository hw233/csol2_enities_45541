# -*- coding: gb18030 -*-
#
# $Id: Spell_121014.py,v 1.5 2008-07-15 04:06:26 kebiao Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
from Spell_BuffNormal import Spell_Buff
import utils
import csstatus
import csdefine
import BigWorld

class Spell_122157001( Spell_Buff ):
	"""
	�Ƹ�����	�����������10%.

	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Buff.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Buff.init( self, dict )

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
		return Spell_Buff.useableCheck( self, caster, target )

	def receiveLinkBuff( self, caster, receiver ):
		"""
		��entity����buff��Ч��
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: ʩչ����
		@type  receiver: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		p1 = receiver
		if p1.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = p1.getOwner()
			if owner.etype == "MAILBOX" : return
			pl = owner.entity
		if not p1.tong_dbID in BigWorld.globalData[ "CityWarRightTongDBID" ]:		# ֻ�г���ս�����زſ��Ի�ø�BUFF
			return
		Spell_Buff.receiveLinkBuff( self, caster, receiver )					# ʩ���߻�ø�buff��

# $Log: not supported by cvs2svn $
# Revision 1.1  2007/12/20 05:43:42  kebiao
# no message
#
#
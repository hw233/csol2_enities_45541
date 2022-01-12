# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemHP.py,v 1.10 2008-08-14 06:11:09 songpeifang Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
from Spell_Item import Spell_Item
import csstatus
import csdefine

class Spell_ItemPK( Spell_Item ):
	"""
	ʹ�ã����̸ı������ߵ�PKֵ by����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.redPKValue = int(( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ))
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		self.setPKValue( caster, receiver )
		
	def setPKValue( self, caster, receiver ):
		"""
		���������ߵ�PKֵ
		"""
		if receiver.getEntityType() != csdefine.ENTITY_TYPE_ROLE: return
		if receiver.pkValue < self.redPKValue:
			receiver.statusMessage( csstatus.SKILL_CHANGE_PKVALUE, receiver.pkValue )
		else:
			receiver.statusMessage( csstatus.SKILL_CHANGE_PKVALUE, self.redPKValue )
		receiver.setPkValue( receiver.pkValue - self.redPKValue )
		
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
		if target.getObject().pkValue == 0:
			return csstatus.SKILL_CHANGE_PKVALUE_NONEED
		return Spell_Item.useableCheck( self, caster, target)
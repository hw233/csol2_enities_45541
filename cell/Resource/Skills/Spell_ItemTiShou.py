# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
���ܶ���Ʒʩչ����������
"""

import csstatus
import random
import csdefine
import cschannel_msgs
from Spell_Item import Spell_Item

class Spell_ItemTiShou( Spell_Item ):
	"""
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

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		#�����������ǰ�� ��ο��ײ�
		Spell_Item.receive( self, caster, receiver )
		#caster.client.openTiShouSelect()
		#caster.setTemp( "allowTiShou", True)
		caster.createTSNPC( caster.id, 1, cschannel_msgs.TISHOU_INFO_01%caster.playerName )

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
		if not target.getObject().canVendInArea():
			return csstatus.TISHOU_FORBID_AREA
		if target.getObject().level < 15:
			return csstatus.TISHOU_FORBID_LEVEL
		if target.getObject().hasFlag( csdefine.ROLE_FLAG_TISHOU ):
			target.getObject().client.onStatusMessage( csstatus.ROLE_ALREADY_TISHOU, "" )
			return csstatus.SKILL_ITEM_NOT_READY
		if caster.isState( csdefine.ENTITY_STATE_VEND ) :
			caster.client.onStatusMessage( csstatus.TISHOU_FORBID_VENDING, "" )
			return csstatus.SKILL_ITEM_NOT_READY
		return Spell_Item.useableCheck( self, caster, target)


# -*- coding: gb18030 -*-
#
# $Id: Spell_Item.py,v 1.1 12:10 2010-9-4 jianyi Exp $

import BigWorld
import csdefine
import csstatus
from bwdebug import *
from Spell_Item import Spell_Item

class Spell_Item_NPC_Visible( Spell_Item ):
	"""
	ʹ����Ʒ��һ��NPC�ɼ�/���ɼ�
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.targetNpcClassName = dict["param1"] if len( dict["param1"] ) > 0 else None	# str or None
		self.checkDistance = int( dict["param2"] if len( dict["param2"] ) > 0 else 0 )
		self.visible = bool( int( dict["param3"] if len( dict["param3"] ) > 0 else 0 ) )
		self.lasted = float( dict["param4"] if len( dict["param4"] ) > 0 else 0 )
		
	def useableCheck( self, caster, target ):
		"""
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		��Ҫ��������Ϣ�����ⲻ��ʹ����Ʒʱ��ʾʹ�ü���
		"""
		# ��ֹ����ԭ���µĲ���ʩ��
		if self.targetNpcClassName is None:
			ERROR_MSG( "config error, target npc className is None." )
			return csstatus.CIB_ITEM_CONFIG_ERROR
		if self.checkDistance <= 0:
			ERROR_MSG( "config error, check distance is 0 or less." )
			return csstatus.CIB_ITEM_CONFIG_ERROR
		
		t = None
		entities = caster.entitiesInRangeExt( self.checkDistance )
		for e in entities:
			if e.className == self.targetNpcClassName:
				t = e
		if t is None:
			return csstatus.CIB_MSG_TEMP_CANT_USE_ITEM
				
		return Spell_Item.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		��������ʱ
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		entities = caster.entitiesInRangeExt( self.checkDistance )
		for e in entities:
			if e.className == self.targetNpcClassName:
				if e.isReal():
					e.setVisibleByRole( caster, self.visible, self.lasted )
				else:
					e.remoteCall( "setVisibleByRole", ( caster, self.visible, self.lasted ) )
		Spell_Item.receive( self, caster, receiver )
# -*- coding: gb18030 -*-
#
# $Id:  Exp $


from SpellBase import *
import random
import csdefine
import csstatus
from bwdebug import *
from Spell_BuffNormal import *

class Spell_Race_Item( Spell_ItemBuffNormal ):
	"""
	ʹ����Ʒ���ܻ���
	"""
	def __init__( self ):
		"""
		"""
		Spell_ItemBuffNormal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_ItemBuffNormal.init( self, dict )

	def getType( self ):
		"""
		"""
		return csdefine.BASE_SKILL_TYPE_ITEM

	def onSpellInterrupted( self, caster ):
		"""
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.hr_getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % ( uid ) )
			return
		item.unfreeze()
		caster.removeTemp( "item_using" )
		Spell_ItemBuffNormal.onSpellInterrupted( self, caster )

	def setCooldownInUsed( self, caster ):
		"""
		"""
		Spell_ItemBuffNormal.setCooldownInUsed( self, caster )
		uid = caster.queryTemp( "item_using" )
		item = caster.hr_getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		item.onSetCooldownInUsed( caster )

	def setCooldownInIntonateOver( self, caster ):
		"""
		"""
		Spell_ItemBuffNormal.setCooldownInIntonateOver( self, caster )
		uid = caster.queryTemp( "item_using" )
		item = caster.hr_getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		item.onSetCooldownInIntonateOver( caster )

	def cast( self, caster, target ):
		"""
		"""
		Spell_ItemBuffNormal.cast( self, caster, target )
		#������Ʒ ֻ����Ʒ�ɹ�ʹ��֮��ſ��Զ���Ʒ���������в���
		self.updateItem( caster ) #������д�����������Ϊ��ʱ���Ա�֤casterΪreal,��Ϊʹ����Ʒ���ܻ�Գ����ʹ�ã���˲���ʹ��receiver

	def updateItem( self , caster ):
		"""
		������Ʒʹ��
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.hr_getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		caster.removeRaceItem( item.getOrder() )
		caster.removeTemp( "item_using" )

	def useableCheck( self, caster, target ):
		"""
		"""
		# ��鼼��cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_ITEM_NOT_READY

		if target.getObject().id == caster.id and self._receiverObject.__class__.__name__ != "ReceiverObjectSelf" \
		and self.getID() != 760016001L and self.getID() != 760015001L:
			return csstatus.SKILL_CAN_NOT_CAST_TO_SELF
		return csstatus.SKILL_GO_ON
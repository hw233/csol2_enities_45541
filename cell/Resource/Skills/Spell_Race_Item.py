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
	使用物品技能基础
	"""
	def __init__( self ):
		"""
		"""
		Spell_ItemBuffNormal.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
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
		#更新物品 只有物品成功使用之后才可以对物品的消减进行操作
		self.updateItem( caster ) #在这里写这个操作是因为此时可以保证caster为real,因为使用物品可能会对宠物等使用，因此不能使用receiver

	def updateItem( self , caster ):
		"""
		更新物品使用
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
		# 检查技能cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_ITEM_NOT_READY

		if target.getObject().id == caster.id and self._receiverObject.__class__.__name__ != "ReceiverObjectSelf" \
		and self.getID() != 760016001L and self.getID() != 760015001L:
			return csstatus.SKILL_CAN_NOT_CAST_TO_SELF
		return csstatus.SKILL_GO_ON
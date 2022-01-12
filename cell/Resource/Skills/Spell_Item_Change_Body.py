# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_Change_Body.py,v 1.2 2008-08-14 02:32:06 zhangyuxing Exp $

"""
在规定位置使用物品
"""

from SpellBase import *
import cschannel_msgs
import ShareTexts as ST
from Spell_BuffNormal import Spell_ItemBuffNormal
import csstatus
import BigWorld
import csdefine
import csconst
from Spell_Item_BianShen import Spell_Item_BianShen

class Spell_Item_Change_Body( Spell_Item_BianShen ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item_BianShen.__init__( self )
		self.spaceLimited = ""


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item_BianShen.init( self, dict )



	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		self.drawChangeBody( caster, receiver )
		Spell_ItemBuffNormal.receive( self, caster, caster )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return

		if item.query( "changeBodyTargetID", "" ) != "":
			return csstatus.SKILL_USE_ITEM_HAS_TARGET
		elif item.query( "changeBodyIntentionTargetID", "") == "" or item.query( "changeBodyIntentionTargetID", "") == target.getObject().className:
			return Spell_Item_BianShen.useableCheck( self, caster, target)

		elif item.query( "changeBodyIntentionTargetID", "") != target.getObject().className:
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET


	def drawChangeBody( self, caster, receiver):
		"""
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		item.set( "changeBodyTargetID", receiver.className )
		item.set( "name",  cschannel_msgs.SKILL_INFO_6 % receiver.getName(), caster )


	def updateItem( self , caster ):
		"""
		更新物品使用
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		itemCopy = item.new()
		item.set( "changeBodyTargetID", "0" )
		item.set( "name",  cschannel_msgs.QUEST_INFO_38, None )
		item.onSpellOver( caster )
		caster.addItemAndNotify_( itemCopy, csdefine.ADD_ITEM_CHANGE_BODY )
		caster.removeTemp( "item_using" )

# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_Dance.py,v 1.2 2008-08-14 02:32:06 zhangyuxing Exp $

"""
在规定位置使用物品
"""

from bwdebug import *
import cschannel_msgs
import ShareTexts as ST
from SpellBase import *
from Spell_Item import Spell_Item
import csstatus
import BigWorld
import csconst
import csdefine
from VehicleHelper import getCurrVehicleID

class Spell_Item_Dance( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )



	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		caster.singleDance()
		self.drawDance( caster, receiver )
		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		if caster.getState() != csdefine.ENTITY_STATE_FREE:
			return csstatus.JING_WU_SHI_KE_NOT_FREE
		if getCurrVehicleID( caster ):
			return csstatus.ACTION_CANT_USE_ON_VEHICLE
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item.query( "danceTargetID", "" ) != "":
			return csstatus.SKILL_USE_ITEM_HAS_TARGET
		elif item.query( "danceIntentionTargetID", "") == "" or item.query( "danceIntentionTargetID", "") == target.getObject().className:
			return Spell_Item.useableCheck( self, caster, target)

		elif item.query( "danceIntentionTargetID", "") != target.getObject().className:
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET


	def drawDance( self, caster, receiver):
		"""
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		item.set( "danceTargetID", receiver.className )
		item.set( "name",  cschannel_msgs.SKILL_INFO_7 % receiver.getName(), caster )


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
		item.set( "danceTargetID", "0" )
		item.set( "name",  cschannel_msgs.QUEST_INFO_41, None )
		item.onSpellOver( caster )
		caster.addItemAndNotify_( itemCopy, csdefine.ADD_ITEM_DANCE )
		caster.removeTemp( "item_using" )

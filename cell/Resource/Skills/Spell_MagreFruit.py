# -*- coding: gb18030 -*-

import csstatus
import csconst
import csdefine
import random
from Spell_Item import Spell_Item
from bwdebug import *
import BigWorld
import items
g_items = items.instance()

class Spell_MagreFruit( Spell_Item ):
	"""
	�ϳɹ�ʵ
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		self.p1 = 0
		self.p2 = 0
		self.p3 = 0
		self.p4 = 0
		self.p5 = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.p1 = int( dict[ "param1" ] )		# ��������1
		self.p2 = int( dict[ "param2" ] )		# ��������1����
		self.p3 = int( dict[ "param3" ] )		# ��������2
		self.p4 = int( dict[ "param4" ] )		# ��������2����
		self.p5 = int( dict[ "param5" ] )		# �ϳ���Ʒ

	def updateItem( self , caster ):
		"""
		������Ʒʹ��
		"""
		uid = caster.popTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		item.onSpellOver( caster )
		
		name1 = g_items.id2name( self.p1 )
		name2 = g_items.id2name( self.p3 )
		items1 = caster.findItemsByID( self.p1 )

		amount1 = sum( [k.amount for k in items1] )
		if amount1 < self.p2:
			caster.statusMessage( csstatus.FRUIT_NO_ITEM, name1, name2 )
			return

		items2 = caster.findItemsByID( self.p3 )
		amount2 = sum( [k.amount for k in items2] )
		if amount2 < self.p4:
			caster.statusMessage( csstatus.FRUIT_NO_ITEM, name1, name2 )
			return

		item = g_items.createDynamicItem( self.p5 )
		if item is None: return

		if caster.addItemAndNotify_( item, reason = csdefine.ADD_ITEM_MEGRA_FRUIT ):
			caster.removeItemTotal( self.p1, self.p2, reason = csdefine.DELETE_ITEM_MEGRA_FRUIT )
			caster.removeItemTotal( self.p3, self.p4, reason = csdefine.DELETE_ITEM_MEGRA_FRUIT )
		else:
			caster.statusMessage( csstatus.FRUIT_BAG_FULL )

# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_PresentKit.py,v  hd

"""
ChinaJoy活动奖品包
"""

from bwdebug import *
from Spell_Item import Spell_Item
import csstatus
import csdefine
import random
import ItemTypeEnum
from Love3 import g_rewards

class Spell_Item_PresentKit_ChinaJoy( Spell_Item ):
	"""
	ChinaJoy活动的奖品包
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

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		return Spell_Item.useableCheck( self, caster, target)

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		Spell_Item.receive( self, caster, receiver )
		
		uid = caster.queryTemp( "item_using" )
		useitem = caster.getByUid( uid )
		rewardID = int( useitem.query( "param1", 0 ) )
		presentItems = g_rewards.fetch( rewardID, caster )
		if presentItems is None:
			useitem.setTemp( "usefailed", 1 )
			caster.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
			return
		mul_list = []
		actureAmount = 0	# 统计物品所需格子数目
		for item in presentItems.items:
			if item.getStackable() <= 1:
				actureAmount += 1
			else:
				if not item.id in mul_list:
					actureAmount += 1
					mul_list.append( item.id )
		freeSpace = caster.getNormalKitbagFreeOrder()
		if freeSpace < 1:
			useitem.setTemp( "usefailed", 1 )
			caster.statusMessage( csstatus.PCU_NOT_ENOUGH_GRID )
			return
			
		for item in presentItems.items:
			item.setBindType( ItemTypeEnum.CBT_PICKUP )
		presentItems.award( caster, csdefine.ADD_ITEM_CHINAJOY )
		
	def updateItem( self , caster ):
		"""
		更新物品使用
		"""
		uid = caster.popTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		if item.queryTemp( "usefailed" ) is None:
			item.onSpellOver( caster )
		else:
			item.popTemp( "usefailed" )
		caster.removeTemp( "item_using" )
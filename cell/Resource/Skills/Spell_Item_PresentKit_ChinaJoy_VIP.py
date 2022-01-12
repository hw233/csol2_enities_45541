# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_PresentKit.py,v  jy

"""
ChinaJoy活动奖品包
"""

from bwdebug import *
from Spell_Item import Spell_Item
import csstatus
import csdefine
import ItemTypeEnum
from Love3 import g_rewards
from ItemSystemExp import EquipIntensifyExp

g_equipIntensify = EquipIntensifyExp.instance()

class Spell_Item_PresentKit_ChinaJoy_VIP( Spell_Item ):
	"""
	ChinaJoy活动VIP的奖品包
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )
		self.instLevel = 0

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
		return Spell_Item.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		Spell_Item.receive( self, caster, receiver )
		
		uid = caster.queryTemp( "item_using" )
		useitem = caster.getByUid( uid )
		rewardID = int( useitem.query( "param1", 0 ) )
		insl = useitem.query( "param2", 0 )
		if insl == None:
			self.instLevel = 0
		else:
			insl = int( insl )
			if insl < 0 or insl > 9:
				ERROR_MSG( "inst config error." )
				self.instLevel = 0
			else:
				self.instLevel = insl
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
		freeSpace = caster.getNormalKitbagFreeOrderCount()	# 背包剩余格子数
		if freeSpace < actureAmount:
			useitem.setTemp( "usefailed", 1 )
			caster.statusMessage( csstatus.PCU_NOT_ENOUGH_GRID )
			return

		for item in presentItems.items:
			item.setBindType( ItemTypeEnum.CBT_PICKUP )
			if item.isEquip() and item.canIntensify() and self.instLevel > 0:
				dragonGemID = 0
				iLevel = item.getLevel()
				if iLevel > 30 and iLevel < 91:
					if iLevel < 51: dragonGemID = 80101032
					else: dragonGemID = 80101037
				else:
					case = iLevel / 30
					if case == 0 or iLevel == 30: dragonGemID = 80101031
					elif case == 3 or iLevel == 120: dragonGemID = 80101038
					else: dragonGemID = 80101039
				for i in xrange( self.instLevel ):
					g_equipIntensify.setIntensifyValue( item, dragonGemID, i + 1 )	# 装备强化和相应等级范围的龙珠及其效果对应
				item.setIntensifyLevel( self.instLevel )
			if item.isEquip(): item.fixedCreateRandomEffect( item.getQuality(), caster, False )	# 附加属性
		presentItems.award( caster, csdefine.ADD_ITEM_CHINAJOY_VIP )
		
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
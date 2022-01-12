# -*- coding: gb18030 -*-

"""
This module implements the ShoppingBag for client only.
购物车模块 for client only
"""
# $Id: ShoppingBag.py,v 1.18 2008-05-07 02:57:32 yangkai Exp $

from ItemSystemExp import EquipQualityExp
import config.client.labels.ShoppingBag as lbDatas

class ShoppingBag:
	class ShoppingBagIter:
		"""
		ShoppingBag's iterator
		"""
		def __init__( self, obj ):
			self._iter1 = obj._srcOrders.__iter__()
			self._iter2 = obj._items.__iter__()

		def __iter__( self ):
			return self

		def next( self ):
			return self._iter1.next(), self._iter2.next()		# srcOrder, instance of item
	### end of iterator ###

	def __init__( self, space ):
		"""
		@param space: 购物车可放置物品数量
		"""
		self._items = [None] * space
		self._srcOrders = [None] * space

	def __iter__( self ):
		return ShoppingBag.ShoppingBagIter( self )

	def __getitem__( self, index ):
		return ( self._srcOrders[index], self._items[index] )	# srcOrder, instance of item

	def __len__( self ):
		return self.getSpaces()

	def getItem( self, index ):
		return self._items[index]

	def getSrcOrder( self, index ):
		return self._srcOrders[index]

	def getSpaces( self ):
		return len( self._items )

	def getUsedSpaces( self ):
		"""
		@return: 返回已使用的空间个数
		"""
		i = 0
		for e in self._items:
			if e is not None:
				i += 1
		return i

	def getInfo( self, order, owner ):
		"""
		取得描述

		@param order: 购物车位置
		@param owner: 购物车的拥有者，一般都是BigWorld.player()
		"""
		if order > len( self._items ):
			return ""

		item = self._items[order]
		if item is None:
			return ""

		return item.description( owner )

	def getPrices( self ):
		"""
		取得总价格
		"""
		prices = 0
		for item in self._items:
			if item is not None:
				prices += item.getPrice() * item.getAmount()
		return prices

	def getFreeOrder( self ):
		"""
		获取第一个空白位置

		@return: INT, 如果没有空闲的位置则返回-1，否则返回相应的位置
		"""
		for order, item in enumerate( self._items ):
			if item is None:
				return order
		return -1

	def _changeAmountWithSrcOrder( self, srcOrder, amount ):
		"""
		改变购物车的某个标志相关的物品的数量

		@return: 如果修改成功则返回被修改的位置，否则返回-1
		"""
		for index, order in enumerate( self._srcOrders ):
			if order == srcOrder:
				item = self._items[index]
				if item.getStackable() >= item.getAmount() + amount:
					item.setAmount( item.getAmount() + amount )
					return index
		return -1

	def clear( self ):
		"""
		清空购物车
		"""
		space = self.getSpaces()
		self._items = [None] * space
		self._srcOrders = [None] * space

	def add( self, srcOrder, item ):
		"""
		加入一个商品

		@param srcOrder: 商品的原始位置
		@param  invoice: 物品实例
		@return: INT, 如果成功加入，则返回商品在购物车中的具体位置，如果失败(装不下了)则返回-1
		"""
		order = self._changeAmountWithSrcOrder( srcOrder, item.getAmount() )
		if order > -1:
			# 购物车中存在同类物品，且能够叠加新的数量
			# 这时我们只要直接返回位置即可
			return order

		# 购物车中不存在同类物品或同类物品无法容叠加更多的数量
		# 我们需要直接把item加入到购物车中（如果购物车还有空间）
		order = self.getFreeOrder()
		if order > -1:
			self._srcOrders[order] = srcOrder
			self._items[order] = item
		return order

	def remove( self, order, amount, notifyFunc ):
		"""
		从购物车里删除一件商品

		@param  notifyFunc: 成功后购物车现在的物品摆放情况通知函数；
		                    此函数有两个参数，第一个为购物车位置(order)，
		                    第二个参数为该位置当前放的物品实例引用，如果物品不存在则为None。
		@param  order: 商品在购物车的位置
		@type   order: INT
		@param amount: 移除数量
		@type  amount: INT
		@return: INT; 如果物品被正确移去则返回被移动的物品的原始位置(srcOrder)，否则返回负值表示失败。
		"""
		if order < 0 or order > self.getSpaces():
			return -1

		item = self._items[order]
		if item is None:
			return -1

		if item.getAmount() < amount:
			return -1

		item.setAmount( item.getAmount() - amount )
		srcOrder = self._srcOrders[order]
		if item.getAmount() == 0:
			self._items.pop( order )
			self._srcOrders.pop( order )
			self._items.append( None )
			self._srcOrders.append( None )

		for index in xrange( order, self.getSpaces() ):
			item = self._items[index]
			notifyFunc( index, item )

		return srcOrder

### end of class ShoppingBag ###


class Buybag( ShoppingBag ):
	"""
	玩家从商人处买入商品的购物车
	"""
	def __init__( self, space ):
		"""
		@param space: 该售物车最多能装几个物品
		@type  space: int
		"""
		ShoppingBag.__init__( self, space )

class Sellbag( ShoppingBag ):
	"""
	玩家卖道具给商人的售物车
	"""
	def __init__( self, space ):
		"""
		@param space: 该售物车最多能装几个物品
		@type  space: int
		"""
		ShoppingBag.__init__( self, space )

class RepairBag( ShoppingBag ):
	"""
	玩家修理装备给商人的修改车
	"""
	def __init__( self, space ):
		"""
		@param space: 该售物车最多能装几个物品
		@type  space: int
		"""
		ShoppingBag.__init__( self, space )

	def _calcuRepairEquipMoney( self, equip, invBuyPercent ):
		"""
		计算修改一个装备的价格
		@param    equip: 装备数据
		@type     equip: instance

		@return: 价格
		"""
		repairCostRate = 1
		repairRate = EquipQualityExp.instance().getRepairRateByQuality( equip.getQuality() )
		# 修理费用 = 品质系数*（1-（实际耐久度/原始最大耐久度））*道具价格 ，用去掉小数＋1的方法取整。
		repairMoney = repairRate * ( 1- float( equip.getHardiness() ) / float( equip.getHardinessLimit() ) ) * equip.getRecodePrice() * repairCostRate
		iMoney = int( repairMoney )
		if iMoney != repairMoney:
			repairMoney = iMoney + 1
		return repairMoney

	def getPrices( self, invBuyPercent ):
		"""
		取得总价格

		@param    invBuyPercent: 贩卖百分比
		@type     invBuyPercent: float
		"""
		prices = 0
		for item in self._items:
			if item is not None and item.query("eq_hardiness") < item.query( "eq_hardinessMax" ):
				prices += self._calcuRepairEquipMoney( item, invBuyPercent )
		return prices

	def getInfo( self, order, owner, invBuyPercent ):
		"""
		取得描述

		@param order: 购物车位置
		@param owner: 购物车的拥有者，一般都是BigWorld.player()
		@param invBuyPercent: 商品百分比
		"""
		if order > len( self._items ):
			return ""

		item = self._items[order]
		if item is None:
			return ""

		msg = item.description( owner )
		msg.append( lbDatas.REPAIRCOST + str( self._calcuRepairEquipMoney( item, invBuyPercent ) ))
		return msg


### end of class Sellbag ###

# $Log: not supported by cvs2svn $
# Revision 1.17  2007/11/24 03:09:25  yangkai
# 物品系统调整，属性更名
# 当前耐久度"endure" -- > "eq_hadriness"
# 最大耐久度"currEndureLimit" --> "eq_hardinessLimit"
# 最大耐久度上限"maxEndureLimit" --> "eq_hardinessMax"
#
# Revision 1.16  2007/08/15 07:59:08  yangkai
# 装备属性"maxEndure" -- > "currEndureLimit"
#
# Revision 1.15  2007/01/15 01:45:27  panguankong
# 修改了修理计费公式
#
# Revision 1.14  2007/01/08 09:37:08  panguankong
# 添加了修理装备BAG
#
# Revision 1.13  2006/08/11 07:38:50  phw
# no message
#
# Revision 1.12  2006/07/22 04:46:15  phw
# 修改(正)接口:
# 	ShoppingBagIter.__init__()
# 	getUsedSpaces()
# 	getInfo()
# 	remove()
#
# Revision 1.11  2006/07/21 10:46:37  phw
# 加入接口：__len__()
# 修正接口：
# 	getPrices()；修正了价格取值不对的问题
# 	_changeAmountWithSrcOrder()
#
# Revision 1.10  2006/07/21 07:59:11  phw
# 修正调用不存在的方法
# from: order = self.getFreeSpace()
# to:   order = self.getFreeOrder()
#
# Revision 1.9  2006/07/19 10:03:10  phw
# 增加getUsedSpaces()方法
#
# Revision 1.8  2006/07/17 10:16:25  phw
# 重写了ShoppingBag模块，使其功能更明确；用于GUIFacade.MerchantFacade模块
#
# Revision 1.7  2005/09/20 09:13:52  phw
# no message
#
# Revision 1.6  2005/04/29 02:11:53  phw
# 这个模块由于原来考虑不够，估计得作废，将来必须重写
#
# Revision 1.5  2005/03/29 09:19:46  phw
# 修改了注释，使其符合epydoc的要求
#
# Revision 1.4  2005/03/07 13:47:05  phw
# no message
#
# Revision 1.3  2005/02/25 03:31:04  phw
# no message

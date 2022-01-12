# -*- coding: gb18030 -*-

"""
This module implements the ChapmanBase for client.

"""
# $Id: ChapmanBase.py,v 1.8 2005-03-29 09:19:53 phw Exp $

import BigWorld
import InvoicesPackType
import bwdebug
import ShoppingBag

class ChapmanBase:
	"""
	An ChapmanBase class for client.
	这个类是作为基础类存在，给其它的类派生用。

	@ivar      attrInvoices: 货物列表
	@type      attrInvoices: INVOICEITEMS
	@ivar   attrSellPercent: 出售价格百份比，例如：1.0表示原价，0.5表示半价，2.0表示双倍价格等，更新由服务器通知
	@type   attrSellPercent: float
	@ivar    attrBuyPercent: 回收价格百分比，例如：1.0表示原价，0.5表示半价，2.0表示双倍价格等，更新由服务器通知
	@type    attrBuyPercent: float
	@ivar	   attrDistance: 距离判断，确定用户必须在离NPC多远的情况下才能交易，单位：米，更新由服务器通知
	@type      attrDistance: float
	"""

	def __init__( self ):
		self.attrInvoices = None
		pass

	def getInvoiceListCallback( self, argInvoiceList ):
		"""
		给cell的回调函数，由cell告诉商人NPC，现在的商品列表，整个全部重新更新一次

		@param argInvoiceList: 商品列表，如果需要做些什么的如更新client界面，可以在此函数上加代码
		@type  argInvoiceList: INVOICEITEMS
		@return:               无
		"""
		self.attrInvoices = argInvoiceList


	def sellToCallback( self, argSellList ):
		"""
		给cell的回调函数，指出玩家所请求要购买的商品里买了哪几种，全部买齐的商品不会出现在列表里

		@param argSellList: 没有全部买下的商品列表,[偶数位置]表示商品uid，[奇数位置]表示已购买的数量
		@type  argSellList: ARRAY of UINT16
		@return:            无
		"""
		if len( argSellList ) == 0:
			return

		for e in xrange( 0, len( argSellList ), 2 ):
			invoiceData = self.attrInvoices[argSellList[e]]
			invoiceData.setAmount( 0 )
			print "%s(%i) buy %i only." % ( invoiceData.getName(), argSellList[e], argSellList[e+1] )
	### end of buyFromCallback() method ###

	def buyFromCallback( self, argState ):
		"""
		给cell的回调函数，指出玩家卖物品给NPC的结果

		@param argState: 1 表示成功出售，0 表示失败
		@type  argState: bool
		@return: 无
		"""
		if argState:
			print "buy success."
		else:
			print "buy fail"
	### end of buyFromCallback() method ###

	def getInvoices( self ):
		"""
		给 gui 的接口，获得商品列表

		@return: 商品列表
		@rtype:  INVOICEITEMS
		"""
		return self.attrInvoices

	# 注：onTargetClick方法是每个商人的事情，不是商人基础类的事情，因此该类里没有此方法
	#def onTargetClick( self, player, position ):
	#	# 交易
	#	#if srcEntity.是红名():
	#	#	return
	#
	#	### 临时商的判断可能没用，据说临时商人是个技能，那就不需要这种判断，但暂时先放着
	#	#if self.是临时商人():
	#	#	if srcEntity.没有召唤临时商人技能():
	#	#		return
	#
	#	pos = position - self.position
	#	distance = abs( math.sqrt(pos.x * pos.x + pos.z * pos.z) )
	#	if distance < attrDistance:
	#		self.cell.sendInvoiceListToClient()
	#	### end of onTargetClient() ###

### end of class ChapmanBase() ###

# $Log: not supported by cvs2svn $


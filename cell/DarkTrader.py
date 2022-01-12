# -*- coding: gb18030 -*-
#
# 2008-12-26 SongPeifang
#
"""
DarkTrader类
"""

from bwdebug import *
from Merchant import Merchant
import ECBExtend
import random

GOOD_AMOUNTS = 8 # 黑市商人的总商品数量

class DarkTrader( Merchant ):
	"""
	投机商人类
	"""
	def __init__( self ):
		Merchant.__init__( self )
		self.currentGoodID = 0
		self.invBuyPercent = random.randint( 160,200 ) / 100.0			# 收购价格在原价的160%-200%
		self.currentBuyPercent = self.invBuyPercent
		self.addTimer( 600, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )		# 该投机商人存在15分钟后消失

	def receiveCurrntCollectGoodID( self, itemID ):
		"""
		Define Method.
		获取投机商人当前出售的物品ID
		"""
		self.currentGoodID = itemID
		self.resetDarkAttrInvoices()

	def resetDarkAttrInvoices( self ):
		"""
		从出售列表中删除掉投机商人当前收购的物品
		"""
		totID = 1
		tempDict = {}
		for totKey in self.attrInvoices:

			tmpInvData = self.attrInvoices[totKey]
			if tmpInvData.srcItem is None:
				ERROR_MSG( "No such item.Error occured in function resetDarkAttrInvoices" )
				continue
			if tmpInvData.srcItem.id != self.currentGoodID:
				# 从出售列表中T掉收购的物品
				tempDict[ totID ] = tmpInvData
				totID += 1
		self.attrInvoices.update( tempDict )
		if self.attrInvoices.has_key( GOOD_AMOUNTS ):
			self.attrInvoices.pop( GOOD_AMOUNTS )
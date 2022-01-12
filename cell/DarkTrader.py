# -*- coding: gb18030 -*-
#
# 2008-12-26 SongPeifang
#
"""
DarkTrader��
"""

from bwdebug import *
from Merchant import Merchant
import ECBExtend
import random

GOOD_AMOUNTS = 8 # �������˵�����Ʒ����

class DarkTrader( Merchant ):
	"""
	Ͷ��������
	"""
	def __init__( self ):
		Merchant.__init__( self )
		self.currentGoodID = 0
		self.invBuyPercent = random.randint( 160,200 ) / 100.0			# �չ��۸���ԭ�۵�160%-200%
		self.currentBuyPercent = self.invBuyPercent
		self.addTimer( 600, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )		# ��Ͷ�����˴���15���Ӻ���ʧ

	def receiveCurrntCollectGoodID( self, itemID ):
		"""
		Define Method.
		��ȡͶ�����˵�ǰ���۵���ƷID
		"""
		self.currentGoodID = itemID
		self.resetDarkAttrInvoices()

	def resetDarkAttrInvoices( self ):
		"""
		�ӳ����б���ɾ����Ͷ�����˵�ǰ�չ�����Ʒ
		"""
		totID = 1
		tempDict = {}
		for totKey in self.attrInvoices:

			tmpInvData = self.attrInvoices[totKey]
			if tmpInvData.srcItem is None:
				ERROR_MSG( "No such item.Error occured in function resetDarkAttrInvoices" )
				continue
			if tmpInvData.srcItem.id != self.currentGoodID:
				# �ӳ����б���T���չ�����Ʒ
				tempDict[ totID ] = tmpInvData
				totID += 1
		self.attrInvoices.update( tempDict )
		if self.attrInvoices.has_key( GOOD_AMOUNTS ):
			self.attrInvoices.pop( GOOD_AMOUNTS )
# -*- coding: gb18030 -*-

"""This module implements the Chapman for client.

@requires: L{ChapmanBase<ChapmanBase>}, L{Role<Role>}
"""
# $Id: Chapman.py,v 1.36 2008-08-11 02:40:55 huangyongwei Exp $

import BigWorld
from bwdebug import *
import InvoicesPackType
import NPC
import Math
import math
import GUI
import GUIFacade

from utils import *

TIME_TO_GET_INVOICE = 0.5
def priceCarry( price ):
	"""
	2008-11-4 11:42 yk
	�߻������ǣ������ǮС��1������1
	�������1����ȡ��
	"""
	if price < 1:
		return 1
	return int( price )

class Chapman( NPC.NPC ):
	"""An Chapman class for client.
	����NPC

	@ivar      attrInvoices: �����б�
	@type      attrInvoices: INVOICEITEMS
	@ivar    invSellPercent: ���ۼ۸�ٷݱȣ����磺1.0��ʾԭ�ۣ�0.5��ʾ��ۣ�2.0��ʾ˫���۸�ȣ������ɷ�����֪ͨ
	@type    invSellPercent: float
	@ivar    invBuyPercent: ���ռ۸�ٷֱȣ����磺1.0��ʾԭ�ۣ�0.5��ʾ��ۣ�2.0��ʾ˫���۸�ȣ������ɷ�����֪ͨ
	@type    invBuyPercent: float
	"""

	def __init__( self ):
		NPC.NPC.__init__( self )
		self.invoiceIndexList = []
		self.__invoiceCount = 0				# ��Ʒ����( hyw -- 2008.09.16 )
		#self.attrInvoices = InvoicesPackType.instance.defaultValue()

	def enterWorld( self ) :
		NPC.NPC.enterWorld( self )

	def leaveWorld( self ) :
		self.__invoiceCount = 0				# �����Ʒ����( hyw -- 2008.09.16 )
		NPC.NPC.leaveWorld( self )

	def addInvoiceCB( self, argUid, argInvoice ):
		"""
		����һ����Ʒ

		@param  argUid: ����Ʒ��Ψһ��ʶ��
		@type   argUid: UINT16
		@param argInvoice: InvoiceDataType���͵���Ʒʵ��
		@type  argInvoice: class instance
		"""
		item = argInvoice.getSrcItem()
		if item is None: return
		item.set( "price", priceCarry( item.getPrice() * self.invSellPercent ) )		# �����¼۸�
		item.set( "invoiceType", argInvoice.getItemType() )								# ��Ʒ��ʹ�ö���ֵ����hyw--08.08.11��
		item.setAmount( argInvoice.getAmount() )
		argInvoice.uid = argUid														# ��¼Ψһ��ʶ
		#self.attrInvoices[argUid] = argInvoice
		GUIFacade.onInvoiceAdded( self.id, argInvoice )

		if argUid == self.__invoiceCount :											# ��ʾ������ϣ�hyw--2008.06.16��
			self.__invoiceCount = 0

	def resetInvoices( self, space ):
		"""
		�����Ʒ�б�

		@param space: ���˵���Ʒ����
		@type  space: INT8
		"""
		#self.attrInvoices.clear()
		GUIFacade.onResetInvoices( space )

	def onBuyArrayFromCB( self, state ):
		"""
		������Ʒ���ջص�

		@param state: ����״̬��1 = �ɹ��� 0 = ʧ��
		@type  state: UINT8
		@return: ��
		"""
		#INFO_MSG( "state = %i" % state )
		GUIFacade.onSellToNPCReply( state )

	def onInvoiceLengthReceive( self, length ):
		"""
		define method
		�����Ʒ�б���
		"""
		GUIFacade.setInvoiceAmount( length )
		self.invoiceIndexList = range( 1, length + 1, 1 )
		self.__invoiceCount = length						# ������Ʒ��������hyw -- 2008.09.16��
		if length == 0:
			return
		self.requestInvoice()

	def requestInvoice( self ):
		"""
		���һ����Ʒ�б�
		"""
		length = len( self.invoiceIndexList )
		if length > 0:
			self.cell.requestInvoice( self.invoiceIndexList[0] ) #����һ����Ʒ�б� ��ʱ�� 14��
		if length > 14:
			self.invoiceIndexList = self.invoiceIndexList[14:]
			BigWorld.callback( TIME_TO_GET_INVOICE, self.requestInvoice )
		else:
			self.invoiceIndexList = []

	def isRequesting( self ) :
		"""
		�Ƿ�����������Ʒ�б�
		hyw -- 2008.09.16
		"""
		return self.__invoiceCount > 0

# end of class Chapman #


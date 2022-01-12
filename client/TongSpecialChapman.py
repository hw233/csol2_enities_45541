# -*- coding: gb18030 -*-
#
# $Id: TongSpecialChapman.py

"""
Chapman����
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
import GUIFacade
from Chapman import Chapman

class TongSpecialChapman( Chapman ):
	"""
	����������NPC����
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		Chapman.__init__( self )
		self.invoiceIndexList = []
		self.__invoiceCount = 0				# ��Ʒ����( hyw -- 2008.09.16 )

	def enterWorld( self ) :
		Chapman.enterWorld( self )

	def leaveWorld( self ) :
		Chapman.leaveWorld( self )

	def addInvoiceCB( self, argUid, argInvoice ):
		"""
		����һ����Ʒ

		@param  argUid: ����Ʒ��Ψһ��ʶ��
		@type   argUid: UINT16
		@param argInvoice: InvoiceDataType���͵���Ʒʵ��
		@type  argInvoice: class instance
		"""
		item = argInvoice.getSrcItem()
		argInvoice.uid = argUid													# ��¼Ψһ��ʶ
		item.set( "invoiceType", argInvoice.getItemType() )
		item.setAmount( argInvoice.getAmount() )
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

	def onReceivePriceChangeInfo( self, priceChangeInfo ):
		"""
		���յ����������͹����ļ۸�䶯��Ϣ
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_PRICE_CHANGE_INFO", priceChangeInfo )

	def onReceiveGoodsAmountChange( self, index, currAmount ):
		"""
		���ܵ���������Ʒ�����ı�֪ͨ

		@param	uid:		��ƷID
		@type	uid:		UINT16
		@param	currAmount:	��Ʒʣ������
		@param	currAmount:	UINT16
		"""
		GUIFacade.updateInvoiceAmount( index, currAmount )

	def onReceiveSpecialItems( self, itemDatas ):
		"""
		������Ʒ����
		"""
		pass
	
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
	���������Ϊ��������ڣ����������������á�

	@ivar      attrInvoices: �����б�
	@type      attrInvoices: INVOICEITEMS
	@ivar   attrSellPercent: ���ۼ۸�ٷݱȣ����磺1.0��ʾԭ�ۣ�0.5��ʾ��ۣ�2.0��ʾ˫���۸�ȣ������ɷ�����֪ͨ
	@type   attrSellPercent: float
	@ivar    attrBuyPercent: ���ռ۸�ٷֱȣ����磺1.0��ʾԭ�ۣ�0.5��ʾ��ۣ�2.0��ʾ˫���۸�ȣ������ɷ�����֪ͨ
	@type    attrBuyPercent: float
	@ivar	   attrDistance: �����жϣ�ȷ���û���������NPC��Զ������²��ܽ��ף���λ���ף������ɷ�����֪ͨ
	@type      attrDistance: float
	"""

	def __init__( self ):
		self.attrInvoices = None
		pass

	def getInvoiceListCallback( self, argInvoiceList ):
		"""
		��cell�Ļص���������cell��������NPC�����ڵ���Ʒ�б�����ȫ�����¸���һ��

		@param argInvoiceList: ��Ʒ�б������Ҫ��Щʲô�������client���棬�����ڴ˺����ϼӴ���
		@type  argInvoiceList: INVOICEITEMS
		@return:               ��
		"""
		self.attrInvoices = argInvoiceList


	def sellToCallback( self, argSellList ):
		"""
		��cell�Ļص�������ָ�����������Ҫ�������Ʒ�������ļ��֣�ȫ���������Ʒ����������б���

		@param argSellList: û��ȫ�����µ���Ʒ�б�,[ż��λ��]��ʾ��Ʒuid��[����λ��]��ʾ�ѹ��������
		@type  argSellList: ARRAY of UINT16
		@return:            ��
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
		��cell�Ļص�������ָ���������Ʒ��NPC�Ľ��

		@param argState: 1 ��ʾ�ɹ����ۣ�0 ��ʾʧ��
		@type  argState: bool
		@return: ��
		"""
		if argState:
			print "buy success."
		else:
			print "buy fail"
	### end of buyFromCallback() method ###

	def getInvoices( self ):
		"""
		�� gui �Ľӿڣ������Ʒ�б�

		@return: ��Ʒ�б�
		@rtype:  INVOICEITEMS
		"""
		return self.attrInvoices

	# ע��onTargetClick������ÿ�����˵����飬�������˻���������飬��˸�����û�д˷���
	#def onTargetClick( self, player, position ):
	#	# ����
	#	#if srcEntity.�Ǻ���():
	#	#	return
	#
	#	### ��ʱ�̵��жϿ���û�ã���˵��ʱ�����Ǹ����ܣ��ǾͲ���Ҫ�����жϣ�����ʱ�ȷ���
	#	#if self.����ʱ����():
	#	#	if srcEntity.û���ٻ���ʱ���˼���():
	#	#		return
	#
	#	pos = position - self.position
	#	distance = abs( math.sqrt(pos.x * pos.x + pos.z * pos.z) )
	#	if distance < attrDistance:
	#		self.cell.sendInvoiceListToClient()
	#	### end of onTargetClient() ###

### end of class ChapmanBase() ###

# $Log: not supported by cvs2svn $


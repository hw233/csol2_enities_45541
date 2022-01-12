# -*- coding: gb18030 -*-

"""
This module implements the ShoppingBag for client only.
���ﳵģ�� for client only
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
		@param space: ���ﳵ�ɷ�����Ʒ����
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
		@return: ������ʹ�õĿռ����
		"""
		i = 0
		for e in self._items:
			if e is not None:
				i += 1
		return i

	def getInfo( self, order, owner ):
		"""
		ȡ������

		@param order: ���ﳵλ��
		@param owner: ���ﳵ��ӵ���ߣ�һ�㶼��BigWorld.player()
		"""
		if order > len( self._items ):
			return ""

		item = self._items[order]
		if item is None:
			return ""

		return item.description( owner )

	def getPrices( self ):
		"""
		ȡ���ܼ۸�
		"""
		prices = 0
		for item in self._items:
			if item is not None:
				prices += item.getPrice() * item.getAmount()
		return prices

	def getFreeOrder( self ):
		"""
		��ȡ��һ���հ�λ��

		@return: INT, ���û�п��е�λ���򷵻�-1�����򷵻���Ӧ��λ��
		"""
		for order, item in enumerate( self._items ):
			if item is None:
				return order
		return -1

	def _changeAmountWithSrcOrder( self, srcOrder, amount ):
		"""
		�ı乺�ﳵ��ĳ����־��ص���Ʒ������

		@return: ����޸ĳɹ��򷵻ر��޸ĵ�λ�ã����򷵻�-1
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
		��չ��ﳵ
		"""
		space = self.getSpaces()
		self._items = [None] * space
		self._srcOrders = [None] * space

	def add( self, srcOrder, item ):
		"""
		����һ����Ʒ

		@param srcOrder: ��Ʒ��ԭʼλ��
		@param  invoice: ��Ʒʵ��
		@return: INT, ����ɹ����룬�򷵻���Ʒ�ڹ��ﳵ�еľ���λ�ã����ʧ��(װ������)�򷵻�-1
		"""
		order = self._changeAmountWithSrcOrder( srcOrder, item.getAmount() )
		if order > -1:
			# ���ﳵ�д���ͬ����Ʒ�����ܹ������µ�����
			# ��ʱ����ֻҪֱ�ӷ���λ�ü���
			return order

		# ���ﳵ�в�����ͬ����Ʒ��ͬ����Ʒ�޷��ݵ��Ӹ��������
		# ������Ҫֱ�Ӱ�item���뵽���ﳵ�У�������ﳵ���пռ䣩
		order = self.getFreeOrder()
		if order > -1:
			self._srcOrders[order] = srcOrder
			self._items[order] = item
		return order

	def remove( self, order, amount, notifyFunc ):
		"""
		�ӹ��ﳵ��ɾ��һ����Ʒ

		@param  notifyFunc: �ɹ����ﳵ���ڵ���Ʒ�ڷ����֪ͨ������
		                    �˺�����������������һ��Ϊ���ﳵλ��(order)��
		                    �ڶ�������Ϊ��λ�õ�ǰ�ŵ���Ʒʵ�����ã������Ʒ��������ΪNone��
		@param  order: ��Ʒ�ڹ��ﳵ��λ��
		@type   order: INT
		@param amount: �Ƴ�����
		@type  amount: INT
		@return: INT; �����Ʒ����ȷ��ȥ�򷵻ر��ƶ�����Ʒ��ԭʼλ��(srcOrder)�����򷵻ظ�ֵ��ʾʧ�ܡ�
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
	��Ҵ����˴�������Ʒ�Ĺ��ﳵ
	"""
	def __init__( self, space ):
		"""
		@param space: �����ﳵ�����װ������Ʒ
		@type  space: int
		"""
		ShoppingBag.__init__( self, space )

class Sellbag( ShoppingBag ):
	"""
	��������߸����˵����ﳵ
	"""
	def __init__( self, space ):
		"""
		@param space: �����ﳵ�����װ������Ʒ
		@type  space: int
		"""
		ShoppingBag.__init__( self, space )

class RepairBag( ShoppingBag ):
	"""
	�������װ�������˵��޸ĳ�
	"""
	def __init__( self, space ):
		"""
		@param space: �����ﳵ�����װ������Ʒ
		@type  space: int
		"""
		ShoppingBag.__init__( self, space )

	def _calcuRepairEquipMoney( self, equip, invBuyPercent ):
		"""
		�����޸�һ��װ���ļ۸�
		@param    equip: װ������
		@type     equip: instance

		@return: �۸�
		"""
		repairCostRate = 1
		repairRate = EquipQualityExp.instance().getRepairRateByQuality( equip.getQuality() )
		# ������� = Ʒ��ϵ��*��1-��ʵ���;ö�/ԭʼ����;öȣ���*���߼۸� ����ȥ��С����1�ķ���ȡ����
		repairMoney = repairRate * ( 1- float( equip.getHardiness() ) / float( equip.getHardinessLimit() ) ) * equip.getRecodePrice() * repairCostRate
		iMoney = int( repairMoney )
		if iMoney != repairMoney:
			repairMoney = iMoney + 1
		return repairMoney

	def getPrices( self, invBuyPercent ):
		"""
		ȡ���ܼ۸�

		@param    invBuyPercent: �����ٷֱ�
		@type     invBuyPercent: float
		"""
		prices = 0
		for item in self._items:
			if item is not None and item.query("eq_hardiness") < item.query( "eq_hardinessMax" ):
				prices += self._calcuRepairEquipMoney( item, invBuyPercent )
		return prices

	def getInfo( self, order, owner, invBuyPercent ):
		"""
		ȡ������

		@param order: ���ﳵλ��
		@param owner: ���ﳵ��ӵ���ߣ�һ�㶼��BigWorld.player()
		@param invBuyPercent: ��Ʒ�ٷֱ�
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
# ��Ʒϵͳ���������Ը���
# ��ǰ�;ö�"endure" -- > "eq_hadriness"
# ����;ö�"currEndureLimit" --> "eq_hardinessLimit"
# ����;ö�����"maxEndureLimit" --> "eq_hardinessMax"
#
# Revision 1.16  2007/08/15 07:59:08  yangkai
# װ������"maxEndure" -- > "currEndureLimit"
#
# Revision 1.15  2007/01/15 01:45:27  panguankong
# �޸�������Ʒѹ�ʽ
#
# Revision 1.14  2007/01/08 09:37:08  panguankong
# ���������װ��BAG
#
# Revision 1.13  2006/08/11 07:38:50  phw
# no message
#
# Revision 1.12  2006/07/22 04:46:15  phw
# �޸�(��)�ӿ�:
# 	ShoppingBagIter.__init__()
# 	getUsedSpaces()
# 	getInfo()
# 	remove()
#
# Revision 1.11  2006/07/21 10:46:37  phw
# ����ӿڣ�__len__()
# �����ӿڣ�
# 	getPrices()�������˼۸�ȡֵ���Ե�����
# 	_changeAmountWithSrcOrder()
#
# Revision 1.10  2006/07/21 07:59:11  phw
# �������ò����ڵķ���
# from: order = self.getFreeSpace()
# to:   order = self.getFreeOrder()
#
# Revision 1.9  2006/07/19 10:03:10  phw
# ����getUsedSpaces()����
#
# Revision 1.8  2006/07/17 10:16:25  phw
# ��д��ShoppingBagģ�飬ʹ�书�ܸ���ȷ������GUIFacade.MerchantFacadeģ��
#
# Revision 1.7  2005/09/20 09:13:52  phw
# no message
#
# Revision 1.6  2005/04/29 02:11:53  phw
# ���ģ������ԭ�����ǲ��������Ƶ����ϣ�����������д
#
# Revision 1.5  2005/03/29 09:19:46  phw
# �޸���ע�ͣ�ʹ�����epydoc��Ҫ��
#
# Revision 1.4  2005/03/07 13:47:05  phw
# no message
#
# Revision 1.3  2005/02/25 03:31:04  phw
# no message

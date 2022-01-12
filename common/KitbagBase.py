# -*- coding: gb18030 -*-

"""
����������
"""

# $Id: KitbagBase.py,v 1.40 2008-08-09 03:40:13 phw Exp $

from bwdebug import *
import ItemTypeImpl

class KitbagBase:
	"""
	���������࣬�Ե���ʵ�����д�ţ��Զ������ͻ����ײ㲿��(����ͨѶ�����ݵı���)��

	@ivar   _dataList: key == order, value == instance of CItemBase or inherit it
	@type   _dataList: list
	@ivar _uid2order: key = INT64(uid), value = orderID
	@type _uid2order: dict
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		self._dataList    = {}				# key == order, value == instance of CItemBase or inherit it
		self._uid2order    = {}				# key = INT64(uid), value = orderID

	def __len__( self ):
		"""
		��õ�ǰ�����м�������

		@return: ��ǰ�������ɵĵ�������
		@rtype:  INT16
		"""
		return len( self._uid2order )

	def __getitem__( self, key ):
		return self._dataList.get( key )

	def hasUid( self, uid ):
		"""
		�ж�һ��uid�Ƿ����

		@param uid: Ԥ����uid
		@type  uid: UINT64
		@return:       ������True����������False
		@rtype:        BOOL
		"""
		return uid in self._uid2order

	def orderHasItem( self, orderID ):
		"""
		�ж�һ��λ�����Ƿ��Ѵ��ڵ���

		@param orderID: λ��
		@type  orderID: INT16
		@return:        True == ָ��λ���е��ߣ�False == ָ��λ��û�е���
		@rtype:         BOOL
		@raise IndexError: ���orderID���ڱ���������Χ����������쳣
		"""
		return orderID in self._dataList

	def iterDatas( self ):
		"""
		"""
		return self._dataList.itervalues()

	def getDatas( self ):
		"""
		��ô���ڱ����������ʵ���б�

		@return: [instance1, instance2, ...]
		@rtype:  list
		"""
		return self._dataList.values()

	def getDatasByRange( self, start = 0, end = -1 ):
		"""
		��ȡָ����Χ����Ʒ�б�

		@return: list as [instance1, ...]
		@rtype:  list of CItemBase
		"""
		if end <= 0:
			return [ e[1] for e in self._dataList.iteritems() if e[0] >= start ]
		else:
			return [ self._dataList[e] for e in xrange( start, end + 1 ) if e in self._dataList ]

	def getUid( self, orderID ):
		"""
		ͨ��orderID��ȡuid

		@param orderID: λ��
		@type  orderID: INT16
		@return:        big than 0 if uid is found, else return -1
		@rtype:         INT64
		"""
		try:
			return self._dataList[orderID].uid
		except KeyError:	# ֻ�������Ͳ��ԵĴ���
			return -1

	def getOrderID( self, uid ):
		"""
		ͨ��uid��ȡorderID

		@param uid: ����Ψһ�Եĵ���Я��ID
		@type  uid: UINT64
		@return:       if True return orderID, else return None
		@rtype:        INT16
		@raise KeyError: ���uid��������������쳣
		"""
		try:
			return self._uid2order[uid]
		except KeyError:
			return -1

	def getByUid( self, uid ):
		"""
		���ĳ���ߵ�ʵ��

		@param uid:   ���ߵ�ΨһID
		@type  uid:   INT64
		@return:         �ɹ��򷵻ص���ʵ�������򷵻�None
		@rtype:          ItemInstance/None
		"""
		try:
			return self.getByOrder( self._uid2order[uid] )
		except KeyError:
			return None

	def getByOrder( self, orderID ):
		"""
		���ĳ���ߵ�ʵ��

		@return:         �ɹ��򷵻ص���ʵ�������򷵻�None
		@rtype:          ItemInstance/None
		"""
		return self._dataList.get( orderID )

	def add( self, orderID, itemInstance ):
		"""
		��ĳ���ߵ�������ĳ��λ�á�

		@param      orderID: λ��
		@type       orderID: INT16
		@param itemInstance: �̳���CItemBase���Զ������͵���ʵ��
		@type  itemInstance: CItemBase
		@return:             �ɹ��򷵻�True�����򷵻�False��
		                     ʧ�������ֿ��ܣ�һ����uid�Ѵ��ڣ���һ����ָ����λ��(orderID)���Ѿ��ж���
		@rtype:              BOOL
		@note:               �÷�����������itemInstanceʵ��������ֱ������itemInstanceʵ��
		"""
		if self.orderHasItem( orderID ):
			return False
		if self.hasUid( itemInstance.uid ):
			return False
		self._uid2order[itemInstance.uid] = orderID
		self._dataList[orderID] = itemInstance
		itemInstance.setOrder( orderID )
		return True

	def removeByUid( self, uid ):
		"""
		��ĳ���ߴӱ�����ɾ��������

		@param uid: ���ߵ�ΨһID
		@type  uid: INT64
		@return:       BOOL
		@raise KeyError: ���uid������ͬ�������쳣
		"""
		return self.removeByOrder( self.getOrderID[uid] )

	def removeByOrder( self, orderID ):
		"""
		��ĳ���ߴӱ�����ɾ��������

		@param orderID: ����λ��
		@type  orderID: UINT8
		@return:        BOOL
		@raise IndexError: ���orderID���ڱ���������Χ����������쳣
		"""
		if not self.orderHasItem( orderID ): return False
		uid = self.getUid( orderID )
		itemInstance = self._dataList[orderID]
		del self._dataList[orderID]
		del self._uid2order[uid]
		itemInstance.setOrder( -1 )
		return True

	def removeByOrderU( self, orderID ):
		"""
		��ĳ���ߴӱ�����ɾ��������

		@param orderID: ����λ��
		@type  orderID: UINT8
		@return:        BOOL
		@raise IndexError: ���orderID���ڱ���������Χ����������쳣
		"""
		if not self.orderHasItem( orderID ): return False
		uid = self.getUid( orderID )
		itemInstance = self._dataList[orderID]
		del self._dataList[orderID]
		del self._uid2order[uid]
		itemInstance.setOrder( -1 )
		return True

	def swapOrder( self, srcOrder, dstOrder ):
		"""
		��������λ���ϵĵ���

		@param srcOrder: λ��1
		@type  srcOrder: UINT8
		@param dstOrder: λ��2
		@type  dstOrder: UINT8
		@return:       �ɹ�(True) or ʧ��(False)
		@rtype:        BOOL
		"""
		srcItem = self.getByOrder( srcOrder )
		dstItem = self.getByOrder( dstOrder )
		if srcItem is None:
			if dstItem is None:
				return False
			self.removeByOrder( dstOrder )
			self.add( srcOrder, dstItem )
		else:
			if dstItem is None:
				self.removeByOrder( srcOrder )
				self.add( dstOrder, srcItem )
			else:
				self.removeByOrder( dstOrder )
				self.removeByOrder( srcOrder )
				self.add( srcOrder, dstItem )
				self.add( dstOrder, srcItem )
		return True

	def getAllOrder( self ):
		"""
		��ȡ��ǰ����������Ʒ��order
		"""
		return self._dataList.iterkeys()
	
# $Log: not supported by cvs2svn $
# Revision 1.39  2008/06/10 08:59:44  huangyongwei
# ȥ���ˣ�
# < 			print "11111111111111111"
#
# 160d158
# < 			print "2222222222222222"
#
# Revision 1.38  2008/05/30 02:59:22  yangkai
# װ��������
#
# Revision 1.37  2008/04/08 06:00:54  yangkai
# ���� findAll
#
# Revision 1.36  2008/04/03 06:28:20  phw
# method rename: find2All() -> find(), findAll2All() -> findAll()
# itemKeyName -> itemID
# return value type modified: find(), findAll()
#
# Revision 1.35  2007/12/14 07:11:23  wangshufeng
# method modify:canSwapOrder,�����Ʒ�����ᣬ��ֹ���ƶ���
# method modify:swapTo,�����Ʒ�����ᣬ��ֹ���ƶ���
#
# Revision 1.34  2007/11/28 02:12:57  yangkai
# �Ƴ������õ� from ItemTypeEnum import *
#
# Revision 1.33  2007/11/27 08:03:29  yangkai
# no message
#
# Revision 1.32  2007/11/24 03:18:51  yangkai
# ��Ʒϵͳ���������Ը���
# "maxSpace" --> "kb_maxSpace"
#
# Revision 1.31  2007/11/08 09:41:16  phw
# self.freeze -> self.freezeState
# �������������뷽����ͬ����bug
#
# Revision 1.30  2007/11/08 06:26:49  yangkai
# ���ӽӿ� updateSrcClass()���ڸ��±�����Դ��Ʒ����
#
# Revision 1.29  2007/10/25 04:22:28  phw
# method removed: popByOrder(), popByTote()
# method added: isFrozen(), freeze(), unfreeze()����������һ���ڱ������еı���������״̬���˹��ܵ�ǰ�������Ҫ�����ڰѿձ���ֱ�Ӵӱ�������ȡ�����ŵ������е��첽���������ݰ�ȫ���ϡ�
# �޸��˱����е���Ʒ���ӡ�ɾ���������Ľӿڣ������˶�����״̬���ж�
#
# Revision 1.28  2007/04/06 09:35:41  huangyongwei
# �� getFreeOrder �����У�����������������
# ��ʾ���ҵ���ʼ�ͽ���λ��
#
# Revision 1.27  2007/03/12 02:31:05  kebiao
# �޸�����Ʒ�뿪һ������ʱû�м�ʱɾ����һ��BUG
# removeByOrder
#
# Revision 1.26  2006/09/21 01:18:00  phw
# add new method: findByType();
#
# Revision 1.25  2006/09/19 03:17:15  huangyongwei
# ����˻�ȡͬ ID ��Ʒ������ getByID����
#
# Revision 1.24  2006/08/11 02:45:13  phw
# �ӿ��������ģ�
#     from: def onInto( self, owner, order, itemInstance )
#     to:   def onInto( self, owner, itemInstance )
#     from: def onLeave( self, owner, order, itemInstance ):
#     to:   def onLeave( self, owner, itemInstance ):
# �޸Ľӿڣ�
#     _add(); ���¼������Ʒ��������kitbag��order��toteID���룬ԭonInto()��ͬ����ɾ��
#     removeByOrder(); ���Ƴ�ȥ����Ʒ��������kitbag��order��toteID����(�ָ�Ϊû������λ��״̬)��ԭonLeave()��ͬ����ɾ��
# ���Ը������޸�����itemInstance.keyName��itemInstance.id()ΪitemInstance.id
#
# Revision 1.23  2006/08/09 08:26:20  phw
# ����"kitName"����Ϊ"srcID"
#
# Revision 1.22  2006/08/05 07:59:13  phw
# �޸Ľӿڣ�onInit()
#     from: self.setMaxSpace( srcClass.maxSpace )
#     to:   self.setMaxSpace( srcClass.query( "maxSpace" ) )
#
# Revision 1.21  2006/05/26 10:21:59  phw
# no message
#
# Revision 1.20  2005/11/07 05:57:21  phw
# ��onLevel()���÷���ɾ����Ʒ֮ǰ
#
# Revision 1.19  2005/10/19 00:36:05  phw
# fix a description
#
# Revision 1.18  2005/10/13 09:59:51  phw
# no message
#
# Revision 1.17  2005/10/10 09:49:43  phw
# no message
#
# Revision 1.16  2005/09/26 04:05:48  phw
# �޸��˱�������Ʒ�Ĳ��ݽӿ�,ʹ���ǽ���һ��owner����,�����ж�ӵ����
#
# Revision 1.15  2005/09/19 10:13:41  phw
# no message
#
# Revision 1.14  2005/09/16 08:01:41  phw
# ����BUG
#
# Revision 1.13  2005/09/14 09:29:04  phw
# no message
#
# Revision 1.12  2005/09/13 08:56:36  phw
# ���϶�ӵ���ߺ���ӵ��������λ�õļ�¼
#
# Revision 1.11  2005/08/31 03:38:05  phw
# ����BUG
#
# Revision 1.10  2005/08/29 08:57:18  phw
# no message
#
# Revision 1.9  2005/08/26 10:45:23  phw
# no message
#
# Revision 1.8  2005/08/24 03:45:42  phw
# ����getList()����
#
# Revision 1.7  2005/07/31 06:09:04  phw
# �ѱ�����ΪcellApp��client��baseApp��dbmgr���ݣ��޸���ز��ݴ���
#
# Revision 1.6  2005/07/21 04:13:23  phw
# ����BUG
#
# Revision 1.5  2005/07/18 01:23:29  phw
# no message
#
# Revision 1.4  2005/07/15 04:45:38  phw
# no message
#
# Revision 1.3  2005/07/14 08:28:58  phw
# �޸��˱����Ĵ��ڷ�ʽ���ѱ����Ļ��������Ƶ������KitbagBaseֻ����������
#
#

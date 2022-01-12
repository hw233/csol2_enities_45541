# -*- coding: gb18030 -*-

"""
背包基础类
"""

# $Id: KitbagBase.py,v 1.40 2008-08-09 03:40:13 phw Exp $

from bwdebug import *
import ItemTypeImpl

class KitbagBase:
	"""
	背包基础类，对道具实例进行存放，自定义类型基础底层部份(包括通讯和数据的保存)。

	@ivar   _dataList: key == order, value == instance of CItemBase or inherit it
	@type   _dataList: list
	@ivar _uid2order: key = INT64(uid), value = orderID
	@type _uid2order: dict
	"""
	def __init__( self ):
		"""
		初始化
		"""
		self._dataList    = {}				# key == order, value == instance of CItemBase or inherit it
		self._uid2order    = {}				# key = INT64(uid), value = orderID

	def __len__( self ):
		"""
		获得当前背包有几个道具

		@return: 当前背包容纳的道具数量
		@rtype:  INT16
		"""
		return len( self._uid2order )

	def __getitem__( self, key ):
		return self._dataList.get( key )

	def hasUid( self, uid ):
		"""
		判断一个uid是否存在

		@param uid: 预检查的uid
		@type  uid: UINT64
		@return:       存在则True，不存在则False
		@rtype:        BOOL
		"""
		return uid in self._uid2order

	def orderHasItem( self, orderID ):
		"""
		判断一个位置上是否已存在道具

		@param orderID: 位置
		@type  orderID: INT16
		@return:        True == 指定位置有道具，False == 指定位置没有道具
		@rtype:         BOOL
		@raise IndexError: 如果orderID不在背包的允许范围内则产生此异常
		"""
		return orderID in self._dataList

	def iterDatas( self ):
		"""
		"""
		return self._dataList.itervalues()

	def getDatas( self ):
		"""
		获得存放在背包里的所有实例列表

		@return: [instance1, instance2, ...]
		@rtype:  list
		"""
		return self._dataList.values()

	def getDatasByRange( self, start = 0, end = -1 ):
		"""
		获取指定范围的物品列表

		@return: list as [instance1, ...]
		@rtype:  list of CItemBase
		"""
		if end <= 0:
			return [ e[1] for e in self._dataList.iteritems() if e[0] >= start ]
		else:
			return [ self._dataList[e] for e in xrange( start, end + 1 ) if e in self._dataList ]

	def getUid( self, orderID ):
		"""
		通过orderID获取uid

		@param orderID: 位置
		@type  orderID: INT16
		@return:        big than 0 if uid is found, else return -1
		@rtype:         INT64
		"""
		try:
			return self._dataList[orderID].uid
		except KeyError:	# 只处理类型不对的错误
			return -1

	def getOrderID( self, uid ):
		"""
		通过uid获取orderID

		@param uid: 代表唯一性的道具携带ID
		@type  uid: UINT64
		@return:       if True return orderID, else return None
		@rtype:        INT16
		@raise KeyError: 如果uid不存在则产生此异常
		"""
		try:
			return self._uid2order[uid]
		except KeyError:
			return -1

	def getByUid( self, uid ):
		"""
		获得某道具的实例

		@param uid:   道具的唯一ID
		@type  uid:   INT64
		@return:         成功则返回道具实例，否则返回None
		@rtype:          ItemInstance/None
		"""
		try:
			return self.getByOrder( self._uid2order[uid] )
		except KeyError:
			return None

	def getByOrder( self, orderID ):
		"""
		获得某道具的实例

		@return:         成功则返回道具实例，否则返回None
		@rtype:          ItemInstance/None
		"""
		return self._dataList.get( orderID )

	def add( self, orderID, itemInstance ):
		"""
		放某道具到背包的某个位置。

		@param      orderID: 位置
		@type       orderID: INT16
		@param itemInstance: 继承于CItemBase的自定义类型道具实例
		@type  itemInstance: CItemBase
		@return:             成功则返回True，否则返回False；
		                     失败有两种可能，一种是uid已存在，另一种是指定的位置(orderID)上已经有东西
		@rtype:              BOOL
		@note:               该方法并不复制itemInstance实例，而是直接引用itemInstance实例
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
		将某道具从背包里删除并返回

		@param uid: 道具的唯一ID
		@type  uid: INT64
		@return:       BOOL
		@raise KeyError: 如果uid不存在同产生此异常
		"""
		return self.removeByOrder( self.getOrderID[uid] )

	def removeByOrder( self, orderID ):
		"""
		将某道具从背包里删除并返回

		@param orderID: 背包位置
		@type  orderID: UINT8
		@return:        BOOL
		@raise IndexError: 如果orderID不在背包的允许范围内则产生此异常
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
		将某道具从背包里删除并返回

		@param orderID: 背包位置
		@type  orderID: UINT8
		@return:        BOOL
		@raise IndexError: 如果orderID不在背包的允许范围内则产生此异常
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
		交换两个位置上的道具

		@param srcOrder: 位置1
		@type  srcOrder: UINT8
		@param dstOrder: 位置2
		@type  dstOrder: UINT8
		@return:       成功(True) or 失败(False)
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
		获取当前背包所有物品的order
		"""
		return self._dataList.iterkeys()
	
# $Log: not supported by cvs2svn $
# Revision 1.39  2008/06/10 08:59:44  huangyongwei
# 去掉了：
# < 			print "11111111111111111"
#
# 160d158
# < 			print "2222222222222222"
#
# Revision 1.38  2008/05/30 02:59:22  yangkai
# 装备栏调整
#
# Revision 1.37  2008/04/08 06:00:54  yangkai
# 修正 findAll
#
# Revision 1.36  2008/04/03 06:28:20  phw
# method rename: find2All() -> find(), findAll2All() -> findAll()
# itemKeyName -> itemID
# return value type modified: find(), findAll()
#
# Revision 1.35  2007/12/14 07:11:23  wangshufeng
# method modify:canSwapOrder,如果物品被冻结，禁止其移动。
# method modify:swapTo,如果物品被冻结，禁止其移动。
#
# Revision 1.34  2007/11/28 02:12:57  yangkai
# 移除了无用的 from ItemTypeEnum import *
#
# Revision 1.33  2007/11/27 08:03:29  yangkai
# no message
#
# Revision 1.32  2007/11/24 03:18:51  yangkai
# 物品系统调整，属性更名
# "maxSpace" --> "kb_maxSpace"
#
# Revision 1.31  2007/11/08 09:41:16  phw
# self.freeze -> self.freezeState
# 修正了属性名与方法名同名的bug
#
# Revision 1.30  2007/11/08 06:26:49  yangkai
# 增加接口 updateSrcClass()用于更新背包的源物品属性
#
# Revision 1.29  2007/10/25 04:22:28  phw
# method removed: popByOrder(), popByTote()
# method added: isFrozen(), freeze(), unfreeze()，用于设置一个在背包栏中的背包的锁定状态，此功能当前的设计主要是用于把空背包直接从背包栏中取下来放到银行中的异步操作的数据安全保障。
# 修改了背包中的物品增加、删除、交换的接口，加入了对锁定状态的判断
#
# Revision 1.28  2007/04/06 09:35:41  huangyongwei
# 在 getFreeOrder 函数中，增加了两个参数，
# 表示查找的起始和结束位置
#
# Revision 1.27  2007/03/12 02:31:05  kebiao
# 修改了物品离开一个背包时没有及时删除的一个BUG
# removeByOrder
#
# Revision 1.26  2006/09/21 01:18:00  phw
# add new method: findByType();
#
# Revision 1.25  2006/09/19 03:17:15  huangyongwei
# 添加了获取同 ID 物品函数： getByID（）
#
# Revision 1.24  2006/08/11 02:45:13  phw
# 接口声明更改：
#     from: def onInto( self, owner, order, itemInstance )
#     to:   def onInto( self, owner, itemInstance )
#     from: def onLeave( self, owner, order, itemInstance ):
#     to:   def onLeave( self, owner, itemInstance ):
# 修改接口：
#     _add(); 给新加入的物品增加设置kitbag、order、toteID代码，原onInto()相同代码删除
#     removeByOrder(); 给移出去的物品增加设置kitbag、order、toteID代码(恢复为没背包、位置状态)，原onLeave()相同代码删除
# 属性更名：修改所有itemInstance.keyName或itemInstance.id()为itemInstance.id
#
# Revision 1.23  2006/08/09 08:26:20  phw
# 属性"kitName"更名为"srcID"
#
# Revision 1.22  2006/08/05 07:59:13  phw
# 修改接口：onInit()
#     from: self.setMaxSpace( srcClass.maxSpace )
#     to:   self.setMaxSpace( srcClass.query( "maxSpace" ) )
#
# Revision 1.21  2006/05/26 10:21:59  phw
# no message
#
# Revision 1.20  2005/11/07 05:57:21  phw
# 把onLevel()调用放在删除物品之前
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
# 修改了背包和物品的部份接口,使它们接收一个owner参数,用于判断拥有者
#
# Revision 1.15  2005/09/19 10:13:41  phw
# no message
#
# Revision 1.14  2005/09/16 08:01:41  phw
# 修正BUG
#
# Revision 1.13  2005/09/14 09:29:04  phw
# no message
#
# Revision 1.12  2005/09/13 08:56:36  phw
# 加上对拥有者和在拥有者身上位置的记录
#
# Revision 1.11  2005/08/31 03:38:05  phw
# 修正BUG
#
# Revision 1.10  2005/08/29 08:57:18  phw
# no message
#
# Revision 1.9  2005/08/26 10:45:23  phw
# no message
#
# Revision 1.8  2005/08/24 03:45:42  phw
# 增加getList()方法
#
# Revision 1.7  2005/07/31 06:09:04  phw
# 把背包分为cellApp、client、baseApp、dbmgr部份，修改相关部份代码
#
# Revision 1.6  2005/07/21 04:13:23  phw
# 修正BUG
#
# Revision 1.5  2005/07/18 01:23:29  phw
# no message
#
# Revision 1.4  2005/07/15 04:45:38  phw
# no message
#
# Revision 1.3  2005/07/14 08:28:58  phw
# 修改了背包的存在方式，把背包的基础功能移到这里，让KitbagBase只处理传输问题
#
#

# -*- coding: gb18030 -*-
#
# $Id: ItemBagRole.py,v 1.52 2008-08-09 09:29:13 wangshufeng Exp $

"""
背包公共模块
"""

from bwdebug import *
import ItemTypeEnum
import csdefine
import csstatus
import csconst
import time

class ItemBagRole:
	"""
	背包的公共方法

	@ivar kitbags: 一个物品列表，用来存储物品
	@type kitbags: ITEMS
	"""
	def checkItemFromNKCK_( self, itemID, amount ):
		"""
		判断物品栏及神机匣里否有指定标识名的物品及数量

		@param itemID: 道具唯一标识符
		@type  itemID: ITEM_ID
		@param      amount: 至少必须存在多少数量
		@type       amount: INT16
		@return:            BOOL
		@rtype:             BOOL
		"""
		return self.countItemTotalEx_( csconst.KB_SEARCH_COMMON_AND_CASKET, itemID ) >= amount

	def getItemByUid_( self, uid ):
		"""
		通过uid获得道具（所有背包）

		@param  uid	: 道具的唯一标识
		@type   uid	: UINT64
		@return		: 继承于CItemBase的自定义类型道具实例，找不到则返回None
		@rtype		: class instance/None
		"""
		try:
			return self.itemsBag.getByUid( uid )
		except KeyError:
			return None

	def findItemFromEK_( self, itemID ):
		"""
		从装备栏里查找某道具是否存在

		@param itemID: 道具唯一标识符
		@type  itemID: ITEM_ID
		@return:       CItemBase（或继承于它）的物品实例类，如果找不到则返回 None.
		@rtype:        CItemBase/None
		"""
		return self.findItemEx_( csconst.KB_SEARCH_EQUIP, itemID )

	def findItemFromNKCK_( self, itemID ):
		"""
		从所有的普通背包以及神机匣里查找某道具是否存在(不包括装备栏)

		@param itemID: 道具唯一标识符
		@type  itemID: ITEM_ID
		@return:       CItemBase（或继承于它）的物品实例类，如果找不到则返回 None.
		@rtype:        CItemBase/None
		"""
		return self.findItemEx_( csconst.KB_SEARCH_COMMON_AND_CASKET, itemID )

	def findItemsFromNKCK_( self, itemID ):
		"""
		从普通背包和神机匣中搜索指定类型的物品是否在背包里

		@param beginKitOrder: 从哪个背包开始搜
		@type  beginKitOrder: UINT8
		@param    beginOrder: 从背包的哪个位置开始搜
		@type     beginOrder: UINT8
		@param        itemID: 物品标识符
		@type         itemID: STRING
		@return:              返回物品列表，如果没有则返回空列表
		@rtype:               ARRAY of CItemBase
		"""
		return self.findItemsEx_( csconst.KB_SEARCH_COMMON_AND_CASKET, itemID )

	def findItemEx_( self, kitbagOrders, itemID ):
		"""
		返回第一个在指定的背包中搜索到的给定类型的物品

		@param kitbagOrders: 搜索哪些位置的背包
		@type  kitbagOrders: ARRAY OF INT
		@param        itemID: 物品标识符
		@type         itemID: STRING
		@return:              CItemBase（或继承于它）的物品实例类，如果找不到则返回 None.
		@rtype:               CItemBase/None
		"""
		l = [ e for e in kitbagOrders if e in self.kitbags ]
		for kitOrder in l:
			for item in self.getItems( kitOrder ):
				if item.id == itemID: return item
		return None

	def findItemsEx_( self, kitbagOrders, itemID ):
		"""
		搜索指定类型的物品是否在背包里

		@param kitbagOrders: 搜索哪些位置的背包
		@type  kitbagOrders: ARRAY OF INT
		@param        itemID: 物品标识符
		@type         itemID: STRING
		@return:              CItemBase（或继承于它）的物品实例类，如果找不到则返回 None.
		@rtype:               CItemBase/None
		"""
		l = [ e for e in kitbagOrders if e in self.kitbags ]
		items = []
		for kitOrder in l:
			for item in self.getItems( kitOrder ):
				if item.id == itemID:
					items.append( item )
		return items

	def getRoleKitBagOrders( self ):
		"""
		获取人物身上装备了的背包的ORDERs，包括普通背包和神机匣
		"""
		return [ e for e in csconst.KB_SEARCH_COMMON_AND_CASKET if e in self.kitbags ]

	def findEquipsByType( self, itemType ):
		"""
		从装备栏中查找相同类型的装备

		@param itemType: 物品类型
		@type  itemType: INT
		@return: 如果找到则返回物品实例列表，如果找不到则返回空列表——[]
		"""
		equips = []
		for item in self.getItems( csdefine.KB_EQUIP_ID ):
			if item.getType() == itemType:
				equips.append( item )
		return equips

	def getSuitEquipIDs( self ):
		"""
		获取已装备的绿色防具ID列表
		@return:          list of ItemIDs
		"""
		ARMOR_ORDER = [	ItemTypeEnum.CEL_HEAD,
							ItemTypeEnum.CEL_BODY,
							ItemTypeEnum.CEL_BREECH,
							ItemTypeEnum.CEL_VOLA,
							ItemTypeEnum.CEL_HAUNCH,
							ItemTypeEnum.CEL_CUFF,
							ItemTypeEnum.CEL_FEET,
							]
		suitEquipIDs = []
		for index in ARMOR_ORDER:
			item = self.getItem_( index )
			if item is None: continue
			if item.getQuality() != ItemTypeEnum.CQT_GREEN: continue
			if item.getHardiness() == 0: continue		#加入耐久度的判断 如果当前耐久度为0则不返回该ID(相当于没有装备)
			suitEquipIDs.append( item.id )
		return suitEquipIDs

	def getAllGreenEquips( self ):
		"""
		获取已装备的绿色装备列表
		@return:          list of ItemIDs
		"""
		greenEquips = []
		for equip in self.getItems( csdefine.KB_EQUIP_ID ):
			if equip.isGreen():
				greenEquips.append( equip )
		return greenEquips

	def getItem_( self, orderID ):
		"""
		根据order获取背包上的某道具

		@param orderID: 道具在背包里的位置
		@type  orderID: INT16
		@return:        继承于CItemBase的自定义类型道具实例，找不到则返回None
		@rtype:         class instance/None
		"""
		return self.itemsBag.getByOrder( orderID )

	def getItems( self, kitOrder ):
		"""
		取得指定背包的物品
		@return: [itemInstance, ...]
		"""
		return self.itemsBag.getDatasByRange( kitOrder * csdefine.KB_MAX_SPACE, kitOrder * csdefine.KB_MAX_SPACE + csdefine.KB_MAX_SPACE - 1 )

	def getAllItems( self ):
		"""
		get all items from kitbags
		@return: [itemInstance, ...]
		"""
		return self.itemsBag.getDatas()

	def getNormalKitbagFreeOrder( self ):
		"""
		取得普通背包的空闲位置
		return: order
		"""
		# 取得除装备栏与神机匣外所有的背包
		maxSpace = csdefine.KB_MAX_SPACE
		kbcid = csdefine.KB_COMMON_ID
		l = [ e for e in xrange( kbcid, kbcid + csdefine.KB_COUNT ) if e in self.kitbags ]
		for kitOrder in l:
			# 加入跳过过期背包的判断 modified by姜毅
			kitItem = self.kitbags.get( kitOrder )
			if kitItem.isActiveLifeTime() and kitItem.isOverdue():
				continue
			for order in xrange( kitOrder * maxSpace, kitOrder *maxSpace + kitItem.getMaxSpace() ):
				if not self.itemsBag.orderHasItem( order ):
					return order
		return -1
		
	def getAllNormalKitbagFreeOrders( self ):
		"""
		取得普通背包的所有空闲位置 by 姜毅
		return: order list
		"""
		# 取得除装备栏与神机匣外所有的背包
		kbcid = csdefine.KB_COMMON_ID
		maxSpace = csdefine.KB_MAX_SPACE
		orders = []
		l = [ e for e in xrange( kbcid, kbcid + csdefine.KB_COUNT ) if e in self.kitbags ]
		for kitOrder in l:
			# 加入跳过过期背包的判断 modified by姜毅
			kitItem = self.kitbags.get( kitOrder )
			if kitItem.isActiveLifeTime() and kitItem.isOverdue():
				continue
			orders.extend(filter(lambda x: not self.itemsBag.orderHasItem( x ), [order for order in xrange( kitOrder * maxSpace, kitOrder * maxSpace + kitItem.getMaxSpace() )]))
		return orders
	
	def getFreeOrderFK( self, kitOrderID ):
		"""
		取得指定背包的空闲位置
		return: order
		"""
		# 取得指定背包的空闲位置
		if kitOrderID not in self.kitbags: return -1
		startOrder = kitOrderID * csdefine.KB_MAX_SPACE
		for order in xrange( startOrder, startOrder + self.kitbags[kitOrderID].getMaxSpace() ):
			if not self.itemsBag.orderHasItem( order ):
				return order
		return -1

	def getFreeOrderCountFK( self, kitOrder ):
		"""
		获得指定背包空白位置的总数量

		@return: free order count
		@rtype:  INT
		"""
		count = 0
		if kitOrder not in self.kitbags: return 0
		for order in xrange( kitOrder * csdefine.KB_MAX_SPACE, kitOrder * csdefine.KB_MAX_SPACE + self.kitbags[kitOrder].getMaxSpace() ):
			if not self.itemsBag.orderHasItem( order ):
				count += 1
		return count

	def getNormalKitbagFreeOrderCount( self ):
		"""
		获得道具栏里空白位置的总数量

		@return: free order count
		@rtype:  INT
		"""
		count = 0
		# 取得除装备栏与神机匣外所有的背包
		l = [ e for e in xrange( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT ) if e in self.kitbags ]
		for kitOrder in l:
			# 加入跳过过期背包的判断 modified by姜毅
			kitItem = self.kitbags.get( kitOrder )
			if kitItem.isActiveLifeTime():
				if kitItem.isOverdue(): continue
			for order in xrange( kitOrder * csdefine.KB_MAX_SPACE, kitOrder * csdefine.KB_MAX_SPACE + self.kitbags[kitOrder].getMaxSpace() ):
				if not self.itemsBag.orderHasItem( order ):
					count += 1
		return count

	def countItemTotal_( self, itemID ):
		"""
		在普通背包和神机匣中查询某一类物品的总数量

		@param itemID: 物品ID
		@type  itemID: ITEM_ID
		@return: 返回所有同类物品的总数量，如果找不到则返回0
		@rtype:  INT16
		"""
		return self.countItemTotalEx_( csconst.KB_SEARCH_COMMON_AND_CASKET, itemID )

	def countItemTotalEx_( self, kitbagOrders, itemID ):
		"""
		在指定的背包中查询某一类物品的总数量

		@param kitbagOrders: 搜索哪些位置的背包
		@type  kitbagOrders: ARRAY OF INT
		@param       itemID: 物品ID
		@type        itemID: ITEM_ID
		@return: 返回所有同类物品的总数量，如果找不到则返回0
		@rtype:  INT16
		"""
		amount = 0
		l = [ e for e in kitbagOrders if e in self.kitbags ]
		for i in l:
			for item in self.getItems( i ):
				if item.id == itemID:
					amount += item.amount
		return amount

	def countItemTotalWithBinded_( self, itemID, isBinded ):
		"""
		在普通背包和神机匣中查询某一类相同绑定状态的物品的总数量

		@param itemID: 物品ID
		@type  itemID: ITEM_ID
		@param isBinded: 是否绑定
		@type  isBinded: BOOL
		@return: 返回所有同类物品的总数量，如果找不到则返回0
		@rtype:  INT16
		"""
		return self.countItemTotalWithBindedEx_( csconst.KB_SEARCH_COMMON_AND_CASKET, itemID, isBinded )

	def countItemTotalWithBindedEx_( self, kitbagOrders, itemID, isBinded ):
		"""
		在指定的背包中查询某一类相同绑定状态的物品的总数量

		@param kitbagOrders: 搜索哪些位置的背包
		@type  kitbagOrders: ARRAY OF INT
		@param itemID: 物品ID
		@type  itemID: ITEM_ID
		@param isBinded: 是否绑定
		@type  isBinded: BOOL
		@return: 返回所有同类物品的总数量，如果找不到则返回0
		@rtype:  INT16
		"""
		amount = 0
		l = [ e for e in kitbagOrders if e in self.kitbags ] 	# 加1的原因是需要从神机匣里搜索wsf，15:07 2008-6-24
		for i in l:
			for item in self.getItems( i ):
				if item.id == itemID and item.isBinded() == isBinded:
					amount += item.amount
		return amount

	def findItemsByIDEx( self, kitbagOrders, itemID ):
		"""
		从指定的背包中搜索 ID 为 itemID 的道具实例列表
		忽略绑定类型

		@param kitbagOrders: 搜索哪些位置的背包
		@type  kitbagOrders: ARRAY OF INT
		@param itemID: 物品ID
		@type  itemID: ITEM_ID
		@return: 返回所有同类物品实例列表
		@rtype:  List of CItemBase instance
		"""
		items = []
		l = [ e for e in kitbagOrders if e in self.kitbags ]
		for korder in l:
			for item in self.getItems( korder ):
				if item.id == itemID:
					items.append( item )
		return items

	def findItemsByIDsEx( self, kitbagOrders, itemIDs ):
		"""
		从指定的背包中搜索 ID 在 itemIDs 内的道具实例列表
		忽略绑定类型

		@param kitbagOrders: 搜索哪些位置的背包
		@type  kitbagOrders: ARRAY OF INT
		@param itemID: 物品ID
		@type  itemIDs: LIST
		@return: 返回所有同类物品实例列表
		@rtype:  List of CItemBase instance
		"""
		items = []
		l = [ e for e in kitbagOrders if e in self.kitbags ]
		for korder in l:
			for item in self.getItems( korder ):
				if item.id in itemIDs:
					items.append( item )
		return items

	def findItemsByID( self, itemID ):
		"""
		从普通背包、神机匣、装备栏中搜索 ID 为 itemID 的道具实例列表
		忽略绑定类型

		@param itemID: 物品ID
		@type  itemID: ITEM_ID
		@return: 返回所有同类物品实例列表
		@rtype:  List of CItemBase instance
		"""
		return self.findItemsByIDEx( csconst.KB_SEARCH_ALL, itemID )

	def findItemsByIDFromNK( self, itemID ):
		"""
		从普通背包中搜索 ID 为 itemID 的道具实例列表
		忽略绑定类型

		@param itemID: 物品ID
		@type  itemID: ITEM_ID
		@return: 返回所有同类物品实例列表
		@rtype:  List of CItemBase instance
		"""
		return self.findItemsByIDEx( csconst.KB_SEARCH_COMMON, itemID )

	def findItemsByIDFromNKCK( self, itemID ):
		"""
		从普通背包和神机匣中搜索 ID 为 itemID 的道具实例列表
		忽略绑定类型

		@param itemID: 物品ID
		@type  itemID: ITEM_ID
		@return: 返回所有同类物品实例列表
		@rtype:  List of CItemBase instance
		"""
		return self.findItemsByIDEx( csconst.KB_SEARCH_COMMON_AND_CASKET, itemID )
		
	def findItemsByIDsFromNKCK( self, itemIDs ):
		"""
		从普通背包和神机匣中搜索 ID 为 itemID 的道具实例列表
		忽略绑定类型

		@param itemID: 物品ID
		@type  itemID: ITEM_ID
		@return: 返回所有同类物品实例列表
		@rtype:  List of CItemBase instance
		"""
		return self.findItemsByIDsEx( csconst.KB_SEARCH_COMMON_AND_CASKET, itemIDs )

	def findItemsByIDWithBindFromNKCK( self, itemID, isBinded ):
		"""
		从普通背包和神机匣中搜索 ID 为 itemID 的道具实例列表
		考虑绑定类型

		@param itemID: 物品ID
		@type  itemID: ITEM_ID
		@param isBinded: 物品是否绑定
		@type  isBinded: BOOL
		@return: 返回所有同类物品实例列表
		@rtype:  List of CItemBase instance
		"""
		return [ item for item in self.findItemsByIDEx( csconst.KB_SEARCH_COMMON_AND_CASKET, itemID ) if item.isBinded() == isBinded ]

	def getItemsFK( self, itemID, kitbagID ):
		"""
		在指定包裹中获取ID为ItemID的物品实例列表
		忽略绑定类型
		@param itemID: 物品ID
		@type  itemID: ITEM_ID
		@return: 返回所有同类物品实例列表
		@rtype:  List of CItemBase instance
		"""
		items = []
		for item in self.getItems( kitbagID ):
			if item.id == itemID:
				items.append( item )
		return items

	def getItemsFKWithBind( self, itemID, kitbagID, isBinded ):
		"""
		在指定包裹中获取ID为ItemID的物品实例列表
		考虑绑定类型
		@param itemID: 物品ID
		@type  itemID: ITEM_ID
		@param kitbagID: 背包位ID
		@type  kitbagID: INT8
		@param isBinded: 物品是否绑定
		@type  isBinded: BOOL
		@return: 返回所有同类物品实例列表
		@rtype:  List of CItemBase instance
		"""
		items = []
		for item in self.getItems( kitbagID ):
			if item.id == itemID and item.isBinded() == isBinded:
				items.append( item )
		return items

	def checkItemsPlaceIntoNK_( self, itemList ):
		"""
		是否能把一批物品放入背包中，此判断根据addItem_()方法的操作方式来决定是否有足够位置。

		@param itemList: list of ITEM as [item1, item2, ...]
		@type  itemList: list of ITEM
		@return: INT8, 0 == True，不为0表示具体的错误原因。
		@rtype:  INT8
		"""
		# 如果玩家仅能拥有有限的此类物品
		if not self.checkItemLimit( itemList ):
			return csdefine.KITBAG_ITEM_COUNT_LIMIT

		freeOrder = self.getNormalKitbagFreeOrderCount()
		# in here, 可能还要检查该物品是否能放进背包里，
		# 以现在的什么物品都可以放到背包里的机制来说，不需要判断。
		# 注：不使用以下代码的原因是为了将来实现上面注释所说的判断时不会产生bug
		#if itemCount <= freeOrder: return True

		# 遍历要加入背包的物品，辅助记录每一个物品加入背包后的背包的中间状态，
		# 会根据此中间状态判断余下的每一个物品是否还能加入背包。11:02 2010-3-1，wsf
		# 可以考虑写一个class实现拥有freeOrder的模拟背包，但为效率计直接把代码扔在这里，实现的逻辑是一样的。
		totalItemDict = {}		# 物品总数统计，以便检查玩家只能拥有某类有限物品规则
		stackableItemDict = {}	# 用于记录已经计算已叠加到背包中的物品数量 {( itemID, isBinded ):amount, ...  }，以便判断再加入同类物品是否还能叠加成功
		needOrderItemList = []	# 模拟物品加入背包空位后的此空位的中间状态
		for item in itemList:
			itemID = item.id
			isBinded = item.isBinded()
			if not isBinded and item.getBindType() in [ ItemTypeEnum.CBT_PICKUP, ItemTypeEnum.CBT_QUEST ]:
				isBinded = True
			amount = item.getAmount()
			stackable = item.getStackable()
			if stackable > 1:
				try:
					hasAmount = stackableItemDict[( itemID, isBinded )] + amount
				except KeyError:
					hasAmount = amount
					stackableItemDict[( itemID, isBinded )] = 0
				if self.canStackable( itemID, isBinded, hasAmount ):	# 可以叠加
					stackableItemDict[( itemID, isBinded )] += amount
				else:	# 如果不可以叠加的话，那么就检查加入物品时是否能够叠加
					isStackable = False
					key = ( itemID, isBinded )
					tempList = []	# 欲加入背包中的可叠加物品列表，用于判断是否可以在加入背包前叠加
					tempAmount = amount
					for itemDict in needOrderItemList:	# 是否和已经占一个位置的同类物品叠加
						itemAmount = itemDict["amount"]
						if itemDict["key"] == key:
							if itemAmount + tempAmount <= stackable:
								tempList.append( itemDict )
								isStackable = True
								break
							else:
								tempList.append( itemDict )
								tempAmount -= stackable - itemAmount
					if isStackable:		# 可以叠加到未加入背包的物品中
						for itemDict in tempList:
							space = stackable - itemDict["amount"]
							if amount <= space:
								itemDict["amount"] += amount
								break
							else:
								itemDict["amount"] = stackable
								amount -= space
					else:				# 没有叠加成功，增加一格数据
						needOrderItemList.append( {"key":(itemID, isBinded),"amount":amount} )
			else:	# 如果是不可叠加物品那么也占一格数据
				needOrderItemList.append( {"key":(itemID, isBinded),"amount":amount} )

		if len( needOrderItemList ) <= freeOrder:
			return csdefine.KITBAG_CAN_HOLD
		else:
			return csdefine.KITBAG_NO_MORE_SPACE

	def checkItemLimit( self, itemList ):
		"""
		检测一些物品是否放入玩家的背包，只检查限制数量
		如果是多个不同ID的物品，只要有一个不满足条件，则不能放入
		@param item: 继承于CItemBase的自定义道具实例
		@type item: itemInstance
		@return Bool
		"""
		# 记录 {物品ID：(数量,最大数)}的dict
		itemAmountCount = {}
		for item in itemList:
			itemID = item.id
			amount = item.amount
			onlyLimit = item.getOnlyLimit()
			if itemID in itemAmountCount:
				itemAmountCount[itemID] = ( itemAmountCount[itemID][0] + amount, onlyLimit )
			else:
				itemAmountCount[itemID] = ( amount, onlyLimit )


		for itemID, data in itemAmountCount.iteritems():
			amount, onlyLimit = data
			if onlyLimit <= 0: continue
			tAmount = self.countItemTotal_( itemID )
			if tAmount + amount > onlyLimit: return False

		return True

	def canStackableInKit( self, itemID, isBinded, amount, kitOrder ):
		"""
		包裹位为kitOrder的包裹是否能够叠加itemID的物品，忽略空格
		如果背包有空位置而没有此物品仍然算不可叠加,由外部添加到背包去。

		@param itemID: 继承于CItemBase的自定义道具实例的id
		@pram bindType : 物品的绑定类型
		@param  iamount: 这个物品的数量
		@param  kitOrder: 包裹位
		@return:             成功则返回True，如果成功，则会自动通知client，失败则返回False
		@rtype:              BOOL
		"""
		currtotal = 0
		itemList = self.getItems( kitOrder )
		items = []
		for item in itemList:
			if item.id == itemID and item.isBinded() == isBinded:
				items.append( item )
		if items == []:
			return False
		stackable = items[0].getStackable()
		for e in items:	currtotal += e.getAmount()	# 获得总数
		return len( items ) * stackable - currtotal >= amount

	def canStackable( self, itemID, isBinded, iamount ):
		"""
		返回背包是否可以完全叠加这个物品 忽略空格(如果背包有空位置而没有此物品仍然算不可叠加,由外部添加到背包去)
		@param itemID: 继承于CItemBase的自定义道具实例的id
		@param bindType : 这个物品的绑定类型
		@param  iamount: 这个物品的数量
		@return:             成功则返回True，如果成功，则会自动通知client，失败则返回False
		@rtype:              BOOL
		"""
		currtotal = 0
		stackableUpperCount = 0
		r = self.findItemsByIDFromNKCK( itemID )
		if r == []:	return False	# 背包没有此物品,不能进行叠加 应该走添加流程
		stackable = r[0].getStackable()
		for e in r:
			if not e.isFrozen() and e.isBinded() == isBinded:
				stackableUpperCount += stackable
				currtotal += e.getAmount()	# 获得总数
		return stackableUpperCount - currtotal >= iamount

	def isEmptyHand( self ):
		"""
		判断是否为空手(两只手都没装备东西)
		"""
		return self.getItem_( ItemTypeEnum.CWT_RIGHTHAND ) is None and self.getItem_( ItemTypeEnum.CWT_LEFTHAND ) is None

	def primaryHandEmpty( self ):
		"""
		判断主手是否为空

		@return: BOOL
		"""
		if self.itemsBag.getByOrder( ItemTypeEnum.CWT_RIGHTHAND ) is None: #如果主手为空
			return True
		else:
			hardiness = self.getItem_( ItemTypeEnum.CWT_RIGHTHAND ).query("eq_hardiness")
			if hardiness <= 0: #如果耐久度为0
				return True
			else:
				return False

	def canWieldEquip( self, order, itemInstance ):
		"""
		判断是否能在某一位置装备一件物品
		"""
		# 物品为空，不能装备
		if itemInstance is None: return csstatus.KIT_EQUIP_NOT_FIT_EQUIP
		# 物品类型不是装备，不能装备
		if not itemInstance.isEquip(): return csstatus.KIT_EQUIP_NOT_FIT_EQUIP
		if not itemInstance.canWield( self ): return csstatus.KIT_EQUIP_NOT_FIT_EQUIP
		if itemInstance.getType() not in ItemTypeEnum.EQUIP_TYPE_SET: return csstatus.KIT_EQUIP_NOT_FIT_EQUIP
		# 玩家正在吟唱，不能装备
		if self.intonating(): return csstatus.KIT_EQUIP_INTONATE_CANT_OPERATER
		# 装备的位置不在该物品可装备位置上， 不能装备
		if order not in itemInstance.getWieldOrders():
			return csstatus.KIT_EQUIP_CANT_APP_ORDER
		unwieldList = itemInstance.getUnwieldOrders( self.itemsBag, order )
		# 如果需要卸下多于一个的装备就失败
		special = [ ItemTypeEnum.ITEM_WEAPON_SPEAR2, ItemTypeEnum.ITEM_WEAPON_SHIELD ]
		if itemInstance.getType() not in special  and len( unwieldList ) > 1:
			return csstatus.KIT_EQUIP_NOT_FIT_EQUIP
		# 只需要卸下一个装备时就必须判断卸下的装备位置与交换的位置是否一样
		if itemInstance.getType() not in special  and len( unwieldList ) == 1 and  unwieldList[0] != order:
			return csstatus.KIT_EQUIP_NOT_FIT_EQUIP
		return csstatus.KIT_EQUIP_CAN_FIT_EQUIP

	def order2uid( self, order ):
		"""
		通过 order  获取 uid
		@param order: 位置
		@type  order: INT16
		@return:        big than 0 if uid is found, else return -1
		@rtype:         INT
		"""
		return self.itemsBag.getUid( order )

	def uid2order( self, uid ):
		"""
		通过 uid 获取 orderID
		@param uid: 位置
		@type  uid: INT64
		@return:        big than 0 if orderID is found, else return -1
		@rtype:         INT
		"""
		return self.itemsBag.getOrderID( uid )

	def getRacehorseItem_( self, orderID ):
		"""
		根据order获取背包上的某道具

		@param orderID: 道具在背包里的位置
		@type  orderID: INT16
		@return:        继承于CItemBase的自定义类型道具实例，找不到则返回None
		@rtype:         class instance/None
		"""
		return self.raceItemsBag.getByOrder( orderID )

	def getUnBindEquips( self ):
		"""
		获取未绑定的装备

		@return:        继承于CItemBase的自定义类型道具实例列表，找不到则返回[]
		@rtype:         class instance/None
		"""
		equips = self.getItems( csdefine.KB_EQUIP_ID )
		return [ equip for equip in equips if not equip.isBinded() ]

	def getUnObeyEquips( self ):
		"""
		获取未认主装备 by姜毅

		@return:        继承于CItemBase的自定义类型道具实例列表，找不到则返回[]
		@rtype:         class instance/None
		"""
		equips = self.getItems( csdefine.KB_EQUIP_ID )
		return [ equip for equip in equips if not equip.isObey() ]

# ItemBagRole.py

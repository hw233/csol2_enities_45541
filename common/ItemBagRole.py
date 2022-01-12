# -*- coding: gb18030 -*-
#
# $Id: ItemBagRole.py,v 1.52 2008-08-09 09:29:13 wangshufeng Exp $

"""
��������ģ��
"""

from bwdebug import *
import ItemTypeEnum
import csdefine
import csstatus
import csconst
import time

class ItemBagRole:
	"""
	�����Ĺ�������

	@ivar kitbags: һ����Ʒ�б������洢��Ʒ
	@type kitbags: ITEMS
	"""
	def checkItemFromNKCK_( self, itemID, amount ):
		"""
		�ж���Ʒ�������ϻ�����ָ����ʶ������Ʒ������

		@param itemID: ����Ψһ��ʶ��
		@type  itemID: ITEM_ID
		@param      amount: ���ٱ�����ڶ�������
		@type       amount: INT16
		@return:            BOOL
		@rtype:             BOOL
		"""
		return self.countItemTotalEx_( csconst.KB_SEARCH_COMMON_AND_CASKET, itemID ) >= amount

	def getItemByUid_( self, uid ):
		"""
		ͨ��uid��õ��ߣ����б�����

		@param  uid	: ���ߵ�Ψһ��ʶ
		@type   uid	: UINT64
		@return		: �̳���CItemBase���Զ������͵���ʵ�����Ҳ����򷵻�None
		@rtype		: class instance/None
		"""
		try:
			return self.itemsBag.getByUid( uid )
		except KeyError:
			return None

	def findItemFromEK_( self, itemID ):
		"""
		��װ���������ĳ�����Ƿ����

		@param itemID: ����Ψһ��ʶ��
		@type  itemID: ITEM_ID
		@return:       CItemBase����̳�����������Ʒʵ���࣬����Ҳ����򷵻� None.
		@rtype:        CItemBase/None
		"""
		return self.findItemEx_( csconst.KB_SEARCH_EQUIP, itemID )

	def findItemFromNKCK_( self, itemID ):
		"""
		�����е���ͨ�����Լ����ϻ�����ĳ�����Ƿ����(������װ����)

		@param itemID: ����Ψһ��ʶ��
		@type  itemID: ITEM_ID
		@return:       CItemBase����̳�����������Ʒʵ���࣬����Ҳ����򷵻� None.
		@rtype:        CItemBase/None
		"""
		return self.findItemEx_( csconst.KB_SEARCH_COMMON_AND_CASKET, itemID )

	def findItemsFromNKCK_( self, itemID ):
		"""
		����ͨ���������ϻ������ָ�����͵���Ʒ�Ƿ��ڱ�����

		@param beginKitOrder: ���ĸ�������ʼ��
		@type  beginKitOrder: UINT8
		@param    beginOrder: �ӱ������ĸ�λ�ÿ�ʼ��
		@type     beginOrder: UINT8
		@param        itemID: ��Ʒ��ʶ��
		@type         itemID: STRING
		@return:              ������Ʒ�б����û���򷵻ؿ��б�
		@rtype:               ARRAY of CItemBase
		"""
		return self.findItemsEx_( csconst.KB_SEARCH_COMMON_AND_CASKET, itemID )

	def findItemEx_( self, kitbagOrders, itemID ):
		"""
		���ص�һ����ָ���ı������������ĸ������͵���Ʒ

		@param kitbagOrders: ������Щλ�õı���
		@type  kitbagOrders: ARRAY OF INT
		@param        itemID: ��Ʒ��ʶ��
		@type         itemID: STRING
		@return:              CItemBase����̳�����������Ʒʵ���࣬����Ҳ����򷵻� None.
		@rtype:               CItemBase/None
		"""
		l = [ e for e in kitbagOrders if e in self.kitbags ]
		for kitOrder in l:
			for item in self.getItems( kitOrder ):
				if item.id == itemID: return item
		return None

	def findItemsEx_( self, kitbagOrders, itemID ):
		"""
		����ָ�����͵���Ʒ�Ƿ��ڱ�����

		@param kitbagOrders: ������Щλ�õı���
		@type  kitbagOrders: ARRAY OF INT
		@param        itemID: ��Ʒ��ʶ��
		@type         itemID: STRING
		@return:              CItemBase����̳�����������Ʒʵ���࣬����Ҳ����򷵻� None.
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
		��ȡ��������װ���˵ı�����ORDERs��������ͨ���������ϻ
		"""
		return [ e for e in csconst.KB_SEARCH_COMMON_AND_CASKET if e in self.kitbags ]

	def findEquipsByType( self, itemType ):
		"""
		��װ�����в�����ͬ���͵�װ��

		@param itemType: ��Ʒ����
		@type  itemType: INT
		@return: ����ҵ��򷵻���Ʒʵ���б�����Ҳ����򷵻ؿ��б���[]
		"""
		equips = []
		for item in self.getItems( csdefine.KB_EQUIP_ID ):
			if item.getType() == itemType:
				equips.append( item )
		return equips

	def getSuitEquipIDs( self ):
		"""
		��ȡ��װ������ɫ����ID�б�
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
			if item.getHardiness() == 0: continue		#�����;öȵ��ж� �����ǰ�;ö�Ϊ0�򲻷��ظ�ID(�൱��û��װ��)
			suitEquipIDs.append( item.id )
		return suitEquipIDs

	def getAllGreenEquips( self ):
		"""
		��ȡ��װ������ɫװ���б�
		@return:          list of ItemIDs
		"""
		greenEquips = []
		for equip in self.getItems( csdefine.KB_EQUIP_ID ):
			if equip.isGreen():
				greenEquips.append( equip )
		return greenEquips

	def getItem_( self, orderID ):
		"""
		����order��ȡ�����ϵ�ĳ����

		@param orderID: �����ڱ������λ��
		@type  orderID: INT16
		@return:        �̳���CItemBase���Զ������͵���ʵ�����Ҳ����򷵻�None
		@rtype:         class instance/None
		"""
		return self.itemsBag.getByOrder( orderID )

	def getItems( self, kitOrder ):
		"""
		ȡ��ָ����������Ʒ
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
		ȡ����ͨ�����Ŀ���λ��
		return: order
		"""
		# ȡ�ó�װ���������ϻ�����еı���
		maxSpace = csdefine.KB_MAX_SPACE
		kbcid = csdefine.KB_COMMON_ID
		l = [ e for e in xrange( kbcid, kbcid + csdefine.KB_COUNT ) if e in self.kitbags ]
		for kitOrder in l:
			# �����������ڱ������ж� modified by����
			kitItem = self.kitbags.get( kitOrder )
			if kitItem.isActiveLifeTime() and kitItem.isOverdue():
				continue
			for order in xrange( kitOrder * maxSpace, kitOrder *maxSpace + kitItem.getMaxSpace() ):
				if not self.itemsBag.orderHasItem( order ):
					return order
		return -1
		
	def getAllNormalKitbagFreeOrders( self ):
		"""
		ȡ����ͨ���������п���λ�� by ����
		return: order list
		"""
		# ȡ�ó�װ���������ϻ�����еı���
		kbcid = csdefine.KB_COMMON_ID
		maxSpace = csdefine.KB_MAX_SPACE
		orders = []
		l = [ e for e in xrange( kbcid, kbcid + csdefine.KB_COUNT ) if e in self.kitbags ]
		for kitOrder in l:
			# �����������ڱ������ж� modified by����
			kitItem = self.kitbags.get( kitOrder )
			if kitItem.isActiveLifeTime() and kitItem.isOverdue():
				continue
			orders.extend(filter(lambda x: not self.itemsBag.orderHasItem( x ), [order for order in xrange( kitOrder * maxSpace, kitOrder * maxSpace + kitItem.getMaxSpace() )]))
		return orders
	
	def getFreeOrderFK( self, kitOrderID ):
		"""
		ȡ��ָ�������Ŀ���λ��
		return: order
		"""
		# ȡ��ָ�������Ŀ���λ��
		if kitOrderID not in self.kitbags: return -1
		startOrder = kitOrderID * csdefine.KB_MAX_SPACE
		for order in xrange( startOrder, startOrder + self.kitbags[kitOrderID].getMaxSpace() ):
			if not self.itemsBag.orderHasItem( order ):
				return order
		return -1

	def getFreeOrderCountFK( self, kitOrder ):
		"""
		���ָ�������հ�λ�õ�������

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
		��õ�������հ�λ�õ�������

		@return: free order count
		@rtype:  INT
		"""
		count = 0
		# ȡ�ó�װ���������ϻ�����еı���
		l = [ e for e in xrange( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT ) if e in self.kitbags ]
		for kitOrder in l:
			# �����������ڱ������ж� modified by����
			kitItem = self.kitbags.get( kitOrder )
			if kitItem.isActiveLifeTime():
				if kitItem.isOverdue(): continue
			for order in xrange( kitOrder * csdefine.KB_MAX_SPACE, kitOrder * csdefine.KB_MAX_SPACE + self.kitbags[kitOrder].getMaxSpace() ):
				if not self.itemsBag.orderHasItem( order ):
					count += 1
		return count

	def countItemTotal_( self, itemID ):
		"""
		����ͨ���������ϻ�в�ѯĳһ����Ʒ��������

		@param itemID: ��ƷID
		@type  itemID: ITEM_ID
		@return: ��������ͬ����Ʒ��������������Ҳ����򷵻�0
		@rtype:  INT16
		"""
		return self.countItemTotalEx_( csconst.KB_SEARCH_COMMON_AND_CASKET, itemID )

	def countItemTotalEx_( self, kitbagOrders, itemID ):
		"""
		��ָ���ı����в�ѯĳһ����Ʒ��������

		@param kitbagOrders: ������Щλ�õı���
		@type  kitbagOrders: ARRAY OF INT
		@param       itemID: ��ƷID
		@type        itemID: ITEM_ID
		@return: ��������ͬ����Ʒ��������������Ҳ����򷵻�0
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
		����ͨ���������ϻ�в�ѯĳһ����ͬ��״̬����Ʒ��������

		@param itemID: ��ƷID
		@type  itemID: ITEM_ID
		@param isBinded: �Ƿ��
		@type  isBinded: BOOL
		@return: ��������ͬ����Ʒ��������������Ҳ����򷵻�0
		@rtype:  INT16
		"""
		return self.countItemTotalWithBindedEx_( csconst.KB_SEARCH_COMMON_AND_CASKET, itemID, isBinded )

	def countItemTotalWithBindedEx_( self, kitbagOrders, itemID, isBinded ):
		"""
		��ָ���ı����в�ѯĳһ����ͬ��״̬����Ʒ��������

		@param kitbagOrders: ������Щλ�õı���
		@type  kitbagOrders: ARRAY OF INT
		@param itemID: ��ƷID
		@type  itemID: ITEM_ID
		@param isBinded: �Ƿ��
		@type  isBinded: BOOL
		@return: ��������ͬ����Ʒ��������������Ҳ����򷵻�0
		@rtype:  INT16
		"""
		amount = 0
		l = [ e for e in kitbagOrders if e in self.kitbags ] 	# ��1��ԭ������Ҫ�����ϻ������wsf��15:07 2008-6-24
		for i in l:
			for item in self.getItems( i ):
				if item.id == itemID and item.isBinded() == isBinded:
					amount += item.amount
		return amount

	def findItemsByIDEx( self, kitbagOrders, itemID ):
		"""
		��ָ���ı��������� ID Ϊ itemID �ĵ���ʵ���б�
		���԰�����

		@param kitbagOrders: ������Щλ�õı���
		@type  kitbagOrders: ARRAY OF INT
		@param itemID: ��ƷID
		@type  itemID: ITEM_ID
		@return: ��������ͬ����Ʒʵ���б�
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
		��ָ���ı��������� ID �� itemIDs �ڵĵ���ʵ���б�
		���԰�����

		@param kitbagOrders: ������Щλ�õı���
		@type  kitbagOrders: ARRAY OF INT
		@param itemID: ��ƷID
		@type  itemIDs: LIST
		@return: ��������ͬ����Ʒʵ���б�
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
		����ͨ���������ϻ��װ���������� ID Ϊ itemID �ĵ���ʵ���б�
		���԰�����

		@param itemID: ��ƷID
		@type  itemID: ITEM_ID
		@return: ��������ͬ����Ʒʵ���б�
		@rtype:  List of CItemBase instance
		"""
		return self.findItemsByIDEx( csconst.KB_SEARCH_ALL, itemID )

	def findItemsByIDFromNK( self, itemID ):
		"""
		����ͨ���������� ID Ϊ itemID �ĵ���ʵ���б�
		���԰�����

		@param itemID: ��ƷID
		@type  itemID: ITEM_ID
		@return: ��������ͬ����Ʒʵ���б�
		@rtype:  List of CItemBase instance
		"""
		return self.findItemsByIDEx( csconst.KB_SEARCH_COMMON, itemID )

	def findItemsByIDFromNKCK( self, itemID ):
		"""
		����ͨ���������ϻ������ ID Ϊ itemID �ĵ���ʵ���б�
		���԰�����

		@param itemID: ��ƷID
		@type  itemID: ITEM_ID
		@return: ��������ͬ����Ʒʵ���б�
		@rtype:  List of CItemBase instance
		"""
		return self.findItemsByIDEx( csconst.KB_SEARCH_COMMON_AND_CASKET, itemID )
		
	def findItemsByIDsFromNKCK( self, itemIDs ):
		"""
		����ͨ���������ϻ������ ID Ϊ itemID �ĵ���ʵ���б�
		���԰�����

		@param itemID: ��ƷID
		@type  itemID: ITEM_ID
		@return: ��������ͬ����Ʒʵ���б�
		@rtype:  List of CItemBase instance
		"""
		return self.findItemsByIDsEx( csconst.KB_SEARCH_COMMON_AND_CASKET, itemIDs )

	def findItemsByIDWithBindFromNKCK( self, itemID, isBinded ):
		"""
		����ͨ���������ϻ������ ID Ϊ itemID �ĵ���ʵ���б�
		���ǰ�����

		@param itemID: ��ƷID
		@type  itemID: ITEM_ID
		@param isBinded: ��Ʒ�Ƿ��
		@type  isBinded: BOOL
		@return: ��������ͬ����Ʒʵ���б�
		@rtype:  List of CItemBase instance
		"""
		return [ item for item in self.findItemsByIDEx( csconst.KB_SEARCH_COMMON_AND_CASKET, itemID ) if item.isBinded() == isBinded ]

	def getItemsFK( self, itemID, kitbagID ):
		"""
		��ָ�������л�ȡIDΪItemID����Ʒʵ���б�
		���԰�����
		@param itemID: ��ƷID
		@type  itemID: ITEM_ID
		@return: ��������ͬ����Ʒʵ���б�
		@rtype:  List of CItemBase instance
		"""
		items = []
		for item in self.getItems( kitbagID ):
			if item.id == itemID:
				items.append( item )
		return items

	def getItemsFKWithBind( self, itemID, kitbagID, isBinded ):
		"""
		��ָ�������л�ȡIDΪItemID����Ʒʵ���б�
		���ǰ�����
		@param itemID: ��ƷID
		@type  itemID: ITEM_ID
		@param kitbagID: ����λID
		@type  kitbagID: INT8
		@param isBinded: ��Ʒ�Ƿ��
		@type  isBinded: BOOL
		@return: ��������ͬ����Ʒʵ���б�
		@rtype:  List of CItemBase instance
		"""
		items = []
		for item in self.getItems( kitbagID ):
			if item.id == itemID and item.isBinded() == isBinded:
				items.append( item )
		return items

	def checkItemsPlaceIntoNK_( self, itemList ):
		"""
		�Ƿ��ܰ�һ����Ʒ���뱳���У����жϸ���addItem_()�����Ĳ�����ʽ�������Ƿ����㹻λ�á�

		@param itemList: list of ITEM as [item1, item2, ...]
		@type  itemList: list of ITEM
		@return: INT8, 0 == True����Ϊ0��ʾ����Ĵ���ԭ��
		@rtype:  INT8
		"""
		# �����ҽ���ӵ�����޵Ĵ�����Ʒ
		if not self.checkItemLimit( itemList ):
			return csdefine.KITBAG_ITEM_COUNT_LIMIT

		freeOrder = self.getNormalKitbagFreeOrderCount()
		# in here, ���ܻ�Ҫ������Ʒ�Ƿ��ܷŽ������
		# �����ڵ�ʲô��Ʒ�����Էŵ�������Ļ�����˵������Ҫ�жϡ�
		# ע����ʹ�����´����ԭ����Ϊ�˽���ʵ������ע����˵���ж�ʱ�������bug
		#if itemCount <= freeOrder: return True

		# ����Ҫ���뱳������Ʒ��������¼ÿһ����Ʒ���뱳����ı������м�״̬��
		# ����ݴ��м�״̬�ж����µ�ÿһ����Ʒ�Ƿ��ܼ��뱳����11:02 2010-3-1��wsf
		# ���Կ���дһ��classʵ��ӵ��freeOrder��ģ�ⱳ������ΪЧ�ʼ�ֱ�ӰѴ����������ʵ�ֵ��߼���һ���ġ�
		totalItemDict = {}		# ��Ʒ����ͳ�ƣ��Ա������ֻ��ӵ��ĳ��������Ʒ����
		stackableItemDict = {}	# ���ڼ�¼�Ѿ������ѵ��ӵ������е���Ʒ���� {( itemID, isBinded ):amount, ...  }���Ա��ж��ټ���ͬ����Ʒ�Ƿ��ܵ��ӳɹ�
		needOrderItemList = []	# ģ����Ʒ���뱳����λ��Ĵ˿�λ���м�״̬
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
				if self.canStackable( itemID, isBinded, hasAmount ):	# ���Ե���
					stackableItemDict[( itemID, isBinded )] += amount
				else:	# ��������Ե��ӵĻ�����ô�ͼ�������Ʒʱ�Ƿ��ܹ�����
					isStackable = False
					key = ( itemID, isBinded )
					tempList = []	# �����뱳���еĿɵ�����Ʒ�б������ж��Ƿ�����ڼ��뱳��ǰ����
					tempAmount = amount
					for itemDict in needOrderItemList:	# �Ƿ���Ѿ�ռһ��λ�õ�ͬ����Ʒ����
						itemAmount = itemDict["amount"]
						if itemDict["key"] == key:
							if itemAmount + tempAmount <= stackable:
								tempList.append( itemDict )
								isStackable = True
								break
							else:
								tempList.append( itemDict )
								tempAmount -= stackable - itemAmount
					if isStackable:		# ���Ե��ӵ�δ���뱳������Ʒ��
						for itemDict in tempList:
							space = stackable - itemDict["amount"]
							if amount <= space:
								itemDict["amount"] += amount
								break
							else:
								itemDict["amount"] = stackable
								amount -= space
					else:				# û�е��ӳɹ�������һ������
						needOrderItemList.append( {"key":(itemID, isBinded),"amount":amount} )
			else:	# ����ǲ��ɵ�����Ʒ��ôҲռһ������
				needOrderItemList.append( {"key":(itemID, isBinded),"amount":amount} )

		if len( needOrderItemList ) <= freeOrder:
			return csdefine.KITBAG_CAN_HOLD
		else:
			return csdefine.KITBAG_NO_MORE_SPACE

	def checkItemLimit( self, itemList ):
		"""
		���һЩ��Ʒ�Ƿ������ҵı�����ֻ�����������
		����Ƕ����ͬID����Ʒ��ֻҪ��һ�����������������ܷ���
		@param item: �̳���CItemBase���Զ������ʵ��
		@type item: itemInstance
		@return Bool
		"""
		# ��¼ {��ƷID��(����,�����)}��dict
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
		����λΪkitOrder�İ����Ƿ��ܹ�����itemID����Ʒ�����Կո�
		��������п�λ�ö�û�д���Ʒ��Ȼ�㲻�ɵ���,���ⲿ��ӵ�����ȥ��

		@param itemID: �̳���CItemBase���Զ������ʵ����id
		@pram bindType : ��Ʒ�İ�����
		@param  iamount: �����Ʒ������
		@param  kitOrder: ����λ
		@return:             �ɹ��򷵻�True������ɹ�������Զ�֪ͨclient��ʧ���򷵻�False
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
		for e in items:	currtotal += e.getAmount()	# �������
		return len( items ) * stackable - currtotal >= amount

	def canStackable( self, itemID, isBinded, iamount ):
		"""
		���ر����Ƿ������ȫ���������Ʒ ���Կո�(��������п�λ�ö�û�д���Ʒ��Ȼ�㲻�ɵ���,���ⲿ��ӵ�����ȥ)
		@param itemID: �̳���CItemBase���Զ������ʵ����id
		@param bindType : �����Ʒ�İ�����
		@param  iamount: �����Ʒ������
		@return:             �ɹ��򷵻�True������ɹ�������Զ�֪ͨclient��ʧ���򷵻�False
		@rtype:              BOOL
		"""
		currtotal = 0
		stackableUpperCount = 0
		r = self.findItemsByIDFromNKCK( itemID )
		if r == []:	return False	# ����û�д���Ʒ,���ܽ��е��� Ӧ�����������
		stackable = r[0].getStackable()
		for e in r:
			if not e.isFrozen() and e.isBinded() == isBinded:
				stackableUpperCount += stackable
				currtotal += e.getAmount()	# �������
		return stackableUpperCount - currtotal >= iamount

	def isEmptyHand( self ):
		"""
		�ж��Ƿ�Ϊ����(��ֻ�ֶ�ûװ������)
		"""
		return self.getItem_( ItemTypeEnum.CWT_RIGHTHAND ) is None and self.getItem_( ItemTypeEnum.CWT_LEFTHAND ) is None

	def primaryHandEmpty( self ):
		"""
		�ж������Ƿ�Ϊ��

		@return: BOOL
		"""
		if self.itemsBag.getByOrder( ItemTypeEnum.CWT_RIGHTHAND ) is None: #�������Ϊ��
			return True
		else:
			hardiness = self.getItem_( ItemTypeEnum.CWT_RIGHTHAND ).query("eq_hardiness")
			if hardiness <= 0: #����;ö�Ϊ0
				return True
			else:
				return False

	def canWieldEquip( self, order, itemInstance ):
		"""
		�ж��Ƿ�����ĳһλ��װ��һ����Ʒ
		"""
		# ��ƷΪ�գ�����װ��
		if itemInstance is None: return csstatus.KIT_EQUIP_NOT_FIT_EQUIP
		# ��Ʒ���Ͳ���װ��������װ��
		if not itemInstance.isEquip(): return csstatus.KIT_EQUIP_NOT_FIT_EQUIP
		if not itemInstance.canWield( self ): return csstatus.KIT_EQUIP_NOT_FIT_EQUIP
		if itemInstance.getType() not in ItemTypeEnum.EQUIP_TYPE_SET: return csstatus.KIT_EQUIP_NOT_FIT_EQUIP
		# �����������������װ��
		if self.intonating(): return csstatus.KIT_EQUIP_INTONATE_CANT_OPERATER
		# װ����λ�ò��ڸ���Ʒ��װ��λ���ϣ� ����װ��
		if order not in itemInstance.getWieldOrders():
			return csstatus.KIT_EQUIP_CANT_APP_ORDER
		unwieldList = itemInstance.getUnwieldOrders( self.itemsBag, order )
		# �����Ҫж�¶���һ����װ����ʧ��
		special = [ ItemTypeEnum.ITEM_WEAPON_SPEAR2, ItemTypeEnum.ITEM_WEAPON_SHIELD ]
		if itemInstance.getType() not in special  and len( unwieldList ) > 1:
			return csstatus.KIT_EQUIP_NOT_FIT_EQUIP
		# ֻ��Ҫж��һ��װ��ʱ�ͱ����ж�ж�µ�װ��λ���뽻����λ���Ƿ�һ��
		if itemInstance.getType() not in special  and len( unwieldList ) == 1 and  unwieldList[0] != order:
			return csstatus.KIT_EQUIP_NOT_FIT_EQUIP
		return csstatus.KIT_EQUIP_CAN_FIT_EQUIP

	def order2uid( self, order ):
		"""
		ͨ�� order  ��ȡ uid
		@param order: λ��
		@type  order: INT16
		@return:        big than 0 if uid is found, else return -1
		@rtype:         INT
		"""
		return self.itemsBag.getUid( order )

	def uid2order( self, uid ):
		"""
		ͨ�� uid ��ȡ orderID
		@param uid: λ��
		@type  uid: INT64
		@return:        big than 0 if orderID is found, else return -1
		@rtype:         INT
		"""
		return self.itemsBag.getOrderID( uid )

	def getRacehorseItem_( self, orderID ):
		"""
		����order��ȡ�����ϵ�ĳ����

		@param orderID: �����ڱ������λ��
		@type  orderID: INT16
		@return:        �̳���CItemBase���Զ������͵���ʵ�����Ҳ����򷵻�None
		@rtype:         class instance/None
		"""
		return self.raceItemsBag.getByOrder( orderID )

	def getUnBindEquips( self ):
		"""
		��ȡδ�󶨵�װ��

		@return:        �̳���CItemBase���Զ������͵���ʵ���б��Ҳ����򷵻�[]
		@rtype:         class instance/None
		"""
		equips = self.getItems( csdefine.KB_EQUIP_ID )
		return [ equip for equip in equips if not equip.isBinded() ]

	def getUnObeyEquips( self ):
		"""
		��ȡδ����װ�� by����

		@return:        �̳���CItemBase���Զ������͵���ʵ���б��Ҳ����򷵻�[]
		@rtype:         class instance/None
		"""
		equips = self.getItems( csdefine.KB_EQUIP_ID )
		return [ equip for equip in equips if not equip.isObey() ]

# ItemBagRole.py

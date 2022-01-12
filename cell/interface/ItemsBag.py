# -*- coding: gb18030 -*-
#
# $Id: ItemsBag.py,v 1.133 2008-09-02 00:54:37 songpeifang Exp $

"""
@summary				:	����ģ��
"""

import time			# wsf
import cschannel_msgs
import ShareTexts as ST
import BigWorld
import Language
import csdefine
import csconst
import csstatus
import ChatObjParser
import ECBExtend
import items
import ItemTypeEnum
from bwdebug import *
from MsgLogger import g_logger
from ItemBagRole import ItemBagRole
from RoleSwapItem import RoleSwapItem
from RoleTradeWithNPC import RoleTradeWithNPC
from RoleTradeWithMerchant import RoleTradeWithMerchant
from RoleVend import RoleVend
import Math
from items.CueItemsLoader import CueItemsLoader
import sys
import Const
import csstatus_msgs
g_cueItem = CueItemsLoader.instance()

g_items = items.instance()


class ItemsBag( ItemBagRole, RoleSwapItem, RoleTradeWithNPC, RoleTradeWithMerchant, RoleVend ):
	"""
	����һ�������� for role of cell only��

	�����ڳ�ʼ��ʱ���Զ���鱳���������ֶ������client��

	@ivar kitbags: һ����Ʒ�б������洢��Ʒ
	@type kitbags: ITEMS
	@ivar mySIState:	1111 1111 -> ��4λ��ʾĿ��, ��4λ��ʾ�Լ�
						- 0	û�н���
						- 1	����������,��ʾ������ȷ��,�ȴ�ȷ��Ŀ��
						- 2	������,��ʽ��ʼ����
						- 3	ȷ��
						- 4	�ٴ�ȷ��
						- 5	ȷ����������Ϊ��ֵʱ�����ٽ���ȡ������Ҫ��
	@type mySIState: UINT8


	kitbagsLockerStatus��ʾ����������״̬�����ݣ���������״̬���Է����ɴ����ݲ�ѯ�ó�������Ҫ��def��������������ݡ��������£�
	kitbagsLockerStatusλ��Ϊ8��ʹ�����ֽ�ģʽ�ұߵĵ�һλ����ʾ�����Ƿ����������״̬����λ�ֽ�ģʽΪ0ʱ��ʾ��������Ϊ1ʱ��ʾ������
	ʹ���ұߵڶ�λ����ʾ�����Ƿ�������״̬���ݣ�������Ϊ0������Ϊ1���ұߵ�������λ�����Ժ���չ��Ҫ��
	ʹ�����ұߵ��塢������λ����ʾ������������ʧ�ܴ������ݣ������Ա�ʾ7��ʧ�ܣ����ֽ�ģʽΪ111��kitbagsLockerStatus����4λ�������ɵò������ݣ�
	ÿʧ��һ�ο�����λ�����+1��10�������㡣

	����������״̬����kitbagsLockerStatus��״̬���£�����ʵ��ʱ�ɲο�����
	0000 0000:������״̬
	0000 0001:������״̬
	0000 0010:����״̬
	0111 0000:��������ʧ�ܴ���
	
	kitbags :����������İ�����һ����Ʒ����������װ������14�����ӣ���ԭʼ������42�����ӣ���3��С�������Ӳ�����
	kitbag  :������������װ������ԭʼ������С����kitbags����kitbag��ɵ�,��һ������
	kbItem  :�������͵���Ʒ
	itemsBag:��Ʒ������ָ�����������а���������İ�����һ����Ʒ����������Ʒ����
	kitTote :����λ��ԭʼ���������3������λ
	item    :��ָ�����е���Ʒ
	"""
	def __init__( self ):
		"""
		"""
		RoleVend.__init__( self )

		#self.kitbagsPassword			# �������������ݣ�������def�ļ���
		#self.kitbagsUnlockLimitTime	# ���Ʊ���������Ϊʱ�䣬������def�ļ���

		# ��ʼ������������״̬
		if self.kitbagsPassword:		# �����������������
			self.kitbagsLockerStatus |= 0x03	# ���ֽ�ģʽ����Ϊ00000011

		if self.kitbagsForceUnlockLimitTime > 0 :	# ������������ǿ�ƽ���
			now = int( time.time() )
			forceUnlockLeaveTime = self.kitbagsForceUnlockLimitTime - now
			if forceUnlockLeaveTime <= 0 : 			# ���ǿ�ƽ���ʱ���ѵ�
				self.__forceUnlockKitbag()			# ǿ�ƽ�������
			else :
				self.__addForceUnlockTimer()		# �������ǿ�ƽ�����Timer

	def onDestroy( self ):
		"""
		�����ٵ�ʱ����������
		"""
		pass

	# -----------------------------------------------------------------------------------------------------
	# ��������
	# -----------------------------------------------------------------------------------------------------
	def __addItem( self, orderID, itemInstance, reason ):
		"""
		����������Ʒ
		"""
		if self.itemsBag.add( orderID, itemInstance ):
			try:
				uid = itemInstance.uid
				fullName = itemInstance.fullName()
				id = itemInstance.id
				amount = itemInstance.getAmount()
				g_logger.itemAddLog( self.databaseID, self.getName(), self.grade, reason, uid, fullName + "(%s)"%id, amount, self.getLevel() )	#������Ʒ
			except:
				g_logger.logExceptLog( GET_ERROR_MSG()  )
			return True
		else:
			return False
	
	def __removeItem( self, orderID, itemInstance, reason ):
		"""
		ɾ��ĳ��Ʒ
		"""
		if self.itemsBag.removeByOrder( orderID ):
			uid = itemInstance.uid
			fullName = itemInstance.fullName()
			id = itemInstance.id
			amount = itemInstance.getAmount()
			try:
				g_logger.itemDelLog( self.databaseID, self.getName(), self.grade, reason, uid, fullName + "(%s)"%id, amount )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG()  )
					
			return True
		else:
			return  False

	# -----------------------------------------------------------------------------------------------------
	# �����Ʒ
	# -----------------------------------------------------------------------------------------------------
	def requestItems( self ) :
		"""
		��������Ʒ���ͻ���( hyw -- 2008.06.10 )
		"""
		self.setTemp( "itemsbag_init_item_order", 0 )
		self.addTimer( 0.0, csconst.ROLE_INIT_INTERVAL, ECBExtend.UPDATE_CLIENT_ITEMS_CBID )

	def onTimer_updateClientItems( self, timerID, cbid ) :
		"""
		�ְ�������Ʒ( hyw -- 2008.06.10 )
		"""
		items = self.itemsBag.getDatas()
		count = len( items )
		startOrder = self.queryTempInt( "itemsbag_init_item_order" )
		endOrder = min( count, startOrder + 5 )							# ÿ�η� 5 ��
		for order in xrange( startOrder, endOrder ) :					# һ�η�һС����Ʒ
			item = items[order]
			if cschannel_msgs.ROLE_INFO_12 in item.name():									# �ж��Ƿ��д�Ѫ��Ʒ
				self.showBloodItemFlag()								# ����д�Ѫ��Ʒ�����ҽ��д���
			if item.id == 50201256 :									# ����Ģ��,���ͷ����Ҫ��ʾĢ�����
				self.tong_showFungusFlag()
			self.client.addItemCB( item )
		if endOrder < count :											# �������ʣ����Ʒ
			self.addTempInt( "itemsbag_init_item_order", 5 )			# ������ָ������ 5 ��
		else :															# ���û��ʣ����Ʒ
			self.cancel( timerID )										# ɾ������ timer
			self.removeTemp( "itemsbag_init_item_order" )				# ɾ����ʱ����ָ��
			self.client.onInitialized( csdefine.ROLE_INIT_ITEMS )		# ���ͽ�������ͻ���

	def requestKitbags( self ) :
		"""
		�����ͱ�����Ʒ���ͻ���( hyw -- 2008.06.10 )
		"""
		for order, item in self.kitbags.iteritems() :
			self.client.addKitbagCB( order, item )
		self.client.onInitialized( csdefine.ROLE_INIT_KITBAGS )

	# -------------------------------------------------
	def addItem( self, itemInstance, reason ):
		"""
		Define method.
		���Լ�����һ�����ߣ����ʧ������ߵ��ڵ��ϡ�

		@param itemInstance: ��CItemProp���ͽ��͵��Զ������͵���ʵ��
		@type  itemInstance: instance
		@return:             �������ķ�����û�з���ֵ
		"""
		self.addItemAndNotify_( itemInstance, reason )
		# ʧ������������
		#itemInstance.createEntity( self.spaceID, Math.Vector3( self.position ), self.direction )

	def addItem_( self, itemInstance, reason ):
		"""
		description: ����ĳ������ʵ��,������ʾ�õ�xx��Ʒ��Ҫ��˳����ʾ����ʹ��addItemAndNotify_
		@param itemInstance	: �̳���CItemBase���Զ������ʵ��
		@type  itemInstance	: CItemBase
		@return				: �ɹ��򷵻سɹ�״̬�룬����ɹ�������Զ�֪ͨclient��ʧ���򷵻�ԭ��
		@rtype				: INT8
		"""
		if itemInstance is None: return csdefine.KITBAG_ADD_ITEM_FAILURE
		# phw: ������Ʒuid�ظ�����־���Ա����պ�����쳣��־ʱ���׷���
		# �������ﲻ��if���жϣ�����assert
		# ��ʵ֤��������ȷʵ�ػ��˲���uid��ͬ����Ʒ���뱳����
		# ��ˣ���������������ĳЩ���뻹�Ǵ������⡣
		try:
			assert not self.itemsBag.hasUid( itemInstance.uid ), \
				"%s(%i): item uid duplicate. itemUID %s, srcItemID %s, dstItemID %s" % (
				self.getName(), self.id, itemInstance.uid, self.itemsBag.getByUid( itemInstance.uid ).id, itemInstance.id )
		except:
			EXCEHOOK_MSG()
			return csdefine.KITBAG_ADD_ITEM_FAILURE

		# ������Ʒ֮ǰ�����ʰȡ�󶨻����������ʱ�ı����״̬���Ա���ȷ�ļ��뱳�����������ʧ�ܣ�����Ҫȡ���󶨡�9:40 2009-2-25��wsf
		bindType = itemInstance.getBindType()
		needCancelBindType = False
		if not itemInstance.isBinded() and bindType in [ ItemTypeEnum.CBT_PICKUP, ItemTypeEnum.CBT_QUEST ]:
			itemInstance.setBindType( bindType )
			needCancelBindType = True

		# �ж��Ƿ���߿ɵ���
		if itemInstance.getStackable() > 1:
			if self.stackableItem( itemInstance, reason ) == csdefine.KITBAG_STACK_ITEM_SUCCESS:
				self.questItemAmountChanged( itemInstance, itemInstance.getAmount() )
				return csdefine.KITBAG_ADD_ITEM_BY_STACK_SUCCESS

		# ����ȡһ����λ��
		orderID = self.getNormalKitbagFreeOrder()
		if orderID == -1:
			if needCancelBindType:
				itemInstance.cancelBindType()
			return csdefine.KITBAG_NO_MORE_SPACE

		# ��󽻸�addItemByOrder_����
		addState = self.addItemByOrder_( itemInstance, orderID, reason )
		if addState != csdefine.KITBAG_ADD_ITEM_SUCCESS:
			if needCancelBindType:
				itemInstance.cancelBindType()
		return addState

	def addItemAndNotify_( self, itemInstance, reason ):
		"""
		description:�����Ʒ����������ʾ��Ϣ
		"""
		addResut = self.addItem_( itemInstance, reason )
		if addResut in csconst.KITBAG_ADD_ITEM_SUCCESS_RESULTS:
			self.notifyPickupInfo( itemInstance, reason )
			self.client.playIconNotify( itemInstance )
			return True
		return False

	def addItemByOrder_( self, itemInstance, orderID, reason ):
		"""
		description: ��ָ��λ�ü���ĳ������ʵ��
		@param itemInstance: �̳���CItemBase���Զ������ʵ��
		@type  itemInstance: CItemBase
		@param orderID: �����ڱ������λ��
		@type  orderID: INT16
		@return:             �ɹ��򷵻سɹ���״̬�룬����ɹ�������Զ�֪ͨclient��ʧ���򷵻صײ㷵�ص�״̬��
		@rtype:              INT8
		"""
		# �����Ʒ��������
		if not self.checkItemLimit( [itemInstance] ):
			return csdefine.KITBAG_ITEM_COUNT_LIMIT

		# ����Ҫ�����λ���Ǳ��� ��Ա�����ʣ��ʱ�����ж� �������ܼ��� by����
		dstKitID = orderID/csdefine.KB_MAX_SPACE
		kitItem = self.kitbags.get( dstKitID )

		# �жϱ���ʹ������ ���ڱ���ֻ����
		if kitItem.isActiveLifeTime():
			if time.time() > kitItem.getDeadTime():
				self.statusMessage( csstatus.CIB_MSG_TIME_OUT, kitItem.name() )
				return csdefine.KITBAG_ADD_ITEM_FAILURE

		# �˺�����������Ʒʵ���ӽ�����
		addResult = self.__addItem( orderID, itemInstance, reason )
		# ���صײ��״̬����ʱ���ڵײ�ֻ����0��1�����Բ���ô��
		if not addResult:
			return csdefine.KITBAG_ADD_ITEM_FAILURE
		self.questItemAmountChanged( itemInstance, itemInstance.getAmount() )
		self.client.addItemCB( itemInstance )
		# ��Ʒ������Ұ�������
		itemInstance.onAdd( self )
		self.kitbags_saveLater()
		return csdefine.KITBAG_ADD_ITEM_SUCCESS

	def addItemByOrderAndNotify_( self, itemInstance, orderID, reason ):
		"""
		description:��ָ��λ�������Ʒ����������ʾ��Ϣ
		�����Ҫ�����Լ�����ʾ����ֱ�ӵ���addItemByOrder_
		"""
		addResut = self.addItemByOrder_( itemInstance, orderID, reason )
		if addResut == csdefine.KITBAG_ADD_ITEM_SUCCESS:
			self.notifyPickupInfo( itemInstance, reason )
			return True
		return False

	def addItemAndRadio( self, itemInstance, itemAddType = ItemTypeEnum.ITEM_GET_GM,  itemFromSpace = "", itemFromOwner = "", stuffItemName = "", insLevel = "", reason = csdefine.ITEM_NORMAL ):
		"""
		���һ����Ʒ�����㲥
		@param itemInstance	: �̳���CItemBase���Զ������ʵ��
		@type  itemInstance	: CItemBase
		@param itemAddType	: ��Ʒ�Ļ�÷�ʽ
		@type  itemAddType	: UINT8
		@param itemFromSpace: ��Ʒ�Ĳ�����
		@type  itemFromSpace: STRING
		@param itemFromOwner: ��Ʒ�Ĳ�����
		@type  itemFromOwner: STRING
		"""
		#װ��ǿ��ʹ��������ӷ�ʽ �����ӷ�ʽ���ʺ� by����
		if not itemAddType in [ ItemTypeEnum.ITEM_GET_EQUIP_INSTENSIFY, ItemTypeEnum.ITEM_GET_STUD ]:
			if not self.addItemAndNotify_( itemInstance, reason ): return False
			# �������棬������True
			if itemAddType == ItemTypeEnum.ITEM_GET_GM: return True
			if not g_cueItem.hasCueFlag( itemInstance.id, itemAddType ): return True
		else:
			if itemAddType == ItemTypeEnum.ITEM_GET_GM: return True
		msg = g_cueItem.getCueMsg( itemAddType )
		if msg is None: return True
		roleName = self.getName()
		itemName = itemInstance.fullName()
		# ������Ʒ������ɫ�ĸı�
		itemName = csconst.ITEM_BROAD_COLOR_FOR_QUALITY[ itemInstance.getQuality() ] % itemName
		itemAmount = itemInstance.getAmount()
		i_Count = msg.count( "_t" ) + msg.count( "_i" )
		link_items = []
		if i_Count > 0:
			d_item = ChatObjParser.dumpItem( itemInstance )	# ������Ʒ��Ϣ����
			for i in xrange( 0, i_Count ):
				link_items.append( d_item )
		msg = g_cueItem.getCueMsgString( _keyMsg = msg, _p = roleName, _a = itemFromSpace, _m = itemFromOwner, _i = "${o0}", _n = str( itemAmount ), _t = "${o0}", _s = stuffItemName, _q = insLevel )
		self.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "", msg, link_items )
		return True

	def stackableItem( self , itemInstance, reason, kitTote =-1  ):
		"""
		description:��Ʒ������ǰ���еĲ����������ܷ��뱳���е�ĳ����Ʒ���ӡ�
					kitTote ==-1����ʾ�����б���������ͬ��Ʒ����
					kitTote !=-1����ʾ��ָ������������ͬ��Ʒ����
		@param itemInstance: �̳���CItemBase���Զ������ʵ��
		@type  itemInstance: CItemBase
		@param kitTote: �����ı��
		@type  kitTote: INT8
		@return: ���ӽ��
		@rtype:  INT8
		"""
		# �����Ʒ��������
		if not self.checkItemLimit( [itemInstance] ):
			return csdefine.KITBAG_ITEM_COUNT_LIMIT

		itemList = []
		# �������
		currtotal = 0
		# ������������
		stackable = itemInstance.getStackable()
		itemAmount = itemInstance.getAmount()
		itemID = itemInstance.id
		# �Ƿ��
		isBinded = itemInstance.isBinded()
		# �ж��Ƿ��ܵ���

		if kitTote != -1:
			if not self.canStackableInKit( itemID, isBinded, itemAmount, kitTote ):
				return csdefine.KITBAG_ADD_ITEM_FAILURE
			# ����ָ��ID������λ�������ͻ�ȡ��Ʒʵ���б�
			itemList = self.getItemsFKWithBind( itemID, kitTote, isBinded )
		else:
			if not self.canStackable( itemID, isBinded, itemAmount ):
				return csdefine.KITBAG_ADD_ITEM_FAILURE
			# ����ָ��ID������λ�������ͻ�ȡ��Ʒʵ���б�
			itemList = self.findItemsByIDWithBindFromNKCK( itemID, isBinded )
		# ����
		currtotal = sum( [ k.getAmount() for k in itemList if not k.isFrozen() ] )

		if len( itemList ) == 0:
			return csdefine.KITBAG_STACK_ITEM_NO_SAME_ITEM

		val = len( itemList ) * stackable - currtotal		# ��ȡ�����Ե��ӵ�����
		val1 = itemInstance.getAmount()				# ��ȡ�����Ʒ������
		if val < val1:
			return csdefine.KITBAG_STACK_ITEM_NO_MORE
		for item in itemList:
			if item.isFrozen(): continue
			if val1 <= 0:break
			amount = stackable - item.getAmount()
			if amount > 0:
				if amount >= val1:
					item.setAmount( item.getAmount() + val1, self, reason )
					break
				else:
					item.setAmount( stackable , self, reason )
					val1 -= amount
		return csdefine.KITBAG_STACK_ITEM_SUCCESS


	def addItemByItemIDWithAmount( self, itemDict, bindType, reason ):
		"""
		ͨ����ƷIDΪ����������б����ݣ���������������ӣ�һϵ�У���Ʒ by ����
		����ǰ��Ҫ���ղ�����ʽ��װ����Ʒ��Ϣ
		���ڲ��ܼ��뱳��������ռ�����������Ʒ����󷵻�
		@param itemDict : { itemID:Amount, ... }
		@type  itemDict : DICT
		@param isAllBinded : ������
		@type : INT8
		"""
		if type( itemDict ) is not dict: return
		if len( itemDict ) <= 0: return
		itemList = []
		for idt in itemDict:
			item = g_items.createDynamicItem( idt )
			if item is None: continue
			item.setAmount( itemDict[idt] )
			item.setBindType( bindType )
			itemList.append( item )

		checkRes = self.checkItemsPlaceIntoNK_( itemList )
		if checkRes != csdefine.KITBAG_CAN_HOLD: return itemList
		for item in itemList: self.addItem( item, reason )
		return None

	# -----------------------------------------------------------------------------------------------------
	# �Ƴ���Ʒ
	# -----------------------------------------------------------------------------------------------------
	def removeItem_( self, orderID, amount = -1, reason = csdefine.DELETE_ITEM_NORMAL ):
		"""
		��ȥĳ����

		@param orderID: �����ڱ������λ��
		@type  orderID: INT16
		@param amount: ��Ҫɾ���ĵ��ߵ�����
		@type  amount: INT16
		@param reason: ɾ�����ߵ�ԭ��
		@type  reason: INT16
		@return:        �����Ʒ��ɾ���򷵻�True,���򷵻�False
		@rtype:         BOOL
		"""
		item = self.itemsBag.getByOrder( orderID )
		if item is None: return False
		deleteAmount = self.deleteItem_( orderID, amount, True, reason )
		if deleteAmount:
			d_item = ChatObjParser.dumpItem( item )
			msg = csstatus_msgs.getStatusInfo( csstatus.CIB_MSG_LOST_ITEMS, "${o0}", deleteAmount ).msg
			self.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSTEM, 0, "", msg, [d_item] )
		item = None # �ͷŵ�item

	def deleteItem_( self, orderID, amount = -1, questItemAmountChanged = True, reason = csdefine.DELETE_ITEM_NORMAL ):
		"""
		description: ɾ��ĳ����,û����ʾ��Ϣ
		@param orderID: �����ڱ������λ��
		@type  orderID: INT16
		@param amount: ��Ҫɾ���ĵ��ߵ�������Ĭ��Ϊ-1��������Ϊ����ʱ�����Ѹ�λ�õ���ȫ��ɾ����Ϊ0ʱ����Ϊ
		@type  amount: INT16
		@param questItemAmountChanged: �������Ӱ�죬��˵����ô���÷�������ʡ�����
		@type  questItemAmountChanged: BOOL
		@param reason: ɾ�����ߵ�ԭ��
		@type  reason: INT16
		@return:        �����Ʒ��ɾ���򷵻�ɾ��������,���򷵻�False
		@rtype:         INT8
		"""
		if amount == 0: return False
		itemInstance = self.itemsBag.getByOrder( orderID )
		if itemInstance is None: return False
		itemAmount = itemInstance.getAmount()
		if amount < 0:
			amount = itemAmount
		remain = itemAmount - amount

		if remain < 0:
			return False
		if remain == 0:
			result = self.__removeItem( orderID, itemInstance, reason )
			if not result :
				return False
				
			itemInstance.onDelete( self )
			self.client.removeItemCB( orderID )
		else:
			itemInstance.setAmount( remain, self, reason )

		if questItemAmountChanged:
			self.questItemAmountChanged( itemInstance, -amount )
			
		self.kitbags_saveLater()
		return amount

	def removeItemByUid_( self, uid, amount = -1, reason = csdefine.DELETE_ITEM_NORMAL ):
		"""
		��ȥĳ�����ϵ�ĳ����

		@param  uid: ������������ϵ�Ψһ��ʶ
		@type   uid: INT64
		@return:        �����Ʒ��ɾ���򷵻�True,���򷵻�False
		@rtype:         BOOL
		"""
		orderID = self.itemsBag.getOrderID( uid )
		if orderID < 0: return
		return self.removeItem_( orderID, amount, reason )

	def removeItemTotal( self, itemKeyName, amount, reason ):
		"""
		��ȥ��itemKeyName��ͬ����Ʒamount����

		@param itemKeyName: ��ʾÿһ����ߵ�Ψһ�ĵ�������
		@type  itemKeyName: str
		@param      amount: ��ɾ��������
		@type       amount: UINT16
		@return: �������ô�����ɾ���ұ�ɾ���򷵻�True�����򷵻�False
		@return: True
		"""
		if not self.checkItemFromNKCK_( itemKeyName, amount ): return False
		rm = amount
		for item in self.findItemsFromNKCK_( itemKeyName ):
			im = item.getAmount()
			if im <= rm:
				rm -= im
				item.setAmount( 0, self, reason )
				if rm == 0:
					self.questItemAmountChanged( item, -amount )
					msg = csstatus_msgs.getStatusInfo( csstatus.CIB_MSG_LOST_ITEMS, "${o0}", amount ).msg
					self.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSTEM, 0, "", msg, [ChatObjParser.dumpItem( item )] )
					return True
			else:
				item.setAmount( item.getAmount() - rm, self, reason )
				self.questItemAmountChanged( item, -amount )
				msg = csstatus_msgs.getStatusInfo( csstatus.CIB_MSG_LOST_ITEMS, "${o0}", amount ).msg
				self.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSTEM, 0, "", msg, [ChatObjParser.dumpItem( item )] )
				return True
		return False

	def removeItemTotalWithNoBind( self, itemKeyName, amount, reason ):
		"""
		��ȥ��itemKeyName��ͬ����δ�󶨵���Ʒamount����

		@param itemKeyName: ��ʾÿһ����ߵ�Ψһ�ĵ�������
		@type  itemKeyName: str
		@param      amount: ��ɾ��������
		@type       amount: UINT16
		@return: �������ô�����ɾ���ұ�ɾ���򷵻�True�����򷵻�False
		@return: True
		"""
		if self.countItemTotalWithBinded_( itemKeyName, False ) < amount: return False
		rm = amount
		for item in self.findItemsEx_( csconst.KB_SEARCH_COMMON_AND_CASKET, itemKeyName ):
			if item.isBinded():
				continue

			im = item.getAmount()
			if im <= rm:
				rm -= im
				item.setAmount( 0, self, reason )
				if rm == 0:
					self.questItemAmountChanged( item, -amount )
					self.statusMessage( csstatus.CIB_MSG_LOST_ITEMS,  item.name(), amount )
					return True
			else:
				item.setAmount( item.getAmount() - rm, self, reason )
				self.questItemAmountChanged( item, -amount )
				self.statusMessage( csstatus.CIB_MSG_LOST_ITEMS,  item.name(), amount )
				return True
		return False


	# -----------------------------------------------------------------------------------------------------
	# client call method
	# ---------------------------------------------------------------------------------------------
	# ʹ����Ʒ
	# ---------------------------------------------------------------------------------------------
	def useItem(self, srcEntityID, uid, targetObj ):
		"""
		Exposed method.
		��ĳ��ʹ��ĳ����

		@param srcEntityID: ʹ���ߣ�������self.idһ��
		@type  srcEntityID: int32
		@param  srcKitTote: ������λ��
		@type   srcKitTote: UINT8
		@param      uid: ����Ψһ��ʶ��
		@type       uid: INT64
		@param dstEntityID: Ŀ��
		@type  dstEntityID: int32
		@return:            �������ķ�����û�з���ֵ
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return False

		if self.iskitbagsLocked():
			DEBUG_MSG( "�����������ˡ�" )
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False
		dstEntity = targetObj.getObject()
		if targetObj.type != csdefine.SKILL_TARGET_OBJECT_POSITION:
			if dstEntity is None:
				self.statusMessage( csstatus.CIB_MSG_INVALID_TARGET )
				return False
			if dstEntity.isDestroyed:
				self.statusMessage( csstatus.CIB_MSG_INVALID_TARGET )
				return False
		dstItem = self.itemsBag.getByUid( uid )
		if dstItem is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return False

		if dstItem.isFrozen():
			WARNING_MSG( "error code: ", csstatus.CIB_MSG_FROZEN )
			return False
		useResult = dstItem.use( self, dstEntity )
		if useResult != csstatus.SKILL_GO_ON and useResult is not None:
			self.statusMessage( useResult )
			return False
		return True

	def destroyItem( self, srcEntityID, uid ):
		"""
		Exposed method.
		����һ����Ʒ

		@param srcEntityID: ����ʵ���ID��
		@type  srcEntityID: int32
		@param      uid: ����Ψһ��ʶ��
		@type       uid: INT64
		@return:            �������ķ�����û�з���ֵ
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False
		item = self.itemsBag.getByUid( uid )
		if item is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return False

		if item.isFrozen():
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			return False

		if not item.canDestroy():
			self.statusMessage( csstatus.CIB_MSG_CANNOT_DESTROY )
			return

		self.removeItemByUid_( uid, reason = csdefine.DELETE_ITEM_DESTROYITEM )
		return True

	def swapItem( self, srcEntityID, srcOrderID, dstOrderID ):
		"""
		Exposed method.
		�����������ߵ�λ�á�

		��Ҫ����Դ������Ŀ�걳�����ͣ��п�����Ҫ���ݲ�ͬ����������ͬ�Ĳ���

		@param srcEntityID: ����ʵ���ID��
		@type  srcEntityID: int32
		@param  srcOrderID: Դ������Դ����
		@type   srcOrderID: INT8
		@param  dstOrderID: Ŀ�걳����Դ����
		@type   dstOrderID: INT8
		@return:            �������ķ�����û�з���ֵ
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		self.swapItemAC( srcOrderID, dstOrderID )

	def swapItemAC( self, srcOrderID, dstOrderID ):
		"""
		�����������ߵ�λ�á�
		"""
		if self.iskitbagsLocked():
			DEBUG_MSG( "�����������ˡ�" )
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False
		srcKitID = srcOrderID/csdefine.KB_MAX_SPACE
		dstKitID = dstOrderID/csdefine.KB_MAX_SPACE
		kitItem = self.kitbags.get( dstKitID )

		# �жϱ���ʹ������ ���ڱ���ֻ����
		if kitItem.isActiveLifeTime():
			if time.time() > kitItem.getDeadTime():
				self.statusMessage( csstatus.CIB_MSG_TIME_OUT, kitItem.name() )
				return False

		if kitItem is None:
			self.statusMessage( csstatus.CIB_MSG_INVALID_KITBAG, dstKitID )
			return False

		srcItem = self.itemsBag.getByOrder( srcOrderID )
		dstItem = self.itemsBag.getByOrder( dstOrderID )
		# ��ֹ�����������ʱ����bug
		if srcItem is None:

			return False
		if (srcItem is not None and srcItem.isFrozen()) or (dstItem is not None and dstItem.isFrozen()):
			WARNING_MSG( "error code: ", csstatus.CIB_MSG_FROZEN )
			return False
		
		# �����Ʒ�Ǵ�װ���������ģ�����Ҫ����Ŀ����Ʒ�Ƿ��ܷ���װ����
		if srcKitID == csdefine.KB_EQUIP_ID:
			if self.actionSign( csdefine.ACTION_FORBID_WIELD ):
				self.statusMessage( csstatus.KIT_EQUIP_CANT_STATE )
				return False
			if dstItem:
				state = self.canWieldEquip( srcOrderID, dstItem )
				if state != csstatus.KIT_EQUIP_CAN_FIT_EQUIP:
					self.statusMessage( state )
					return False

		# �����ƷҪ�ŵ�װ�����ϣ�����Ҫ���Ǹ���Ʒ�Ƿ��ܷ���װ����
		if dstKitID == csdefine.KB_EQUIP_ID:
			if self.actionSign( csdefine.ACTION_FORBID_WIELD ):
				self.statusMessage( csstatus.KIT_EQUIP_CANT_STATE )
				return False
			state = self.canWieldEquip( dstOrderID, srcItem )
			if state != csstatus.KIT_EQUIP_CAN_FIT_EQUIP:
				self.statusMessage( state )
				return False
		
		weaponOrders = [ ItemTypeEnum.CEL_LEFTHAND, ItemTypeEnum.CEL_RIGHTHAND ]
		if self.getClass() == csdefine.CLASS_FIGHTER and ( srcOrderID in weaponOrders or dstOrderID in weaponOrders ):
			l_item = self.itemsBag.getByOrder( ItemTypeEnum.CEL_LEFTHAND )
			r_item = self.itemsBag.getByOrder( ItemTypeEnum.CEL_RIGHTHAND )
			orderIDs = self.getAllNormalKitbagFreeOrders()
			
			if srcKitID == csdefine.KB_EQUIP_ID : #�����Ʒ�Ǵ�װ����������
				if dstItem: #Ŀ�����װ������
					if srcItem.getType() != dstItem.getType(): #Ŀ�����װ����Դ����װ�����Ͳ�һ��
						if srcOrderID == ItemTypeEnum.CEL_LEFTHAND: #Դ����װ����������
							self.statusMessage( csstatus.KIT_EQUIP_CANT_APP_ORDER )
							return False
						else: #Դ����װ����������
							if l_item: #�����ж�
								if len( orderIDs ) < 1 :
									self.statusMessage( csstatus.CIB_MSG_UNWIELD_ITEM )
									return False
								else:
									flag1 = self.swapItemACBack( srcOrderID, dstOrderID )
									flag2 = self.swapItemACBack( ItemTypeEnum.CEL_LEFTHAND, orderIDs[0] )
									return flag1 and flag2
			
			if dstKitID == csdefine.KB_EQUIP_ID: #��ƷҪ�ŵ�װ������
				if dstItem: #Ŀ�����װ������
					if srcItem.getType() != dstItem.getType(): #Ŀ�����װ����Դ����װ�����Ͳ�һ��
						if dstOrderID == ItemTypeEnum.CEL_LEFTHAND: #Ŀ�����������
							self.statusMessage( csstatus.KIT_EQUIP_CANT_APP_ORDER )
							return False
						else: #Ŀ�����������
							if l_item: #�����ж�
								if len( orderIDs ) < 1 :
									self.statusMessage( csstatus.CIB_MSG_UNWIELD_ITEM )
									return False
								else:
									flag1 = self.swapItemACBack( srcOrderID, dstOrderID )
									flag2 = self.swapItemACBack( ItemTypeEnum.CEL_LEFTHAND, orderIDs[0] )
									return flag1 and flag2
				else:
					if l_item: #�����ж�
						if srcItem.getType() == ItemTypeEnum.ITEM_WEAPON_SPEAR2: #��װ��ǹ
							flag1 = self.swapItemACBack( srcOrderID, dstOrderID )
							flag2 = self.swapItemACBack( ItemTypeEnum.CEL_LEFTHAND, srcOrderID )
							return flag1 and flag2
					else: #�����޶�
						if srcItem.getType() == ItemTypeEnum.ITEM_WEAPON_SHIELD and r_item and r_item.getType() == ItemTypeEnum.ITEM_WEAPON_SPEAR2: #Ŀ�����������,��������Ϊǹ
							flag1 = self.swapItemACBack( srcOrderID, dstOrderID )
							flag2 = self.swapItemACBack( ItemTypeEnum.CEL_RIGHTHAND, srcOrderID )
							return flag1 and flag2	
		
		return self.swapItemACBack( srcOrderID, dstOrderID )
	
	def swapItemACBack( self, srcOrderID, dstOrderID ):
		"""
		�����������ߵ�λ�á�
		"""
		srcKitID = srcOrderID/csdefine.KB_MAX_SPACE
		dstKitID = dstOrderID/csdefine.KB_MAX_SPACE
		srcItem = self.itemsBag.getByOrder( srcOrderID )
		dstItem = self.itemsBag.getByOrder( dstOrderID )
		
		if self.itemsBag.swapOrder( srcOrderID, dstOrderID ):
			self.client.swapItemCB( srcOrderID, dstOrderID )
			# �������ͬ������λ�����˹��ܾͽ�����
			if srcKitID == dstKitID: return True
			# ��λ�ɹ��Ž���װ����֪ͨ�ͻ��˸���װ��ģ��
			newEquip = None
			if srcKitID == csdefine.KB_EQUIP_ID:
				if srcItem: srcItem.unWield( self, update = False )
				if dstItem is not None:
					dstItem.wield( self, update = False )
					newEquip = dstItem
				self.resetEquipModel( srcOrderID, newEquip )
			if dstKitID == csdefine.KB_EQUIP_ID:
				if dstItem: dstItem.unWield( self, update = False )
				if srcItem is not None:
					srcItem.wield( self, update = False )
					newEquip = srcItem
				self.resetEquipModel( dstOrderID, newEquip )
			# ���ż�������
			self.calcDynamicProperties()
			return True
		else:
			WARNING_MSG( "error code: ", csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False

	def splitItem( self, srcEntityID, uid, amount ):
		"""
		Exposed method.
		�ֿ�һ���ɵ��ӵĵ��ߡ�

		��Ҫ����Դ������Ŀ�걳�����ͣ��п�����Ҫ���ݲ�ͬ����������ͬ�Ĳ���

		@param srcEntityID: ����ʵ���ID��
		@type  srcEntityID: int32
		@param         uid: Դ������Դ���ߵ�ΨһID
		@type          uid: INT64
		@param      amount: ��ʾ��Դ��Ʒ����ֳ����ٸ���
		@type       amount: UINT16
		@return:             �������ķ�����û�з���ֵ
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return False

		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False

		srcItem = self.itemsBag.getByUid( uid )
		if srcItem is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return False

		if srcItem.isFrozen():
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			return False

		if amount < 1:
			self.statusMessage( csstatus.CIB_MSG_AMOUNT_CANT_BE_ZERO )
			return False

		if srcItem.getAmount() - amount < 1:
			self.statusMessage( csstatus.CIB_MSG_AMOUNT_TOO_BIG )
			return False

		if srcItem.getStackable() <= 1:
			self.statusMessage( csstatus.CIB_MSG_CANNOT_STACKABLE )
			return False

		freeOrder = self.getNormalKitbagFreeOrder()
		if freeOrder == -1:
			self.statusMessage( csstatus.CIB_MSG_ORDER_NOT_NULL )
			return False
		dstItem = srcItem.new()
		dstItem.setAmount( amount )
		srcItem.setAmount( srcItem.getAmount() - amount, self, csdefine.DELETE_ITEM_SPLITITEM )
		if self.__addItem( freeOrder, dstItem, csdefine.ADD_ITEM_SPLITITEM ):
			self.client.addItemCB( dstItem )
		return True

	def combineItem( self, srcEntityID, srcOrder, dstOrder ):
		"""
		Exposed method.
		��һ���������ĳ������������һ��������ĵ��ߺϲ���
		���磺����A���С��ҩˮ��100��������B��С��ҩˮ��20����С��ҩˮ��������Ϊ200��
		�����ǿ���ʹ�ô˷����ѱ���B��С��ҩˮ���ڱ���A��Կճ�һ��λ�á�

		@param srcEntityID: ����ʵ���ID��
		@type  srcEntityID: int32
		@param    srcOrder: Դ������Դ����
		@type     srcOrder: UINT8
		@param    dstOrder: Ŀ�걳����Դ����
		@type     dstOrder: UINT8
		@return:            �������ķ�����û�з���ֵ
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return False

		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False

		srcItem = self.itemsBag.getByOrder( srcOrder )
		dstItem = self.itemsBag.getByOrder( dstOrder )
		if ( srcItem is None ) or ( dstItem is None ):
			self.statusMessage( csstatus.CIB_MSG_SRC_DES_NOT_EXIST, srcOrder, dstOrder )
			return False

		if srcItem.isFrozen() or dstItem.isFrozen():
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			return False

		# ������ͬ���߲��������
		if srcItem.id != dstItem.id:
			self.statusMessage( csstatus.CIB_MSG_CANNOT_STACKABLE )
			return False

		if srcItem.isBinded() != dstItem.isBinded():	# ������Ʒ�Ƿ�󶨡�18:49 2009-2-16��wsf
			self.statusMessage( csstatus.BANK_BIND_TYPE_CANT_STACKABLE )
			return False

		stackable = dstItem.getStackable()
		# �������ĸ��������ֻ��Ŀ���Ƿ��ܵ���
		if stackable <= 1:
			self.statusMessage( csstatus.CIB_MSG_CANNOT_STACKABLE )
			return False
		dAmount = dstItem.getAmount()
		# ���Ŀ��ﵽ�ɵ������������ʲôҲ����,Ҳ����֪ͨ�ͻ���
		if dAmount == stackable:
			return False

		sAmount = srcItem.getAmount()
		# ���Ŀ����߿ɵ�������
		stackAmount = stackable - dAmount
		if stackAmount >= sAmount:
			newDstAmount = dAmount + sAmount
			newSrcAmount = 0
			srcItem.setAmount( newSrcAmount, self, csdefine.DELETE_ITEM_COMBINEITEM )
			dstItem.setAmount( newDstAmount, self, csdefine.ADD_ITEM_COMBINEITEM )
		else:
			newDstAmount = stackable
			newSrcAmount = sAmount - stackAmount
			srcItem.setAmount( newSrcAmount, self, csdefine.DELETE_ITEM_COMBINEITEM )
			dstItem.setAmount( newDstAmount, self, csdefine.ADD_ITEM_COMBINEITEM )

		return True

	def moveItemToKitTote( self, srcEntityID, srcOrder, dstKitTote ):	# wsf add��15:10 2008-6-10
		"""
		Exposed method.
		��һ����Ʒ�ϵ�����λ�İ����ϵĴ���Ŀǰ��ʱֻ������һ���ɵ�����Ʒ�ҿɵ��ӵ������е������
		param srcOrder:	���Ӻ�
		type srcOrder:	INT16
		param dstKitTote:��������λ��
		type dstKitTote:UINT8
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		kitItem = self.kitbags.get( dstKitTote )
		if kitItem is None:
			self.statusMessage( csstatus.CIB_MSG_INVALID_KITBAG, dstKitTote )
			return False

		srcItem = self.itemsBag.getByOrder( srcOrder )
		if srcItem is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return

		if srcItem.isFrozen():
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			return

		if dstKitTote < csdefine.KB_COMMON_ID or dstKitTote > csdefine.KB_CASKET_ID:
			HACK_MSG( "dstKitTote( %i ) not in kitbag id list." % dstKitTote )
			return

		if srcItem.getStackable() > 1:	# ����ǿɵ�����Ʒ
			if self.stackableItem( srcItem, csdefine.ADD_ITEM_STACK, dstKitTote ) == csdefine.KITBAG_STACK_ITEM_SUCCESS:	# ���ӳɹ�
				self.deleteItem_( srcOrder, questItemAmountChanged = False, reason = csdefine.DELETE_ITEM_STACK  )
				return
		else:	# ���ڲ��ɵ��ӵ���Ʒ���ͻ���Ŀǰ����ʹ�ô˽ӿڣ�����ʹ��swapOrder�ӿڡ�
			pass

	# ---------------------------------------------------------------------------------------------
	# ��Ʒ����
	# ---------------------------------------------------------------------------------------------
	def freezeItem_( self, order ):
		"""
		����һ����Ʒ

		@return: BOOL
		"""
		item = self.itemsBag.getByOrder( order )
		if item is None: return False
		return item.freeze( self )

	def unfreezeItem_( self, order ):
		"""
		����һ����Ʒ

		@return: ��
		"""
		item = self.itemsBag.getByOrder( order )
		if item is None: return False
		item.unfreeze( self )

	def freezeItemByUid_( self, uid ):
		"""
		����һ����Ʒ

		@return: BOOL
		"""
		orderID = self.itemsBag.getOrderID( uid )
		return self.freezeItem_( orderID )

	def unfreezeItemByUid_( self, uid ):
		"""
		����һ����Ʒ

		@return: ��
		"""
		orderID = self.itemsBag.getOrderID( uid )
		return self.unfreezeItem_( orderID )

	def notifyPickupInfo( self, itemInstance, reason ):
		"""
		��ͻ��˷��ͻ����Ʒ��Ϣ
		"""
		#chat_onChannelMessage( self.id, speaker.id, speaker.playerName, msg, blobArgs )

		d_item = ChatObjParser.dumpItem( itemInstance )

		if reason == csdefine.ADD_ITEM_LUCKYBOXZHAOCAI:
			msg = csstatus_msgs.getStatusInfo( csstatus.CIB_ZHAOCAI_ADD_REWARD, "${o0}" ).msg + "x%i"%( itemInstance.amount )
			self.statusMessage( csstatus.CIB_ZHAOCAI_ADD_REWARD, "[%s]" % itemInstance.fullName() )
		elif reason == csdefine.ADD_ITEM_LUCKYBOXJINBAO:
			msg = csstatus_msgs.getStatusInfo( csstatus.CIB_JINBAO_ADD_REWARD, "${o0}" ).msg + "x%i"%( itemInstance.amount )
			self.statusMessage( csstatus.CIB_JINBAO_ADD_REWARD, "[%s]" % itemInstance.fullName() )
		else:
			msg = csstatus_msgs.getStatusInfo( csstatus.CIB_MSG_GAIN_ITEMS, "${o0}", itemInstance.amount ).msg

		self.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSTEM, 0, "", msg, [d_item] )

	# ---------------------------------------------------------------------------------------------
	# �����������
	# ---------------------------------------------------------------------------------------------
	def moveKbItemToKitTote( self, srcEntityID, srcOrderID, dstKitTote ):
		"""
		Exposed method
		ת��ĳ���������͵ĵ���Ϊ����
		@param srcEntityID: ʹ���ߣ�������self.idһ��
		@type  srcEntityID: int32
		@param   srcOrderID: ����λ��
		@type    srcOrderID: INT16
		@param  dstKitTote: ������λ�ã���ʾ�µı����ŵ��ĸ�λ��
		@type   dstKitTote: INT8
		@return:            �������ķ�����û�з���ֵ
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		self.__itemToKitbag( srcOrderID, dstKitTote )
		
	def __itemToKitbag( self, srcOrderID, dstKitTote ):
		"""
		ת��ĳ���������͵ĵ���Ϊ����
		@param   srcOrderID: ����λ��
		@type    srcOrderID: INT16
		@param  dstKitTote: ������λ�ã���ʾ�µı����ŵ��ĸ�λ��
		@type   dstKitTote: INT8
		"""
		if self.iskitbagsLocked():
			DEBUG_MSG( "�����������ˡ�" )
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False

		srcItem = self.itemsBag.getByOrder( srcOrderID )
		if srcItem is None:
			self.statusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return False

		# �жϱ����Ƿ���� ���ڱ�������װ�� by����
		if srcItem.isActiveLifeTime():
			if time.time() > srcItem.getDeadTime():
				self.statusMessage( csstatus.CIB_ITEM_CANT_EQUIP_OVERTIME )
				return
		else:
			srcItem.activaLifeTime()

		if srcItem.isFrozen():
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			return

		itemType = srcItem.getType()
		if itemType not in ItemTypeEnum.KITBAG_LIST:
			freeOrder = self.getFreeOrderFK( dstKitTote )
			if freeOrder == -1:
				return False
			self.swapItemAC( srcItem.order, freeOrder )
			return True
		# ��������ϻ����ֻ�ܷ��ڵ�6������λ
		if itemType == ItemTypeEnum.ITEM_WAREHOUSE_CASKET and dstKitTote  != csdefine.KB_CASKET_ID:
			return False
		# �������ͨ��������ֻ�ܷ��ڵ�2-5������λ
		if itemType == ItemTypeEnum.ITEM_WAREHOUSE_KITBAG \
			and ( dstKitTote <= csdefine.KB_COMMON_ID or dstKitTote >= csdefine.KB_CASKET_ID ):
			return False

		sOrder = srcItem.order
		kitItem = None
		if self.kitbags.has_key( dstKitTote ):
			# ��鱳���Ƿ񱻶���
			kitItem = self.kitbags[dstKitTote]
			if kitItem.isFrozen():
				self.statusMessage( csstatus.CIB_MSG_FROZEN )
				return

			if itemType == ItemTypeEnum.ITEM_WAREHOUSE_CASKET:	# ��������У���������ж����Ͳ��ܻ�λ by ����
				if csdefine.KB_CASKET_ID in self.kitbags and self.getFreeOrderCountFK( csdefine.KB_CASKET_ID ) != self.kitbags[csdefine.KB_CASKET_ID].getMaxSpace():
					return False
			elif kitItem.getMaxSpace() >= srcItem.getMaxSpace():	# ���Ŀ������ռ�����û��İ����ռ䣬�����滻��17:37 2008-10-30 wsf
				self.statusMessage( csstatus.CIB_PLACE_EXIST_BIGER_BAG )
				return

		if self.__removeItem( sOrder, srcItem, csdefine.DELETE_ITEM_TO_KITBAG ):
			self.kitbags[dstKitTote] = srcItem
			srcItem.onWield( self )
			self.client.removeItemCB( sOrder )
			self.client.addKitbagCB( dstKitTote, srcItem )		# ֪ͨclient
			if kitItem:
				self.__addItem( sOrder, kitItem, csdefine.ADD_ITEM_TO_KITBAG )
				self.client.addItemCB( kitItem )
			return True
		return False

	
	def moveKitbagToKbItem( self, srcEntityID, srcKitTote, dstOrder ):
		"""
		Exposed method
		ת��ĳ������Ϊ�������͵ĵ���
		@param srcEntityID: ʹ���ߣ�������self.idһ��
		@type  srcEntityID: int32
		@param  srcKitTote: ������λ�ã���ʾ���ĸ����������ó�����
		@type   srcKitTote: INT8
		@param    dstOrder: �ŵ������ĸ�λ��
		@type     dstOrder: UINT8
		@return:            �������ķ�����û�з���ֵ
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		self.__kitbagToItem( srcKitTote, dstOrder )
	
	def __kitbagToItem( self, srcKitTote, dstOrder ):
		"""
		@param  srcKitTote: ������λ�ã���ʾ���ĸ����������ó���
		@type   srcKitTote: INT8
		@param    dstOrder: �ŵ������ĸ�λ��
		@type     dstOrder: UINT8
		"""
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False

		if srcKitTote == dstOrder/csdefine.KB_MAX_SPACE:
			self.statusMessage( csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False

		if srcKitTote in [ csdefine.KB_EQUIP_ID, csdefine.KB_COMMON_ID ]:
			# װ�����͵�һ��Ʒ�����ɱ�
			self.statusMessage( csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False

		kitItem = self.kitbags.get( srcKitTote )
		if kitItem is None:
			self.statusMessage( csstatus.CIB_MSG_INVALID_KITBAG, srcKitTote )
			return False

		if kitItem.isFrozen():
			self.statusMessage( csstatus.CIB_MSG_FROZEN )
			return False

		if len( self.getItems( srcKitTote ) ) != 0:
			# �����ǿգ������Ƴ�����Ϊ����
			self.statusMessage( csstatus.CIB_MSG_BAG_NOT_NULL )
			return False

		dstItem = self.itemsBag.getByOrder( dstOrder )
		if dstItem is not None:
			self.statusMessage( csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False

		if self.__addItem( dstOrder, kitItem, csdefine.ADD_ITEM_KITBAG_TO_ITEM ):
			del self.kitbags[srcKitTote]
			self.client.addItemCB( kitItem )
			self.client.removeKitbagCB( srcKitTote )

	def swapKitbag( self, srcEntityID, srcKitOrder, dstKitOrder ):
		"""
		Exposed method
		��������������λ��
		@param  srcKitOrder: Դ������λ
		@type   srcKitOrder: INT8
		@param  dstKitOrder: Ŀ�걳����λ
		@type   dstKitOrder: INT8
		@return:         ������󱻷����򷵻�True�����򷵻�False
		@rtype:          BOOL
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False

		# �ж�Դ����λ���Ƿ�Ϸ�
		if srcKitOrder <= csdefine.KB_COMMON_ID or srcKitOrder >= csdefine.KB_CASKET_ID:
			self.statusMessage( csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False
		# �ж�Ŀ�걳��λ���Ƿ�Ϸ�
		if dstKitOrder <= csdefine.KB_COMMON_ID or dstKitOrder >= csdefine.KB_CASKET_ID:
			self.statusMessage( csstatus.CIB_MSG_KITBAG_NOT_ALLOW )
			return False

		srckitItem = self.kitbags.get( srcKitOrder )
		if srckitItem is None:
			self.statusMessage( csstatus.CIB_MSG_INVALID_KITBAG, srcKitOrder )
			return False
		# �ж�Դ�������Ƿ��б�������Ʒ
		srcItemsList = self.getItems( srcKitOrder )
		for tempItem in srcItemsList:
			if tempItem.isFrozen():
				self.statusMessage( csstatus.CIB_MSG_FROZEN )
				return False

		dstkitItem = self.kitbags.get( dstKitOrder )
		swapItemData = {}	# ��¼��������
		orderAmend = csdefine.KB_MAX_SPACE *( dstKitOrder - srcKitOrder )
		if dstkitItem is not None:
			# �ж�Ŀ�걳�����Ƿ��б�������Ʒ
			dstItemsList = self.getItems( dstKitOrder )
			for tempItem in dstItemsList:
				if tempItem.isFrozen():
					self.statusMessage( csstatus.CIB_MSG_FROZEN )
					return False
			# Դ������Ŀ�걳�������ڣ���������
			for item in srcItemsList:
				swapItemData[item.order + orderAmend] = item
				self.__removeItem( item.order, item, csdefine.DELETE_ITEM_SWAP_KITBAG )
				
			for item in dstItemsList:
				swapItemData[item.order - orderAmend] = item
				self.__removeItem( item.order, item, csdefine.DELETE_ITEM_SWAP_KITBAG )
				
			self.kitbags.update( { srcKitOrder : dstkitItem, dstKitOrder : srckitItem } )
		else:
			# Դ�������ڣ�Ŀ�걳�������ڣ�������λ
			for item in srcItemsList:
				swapItemData[item.order + orderAmend] = item
				self.__removeItem( item.order, item, csdefine.DELETE_ITEM_SWAP_KITBAG )
				
			self.kitbags[dstKitOrder] = self.kitbags.pop( srcKitOrder )

		for order, itemData in swapItemData.iteritems():
			self.__addItem( order, itemData, csdefine.ADD_ITEM_SWAP_KITBAG )
				
		self.client.swapKitbagCB( srcKitOrder, dstKitOrder )

	# ------------------------------------------�������������� BEGIN----------------------------------------
	def _iskitbagsSetPassword( self ):
		"""
		��֤�Ƿ������˱�������
		"""
		return self.kitbagsPassword != ""	# ��ʾ����������״̬��λ�Ƿ�Ϊ1


	def iskitbagsLocked( self ):
		"""
		��֤�����Ƿ�����
		"""
		return ( self.kitbagsLockerStatus >> 1 ) & 0x01 == 1	# ��ʾ�����Ƿ��������״̬λ�Ƿ�Ϊ1


	def kitbags_setPassword( self, srcEntityID, srcPassword, password ):
		"""
		Exposed method.
		���á��޸ı������붼ʹ�ô˽ӿڡ���������Ϊ��ʱ��srcPasswordֵΪ"",�޸�����ʱsrcPasswordֵΪ ��ҵľ�����

		param srcPassword:	����ԭ����,
		type srcPassword:	STRING
		param password:	������������
		type password:	STRING
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		if not cmp( srcPassword, self.kitbagsPassword ) == 0:
			DEBUG_MSG( "�������ľ����벻��ȷ��" )
			if self.kitbagsUnlockLimitTime > 0 and int( time.time() ) - self.kitbagsUnlockLimitTime > 0:
				self.kitbagsUnlockLimitTime = 0			# ���˽����������ޣ�ȡ������
				self.kitbagsLockerStatus |= 0x10		# ���ұߵ�5λ����Ϊ1����ʾ��һ���������
				self.client.kitbags_lockerNotify( 3 )	# �����������Ҫ֪ͨ���
				return
			if self.kitbagsUnlockLimitTime == 0:		# ��Ҳ��ڽ�������������
				temp = self.kitbagsLockerStatus >> 4
				temp += 1
				if temp == 3:							# ��������������ﵽ3��
					self.kitbagsUnlockLimitTime = int( time.time() ) + csconst.KITBAG_CANT_UNLOCK_INTERVAL	# �������ƽ�������
					self.kitbagsLockerStatus &= 0x03	# ��������������0���Ա��´����¼������
					return
				temp <<= 4
				self.kitbagsLockerStatus &= 0x03		# �������ұ�2λ���䣬������λ����0
				self.kitbagsLockerStatus |= temp		# ������״̬�仯����¼����������Ĵ���
				self.client.kitbags_lockerNotify( 3 )	# �����������Ҫ֪ͨ���
				return
			self.client.kitbags_lockerNotify( 3 )		# �ڽ������������ھ����������Ҫ֪ͨ���
			return

		if self.kitbagsPassword == "":
			self.kitbagsLockerStatus |= 0x01
			self.client.kitbags_lockerNotify( 0 )		# ��������ɹ���֪ͨ�ͻ���
		else:
			self.client.kitbags_lockerNotify( 1 )		# �޸�����ɹ���֪ͨ

		self.kitbagsPassword = password


	def kitbags_lock( self, srcEntityID ):
		"""
		Exposed method.
		����������������������������һ�û�жԱ���������ǰ���£�������˽ӿڵ�ʹ������

		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		if not self._iskitbagsSetPassword():
			HACK_MSG( "����û�����롣" )
			return

		if self.iskitbagsLocked():
			HACK_MSG( "�����Ѿ���������״̬��" )
			return
		#���ڽ���״̬ʱ�����ᵼ�½���ȡ��
		if self.si_myState != csdefine.TRADE_SWAP_DEFAULT:
			self.__cancelTradeForLock()

		self.kitbagsLockerStatus |= 0x02		# ���ñ���״̬Ϊ����״̬
		self.client.kitbags_lockerNotify( 4 )

		if self._isVend():						# ������ڰ�̯����ôȡ����̯
			self.vend_endVend( self.id, True )

	def __cancelTradeForLock( self ):
		tradeTarget = BigWorld.entities.get( self.si_targetID )
		if tradeTarget :
			self.si_tradeCancelFC( self.id )
			self.si_resetData()
			tradeTarget.client.onStatusMessage( csstatus.CIB_MSG_CANCEL_TRADE_FOR_LOCK, "" )	#Ϊ��ֹ���׶�����ghostʱ�������tradeTarget.statusMessage�����ĳ������
			self.statusMessage( csstatus.CIB_MSG_CANCEL_TRADE )

	def kitbags_unlock( self, srcEntityID, srcPassword ):
		"""
		Exposed method.
		����������������������˱��������Ҹ�����������ǰ���£�������˽ӿڵ�ʹ��������
		ע�⣺�����Ĳ�������ڱ��ε�½�ڼ�����ʧ��3�Σ�KITBAG_CANT_UNLOCK_INTERVAL������������������

		param srcPassword:	����ԭ����,
		type srcsrcPassword:STRING
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		if not self._iskitbagsSetPassword():
			HACK_MSG( "����û�����롣" )
			return

		if not self.iskitbagsLocked():
			HACK_MSG( "�����Ѿ����ڷ�����״̬��" )
			return

		if self.kitbagsUnlockLimitTime > 0:
			if not int( time.time() ) > self.kitbagsUnlockLimitTime:	# ������Ҳ�ڿͻ�����������������������������ɽ���֪ͨ��ң�����������Ҫ֪ͨ
				self.client.kitbags_lockerNotify( 6 )
				DEBUG_MSG( "��Ҵ��ڲ���������ڼ䡣" )
				return
			self.kitbagsUnlockLimitTime = 0

		if not cmp( srcPassword, self.kitbagsPassword ) == 0:
			DEBUG_MSG( "�����������벻��ȷ��" )
			temp = self.kitbagsLockerStatus >> 4
			temp += 1
			if temp == 3:	# ��������������ﵽ3��
				self.kitbagsUnlockLimitTime = int( time.time() ) + csconst.KITBAG_CANT_UNLOCK_INTERVAL
				self.kitbagsLockerStatus &= 0x03			# ��������������0���Ա��´����¼������
				self.client.kitbags_lockerNotify( 2 )		# �����������֪ͨ
				return
			temp <<= 4
			self.kitbagsLockerStatus &= 0x03				# �������ұ�2λ���䣬������λ����0
			self.kitbagsLockerStatus |= temp				# ������״̬�仯����¼����������Ĵ���
			self.client.kitbags_lockerNotify( 2 )			# �����������֪ͨ
			return

		self.kitbagsLockerStatus &= 0x03					# �ɹ�������,��������������0(�������3��������룬������)
		self.kitbagsLockerStatus &= 0xfd					# ���ұߵ�2λ��0����ʾ�������ڷ�����״̬
		self.client.kitbags_lockerNotify( 5 )
		self.__cancelForceUnlock()							# �ɹ���������ǿ�ƽ���

	def kitbags_onForceUnlock( self, srcEntityID ) :
		"""
		Exposed method
		�������ǿ�ƽ�������������������
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		if self.kitbagsForceUnlockLimitTime > 0 :			# ��ǿ�ƽ�����������ڣ������ظ���Ӧ����
			self.statusMessage( csstatus.CIB_MSG_KITBAG_FORCE_UNLOCK_REPEAT )
			return
		if not self.kitbagsLockerStatus & 0x02 :			# ����δ���ϣ�����������ǿ�ƽ���
			self.statusMessage( csstatus.CIB_MSG_KITBAG_FORCE_UNLOCK_FORBID )
			return
		self.kitbagsForceUnlockLimitTime = int( time.time() ) + csconst.KITBAG_FORCE_UNLOCK_LIMIT_TIME
		self.__addForceUnlockTimer()

	def kitbags_clearPassword( self, srcEntityID, srcPassword ):
		"""
		���������ý���������Ѿ������������������ǰ���£��˽ӿ����������õ����룬�ѱ���������Ϊ�ա�
		ע�⣺���ý����Ĳ�������ڱ��ε�½�ڼ�ʧ��3�Σ�KITBAG_CANT_UNLOCK_INTERVAL�ڲ�����������������

		param srcPassword:	����ԭ����,
		type srcsrcPassword:STRING
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		if not self._iskitbagsSetPassword():
			HACK_MSG( "����û�����롣" )
			return

		if self.kitbagsUnlockLimitTime > 0:
			if int( time.time() ) <= self.kitbagsUnlockLimitTime:	# ������Ҳ�ڿͻ�����������������������������ɽ���֪ͨ��ң�����������Ҫ֪ͨ
				self.client.kitbags_lockerNotify( 6 )
				DEBUG_MSG( "��Ҵ��ڲ���������ڼ䡣" )
				return
			self.kitbagsUnlockLimitTime = 0

		if not cmp( srcPassword, self.kitbagsPassword ) == 0:
			DEBUG_MSG( "�������ľ����벻��ȷ��" )
			temp = self.kitbagsLockerStatus >> 4
			temp += 1
			if temp == 3:	# ��������������ﵽ3��
				self.kitbagsUnlockLimitTime = int( time.time() ) + csconst.KITBAG_CANT_UNLOCK_INTERVAL
				self.kitbagsLockerStatus &= 0x03			# ��������������0���Ա��´����¼������
				self.client.kitbags_lockerNotify( 2 )		# �����������֪ͨ
				return
			temp <<= 4
			self.kitbagsLockerStatus &= 0x03				# �������ұ�2λ���䣬������λ����0
			self.kitbagsLockerStatus |= temp				# ������״̬�仯����¼����������Ĵ���
			self.client.kitbags_lockerNotify( 2 )			# �����������֪ͨ
			return

		self.kitbagsPassword = ""
		self.kitbagsLockerStatus &= 0x00
		self.kitbagsUnlockLimitTime = 0						# ����û���ˣ����е�������������ݶ���0
		self.client.kitbags_lockerNotify( 7 )
		self.__cancelForceUnlock()							# �ɹ���������ǿ�ƽ���
	# ------------------------------------------�������������� END----------------------------------------


	def combineAppItem( self, itemID ):
		"""
		�ϲ�ָ������Ʒ
		@param    srcOrder: Դ������Դ����
		@type     srcOrder: UINT8
		@param    dstOrder: Ŀ�걳����Դ����
		@type     dstOrder: UINT8
		"""
		if self.iskitbagsLocked(): return

		self.combineItems( self.findItemsByIDWithBindFromNKCK( itemID, True ) )
		self.combineItems( self.findItemsByIDWithBindFromNKCK( itemID, False ) )

	def combineItems( self, items ):
		"""
		�ϲ�һ����Ʒ
		"""
		# С��2����Ʒ��û��Ҫ�ϲ���
		if len( items ) < 2: return False
		uItem = items[0]
		# �жϸ���Ʒ�Ƿ��ܺϲ�
		stackable = uItem.getStackable()
		if stackable <= 1: return False
		# �ж��Ƿ���ס��
		for item in items:
			if item.isFrozen(): return False

		allAmount = sum( [item.amount for item in items] )
		group = allAmount / stackable
		keepAmount = allAmount % stackable

		i = 0
		for item in items:
			if i < group:
				item.setAmount( stackable, self, csdefine.ADD_ITEM_COMBINEITEM )
			elif i == group:
				item.setAmount( keepAmount, self, csdefine.DELETE_ITEM_COMBINEITEM )
			else:
				item.setAmount( 0, self, csdefine.DELETE_ITEM_COMBINEITEM )
			i += 1

		return True

	def autoInStuffs( self, srcEntityID, itemIDs, needAmounts ):
		"""
		Exposed Method
		װ�������У��Զ��ϲ����������Ĳ���
		��ָ������ƷID���ϲ������� needAmount ��������
		һ���ܹ���ķ���.
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		if self.iskitbagsLocked(): return False

		# Ҫ���в�ֺϲ���������Ʒ�У�ֻҪ��һ����Ʒ��������״̬����������
		for itemID in itemIDs:
			items = self.findItemsByIDFromNKCK( itemID )
			for item in items:
				if item.isFrozen():
					self.statusMessage( csstatus.AUTO_STUFF_ITEM_FROZEN )
					return False

		# ������λ���
		needCount = len( itemIDs )
		freeOrderCount = self.getNormalKitbagFreeOrderCount()
		if freeOrderCount < needCount:
			self.statusMessage( csstatus.AUTO_STUFF_NO_FREEORDER, needCount )
			return

		needOrder = []

		for itemID, amount in zip( itemIDs, needAmounts ):
			self.combineAppItem( itemID )
			items = self.findItemsByIDFromNKCK( itemID )
			if len( items ) == 0: return False
			orders = [ item.order for item in items if item.amount == amount ]
			if len( orders )  > 0:
				needOrder.append( orders[0] )
			else:
				newAmount = amount
				for item in items:
					itemAmount = item.amount
					if itemAmount > newAmount:
						newItem = item.new()
						newItem.setAmount( newAmount )
						freeOrder = self.getNormalKitbagFreeOrder()
						if self.__addItem( freeOrder, newItem, csdefine.ADD_ITEM_AUTOINSTUFFS ):
							self.questItemAmountChanged( newItem, newAmount )
							self.client.addItemCB( newItem )
							item.setAmount( itemAmount - newAmount, self, csdefine.DELETE_ITEM_AUTOINSTUFFS )
							needOrder.append( freeOrder )
						break
					else:
						needOrder.append( item.order )
						newAmount -= itemAmount

		self.client.autoStuffFC( needOrder )

	def getByUid( self, uid ):
		"""
		����UID ��ȡ�����е���Ʒ
		@type  uid : UINT32
		@param uid : ��Ʒ��UID
		@return ��Ʒ��ʵ����û�з���None
		"""
		return self.itemsBag.getByUid( uid )


	def onMoneyChanged( self, value, reason ):
		"""
		��Ҹ�Ǯ
		"""
		RoleSwapItem.onMoneyChanged( self, value, reason )

	# -------------------------------------------------
	# ����ǿ�ƽ������
	# -------------------------------------------------
	def onKitbagForceUnlockTimer( self ) :
		"""
		ǿ�ƽ������������timer����
		"""
		self.__forceUnlockKitbag()

	def __forceUnlockKitbag( self ) :
		"""
		ǿ�ƽ�������
		"""
		self.kitbagsPassword = ""								# �������
		self.kitbagsLockerStatus &= 0x00						# ��������
		self.kitbagsUnlockLimitTime = 0							# ����ʱ������
		self.kitbagsForceUnlockLimitTime = 0					# ǿ�ƽ���ʱ������
		self.removeTemp( "kb_forceUnlock_timerID" )
		self.statusMessage( csstatus.CIB_MSG_KITBAG_FORCE_UNLOCK_SUCCESS )
		mailMgr = BigWorld.globalData["MailMgr"]
		content = cschannel_msgs.FORCE_UNLOCK_MAIL_CONTENT % cschannel_msgs.GMMGR_BEI_BAO
		title = cschannel_msgs.FORCE_UNLOCK_MAIL_TITLE % cschannel_msgs.GMMGR_BEI_BAO
		mailMgr.send( None,
					self.getName(),
					csdefine.MAIL_TYPE_QUICK,
					csdefine.MAIL_SENDER_TYPE_NPC,
					cschannel_msgs.SHARE_SYSTEM,
					title, content, 0, []
					)

	def __cancelForceUnlock( self ) :
		"""
		����ǿ�ƽ���
		"""
		kb_forceUnlock_timerID = self.queryTemp( "kb_forceUnlock_timerID", 0 )
		if kb_forceUnlock_timerID > 0 :
			self.cancel( kb_forceUnlock_timerID )
			self.removeTemp( "kb_forceUnlock_timerID" )
		self.kitbagsForceUnlockLimitTime = 0

	def __addForceUnlockTimer( self ) :
		"""
		���ǿ�ƽ�����timer
		"""
		now = int( time.time() )
		leaveTime = self.kitbagsForceUnlockLimitTime - now
		if leaveTime <= 0 : return								# ʱ���ѳ���
		kb_forceUnlock_timerID = self.queryTemp( "kb_forceUnlock_timerID", 0 )
		if kb_forceUnlock_timerID > 0 : return					# �������һ��timer���������ظ����
		kb_forceUnlock_timerID = self.delayCall( leaveTime, "onKitbagForceUnlockTimer" )
		self.setTemp( "kb_forceUnlock_timerID", kb_forceUnlock_timerID )
		leaveHours = leaveTime / 3600
		leaveMinutes = leaveTime % 3600 / 60
		leaveSeconds = leaveTime % 60
		leaveText = ""
		if leaveHours :
			leaveText += "%d%s" % ( leaveHours, ST.CHTIME_HOUR )
		if leaveMinutes :
			leaveText += "%d%s" % ( leaveMinutes, ST.CHTIME_MINUTE )
		if leaveSeconds :
			leaveText += "%d%s" % ( leaveSeconds, ST.CHTIME_SECOND )
		self.delayCall( 1, "statusMessage", csstatus.CIB_MSG_KITBAG_FORCE_UNLOCK_REMAIN, leaveText )
	
	def kitbags_saveLater( self ):
		"""
		�����ӳٴ洢
		"""
		if self.kitbags_saveTimerID:
			return
			
		self.kitbags_saveTimerID = self.addTimer( 60.0, 0, ECBExtend.ROLE_ITEM_BAG_SAVE_LATER )
	
	def kitbags_onSaveLaterTimer( self, timerID, cbid ):
		"""
		ִ���ӳٴ洢����
		"""
		self.kitbags_saveTimerID = 0
		self.writeToDB()

	
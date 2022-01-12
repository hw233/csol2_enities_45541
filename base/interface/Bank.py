# -*- coding: gb18030 -*-
#
# $Id: Bank.py,v 1.21 2008-08-08 03:08:13 fangpengjun Exp $


import cschannel_msgs
import ShareTexts as ST
import items
import ItemTypeEnum
import csdefine
import csstatus
import csconst
import sys
from bwdebug import *
from MsgLogger import g_logger
from ChatProfanity import chatProfanity

g_item = items.instance()


class Bank:
	"""
	Ǯׯϵͳ�ӿ�
	"""
	def __init__( self ):
		"""
		"""
		# self.bankBags ������def�ļ���
		self._lastTote = 0
		self._isOperateBank = False # �򿪲ֿ��Ƿ�����˲���
		if not self.bankNameList:	# ��δ�����Ϊ�˼���Ǯׯδ�İ�ǰ�Ĵ��������wsf,13:40 2008-8-7
			self.bankNameList.append( "" )

	def bank_requestBankBag( self, itemIndex,):
		"""
		Exposed method
		"""
		if itemIndex >= len( self.bankNameList ):	# ������û�д˴�����
			return
		bankItemList = self._getBankItems( itemIndex )
		self.client.bank_receiveBaseData(  itemIndex, bankItemList )

	def bank_activateBag( self, amount ):
		"""
		Define method.
		�������
		"""
		#item = g_item.createDynamicItem( "070101005" )
		bagIndex = len( self.bankNameList )
		if bagIndex >= csconst.BANK_MAX_COUNT:
			self.client.onStatusMessage( csstatus.BANK_CANNOT_OPEN_MORE_BAG, "" )
#			ERROR_MSG( "���( %s )������ӵ�и���Ĵ������ˡ�" %( self.getName() ) )
			return
		#self.bankBags[ count ] = item
		elif amount < csconst.NEED_ITEM_COUNT_DICT[bagIndex]:
			self.client.noticeFailure()
			return
		self.bankNameList.append( "" )
		self.cell.onBank_activateBagSuccess( csconst.NEED_ITEM_COUNT_DICT[bagIndex] )
		self.client.bank_activateBagSuccess()
		# �ֿ�������־
		try:
			g_logger.bankExtendLog( self.databaseID, self.getName(), bagIndex, bagIndex*csconst.BANKBAG_NORMAL_ORDER_COUNT )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	#------------------------------------Ǯׯ�����Ĳ��� BEGIN-----------------------------
	def _addItem2Order( self, srcOrder, dstOrder, srcItem ):
		"""
		description:��һ����Ʒ�ŵ�ָ�������ĸ����У���bank_storeItem2Order���ã�
					������ο�bank_storeItem2Order,�����������֣�
					1.Ŀ��λ������Ʒ�ҿ��Ժ�Դ��Ʒ���ӣ����Ӳ���
					2.Ŀ��λ������Ʒ�Ҳ����Ժ�Դ��Ʒ���ӣ���������
					3.Ŀ��λ��û����Ʒ����Ӳ���
		param kitbag:	����ʵ��
		type kitbag:	KITBAG
		param order:	���Ӻ�
		type order:		INT16
		"""
		if srcItem is None :
			return False
		dstItem = self.bankItemsBag.getByOrder( dstOrder )
		if dstItem is None:			# ���3
			addResult = self._addItemByOrder( srcItem, dstOrder )
			if addResult == csdefine.KITBAG_ADD_ITEM_SUCCESS:
				self.cell.bank_storeItemSuccess01( srcOrder )
				return True
			return False

		if dstItem.isFrozen():
			WARNING_MSG( "������������" )
			return False

		if dstItem.id == srcItem.id and dstItem.isBinded() != srcItem.isBinded() and dstItem.getAmount() < dstItem.getStackable():
			self.statusMessage( csstatus.CIB_MSG_CANNOT_STACKABLE )
			return False

		if dstItem.id == srcItem.id and dstItem.getAmount() < dstItem.getStackable():	# ���1
			stackable = srcItem.getStackable()
			srcAmount = srcItem.getAmount()
			dstAmount = dstItem.getAmount()
			stackAmount = min( stackable - dstAmount, srcAmount )
			dstItem.setAmount( dstAmount + stackAmount )
			self.client.bank_storeItemUpdate( dstItem )
			srcAmount = srcAmount - stackAmount
			if srcAmount:	# ��Ŀ��λ�õ��Ӻ���ʣ�࣬�Żر���
				srcItem.setAmount( srcAmount )
				self.client.bank_storeItemUpdate( srcItem )
				self.cell.bank_storeItemSuccess02( srcOrder, srcItem )
			else:
				self.cell.bank_storeItemSuccess01( srcOrder )
			return True

		swapSucc = self._swapItem( dstOrder, srcItem )	# ���2
		if swapSucc:
			self._isOperateBank = True
			self.cell.bank_storeItemSuccess02( srcOrder, dstItem )
			return True
		return False

	def _swapItem( self, dstOrder, srcItem ):
		"""
		description:��cell��������Ʒ�����а�������Ʒ����
		@param itemInstance: �̳���CItemBase���Զ������ʵ��
		@type  itemInstance: CItemBase
		@return:             �ɹ��򷵻سɹ�״̬�룬����ɹ�������Զ�֪ͨclient��ʧ���򷵻�ԭ��
		@rtype:              INT8
		"""
		if self.bankItemsBag.removeByOrder( dstOrder ):
			addResult = self._addItemByOrder( srcItem, dstOrder )
			if addResult == csdefine.KITBAG_ADD_ITEM_SUCCESS:
				return True
		return False

	def _addItemByOrder( self, itemInstance, orderID ):
		"""
		description:��ָ��λ�ü���ĳ������ʵ��
		@param itemInstance: �̳���CItemBase���Զ������ʵ��
		@type  itemInstance: CItemBase
		@param orderID: �����ڱ������λ��
		@type  orderID: INT16
		@return: ���ز�����״̬��
		@rtype:  INT8
		"""
		# �˺�����������Ʒʵ���ӽ����а���
		addResult = self.bankItemsBag.add( orderID, itemInstance )
		if not addResult:				# ���صײ��״̬����ʱ���ڵײ�ֻ����0��1�����Բ���ô��
			return csdefine.KITBAG_ADD_ITEM_FAILURE
		self.client.bank_storeItemUpdate( itemInstance )
		try:
			g_logger.bankStoreLog( self.databaesID, self.getName(), itemInstance.uid, itemInstance.name(), itemInstance.getAmount() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		
		self._isOperateBank = True
		return csdefine.KITBAG_ADD_ITEM_SUCCESS

	#------------------------------------Ǯׯ�����Ĳ��� END-----------------------------

	#------------------------------------��Ǯׯ�����Ʒ BEGIN-----------------------------
	def bank_storeItem2Order( self, srcOrder, srcItem, dstOrder ):
		"""
		Define method.
		description:��Ǯׯ������ָ���ĸ��Ӵ洢��Ʒ�Ľӿ�
		param srcOrder:	���Ӻ�
		type srcOrder:	INT16
		param item:		��Ǯׯ��洢����Ʒ
		type item:		ITEM
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		"""
		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		bankBagNum = dstOrder / csdefine.KB_MAX_SPACE
		if bankBagNum >= len( self.bankNameList ):
			HACK_MSG( "���(%s)Ǯׯ����λ����(%i)��" % ( self.getName(), bankBagNum ) )
			self.cell.bank_storeItemFailed( srcOrder )
			return

		if not self._addItem2Order( srcOrder, dstOrder, srcItem ):	# ���ʧ��
			self.cell.bank_storeItemFailed( srcOrder )
			return

	def bank_storeItem2Bank( self, srcOrder, item ):
		"""
		Define method.
		��Ǯׯ��洢��Ʒ�Ľӿڣ���ָ������λ��Ŀ����ӣ���Ǯׯ����ҵ�һ����λ
		@param dstOrder:	���Ӻ�
		@type dstOrder:	INT16
		@param item:		��Ǯׯ��洢����Ʒ
		@type item:		ITEM
		@param bankBagNum:Ǯׯ����λ��
		@type bankBagNum:UINT8
		"""
		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		if item.getStackable() > 1:					# ����ǿɵ�����Ʒ
			if self._stackableInBank( item ):		# ����Ǯׯ���ͬ��ɵ�����Ʒ ����
				self.cell.bank_storeItemSuccess01( srcOrder )
				return
		# ����Ǯׯ��Ŀ�λ
		orderID = self._findFreeOrder()
		if orderID != -1:
			result = self._addItemByOrder( item, orderID )
			if result == csdefine.KITBAG_ADD_ITEM_SUCCESS:
				self.cell.bank_storeItemSuccess01( srcOrder )
			else:
				ERROR_MSG("���򱳰�������һ������ʱʧ��")
				self.cell.bank_storeItemFailed( srcOrder )
		else:	# ��Ʒ�洢ʧ��
			self.statusMessage( csstatus.BANK_IS_FULL )
			self.cell.bank_storeItemFailed( srcOrder )
			return

	def bank_storeItem2Bag( self, srcOrder, item, bankBagNum ):
		"""
		Define method.
		��Ǯׯ��洢��Ʒ�Ľӿڣ���ָ���˰���λ
		���ڽ����Ѿ��ı䣬�˹����Ѿ�����Ҫ����ʱ����
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param item:		��Ǯׯ��洢����Ʒ
		type item:		ITEM
		param bankBagNum:Ǯׯ����λ��
		type bankBagNum:UINT8
		"""
		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		if bankBagNum >= len( self.bankNameList ):
			HACK_MSG( "���(%s)Ǯׯ����λ����(%i)��" % ( self.getName(), bankBagNum ) )
			self.cell.bank_storeItemFailed( srcOrder )
			return
		if item.getStackable() > 1:							# ����ǿɵ�����Ʒ
			if self._stackableInBag( item, bankBagNum ):	# ���ӳɹ�
				self.cell.bank_storeItemSuccess01( srcOrder )
				return
		order = self.__getFreeOrder( bankBagNum )
		if order == -1:
			self.cell.bank_storeItemFailed( srcOrder )
			self.statusMessage( csstatus.BANK_CURRENT_BAG_FULL )
			return
		if self._addItemByOrder( item, order ) == csdefine.KITBAG_ADD_ITEM_SUCCESS:
			self.cell.bank_storeItemSuccess01( srcOrder )
			#self.cell.bank_storeItemFailed( srcOrder )
			return

	def _stackableInBag( self, itemInstance, bankBagID ):
		"""
		�ڰ����ж�һ���ɵ�����Ʒ���Ӳ���
		"""
		currtotal = 0
		stackable = itemInstance.getStackable()
		r = []
		for item in self._getBankItems( bankBagID ):
			if item.id == itemInstance.id and item.isBinded() == itemInstance.isBinded():	# ����ʱ�������ǰ�����һ������Ʒ���ܵ��ӡ�18:01 2009-2-16��wsf
				r.append( item )
		if len( r ) == 0: return False
		#�������
		for item in r:
			# like as: c += a < b ? a : b�����������ԭ���Ǳ������ʱ�ֶ����ö���stackable��������Ʒ�����жϴ���
			currtotal += item.getAmount() < stackable and item.getAmount() or stackable
		val = len( r ) * stackable - currtotal		# ��ȡ�����Ե��ӵ�����
		val1 = itemInstance.getAmount()				# ��ȡ�����Ʒ������
		if val < val1 : return False
		for item in r :
			if val1 <= 0 : break
			amount = stackable - item.getAmount()
			if amount > 0:
				if amount > val1:
					item.setAmount( item.getAmount() + val1 )
					self.client.bank_storeItemUpdate( item )
					return True
				else:
					item.setAmount( stackable )
					self.client.bank_storeItemUpdate( item )
					val1 -= amount
		return True


	#------------------------------------��Ǯׯ�����Ʒ END--------------------------------


	#------------------------------------��Ʒ��Ǯׯȡ�� BEGIN------------------------------
	def bank_fetchItemFailed( self, itemOrder ):
		"""
		Define method.
		�洢��Ʒ��Ǯׯʧ��

		@param itemOrder : û�洢�ɹ�����Ʒorder
		@type itemOrder : INT16
		"""
		item = self.bankItemsBag.getByOrder( itemOrder )
		if item is None:
			ERROR_MSG( "player( %s ) can not find item( order : %i )." % ( self.getName(), itemOrder) )
		else:
			item.unfreeze()

	def bank_fetchItem2Order( self, srcOrder, dstOrder ):
		"""
		�����Ǯׯ��Ʒ����Ʒ��ȷ���ı�����Ʒ��

		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param kitbagNum:��������λ��
		type kitbagNum:	UINT8
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		"""
		bankBagNum = srcOrder / csdefine.KB_MAX_SPACE
		if bankBagNum >= len( self.bankNameList ):
			return

		item = self.bankItemsBag.getByOrder( srcOrder )
		if item is None:
			DEBUG_MSG( "��ң�%s��Ǯׯλ�ã�bankBagNum(%i),order(%i)����������Ʒ��" % ( self.getName(), bankBagNum, srcOrder ) )
			return
		if item.isFrozen():
			DEBUG_MSG( "��ң�%s��Ǯׯλ�ã�bankBagNum(%i),order(%i)����������Ʒ��" % ( self.getName(), bankBagNum, srcOrder ) )
			return
		item.freeze()
		self.cell.bank_fetchItem2OrderCB( dstOrder, item.copy(), srcOrder )

	def bank_fetchItem2Kitbags( self, srcOrder ):
		"""
		��Ǯׯ��ȡ����Ʒ�Ľӿڣ���ָ������λ��Ŀ����ӣ��ڱ�������ҵ�һ����λ
		param kitbagNum:Ǯׯ����λ��
		type kitbagNum:UINT8
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		bankBagNum = srcOrder / csdefine.KB_MAX_SPACE
		item = self.bankItemsBag.getByOrder( srcOrder )
		if item is None:
			HACK_MSG( "��Ʒ�����ڡ�" )
			return
		if item.isFrozen():
			WARNING_MSG( "��Ʒ������" )
			return
		item.freeze()
		self.cell.bank_fetchItem2KitbagsCB( srcOrder, item.copy() )

	def bank_fetchItemSuccess01( self, dstOrder ):
		"""
		Define method.
		�洢һ����Ʒ�ɹ��� base������ɾ����Ʒ
		"""
		bankBagNum = dstOrder / csdefine.KB_MAX_SPACE
		dstItem = self.bankItemsBag.getByOrder( dstOrder )
		if dstItem is None:
			return
		self.bankItemsBag.removeByOrder( dstOrder )
		self.client.bank_delItemUpdate( bankBagNum, dstOrder )
		self.statusMessage( csstatus.CIB_MSG_FETCH_ITEMS_FROM_BANK, dstItem.name(),dstItem.amount )
		try:
			g_logger.bankTakeLog( self.databaseID, self.getName(), dstItem.uid, dstItem.name(), dstItem.getAmount() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def bank_fetchItemSuccess02( self, dstOrder, item ):
		"""
		Define method.
		������Ǯׯȡһ����Ʒ�Ļص���
		�����е���һ����Ʒ��ʣ�࣬��Ǯׯ�뱳��Ŀ����ӽ�����Ʒ���� ʣ����Ʒ �� ��������Ʒ �Ż�Ǯׯ
		"""
		bankBagNum = dstOrder / csdefine.KB_MAX_SPACE
		dstItem = self.bankItemsBag.getByOrder( dstOrder )
		if self.bankItemsBag.removeByOrder( dstOrder ):
			self._addItemByOrder( item, dstOrder )
			if dstItem.id == item.id:
				self.statusMessage( csstatus.CIB_MSG_FETCH_ITEMS_FROM_BANK, dstItem.name(),dstItem.amount-item.amount )
			else:
				self.statusMessage( csstatus.CIB_MSG_FETCH_ITEMS_FROM_BANK, dstItem.name(),dstItem.amount )
				self.statusMessage( csstatus.CIB_MSG_STORE_ITEMS_TO_BANK, item.name(),item.amount )
		try:
			g_logger.bankTakeLog( self.databaseID, self.getName(), dstItem.uid, dstItem.name(), dstItem.getAmount() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	#------------------------------------��Ʒ��Ǯׯȡ�� END------------------------------

	def bank_destroyItem( self, order ):
		"""
		Define method.
		������Ʒ�Ľӿ�
		param kitbagNum:Ǯׯ����λ��
		type kitbagNum:UINT8
		param order:	���Ӻ�
		type order:	INT16
		"""
		bankBagNum = order / csdefine.KB_MAX_SPACE

		#--����ǰ��һЩ�ж�--
		if bankBagNum >= len( self.bankNameList ):
			HACK_MSG( "���(%s)Ǯׯ����λ����(%i)��" % ( self.getName(), bankBagNum ) )
			#self.cell.bank_unfreezeBag( kitbagNum )
			return
		item = self.bankItemsBag.getByOrder( order )
		if item is None:
			WARNING_MSG( "��Ʒ�����ڡ�" )
			return
		if item.isFrozen():
			WARNING_MSG( "��Ʒ��������" )
			return
		if not item.canDestroy():
			WARNING_MSG( "��Ʒ�������١�" )
			return
		#--------------------
		self._isOperateBank = True
		if self.bankItemsBag.removeByOrder( order ):
			self.client.bank_delItemUpdate( bankBagNum, order )
			try:
				g_logger.bankDestroyLog( self.databaseID, self.getName(), item.uid,item.name(),item.getAmount() )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

	def bank_moveItem( self, srcOrder, dstOrder ):
		"""
		Define method.
		��ͬһ���������ƶ���Ʒ�Ľӿ�
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param srcOrder:	���Ӻ�
		type srcOrder:	INT16
		"""
		if srcOrder == dstOrder:
 			return
		srcBankBagNum = srcOrder / csdefine.KB_MAX_SPACE
		dstBankBagNum = dstOrder / csdefine.KB_MAX_SPACE
		if srcBankBagNum != dstBankBagNum:
			return
		if srcBankBagNum >= len( self.bankNameList ):
			HACK_MSG( "���(%s)Ǯׯ����λ����(%i)��" % ( self.getName(), srcBankBagNum ) )
			return
		srcItem = self.bankItemsBag.getByOrder( srcOrder )
		if srcItem is None:
			WARNING_MSG( "error code: ", csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return
		if srcItem.isFrozen():
			return

		dstItem = self.bankItemsBag.getByOrder( dstOrder )
		if dstItem and dstItem.isFrozen():
			return

		stack = srcItem.getStackable()
		srcAmount = srcItem.getAmount()
		if dstItem is None or dstItem.id != srcItem.id or dstItem.isBinded() != srcItem.isBinded() \
		or ( dstItem.getAmount() == stack or srcAmount == stack ) and srcAmount != dstItem.getAmount() :
			if self.bankItemsBag.swapOrder( srcOrder, dstOrder ) :
				self.client.moveItemCB( srcBankBagNum, srcOrder, srcBankBagNum, dstOrder )
				return
			else :
				ERROR_MSG(  "Swap false : src: %d <==> dst: %d " % ( srcOrder, dstOrder ) )
		dstAmount = dstItem.getAmount()
		if dstAmount < stack:	# �ɵ��ӵ��ߴ���
			storeAmount = min( stack - dstAmount, srcAmount )
			dstItem.setAmount( dstAmount + storeAmount )				# �Զ�֪ͨ�ͻ���
			srcAmount = srcAmount - storeAmount
			if srcAmount:	# ��Ŀ��λ�õ��Ӻ���ʣ�࣬�Ż�Դλ��
				srcItem.setAmount( srcAmount )
				self.client.bank_storeItemUpdate( srcItem )
			elif self.bankItemsBag.removeByOrder( srcOrder ):	# ��ʣ�࣬ɾ��Դ��Ʒ
				self.client.bank_delItemUpdate( srcBankBagNum, srcOrder )
			self.client.bank_storeItemUpdate( dstItem )

	def bank_unfreezeBag( self, bankBagNum ):

		"""
		Define method.
		Cell�ϼ�����������㣬�򲻽���ж�°��� �� ȡ����Ʒ�Ĳ�������ͨ���˽ӿڽ��base�ϱ�����İ���
		"""
		pass
		#self.bankBags[bankBagNum].unfreeze()

	#-------------------------------------------------------------------------------------------
	def _findAllItemFromBank( self, itemKeyName ):
		"""
		��������ͨ�������ҵ�������itemKeyName��ͬ����Ʒ

		@param itemKeyName: ��ʾÿһ����ߵ�Ψһ�ĵ�������
		@type  itemKeyName: STRING
		@return:	array of tuple as (kitOrder, orderID, itemData)
		@rtype:		array of tuple
		"""
		ar = []
		for i in xrange( csdefine.BANK_COMMON_ID, csdefine.BANK_COMMON_ID + csconst.BANK_MAX_COUNT ):
			if i < len( self.bankNameList ):
				for item in self._getBankItems( i ):
					if item.id == itemKeyName:
						ar.append( item )
		return ar

	def _getBankItems( self, bankBagID ):
		"""
		ȡ��ָ���ֿⱳ������Ʒ
		@return: [itemInstance, ...]
		"""
		start = bankBagID * csdefine.KB_MAX_SPACE
		end = bankBagID * csdefine.KB_MAX_SPACE + csdefine.KB_MAX_SPACE - 1
		return self.bankItemsBag.getDatasByRange( start, end )

	def _stackableInBank( self, itemInstance ):
		"""
		description:��Ǯׯ�ж�һ���ɵ�����Ʒ���Ӳ���
		@param itemInstance:�̳���CItemBase���Զ������ʵ��
		@type  itemInstance:CItemBase
		@return:	�ɹ��򷵻�Trueʧ���򷵻�False
		@rtype:		BOOL
		"""
		itemList = []
		currtotal = 0
		stackable = itemInstance.getStackable()
		#�������
		for e in self._findAllItemFromBank( itemInstance.id ):		# e like as ( kitOrder, orderID, itemData )
			# like as: c += a < b ? a : b�����������ԭ���Ǳ������ʱ�ֶ����ö���stackable��������Ʒ�����жϴ���
			if e.isBinded() != itemInstance.isBinded():
				continue
			itemList.append( e )
			currtotal += e.getAmount() < stackable and e.getAmount() or stackable
		if itemList == []:return False
		val = len( itemList ) * stackable - currtotal	# ��ȡ�����Ե��ӵ�����
		val1 = itemInstance.getAmount()					# ��ȡ�����Ʒ������
		if val < val1:	return False
		for e in itemList:
			if val1 <= 0:break
			amount = stackable - e.getAmount()
			if amount > 0:
				if amount > val1:
					e.setAmount( e.getAmount() + val1 )
					self.client.bank_storeItemUpdate( e )
					return True
				else:
					e.setAmount( stackable )
					self.client.bank_storeItemUpdate( e )
					val1 -= amount
		return True

	def _findFreeOrder( self ):
		"""
		����Ǯׯ�е�һ����λ��

		@return: tuple as (kitOrder, orderID), return None while no free order
		@rtype:  tuple/None
		"""
		for i in xrange( csdefine.BANK_COMMON_ID, csdefine.BANK_COMMON_ID + csdefine.BANK_COUNT ):
			if i >= len( self.bankNameList ):
				 break
			# ������ʱ��ΪֻҪ���ܷŵ����������Ʒ���ܷŵ�Ǯׯ�У���Ʒ�Ƿ��ܱ��洢Ӧ������Ʒ��������Զ���Ӧ���ǰ����ṩ�ӿ��жϡ�wsf
			order = self.__getFreeOrder( i )
			if order != -1:
				return order
		return -1

	def __getFreeOrder( self, bankBagID ):
		"""
		ȡ��ָ���ֿⱳ���Ŀ���λ��
		return: order
		"""
		# ȡ��ָ�������Ŀ���λ��
		if bankBagID >= len( self.bankNameList ):
			return -1
		startOrder = bankBagID * csdefine.KB_MAX_SPACE
		endOrder  = startOrder + csconst.BANKBAG_NORMAL_ORDER_COUNT
		for order in xrange( startOrder, endOrder ):
			if not self.bankItemsBag.orderHasItem( order ):
				return order
		return -1

	def bank_changeName( self, index, name ):
		"""
		Exposed method.

		@param index : Ǯׯ������,UINT8
		@param name : ���֣�STRING
		"""
		if index >= len( self.bankNameList ):
			HACK_MSG( "���(%s)Ǯׯ����λ����(%i)��" % ( self.getName(), index ) )
			return

		illegalWord = chatProfanity.searchNameProfanity( name )					# ��֤�����Ƿ�Ϸ�
		if illegalWord is not None :
			self.statusMessage( csstatus.PET_RENAME_FAIL_ILLEGAL_WORD, illegalWord )
		elif len( name.decode( "gb2312" ) ) > csconst.PET_NAME_MAX_LENGTH :		# �����Ƿ񳬳��޶�����
			self.statusMessage( csstatus.PET_RENAME_FAIL_OVERLONG )
		self.bankNameList[ index ] = name
		self.client.bank_bagNameUpdate( index, name )

	def bank_changeGoldToItem( self, goldValue ):
		"""
		Exposed method.
		��Ʊ�滻Ϊ��Ԫ��Ʊ��Ʒ
		"""
		if self.getUsableGold() < goldValue:
			self.statusMessage( csstatus.BANK_CHARGE_GOLD_LACK )
			return

		if goldValue < 0 and goldValue > 20000:
			self.statusMessage( csstatus.BANK_CHARGE_OVERTOP )
			return
		self.freezeGold( goldValue )
		self.cell.bank_changeGoldToItem( goldValue )

	def bank_changeGoldToItemCB( self, value, state ):
		"""
		Define method.
		Ԫ��Ʊ�һ�����ص�
		"""
		self._isOperateBank = True
		self.thawGold( value )
		if state:
			self.payGold( value, csdefine.CHANGE_GOLD_BANK_CHANGEGOLDTOITEM )

	def bank_item2Gold( self, value ):
		"""
		Define method.
		Ԫ��Ʊ�һ��ɽ�Ԫ��
		"""
		self._isOperateBank = True
		self.gainGold( value, csdefine.CHANGE_GOLD_BANK_ITEM2GOLD )

	
	def leaveBank( self ):
		"""
		exposed method
		�˳��ֿ�
		"""
		if self._isOperateBank:
			self.writeToDB()
		
		self._isOperateBank = False
#
# Revision 1.15  2008/07/02 05:38:59  songpeifang
# �����˰�����װ���󶨹��ܣ�������1��Ǯׯ��Ʒ��->Ǯׯ��λ����2��Ǯׯ��Ʒ��->������λ����3��������Ʒ��->Ǯׯ��������
#
# Revision 1.14  2008/05/30 03:03:49  yangkai
# װ������������Ĳ����޸�
#
# Revision 1.13  2008/05/13 06:12:37  wangshufeng
# method modify:bank_splitItem,ȥ��Ŀ�������Ŀ����Ӳ��������ұ�����һ����λ���ò�ֺ����Ʒ��
#
# Revision 1.12  2008/05/07 02:59:21  yangkai
# query( "stackable" ) -> getStackable()
#
# Revision 1.11  2008/04/28 06:07:12  wangshufeng
# method modify:bank_fetchItem2Order,����Ǯׯλ�õ���ƷΪNone��bug
#
# Revision 1.10  2008/04/21 06:33:18  wangshufeng
# �����ͻ��˴��ݵ���Ʒ�������첻��ȷ��bug
#
# Revision 1.9  2008/04/03 06:33:07  phw
# KitbagBase::find2All()����Ϊfind()�������ķ���ֵ��ԭ����( order, toteID, itemInstance )��ΪitemInstance
# KitbagBase::findAll2All()����ΪfindAll()�������ķ���ֵ��ԭ����( order, toteID, itemInstance )��ΪitemInstance
# �������ϵı仯���������ʹ�õ����ϽӿڵĴ���
#
# Revision 1.8  2008/02/04 00:56:52  zhangyuxing
# �޸Ĳֿ���Ʒ��÷�ʽ
#
# Revision 1.7  2007/12/22 09:51:55  fangpengjun
# if srcBag.swapOrder( srcOrder, dstOrder )
#   --------->
#          if bankBag.swapOrder( srcOrder, dstOrder ):
#
# Revision 1.6  2007/12/22 02:06:34  wangshufeng
# ����2����Ʒλ��ʹ��moveItemCB����֪ͨ�ͻ���
#
# Revision 1.5  2007/12/11 06:41:43  wangshufeng
# �����ˣ����ԭ����λ���ڰ����Ұ���������Ʒ��������λ���ø������ʱ�Ĵ������
#
# Revision 1.4  2007/11/27 07:58:59  yangkai
# CIST_KITBAG --> ITEM_WAREHOUSE_KITBAG
# CIST_CASKET --> ITEM_WAREHOUSE_CASKET
#
# Revision 1.3  2007/11/26 02:10:39  wangshufeng
# interface modify:bank_requireItemData -> bank_requireData
# interface modify:bank_unlockBag -> bank_unfreezeBag
#
# Revision 1.2  2007/11/24 02:53:29  yangkai
# ��Ʒϵͳ���������Ը���
# "wieldType" --> "eq_wieldType"
#
# Revision 1.1  2007/11/14 02:57:05  wangshufeng
# �����Ǯׯϵͳ
#
#
#
#
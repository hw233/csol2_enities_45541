# -*- coding: gb18030 -*-
#
# $Id: Bank.py,v 1.22 2008-08-08 03:10:24 fangpengjun Exp $


import BigWorld
from bwdebug import *
import csconst
import csstatus
import csdefine
import ItemTypeEnum
import cschannel_msgs
import ShareTexts as ST

import time
import items
import sys

g_item = items.instance()

GOLD_ITEM_ID = 110103022	#Ԫ��Ʊ

class Bank:
	"""
	Ǯׯϵͳ�ӿ�

	bankLockerStatus��ʾǮׯ������״̬�����ݣ���������״̬���Է����ɴ����ݲ�ѯ�ó�������Ҫ��def��������������ݡ��������£�
	bankLockerStatusλ��Ϊ8��ʹ�����ֽ�ģʽ�ұߵĵ�һλ����ʾǮׯ�Ƿ����������״̬����λ�ֽ�ģʽΪ0ʱ��ʾ��������Ϊ1ʱ��ʾ������
	ʹ���ұߵڶ�λ����ʾǮׯ�Ƿ�������״̬���ݣ�������Ϊ0������Ϊ1���ұߵ�������λ�����Ժ���չ��Ҫ��
	ʹ�����ұߵ��塢������λ����ʾǮׯ��������ʧ�ܴ������ݣ������Ա�ʾ7��ʧ�ܣ����ֽ�ģʽΪ111��bankLockerStatus����4λ�������ɵò������ݣ�
	ÿʧ��һ�ο�����λ�����+1��10�������㡣

		Ǯׯ������״̬����bankLockerStatus��״̬���£�
		0000 0000:������״̬
		0000 0001:������״̬
		0000 0010:����״̬
		0111 0000:Ǯׯ����ʧ�ܴ���
	"""
	def __init__( self ):
		"""
		"""
		#self.bankMoney 			# Ǯׯ�洢�Ľ�Ǯ��������def�ļ���
		#self.bagStatus 			# Ǯׯ����λ״̬��������def�ļ���
		#self.bankPassword			# Ǯׯ���������ݣ�������def�ļ���
		#self.bankUnlockLimitTime	# ����Ǯׯ������Ϊʱ�䣬������def�ļ���

		# ��ʼ������������״̬
		if self.bankPassword:		# ���Ǯׯ����������
			self.bankLockerStatus |= 0x03	# ���ֽ�ģʽ����Ϊ00000011

		if self.bankForceUnlockLimitTime > 0 :	# ������������ǿ�ƽ���
			now = int( time.time() )
			forceUnlockLeaveTime = self.bankForceUnlockLimitTime - now
			if forceUnlockLeaveTime <= 0 : 			# ���ǿ�ƽ���ʱ���ѵ�
				self.__forceUnlockKitbag()			# ǿ�ƽ�������
			else :
				self.__addForceUnlockTimer()		# �������ǿ�ƽ�����Timer

	def _isBankSetPassword( self ):
		"""
		��֤�Ƿ�������Ǯׯ����
		"""
		return not self.bankPassword == ""	# ��ʾ����������״̬��λ�Ƿ�Ϊ1

	def _isBankLocked( self ):
		"""
		��֤Ǯׯ�Ƿ�����
		"""
		return ( self.bankLockerStatus >> 1 ) & 0x01 == 1	# ��ʾǮׯ�Ƿ��������״̬λ�Ƿ�Ϊ1

	def _bankOperateVerify( self, srcEntityID, entityID ):
		"""
		��֤�Ƿ��ܹ�����Ǯׯ����

		@param entityID:����npc��id
		@type entityID: OBJECT_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return False
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return False

		# �ж��Ƿ��������׷�Χ��
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return False

		if self._isBankLocked():
			self.statusMessage( csstatus.BANK_ITEM_CANNOT_MOVE )
			DEBUG_MSG( "Ǯׯ�������ˡ�" )
			return False

		if self.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
			self.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
			return False
		
		statusID = npc.getScript().canUseBank( npc, self )
		if statusID != csstatus.BANK_CAN_USE:
			self.statusMessage( statusID )
			return False
			
		return True

	def _getRequireItemCount( self ):

		items = self.findItemsByIDFromNKCK( csdefine.ID_OF_ITEM_OPEN_BAG )
		count = 0
		for item in items:
			count += item.amount
		return count

	def bank_canActivateBag( self,amount ):
		"""
		�ж��Ƿ��ܹ����������
		"""
		return True

	def bank_activateBag( self, srcEntityID ):
		"""
		Exposed method.
		�������
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return False
		# �жϰ����Ƿ���ס��
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		count = self._getRequireItemCount()
		self.base.bank_activateBag( count )

	def onBank_activateBagSuccess( self, itemAmount ):
		# ��Ҫ��������base�ṩ�ĵ��ýӿڡ�
		# ����ֿ�ɹ�ʱ��������ʣ��Ҫ������
		# @param:itemAmount		���������Ӧ��ɾ�����ٸ���˿ľ
		# @type: int

		items = self.findItemsByIDFromNKCK( csdefine.ID_OF_ITEM_OPEN_BAG )
		# Ϊ�˷�ֹ��˿ľ�Ȳ��Ϸֶ�ʱ��ȥ���� ��һЩ���� by����
		if len( items ) > 1:
			for item in items:
				amount = item.getAmount()
				if itemAmount <= 0: break
				if amount > itemAmount: amount = itemAmount
				itemAmount -= amount
				self.removeItemByUid_( item.uid, amount, csdefine.DELETE_ITEM_ACTIVATEBAG )
		else:
			self.removeItemByUid_( items[0].uid,itemAmount, csdefine.DELETE_ITEM_ACTIVATEBAG )

	def bank_unfreezeBag( self, kitbagNum ):
		"""
		Define method.
		�ṩ��base�Ļ������������б����������Ľӿ�

		param kitbagNum:��������λ��
		type kitbagNum:	UINT8
		"""
		if self.kitbags[kitbagNum].isFrozen():
			self.kitbags[kitbagNum].unfreeze()

	#------------------------------------��Ǯׯ�����Ʒ BEGIN------------------------------
	def bank_storeItemFailed( self, itemOrder ):
		"""
		Define method.
		�洢��Ʒ��Ǯׯʧ��

		@param itemOrder : û�洢�ɹ�����Ʒorder
		@type itemOrder : INT16
		"""
		item = self.getItem_( itemOrder )
		if item is None:
			ERROR_MSG( "player( %s ) can not find item( order : %i )." % ( self.getName(), itemOrder) )
		else:
			item.unfreeze()

	def bank_storeItem2Order( self, srcEntityID, srcOrder, dstOrder, entityID ):
		"""
		Exposed method.
		��Ǯׯ��洢��Ʒ�Ľӿڣ���֪Ŀ����Ʒ��

		param srcOrder:	���Ӻ�
		type srcOrder:	INT16
		param bankBagNum:Ǯׯ����λ��
		type bankBagNum:UINT8
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():	# ����������by����
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		try:
			kitbag = self.kitbags[kitbagNum]
		except KeyError:
			ERROR_MSG( "����λ�ó���kitbagNum(%i)" % ( kitbagNum ) )
			return
		if kitbag.isFrozen():
			WARNING_MSG( "������������" )
			return
		if dstOrder % csdefine.KB_MAX_SPACE >= csconst.BANKBAG_NORMAL_ORDER_COUNT:
			HACK_MSG( "���(%s)Ǯׯ����λ��( %i )���ԡ�" % ( self.getName(), dstOrder ) )
			return

		item = self.getItem_(  srcOrder )
		if item is None:
			DEBUG_MSG( "��Ʒ������" )
			return
		if item.isFrozen():
			WARNING_MSG( "��Ʒ������." )
			return
		if not item.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return
		item.freeze()

		# ȡ��һ�ݸɾ�����Ʒ���ݷ���base
		self.base.bank_storeItem2Order( srcOrder, item.copy(), dstOrder )

	def bank_storeItem2Bank( self, srcEntityID, srcOrder, entityID ):
		"""
		Exposed method.
		��Ǯׯ��洢��Ʒ�Ľӿڣ���ָ������λ��Ŀ����ӣ���Ǯׯ����ҵ�һ����λ
		�Ҽ�����洢��Ʒ�Ľӿ�

		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():	# ����������by����
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		try:
			kitbag = self.kitbags[kitbagNum]
		except KeyError:
			ERROR_MSG( "����λ�ó���kitbagNum(%i)" % ( kitbagNum ) )
			return
		if kitbag.isFrozen():
			WARNING_MSG( "������������" )
			return
		item = self.getItem_(  srcOrder )
		if item is None:
			ERROR_MSG( "��Ʒλ�ó���srcOrder(%i)" % ( srcOrder ) )
			return
		if item.isFrozen():
			WARNING_MSG( "��Ʒ������." )
			return
		if not item.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return
		item.freeze()
		self.base.bank_storeItem2Bank( srcOrder, item.copy() )

	def bank_storeItem2Bag( self, srcEntityID, srcOrder, bankBagNum, entityID ):
		"""
		Exposed method.
		��Ǯׯ��洢��Ʒ�Ľӿڣ���ָ���˰���λ

		param kitbagNum:��������λ��
		type kitbagNum:	UINT8
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param bankBagNum:Ǯׯ����λ��
		type bankBagNum:UINT8
		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():	# ����������by����
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return
		if bankBagNum < csdefine.BANK_COMMON_ID or bankBagNum >= csdefine.BANK_COUNT:		# ����λ�������
			HACK_MSG( "����λ�����Ƿ�bankBagNum(%i)." % ( bankBagNum ) )
			return
		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		try:
			kitbag = self.kitbags[kitbagNum]
		except KeyError:
			ERROR_MSG( "����λ�ó���kitbagNum(%i)" % ( kitbagNum ) )
			return
		if kitbag.isFrozen():
			WARNING_MSG( "������������" )
			return
		item = self.getItem_( srcOrder )
		if item is None:
			ERROR_MSG( "��Ʒλ�ó���srcOrder(%i)" % ( srcOrder ) )
			return
		if item.isFrozen():
			WARNING_MSG( "��Ʒ������." )
			return
		if not item.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return
		item.freeze()
		self.base.bank_storeItem2Bag( srcOrder, item.copy(), bankBagNum )

	def bank_storeItemSuccess01( self, dstOrder ):
		"""
		Define method.
		��Ǯׯ��λ�洢һ����Ʒ�ɹ�����cell������ɾ����Ʒ
		��base��,������Ǯׯ�洢һ����Ʒ�ɹ��Ļص�����
		"""
		item = self.getItem_( dstOrder )
		if self.deleteItem_( dstOrder, reason = csdefine.DELETE_ITEM_STOREITEM ):
			self.statusMessage( csstatus.CIB_MSG_STORE_ITEMS_TO_BANK,item.name(),item.amount )

	def bank_storeItemSuccess02( self, dstOrder, item ):
		"""
		Define method.
		����һ����Ʒ��ʣ�࣬����ǮׯĿ����ӽ�����Ʒ����ʣ����Ʒ�򽻻�����Ʒ�Żر���
		��base��,������Ǯׯ�洢һ����Ʒ�ɹ��Ļص�����
		"""
		kitbagNum = dstOrder / csdefine.KB_MAX_SPACE
		item1 = self.getItem_( dstOrder )
		if self.deleteItem_( dstOrder, reason = csdefine.DELETE_ITEM_STOREITEM  ):
			addResult = self.addItemByOrder_( item, dstOrder, reason = csdefine.ADD_ITEM_STOREITEM )
			if addResult == csdefine.KITBAG_ADD_ITEM_SUCCESS:
				if item1.id == item.id:
					amount = item1.amount - item.amount
					if amount > 0:
						statusID = csstatus.CIB_MSG_STORE_ITEMS_TO_BANK
					else:
						amount = -amount
						statusID = csstatus.CIB_MSG_FETCH_ITEMS_FROM_BANK
					self.statusMessage( statusID, item1.name(), amount )
				else:
					self.statusMessage( csstatus.CIB_MSG_STORE_ITEMS_TO_BANK, item1.name(),item1.amount )
					self.statusMessage( csstatus.CIB_MSG_FETCH_ITEMS_FROM_BANK, item.name(),item.amount )
		else:
			# ����˵���ﲻӦ�û������������˿�����BUG
			ERROR_MSG( "���򱳰�������һ������ʱʧ�ܡ�kitTote = %i, kitName = %s, orderID = %i" % (kitbagNum, self.kitbags[kitbagNum].srcID, dstOrder) )

	#------------------------------------��Ǯׯ�����Ʒ END------------------------------


	#------------------------------------��Ʒ��Ǯׯȡ�� BEGIN------------------------------
	def bank_fetchItem2Order( self, srcEntityID, srcOrder, dstOrder, entityID ):
		"""
		�����Ǯׯ��Ʒ����Ʒ��ȷ���ı�����Ʒ��

		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():	# ����������by����
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		kitbagNum = dstOrder / csdefine.KB_MAX_SPACE
		try:
			kitbag = self.kitbags[kitbagNum]
		except KeyError:
			ERROR_MSG( "����λ�ó���kitbagNum(%i)" % ( kitbagNum ) )
			return
		if kitbag.isFrozen():
			WARNING_MSG( "������������" )
			return
		item = self.getItem_(dstOrder)
		if item and not item.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return

		self.base.bank_fetchItem2Order( srcOrder, dstOrder )

	def bank_fetchItem2OrderCB( self, dstOrder, item, srcOrder ):
		"""
		Define method.
		��base��bank_fetchItem2Order���ã���base����������Ʒ���õ�Ŀ����Ʒ��
		"""
		if not self._addItem2Order( dstOrder, srcOrder, item ):	# ���ʧ��
			self.base.bank_fetchItemFailed( srcOrder )
			return

	def _addItem2Order( self, dstOrder, bankOrder, srcItem ):
		"""
		��һ����Ʒ�ŵ�ָ�������ĸ�����,��bank_fetchItem2OrderCB����
		�ɹ��򷵻�true�����򷵻�false

		param kitbag:	����ʵ��
		type kitbag:	KITBAG
		param dstOrder:	���Ӻ�
		type dstOrder:		INT16
		"""
		if self.addItemByOrder_( srcItem, dstOrder, reason = csdefine.ADD_ITEM_ADDITEM2ORDER ) == csdefine.KITBAG_ADD_ITEM_SUCCESS:
			self.base.bank_fetchItemSuccess01( bankOrder )
			return True

		dstItem = self.getItem_( dstOrder )
		if dstItem.isFrozen():
			WARNING_MSG( "error code: ", csstatus.CIB_MSG_FROZEN )
			return False
		if not dstItem.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return False
		if dstItem.id == srcItem.id and dstItem.isBinded() != srcItem.isBinded() and dstItem.getAmount() < dstItem.getStackable():
			self.statusMessage( csstatus.BANK_BIND_TYPE_CANT_STACKABLE )
			return False
		if dstItem.id == srcItem.id and dstItem.getStackable() > dstItem.amount:	# �ɵ��ӵ������⴦��
			overlapAmount = dstItem.getStackable()
			dstAmount = dstItem.amount
			srcAmount = srcItem.amount
			storeAmount = min( overlapAmount - dstAmount, srcAmount )
			dstItem.setAmount( dstAmount + storeAmount, self, csdefine.ADD_ITEM_ADDITEM2ORDER )
			try:
				self.questItemAmountChanged( dstItem, dstItem.getAmount() )
			except:
				ERROR_MSG( "���( %s )�Ӱ��ֿ�ȡ��Ʒ�������������������" % self.getName() )
			srcAmount = srcAmount - storeAmount
			srcItem.setAmount( srcAmount )
			if srcAmount:	# ��Ŀ��λ�õ��Ӻ���ʣ�࣬�Żزֿ�
				self.base.bank_fetchItemSuccess02( bankOrder, srcItem )
				return True
			self.base.bank_fetchItemSuccess01( bankOrder )
			return True
		else:	# id��ͬ�Ĳ��ɵ�����Ʒ �� id��ͬ�Ŀɵ�����Ʒ �ǽ�������
			if self.deleteItem_( dstOrder, reason = csdefine.DELETE_ITEM_STOREITEM  ):
				if self.addItemByOrder_( srcItem, dstOrder, reason = csdefine.ADD_ITEM_ADDITEM2ORDER )== csdefine.KITBAG_ADD_ITEM_SUCCESS:
					self.base.bank_fetchItemSuccess02( bankOrder, dstItem )
					return True
		return False

	def bank_fetchItem2Kitbags( self, srcEntityID, srcOrder, entityID ):
		"""
		Exposed method.
		��Ǯׯ��ȡ����Ʒ�Ľӿڣ���ָ������λ��Ŀ����ӣ��ڱ�������ҵ�һ����λ

		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		if self.iskitbagsLocked():	# ����������by����
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return
		order = self.getNormalKitbagFreeOrder()
		if order == -1:
			DEBUG_MSG( "���(%s)�����޿�λ��" % ( self.getName() ) )
			return
		self.base.bank_fetchItem2Kitbags( srcOrder )

	def bank_fetchItem2KitbagsCB( self, srcOrder, srcItem ):
		"""
		Define method.
		��base��bank_fetchItem2Kitbags���ã���base����������Ʒ���õ�������
		"""
		if srcItem.getStackable() > 1:	# �ɵ��ӵ������⴦��
			if self.stackableItem( srcItem, reason = csdefine.ADD_ITEM_FETCHITEM2KITBAGS  ) == csdefine.KITBAG_STACK_ITEM_SUCCESS:
				self.base.bank_fetchItemSuccess01( srcOrder )
				try:
					self.questItemAmountChanged( srcItem, srcItem.getAmount() )
				except:
					ERROR_MSG( "���( %s )�Ӱ��ֿ�ȡ��Ʒ�������������������" % self.getName() )
				return
		order = self.getNormalKitbagFreeOrder()		# getNormalKitbagFreeOrder()������itemBagRole.py�У��ڱ����в��ҿ�λ
		if order == -1:
			self.base.bank_fetchItemFailed( srcOrder )
			self.statusMessage( csstatus.CIB_MSG_BAG_HAS_FULL )
			return
		addResult = self.addItemByOrder_( srcItem, order, reason = csdefine.ADD_ITEM_FETCHITEM2KITBAGS )
		if addResult == csdefine.KITBAG_ADD_ITEM_SUCCESS:
			self.base.bank_fetchItemSuccess01( srcOrder )

	#------------------------------------��Ʒ��Ǯׯȡ�� END------------------------------
	def bank_destroyItem( self, srcEntityID, order, entityID ):
		"""
		Exposed method.
		������Ʒ�Ľӿ�

		param kitbagNum:Ǯׯ����λ��
		type kitbagNum:UINT8
		param order:	���Ӻ�
		type order:	INT16
		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		self.base.bank_destroyItem( order )

	def bank_moveItem( self, srcEntityID, srcOrder, dstOrder, entityID ):
		"""
		Exposed method.
		��ͬһ���������ƶ���Ʒ�Ľӿ�

		param bankBagNum:Ǯׯ����λ��
		type bankBagNum:UINT8
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param srcOrder:	���Ӻ�
		type srcOrder:	INT16
		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		self.base.bank_moveItem( srcOrder, dstOrder )

	def bank_storeMoney( self, srcEntityID, money, entityID ):
		"""
		Exposed method.
		�����Ǯׯ�洢��Ǯ�Ľӿ�

		param money�����Ҫ��Ǯׯ��Ľ�Ǯ��Ŀ
		type money��UINT32
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return
		if int( money ) > int( self.money ):	# ע��,money���޷�����
			self.statusMessage( csstatus.BANK_MONEY_NOT_ENOUGH_TO_STORE )
			return
		if self.iskitbagsLocked():	# ����������by����
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		if money + self.bankMoney > csconst.BANK_MONEY_LIMIT:
			if self.bankMoney >=csconst.BANK_MONEY_LIMIT:		#���Ǯׯ���Ĵ�����ʹ������� ��ôֱ���˳�
				return
			temp = csconst.BANK_MONEY_LIMIT - self.bankMoney
			self.payMoney( temp, csdefine.CHANGE_MONEY_STORE)
			self.bankMoney = csconst.BANK_MONEY_LIMIT
			self.statusMessage( csstatus.BANK_MONEY_LIMIT )
			return

		self.payMoney( money, csdefine.CHANGE_MONEY_STORE )
		self.bankMoney = self.bankMoney + money

	def bank_fetchMoney( self, srcEntityID, money, entityID ):
		"""
		Exposed method.
		��Ҵ�Ǯׯȡ����Ǯ�Ľӿ�

		param money�����Ҫȡ���Ľ�Ǯ��Ŀ
		type money��UINT32
		"""
		if not self._bankOperateVerify( srcEntityID, entityID ):
			return

		if self.iskitbagsLocked():	# ����������by����
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		addMax = self.testAddMoney( int( money ) )			#���Լӵ�Ǯ������
		if addMax > 0:		#���������ٴ��ж����ȡ��Ǯ�� �Ƿ�ᳬ������
			if self.ifMoneyMax():	#������Я����Ǯ������ ��ô����
				return
			money = int( money ) + addMax	#��������ԼӵĽ�Ǯ

		if int( money ) > int( self.bankMoney ):
			if self.gainMoney( self.bankMoney, csdefine.CHANGE_MONEY_FETCH ):
				self.bankMoney = 0
				return
			return

		if self.gainMoney( money, csdefine.CHANGE_MONEY_FETCH ):
			self.bankMoney = self.bankMoney - money
			return
		return

	# ------------------------------------------Ǯׯ���������� BEGIN----------------------------------------
	def	bank_setPassword( self, srcEntityID, srcPassword, password, entityID ):
		"""
		Exposed method.
		���á��޸�Ǯׯ���붼ʹ�ô˽ӿڡ�Ǯׯ����Ϊ��ʱ��srcPasswordֵΪ"",�޸�����ʱsrcPasswordֵΪ ��ҵľ�����

		param srcPassword:	Ǯׯԭ����,
		type srcPassword:	STRING
		param password:	������������
		type password:	STRING
		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		# �ж��Ƿ��������׷�Χ��
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return

		# ����ͳһ���ж�entityID�ķ�ʽ

		if not cmp( srcPassword, self.bankPassword ) == 0:
			DEBUG_MSG( "�������ľ����벻��ȷ��" )
			if self.bankUnlockLimitTime > 0 and int( time.time() ) - self.bankUnlockLimitTime > 0:
				self.bankUnlockLimitTime = 0		# ���˽����������ޣ�ȡ������
				self.bankLockerStatus |= 0x10		# ���ұߵ�5λ����Ϊ1����ʾ��һ���������
				self.client.bank_lockerNotify( 3, 0 )	# �����������Ҫ֪ͨ���
				return
			if self.bankUnlockLimitTime == 0:		# ��Ҳ��ڽ�������������
				temp = self.bankLockerStatus >> 4
				temp += 1
				if temp == 3:						# ��������������ﵽ3��
					self.bankUnlockLimitTime = int( time.time() ) + csconst.BANK_CANT_UNLOCK_INTERVAL	# �������ƽ�������Ϊcsconst.BANK_CANT_UNLOCK_INTERVAL
					self.bankLockerStatus &= 0x03	# ��������������0���Ա��´����¼������
					return
				temp <<= 4
				self.bankLockerStatus &= 0x03		# �������ұ�2λ���䣬������λ����0
				self.bankLockerStatus |= temp		# ������״̬�仯����¼����������Ĵ���
				self.client.bank_lockerNotify( 3, 0 )	# �����������Ҫ֪ͨ���
				return
			self.client.bank_lockerNotify( 3, 0 )		# �ڽ������������ھ����������Ҫ֪ͨ���
			return

		if self.bankPassword == "":
			self.bankLockerStatus |= 0x01
			self.client.bank_lockerNotify( 0, 0 )		# ��������ɹ���֪ͨ�ͻ���
		else:
			self.client.bank_lockerNotify( 1, 0 )		# �޸�����ɹ���֪ͨ

		self.bankPassword = password

	def bank_lock( self, srcEntityID, entityID ):
		"""
		Exposed method.
		��Ǯׯ����������������������һ�û�ж�Ǯׯ������ǰ���£�������˽ӿڵ�ʹ������

		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		# �ж��Ƿ��������׷�Χ��
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return

		# ����ͳһ���ж�entityID�ķ�ʽ

		if not self._isBankSetPassword():
			HACK_MSG( "Ǯׯû�����롣" )
			return

		if self._isBankLocked():
			HACK_MSG( "Ǯׯ�Ѿ���������״̬��" )
			return

		self.bankLockerStatus |= 0x02		# ����Ǯׯ״̬Ϊ����״̬
		self.client.bank_lockerNotify( 4, 0 )

	def bank_unlock( self, srcEntityID, srcPassword, entityID ):
		"""
		Exposed method.
		��Ǯׯ�����������������Ǯׯ�����Ҹ�Ǯׯ������ǰ���£�������˽ӿڵ�ʹ��������
		ע�⣺�����Ĳ�������ڱ��ε�½�ڼ�ʧ��3�Σ�csconst.BANK_CANT_UNLOCK_INTERVAL�ڲ�����Ǯׯ����������

		param srcPassword:	Ǯׯԭ����,
		type srcsrcPassword:STRING
		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		# �ж��Ƿ��������׷�Χ��
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return

		# ����ͳһ���ж�entityID�ķ�ʽ

		if not self._isBankSetPassword():
			HACK_MSG( "Ǯׯû�����롣" )
			return

		if not self._isBankLocked():
			HACK_MSG( "Ǯׯ�Ѿ����ڷ�����״̬��" )
			return

		if self.bankUnlockLimitTime > 0:
			if not int( time.time() ) > self.bankUnlockLimitTime:	# ������Ҳ�ڿͻ�����������������������������ɽ���֪ͨ��ң�����������Ҫ֪ͨ
				remainTime = int( self.bankUnlockLimitTime - int( time.time() ) )
				self.client.bank_lockerNotify( 6, remainTime )
				DEBUG_MSG( "��Ҵ���csconst.BANK_CANT_UNLOCK_INTERVAL����������ڼ䡣" )
				return
			self.bankUnlockLimitTime = 0

		if not cmp( srcPassword, self.bankPassword ) == 0:
			DEBUG_MSG( "�����������벻��ȷ��" )
			temp = self.bankLockerStatus >> 4
			temp += 1
			if temp == 3:	# ��������������ﵽ3��
				self.bankUnlockLimitTime = int( time.time() ) + csconst.BANK_CANT_UNLOCK_INTERVAL
				self.bankLockerStatus &= 0x03			# ��������������0���Ա��´����¼������
				self.client.bank_lockerNotify( 2, 0 )		# �����������֪ͨ
				return
			temp <<= 4
			self.bankLockerStatus &= 0x03				# �������ұ�2λ���䣬������λ����0
			self.bankLockerStatus |= temp				# ������״̬�仯����¼����������Ĵ���
			self.client.bank_lockerNotify( 2, 0 )			# �����������֪ͨ
			return

		self.bankLockerStatus &= 0x03					# �ɹ�������,��������������0(�������3��������룬������)
		self.bankLockerStatus &= 0xfd					# ���ұߵ�2λ��0����ʾǮׯ���ڷ�����״̬
		self.client.bank_lockerNotify( 5, 0 )				# ֪ͨ�ͻ���
		self.__cancelForceUnlock()						# �ɹ���������ǿ�ƽ���

	def bank_onForceUnlock( self, srcEntityID ) :
		"""
		Exposed method
		�������ǿ�ƽ�������������������
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		if self.bankForceUnlockLimitTime > 0 :			# ��ǿ�ƽ�����������ڣ������ظ���Ӧ����
			self.statusMessage( csstatus.BANK_FORCE_UNLOCK_REPEAT )
			return
		if not self.bankLockerStatus & 0x02 :			# ����δ���ϣ�����������ǿ�ƽ���
			self.statusMessage( csstatus.BANK_FORCE_UNLOCK_FORBID )
			return
		self.bankForceUnlockLimitTime = int( time.time() ) + csconst.BANK_FORCE_UNLOCK_LIMIT_TIME
		self.__addForceUnlockTimer()

	def bank_clearPassword( self, srcEntityID, srcPassword, entityID ):
		"""
		Exposed method.
		��Ǯׯ���ý���������Ѿ���Ǯׯ�����������ǰ���£��˽ӿ����������õ����룬��Ǯׯ������Ϊ�ա�
		ע�⣺���ý����Ĳ�������ڱ��ε�½�ڼ�ʧ��3�Σ�csconst.BANK_CANT_UNLOCK_INTERVAL�ڲ�����Ǯׯ����������

		param srcPassword:	Ǯׯԭ����,
		type srcsrcPassword:STRING
		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		# �ж��Ƿ��������׷�Χ��
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return

		# ����ͳһ���ж�entityID�ķ�ʽ

		if not self._isBankSetPassword():
			HACK_MSG( "Ǯׯû�����롣" )
			return

		if self.bankUnlockLimitTime > 0:
			if int( time.time() ) <= self.bankUnlockLimitTime:	# ������Ҳ�ڿͻ�����������������������������ɽ���֪ͨ��ң�����������Ҫ֪ͨ
				remainTime = int( self.bankUnlockLimitTime - int( time.time() ) )
				self.client.bank_lockerNotify( 6, remainTime )
				DEBUG_MSG( "��Ҵ���csconst.BANK_CANT_UNLOCK_INTERVAL����������ڼ䡣" )
				return
			self.bankUnlockLimitTime = 0

		if not cmp( srcPassword, self.bankPassword ) == 0:
			DEBUG_MSG( "�������ľ����벻��ȷ��" )
			temp = self.bankLockerStatus >> 4
			temp += 1
			if temp == 3:	# ��������������ﵽ3��
				self.bankUnlockLimitTime = int( time.time() ) + csconst.BANK_CANT_UNLOCK_INTERVAL
				self.bankLockerStatus &= 0x03			# ��������������0���Ա��´����¼������
				self.client.bank_lockerNotify( 2, 0 )		# �����������֪ͨ
				return
			temp <<= 4
			self.bankLockerStatus &= 0x03				# �������ұ�2λ���䣬������λ����0
			self.bankLockerStatus |= temp				# ������״̬�仯����¼����������Ĵ���
			self.client.bank_lockerNotify( 2, 0 )			# �����������֪ͨ
			return

		self.bankPassword = ""
		self.bankLockerStatus &= 0x00
		self.bankUnlockLimitTime = 0					# ����û���ˣ����е�������������ݶ���0
		self.client.bank_lockerNotify( 7, 0 )
		self.__cancelForceUnlock()						# �ɹ���������ǿ�ƽ���

	def onBankForceUnlockTimer( self ) :
		"""
		ǿ�ƽ������������timer����
		"""
		self.__forceUnlockKitbag()

	def __forceUnlockKitbag( self ) :
		"""
		ǿ�ƽ�������
		"""
		self.bankPassword = ""								# �������
		self.bankLockerStatus &= 0x00						# ��������
		self.bankUnlockLimitTime = 0						# ����ʱ������
		self.bankForceUnlockLimitTime = 0					# ǿ�ƽ���ʱ������
		self.removeTemp( "bk_forceUnlock_timerID" )
		self.statusMessage( csstatus.BANK_FORCE_UNLOCK_SUCCESS )
		mailMgr = BigWorld.globalData["MailMgr"]
		content = cschannel_msgs.FORCE_UNLOCK_MAIL_CONTENT % cschannel_msgs.GMMGR_CANG_KU
		title = cschannel_msgs.FORCE_UNLOCK_MAIL_TITLE % cschannel_msgs.GMMGR_CANG_KU
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
		bk_forceUnlock_timerID = self.queryTemp( "bk_forceUnlock_timerID", 0 )
		if bk_forceUnlock_timerID > 0 :
			self.cancel( bk_forceUnlock_timerID )
			self.removeTemp( "bk_forceUnlock_timerID" )
		self.bankForceUnlockLimitTime = 0

	def __addForceUnlockTimer( self ) :
		"""
		���ǿ�ƽ�����timer
		"""
		now = int( time.time() )
		leaveTime = self.bankForceUnlockLimitTime - now
		if leaveTime <= 0 : return								# ʱ���ѳ���
		bk_forceUnlock_timerID = self.queryTemp( "bk_forceUnlock_timerID", 0 )
		if bk_forceUnlock_timerID > 0 : return					# �������һ��timer���������ظ����
		bk_forceUnlock_timerID = self.delayCall( leaveTime, "onBankForceUnlockTimer" )
		self.setTemp( "bk_forceUnlock_timerID", bk_forceUnlock_timerID )
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
		self.delayCall( 1, "statusMessage", csstatus.BANK_FORCE_UNLOCK_REMAIN, leaveText )


	# ------------------------------------------Ǯׯ���������� END----------------------------------------

	# -----------------------------------------���¹������ڽ���ı仯�Ѿ�����------------------------------


	def bank_changeGoldToItem( self, goldValue ):
		"""
		Define method.
		��Ʊ�滻Ϊ��Ԫ��Ʊ��Ʒ
		"""
		tempItem = items.instance().createDynamicItem( GOLD_ITEM_ID )
		tempItem.set( 'goldYuanbao', goldValue )
		if not self.addItemAndNotify_( tempItem, csdefine.ADD_ITEM_CHANGEGOLDTOITEM ):
			self.statusMessage( csstatus.KITBAG_IS_FULL )
			self.base.bank_changeGoldToItemCB( goldValue, False )
		else:
			self.base.bank_changeGoldToItemCB( goldValue, True )
			INFO_MSG( "---->>>���( %s ) �һ�Ԫ��Ʊ( ���%i )�ɹ���" % ( self.getName(), goldValue ) )

	# -----------------------------------------------------------------------------------------------------
#
# $Log: not supported by cvs2svn $
# Revision 1.21  2008/07/10 07:21:23  songpeifang
# ��������Ǯׯ����λ��ʱ��Ϊ����ʱ����Ǯ����ȴ��������ʾ��bug
#
# Revision 1.20  2008/07/07 11:04:24  wangshufeng
# method modify:bank_kitbagsOffload2Bank,����ж�°�����Ǯׯ�Ĵ������
#
# Revision 1.19  2008/07/03 04:50:39  songpeifang
# ����bug����Ǯׯ��Ʒ���ϰ����������������������Ҫ������Ʒ��������Ǯׯ��Ʒ���ͻ��˲�ˢ��
#
# Revision 1.18  2008/07/02 07:07:18  songpeifang
# �����˰���Ʒ��Ǯׯ����������Ǯׯ��Ʒ��ʱ��Ʒ����ɻ÷����ҵ�bug
#
# Revision 1.17  2008/07/02 05:40:00  songpeifang
# �����˰�����װ���󶨹���
#
# Revision 1.16  2008/05/30 03:00:02  yangkai
# �������������²ֿ����
#
# Revision 1.15  2008/05/13 06:05:51  wangshufeng
# method modify:bank_splitItem,ȥ��Ŀ�������Ŀ����Ӳ��������ұ�����һ����λ���ò�ֺ����Ʒ��
#
# Revision 1.14  2008/05/07 02:57:54  yangkai
# query( "stackable" ) -> getStackable()
#
# Revision 1.13  2008/04/19 07:33:20  wangshufeng
# ������һ������λ��Ҫ���ò���ʹ�õ�bug
#
# Revision 1.12  2008/04/03 06:31:05  phw
# KitbagBase::find2All()����Ϊfind()�������ķ���ֵ��ԭ����( order, toteID, itemInstance )��ΪitemInstance
# KitbagBase::findAll2All()����ΪfindAll()�������ķ���ֵ��ԭ����( order, toteID, itemInstance )��ΪitemInstance
# �������ϵı仯���������ʹ�õ����ϽӿڵĴ���
#
# Revision 1.11  2008/03/27 08:16:01  wangshufeng
# ������_isRentBagPlace����ֵ����ȷ��bug
#
# Revision 1.10  2008/02/03 03:30:11  wangshufeng
# no message
#
# Revision 1.9  2008/01/22 04:01:49  wangshufeng
# method modify��bank_lock,bank_unlock�ɹ����������������kitbags_lockerNotify֪ͨclient
#
# Revision 1.8  2008/01/18 06:28:19  zhangyuxing
# ������Ʒ���Ƴ���Ʒ�ķ�ʽ���˵���
#
# Revision 1.7  2007/12/22 09:50:09  fangpengjun
# �޸���bank_swapBag�ӿ�
#
# Revision 1.6  2007/12/11 06:50:52  wangshufeng
# add interface:_setBagData,��Դ��������Ʒ����ת�Ƹ�Ŀ�����.
#
# Revision 1.5  2007/12/05 03:20:30  wangshufeng
# no message
#
# Revision 1.4  2007/11/27 07:59:52  yangkai
# CIST_KITBAG --> ITEM_WAREHOUSE_KITBAG
# CIST_CASKET --> ITEM_WAREHOUSE_CASKET
#
# Revision 1.3  2007/11/27 03:41:10  wangshufeng
# no message
#
# Revision 1.2  2007/11/26 02:12:27  wangshufeng
# interface modify:bank_requireItemData -> bank_requireData
# interface modify:bank_unlockBag -> bank_unfreezeBag
#
# ������Ǯׯ����������
#
# Revision 1.1  2007/11/14 02:56:35  wangshufeng
# �����Ǯׯϵͳ
#
#
#
#
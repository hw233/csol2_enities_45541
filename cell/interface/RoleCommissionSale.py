# -*- coding: gb18030 -*-
#

import BigWorld
from bwdebug import *
import csdefine
import csconst
import csstatus
import ItemBagRole
import cPickle
import items

g_items = items.instance()	# �ڴ���һ����Ʒʱ��Ҫ

class RoleCommissionSale:
	"""
	����ϵͳ���cell�˽ӿ�
	"""
	def __init__( self ):
		"""
		"""
		# persistent�����ݣ������Ϊ0��ȥ�����ݿ⣬���Ϊ0�ͱ����޼�����Ϣ���ü�����ݿ�
		# ����ÿ�����߶����ж�ȡ���ݿ���������ֵĬ��Ϊ0����Ϊ0ʱ��ʾ��������ݿ��м�������Ʒ������������м����ʱ����
		# self.cms_itemNum = 0


	def __operateVerify( self, entityID ):
		"""
		��֤�Ƿ��ܹ����м�������

		@param entityID:����npc��id
		@type entityID: OBJECT_ID
		"""
		if self.level < 10:		# ��������С����Ϊ10
			return False

		# ����һ���Ƿ����ҵ���NPC
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			return False

		# �ж��Ƿ��������׷�Χ��
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )	# ��ʱʹ��IV_TRADER_TOO_FAR
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return False

		# ����ͳһ���ж϶�Ӧ�Ľ���npc����������ʱ��ʹ��wangshufeng
		#if not npc.commissionNPC:	# ��֤�Ƿ��Ǽ���npc
		#	return False

		# ��npc��def����룺
		#<commissionNPC>
		#	<Type>			BOOL			</Type>
		#	<Flags>			CELL_PUBLIC		</Flags>
		#	<Persistent>		false			</Persistent>
		#	<Default>		1			</Default>
		#</commissionNPC>

		return True


	def cms_enterTrade( self, entityID ):
		"""
		Define method.
		������npc����

		@param entityID:	����NPC��id
		@type entityID:		OBJECT_ID
		"""
		if not self.__operateVerify( entityID ):
			return

		self.client.cms_enterTrade()	# ֪ͨ�ͻ��˴򿪼�������


	def cms_saleGoods( self, srcEntityID, price, uid, entityID ):
		"""
		Exposed method.
		����һ����Ʒ
		@param srcEntityID������������ID
		@type srcEntityID:	OBJECT_ID
		@param price��		�����ļ۸�
		@type price:		UINT32
		@param uid��		��Ʒ��ΨһID
		@type uid:			INT64

		���̣�	1��������ּ����������жϣ��κ�һ������������ֱ�ӷ��ء��ڿͻ���Ҳ�������Ƶ��жϣ���ʾ��ϢҲ�ڿͻ����Ǳ߷��ء�
				2�������������ҵ�Ӱ�졣��Ǯ���ˣ���Ʒû�ˣ�
				3����¼���Ӱ�쵽��־���������������ʱ��鿴��
				4��������������������Ϣ�ύ��base�� ������������
		"""
		if srcEntityID != self.id:
			return False

		if not self.__operateVerify( entityID ):
			return

		if not self.cms_itemNum < csconst.COMMISSION_ITEMS_UPPER_LIMIT:
			self.statusMessage( csstatus.CMS_ITEM_OVERSTEP )
			return

		item = self.getItemByUid_( uid )
		# �������޴���Ʒ
		if item == None:
			return

		# ��������Ǯ���Ƿ��ܹ�֧����������
		value = price * csconst.COMMISSION_CHARGE_PERCENT
		if self.money < int( value ):
			return

		# ��ȡ��Ҽ������ã�����Ʒ����ұ���ɾ��
		self.payMoney( value, csdefine.CHANGE_MONEY_SALEGOODS )
		self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_SALEGOODS )
		self.cms_itemNum += 1	# ÿ����һ����Ʒ����������1

		# ����Ʒ����д����־���Ա���Ʒ���������
		itemData = repr( item.addToDict() )
		INFO_MSG( "INFO:%s vender an item. price of item: %i, item data: %s" % ( self.playerName, price, itemData ) )

		# ����Ʒ���͸�����ϵͳ
		self._getCommissionSaleMgr().saleGoods( self.playerName, price, item )


	def cms_buyGoods( self, srcEntityID, index, entityID ):
		"""
		Exposed method.
		�Ӽ���ϵͳ����һ����Ʒ

		@param srcEntityID���������͹����ĵ�����id
		@type srcEntityID:	OBJECT_ID
		@param index��		��Ʒ�����
		@type index:		INT32

		���̣�	1��������ּ���������жϣ��κ�һ������������ֱ�ӷ��ء��ڿͻ���Ҳ�������Ƶ��жϣ���ʾ��ϢҲ�ڿͻ����Ǳ߷��ء�
					��Ʒ������Ҫ�����ݿ��ж�������������������ж�û���漰����Ʒ��Ϣ��
				2�����������Ʒ���������Ϣ�ύ��base�� ������������
		"""
		if srcEntityID != self.id:
			return False

		if not self.__operateVerify( entityID ):
			return

		tempOrder = self.getNormalKitbagFreeOrder()
		if tempOrder == -1:
			self.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return

		self._getCommissionSaleMgr().buyGoods( index, self.money, self.base )


	def cms_receiveSaleItem( self, owner, price, item, index ):
		"""
		Define method.
		����ҷ���һ����Ʒ

		@param owner:	������Ʒ��������
		@type owner:	STRING
		@param price:	������Ʒ�ļ۸�
		@type price:	INT32
		@param item:	������Ʒ
		@type item:		ITEM
		@param index:	��Ʒ����
		@type item:		INT32
		"""
		# ��һ�μ������Ƿ�Ǯ
		if self.money < price:
			return

		self.payMoney( price, csdefine.CHANGE_MONEY_RECEIVESALEITEM )
		self.addItem( item, csdefine.ADD_ITEM_RECEIVESALEITEM )
		itemName = item.query( "name" )

		self._getCommissionSaleMgr().sendItemSuccess( self.playerName, index )


	def cms_receiveCancelItem( self, item, index ):
		"""
		Define method.

		���ȡ��������Ʒ�Ľӿ�
		"""
		self.cms_itemNum -= 1
		self.addItem( item, csdefine.ADD_ITEM_RECEIVECANCELITEM )
		self._getCommissionSaleMgr().cancelSuccess( index )


	def cms_receiveMoney( self, price, itemName, buyerName, index ):
		"""
		Define method.
		֪ͨ������Ʒ����

		@param price: 	��Ʒ�ļ۸�
		@type price: 	UNINT32
		@param itemID: 	��Ʒ��id
		@type itemID: 	STRING
		@buyerName: 	����Ʒ���������
		@type buyerName: STRING
		@param index:	��Ʒ����
		@type item:		INT32

		���̣�	1����Ǯ̫��Ĵ���
				2����ҳɹ���ü�����Ǯ��ͳ��
		"""
		if self.testAddMoney( price ) > 0:
			self.statusMessage( csstatus.CIB_MONEY_OVERFLOW )
			return

		if self.gainMoney( price, csdefine.CHANGE_MONEY_CMS_RECEIVEMONEY ) == False:
			# �´����������»��
			return

		self.cms_itemNum -= 1
		# ��Ǯʱд����־
		INFO_MSG( "vender receive the money for commission.verderName:'%s', price: '%i',itemIndex:'%i' "\
			 % ( self.playerName, price, index ) )
		self._getCommissionSaleMgr().sendMoneySuccess( index )
		self.statusMessage( csstatus.CMS_NOTIFY_VENDER, itemName, buyerName )


	def cms_cancelSaleGoods( self, srcEntityID, index, entityID ):
		"""
		Exposed method.
		ȡ��������Ʒ

		@param srcEntityID:	�ͻ�����ʽ����cell�ĵ�����id
		@type srcEntityID:	OBJECT_ID
		@param index:    	��Ʒ���
		@type index:		INT32
		@param entityID: 	����NPC��id
		@type entityID:		OBJECT_ID

		���̣�	1������򵥵�ȡ�������ж�
				2����ȡ��������Ʒ����������Ϣ���͵�base�� ����������
		"""
		if srcEntityID != self.id:
			return False

		if not self.__operateVerify( entityID ):
			return

		# getNormalKitbagFreeOrder(),�п�λ�򷵻�һ��order�����򷵻�-1
		if self.getNormalKitbagFreeOrder() == -1:	# ����û�пո�
			self.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return

		self._getCommissionSaleMgr().cancelSaleGoods( index, self.base, self.playerName )


	def _getCommissionSaleMgr( self ):
		"""
		���ȫ�ֵļ���������

		@return: CommissionSaleMgr��base mailbox
		"""
		# ��������쳣�ͱ�ʾ��bug
		return BigWorld.globalData["CommissionSaleMgr"]


	def cms_queryByType( self, srcEntityID, param1, param2, param3, beginNum, callFlag, entityID ):
		"""
		Exposed method.

		����Ʒ���Ͳ�ѯ,Ϊ����Ӧ����������Ʒ��3���ѯ(����߻��ĵ�),������param1,param2,param3��3������,��3�������Ľ�����callFlag����.
		��callFlagΪ1ʱ,param1Ϊ��Ʒ����,param2Ϊ0,param3Ϊ0,��ʱ�ǰ���Ʒ���Ͳ�ѯ;
		��callFlagΪ2ʱ,˵���ǲ�ѯ�������͵���Ʒ->����������ְҵ,param1Ϊ��Ʒ����,param2Ϊ������ְҵ,param3Ϊ0;
		��callFlagΪ3ʱ,˵���ǲ�ѯ�������͵���Ʒ->����������ְҵ->�����ĵ�˫������,param1Ϊ�������param2Ϊ������ְҵ,param3Ϊ�����ĵ�˫������
		����ѯ�Ĳ����������͵���Ʒʱ,�����õ�param1,��Ϊ������Ʒû������������Ʒ�Ĳ�ѯ���.

		@param param1,param2,param3: ����callFlag����������3������������
		@type param1: 		STRING
		@type param2:		STRING
		@type param3:		STRING
		@param beginNum : 	��ѯ��Ʒ�Ŀ�ʼλ��
		@type biginNum:		INT32
		@param call : 		��ѯ������
		@type call : 		INT8
		@param entityID: 	����NPC��id
		@type entityID:		OBJECT_ID
		"""
		if srcEntityID != self.id:
			return False

		if not self.__operateVerify( entityID ):
			return

		self._getCommissionSaleMgr().queryByType( param1, param2, param3, beginNum, callFlag, self.base, self.playerName )


	def cms_queryByItemName( self, srcEntityID, itemName, beginNum, entityID ):
		"""
		Exposed method.

		���ͻ����ṩ�ĸ�����Ʒ���ֲ�ѯ�Ľӿ�
		@param entityID: 	����NPC��id
		@type entityID:		OBJECT_ID
		"""
		if srcEntityID != self.id:
			return False

		if not self.__operateVerify( entityID ):
			return

		self._getCommissionSaleMgr().queryByItemName( itemName, beginNum, self.base, self.playerName )


	def cms_queryOwnGoods( self, srcEntityID, beginNum, entityID ):
		"""
		Exposed method.
		��ѯ�Լ�������Ʒ�Ľӿ�
		@param entityID: 	����NPC��id
		@type entityID:		OBJECT_ID
		"""
		if srcEntityID != self.id:
			return False

		if not self.__operateVerify( entityID ):
			return

		self._getCommissionSaleMgr().queryOwnGoods( beginNum, self.base, self.playerName )
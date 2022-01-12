# -*- coding: gb18030 -*-
#
# $Id: RoleVend.py,v 1.6 2008-09-03 07:26:12 wangshufeng Exp $

import BigWorld
import time
import Language#add by wuxo 2012-5-21

from bwdebug import *
import csdefine
import csconst
import csstatus
import random
from ChatProfanity import chatProfanity
import sys
from MsgLogger import g_logger
from VehicleHelper import getCurrVehicleID

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_WIELD | \
		 	csdefine.ACTION_FORBID_TRADE | csdefine.ACTION_FORBID_ATTACK		# ������ �ƶ���ʹ����Ʒ��װ�������ס�����

SPECIALSHOP_ITEM_BUY_LEVEL = 30 #�̳���Ʒ����ȼ����Ϊ30

class RoleVend:
	"""
	��Ұ�̯ϵͳ
	"""
	def __init__( self ):
		"""
		"""
		# self.vendMerchandise		��̯��Ʒλ����Ϣ�б�
		# self.vendSignboard		̯λ������
		pass

	def _canVend( self ):
		"""
		�ж��Լ��Ƿ��ܰ�̯
		"""
		if not self.canVendInArea():
			return csstatus.VEND_FORBIDDEN_AREA

		if self.vehicle or getCurrVehicleID( self ):
			return csstatus.VEND_NO_VEHICLE

		if self.iskitbagsLocked():
			return csstatus.VEND_FORBIDDEN_BAG_LOCKED

		if self.intonating():
			return csstatus.VEND_FORBIDDEN_VEND_ON_INTONATE

		if self.isTeamFollowing():
			return csstatus.VEND_FORBIDDEN_FOLLOWING

		if self.hasFlag( csdefine.ROLE_FLAG_TISHOU ):
			return csstatus.VEND_FORBIDDEN_VEND_ON_TISHOU

		if self.getState() != csdefine.ENTITY_STATE_FREE:
			return csstatus.VEND_FORBIDDEN_NOT_FREE_STATE

		return csstatus.VEND_NO_PROBLEM

	def _isVend( self ):
		"""
		�ж��Լ��Ƿ��ڰ�̯״̬
		"""
		return self.getState() == csdefine.ENTITY_STATE_VEND


	def vend_vend( self, srcEntityID, kitUidList, uidList, priceList, petDatabaseIDList, petPriceList ):
		"""
		Exposed method.
		��Ұ�̯�Ľӿ�,�������Ƿ��ڰ�̯״̬,���ð�̯��Ʒ���ݣ���������ڰ�̯����ֹ���������Ϊ�ı�־��

		param uidList: ��Ұ�̯��Ʒ��uid�б�
		type uidList: ARRAY OF INT64
		param priceList: ���̯��Ʒ��Ӧ�İ�̯��Ʒ�۸��б�
		type priceList: ARRAY OF UINT32
		"""
		if srcEntityID != self.id:
			HACK_MSG( "�Ƿ�������." )
			return

		if self.level < 15: #���ӽ�ɫ��̯�ĵȼ����ƣ�15�����ϣ�
			self.statusMessage( csstatus.VEND_LEVEL_NOT_ENOUGH )
			return

		if self._isVend():
			HACK_MSG( "����Ѿ��ڰ�̯�ˡ�" )
			return

		if self.getState() == csdefine.ENTITY_STATE_DEAD:		# �жϽ�ɫ�Ƿ��Ѿ�����
			self.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
			return

		canVendStatus = self._canVend()
		if canVendStatus != csstatus.VEND_NO_PROBLEM:			# �ж��Ƿ��ڰ�̯����������
			self.statusMessage( canVendStatus )
			HACK_MSG( "��Ҵ��ڲ������̯״̬��" )
			return

		# �����̯����Ʒ����̯������ û�гɹ�
		if not self.vend_itemVend( kitUidList, uidList, priceList ) or not self.vend_petVend( petDatabaseIDList, petPriceList ):
			return

		actPet = self.pcg_getActPet()
		if actPet :
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )

		# ��������̯��������ҵ�״̬actWord,��client/Role.py��set_actWord�ӿ��л���������Ӧ�İ�̯����wsf
		self.changeState( csdefine.ENTITY_STATE_VEND )	# ���ð�̯״̬
		try:
			g_logger.roleVendLog( self.databaseID, self.getName() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

#	def vend_pauseVend( self, srcEntityID ):
#		"""
#		Exposed method.
#		�����ͣ��̯�Ľӿ�
#		"""
#		if srcEntityID != self.id:
#			HACK_MSG( "�Ƿ�������." )
#			return
#		self.vendMerchandise = []
#		self.setTemp( "isPauseVend", 1 ) #������ͣ��̯���
#		self.client.vend_isPauseVend( self.queryTemp( "isPauseVend" ) )


	def vend_itemVend( self, kitUidList, uidList, priceList ):
		"""
		��̯����Ʒ
		"""
		if len( kitUidList ) != len( uidList ) or len( kitUidList ) != len( priceList ):
			HACK_MSG( "��̯��Ʒλ�ò������Ȳ��ԡ�" )
			return False

		if len( kitUidList ) > csconst.VEND_ITEM_MAX_COUNT:
			HACK_MSG( "�����̯����Ʒ������������." )
			return False
		for kitUid, uid, price in zip( kitUidList, uidList, priceList ):
			if kitUid == csdefine.KB_EQUIP_ID:
				HACK_MSG( "װ������Ʒ�������ڰ�̯��" )
				return False
			tempItem = self.getItemByUid_( uid )
			if tempItem is None:
				ERROR_MSG( "%s(%i): ��Ʒ������( kitUid = %i, uid = %i )" % ( self.playerName, self.id, kitUid, uid ) )
				self.vendMerchandise = []
				return False

			if not self.canGiveItem( tempItem.id ):	# �ض���Ʒ�ȼ����Ʋ��ܰ�̯
				ERROR_MSG( "%s(%i): item( id = %s )�ȼ����Ʋ��ɰ�̯." % (self.playerName, self.id, tempItem.id) )
				self.statusMessage( csstatus.TISHOU_FORBID_CANNOT_GIVE_ITEM, csconst.SPECIFIC_ITEM_GIVE_LEVEL )
				self.vendMerchandise = []
				return False

			if not tempItem.canGive():	# �������Ĳ��������ڰ�̯
				ERROR_MSG( "%s(%i): item( id = %s )���ɳ���." % (self.playerName, self.id, tempItem.id) )
				self.vendMerchandise = []
				return False
			if not tempItem.canExchange():	# ������Ҽ佻�׵Ĳ����� by����
				self.statusMessage( csstatus.ROLE_TRADE_ITEM_NOT_TRADE )
				return False
			if price > csconst.ROLE_MONEY_UPPER_LIMIT:
				HACK_MSG( "���õİ�̯��Ʒ�۸���ߡ�" )
				return False
			self.vendMerchandise.append( { "kitUid":kitUid, "uid":uid, "price":price } )	# �Ѱ�̯��Ʒ��Ϣ����vendMerchandise

		for kitUid, uid, price in zip( kitUidList, uidList, priceList ):
			item = self.getItemByUid_( uid )
			item.freeze( self )				# ��̯�ɹ������ᱻ���ڰ�̯����Ʒ

		return True

	def vend_petVend( self, petDatabaseIDList, petPriceList ):
		"""
		��̯������
		"""
		if len( petDatabaseIDList ) != len( petPriceList ):
			HACK_MSG( "��̯�����λ�ò������Ȳ��ԡ�" )
			return False

		if len( petDatabaseIDList ) > csconst.VEND_PET_MAX_COUNT:
			HACK_MSG( "�����̯�ĳ���������������." )
			return False

		# �ж����д����۳����Ƿ��������
		for petDatabaseID, price in zip( petDatabaseIDList, petPriceList ):
			if not self.pcg_petDict.has_key( petDatabaseID ):
				HACK_MSG( "����ĳ���databaseID��" )
				return
			if self.pcg_isPetBinded( petDatabaseID ):
				self.statusMessage( csstatus.PET_HAD_BEEN_BIND )
				return
			if price > csconst.ROLE_MONEY_UPPER_LIMIT:
				HACK_MSG( "���õİ�̯����۸���ߡ�" )
				return False

		# ���з��ϳ��������ĳ���ϼܳ���
		for petDatabaseID, price in zip( petDatabaseIDList, petPriceList ):
			actPet = self.pcg_getActPet()
			if actPet and actPet.dbid == petDatabaseID :	# ���Ҫ��̯���۵ĳ����ڳ�ս�У����Ȼ���
				actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )

			# to do�������Ӱ�̯�����б�ǣ����ó��ۼ۸�
			self.base.vend_petForSale( petDatabaseID, price )

			self.vendPetMerchandise.append( { "databaseID" : petDatabaseID, "price" :price } )	# �Ѱ�̯��Ʒ��Ϣ����vendPetMerchandise

		return True

	def vend_endVend( self, srcEntityID, isEnd ):
		"""
		Exposed method.
		��ҽ�����̯�Ľӿ�
		isEnd				�Ƿ����
		"""
		if srcEntityID != self.id:
			HACK_MSG( "�Ƿ�������." )
			return

		for temp in self.vendMerchandise:
			kitUid = temp["kitUid"]
			uid = temp["uid"]
			item = self.getItemByUid_( uid )
			if item is None:
				ERROR_MSG( "�Ҳ�����Ʒ:kitUid(%i),uid(%i)" %( kitUid, uid ) )
				continue
			item.unfreeze( self )

		# �����¼ܣ��������İ�̯�б��
		for e in self.vendPetMerchandise:
			if not self.pcg_petDict.has_key( e["databaseID"] ):
				ERROR_MSG( "����ĳ���databaseID��" )
				continue
			self.base.vend_petEndForSale( e["databaseID"] )

		self.vendMerchandise = []
		self.vendPetMerchandise = []
#		self.vendSignboard = ""
		#self.actCounterDec( STATES )
		if self.getState() == csdefine.ENTITY_STATE_VEND:
			self.changeState( csdefine.ENTITY_STATE_FREE )	# ������̯���ı����״̬


	def vend_setSignboard( self, srcEntityID, signboard ):
		"""
		Exposed method.
		��������̯λ���ƵĽӿ�

		param signboard:�����õ�̯λ��
		type signboard:	STRING
		"""
		if srcEntityID != self.id:
			HACK_MSG( "�Ƿ�������." )
			return

		if not self._canVend():
			self.statusMessage( csstatus.VEND_FORBIDDEN_VEND )
			HACK_MSG( "��Ҵ��ڲ������̯״̬��" )
			return

		if len( signboard ) > csconst.VEND_SIGNBOARD_MAX_LENGTH:
			HACK_MSG( "��������." )
			return

		if chatProfanity.searchMsgProfanity( signboard ) is not None:
			return

		self.vendSignboard = signboard

	def	vend_buyerQueryInfo( self, srcEntityID ):
		"""
		Exposed method.
		�����client���ã���Ҳ鿴����̯λ����
		"""
		if srcEntityID == self.id:
			HACK_MSG( "�����߲������Լ�." )
			return

		if not self._isVend():
			HACK_MSG( "��������ڰ�̯״̬��" )
			return

		buyer = BigWorld.entities.get( srcEntityID )
		if buyer == None:
			HACK_MSG( "�Ҳ������, srcEntityID: %i" % ( srcEntityID ) )
			return

		if self.position.flatDistTo( buyer.position ) > csconst.COMMUNICATE_DISTANCE:	# ��ʱʹ��COMMUNICATE_DISTANCE
			buyer.statusMessage( csstatus.VEND_DISTANCE_TOO_FAR )
			DEBUG_MSG( "too far from vendor: %i. ( srcEntityID: %s )" % ( self.id, srcEntityID ) )
			return

		items = []
		for temp in self.vendMerchandise:			# ����self.vendMerchandise��ð�̯��Ʒ���ݣ����͸����
			kitUid = temp["kitUid"]
			uid = temp["uid"]
			item = self.getItemByUid_( uid )
			if item == None:
				ERROR_MSG( "��̯��Ʒ���ݳ���" )
				return
			item = item.copy()
			item.setPrice( temp["price"] )			# ���ü۸�
			items.append( item )

		buyer.clientEntity( self.id ).vend_receiveShopData( items )	# ���Ͱ�̯��Ʒ���ݸ���ҿͻ���
		self.base.vend_buyerQueryPetInfo( buyer.base, self.vendPetMerchandise )	# �����·�����������Ϣ

		records = buyer.queryTemp( "vendRecord", [] )
		for record in records:
			buyer.clientEntity( self.id ).vend_receiveRecord( record )

	def vend_sell( self, srcEntityID, uid ):
		"""
		Exposed method.
		�ṩ����ҵĿͻ��˵��ã�vendor��һ����Ʒ�Ľӿ�

		param kitUid:	���������Ʒ��kitUid
		type kitUid:	UINT8
		param uid:	���������Ʒ��uid
		type Uid:	INT64
		"""
		if srcEntityID == self.id:
			HACK_MSG( "�����߲������Լ�." )
			return

		if not self._isVend():
			HACK_MSG( "���Ҳ��ڰ�̯״̬��" )
			return

		buyer = BigWorld.entities.get( srcEntityID )
		if buyer == None:
			HACK_MSG( "�Ҳ������, srcEntityID: %i." % ( srcEntityID ) )
			return

		if not buyer.isReal():
			DEBUG_MSG( "Ŀǰ������real entity֮��İ�̯���ס�" )
			return

		# �ж��Ƿ��������׷�Χ��
		if self.position.flatDistTo( buyer.position ) > csconst.COMMUNICATE_DISTANCE:	# ��ʱʹ��COMMUNICATE_DISTANCE
			buyer.statusMessage( csstatus.VEND_DISTANCE_TOO_FAR )
			DEBUG_MSG( "too far from vendor: %s. ( srcEntityID: %s )" % ( self.getName(), srcEntityID ) )
			return

		if uid < 0:
			HACK_MSG( "uid(%i)��������ȷ��" % ( uid ) )
			return

		if self.iskitbagsLocked():
			DEBUG_MSG( "���Ұ��������ˡ�" )
			return

		temp = None
		for itemInfo in self.vendMerchandise:
			if itemInfo["uid"] == uid:
				temp = itemInfo
				break
		if temp is None:
			buyer.statusMessage( csstatus.VEND_ITEM_IS_NONE )
			HACK_MSG( "��Ӧuid����Ʒ�����ڡ�" )
			buyer.clientEntity( self.id ).vend_removeItemNotify( uid )		# ����buyer�ͻ�������
			return

		price = temp["price"]
		if buyer.money < price:
			buyer.statusMessage( csstatus.VEND_NOT_ENOUGH_MONEY )
			DEBUG_MSG( "���Ǯ�������̯��Ʒ��" )
			return

		kitUid = temp["kitUid"]
		item = self.getItemByUid_( uid )			# ȡ��vendor�����е���Ʒ
		if item == None:
			buyer.statusMessage( csstatus.VEND_ITEM_IS_NONE )
			HACK_MSG( "��Ӧuid����Ʒ�����ڡ�" )
			index = self.vendMerchandise.index( temp )			# ɾ����Ӧ�İ�̯��Ʒ��Ϣ
			self.vendMerchandise.pop( index )
			buyer.clientEntity( self.id ).vend_removeItemNotify( uid )		# ����buyer�ͻ�������
			return

		kitbagState = buyer.checkItemsPlaceIntoNK_( [item] )
		if kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			buyer.statusMessage( csstatus.VEND_KITBAG_FULL )
			DEBUG_MSG( "�����Ʒ������" )
			return
		elif kitbagState == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			buyer.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
			DEBUG_MSG( "���ĳ��Ʒ��Ʒ�����ﵽ���ޡ�" )
			return

		if item.id in self.getAllSpecialShopItemID() and buyer.level < SPECIALSHOP_ITEM_BUY_LEVEL : #
			buyer.statusMessage( csstatus.VEND_SPECIALSHOP_ITEM_BUY_LEVEL    )	
			return
			
		nearMax = self.testAddMoney( price )
		if  nearMax >= 0:	#������Я���Ľ�Ǯ��������������Ʒ��Ǯ�ѵ�����
			buyer.statusMessage( csstatus.VEND_GAINMONEY_FAILD    )		#֪ͨ���
			self.statusMessage( csstatus.CIB_MONEY_OVERFLOW )		#֪ͨ����
			return
		elif nearMax == 0:
			buyer.statusMessage( csstatus.VEND_GAINMONEY_FAILD    )		#֪ͨ���
			self.statusMessage( csstatus.CIB_MSG_MONEY_OVERFLOW )		#֪ͨ����
			return

		item.unfreeze( self )									# ����Ʒ�ⶳ
		if not buyer.payMoney( price, csdefine.CHANGE_MONEY_VEND_SELL ):			# buyer��Ǯʧ��
			item.freeze( self )								# ���¶�����Ʒ�����ײ��ɹ�
			DEBUG_MSG( "��Ҹ�Ǯʧ�ܡ�" )
			return
		buyer.addItem( item.copy(), csdefine.ADD_ITEM_VEND_SELL )					# ����Ʒ��buyer

		#��̯���۳���1��Ҫ�����۵�1%˰,����1������5ͭ����1ͭ  by:���� 2009-5-25
		if price >= 100 :
			price = price * 99 / 100
		elif price > 5 :
			price = price - 1

		self.gainMoney( price, csdefine.CHANGE_MONEY_VEND_SELL )							# vendor��Ǯ
		# ����������¼����ʱ���ݣ����ߺ���ա�
		records = self.queryTemp( "vendRecord", [] )
		timeStr = "%s:%s"%( time.localtime()[3], time.localtime()[4] )
		records.append( [ buyer.getName(), item.id, price, timeStr, item.amount ] )
		self.setTemp( "vendRecord", records )
		self.client.vend_addRecordNotify( [ buyer.getName(), item.name(), price, timeStr, item.amount ] )
		self.removeItemByUid_( uid, reason = csdefine.DELETE_ITEM_VEND_SELL )		# vendorɾ����Ʒ
		index = self.vendMerchandise.index( temp )		# ɾ����Ӧ�İ�̯��Ʒ��Ϣ
		self.vendMerchandise.pop( index )
		self.client.vend_removeItemNotify( uid )		# ����vendor�ͻ�������
		buyer.clientEntity( self.id ).vend_removeItemNotify( uid )			# ����buyer�ͻ�������

	def vend_sellPet( self, srcEntityID, petDatabaseID ):
		"""
		�ṩ����ҵĿͻ��˵��ã�vendor��һ������Ľӿ�
		"""
		if srcEntityID == self.id:
			HACK_MSG( "�����߲������Լ�." )
			return

		if not self._isVend():
			HACK_MSG( "���Ҳ��ڰ�̯״̬��" )
			return

		buyer = BigWorld.entities.get( srcEntityID )
		if buyer == None:
			HACK_MSG( "�Ҳ������, srcEntityID: %i." % ( srcEntityID ) )
			return

		if not buyer.isReal():
			DEBUG_MSG( "Ŀǰ������real entity֮��İ�̯���ס�" )
			return

		# �ж��Ƿ��������׷�Χ��
		if self.position.flatDistTo( buyer.position ) > csconst.COMMUNICATE_DISTANCE:	# ��ʱʹ��COMMUNICATE_DISTANCE
			buyer.statusMessage( csstatus.VEND_DISTANCE_TOO_FAR )
			DEBUG_MSG( "too far from vendor: %s. ( srcEntityID: %s )" % ( self.getName(), srcEntityID ) )
			return

		if petDatabaseID < 0:
			HACK_MSG( "petDatabaseID(%i)��������ȷ��" % ( petDatabaseID ) )
			return

		if not self.pcg_petDict.has_key( petDatabaseID ):
			HACK_MSG( "����ĳ���databaseID��" )
			return

		temp = None
		for petInfo in self.vendPetMerchandise:
			if petInfo["databaseID"] == petDatabaseID:
				temp = petInfo
				break
		if temp is None:
			buyer.statusMessage( csstatus.VEND_PET_IS_NONE )
			HACK_MSG( "��ӦdatabaseID���ﲻ���ڡ�" )
			buyer.client.vend_removePetNotify( petDatabaseID )		# ����buyer�ͻ�������
			return

		if buyer.pcg_isFull():
			buyer.statusMessage( csstatus.VEND_PET_IS_FULL )
			HACK_MSG( "�򷽵ĳ���������" )
			return

		petDict = self.pcg_petDict.get( petDatabaseID )
		if buyer.level < petDict.takeLevel or buyer.level + 5 < petDict.level:
			buyer.statusMessage( csstatus.ROLE_PET_TAKE_LEVEL_INVALID )
			HACK_MSG( "�򷽵ĵȼ�����" )
			return

		price = temp["price"]
		if buyer.money < price:
			buyer.statusMessage( csstatus.VEND_NOT_ENOUGH_MONEY )
			DEBUG_MSG( "���Ǯ�������̯��Ʒ��" )
			return

		nearMax = self.testAddMoney( price )
		if  nearMax > 0:	#������Я���Ľ�Ǯ��������������Ʒ��Ǯ�ѵ�����
			buyer.statusMessage( csstatus.VEND_GAINMONEY_FAILD    )		#֪ͨ���
			self.statusMessage( csstatus.CIB_MONEY_OVERFLOW )		#֪ͨ����
			return
		elif nearMax == 0:
			buyer.statusMessage( csstatus.VEND_GAINMONEY_FAILD    )		#֪ͨ���
			self.statusMessage( csstatus.CIB_MSG_MONEY_OVERFLOW )		#֪ͨ����
			return

		if not buyer.payMoney( price, csdefine.CHANGE_MONEY_VEND_SELLPET ):			# buyer��Ǯʧ��
			DEBUG_MSG( "��Ҹ�Ǯʧ�ܡ�" )
			return

		#��̯���۳���1��Ҫ�����۵�1%˰,����1������5ͭ����1ͭ,���������:���� 2009-5-25
		if price >= 100 :
			price = price * 99 / 100
		elif price > 5 :
			price = price - 1

		self.gainMoney( price, csdefine.CHANGE_MONEY_VEND_SELLPET )							# vendor��Ǯ

		timeStr = "%s:%s"%( time.localtime()[3], time.localtime()[4] )
		self.base.vend_addRecordNotify( buyer.getName(), petDatabaseID, price, timeStr )

		self.base.vend_sellPet( buyer.base, petDatabaseID )	# ����ת��

		# ����������¼����ʱ���ݣ����ߺ���ա�
		if temp in self.vendPetMerchandise:
			self.vendPetMerchandise.remove( temp )

		self.client.vend_removePetNotify( petDatabaseID )							# ����vendor�ͻ�������
		buyer.clientEntity( self.id ).vend_removePetNotify( petDatabaseID )			# ����buyer�ͻ�������

	def vend_isVendedPet( self, dbid ) :
		"""
		���ݳ���DBID�жϸó����Ƿ��ڰ�̯��
		@param		dbid : �����DBID
		@type		dbid : DATABASE_ID
		@rtype		bool
		"""
		for petInfo in self.vendPetMerchandise :
			if petInfo["databaseID"] == dbid :
				return True
		return False

	def getAllSpecialShopItemID( self ):
		section = Language.openConfigSection( "config/server/SpecialShop.xml" )
		itemIDs = []
		if section is not None:
			for item in section.values():
				itemID = item.readInt( "itemID" )
				itemIDs.append( itemID )
		return itemIDs
	
# $Log: not supported by cvs2svn $
# Revision 1.5  2008/09/02 09:52:41  fangpengjun
# ������ҿͻ��˼�¼���º���vend_addRecordNotify
#
# Revision 1.4  2008/07/01 03:06:50  zhangyuxing
# ������Ʒ���뱳������ʧ�ܵ�״̬
#
# Revision 1.3  2008/05/30 03:01:33  yangkai
# װ������������Ĳ����޸�
#
# Revision 1.2  2008/05/07 02:58:55  yangkai
# no message
#
# Revision 1.1  2007/12/14 07:31:34  wangshufeng
# ��Ӱ�̯ϵͳ(RoleVend)
#
#
#
#
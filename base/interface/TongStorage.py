# -*- coding: gb18030 -*-

import time

from bwdebug import *
from MsgLogger import g_logger
import csdefine
import csconst
import csstatus
import Const
import ItemTypeEnum
import time

import items
g_item = items.instance()

EXTEND_LEVEL_LIST = [ 3, 5, 7, 9, 10 ]		# �ֿ�������չ�ռ�ļ����б�
REDUCE_LEVEL_LIST = [ 2, 4, 6, 8, 9 ]			# �ֿ⽵����С�ռ�ļ����б�

DAY_FETCH_ITEM_LIMIT = 30000

ITEM_QUALITYS = [ ItemTypeEnum.CQT_WHITE, ItemTypeEnum.CQT_BLUE, ItemTypeEnum.CQT_GOLD, ItemTypeEnum.CQT_PINK, ItemTypeEnum.CQT_GREEN ]

RESET_LIMIT_POINT = [ 0, 0, 0 ]



class TongStorage:
	"""
	���ֿ�Interface
	"""
	def __init__( self ):
		"""
		"""
		self._lastTote = 0
		self.storageFreezeFlag = False	# ���ֿ��Ƿ񶳽�ı��

		if self.storageLog is None:		# ��ʼ��
			self.storageLog = []

		if self.playerFetchRecord is None:
			self.playerFetchRecord = {}

		if len( self.storageBagPopedom ) == 0:
			# ���г�Ա��Ĭ��Ȩ��Ϊ��ȡ���޶����Ʒ
			gradeFetchItemLimit = { csdefine.TONG_DUTY_MEMBER		:	0,\
									csdefine.TONG_DUTY_TONG			:	0,\
									csdefine.TONG_DUTY_DEPUTY_CHIEF	:	0,\
									csdefine.TONG_DUTY_CHIEF		:	DAY_FETCH_ITEM_LIMIT,\
									}

			tongStoragePopedom = { "bagID":csdefine.TONG_STORAGE_ONE,
									"bagName":"",
									"qualityUpLimit":ItemTypeEnum.CQT_GREEN,
									"qualityLowerLimit":ItemTypeEnum.CQT_WHITE,
									"fetchItemLimit":gradeFetchItemLimit,
									}
			self.storageBagPopedom.append( tongStoragePopedom )
		
		for item in self.storageBagPopedom:
			if len( set( item[ "fetchItemLimit" ].keys() ) & set( csdefine.TONG_DUTYS ) ) != len( csdefine.TONG_DUTYS ):
				self.storageBagPopedom.remove( item )
				
				gradeFetchItemLimit = { csdefine.TONG_DUTY_MEMBER	:	0,\
										csdefine.TONG_DUTY_TONG	:	0,\
										csdefine.TONG_DUTY_DEPUTY_CHIEF	:	0,\
										csdefine.TONG_DUTY_CHIEF	:	DAY_FETCH_ITEM_LIMIT,\
										}

				tongStoragePopedom = { "bagID":csdefine.TONG_STORAGE_ONE,
										"bagName":"",
										"qualityUpLimit":ItemTypeEnum.CQT_GREEN,
										"qualityLowerLimit":ItemTypeEnum.CQT_WHITE,
										"fetchItemLimit":gradeFetchItemLimit,
										}
				self.storageBagPopedom.append( tongStoragePopedom )

		self.storage_resetLimitTimer = self.addTimer( self._storageCalcTime( RESET_LIMIT_POINT[:] ) )
		now = time.time()
		if now - self.resetStorageLimitTime >= 24 * 60 * 60:	# �����һ������ʱ����24Сʱ֮ǰ,��ô���ü�¼
			self.resetStorageLimit()


	def isStorageFrozen( self ):
		"""
		���ֿ��Ƿ񶳽�
		"""
		return self.storageFreezeFlag


	def freezeStorage( self ):
		"""
		������ֿ�,����ͬʱ���ж����Ҳ����ֿ�

		��Ϊ�漰��������������ݽ���,�����첽����,���뱣֤һ����ҵĲ������������Ҳ��ܲ���
		"""
		self.storageFreezeFlag = True


	def unFreezeStorage( self ):
		"""
		�ⶳ���ֿ�
		"""
		self.storageFreezeFlag = False


	def unFreezeStorageRemote( self ):
		"""
		Define method.
		Զ�̷������ⶳ���ֿ�
		"""
		self.unFreezeStorage()


	def _findFreeOrder( self ):
		"""
		��òֿ�ĵ�һ����λ
		"""
		for i in xrange( csdefine.TONG_STORAGE_ONE, csdefine.TONG_STORAGE_ONE + csdefine.TONG_STORAGE_COUNT ):
			if i >= len( self.storageBagPopedom ): continue
			# ������ʱ��ΪֻҪ���ܷŵ����������Ʒ���ܷŵ�Ǯׯ�У���Ʒ�Ƿ��ܱ��洢Ӧ������Ʒ��������Զ���Ӧ���ǰ����ṩ�ӿ��жϡ�wsf
			#if not self.bankBags[i].canPlace( self, itemInstance ): continue
			order = self._findBagFreeOrder( i )
			if order == -1: continue
			return order	# orderID
		return -1


	def _findBagFreeOrder( self, bagID ):
		"""
		��ð��ֿ�ָ�������ĵ�һ����λ
		"""
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID ��������,�������:%s,bagID:%i." % ( self.playerName, bagID ) )
			return
		startOrder = bagID * csdefine.KB_MAX_SPACE
		for order in xrange( startOrder, startOrder + csconst.TONG_BAG_ORDER_COUNT ):
			if not self.storage.orderHasItem( order ):
				return order
		return -1

	def addStorageLog( self, playerDBID, operation, srcItem, bagID, date ):
		"""
		��¼���ֿ������־

		@param playerDBID : ��ҵ�DBID
		@type playerName : TongEntitiy.MemberInfos
		@operation : ��ҵĲ���:ȡ�� �� ����
		@type srcItem : ITEM
		@param srcItem : ��Ʒʵ��
		@type itemCount : INT
		@param bagID : �ֿ�İ���id
		@type bagID : INT16
		@param date : �����ֿ��ʱ��
		@type date : INT64
		"""
		memberINFO = self.getMemberInfos( playerDBID )
		logINFO = ( memberINFO.getName(), operation, srcItem.id, srcItem.getAmount(), bagID, date )
		self.storageLog.append( logINFO )
		if len( self.storageLog ) > csconst.TONG_STORAGE_LOG_COUNT:	# ֻ�洢200��
			self.storageLog.pop( 0 )
		memberINFO.getBaseMailbox().client.tong_receiveStorageLog( logINFO )

		if operation == csdefine.TONG_STORAGE_OPERATION_ADD:
			try:
				g_logger.tongItemAddLog( self.databaseID, self.getName(), playerDBID, memberINFO.getName(), srcItem.getuid(), srcItem.id, srcItem.getAmount(), bagID )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
				
		elif operation == csdefine.TONG_STORAGE_OPERATION_MINUS:
			try:
				g_logger.tongItemRemoveLog( self.databaseID, self.getName(), playerDBID, memberINFO.getName(), srcItem.getuid(), srcItem.id, srcItem.getAmount(), bagID )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

	def requestStorageLog( self, playerDBID, count ):
		"""
		Define method.
		������ֿ��log��Ϣ

		@param playerDBID : ��ҵ�dbid
		@type playerDBID : DATABASE_ID
		@param count : ����Ĵ���
		@type count : INT8
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return

		startIndex = count * 50
		if startIndex > len( self.storageLog ):
			return

		endIndex = startIndex + 50
		if endIndex > len( self.storageLog ):
			endIndex = len( self.storageLog )
		for index in xrange( startIndex, endIndex ):
			playerBase.client.tong_receiveStorageLog( self.storageLog[ index ] )


	def enterStorage( self, playerDBID ):
		"""
		Define method.
		�������򿪲ֿ⣬�Ѳֿ���Ʒ������ҿͻ���

		@param playerDBID : ��ҵ�databaseID
		@type playerDBID : DATABASE_ID
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return
		fetchRecord = self.getTodayStorageFetchRecord( playerDBID )
		playerBase.client.tong_enterStorage( self.storageBagPopedom, fetchRecord )


	def _getStorageBagItems( self, bagID ):
		"""
		ȡ�òֿ����Ʒ
		@return: [itemInstance, ...]
		"""
		# Ŀǰ���140������Ҫ��������
		#return self.storage.getDatas()
		return self.storage.getDatasByRange( bagID * csdefine.KB_MAX_SPACE, bagID * csdefine.KB_MAX_SPACE + csdefine.KB_MAX_SPACE - 1 )


	def requestStorageItem( self, playerDBID, count ):
		"""
		Define method.
		����ֿ�����

		@param playerDBID : ��������dbid
		@type playerDBID : DATABASE_ID
		@param count : ����0,1,2...
		@type count : UINT8
		"""
		#storageOrderCount = csconst.TONG_WAREHOUSE_LIMIT[ self.ck_level ]
		#if count * 30 >= storageOrderCount:
		#	ERROR_MSG( "request items:out of storage's space!" )
		#	return
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return

		if count % 2 == 0:
			startOrder = count / 2 * 255
		else:
			startOrder = count / 2 * 255 + 40
		endOrder = startOrder + 40	# һ����෢40��

		items = self.storage.getDatasByRange( startOrder, endOrder )
		playerBase.client.tong_receiveStorageItem( items )


	def storeItem2Order( self, srcOrder, srcItem, dstOrder, playerDBID ):
		"""
		Define method.
		�洢��Ʒ�����ֿ�ָ����Ʒ��

		@param srcOrder : ��Ʒ�ڱ����е�order
		@type srcOrder : INT16
		@param srcItem : ��Ʒʵ��
		@type srcItem : ITEM
		@param dstOrder : ��Ʒ�ڲֿ��е�order
		@type dstOrder : INT16
		@param playerDBID : ���databaseID
		@type playerDBID : DATABASE_ID
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return

		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE

		if self.isStorageFrozen():
			DEBUG_MSG( "The storage has been Frozen.-------->>>" )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return

		bagID = dstOrder / csdefine.KB_MAX_SPACE
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID ��������,�������:%s,bagID:%i." % ( self.playerName, bagID ) )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return

		quality = srcItem.getQuality()
		if self.storageBagPopedom[bagID]["qualityLowerLimit"] > quality:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_QUALITY_LOWER )
			return

		if self.storageBagPopedom[bagID]["qualityUpLimit"] < quality:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_QUALITY_HIGHER )
			return

		if not self._addItem2Order( srcOrder, dstOrder, srcItem, playerBase ):	# ���ʧ��
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return
		self.addStorageLog( playerDBID, csdefine.TONG_STORAGE_OPERATION_ADD, srcItem, bagID, time.time() )

	def _addItem2Order( self, srcOrder, dstOrder, srcItem, playerBase ):
		"""
		��һ����Ʒ�ŵ�ָ�������ĸ����У���storeItem2Order����
		�ɹ��򷵻�True�����򷵻�False

		@param srcOrder : ��Ʒ�ڱ����е�order
		@type srcOrder : INT16
		@param srcItem : ��Ʒʵ��
		@type srcItem : ITEM
		@param dstOrder : ��Ʒ�ڲֿ��е�order
		@type dstOrder : INT16
		@param playerBase : ���baseMailbox
		@type playerBase : MAILBOX
		"""
		if self.storage.add( dstOrder, srcItem ):
			playerBase.cell.tong_storeItemSuccess01( srcOrder )
			playerBase.client.tong_storeItemUpdate( srcItem )
			return True

		dstItem = self.storage.getByOrder( dstOrder )
		if dstItem.isFrozen():
			WARNING_MSG( "������������" )
			return False

		if srcItem.getStackable() > 1 and dstItem.id == srcItem.id:	# �ɵ��ӵ������⴦��
			overlapAmount = srcItem.getStackable()
			dstAmount = dstItem.getAmount()
			srcAmount = srcItem.getAmount()
			storeAmount = min( overlapAmount - dstAmount, srcAmount )
			# �����Զ�֪ͨ�ͻ��ˣ��ֶ�֪ͨ
			dstItem.setAmount( dstAmount + storeAmount )
			playerBase.client.tong_storeItemUpdate( dstItem )
			srcAmount = srcAmount - storeAmount
			if srcAmount:	# ��Ŀ��λ�õ��Ӻ���ʣ�࣬�Żر���
				srcItem.setAmount( srcAmount )
				playerBase.client.tong_storeItemUpdate( srcItem )
				playerBase.cell.tong_storeItemSuccess02( srcOrder, srcItem )
				return True
			playerBase.cell.tong_storeItemSuccess01( srcOrder )			# û��ʣ��
			return True

		else:	# ���Ŀ��λ���� id��ͬ�Ĳ��ɵ�����Ʒ �� id��ͬ�Ŀɵ�����Ʒ�����ǽ�������
			playerBase.cell.tong_storeItemSuccess02( srcOrder, dstItem )
			if self.storage.removeByOrder( dstOrder ):
				if self.storage.add( dstOrder, srcItem ):	# �Ѵӱ����Ǳ�����ֿ����Ʒ���뵽�ֿ���Ʒ��
					playerBase.client.tong_storeItemUpdate( srcItem )
					return True
		return False


	def storeItem2Bag( self, srcOrder, item, bagID, playerDBID ):
		"""
		Define method.
		�����ֿ���洢��Ʒ�Ľӿڣ���ָ���˰���λ

		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param item:		�����ֿ���洢����Ʒ
		type item:		ITEM
		param bagID:���ֿ����λ��
		type bagID:UINT8
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return
		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID ��������,�������:%s,bagID:%i." % ( self.playerName, bagID ) )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return

		if self.isStorageFrozen():
			DEBUG_MSG( "The storage has been Frozen.-------->>>" )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return

		quality = item.getQuality()
		if self.storageBagPopedom[bagID]["qualityLowerLimit"] > quality:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_QUALITY_LOWER )
			return

		if self.storageBagPopedom[bagID]["qualityUpLimit"] < quality:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_QUALITY_HIGHER )
			return

		if item.getStackable() > 1:							# ����ǿɵ�����Ʒ
			if self._stackableInStorageBag( item, bagID, playerBase ):	# ���ӳɹ�
				playerBase.cell.tong_storeItemSuccess01( srcOrder )
			else:
				order = self._findBagFreeOrder( bagID )
				if order == -1:
					playerBase.cell.tong_unfreezeBag( kitbagNum )
					return
				if self.storage.add( order, item ):
					playerBase.client.tong_storeItemUpdate( item )
					playerBase.cell.tong_storeItemSuccess01( srcOrder )
					playerBase.cell.tong_unfreezeBag( kitbagNum )
		else:	# ������ǿɵ�����Ʒ
			order = self._findBagFreeOrder( bagID )
			if order == -1:
				playerBase.cell.tong_unfreezeBag( kitbagNum )
				return
			if self.storage.add( order, item ):
				playerBase.client.tong_storeItemUpdate( item )
				playerBase.cell.tong_storeItemSuccess01( srcOrder )
				playerBase.cell.tong_unfreezeBag( kitbagNum )
		self.addStorageLog( playerDBID, csdefine.TONG_STORAGE_OPERATION_ADD, item, bagID, time.time() )


	def storeItem2Storage( self, srcOrder, item, playerDBID ):
		"""
		Define method.
		�洢��Ʒ���ֿ�,����:����Ҽ�����

		@param srcOrder : ��Ʒ�ڱ����е�order
		@type srcOrder : INT16
		@param item : ��Ʒʵ��
		@type item : ITEM
		@param playerDBID : ���databaseID
		@type playerDBID : DATABASE_ID
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return
		kitbagNum = srcOrder / csdefine.KB_MAX_SPACE

		if self.isStorageFrozen():
			DEBUG_MSG( "The storage has been Frozen.-------->>>" )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return

		dstOrder = self._findFreeOrder()
		if dstOrder == -1:
			#playerBase,֪ͨ��û�п�λ�ˡ�
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return

		bagID = dstOrder / csdefine.KB_MAX_SPACE
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID ��������,�������:%s,bagID:%i." % ( self.playerName, bagID ) )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			return

		quality = item.getQuality()
		if self.storageBagPopedom[bagID]["qualityLowerLimit"] > quality:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_QUALITY_LOWER )
			return

		if self.storageBagPopedom[bagID]["qualityUpLimit"] < quality:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_QUALITY_HIGHER )
			return

		def storeItem():
			# ���Ұ��ֿ���Ŀ�λ
			orderID = self._findFreeOrder()
			if orderID != -1:	# ����п�λ
				if self.storage.add( orderID, item ):
					playerBase.cell.tong_storeItemSuccess01( srcOrder )
					playerBase.client.tong_storeItemUpdate( item )
					return
			else:	# ��Ʒ�洢ʧ��
				playerBase.cell.tong_unfreezeBag( kitbagNum )
				return

		if item.getStackable() > 1:					# ����ǿɵ�����Ʒ
			if self._stackableInStorage( item, playerBase ):	# ���Ҳֿ����ͬ��ɵ�����Ʒ ����
				playerBase.cell.tong_storeItemSuccess01( srcOrder )
			else:
				storeItem()
		else:		# ������ǿɵ�����Ʒ
			storeItem()
		self.addStorageLog( playerDBID, csdefine.TONG_STORAGE_OPERATION_ADD, item, bagID, time.time() )


	def fetchItem2Order( self, srcOrder, dstOrder, playerDBID ):
		"""
		Define method.
		�Ӳֿ�ȡ����Ʒ������

		@param srcOrder : ��Ʒ�ڲֿ��е�order
		@type srcOrder : INT16
		@param dstOrder : ��Ʒ����ұ�����order
		@type dstOrder : INT16
		@param playerDBID : ���databaseID
		@type playerDBID : DATABASE_ID
		"""
		kitbagNum = dstOrder / csdefine.KB_MAX_SPACE
		item = self.storage.getByOrder( srcOrder )
		self._fetchItem( kitbagNum, srcOrder, dstOrder, item.getAmount(), playerDBID )

	def fetchItem2Kitbags( self, kitbagNum, srcOrder, playerDBID ):
		"""
		Define method.
		�Ӱ��ֿ���ȡ����Ʒ�Ľӿڣ���ָ������λ��Ŀ����ӣ��ڱ�������ҵ�һ����λ

		@param srcOrder : ��Ʒ�ڱ����е�order
		@type srcOrder : INT16
		@param playerDBID : ���databaseID
		@type playerDBID : DATABASE_ID
		"""
		item = self.storage.getByOrder( srcOrder )
		self._fetchItem( kitbagNum, srcOrder, 0, item.getAmount(), playerDBID )

	def fetchSplitItem2Kitbags( self, kitbagNum, srcOrder, amount, playerDBID ):
		"""
		Define method.
		�Ӱ��ֿ���ȡ����Ʒ�Ľӿڣ���ָ������λ��Ŀ����ӣ��ڱ�������ҵ�һ����λ

		@param srcOrder : ��Ʒ�ڲֿ��е�order
		@type srcOrder : INT16
		@param playerDBID : ���databaseID
		@param amount : ��ȡ��Ʒ����
		@param amount : INT16
		@type playerDBID : DATABASE_ID
		"""
		self._fetchItem( kitbagNum, srcOrder, 0, amount, playerDBID )
		
	def _fetchItem( self, kitbagNum, srcOrder, dstOrder, amount, playerDBID ):
		"""
		Define method.
		�Ӱ��ֿ���ȡ����Ʒ�Ľӿڣ���ָ������λ��Ŀ����ӣ��ڱ�������ҵ�һ����λ

		@param srcOrder : ��Ʒ�ڲֿ��е�order
		@type srcOrder : INT16
		@param dstOrder : ��Ʒ����ұ�����order
		@type dstOrder : INT16
		@param playerDBID : ���databaseID
		@param amount : ��ȡ��Ʒ����
		@param amount : INT16
		@type playerDBID : DATABASE_ID
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return
		
		# �жϵ�ǰ��Ʒ�Ƿ����
		item = self.storage.getByOrder( srcOrder )
		if item is None:
			HACK_MSG( "��Ʒ�����ڡ�" )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			playerBase.client.tong_delItemUpdate( srcOrder )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_ITEM_NOT_EXIST )
			return
			
		# �жϲֿ��Ƿ�����	
		if self.isStorageFrozen():
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_ISCHANGE )
			return
		
		# �жϵ�ǰ��Ʒ�Ƿ�����
		if item.isFrozen():
			WARNING_MSG( "��Ʒ������" )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_ISCHANGE )
			return
		
		# �ж���ȡorder����Ч��	
		bagID = srcOrder / csdefine.KB_MAX_SPACE
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID ��������,�������:%s,bagID:%i." % ( self.playerName, bagID ) )
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_BAGID_ERROR )
			return
			
		# ��ǰְλÿ����ȡ������Ʒ
		fetchNum = self.getFetchNumByOfficialPos( bagID, menberInfo.getGrade() )	
		if fetchNum == 0:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_NOT_PURVIEW )
			return
		
		# �жϵ�����ȡ�Ƿ��Ѿ����ڵ�ǰְλ����ȡ��
		todayFetchNum = self.getTodayFetchNum( bagID, playerDBID )
		if amount > fetchNum - todayFetchNum:
			playerBase.cell.tong_unfreezeBag( kitbagNum )
			self.storageStatusMessage( playerBase, csstatus.TONG_STORAGE_NOT_FETCH_MORE )
			return
		
		tempItem = item.copy()
		tempItem.setAmount( amount )
		item.freeze()
		if dstOrder == 0 or dstOrder == None:
			itemAmount = item.getAmount()
			if itemAmount <= amount:
				playerBase.cell.tong_fetchItem2KitbagsCB( srcOrder, tempItem )
			else:
				playerBase.cell.tong_fetchSplitItem2KitbagsCB( srcOrder, tempItem )
		else:
			playerBase.cell.tong_fetchItem2OrderCB( dstOrder, tempItem, srcOrder )

	def moveStorageItem( self, srcOrder, dstOrder, playerDBID ):
		"""
		Define method.
		��ͬһ���������ƶ���Ʒ�Ľӿ�

		@param srcOrder : ��Ʒ�ڱ����е�order
		@type srcOrder : INT16
		@param dstOrder : ��Ʒ�ڲֿ��е�order
		@type dstOrder : INT16
		@param playerDBID : ���databaseID
		@type playerDBID : DATABASE_ID
		"""
 		if srcOrder == dstOrder:
 			return

		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		if not playerBase:
			return

		# ���Ȩ��
		if not self.checkMemberDutyRights( menberInfo.getGrade() , csdefine.TONG_RIGHT_STORAGE_MANAGE ):
			DEBUG_MSG( "------>>>Ȩ�޲���."  )
			return

		srcItem = self.storage.getByOrder( srcOrder )
		if srcItem is None:
			WARNING_MSG( "error code: ", csstatus.CIB_MSG_ITEM_NOT_EXIST )
			return

		if srcItem.isFrozen():
			return

		if not self.storage.orderHasItem( dstOrder ):	# Ŀ����ӿ�
			if self.storage.swapOrder( srcOrder, dstOrder ):
				playerBase.client.tong_moveItemCB( srcOrder, dstOrder )
				return
			else:	# ���ɿ�ԭ��
				return

		dstItem = self.storage.getByOrder( dstOrder )
		if dstItem.isFrozen():
			return

		if srcItem.getStackable() <= 1 or dstItem.id != srcItem.id:	# �ɵ��ӵ��ߴ���
			if self.storage.swapOrder( srcOrder, dstOrder ):
				playerBase.client.tong_moveItemCB( srcOrder, dstOrder )
		else:	# ���Ŀ��λ���� id��ͬ�Ĳ��ɵ�����Ʒ �� id��ͬ�Ŀɵ�����Ʒ�����ǽ�������
			overlapAmount = srcItem.getStackable()
			dstAmount = dstItem.getAmount()
			srcAmount = srcItem.getAmount()
			storeAmount = min( overlapAmount - dstAmount, srcAmount )
			dstItem.setAmount( dstAmount + storeAmount )
			playerBase.client.tong_storeItemUpdate( dstItem )
			srcAmount = srcAmount - storeAmount
			if srcAmount:	# ��Ŀ��λ�õ��Ӻ���ʣ�࣬�Ż�Դλ��
				srcItem.setAmount( srcAmount )
				playerBase.client.tong_storeItemUpdate( srcItem )
				return
			if self.storage.removeByOrder( srcOrder ):	# ��ʣ�࣬ɾ��Դ��Ʒ
				playerBase.client.tong_delItemUpdate( srcOrder )

	def storageStatusMessage( self, targetBaseMailbox, statusID, *args ) :
		"""
		send status message
		@type			statusID : INT32
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		if args == ():
			tempArgs = ""
		else:
			tempArgs = str( args )
		#args = args == () and "" or str( args )
		targetBaseMailbox.client.onStatusMessage( statusID, tempArgs )


	def fetchItemSuccess01( self, dstOrder, playerDBID ):
		"""
		Define method.
		ȡ��һ����Ʒ�ɹ��� base������ɾ����Ʒ

		@param dstOrder : ��Ʒ�ڲֿ��е�order
		@type dstOrder : INT16
		@param playerDBID : ���databaseID
		@type playerDBID : DATABASE_ID
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		self.unFreezeStorage()
		item = self.storage.getByOrder( dstOrder )
		itemAmount = item.getAmount()
		self.storage.removeByOrder( dstOrder )
		bagID = dstOrder / csdefine.KB_MAX_SPACE
		self.addStorageLog( playerDBID, csdefine.TONG_STORAGE_OPERATION_MINUS, item, bagID, time.time() )
		self._fetchItemSuccess( playerDBID, bagID, itemAmount )
		playerBase = menberInfo.getBaseMailbox()
		if playerBase:
			playerBase.client.tong_fetchStorageItemCB( itemAmount )
			playerBase.client.tong_delItemUpdate( dstOrder )


	def fetchItemSuccess02( self, dstOrder, item, playerDBID ):
		"""
		Define method.
		�����Ӱ��ֿ�ȡһ����Ʒ�Ļص���
		�����е���һ����Ʒ��ʣ�࣬����ֿ��뱳��Ŀ����ӽ�����Ʒ���� ʣ����Ʒ �� ��������Ʒ �Żذ��ֿ�

		@param dstOrder : ��Ʒ�ڲֿ��е�order
		@type dstOrder : INT16
		@param item : ��Ʒ
		@type item : ITEM
		@param playerDBID : ���databaseID
		@type playerDBID : DATABASE_ID
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		playerBase = menberInfo.getBaseMailbox()
		self.unFreezeStorage()
		srcItem = self.storage.getByOrder( dstOrder )
		itemAmount = srcItem.getAmount()
		self.storage.removeByOrder( dstOrder )
		bagID = dstOrder / csdefine.KB_MAX_SPACE
		self.addStorageLog( playerDBID, csdefine.TONG_STORAGE_OPERATION_MINUS, srcItem, bagID, time.time() )
		self._fetchItemSuccess( playerDBID, bagID, itemAmount )
		if self.storage.add( dstOrder, item ):
			self.addStorageLog( playerDBID, csdefine.TONG_STORAGE_OPERATION_ADD, item, bagID, time.time() )
			if playerBase:
				playerBase.client.tong_storeItemUpdate( item )


	def fetchItemSuccess03( self, dstOrder, amount, playerDBID ):
		"""
		Define method.
		ȡ��һ����Ʒ�ɹ��� base������ɾ����Ʒ

		@param dstOrder : ��Ʒ�ڲֿ��е�order
		@type dstOrder : INT16
		@param playerDBID : ���databaseID
		@type playerDBID : DATABASE_ID
		"""
		menberInfo = self.getMemberInfos( playerDBID )
		self.unFreezeStorage()
		item = self.storage.getByOrder( dstOrder )
		itemAmount = item.getAmount()
		
		item.setAmount( itemAmount - amount )
		item.unfreeze()
			
		bagID = dstOrder / csdefine.KB_MAX_SPACE
		self.addStorageLog( playerDBID, csdefine.TONG_STORAGE_OPERATION_MINUS, item, bagID, time.time() )
		self._fetchItemSuccess( playerDBID, bagID, amount )
		playerBase = menberInfo.getBaseMailbox()
		if playerBase:
			playerBase.client.tong_fetchStorageItemCB( amount )
			playerBase.client.tong_storeItemUpdate( item )
				
	def _stackableInStorage( self, itemInstance, playerBase ):
		"""
		�ڲֿ��ж�һ���ɵ�����Ʒ���Ӳ���

		@param itemInstance:�̳���CItemBase���Զ������ʵ��
		@type  itemInstance:CItemBase
		@param playerBase : ���baseMailbox
		@type playerBase : MAILBOX
		@return:	�ɹ��򷵻�Trueʧ���򷵻�False
		@rtype:		BOOL
		"""
		currtotal = 0
		stackable = itemInstance.getStackable()
		r = self._findAllItemFromStorage( itemInstance.id, itemInstance.isBinded() )
		if r == []:return False
		#�������
		for e in r:									# e like as ( kitOrder, orderID, itemData )
			# like as: c += a < b ? a : b�����������ԭ���Ǳ������ʱ�ֶ����ö���stackable��������Ʒ�����жϴ���
			currtotal += e.getAmount() < stackable and e.getAmount() or stackable
		val = len( r ) * stackable - currtotal		# ��ȡ�����Ե��ӵ�����
		val1 = itemInstance.getAmount()				# ��ȡ�����Ʒ������
		if val < val1:	return False
		for e in r:
			if val1 <= 0:break
			amount = stackable - e.getAmount()
			if amount > 0:
				if amount > val1:
					e.setAmount( e.getAmount() + val1 )
					playerBase.client.tong_storeItemUpdate( e )
					return True
				else:
					e.setAmount( stackable )
					playerBase.client.tong_storeItemUpdate( e )
					val1 -= amount
		return True


	def _findAllItemFromStorage( self, itemKeyName, isBinded ):
		"""
		��������ͨ�������ҵ�������itemKeyName��ͬ����Ʒ

		@param itemKeyName: ��ʾÿһ����ߵ�Ψһ�ĵ�������
		@type  itemKeyName: STRING
		@return:	array of tuple as (kitOrder, orderID, itemData)
		@rtype:		array of tuple
		"""
		itemList = []
		for item in self.storage.getDatas():
			if item.id == itemKeyName and item.isBinded() == isBinded:
				itemList.append( item )
		return itemList


	def checkFetchStatus( self, playerDBID ):
		"""
		��ѯ��ҵ�ȡ��Ʒ״̬

		@param playerDBID : ��ҵ�dbid
		@type playerDBID : DATABASE_ID

		��ѯ�Ľ���п�����:
		1,�����Ѳ�����ȡ��Ʒ
		2,û��ȡ��Ʒ��Ȩ��
		3,����ȡ��Ʒ
		"""
		pass

	def isStorageExtend( self ):
		"""
		�ֿ��Ƿ���Ϊ������չ�ռ�
		"""
		if self.ck_level in EXTEND_LEVEL_LIST:
			return True
		return False

	def isStorageReduce( self ):
		"""
		�ֿ��Ƿ���Ϊ�������ٿռ�
		"""
		if self.ck_level in REDUCE_LEVEL_LIST:
			return True
		return False

	def onStorageUpgrade( self ):
		"""
		�ֿ�����
		"""
		if not self.isStorageExtend():
			return

		# ���г�Ա��Ĭ��Ȩ��Ϊ��ȡ���޶����Ʒ
		gradeFetchItemLimit = { csdefine.TONG_DUTY_MEMBER	:	0,
								csdefine.TONG_DUTY_TONG	:	0,
								csdefine.TONG_DUTY_DEPUTY_CHIEF	:	0,
								csdefine.TONG_DUTY_CHIEF	:	DAY_FETCH_ITEM_LIMIT,
								}

		tongStoragePopedom = { "bagID":len( self.storageBagPopedom ),	# �ֿ��������¼Ӱ���id�պ�Ϊlen( self.storageBagPopedom )
								"bagName":"",
								"qualityUpLimit":ItemTypeEnum.CQT_GREEN,
								"qualityLowerLimit":ItemTypeEnum.CQT_WHITE,
								"fetchItemLimit":gradeFetchItemLimit,
								}

		self.storageBagPopedom.append( tongStoragePopedom )


	def onStorageDegrade( self ):
		"""
		�ֿ⽵��
		"""
		if not self.isStorageReduce():
			return
		self.storageBagPopedom.pop()	# ��ʱ�������Ųֿ���Ʒ.


	def renameStorageBag( self, bagID, newName, playerDBID ):
		"""
		Define method.
		�ı����������

		@param bagID : ���ֿ������id
		@type bagID : UINT8
		@param newName : ������
		@type newName : STRING
		@param playerDBID : ���dbid
		@type playerDBID : DATABASE_ID
		"""
		# �������
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID ��������,�������:%s,bagID:%i." % ( self.playerName, bagID ) )
			return
		menberInfo = self.getMemberInfos( playerDBID )
		if not self.checkMemberDutyRights( menberInfo.getGrade() , csdefine.TONG_RIGHT_STORAGE_MANAGE ):
			DEBUG_MSG( "------>>>Ȩ�޲���."  )
			return

		if newName == self.storageBagPopedom[ bagID ]["bagName"]:
			return

		self.storageBagPopedom[ bagID ]["bagName"] = newName

		playerBase = menberInfo.getBaseMailbox()
		if playerBase:	# ��֪ͨ�����ߵĿͻ���
			playerBase.client.tong_updateStorageBagName( bagID, newName )


	def changeStorageQualityUp( self, bagID, quality, playerDBID ):
		"""
		Define method.
		�ı���ֿ������Ʒ��������

		@param bagID : ���ֿ������id
		@type bagID : UINT8
		@param quality : ����
		@type quality : UINT8
		@param playerDBID : ���dbid
		@type playerDBID : DATABASE_ID
		"""
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID ��������,�������:%s,bagID:%i." % ( self.playerName, bagID ) )
			return
		if quality not in ITEM_QUALITYS:
			DEBUG_MSG( "----->>>quality:%i ������." % quality )
			return
		menberInfo = self.getMemberInfos( playerDBID )
		if not self.checkMemberDutyRights( menberInfo.getGrade() , csdefine.TONG_RIGHT_STORAGE_MANAGE ):
			DEBUG_MSG( "------>>>Ȩ�޲���."  )
			return
		self.setBagUpQuality( bagID, quality )


	def changeStorageQualityLower( self, bagID, quality, playerDBID ):
		"""
		Define method.
		�ı���ֿ������Ʒ��������

		@param bagID : ���ֿ������id
		@type bagID : UINT8
		@param quality : ����
		@type quality : UINT8
		@param playerDBID : ���dbid
		@type playerDBID : DATABASE_ID
		"""
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID ��������,�������:%s,bagID:%i." % ( self.playerName, bagID ) )
			return
		if quality not in ITEM_QUALITYS:
			DEBUG_MSG( "------->>>quality:%i ������." % quality )
			return
		menberInfo = self.getMemberInfos( playerDBID )
		if not self.checkMemberDutyRights( menberInfo.getGrade() , csdefine.TONG_RIGHT_STORAGE_MANAGE ):
			DEBUG_MSG( "------>>>Ȩ�޲���."  )
			return

		self.setBagLowerQuality( bagID, quality )


	def setBagLowerQuality( self, bagID, quality ):
		"""
		���ð�������ƷƷ������

		@param bagID : ���ֿ������id
		@type bagID : UINT8
		@param quality : ����
		@type quality : UINT8
		"""
		self.storageBagPopedom[bagID]["qualityLowerLimit"] = quality


	def setBagUpQuality( self, bagID, quality ):
		"""
		���ð�������ƷƷ������

		@param bagID : ���ֿ������id
		@type bagID : UINT8
		@param quality : ����
		@type quality : UINT8
		"""
		self.storageBagPopedom[bagID]["qualityUpLimit"] = quality


	def getBagLimitByID( self, bagID ):
		"""
		����bagID��ô˰����Ķ�������
		"""
		return self.storageBagPopedom[ bagID ]


	def isStorageBagID( self, bagID ):
		"""
		��֤bagID�Ƿ�Ϸ�
		"""
		return bagID < len( self.storageBagPopedom )


	def changeStorageBagLimit( self, bagID, job, limitCount, playerDBID ):
		"""
		Define method.
		�ı������ְλʹ��Ȩ��

		@param bagID : ���ֿ������id
		@type bagID : UINT8
		"""
		if not self.isStorageBagID( bagID ):
			HACK_MSG( "bagID ��������,�������:%s,bagID:%i." % ( self.playerName, bagID ) )
			return

		if job == csdefine.TONG_DUTY_CHIEF:
			# ���ܸı������Ȩ��
			return

		menberInfo = self.getMemberInfos( playerDBID )
		if not self.checkMemberDutyRights( menberInfo.getGrade() , csdefine.TONG_RIGHT_STORAGE_MANAGE ):
			DEBUG_MSG( "------>>>Ȩ�޲���."  )
			return

		bagLimit = self.getBagLimitByID( bagID )
		bagLimit[ "fetchItemLimit" ][job] = limitCount
		# ����Ҫ���µ��ͻ���


	def getFetchNumByOfficialPos( self, bagID, grade ):
		"""
		����ְλ���ȡ��Ʒ��Ȩ��
		"""
		return self.storageBagPopedom[bagID]["fetchItemLimit"][grade]


	def getTodayStorageFetchRecord( self, playerDBID ):
		"""
		�����ҽ����ڰ��ֿ��е�ȡ��Ʒ��¼
		"""
		playerFetchRecord = {}
		if playerDBID in self.playerFetchRecord:
			playerFetchRecord = self.playerFetchRecord[playerDBID]
		else:
			self.playerFetchRecord[playerDBID] = {}
		return playerFetchRecord


	def getTodayFetchNum( self, bagID, playerDBID ):
		"""
		�������dbid�����ҽ�����bagID�İ������Ѿ�ȡ������Ʒ����
		"""
		num = 0
		if playerDBID in self.playerFetchRecord:
			if bagID in self.playerFetchRecord[playerDBID]:
				num = self.playerFetchRecord[playerDBID][bagID]
			else:
				self.playerFetchRecord[playerDBID][bagID] = 0
		else:	# ������컹ûȡ��,��ô�����¼
			self.playerFetchRecord[playerDBID] = {}
			self.playerFetchRecord[playerDBID][bagID] = 0

		return num


	def _fetchItemSuccess( self, playerDBID, bagID, amount ):
		"""
		ȡ��Ʒ�ɹ���Ĵ���
		����:������ҽ����ȡ��Ʒ����

		@param playerDBID : ���dbid
		@type playerDBID : DATABASE_ID
		@param amount : ��Ʒ����
		@type amount : INT32
		"""
		if playerDBID in self.playerFetchRecord:
			if bagID in self.playerFetchRecord[playerDBID]:
				self.playerFetchRecord[playerDBID][bagID] += amount
			else:
				self.playerFetchRecord[playerDBID][bagID] = amount
		else:
			self.playerFetchRecord[ playerDBID ] = {}
			self.playerFetchRecord[ playerDBID ][bagID] = amount


	def _stackableInStorageBag( self, itemInstance, bagID, playerBase ):
		"""
		�ڰ����ж�һ���ɵ�����Ʒ���Ӳ���
		"""
		currtotal = 0
		stackable = itemInstance.getStackable()
		r = []
		for item in self._getStorageBagItems( bagID ):
			if item.id == itemInstance.id and item.isBinded() == itemInstance.isBinded():
				r.append( item )
		if len( r ) == 0: return False
		#�������
		for item in r:
			# like as: c += a < b ? a : b�����������ԭ���Ǳ������ʱ�ֶ����ö���stackable��������Ʒ�����жϴ���
			currtotal += item.getAmount() < stackable and item.getAmount() or stackable
		val = len( r ) * stackable - currtotal		# ��ȡ�����Ե��ӵ�����
		val1 = itemInstance.getAmount()				# ��ȡ�����Ʒ������
		if val < val1:	return False
		for item in r:
			if val1 <= 0:break
			amount = stackable - item.getAmount()
			if amount > 0:
				if amount > val1:
					item.setAmount( item.getAmount() + val1 )
					playerBase.client.tong_storeItemUpdate( item )
					return True
				else:
					item.setAmount( stackable )
					playerBase.client.tong_storeItemUpdate( item )
					val1 -= amount
		return True


	def resetStorageLimit( self ):
		"""
		������ҵ�ȡ��Ʒ��¼
		"""
		self.playerFetchRecord = {}
		self.resetStorageLimitTime = time.time()	# ��¼��һ������ʱ��


	def onTimer( self, timerID, cbid ):
		"""
		timer:ÿ��0�����ð��ֿ��ȡ��Ʒ��������.
		"""
		if timerID == self.storage_resetLimitTimer:
			self.resetStorageLimit()
			self.storage_resetLimitTimer = self.addTimer( 24*60*60 )	# ������һ������timer


	def _storageCalcTime( self, point ):
		"""
		������point��ʱ������pointΪ[ 21, 40, 0 ]�� ������������һ��point������Ҫ��ʱ��
		@param point: [ Сʱ, ����, �� ]
		"""
		t = time.localtime()
		h = t[ 3 ]
		m = t[ 4 ]
		s = t[ 5 ]

		# ���¹���ģ���������
		second = point[ 2 ] - s
		if second < 0:
			second = point[ 2 ] + 60 - s
			point[ 1 ] -= 1
		minut = point[ 1 ] - m
		if minut < 0:
			minut = point[ 1 ] + 60 - m
			point[ 0 ] -= 1
		hour = point[ 0 ] - h
		if hour < 0:
			hour = point[ 0 ] + 24 - h

		return hour * 60 * 60 + minut * 60 + second

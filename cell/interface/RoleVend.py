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
		 	csdefine.ACTION_FORBID_TRADE | csdefine.ACTION_FORBID_ATTACK		# 不允许 移动、使用物品、装备、交易、攻击

SPECIALSHOP_ITEM_BUY_LEVEL = 30 #商城物品购买等级最低为30

class RoleVend:
	"""
	玩家摆摊系统
	"""
	def __init__( self ):
		"""
		"""
		# self.vendMerchandise		摆摊物品位置信息列表
		# self.vendSignboard		摊位名数据
		pass

	def _canVend( self ):
		"""
		判断自己是否能摆摊
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
		判断自己是否处于摆摊状态
		"""
		return self.getState() == csdefine.ENTITY_STATE_VEND


	def vend_vend( self, srcEntityID, kitUidList, uidList, priceList, petDatabaseIDList, petPriceList ):
		"""
		Exposed method.
		玩家摆摊的接口,检查玩家是否处于摆摊状态,设置摆摊物品数据，设置玩家在摆摊其间禁止其他相关行为的标志。

		param uidList: 玩家摆摊物品的uid列表
		type uidList: ARRAY OF INT64
		param priceList: 与摆摊物品对应的摆摊物品价格列表
		type priceList: ARRAY OF UINT32
		"""
		if srcEntityID != self.id:
			HACK_MSG( "非法调用者." )
			return

		if self.level < 15: #增加角色摆摊的等级限制（15级以上）
			self.statusMessage( csstatus.VEND_LEVEL_NOT_ENOUGH )
			return

		if self._isVend():
			HACK_MSG( "玩家已经在摆摊了。" )
			return

		if self.getState() == csdefine.ENTITY_STATE_DEAD:		# 判断角色是否已经死亡
			self.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
			return

		canVendStatus = self._canVend()
		if canVendStatus != csstatus.VEND_NO_PROBLEM:			# 判断是否处于摆摊允许区域内
			self.statusMessage( canVendStatus )
			HACK_MSG( "玩家处于不允许摆摊状态。" )
			return

		# 如果摆摊卖物品、摆摊卖宠物 没有成功
		if not self.vend_itemVend( kitUidList, uidList, priceList ) or not self.vend_petVend( petDatabaseIDList, petPriceList ):
			return

		actPet = self.pcg_getActPet()
		if actPet :
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )

		# 如果允许摆摊则设置玩家的状态actWord,在client/Role.py的set_actWord接口中还需设置相应的摆摊处理wsf
		self.changeState( csdefine.ENTITY_STATE_VEND )	# 设置摆摊状态
		try:
			g_logger.roleVendLog( self.databaseID, self.getName() )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

#	def vend_pauseVend( self, srcEntityID ):
#		"""
#		Exposed method.
#		玩家暂停摆摊的接口
#		"""
#		if srcEntityID != self.id:
#			HACK_MSG( "非法调用者." )
#			return
#		self.vendMerchandise = []
#		self.setTemp( "isPauseVend", 1 ) #设置暂停摆摊标记
#		self.client.vend_isPauseVend( self.queryTemp( "isPauseVend" ) )


	def vend_itemVend( self, kitUidList, uidList, priceList ):
		"""
		摆摊卖物品
		"""
		if len( kitUidList ) != len( uidList ) or len( kitUidList ) != len( priceList ):
			HACK_MSG( "摆摊物品位置参数长度不对。" )
			return False

		if len( kitUidList ) > csconst.VEND_ITEM_MAX_COUNT:
			HACK_MSG( "加入摆摊的物品数量超出上限." )
			return False
		for kitUid, uid, price in zip( kitUidList, uidList, priceList ):
			if kitUid == csdefine.KB_EQUIP_ID:
				HACK_MSG( "装备栏物品不能用于摆摊。" )
				return False
			tempItem = self.getItemByUid_( uid )
			if tempItem is None:
				ERROR_MSG( "%s(%i): 物品不存在( kitUid = %i, uid = %i )" % ( self.playerName, self.id, kitUid, uid ) )
				self.vendMerchandise = []
				return False

			if not self.canGiveItem( tempItem.id ):	# 特定物品等级限制不能摆摊
				ERROR_MSG( "%s(%i): item( id = %s )等级限制不可摆摊." % (self.playerName, self.id, tempItem.id) )
				self.statusMessage( csstatus.TISHOU_FORBID_CANNOT_GIVE_ITEM, csconst.SPECIFIC_ITEM_GIVE_LEVEL )
				self.vendMerchandise = []
				return False

			if not tempItem.canGive():	# 不能卖的不可以用于摆摊
				ERROR_MSG( "%s(%i): item( id = %s )不可出售." % (self.playerName, self.id, tempItem.id) )
				self.vendMerchandise = []
				return False
			if not tempItem.canExchange():	# 不可玩家间交易的不能卖 by姜毅
				self.statusMessage( csstatus.ROLE_TRADE_ITEM_NOT_TRADE )
				return False
			if price > csconst.ROLE_MONEY_UPPER_LIMIT:
				HACK_MSG( "设置的摆摊物品价格过高。" )
				return False
			self.vendMerchandise.append( { "kitUid":kitUid, "uid":uid, "price":price } )	# 把摆摊物品信息加入vendMerchandise

		for kitUid, uid, price in zip( kitUidList, uidList, priceList ):
			item = self.getItemByUid_( uid )
			item.freeze( self )				# 摆摊成功，冻结被用于摆摊的物品

		return True

	def vend_petVend( self, petDatabaseIDList, petPriceList ):
		"""
		摆摊卖宠物
		"""
		if len( petDatabaseIDList ) != len( petPriceList ):
			HACK_MSG( "摆摊宠物的位置参数长度不对。" )
			return False

		if len( petDatabaseIDList ) > csconst.VEND_PET_MAX_COUNT:
			HACK_MSG( "加入摆摊的宠物数量超出上限." )
			return False

		# 判断所有待出售宠物是否符合条件
		for petDatabaseID, price in zip( petDatabaseIDList, petPriceList ):
			if not self.pcg_petDict.has_key( petDatabaseID ):
				HACK_MSG( "错误的宠物databaseID。" )
				return
			if self.pcg_isPetBinded( petDatabaseID ):
				self.statusMessage( csstatus.PET_HAD_BEEN_BIND )
				return
			if price > csconst.ROLE_MONEY_UPPER_LIMIT:
				HACK_MSG( "设置的摆摊宠物价格过高。" )
				return False

		# 所有符合出售条件的宠物，上架出售
		for petDatabaseID, price in zip( petDatabaseIDList, petPriceList ):
			actPet = self.pcg_getActPet()
			if actPet and actPet.dbid == petDatabaseID :	# 如果要摆摊出售的宠物在出战中，则先回收
				actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )

			# to do宠物增加摆摊出售中标记，设置出售价格
			self.base.vend_petForSale( petDatabaseID, price )

			self.vendPetMerchandise.append( { "databaseID" : petDatabaseID, "price" :price } )	# 把摆摊物品信息加入vendPetMerchandise

		return True

	def vend_endVend( self, srcEntityID, isEnd ):
		"""
		Exposed method.
		玩家结束摆摊的接口
		isEnd				是否结束
		"""
		if srcEntityID != self.id:
			HACK_MSG( "非法调用者." )
			return

		for temp in self.vendMerchandise:
			kitUid = temp["kitUid"]
			uid = temp["uid"]
			item = self.getItemByUid_( uid )
			if item is None:
				ERROR_MSG( "找不到物品:kitUid(%i),uid(%i)" %( kitUid, uid ) )
				continue
			item.unfreeze( self )

		# 宠物下架，解除宠物的摆摊中标记
		for e in self.vendPetMerchandise:
			if not self.pcg_petDict.has_key( e["databaseID"] ):
				ERROR_MSG( "错误的宠物databaseID。" )
				continue
			self.base.vend_petEndForSale( e["databaseID"] )

		self.vendMerchandise = []
		self.vendPetMerchandise = []
#		self.vendSignboard = ""
		#self.actCounterDec( STATES )
		if self.getState() == csdefine.ENTITY_STATE_VEND:
			self.changeState( csdefine.ENTITY_STATE_FREE )	# 结束摆摊，改变玩家状态


	def vend_setSignboard( self, srcEntityID, signboard ):
		"""
		Exposed method.
		卖家设置摊位招牌的接口

		param signboard:欲设置的摊位名
		type signboard:	STRING
		"""
		if srcEntityID != self.id:
			HACK_MSG( "非法调用者." )
			return

		if not self._canVend():
			self.statusMessage( csstatus.VEND_FORBIDDEN_VEND )
			HACK_MSG( "玩家处于不允许摆摊状态。" )
			return

		if len( signboard ) > csconst.VEND_SIGNBOARD_MAX_LENGTH:
			HACK_MSG( "店名过长." )
			return

		if chatProfanity.searchMsgProfanity( signboard ) is not None:
			return

		self.vendSignboard = signboard

	def	vend_buyerQueryInfo( self, srcEntityID ):
		"""
		Exposed method.
		被买家client调用，买家查看卖家摊位数据
		"""
		if srcEntityID == self.id:
			HACK_MSG( "调用者不能是自己." )
			return

		if not self._isVend():
			HACK_MSG( "请求对象不在摆摊状态。" )
			return

		buyer = BigWorld.entities.get( srcEntityID )
		if buyer == None:
			HACK_MSG( "找不到玩家, srcEntityID: %i" % ( srcEntityID ) )
			return

		if self.position.flatDistTo( buyer.position ) > csconst.COMMUNICATE_DISTANCE:	# 暂时使用COMMUNICATE_DISTANCE
			buyer.statusMessage( csstatus.VEND_DISTANCE_TOO_FAR )
			DEBUG_MSG( "too far from vendor: %i. ( srcEntityID: %s )" % ( self.id, srcEntityID ) )
			return

		items = []
		for temp in self.vendMerchandise:			# 根据self.vendMerchandise获得摆摊物品数据，发送给买家
			kitUid = temp["kitUid"]
			uid = temp["uid"]
			item = self.getItemByUid_( uid )
			if item == None:
				ERROR_MSG( "摆摊物品数据出错。" )
				return
			item = item.copy()
			item.setPrice( temp["price"] )			# 设置价格
			items.append( item )

		buyer.clientEntity( self.id ).vend_receiveShopData( items )	# 发送摆摊物品数据给买家客户端
		self.base.vend_buyerQueryPetInfo( buyer.base, self.vendPetMerchandise )	# 给买方下发卖方宠物信息

		records = buyer.queryTemp( "vendRecord", [] )
		for record in records:
			buyer.clientEntity( self.id ).vend_receiveRecord( record )

	def vend_sell( self, srcEntityID, uid ):
		"""
		Exposed method.
		提供给买家的客户端调用，vendor卖一个物品的接口

		param kitUid:	买家欲买物品的kitUid
		type kitUid:	UINT8
		param uid:	买家欲买物品的uid
		type Uid:	INT64
		"""
		if srcEntityID == self.id:
			HACK_MSG( "调用者不能是自己." )
			return

		if not self._isVend():
			HACK_MSG( "卖家不在摆摊状态。" )
			return

		buyer = BigWorld.entities.get( srcEntityID )
		if buyer == None:
			HACK_MSG( "找不到玩家, srcEntityID: %i." % ( srcEntityID ) )
			return

		if not buyer.isReal():
			DEBUG_MSG( "目前仅允许real entity之间的摆摊交易。" )
			return

		# 判断是否在允许交易范围内
		if self.position.flatDistTo( buyer.position ) > csconst.COMMUNICATE_DISTANCE:	# 暂时使用COMMUNICATE_DISTANCE
			buyer.statusMessage( csstatus.VEND_DISTANCE_TOO_FAR )
			DEBUG_MSG( "too far from vendor: %s. ( srcEntityID: %s )" % ( self.getName(), srcEntityID ) )
			return

		if uid < 0:
			HACK_MSG( "uid(%i)参数不正确。" % ( uid ) )
			return

		if self.iskitbagsLocked():
			DEBUG_MSG( "卖家包裹上锁了。" )
			return

		temp = None
		for itemInfo in self.vendMerchandise:
			if itemInfo["uid"] == uid:
				temp = itemInfo
				break
		if temp is None:
			buyer.statusMessage( csstatus.VEND_ITEM_IS_NONE )
			HACK_MSG( "相应uid的物品不存在。" )
			buyer.clientEntity( self.id ).vend_removeItemNotify( uid )		# 更新buyer客户端数据
			return

		price = temp["price"]
		if buyer.money < price:
			buyer.statusMessage( csstatus.VEND_NOT_ENOUGH_MONEY )
			DEBUG_MSG( "买家钱不够买摆摊物品。" )
			return

		kitUid = temp["kitUid"]
		item = self.getItemByUid_( uid )			# 取得vendor背包中的物品
		if item == None:
			buyer.statusMessage( csstatus.VEND_ITEM_IS_NONE )
			HACK_MSG( "相应uid的物品不存在。" )
			index = self.vendMerchandise.index( temp )			# 删除相应的摆摊物品信息
			self.vendMerchandise.pop( index )
			buyer.clientEntity( self.id ).vend_removeItemNotify( uid )		# 更新buyer客户端数据
			return

		kitbagState = buyer.checkItemsPlaceIntoNK_( [item] )
		if kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			buyer.statusMessage( csstatus.VEND_KITBAG_FULL )
			DEBUG_MSG( "买家物品栏满。" )
			return
		elif kitbagState == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			buyer.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
			DEBUG_MSG( "买家某物品物品数量达到上限。" )
			return

		if item.id in self.getAllSpecialShopItemID() and buyer.level < SPECIALSHOP_ITEM_BUY_LEVEL : #
			buyer.statusMessage( csstatus.VEND_SPECIALSHOP_ITEM_BUY_LEVEL    )	
			return
			
		nearMax = self.testAddMoney( price )
		if  nearMax >= 0:	#如果玩家携带的金钱数量加上卖出物品的钱已到上限
			buyer.statusMessage( csstatus.VEND_GAINMONEY_FAILD    )		#通知买家
			self.statusMessage( csstatus.CIB_MONEY_OVERFLOW )		#通知卖家
			return
		elif nearMax == 0:
			buyer.statusMessage( csstatus.VEND_GAINMONEY_FAILD    )		#通知买家
			self.statusMessage( csstatus.CIB_MSG_MONEY_OVERFLOW )		#通知卖家
			return

		item.unfreeze( self )									# 给物品解冻
		if not buyer.payMoney( price, csdefine.CHANGE_MONEY_VEND_SELL ):			# buyer给钱失败
			item.freeze( self )								# 重新冻结物品，交易不成功
			DEBUG_MSG( "买家给钱失败。" )
			return
		buyer.addItem( item.copy(), csdefine.ADD_ITEM_VEND_SELL )					# 把物品给buyer

		#摆摊卖价超过1银要收卖价的1%税,不足1银大于5铜的收1铜  by:姜毅 2009-5-25
		if price >= 100 :
			price = price * 99 / 100
		elif price > 5 :
			price = price - 1

		self.gainMoney( price, csdefine.CHANGE_MONEY_VEND_SELL )							# vendor收钱
		# 卖家买卖记录，临时数据，下线后清空。
		records = self.queryTemp( "vendRecord", [] )
		timeStr = "%s:%s"%( time.localtime()[3], time.localtime()[4] )
		records.append( [ buyer.getName(), item.id, price, timeStr, item.amount ] )
		self.setTemp( "vendRecord", records )
		self.client.vend_addRecordNotify( [ buyer.getName(), item.name(), price, timeStr, item.amount ] )
		self.removeItemByUid_( uid, reason = csdefine.DELETE_ITEM_VEND_SELL )		# vendor删除物品
		index = self.vendMerchandise.index( temp )		# 删除相应的摆摊物品信息
		self.vendMerchandise.pop( index )
		self.client.vend_removeItemNotify( uid )		# 更新vendor客户端数据
		buyer.clientEntity( self.id ).vend_removeItemNotify( uid )			# 更新buyer客户端数据

	def vend_sellPet( self, srcEntityID, petDatabaseID ):
		"""
		提供给买家的客户端调用，vendor卖一个宠物的接口
		"""
		if srcEntityID == self.id:
			HACK_MSG( "调用者不能是自己." )
			return

		if not self._isVend():
			HACK_MSG( "卖家不在摆摊状态。" )
			return

		buyer = BigWorld.entities.get( srcEntityID )
		if buyer == None:
			HACK_MSG( "找不到玩家, srcEntityID: %i." % ( srcEntityID ) )
			return

		if not buyer.isReal():
			DEBUG_MSG( "目前仅允许real entity之间的摆摊交易。" )
			return

		# 判断是否在允许交易范围内
		if self.position.flatDistTo( buyer.position ) > csconst.COMMUNICATE_DISTANCE:	# 暂时使用COMMUNICATE_DISTANCE
			buyer.statusMessage( csstatus.VEND_DISTANCE_TOO_FAR )
			DEBUG_MSG( "too far from vendor: %s. ( srcEntityID: %s )" % ( self.getName(), srcEntityID ) )
			return

		if petDatabaseID < 0:
			HACK_MSG( "petDatabaseID(%i)参数不正确。" % ( petDatabaseID ) )
			return

		if not self.pcg_petDict.has_key( petDatabaseID ):
			HACK_MSG( "错误的宠物databaseID。" )
			return

		temp = None
		for petInfo in self.vendPetMerchandise:
			if petInfo["databaseID"] == petDatabaseID:
				temp = petInfo
				break
		if temp is None:
			buyer.statusMessage( csstatus.VEND_PET_IS_NONE )
			HACK_MSG( "相应databaseID宠物不存在。" )
			buyer.client.vend_removePetNotify( petDatabaseID )		# 更新buyer客户端数据
			return

		if buyer.pcg_isFull():
			buyer.statusMessage( csstatus.VEND_PET_IS_FULL )
			HACK_MSG( "买方的宠物栏已满" )
			return

		petDict = self.pcg_petDict.get( petDatabaseID )
		if buyer.level < petDict.takeLevel or buyer.level + 5 < petDict.level:
			buyer.statusMessage( csstatus.ROLE_PET_TAKE_LEVEL_INVALID )
			HACK_MSG( "买方的等级不足" )
			return

		price = temp["price"]
		if buyer.money < price:
			buyer.statusMessage( csstatus.VEND_NOT_ENOUGH_MONEY )
			DEBUG_MSG( "买家钱不够买摆摊物品。" )
			return

		nearMax = self.testAddMoney( price )
		if  nearMax > 0:	#如果玩家携带的金钱数量加上卖出物品的钱已到上限
			buyer.statusMessage( csstatus.VEND_GAINMONEY_FAILD    )		#通知买家
			self.statusMessage( csstatus.CIB_MONEY_OVERFLOW )		#通知卖家
			return
		elif nearMax == 0:
			buyer.statusMessage( csstatus.VEND_GAINMONEY_FAILD    )		#通知买家
			self.statusMessage( csstatus.CIB_MSG_MONEY_OVERFLOW )		#通知卖家
			return

		if not buyer.payMoney( price, csdefine.CHANGE_MONEY_VEND_SELLPET ):			# buyer给钱失败
			DEBUG_MSG( "买家给钱失败。" )
			return

		#摆摊卖价超过1银要收卖价的1%税,不足1银大于5铜的收1铜,代码加入人:姜毅 2009-5-25
		if price >= 100 :
			price = price * 99 / 100
		elif price > 5 :
			price = price - 1

		self.gainMoney( price, csdefine.CHANGE_MONEY_VEND_SELLPET )							# vendor收钱

		timeStr = "%s:%s"%( time.localtime()[3], time.localtime()[4] )
		self.base.vend_addRecordNotify( buyer.getName(), petDatabaseID, price, timeStr )

		self.base.vend_sellPet( buyer.base, petDatabaseID )	# 宠物转移

		# 卖家买卖记录，临时数据，下线后清空。
		if temp in self.vendPetMerchandise:
			self.vendPetMerchandise.remove( temp )

		self.client.vend_removePetNotify( petDatabaseID )							# 更新vendor客户端数据
		buyer.clientEntity( self.id ).vend_removePetNotify( petDatabaseID )			# 更新buyer客户端数据

	def vend_isVendedPet( self, dbid ) :
		"""
		根据宠物DBID判断该宠物是否在摆摊中
		@param		dbid : 宠物的DBID
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
# 添加卖家客户端记录更新函数vend_addRecordNotify
#
# Revision 1.4  2008/07/01 03:06:50  zhangyuxing
# 增加物品进入背包返回失败的状态
#
# Revision 1.3  2008/05/30 03:01:33  yangkai
# 装备栏调整引起的部分修改
#
# Revision 1.2  2008/05/07 02:58:55  yangkai
# no message
#
# Revision 1.1  2007/12/14 07:31:34  wangshufeng
# 添加摆摊系统(RoleVend)
#
#
#
#
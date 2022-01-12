# -*- coding: gb18030 -*-
#
# $Id: RoleVend.py,v 1.3 2008-09-03 10:44:47 fangpengjun Exp $

import BigWorld

from bwdebug import *
import csdefine
import event.EventCenter as ECenter
import config.client.labels.RoleVend as lbDatas
from NPCModelLoader import NPCModelLoader as NPCModel

class RoleVend:
	"""
	玩家摆摊系统
	"""
	def __init__( self ):
		"""
		"""
		self.sellerID = 0
		pass
		#self.vendMerchandise = {}		# test,wsf

	def vend_vend( self, kitUidList, uidList, priceList, petDatabaseIDList = [], petPriceList = [] ):
		"""
		玩家摆摊的接口，在界面上先检查玩家是否满足摆摊条件，满足才能打开摆摊界面
		在调用此接口之前在界面必须先做检测:
		BigWorld.player().position,检查是否是在允许摆摊范围,不在则不弹出摆摊界面wsf
		if BigWorld.player().actionSign( csdefine.ACTION_FORBID_VEND ):
			DEBUG_MSG( "玩家处于不允许摆摊状态." )
		通知打开摆摊界面,接收摆摊的数据,然后才能调用此接口

		param kitUidList: 玩家摆摊物品的包裹号列表
		type kitUidList: ARRAY OF UINT8
		param uidList: 玩家摆摊物品的uidList列表
		type uidList: ARRAY OF INT64
		param priceList: 与摆摊物品对应的摆摊物品价格列表
		type priceList: ARRAY OF UINT32
		"""
		# 在卖家界面上要保存一个摆摊物品列表,当摆摊物品卖出,回来通知卖家界面删除相应的数据,更新界面
		self.cell.vend_vend( kitUidList, uidList, priceList, petDatabaseIDList, petPriceList )

	def vend_pauseVend( self ):
		"""
		玩家暂停摆摊接口
		"""
		self.cell.vend_endVend( False )

	def vend_endVend( self ):
		"""
		玩家结束摆摊的接口
		"""
		self.cell.vend_endVend( True )

	def vend_setSignboard( self, signboard ):
		"""
		卖家设置摊位招牌的接口，界面调用时如果玩家不更改默认招牌，则signboard默认使用“**的店铺”参数
		如果玩家更改了招牌名字，则默认参数变为玩家合法更改的招牌名，以便玩家收摊而不是关闭摆摊时使用没有清空的参数。

		param signboard: 欲设置的摊位名
		type signboard: STRING
		"""
		self.cell.vend_setSignboard( signboard )

	def set_vendSignboard( self, oldValue ):
		"""
		卖家摆摊招牌自动更新函数
		"""
		if oldValue != self.vendSignboard:
			ECenter.fireEvent( "EVT_ON_VEND_UI_NAME_CHANGE", self.id, self.vendSignboard ) #界面更新招牌名称
		signboard = ""
		if self.vendSignboard == "":
			signboard = self.getName() + lbDatas.SIGNBOARD
		else:
			signboard = self.vendSignboard
		ECenter.fireEvent( "EVT_ON_VEND_SIGNBOARD_NAME_CHANGED", self.id, signboard ) #更新头顶招牌名称

	def set_vendSignboardNumber( self, oldValue ):
		"""
		卖家摆摊招牌贴图更新函数
		"""
		if oldValue != self.vendSignboardNumber:
			ECenter.fireEvent( "EVT_ON_VEND_SIGNBOARD_NUMBER_CHANGE", self.vendSignboardNumber ) #更新

	def	vend_buyerQueryInfo( self, vendorID ):
		"""
		买家查看卖家摊位数据的接口

		param vendorID:	卖家的entity id
		type vendorID:	OBJECT_ID
		"""
		if self.id == vendorID:
			HACK_MSG( "vendor不能是自己." )
			return

		vendor = BigWorld.entities.get( vendorID )
		if vendor == None:
			HACK_MSG( "找不到玩家, vendorID: %i" % ( vendorID ) )
			return

		vendor.cell.vend_buyerQueryInfo()			# 包括出售的物品、宠物消息
		vendor.cell.queryOwnCollectionItem()		# 查询收购物品
		ECenter.fireEvent( "EVT_ON_CLEAR_VEND_PURCHASED_ITEM" )
		self.sellerID = vendorID

	def vend_receiveShopData( self, items ):
		"""
		Define method.
		买家接收卖家摊位数据的接口

		param items:摆摊的物品数据
		type items:	ITEMS
		"""
		# 通知界面wsf
		ECenter.fireEvent( "EVT_ON_VEND_STATE_CHANGE", csdefine.ENTITY_STATE_VEND )
		ECenter.fireEvent( "EVT_ON_VEND_RECEIVE_VEND_ITEMS", items )
		#for temp in items:
		#	self.vendMerchandise[temp.getuid()] = temp	# test,存为一个字典,方便操作wsf

	def vend_receivePetData( self, epitomes ):
		"""
		买家接收卖家摆摊出售宠物数据的接口
		"""
		ECenter.fireEvent( "EVT_ON_VEND_RECEIVE_VEND_PETEPITOMES", epitomes )

	def vend_receiveRecord( self, record ):
		"""
		Define mehthod.
		买家接收卖家买卖记录数据的函数

		@param record : [ playerName, itemID, time, price ]
		@type record : PYTHON --> [ STRING, itemID, FLOAT, UINT32 ]
		"""
		ECenter.fireEvent( "EVT_ON_VEND_BUYER_RECEIVE_RECORD", record )

	def vend_addRecordNotify( self, record ):
		"""
		Define mehthod.
		卖家自己更新客户端记录
		@param record : [ playerName, itemID, time, price ]
		@type record : PYTHON --> [ STRING, itemID, FLOAT, UINT32 ]
		"""
		ECenter.fireEvent( "EVT_ON_VEND_VENDOR_ADD_RECORD", record )
		
	def vend_addRecordNotify2( self, record ):
		"""
		Define mehthod.
		更新收购记录
		@param record : [ playerName, itemID, time, price ]
		@type record : PYTHON --> [ STRING, itemID, FLOAT, UINT32 ]
		"""
		ECenter.fireEvent( "EVT_ON_VEND_VENDOR_ADD_RECORD_BUY", record )

	def vend_buy( self, uid, vendorID ):
		"""
		买家买一个物品接口

		param uid:	买家欲买物品的uid
		type uid:	INT64
		param vendorID:	卖家的entity id
		type vendorID:	OBJECT_ID
		"""
		if self.id == vendorID:
			HACK_MSG( "vendor不能是自己." )
			return

		vendor = BigWorld.entities.get( vendorID )
		if vendor == None:
			HACK_MSG( "找不到玩家, vendorID: %i" % ( vendorID ) )
			return

		vendor.cell.vend_sell( uid )

	def vend_buyPet( self, petDatabaseID, vendorID ):
		"""
		买家买一个宠物的接口
		"""
		if self.id == vendorID:
			HACK_MSG( "vendor不能是自己." )
			return

		vendor = BigWorld.entities.get( vendorID )
		if vendor == None:
			HACK_MSG( "找不到玩家, vendorID: %i" % ( vendorID ) )
			return

		vendor.cell.vend_sellPet( petDatabaseID )

	def vend_removeItemNotify( self, uid ):
		"""
		Define method.
		相应uid的物品被买走，更新玩家客户端数据

		param uid: 买家欲买物品的uid
		type uid: INT64
		"""
		#try:
		#	del self.vendMerchandise[uid]
		#except KeyError:
		#	DEBUG_MSG( "uid(%i)不存在。" % ( uid ) )
		ECenter.fireEvent( "EVT_ON_VEND_ITEM_SELLED", uid )
		# 通知界面,wsf

	def	vend_removePetNotify( self, petDataBaseID ):
		"""
		dataBaseID的宠物被买走，更新玩家客户端数据
		"""
		ECenter.fireEvent( "EVT_ON_VEND_PET_SELLED",petDataBaseID )

	def vend_onLeaveWorld( self ):
		self.vendSignboard = ""

	def _isVend( self ):
		"""
		判断自己是否处于摆摊状态
		"""
		return self.getState() == csdefine.ENTITY_STATE_VEND

	def vend_onVendEnd( self ):
		"""
		结束摆摊时调用。
		注：和上面的区别vend_endVend。
		vend_endVend是：	界面调用向服务器申请关闭。
		vend_onVendEnd是：	服务器发送回状态改变时调用。
		"""
		if self.id == BigWorld.player().sellerID: #买家关闭客户端关闭界面
			# 关掉界面
			ECenter.fireEvent( "EVT_ON_VEND_STATE_CHANGE", csdefine.ENTITY_STATE_FREE )
			BigWorld.player().sellerID = 0
		ECenter.fireEvent( "EVT_ON_VEND_RESET_SIGNBOARD", self.id )#卖家自己重新设置头顶信息

#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/09/02 09:56:48  fangpengjun
# 添加记录更新函数vend_addRecordNotify，以及界面信息更新消息
#
# Revision 1.1  2007/12/14 07:31:20  wangshufeng
# 添加摆摊系统(RoleVend)
#
#
#
#
# -*- coding: gb18030 -*-
#
# $Id: RoleTradeWithNPC.py,v 1.7 2008-05-04 06:44:37 zhangyuxing Exp $

"""
"""

import BigWorld
import GUIFacade
import csdefine
import event.EventCenter as ECenter
from bwdebug import *

class RoleTradeWithNPC:
	"""
	与NPC商人交易
	"""

	def __init__( self ) :
		self.__targetID = 0					# 当前交易 NPC 的 ID	（2008.09.16）

	def leaveTradeWithNPC( self ):
		"""
		Define Method
		离开当与NPC交易状态
		"""
		self.__targetID = 0									# 清除对话 NPC 的 ID
		GUIFacade.onTradeWithNPCOver()

	def enterTradeWithNPC( self, objectID ):
		"""
		Define Method
		进入与NPC交易状态
		@param   objectID: 交易目标
		@type    objectID: OBJECT_ID
		@return: 无
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The trade NPC  %s has not exist " % objectID )
			self.__targetID = 0
			return

		if self.__targetID == objectID : return								# 重复点击了同一个 NPC 进行交易，则返回
		ECenter.fireEvent("EVT_ONTRADE_STATE_LEAVE", self.tradeState )		# 则结束之前的交易（这样做法很不好）
		self.__targetID = objectID											# 记录下当前对话的 NPC ID（hyw -- 2008.09.16）
		# 取得商品列表
		#if not entity.isRequesting() :										# 增加是否处于物品申请过程中的判断( hyw -- 2008.09.16 )
		entity.cell.sendInvoiceListToClient()								# 如果正处在申请商品列表状态，则不会再申请
		# 通知开始交易了
		tradeObject = entity.__class__.__name__
		if tradeObject == "Merchant":
			entity.cell.sendPriceChangeInfo()								# 向服务器申请价格变动信息，只有Merchant才有这个方法
			GUIFacade.onTradeWithMerchant( entity )
		elif tradeObject == "DarkMerchant":
			entity.cell.sendPriceChangeInfo()
			GUIFacade.onTradeWithDarkMerchant( entity )
		elif tradeObject == "YXLMEquipChapman":
			GUIFacade.onTradeWithYXLMEquipChapman( entity )
		else:
			#entity.__class__.__name__ == "Chapman":
			GUIFacade.onTradeWithNPC( entity )

	def enterTradeWithDarkTrader( self, objectID ):
		"""
		Define Method
		从投机商人处购买物品
		@param   objectID: 交易目标
		@type    objectID: OBJECT_ID
		@return: 无
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The trade NPC  %s has not exist " % objectID )
			self.__targetID = 0
			return
		if self.__targetID == objectID:
			return										# 重复点击了同一个 NPC 进行交易，则返回
		ECenter.fireEvent("EVT_ONTRADE_STATE_LEAVE", self.tradeState )	# 则结束之前的交易（这样做法很不好）
		self.__targetID = objectID						# 记录下当前对话的 NPC ID（hyw -- 2008.09.16）
		entity.cell.sendInvoiceListToClient()			# 取得商品列表，如果正处在申请商品列表状态，则不会再申请
		GUIFacade.onTradeWithDarkTrader( entity )		# 通知开始交易了

	def tradeWithItemChapman( self, objectID ):
		"""
		Define Method
		进入与NPC交易状态
		@param   objectID: 交易目标
		@type    objectID: OBJECT_ID
		@return: 无
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The trade NPC  %s has not exist " % objectID )
			self.__targetID = 0
			return

		if self.__targetID == objectID : return								# 重复点击了同一个 NPC 进行交易，则返回
		ECenter.fireEvent("EVT_ONTRADE_STATE_LEAVE", self.tradeState )		# 则结束之前的交易（这样做法很不好）
		self.__targetID = objectID											# 记录下当前对话的 NPC ID
		# 取得商品列表
		entity.cell.sendInvoiceListToClient()								# 如果正处在申请商品列表状态，则不会再申请
		# 通知开始交易了
		GUIFacade.onTradeWithItemChapman( entity )

	def tradeWithPointChapman( self, objectID ):
		"""
		Define Method
		进入与NPC交易状态
		@param   objectID: 交易目标
		@type    objectID: OBJECT_ID
		@return: 无
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The trade NPC  %s has not exist " % objectID )
			self.__targetID = 0
			return
		if self.__targetID == objectID : return								# 重复点击了同一个 NPC 进行交易，则返回
		ECenter.fireEvent("EVT_ONTRADE_STATE_LEAVE", self.tradeState )		# 则结束之前的交易（这样做法很不好）
		self.__targetID = objectID											# 记录下当前对话的 NPC ID
		# 取得商品列表
		entity.cell.sendInvoiceListToClient()								# 如果正处在申请商品列表状态，则不会再申请
		# 通知开始交易了
		GUIFacade.onTradeWithPointChapman( entity )

	def onTradeWithTongSpecialChapman( self, objectID ):
		"""
		与帮会特殊商人对话
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The trade NPC  %s has not exist " % objectID )
			self.__targetID = 0
			return
		if self.__targetID == objectID : return								# 重复点击了同一个 NPC 进行交易，则返回
		ECenter.fireEvent("EVT_ONTRADE_STATE_LEAVE", self.tradeState )		# 则结束之前的交易（这样做法很不好）
		self.__targetID = objectID											# 记录下当前对话的 NPC ID
		# 取得商品列表
		entity.cell.sendInvoiceListToClient()								# 如果正处在申请商品列表状态，则不会再申请
		# 通知开始交易了
		GUIFacade.onTradeWithTongSpecialChapman( entity )

	def delRedeemItemUpdate( self, uid ):
		"""
		Define method.
		回购一个可赎回物品成功的更新函数，删除可赎回列表的对应物品

		param uid:
		type uid:
		"""
		GUIFacade.onDelRedeemItem( uid )

	def addRedeemItemUpdate( self, item ):
		"""
		Define method.
		给可赎回物品列表增加物品的更新函数

		param item:	新加入可赎回列表的物品
		type item:	ITEM
		"""
		GUIFacade.onAddRedeemItem( item )

	def getTradeNPCID( self ) :
		"""
		获取当前正在交易的 NPC ID
		hyw -- 2008.09.16
		@rtype				: INT32
		@return				: 如果存在交易 NPC 则返回 NPC ID，否则返回 0
		"""
		return self.__targetID

	def onAddYXLMEquip( self, equipInstance ):
		"""
		<Define method>
		获得英雄联盟的装备
		@type	equipItem : ITEM
		@param	equipItem : 继承于CItemBase的物品实例
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_ADD_YXLM_EQUIP", equipInstance )

	def onRemoveYXLMEquip( self, equipUid ) :
		"""
		<Define method>
		移除英雄联盟的装备
		@type	equipUid : UID
		@param	equipUid : 物品实例的UID
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_REMOVE_YXLM_EQUIP", equipUid )
#
# $Log: not supported by cvs2svn $
# Revision 1.6  2007/11/19 08:10:11  wangshufeng
# add interface: delRedeemItemUpdate,回购一个可赎回物品成功的更新函数;
# add interface: addRedeemItemUpdate,可赎回物品列表数据变动的更新函数;
#
# Revision 1.5  2007/08/18 08:12:31  yangkai
# NPC交易代码调整
#     - 修改相关接口
#
# Revision 1.4  2007/06/14 10:32:35  huangyongwei
# 整理了全局宏定义
#
# Revision 1.3  2006/07/21 08:12:37  phw
# 修改了接口：
#     onLeaveTrade()
#     onEnterTrade()
#
# Revision 1.2  2006/05/18 03:28:26  huangyongwei
# no message
#
# Revision 1.1  2005/12/12 01:58:55  phw
# no message
#
#

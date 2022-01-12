# -*- coding: gb18030 -*-
#
# $Id: RoleSwapItem.py,v 1.41 2008-06-21 01:34:23 zhangyuxing Exp $

"""
"""

import BigWorld
import csdefine
import csconst
import csstatus
from bwdebug import *
import GUIFacade

from event.EventCenter import *
from ItemsFactory import ObjectItem


class RoleSwapItem:
	"""
	玩家间物品交换相关代码
	"""
	def __init__( self ):
		"""
		"""
		self.si_dstState = 0	# 交易对象的状态
		self.si_myItem = {}
		self.si_dstItem = {}
		self.si_dstPet = {}
		self.si_targetID = 0

	def si_resetData( self ):
		"""
		重置所有数据到未交易前状态
		"""
		self.si_dstState = 0	# 交易对象的状态
		self.si_myItem.clear()
		self.si_dstItem.clear()
		self.si_dstPet.clear()
		self.si_targetID = 0


	def si_dstChangePet( self, epitome ):
		"""
		Define method.
		交易对像改变交易物品

		param epitome: 宠物数据
		type epitome: PET_EPITOME
		"""
		self.si_dstPet[ epitome.databaseID ] = epitome
		# 通知界面。
		fireEvent( "EVT_ON_RSI_DST_PET_CHANGE", epitome )

	def si_dstChangeItem( self, swapOrder, itemData ):
		"""
		Define method.
		交易对像改变交易物品

		@param swapOrder: 哪个位置的物品改变
		@type  swapOrder: UINT8
		@param  itemData: 物品数据
		@type   itemData: ITEM
		"""
		self.si_dstItem[ swapOrder ] = itemData
		GUIFacade.onDstSwapItemChanged( swapOrder, itemData )

	def si_meChangeItem( self, swapOrder, kitOrder, uid ):
		"""
		Define method.
		改变自己的交易物品

		@param swapOrder: 交换位置
		@param  kitOrder: 哪个背包
		@param       uid: 哪个物品
		"""
		if self.si_myItem.has_key( swapOrder ):
			itemInfo = ObjectItem( self.si_myItem[ swapOrder ] )
			fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", itemInfo.kitbagID, itemInfo.orderID, False ) #解锁物品
			del self.si_myItem[ swapOrder ] #删除交易列表中对该物品的记录
		self.si_myItem[ swapOrder ] = self.getItemByUid_( uid )
		GUIFacade.onSelfSwapItemChanged( swapOrder, self.si_myItem[ swapOrder ] )
		itemInfo = ObjectItem( self.si_myItem[ swapOrder ] )
		fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", itemInfo.kitbagID, itemInfo.orderID, True ) #锁定物品


	def si_removeSwapItem( self, flag, swapOrder ):
		"""
		Define method.
		交易对像删除一个交易物品

		@param    flag: 删除的交易栏位, 0 表示删除自己的栏位, 1 表示删除目标的栏位
		@type     flag: UINT8
		@param swapOrder: 交易栏位置
		@type  swapOrder: UINT8
		"""
		if flag == 0:
			#GUIFacade.onSelfSwapItemChanged( swapOrder, self.si_myItem[swapOrder] )
			itemInfo = ObjectItem( self.si_myItem[ swapOrder ] )
			fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", itemInfo.kitbagID, itemInfo.orderID, False ) #解锁物品
			del self.si_myItem[ swapOrder ] #删除交易列表中对该物品的记录
			GUIFacade.onSelfSwapItemChanged( swapOrder, None )
		else:
			del self.si_dstItem[ swapOrder ]
			GUIFacade.onDstSwapItemChanged( swapOrder, None )


	def set_si_myMoney( self, oldValue = 0 ):
		"""
		当自己改变交易金额被确认时
		"""
		#DEBUG_MSG( "oldValue =", oldValue, "newValue =", self.si_myMoney )
		GUIFacade.onSelfSwapMoneyChanged( self.si_myMoney )


	def set_si_dstMoney( self, oldValue = 0 ):
		"""
		当交易对像改变交易金额时
		"""
		#DEBUG_MSG( "oldValue =", oldValue, "newValue =", self.si_dstMoney )
		GUIFacade.onDstSwapMoneyChanged( self.si_dstMoney )


	def set_si_myPetDBID( self, oldValue ):
		"""
		改变用于交易的宠物
		"""
		if oldValue != self.si_myPetDBID:
			fireEvent( "EVT_ON_RSI_SELF_PET_CHANGED", self.si_myPetDBID )

	def set_si_myState( self, oldValue = 0 ):
		"""
		当交易状态改变时
		"""
		DEBUG_MSG( "oldValue =", oldValue, "newValue =", self.si_myState )
		if self.si_myState == csdefine.TRADE_SWAP_DEFAULT:
			if oldValue == csdefine.TRADE_SWAP_INVITE or oldValue == csdefine.TRADE_SWAP_PET_INVITE:
				# 拒绝交易
				BigWorld.player().statusMessage( csstatus.ROLE_TRADE_TARGET_REFUSED )
				return
			if oldValue == csdefine.TRADE_SWAP_WAITING or oldValue == csdefine.TRADE_SWAP_PET_WAITING:
				return
			if oldValue != csdefine.TRADE_SWAP_LOCKAGAIN:
				for order in self.si_myItem:
					itemInfo = ObjectItem( self.si_myItem[ order ] )
					fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", itemInfo.kitbagID, itemInfo.orderID, False ) #解锁物品
			GUIFacade.onSwapItemEnd()
			self.si_resetData()
		elif self.si_myState == csdefine.TRADE_SWAP_INVITE or self.si_myState == csdefine.TRADE_SWAP_PET_INVITE:
			BigWorld.callback( csconst.TRADE_WAITING_TIME, self.onSwapInviteTimer )
		elif self.si_myState == csdefine.TRADE_SWAP_WAITING or self.si_myState == csdefine.TRADE_SWAP_PET_WAITING:
			if self.si_targetID == 0:
				DEBUG_MSG( "对方的id还没更新。" )
				return
			# 如果交易对象的id先于己方状态更新，那么在这里谈出询问是否交易的窗口
			try:
				name = BigWorld.entities[ self.si_targetID ].getName()
			except KeyError:
				self.si_tradeCancel()
				return
			if not self.allowTrade:	#拒绝交易
				self.si_tradeCancel()
				return
			flag = self.si_myState == csdefine.TRADE_SWAP_WAITING
			GUIFacade.onInviteSwapItem( name, flag )
		elif self.si_myState == csdefine.TRADE_SWAP_BEING:
			# 显示交易窗，开始交易
			#self.si_dstItem = {}
			#self.si_myItem = {}
			if oldValue == csdefine.TRADE_SWAP_INVITE or oldValue == csdefine.TRADE_SWAP_WAITING:
				GUIFacade.onSwapItemBegin( BigWorld.entities[ self.si_targetID ].getName() )
			#elif oldValue == csdefine.TRADE_SWAP_PET_BEING or oldValue == csdefine.TRADE_SWAP_PET_LOCK:
			#	DEBUG_MSG( "从宠物交易进入物品交易。" )
			fireEvent( "EVT_ON_RSI_SELF_SWAP_STATE_CHANGED", self.si_myState )
		elif self.si_myState == csdefine.TRADE_SWAP_LOCK:
			fireEvent( "EVT_ON_RSI_SELF_SWAP_STATE_CHANGED", self.si_myState )
			#GUIFacade.onDstSwapStateChanged( True, False )
			#GUIFacade.onSelfSwapStateChanged( False, True )
		elif self.si_myState == csdefine.TRADE_SWAP_SURE:
			fireEvent( "EVT_ON_RSI_SELF_SWAP_STATE_CHANGED", self.si_myState )
		elif self.si_myState == csdefine.TRADE_SWAP_PET_BEING:
			DEBUG_MSG( "改变宠物交易的数据，回复宠物正在交易状态。" )
			fireEvent( "EVT_ON_RSI_SELF_SWAP_STATE_CHANGED", self.si_myState )
			if oldValue == csdefine.TRADE_SWAP_PET_INVITE or oldValue == csdefine.TRADE_SWAP_PET_WAITING:
				fireEvent( "EVT_ON_RSI_SWAP_PET_BEGIN", BigWorld.entities[ self.si_targetID ].getName() )
		elif self.si_myState == csdefine.TRADE_SWAP_PET_LOCK:
			fireEvent( "EVT_ON_RSI_SELF_SWAP_STATE_CHANGED", self.si_myState )
			DEBUG_MSG( "锁定宠物交易。" )

	def onSwapInviteTimer( self ):
		"""
		邀请时间期限
		"""
		if self.si_myState == csdefine.TRADE_SWAP_INVITE or \
		self.si_myState == csdefine.TRADE_SWAP_PET_INVITE:
			self.si_tradeCancel()


	def si_replySwapItemInvite( self, accept = True ):
		"""
		物品交易邀请答复

		@param accept: 是否接受交易
		@type  accept: BOOL
		"""
		if not self.__canTrade():
			return
		if accept:
			self.cell.si_changeStateFC( csdefine.TRADE_SWAP_BEING )		# 接受交易
		else:
			self.si_tradeCancel()				# 不接受交易


	def si_replySwapPetInvite( self, accept = True ):
		"""
		宠物交易邀请答复

		@param accept: 是否接受交易
		@type  accept: BOOL
		"""
		if not self.__canTrade():
			return
		if accept:
			self.cell.si_changeStateFC( csdefine.TRADE_SWAP_PET_BEING )		# 接受交易
		else:
			self.si_tradeCancel()				# 不接受交易


	def set_si_targetID( self, oldValue = 0 ):
		"""
		"""
		DEBUG_MSG( "oldValue =", oldValue, "newValue =", self.si_targetID )

		# 如果己方的状态先于交易对象的id更新，那么在这里询问是否进行交易
		if self.si_targetID != 0 and ( self.si_myState == csdefine.TRADE_SWAP_WAITING or self.si_myState == csdefine.TRADE_SWAP_PET_WAITING ):
			try:
				name = BigWorld.entities[ self.si_targetID ].getName()
			except KeyError:
				self.si_tradeCancel()
				return
			if not self.allowTrade:	#拒绝交易
				self.si_tradeCancel()
				return
			self.si_swapFlag = True
			flag = self.si_myState == csdefine.TRADE_SWAP_WAITING
			GUIFacade.onInviteSwapItem( name, flag )


	def si_getTargetEntity( self ):
		"""
		获得交易对象的entity
		"""
		return BigWorld.entities.get( self.si_targetID )


	def si_tradeCancel( self ):
		"""
		取消交易
		"""
		self.cell.si_tradeCancelFC()


	def si_requestSwap( self, entity, flag ):
		"""
		请求与某entity交易
		"""
		if not entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_TARGET_REFUSED )
			return

		if self.id == entity.id:
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_CANNOT_TRADE_SELF )
			return
		if self.position.flatDistTo( entity.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.ROLE_TRADE_TARGET_TOO_FAR )
			return

		self.cell.si_requestSwapFC( entity.id, flag )


	def si_changeItem( self, swapOrder, kitOrder, order ):
		"""
		改变某个位置上的交易物品

		@param swapOrder: 交易栏中的位置
		@type  swapOrder: INT
		@param  kitOrder: 物品所在的背包
		@type   kitOrder: INT
		@param     order: 物品所在的位置
		@type      order: INT
		"""
		if not self.__isTrading():	# 没有在交易状态或已处于确认状态
			#ERROR_MSG( "state not allow." )
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_OPERATER_NOT_ALLOW )
			return
		if swapOrder >= csconst.TRADE_ITEMS_UPPER_LIMIT:
			#ERROR_MSG( "swap order overflow." )
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_POS_WRONG )
			return
		try:
			kit = self.kitbags[ kitOrder ]
		except KeyError:
			#ERROR_MSG( "no such kitbag." )
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_KITBAG_INVALID )
			return

		order = kitOrder * csdefine.KB_MAX_SPACE + order
		item = self.getItem_( order )

		if item is None:
			#ERROR_MSG( "item not found." )
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_ITEM_INVALID )
			return

		if not item.canGive():
			#ERROR_MSG( "item can't trade." )
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_ITEM_CANT_TRAEDED )
			return

		if not self.__canTrade():
			return
		uid = self.order2uid( order )
		self.cell.si_changeItemFC( swapOrder, kitOrder, uid )


	def si_removeItem( self, swapOrder ):
		"""
		删除某个位置上的交易物品

		@param swapOrder: 交易栏中的位置
		@type  swapOrder: INT
		"""
		if not self.__isTrading():	# 没有在交易状态或已处于确认状态
			#ERROR_MSG( "state not allow." )
			self.statusMessage( csstatus.ROLE_TRADE_OPERATER_NOT_ALLOW )
			return
		if swapOrder >= csconst.TRADE_ITEMS_UPPER_LIMIT:
			#ERROR_MSG( "swap order overflow." )
			self.statusMessage( csstatus.ROLE_TRADE_POS_WRONG  )
			return
		if not self.si_myItem.has_key( swapOrder ):
			#ERROR_MSG( "swap order item not exist." )
			self.statusMessage( csstatus.ROLE_TRADE_ITEM_INVALID )
			return
		if not self.__canTrade():
			return
		self.cell.si_removeItemFC( swapOrder )


	def si_changeMoney( self, amount ):
		"""
		改变金钱数
		"""
		if not self.__isTrading():	# 没有在交易状态或已处于确认状态
			#ERROR_MSG( "state not allow." )
			self.statusMessage( csstatus.ROLE_TRADE_OPERATER_NOT_ALLOW )
			return
		if amount > self.money:
			#ERROR_MSG( "money not enough." )
			GUIFacade.onSelfSwapMoneyChanged( self.si_myMoney )
			self.statusMessage( csstatus.ROLE_TRADE_HAVET_SUCH_MONEY, amount )
			return
		if not self.__canTrade():
			return
		self.cell.si_changeMoneyFC( amount )


	def si_changePet( self, petDBID ):
		"""
		改变用于交易的宠物
		"""
		if not self.__isTrading():	# 没有在交易状态或已处于确认状态
			#ERROR_MSG( "state not allow." )
			self.statusMessage( csstatus.ROLE_TRADE_OPERATER_NOT_ALLOW )
			return
		if not self.__canTrade():
			return
		self.cell.si_changePetFC( petDBID )


	def si_removePet( self ):
		"""
		移除交易宠物
		"""
		if not self.__isTrading():	# 没有在交易状态或已处于确认状态
			self.statusMessage( csstatus.ROLE_TRADE_OPERATER_NOT_ALLOW )
			return
		if not self.__canTrade():
			return
		self.cell.si_removePetFC()


	def si_dstRemovePet( self ):
		"""
		Define method.
		交易对象移除交易宠物
		"""
		self.si_dstPet.clear()
		# 通知界面，wsf
		fireEvent( "EVT_ON_RSI_DST_PET_REMOVE" )

	def si_secondAccept( self, accept = True ):
		"""
		物品第二次确认
		"""
		if accept:
			self.cell.si_changeStateFC( csdefine.TRADE_SWAP_SURE )
		else:
			self.cell.si_changeStateFC( csdefine.TRADE_SWAP_BEING )


	def si_accept( self ):
		"""
		物品第一次确认
		"""
		self.cell.si_changeStateFC( csdefine.TRADE_SWAP_LOCK )


	def si_acceptPet( self ):
		"""
		宠物第一次确认
		"""
		self.cell.si_changeStateFC( csdefine.TRADE_SWAP_PET_LOCK )

	def si_secondAcceptPet( self, accept = True ):
		"""
		宠物第二次确认
		"""
		if accept:
			self.cell.si_changeStateFC( csdefine.TRADE_SWAP_SURE )
		else:
			self.cell.si_changeStateFC( csdefine.TRADE_SWAP_PET_BEING )


	def si_changeState( self, state ):
		"""
		玩家改变自己状态的接口，锁定、确认交易相当于改变状态。
		"""
		if not self.__canTrade():
			return
		self.cell.si_changeStateFC( state )

	def __canTrade( self ):
		"""
		是否能够进行交易活动，是则返回True，否则返回False
		"""
		dstEntity = BigWorld.entities.get( self.si_targetID )
		if dstEntity == None:
			return False
		if self.position.flatDistTo( dstEntity.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.ROLE_TRADE_TARGET_TOO_FAR )
			return False
		return True


	def __isTrading( self ):
		"""
		判断自己是否在交易状态中

		@return: bool
		"""
		#在开始交易到锁定前，判断玩家处于交易状态中
		if self.si_myState > csdefine.TRADE_SWAP_WAITING and self.si_myState < csdefine.TRADE_SWAP_SURE:
			return True
		return False


	def si_dstStateChange( self, state ):
		"""
		Define method.
		交易对象的状态改变
		"""
		self.si_dstState = state
		fireEvent( "EVT_ON_RSI_DST_SWAP_STATE_CHANGED", state )

#
# $Log: not supported by cvs2svn $
# Revision 1.40  2008/06/05 02:21:47  wangshufeng
# 交易状态为TRADE_SWAP_DEFAULT时，关闭交易窗口
#
# Revision 1.39  2008/05/31 03:04:38  yangkai
# 物品获取接口改变
#
# Revision 1.38  2008/05/30 09:54:15  fangpengjun
# 为宠物交易添加部分消息
#
# Revision 1.37  2008/05/28 08:36:57  wangshufeng
# 分离宠物交易和物品交易，相应调整代码
#
# Revision 1.36  2008/05/22 08:03:05  wangshufeng
# add method;si_getTargetEntity,获得目标玩家实体
#
# Revision 1.35  2008/05/04 06:44:28  zhangyuxing
# no message
#
# Revision 1.34  2008/03/19 02:49:00  wangshufeng
# 新版玩家交易系统
#

#
#

# -*- coding: gb18030 -*-
#
from bwdebug import *
from Chapman import Chapman
import csstatus
import csdefine
import cschannel_msgs

class TongSpecialChapman( Chapman ):
	"""
	帮会特殊商人
	"""
	def __init__( self ):
		Chapman.__init__( self )

	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		与玩家对话；未声明(不能声明)的方法，因此重载此方法的上层如果需要访问自己的私有属性请自己判断self.isReal()。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 说话的玩家
		@type  playerEntity: Entity
		@param       dlgKey: 对话关键字
		@type        dlgKey: str
		@return: 无
		"""
		if selfEntity.ownTongDBID != playerEntity.tong_dbID:
			playerEntity.statusMessage( csstatus.TONG_NPC_IS_TARGET_TONG_NPC )
			return
		elif selfEntity.locked:
			playerEntity.statusMessage( csstatus.TONG_NPC_LOCKED )
			return
#		if playerEntity.tong_grade != csdefine.TONG_DUTY_CHIEF:				#只能帮主对话
#			playerEntity.statusMessage( csstatus.TONG_NPC_LOCKED )
#			return
		tongMailbox = playerEntity.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.onRequestOpenTongSpecialShop( selfEntity.base, playerEntity.id, dlgKey )
	
	def onRequestOpenTongSpecialShop( self, selfEntity, srcEntityID, talkID, isEnough ):
		"""
		打开特殊商店
		"""
		try:
			playerEntity = BigWorld.entities[srcEntityID]
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % srcEntityID )	# 这个应该永远都不可能到达
			return
		if isEnough:
			Chapman.gossipWith( self, selfEntity, playerEntity, talkID )
		else:
			playerEntity.setGossipText( cschannel_msgs.TONG_INFO_27 )
			playerEntity.sendGossipComplete( selfEntity.id )
	
	def sellTo( self, selfEntity, playerEntity, argIndex, argAmount ):
		"""
		商人把东西卖给玩家

		@param 	 selfEntity	 : NPC自身实例
		@param   playerEntity: 玩家
		@param   argIndex	 : 要买第几个货物
		@param   argAmount	 : 要买的数量
		@return: 			无
		"""
		try:
			objInvoice = selfEntity.attrInvoices[argIndex]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such invoice(argIndex = %i)." % (selfEntity.getName(), selfEntity.id, playerEntity.id, argIndex) )
			return

		srcItem = objInvoice.getSrcItem()

		if srcItem.getStackable() < argAmount:
			# 无论是否可叠加的物品，如果数量大于叠加上限则出错
			ERROR_MSG( "stackable less then sell amount" )
			return

		# 现在开始卖商品了
		if objInvoice.getMaxAmount() > 0 and argAmount > objInvoice.getAmount():	# 商品有数量限制
			playerEntity.client.onStatusMessage( csstatus.GOODS_IS_NONE_1, "" )
			ERROR_MSG( "%s(%i): %s(%i) buy %i '%s', %i only." % ( selfEntity.getName(), selfEntity.id, playerEntity.playerName, playerEntity.id, srcItem.id, argAmount, objInvoice.getAmount() ) )
			return	# 没这么多货，不卖
		
		newInvoice = objInvoice.copy()
		self.onSellItem( selfEntity, playerEntity, newInvoice, argIndex, argAmount )

	
	def sellArrayTo( self, selfEntity, playerEntity, memberDBID, argIndices, argAmountList ):
		"""
		商人把东西卖给玩家

		@param 	 selfEntity	  : NPC自身实例
		@param   playerEntity : 玩家
		@param   argIndices  : 要买的哪个商品
		@type    argIndices  : ARRAY <of> UINT16	</of>
		@param   argAmountList: 要买的数量
		@type    argAmountList: ARRAY <of> UINT16	</of>
		@return: 			无
		"""
		if playerEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
			return
			
		invoiceIDs = []
		amountList = []
		totalAmount = {}

		for argIndex, argAmount in zip(argIndices, argAmountList):
			try:
				objInvoice = selfEntity.attrInvoices[argIndex]
			except:
				ERROR_MSG( "%s(%i): srcEntityId = %i, no such invoice(argIndex = %i)." % (selfEntity.getName(), selfEntity.id, playerEntity.id, argIndex) )
				return
			# 统计各类物品的购买总数
			if argIndex in totalAmount:
				totalAmount[argIndex] += argAmount
			else:
				totalAmount[argIndex] = argAmount
			srcItem = objInvoice.getSrcItem()
			
			if srcItem.getStackable() < argAmount:
				# 无论是否可叠加的物品，如果数量大于叠加上限则出错
				ERROR_MSG( "stackable less then sell amount" )
				return

			INFO_MSG("%s try to buy %d '%s'from'%s', %d remain.it's maxAmount is %d." % ( playerEntity.getName(), totalAmount[argIndex], srcItem.name(), selfEntity.getName(), objInvoice.getAmount(), objInvoice.getMaxAmount() ) )
			if objInvoice.getMaxAmount() > 0:	# 商品有数量限制
				if objInvoice.getAmount() <= 0:
					playerEntity.client.onStatusMessage( csstatus.GOODS_IS_NONE_2, str(( srcItem.name(), )) )
#					selfEntity.sellToCB( argIndex, 0, playerEntity.id )	# 添加这句是为了通知客户端商品已被别人买光
					ERROR_MSG( "%s(%i): %s(%i) buy %i '%s', %i only." % ( selfEntity.getName(), selfEntity.id, playerEntity.playerName, playerEntity.id, srcItem.id, argAmount, objInvoice.getAmount() ) )
					return	# 没货，不卖
				elif totalAmount[argIndex] > objInvoice.getAmount():
					playerEntity.client.onStatusMessage( csstatus.GOODS_NOT_ENOUGH, str(( srcItem.name(), )) )
					ERROR_MSG( "%s(%i): %s(%i) buy %i '%s', %i only." % ( selfEntity.getName(), selfEntity.id, playerEntity.playerName, playerEntity.id, srcItem.id, argAmount, objInvoice.getAmount() ) )
					return	# 没这么多货，不卖
			invoiceID = srcItem.id
			invoiceIDs.append( invoiceID )
			amountList.append( argAmount )
		if len( invoiceIDs ) > 0:
			tong_dbID = playerEntity.tong_dbID
			playerDBID = playerEntity.databaseID
			BigWorld.globalData[ "TongManager" ].buyTongSpecialArrayFromNPC( selfEntity.base, tong_dbID, playerDBID, memberDBID, invoiceIDs, argAmountList )
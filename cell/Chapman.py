# -*- coding: gb18030 -*-

"""This module implements the Chapman for cell.
"""
# $Id: Chapman.py,v 1.33 2008-08-06 07:23:01 kebiao Exp $

import BigWorld
import NPC
from bwdebug import *
from utils import *
import ItemTypeEnum
import csstatus
import ECBExtend

class Chapman( NPC.NPC ):
	"""An Chapman class for cell.
	商人NPC

	@ivar      attrInvoices: 货物列表
	@type      attrInvoices: INVOICEITEMS
	"""

	def __init__( self ):
		NPC.NPC.__init__( self )
		self.addTimer( self.invRestoreTime, self.invRestoreTime, ECBExtend.CHAPMAIN_RESTOREINVOICE_CBID )

	def onRestoreInvoices( self, timerID, cbID ):
		"""
		恢复所有商品到最大数量

		@param timerID: 使用addTimer()方法时产生的标志，由onTimer()被触发时自动传递进来
		@type  timerID: int
		@param    cbID: 当前方法所代表的编号，同样由onTimer()被触发时自动传递进来
		@type     cbID: int
		@return: 无
		"""
		for i in self.attrInvoices.itervalues():
			i.setAmount( i.maxAmount )

	def sendInvoiceListToClient( self, srcEntityId ):
		"""
		Expose method
		提供给client的方法，向client的自己发送商品列表

		@param srcEntityId: 由于使用了<Expose/>，这个是由系统自动传递进来的，表示是哪个client上的调用
		@type  srcEntityId: int
		@return: 无
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		#if srcEntity.处于与交易相冲的其它状态中():
		#	ERROR_MSG( "sellTo(srcEntityId = %i), state mode not right, perhaps have a deceive." % (srcEntityId) )
		#	return

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		#srcEntity.设置状态为交易状态()
		clientEntity = srcEntity.clientEntity(self.id)
		clientEntity.resetInvoices( len(self.attrInvoices) )
		clientEntity.onInvoiceLengthReceive( len( self.attrInvoices ) )
		### end of getInvoiceList() mothed ###

	def requestInvoice( self, srcEntityId, startPos ):
		"""
		Expose method
		请求一批商品
		@param startPos: 商品开始位置
		@type startPos: INT16
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return
		if startPos > len( self.attrInvoices ):
			return
		minLen = min( startPos+13, len( self.attrInvoices ) )
		clientEntity = srcEntity.clientEntity( self.id )

		for i in xrange( startPos, minLen+1, 1 ):
			try:
				clientEntity.addInvoiceCB( i, self.attrInvoices[i] )
			except KeyError, errstr:
				ERROR_MSG( "%s(%i): no souch index.", errstr )
				continue

	def sellTo( self, srcEntityId, argIndex, argAmount ):
		"""
		商人把东西卖给玩家

		@param srcEntityId: 由于使用了<Expose/>，这个是由系统自动传递进来的，表示是哪个client上的调用
		@type  srcEntityId: int
		@param   argIndex: 要买的哪个商品
		@type    argIndex: UINT16
		@param   argAmount: 要买的数量
		@type    argAmount: UINT16
		@return: 			无
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		#if srcEntity.是红名():
		#	ERROR_MSG( "sellTo(srcEntityId = %i), it's a pker, here perhaps have a deceive." % (srcEntityId) )
		#	return

		self.getScript().sellTo( self, srcEntity, argIndex, argAmount )
	### end of sellTo() method ###

	def sellArrayTo( self, srcEntityId, argIndices, argAmountList ):
		"""
		商人把东西卖给玩家

		@param srcEntityId: 由于使用了<Expose/>，这个是由系统自动传递进来的，表示是哪个client上的调用
		@type  srcEntityId: int
		@param argIndices: 要买的哪个商品
		@type  argIndices: ARRAY <of> UINT16	</of>
		@param argAmountList: 要买的数量
		@type  argAmountList: ARRAY <of> UINT16	</of>
		@return: 			无
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		#if srcEntity.是红名():
		#	ERROR_MSG( "sellTo(srcEntityId = %i), it's a pker, here perhaps have a deceive." % (srcEntityId) )
		#	return
		self.getScript().sellArrayTo( self, srcEntity, argIndices, argAmountList )

	def sellToCB( self, argIndex, argAmount, playerEntityID ):
		"""
		define method
		给玩家的回调

		@param   argIndex: 要买的哪个商品
		@type    argIndex: UINT16
		@param   argAmount: 要买的数量
		@type    argAmount: UINT16
		@param	playerEntityID:	新添加的变量，用于通知客户端商品数量改变
		@type	playerEntityID:	OBJECT_ID
		"""
		try:
			objInvoice = self.attrInvoices[argIndex]
		except:
			return
		objInvoice.addAmount( -argAmount )

	def buyFrom( self, srcEntityId, argUid, argAmount ):
		"""
		商人从玩家身上收购东西

		@param srcEntityId: 由于使用了<Expose/>，这个是由系统自动传递进来的，表示是哪个client上的调用
		@type  srcEntityId: int
		@param   argUid: 要买的哪个商品
		@type    argUid: INT64
		@param   argAmount: 要买的数量
		@type    argAmount: UINT16
		@return: 			无
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		#if srcEntity.是红名():
		#	ERROR_MSG( "sellTo(srcEntityId = %i), it's a pker, here perhaps have a deceive." % (srcEntityId) )
		#	return
		self.getScript().buyFrom( self, srcEntity, argUid, argAmount )

	### end of buyFrom() method ###

	def buyArrayFrom( self, srcEntityId, argUidList, argAmountList ):
		"""
		商人从玩家身上收购大量东西；
		参数列表里的每一个元素对应一个物品所在背包、标识和数量。
		收购规则：所有物品都存在且可以卖以及卖出总价值与玩家身上金钱总和不会超过玩家允许携带的金钱总数时，允许出售，否则不允许出售。

		@param    srcEntityId: 由于使用了<Expose/>，这个是由系统自动传递进来的，表示是哪个client上的调用
		@type     srcEntityId: int
		@param  argUidList: 要买的哪个商品
		@type   argUidList: ARRAY OF INT64
		@param  argAmountList: 要买的数量
		@type   argAmountList: ARRAY OF UINT16
		@return:               无
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		#if srcEntity.是红名():
		#	ERROR_MSG( "sellTo(srcEntityId = %i), it's a pker, here perhaps have a deceive." % (srcEntityId) )
		#	return

		# 检查三个参数的长度
		if len(argUidList) != len(argAmountList):
			ERROR_MSG( "%s(%i): param length not right. argUidList = %i, argAmountList = %i" % (srcEntity.playerName, srcEntity.id,  len(argUidList), len(argAmountList)) )
			srcEntity.clientEntity( self.id ).onBuyArrayFromCB( 0 )	# 出售失败
			return
		self.getScript().buyArrayFrom( self, srcEntity, argUidList, argAmountList )

	def repairOneEquip( self, srcEntityId, kitBagID, orderID, repairLevel ):
		"""
		expose method.
		修理玩家的一个装备一次
		@param    srcEntityId: 由于使用了<Expose/>，这个是由系统自动传递进来的，表示是哪个client上的调用
		@type     srcEntityId: int
		@param    kitBagID: 背包索引
		@type     kitBagID: int
		@param    orderID: 物品索引
		@type     orderID: int
		@param    repairLevel: 修理模式
		@type     repairLevel: int
		@return   无
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		if not self.hasFlag( csdefine.ENTITY_FLAG_REPAIRER ):
			return

		if srcEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
			return

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		srcEntity.repairOneEquip( repairLevel, kitBagID, orderID, self.getRevenueRate(), self.className )

	def repairAllEquip( self, srcEntityId, repairLevel ):
		"""
		expose method.
		修理所有装备
		@param    srcEntityId: 由于使用了<Expose/>，这个是由系统自动传递进来的，表示是哪个client上的调用
		@type     srcEntityId: int
		"""
		# 要是修理NPC将"repair"置为1即可
		#if not self.query("repair"):
		#	return
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		if not self.hasFlag( csdefine.ENTITY_FLAG_REPAIRER ):
			return

		if srcEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
			return

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		srcEntity.repairAllEquip( repairLevel, self.getRevenueRate(), self.className )

	def getRevenueRate( self ):
		"""
		获得当前城市的税收比率
		"""
		if self.isJoinRevenue:
			spaceType = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			if BigWorld.globalData.has_key( spaceType + ".revenueRate" ):
				return BigWorld.globalData[ spaceType + ".revenueRate" ]
		return 0

### end of class Chapman ###


# Chapman.py

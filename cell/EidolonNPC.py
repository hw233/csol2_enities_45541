# -*- coding: gb18030 -*-

import time
import BigWorld
from bwdebug import *
import csdefine
import csconst
import csstatus
from NPC import NPC
import ECBExtend
import Math


DESTROY_DELAY_TIME = 1
GOTO_OWNER_TRY_COUNT = 5

class EidolonNPC( NPC ):
	"""
	小精灵NPC
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_EIDOLON_NPC )
		if self.ownerLevel > csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL:
			self.bornTime = int( time.time() )	# 出生时间，all_clients,会通知到各客户端
			self.lifetime = csconst.VIP_EIDOLON_LIVE_TIME
			self.addTimer( self.lifetime, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )

	def onDestroySelfTimer( self, timerID, cbID ):
		"""
		virtual method.
		删除自身
		"""
		if not self.queryTemp( "isLock", False ):	# 还没锁定那么锁定并再次启动销毁timer，避免小精灵在和玩家交互中销毁造成的问题
			self.addTimer( DESTROY_DELAY_TIME, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )
			self.setTemp( "isLock", True )
			return
		self._destroy()

	def giveControlToOwner( self ):
		"""
		Define method.
		控制权交给主人
		"""
		self.controlledBy = None
		self.controlledBy = self.baseOwner

	def clientReady( self, srcEntityID ):
		"""
		Exposed method.
		owner的客户端通知小精灵的client准备好了可以接收controlledBy了
		"""
		if srcEntityID != self.ownerID:
			return
		try:
			owner = BigWorld.entities[self.ownerID]
		except KeyError:
			self.baseOwner.cell.conjureEidolonSuccess( self.base ) # 通知主人召唤成功
		else:
			owner.conjureEidolonSuccess( self.base )

	def getOwnerID( self ):
		"""
		获得自己主人的 id
		"""
		return self.ownerID
	
	def getOwner( self ):
		if BigWorld.entities.get( self.getOwnerID() ):
			owner = BigWorld.entities[ self.getOwnerID() ]
			if owner.isReal():
				return owner
		
		return self.baseOwner.cell
		
	def gotoOwner( self ):
		"""
		for real
		"""
		self.controlledBy = None
		self.addTimer( 2.0, 0.0, ECBExtend.FLY_TO_MASTER_CB )
	
	def flyToMasterCB( self, controllerID, userData ):
		"""
		timer callback
		use arg ECBExtend.FLY_TO_MASTER_CB
		"""
		count = self.queryTemp( "gotoOwnerTryCount", 0 )
		if count >= GOTO_OWNER_TRY_COUNT:			# 尝试GOTO_OWNER_TRY_COUNT次，如果无法传送，那么销毁自身
			self.destroyEidolon()
			return
			
		self.setTemp( "gotoOwnerTryCount", count+1 )
		self.getOwner().eidolonTeleport()
		
	def teleportToOwner( self, owner, spaceID, position, direction ):
		"""
		define method
		精灵传送
		"""
		# 能在当前 cellapp 找到指定的 entity 且两个 entity 在同一个 space 里，是相同地图传送
		# 目标spaceID与当前地图的spaceID相同，是相同地图传送
		self.openVolatileInfo()
		if spaceID == self.spaceID:
			self.teleport( None, position + Math.Vector3( 0, 2, 0), direction )
		else:
			self.teleport( owner, position + Math.Vector3( 0, 2, 0), direction )
		self.giveControlToOwner()
		self.removeTemp( "gotoOwnerTryCount" )
		
	def onDestroy( self ):
		"""
		entity 销毁的时候由BigWorld.Entity自动调用
		"""
		self.baseOwner = None # 原理见pet.onDestroy
		NPC.onDestroy( self )

	def destroyEidolon( self ):
		"""
		define method
		销毁小精灵
		"""
		if self.ownerLevel > csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL:
			self.onDestroySelfTimer( 0 ,0 )
		else:
			self._destroy()

	def _destroy( self ):
		self.controlledBy = None	# 如此PlayerRole客户端才会销毁小精灵(存疑，测试一下)
		self.baseOwner.cell.onEidolonDestory()
		self.destroy()

	def doRandomWalk( self ):
		"""
		小精灵不需要随机走动，屏蔽之
		"""
		pass

	def onThink( self ):
		"""
		virtual method.
		"""
		if not self.canThink():
			return

		if self.state == csdefine.ENTITY_STATE_FIGHT:
			self.onFightAIHeartbeat_AIInterface_cpp()
		else:
			self.onNoFightAIHeartbeat()

		self.think( 1.0 )

	def changeModel( self, modelNum, modelScale ):
		"""
		Define method.
		改变模型

		@param modelNum : 模型编号
		@type modelNum : STRING
		@pram modelScale : 模型缩放倍数
		@type modelScale : FLOAT
		"""
		self.modelNumber = modelNum
		self.modelScale = modelScale

	def vipShare( self, shareVIPLevel ):
		"""
		Define method.
		设置vip共享

		@param isOpen : 是否开共享
		@type isOpen : BOOL
		"""
		self.isShare = True
		self.shareVIPLevel = shareVIPLevel

	def stopShare( self ):
		"""
		Define method.
		停止共享
		"""
		self.isShare = False
		self.shareVIPLevel = csdefine.ROLE_VIP_LEVEL_NONE

	def onOwnerVIPLevelChange( self, ownerVIPLevel ):
		"""
		Define method.
		主人的vip级别改变了

		@param ownerVIPLevel
		"""
		self.shareVIPLevel = ownerVIPLevel

	def onOwnerLeaveTeam( self ):
		"""
		Define method.
		主人离开了队伍
		"""
		self.ownerTeamID = -1

	def onOwnerJoinTeam( self, ownerTeamID ):
		"""
		Define method.
		主人加入了队伍

		@param captainID : 队伍的队长id
		"""
		self.ownerTeamID = ownerTeamID

	# --------------------------------------------------------------------------
	# 技能导师功能
	# --------------------------------------------------------------------------
	def trainPlayer( self, srcEntityId, skillID ):
		"""
		训练玩家

		@param srcEntityId: 由于使用了<Expose/>，这个是由系统自动传递进来的，表示是哪个client上的调用
		@type  srcEntityId: int
		@param     skillID: 要训练的技能
		@type      skillID: INT
		@return: 			无
		"""
		srcEntity = BigWorld.entities[srcEntityId]

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		#if not self.validLearn( srcEntity, skillID ):
		if not self.getScript().validLearn( srcEntity, skillID ):
			srcEntity.statusMessage( csstatus.LEARN_SKILL_FAIL )		# hyw
			return

		state = self.spellTarget( skillID, srcEntityId )
		if state != csstatus.SKILL_GO_ON:
			INFO_MSG( "%i: skill %i use state = %i." % ( self.id, skillID, state ) )

	def sendTrainInfoToPlayer( self, srcEntityId, researchType ):
		"""
		"""
		srcEntity = BigWorld.entities[srcEntityId]

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		srcEntity.clientEntity( self.id ).receiveTrainInfos( list( self.getScript().attrTrainInfo )	)	# attrTrainInfo declare in srcClass()


	# --------------------------------------------------------------------------
	# 商人功能
	# --------------------------------------------------------------------------
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
		clientEntity.resetInvoices( len(self.getScript().attrInvoices) )
		clientEntity.onInvoiceLengthReceive( len( self.getScript().attrInvoices ) )
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
		if startPos > len( self.getScript().attrInvoices ):
			return
		minLen = min( startPos+13, len( self.getScript().attrInvoices ) )
		clientEntity = srcEntity.clientEntity( self.id )

		for i in xrange( startPos, minLen+1, 1 ):
			try:
				clientEntity.addInvoiceCB( i, self.getScript().attrInvoices[i] )
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
			objInvoice = self.getScript().attrInvoices[argIndex]
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
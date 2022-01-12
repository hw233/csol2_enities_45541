# -*- coding: gb18030 -*-
#
# $Id:Exp $


from bwdebug import *
import csdefine
import csstatus
import time
import BigWorld
import csconst
from Resource.Rewards.RewardManager import g_rewardMgr
import ECBExtend
from ActivityRecordMgr import g_activityRecordMgr
from VehicleHelper import getCurrVehicleID
import Const

EXTRA_EXP_ITEM = 40501010	#额外经验 物品 ID
EXTRA_MONEY_ITEM = 40501011	#额外金钱 物品 ID
SAVE_BUFFID = 12010			#保护BUFF

class HorseRacer:
	"""
	"""
	def __init__( self ):
		"""
		"""
		pass

	def onBecomeRacer( self ):
		"""
		define method
		"""
		#self.lastRaceTime = time.localtime()[2]
		if BigWorld.globalData["RacehorseType"] == "sai_ma_chang_03":
			self.addFlag( csdefine.ENTITY_FLAG_CHRISTMAS_HORSE )
		self.addActivityCount( csdefine.ACTIVITY_SAI_MA )
		self.changeState( csdefine.ENTITY_STATE_RACER )
		# 移除相关加速BUFF
		self.clearBuff( [csdefine.BUFF_INTERRUPT_HORSE] )
		if not self.queryTemp( "horse_race_increase_speed", False ):
			# 记住进入赛马状态前的移动速度相关值
			self.setTemp( "horse_move_speed_value", self.move_speed_value )
			self.setTemp( "horse_move_speed_percent", self.move_speed_percent )
			self.setTemp( "horse_move_speed_extra", self.move_speed_extra )
			self.move_speed_value = 0
			self.move_speed_percent = Const.HORSE_MOVE_SPEED_PERCENT * csconst.FLOAT_ZIP_PERCENT
			self.move_speed_extra = 0
			self.calcMoveSpeed()
			self.setTemp( "horse_race_increase_speed", True )
		self.resist_in_affected = 0		# 无法闪避
		self.client.onRacehorseStart()

	def onBecomeNonRacer( self ):
		"""
		define method
		"""
		self.changeState( csdefine.ENTITY_STATE_FREE )
		self.client.onRacehorseEnd()
		self.clearBuff( [csdefine.BUFF_INTERRUPT_HORSE] )
		if self.queryTemp( "horse_race_increase_speed", False ):
			# 恢复赛马前的移动速度
			self.move_speed_value = self.popTemp( "horse_move_speed_value", 0 )
			self.move_speed_percent = self.popTemp( "horse_move_speed_percent", 0 )
			self.move_speed_extra = self.popTemp( "horse_move_speed_extra", 0 )
			self.calcMoveSpeed()
			self.removeTemp( "horse_race_increase_speed" )
		self.resist_in_affected = 1
		self.removeTemp( "pointIndexs" )
		self.removeTemp( "raceCircles" )
		if BigWorld.globalData["RacehorseType"] == "sai_ma_chang_03":
			self.removeFlag( csdefine.ENTITY_FLAG_CHRISTMAS_HORSE )


	def finishRacehorse( self ):
		self.setTemp( 'racehorseFinishFlag', True )

	def addRaceItem( self, item ):
		"""
		给赛马栏增加一个道具
		"""
		orderID = self.getFreeRaceBagOrder()
		self.raceItemsBag.add( orderID, item )
		self.client.addRaceItemCB( orderID, item )

	def removeRaceItem( self, orderID ):
		self.raceItemsBag.removeByOrder( orderID )
		self.client.onRemoveRaceItem( orderID )

	def removeAllRaceItem( self ):
		orders = [1,2,3]
		for i in orders:
			if self.getRacehorseItem(i) != None:
				self.removeRaceItem( i )

	def getFreeRaceBagOrder( self ):
		"""
		取得赛马栏空闲位置
		"""
		orders = [1,2,3]
		rl = []
		for i in self.raceItemsBag.getDatas():
			rl.append( i.getOrder() )
		for j in rl:
			assert j in orders ,"HorseRacer BagOrder's j = %i"%j
			orders.remove( j )
		if len( orders ) == 0:
			return -1
		return orders[0]

	def swapRaceItems( self, srcEntityID, srcOrder, destOrder ):
		"""
		Explore method
		交换赛马道具位置
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		self.raceItemsBag.swapOrder( srcOrder, destOrder )

		self.client.swapRaceItemCB( srcOrder, destOrder )

	def useRacehorseItem(self, srcEntityID, uid, dstEntityID ):
		"""
		Exposed method.
		对某人使用某赛马道具

		@param srcEntityID: 使用者，必须与self.id一致
		@type  srcEntityID: int32
		@param  srcKitTote: 道具栏位置
		@type   srcKitTote: UINT8
		@param      uid: 道具唯一标识符
		@type       uid: INT64
		@param dstEntityID: 目标
		@type  dstEntityID: int32
		@return:            被声明的方法，没有返回值
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return

		if srcEntityID == dstEntityID:
			dstEntity = self
		else:
			try:
				dstEntity = BigWorld.entities[dstEntityID]
			except:
				self.client.onStatusMessage( csstatus.CIB_MSG_INVALID_TARGET, "" )
				return
		if not dstEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			return

		dstItem = self.raceItemsBag.getByUid( uid )
		if dstItem is None:
			self.client.onStatusMessage( csstatus.CIB_MSG_ITEM_NOT_EXIST, "" )
			return

		if dstItem.isFrozen():
			WARNING_MSG( "error code: ", csstatus.CIB_MSG_FROZEN )
			return

		if dstItem.id in [ EXTRA_EXP_ITEM, EXTRA_MONEY_ITEM ]:
			self.removeRaceItem( dstItem.getOrder() )
			return

		if len( dstEntity.findBuffsByBuffID( SAVE_BUFFID ) ) != 0 and self.id != dstEntity.id and not dstItem.id in [ 40501009, 40501008 ]:
			self.client.onStatusMessage( csstatus.ROLE_RACE_PROTECTED, "" )
			return

		if dstItem.id == 40501009:
			dstEntity = self

		useResult = dstItem.use( self, dstEntity )
		if useResult != csstatus.SKILL_GO_ON:
			#if useResult == csstatus.SKILL_CAN_NOT_CAST_TO_SELF:
			#	self.client.onStatusMessage( csstatus.CIB_MSG_ITEM_NOT_USED )
			self.client.onStatusMessage( useResult, "" )
		return

	def getRacehorseItem( self, order ):
		"""
		"""
		return self.raceItemsBag[order]

	def hr_getByUid( self, uid ):
		"""
		根据UID 获取背包中的物品
		@type  uid : UINT32
		@param uid : 物品的UID
		@return 物品的实例，没有返回None
		"""
		return self.raceItemsBag.getByUid( uid )

	def addRaceRewards( self, place ):
		"""
		"""
		self.set( "raceHorse_place", place )
		g_rewardMgr.rewards( self, csdefine.REWARD_RACE_HORSE )

	def queryRaceItemCount( self, id ):
		"""
		"""
		count = 0
		for i in xrange(1,4):
			if self.raceItemsBag[i] != None and self.raceItemsBag[i].id == id:
				count += 1
		return count

	def waitForStart( self, startTime ):
		"""
		define method
		"""
		self.setTemp( 'horseRaceStartTime', startTime )
		#self.onBecomeRacer()
		# 如果玩家在骑宠上则先下骑宠
		if getCurrVehicleID( self ):
			self.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )

		actPet = self.pcg_getActPet()
		if actPet :														# 如果有出征宠物
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )		# 则首先回收宠物

	def onLeaveRacehorseMap( self, controllerID, userData ):
		"""
		离开赛马地图。
		"""
		self.gotoForetime()

	def addRacePointIndex( self, pointIndex, isEndPoint ):
		"""
		Define method.
		增加一个路点记录
		"""
		pointIndexs = self.queryTemp( "pointIndexs", [] )

		if pointIndex == 1:
			raceCircles = self.queryTemp( "raceCircles", 1 )
			if pointIndex in pointIndexs and len( pointIndexs ) >= ( 7 * raceCircles ):
				self.setTemp( "raceCircles", raceCircles + 1 )
				self.client.updateRaceCircle()

		if pointIndex in pointIndexs:
			return

		if len(pointIndexs) != pointIndex-1:
			return

		pointIndexs.append( pointIndex )
		self.setTemp( "pointIndexs", pointIndexs )

		if isEndPoint == True:
			self.getCurrentSpaceBase().raceWin( self.base, self.playerName, self.databaseID, self.level, self.queryTemp( "raceType", 0 ) )
			self.removeTemp( "pointIndexs" )
			self.addTimer( 5.0, 0, ECBExtend.LEAVE_RACEHORSE_MAP )
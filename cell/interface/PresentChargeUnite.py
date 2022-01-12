# -*- coding: gb18030 -*-

# $Id: PresentChargeUnite.py  hd
# 玩家领取运营活动奖励和充值元宝的模块

from bwdebug import *
import items
import csstatus
import csdefine
import sys

g_items = items.instance()

class PresentChargeUnite:
	"""
	玩家领取运营活动奖励和充值元宝的模块
	"""
	def __init__( self ):
		pass

	def pcu_takeThings( self, dataType, item_id ):
		"""
		开始领取物品或者充值,该接口是主接口，调用后就能获取领取的物品
		@type  dataType	: UINT8
		@param dataType	: 领取的类型
		@type  item_id	: ITEM_ID
		@param item_id	: 领取的物品的ID
		"""
		self.base.pcu_takeThings(dataType, item_id)

	def pcu_getPresentTypes( self ):
		"""
		到服务器请求获取玩家拥有的奖励类型
		"""
		self.base.pcu_getPresentTypes()

	def pcu_onGetPresentTypes(self, types):
		"""
		@define method
		pcu_getPresentTypes接口获取奖励类型后，该接口将收到最终结果，该结果可用于玩家领取奖励
		"""
		pass

	def takePresent( self, presentIDs ):
		"""
		@define method
		领取奖品包
		"""
		itemInstances = []
		for id in presentIDs:
			item = g_items.createDynamicItem( int( id ))
			itemInstances.append( item )
		# 先判断能否加入背包
		checkReult = self.checkItemsPlaceIntoNK_( itemInstances )
		if checkReult != csdefine.KITBAG_CAN_HOLD :
			self.base.takeOverFailed()
			self.statusMessage( csstatus.PCU_NOT_ENOUGH_GRID )
			return
		for item in itemInstances:
			self.addItem( item, csdefine.ADD_ITEM_TAKEPRESENT )

		self.base.takeOverSuccess()					#通知base清理数据

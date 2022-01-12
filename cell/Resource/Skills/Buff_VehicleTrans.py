# -*- coding: gb18030 -*-
#
# $Id: Buff_VehicleTrans.py.py,v 1.2 10:33 2010-12-21 jiangyi Exp $

"""
持续性效果
"""

import csstatus
from bwdebug import *
from Buff_Normal import Buff_Normal

class Buff_VehicleTrans( Buff_Normal ):
	"""
	example:改骑宠模型
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self.vehicleNum = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.vehicleNum = int( dict["param1"] )

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.vehicleModelNum = self.vehicleNum

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		if receiver.currVehicleData:
			itemID = receiver.currVehicleData["srcItemID"]
			item = receiver.createDynamicItem( itemID )
			receiver.vehicleModelNum = item.model()
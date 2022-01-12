# -*- coding: gb18030 -*-
#

"""
下坐骑效果edit by wuxo
"""

import csdefine
from bwdebug import *
from Buff_Normal import Buff_Normal
from VehicleHelper import getCurrVehicleID

class Buff_8008( Buff_Normal ):
	"""
	下坐骑
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 1
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		if dict[ "Param1" ] != "":
			self._p1 = int( dict[ "Param1" ])
		
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
		if self._p1 == 1:
			if getCurrVehicleID( receiver ): # 如果人在骑宠上，强制下骑宠
				receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。
		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		if self._p1 == 1:
			if getCurrVehicleID( receiver ): # 如果人在骑宠上，强制下骑宠
				receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )
		

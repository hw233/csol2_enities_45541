# -*- coding: gb18030 -*-

from bwdebug import *
from Buff_Individual import Buff_Individual
import event.EventCenter as ECenter
import BigWorld
import csstatus
from Role import PlayerRole
from ModelHelper import isInNarrowSpace
from gbref import rds

class Buff_Vehicle( Buff_Individual ):
	"""
	骑宠buff，客户端接口 by mushuang
	"""
	def __init__( self ):
		Buff_Individual.__init__( self )
		self._vehicleDBID = 0

	def __narrowSpaceHandling( self, player ):
		"""
		当在狭窄空间召唤骑宠时的相关处理逻辑
		"""
		if not isInNarrowSpace( player ):
			return

		DEBUG_MSG( "Summon vehicle in narrow space!" )

		# 在狭窄空间召唤骑宠会不成功，并提示玩家
		buffData = player.findBuffByID( self.getID() )
		if buffData:
			player.cell.requestRemoveBuff( buffData[ "index" ] )
			player.statusMessage( csstatus.SPACE_TOO_NARROW_FOR_VEHICLE )


	def cast( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff_Individual.cast( self, caster, target )
		if target != BigWorld.player():
			return
		target.vehicleDBID = self._vehicleDBID # 设定当前骑宠DBID
		DEBUG_MSG( "Setting Role.vehicleDBID to %s "%BigWorld.player().vehicleDBID )

		# 通知界面
		ECenter.fireEvent( "EVT_ON_PLAYER_UP_VEHICLE" )

		self.__narrowSpaceHandling( target )

	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""


		self._vehicleDBID = 0
		target.vehicleDBID = 0
		DEBUG_MSG( "Clear Role.vehicleDBID to 0 " )

		if target != BigWorld.player():
			return
		# 尝试捕获一个概率bug：在某些时候会出现target是Role的情况，产生原因未知。
		if isDebuged:
			assert isinstance( target, PlayerRole )

		target.updateMoveMode()		# 下马时，重新设置角色移动速度（hyw--2008.12.30）

		# 停止自动寻路
#		target.endAutoRun( False )

		# 通知界面
		ECenter.fireEvent( "EVT_ON_PLAYER_DOWN_VEHICLE" )
		target.resetCamera()
		Buff_Individual.end( self, caster, target )

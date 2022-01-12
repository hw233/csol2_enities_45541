# -*- coding: gb18030 -*-
#
# $Id: Buff_Vehicle.py,v 1.2 10:02 2010-12-21 jiangyi Exp $

"""
持续性效果
骑宠buff，此buff代表玩家骑乘的完整状态
"""

import BigWorld
import csconst
import csstatus
import csdefine
import Const
from bwdebug import *
from Buff_Individual import Buff_Individual
from VehicleHelper import getDefaultVehicleData, getVehicleModelNum, canMount,  resetVehicleSkills
from Function import newUID

class Buff_Vehicle( Buff_Individual ):
	"""
	骑乘状态buff by mushuang
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Individual.__init__( self )
		self._vehicleDBID = 0 # 当前骑宠的DBID，注意这个数据是与每个玩家相关的

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Individual.init( self, dict )

	def _onDoBegin( self, receiver, buffData ):
		"""
		此方法由Buff_Individual的doBegin调用，用于更新“玩家个性化数据”，如果在这个过程中更新了某个个性化数据，请使用：
		_packIndividualData将数据打包，否则，数据无法正确迁移。		
		"""
		self._vehicleDBID = receiver.currVehicleData[ "id" ]

		# 数据改动之后，一定将数据打包，否则玩家个性化数据无法正确迁移。
		self._packIndividualData( "_vehicleDBID", self._vehicleDBID ) # 这里传入的key值为属性名，必须保证此对象中有这个属性

	def _onDoEnd( self, receiver, buffData ):
		"""
		此方法由Buff_Individual的doEnd调用，用于更新“玩家个性化数据”，如果在这个过程中更新了某个个性化数据，请使用：
		_packIndividualData将数据打包，否则，数据无法正确迁移。
		"""
		self._vehicleDBID = 0
		# 数据改动之后，一定将数据打包，否则玩家个性化数据无法正确迁移。
		self._packIndividualData( "_vehicleDBID", self._vehicleDBID ) # 这里传入的key值为属性名，必须保证此对象中有这个属性

	def receive( self, caster, receiver ):
		"""
		用于给目标施加一个buff，所有的buff的接收都必须通过此接口，
		此接口必须判断接收者是否为realEntity，
		如果否则必须要通过receiver.receiveOnReal()接口处理。
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		casterID = caster.id if caster else 0
		if not receiver.isReal():
			receiver.receiveOnReal( casterID, self )
			return

		if not receiver.currVehicleData:
			ERROR_MSG( "Can't find vehicle data on player!" )
			return

		if canMount( receiver, receiver.currVehicleData["id"], receiver.currVehicleData["type"] ) != csstatus.SKILL_GO_ON:
			receiver.currVehicleData = getDefaultVehicleData()  # 置空当前骑宠数据
			receiver.planesAllClients( "stopActions", () )					# 停止当前动作
			return

		return Buff_Individual.receive( self, caster, receiver )

	def __conjureVehicle( self, player ):
		"""
		所有基本检查通过，基本准备工作完成，准备开始正式加载骑宠
		"""
		assert player.isReal(), "receiver must be a real entity!"
		assert player.currVehicleData, "Vehicle data needed!"

		vehicleData = player.currVehicleData
		modelNum = getVehicleModelNum( vehicleData )
		if modelNum == -1: return

		if player.vehicleModelNum != modelNum:
			player.vehicleModelNum = modelNum
		resetVehicleSkills( player, True )

	def __retractVehicle( self, player ):
		"""
		收回骑宠
		在收回骑宠之前做一些事情
		此接口用于buff取消时的回调，
		一搬玩家不会主动调用该接口
		而是直接清楚对应的buff即可
		"""
		assert player.isReal(),"player must be a real entity!"
		player.currVehicleData = getDefaultVehicleData()
		player.vehicleModelNum = 0

		
	def __addVehicleBuff( self, player ):
		"""
		将骑宠buff，加载到玩家身上
		"""
		assert player.isReal(),"player must be a real entity!"

		# 把骑宠buff加载到角色身上
		if player.currVehicleData:
			for buff in player.currVehicleData["attrBuffs"]:
				player.addBuff( buff )
				player.currentVehicleBuffIndexs.append( buff["index"] )
			player.currVehicleData["attrBuffs"] = []

	def __removeVehicleBuff( self, player ):
		"""
		从玩家身上撤销骑宠buff
		"""
		assert player.isReal(),"player must be a real entity!"

		# 把骑宠buff从角色身上卸载
		buffs = []
		for index in player.currentVehicleBuffIndexs:
			buff = player.getBuffByIndex( index )
			buffs.append(buff)
			player.removeBuffByIndex( index, [csdefine.BUFF_INTERRUPT_VEHICLE_OFF] )
		player.currentVehicleBuffIndexs = []
		if player.currVehicleData:
			player.currVehicleData["attrBuffs"] = buffs
		player.base.updateVehicleBuffs( player.currVehicleData["id"], buffs )

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
		self.__conjureVehicle( receiver )
		self.__addVehicleBuff( receiver )

		#这个过程会调用_onDoBegin，将玩家个性化数据打包，因此根据依赖关系，将其放在最后
		Buff_Individual.doBegin( self, receiver, buffData ) 

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
		Buff_Individual.doReload( self, receiver, buffData )

		self.__conjureVehicle( receiver )
		self.__addVehicleBuff( receiver )
		receiver.addC_VehicleFDTimmer()

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Individual.doEnd( self, receiver, buffData )

		self.__retractVehicle( receiver )
		self.__removeVehicleBuff( receiver )

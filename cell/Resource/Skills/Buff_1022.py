# -*- coding:gb18030 -*-

from bwdebug import *
from Buff_Individual import Buff_Individual
from VehicleHelper import getDefaultVehicleData_Attr

class Buff_1022( Buff_Individual ):
	"""
	骑宠属性加成buff
	"""
	def __init__( self ):
		"""
		"""
		Buff_Individual.__init__( self )
		self._vehicleData = {} # 当前骑宠的DBID，注意这个数据是与每个玩家相关的

	def init( self, dict ):
		"""
		"""
		Buff_Individual.init( self, dict )
		
	def _onDoBegin( self, receiver, buffData ):
		"""
		此方法由Buff_Individual的doBegin调用，用于更新“玩家个性化数据”，如果在这个过程中更新了某个个性化数据，请使用：
		_packIndividualData将数据打包，否则，数据无法正确迁移。		
		"""
		self._vehicleData = receiver.currAttrVehicleData
		# 数据改动之后，一定将数据打包，否则玩家个性化数据无法正确迁移。
		self._packIndividualData( "_vehicleData", self._vehicleData ) # 这里传入的key值为属性名，必须保证此对象中有这个属性

	def _onDoEnd( self, receiver, buffData ):
		"""
		此方法由Buff_Individual的doEnd调用，用于更新“玩家个性化数据”，如果在这个过程中更新了某个个性化数据，请使用：
		_packIndividualData将数据打包，否则，数据无法正确迁移。
		"""
		self._vehicleData = {}
		# 数据改动之后，一定将数据打包，否则玩家个性化数据无法正确迁移。
		self._packIndividualData( "_vehicleData", self._vehicleData ) # 这里传入的key值为属性名，必须保证此对象中有这个属性

	def doBegin( self, receiver, buffData ):
		"""
		"""
		Buff_Individual.doBegin( self, receiver, buffData )
		vehicleData= receiver.currAttrVehicleData
		strength   = vehicleData["strength"]
		intellect  = vehicleData["intellect"]
		dexterity  = vehicleData["dexterity"]
		corporeity = vehicleData["corporeity"]

		receiver.strength_value += strength
		receiver.intellect_value += intellect
		receiver.dexterity_value +=  dexterity
		receiver.corporeity_value +=  corporeity
		receiver.calcDynamicProperties()

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
		vehicleData= receiver.currAttrVehicleData

		#重新进行计算
		receiver.addA_VehicleFDTimmer()

		strength   = vehicleData["strength"]
		intellect  = vehicleData["intellect"]
		dexterity  = vehicleData["dexterity"]
		corporeity = vehicleData["corporeity"]

		receiver.strength_value += strength
		receiver.intellect_value += intellect
		receiver.dexterity_value +=  dexterity
		receiver.corporeity_value +=  corporeity

	def doEnd( self, receiver, buffData ):
		"""
		"""
		Buff_Individual.doEnd( self, receiver, buffData )
		vehicleData= receiver.currAttrVehicleData
		strength   = vehicleData["strength"]
		intellect  = vehicleData["intellect"]
		dexterity  = vehicleData["dexterity"]
		corporeity = vehicleData["corporeity"]

		receiver.strength_value -= strength
		receiver.intellect_value -= intellect
		receiver.dexterity_value -=  dexterity
		receiver.corporeity_value -=  corporeity
		receiver.calcDynamicProperties()
		receiver.currAttrVehicleData  = getDefaultVehicleData_Attr()

# -*- coding: gb18030 -*-

#edit by wuxo 2013-3-27


from bwdebug import *
import event.EventCenter as ECenter
from Buff_Individual import Buff_Individual
from LabelGather import labelGather

class Buff_1022( Buff_Individual ):
	"""
	骑宠属性加成buff
	"""
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Buff_Individual.__init__( self )
		self._vehicleData = {}

	def cast( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff_Individual.cast( self, caster, target )
		if target == BigWorld.player():
			target.activateVehicleID = self._vehicleData["id"] # 设定当前骑宠DBID
			ECenter.fireEvent( "EVT_ON_VEHICLE_ACTIVATED" )

	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff_Individual.end( self, caster, target )
		if target == BigWorld.player():
			target.activateVehicleID = 0
			ECenter.fireEvent( "EVT_ON_VEHICLE_UNACTIVATED", self._vehicleData["id"] )
		self._vehicleData = {}

	def getIcon( self ):
		"""
		骑宠属性加成buff图标
		"""
		player = BigWorld.player()
		if not self._vehicleData: return Buff_Individual.getIcon( self )
		srcItemID = self._vehicleData["srcItemID"]
	 	item = player.createDynamicItem( srcItemID )
	 	if item is None: return Buff_Individual.getIcon( self )
	 	return item.icon()

	def getDescription( self ):
		"""
		骑宠属性加成buff鼠标移上描述
		"""
		player = BigWorld.player()
		if not self._vehicleData: return Buff_Individual.getDescription( self )
		srcItemID = self._vehicleData["srcItemID"]
		item = player.createDynamicItem( srcItemID )
		if item is None: return Buff_Individual.getDescription( self )
		color = item.getQualityColor()
		strText = "@F{fc=" + str( color ) + "}"
		nameText = strText + item.name().split("(")[-1].split(")")[0]
		propertyText = labelGather.getText( "PetsWindow:VehiclesPanel", "propertyText" )
		strength = self._vehicleData["strength"]
		strengthText = labelGather.getText( "PetsWindow:VehiclesPanel", "strengthText", strength )
		corporeity = self._vehicleData["corporeity"]
		corporeityText = labelGather.getText( "PetsWindow:VehiclesPanel", "corporeityText", corporeity )
		dexterity = self._vehicleData["dexterity"]
		dexterityText = labelGather.getText( "PetsWindow:VehiclesPanel", "dexterityText", dexterity )
		intellect = self._vehicleData["intellect"]
		intellectText = labelGather.getText( "PetsWindow:VehiclesPanel", "intellectText", intellect )
		return nameText + propertyText + strengthText + corporeityText + dexterityText + intellectText

# -*- coding: gb18030 -*-
import BigWorld
import csdefine
import csstatus
import Const
from ItemTypeEnum import CFE_FLYING_ONLY, VEHICLE_EQUIP_LIST, FLYING_VEHICLE_EQUIP_LIST,ITEM_VEHICLE_BOOK
from config.VehicleProperty import Datas as P_DATA
from config.VehicleUpStep import Datas as U_DATA

"""
骑宠相关的一些助手函数 by mushuang
"""

def isFlying( player ):
	"""
	判断玩家是否正处于飞行状态
	"""
	assert player.isEntityType( csdefine.ENTITY_TYPE_ROLE ), "player must be a role instance!"

	return bool( player.findBuffByBuffID( csdefine.FLYING_BUFF_ID ) )


def isOnVehicle( player ):
	"""
	判断玩家是否正在骑乘状态
	"""
	assert player.isEntityType( csdefine.ENTITY_TYPE_ROLE ), "player must be a role instance!"

	return player.vehicleDBID != 0

def isOnFlyingVehicle( player ):
	"""
	判断当前骑宠是否为飞行骑宠
	"""
	assert player.isEntityType( csdefine.ENTITY_TYPE_ROLE ), "player must be a role instance!"

	# 设置这个函数为了隔离改变，目前而言上天只有一种方式——通过飞行骑宠
	# 也许以后会有其他方式上天，那么那时如果直接依赖玩家是否在飞而判断当
	# 前骑宠为飞行骑宠的方法就失效了。所以，建议所有判断当前骑宠为飞行骑
	# 都通过此方法，不要直接使用isFlying()

	return isOnVehicle( player ) and isFlying( player )

def isOnLandVehicle( player ):
	"""
	判断当前骑宠是否为陆地骑宠
	"""
	assert player.isEntityType( csdefine.ENTITY_TYPE_ROLE ), "player must be a role instance!"
	return isOnVehicle( player ) and not isFlying( player )

def isFlyingVehicleEquip( item ):
	"""
	判断某件物品是否为飞行骑宠专用
	"""
	from items.CItemBase import CItemBase
	assert isinstance( item, CItemBase ), "item must be a CItemBase instance!"

	return item.getType() in FLYING_VEHICLE_EQUIP_LIST

def isLandVehicleEquip( item ):
	"""
	判断某件物品是否为陆地骑宠专用
	"""
	from items.CItemBase import CItemBase
	assert isinstance( item, CItemBase ), "item must be a CItemBase instance!"

	return item.getType() in VEHICLE_EQUIP_LIST

def isVehicleEquip( item ):
	"""
	判断某件物品是否为骑宠装备
	"""
	from items.CItemBase import CItemBase
	assert isinstance( item, CItemBase ), "item must be a CItemBase instance!"

	return isLandVehicleEquip( item ) or isFlyingVehicleEquip( item )

def isVehicleBook( item ):
	"""
	判断某件物品是否为骑宠技能书
	"""
	from items.CItemBase import CItemBase
	assert isinstance( item, CItemBase ), "item must be a CItemBase instance!"

	return item.getType() == ITEM_VEHICLE_BOOK

def isVehicleEquipUseable( equip, player ):
	"""
	判断装备骑宠装备是否可以被装备
	与CVechicleEquip.canWield()的区别在于它返回csstatus中的相关提示信息ID而不是简单的True/False by mushuang
	"""
	from items.CVehicleEquip import CVehicleEquip
	assert isinstance( equip, CVehicleEquip ), "equip must be a CVehicleEquip instance!"

	# 是否已经召唤了骑宠
	if not isOnVehicle( player ):
		return csstatus.VEHICLE_NO_CONJURE

	# 是否为骑宠装备
	if not isVehicleEquip( equip ):
		return csstatus.VEHICLE_NO_EQUIP

	# 骑宠级别是否允许使用此骑宠装备
	if player.getVehicleLevel() < equip.getReqLevel():
		return csstatus.VEHICLE_CANT_WIELD

	# 飞行骑宠只能装备飞行骑宠的装备
	if isOnFlyingVehicle( player ) and not isFlyingVehicleEquip( equip ):
		return csstatus.CANT_WIELD_LAND_VEHICLE_EQUIP

	# 地面骑宠只能装备地面骑宠的装备
	if isOnLandVehicle( player ) and not isLandVehicleEquip( equip ):
		return csstatus.CANT_WIELD_FLYING_VEHICLE_EQUIP

	return csstatus.KIT_EQUIP_CAN_FIT_EQUIP

def isFalling( player ):
	"""
	判断玩家是否正在掉落
	"""
	assert player.isEntityType( csdefine.ENTITY_TYPE_ROLE ), "player must be a role instance!"

	return not ( player.isOnSomething() or isFlying( player ) ) and player.getJumpState() == Const.STATE_JUMP_DOWN

def getVehicleMaxStep( id ):
	"""
	获得id坐骑的最高阶次
	"""
	player = BigWorld.player()
	if not player.isEntityType( csdefine.ENTITY_TYPE_ROLE ):return 1
	vehicleData = player.vehicleDatas.get( id )
	if vehicleData is None: return 1
	return getVehicleStepBySrcID( vehicleData["srcItemID"] )
	
def getVehicleStepBySrcID( id ):
	"""
	通过坐骑srcItemID来获得坐骑可升的最高阶次
	"""
	if not P_DATA[id]["nextStepItemID"]:
		return P_DATA[id]["step"]
	else:
		return getVehicleStepBySrcID( P_DATA[id]["nextStepItemID"] )
	
def getVehicleToItemNeed( step ):
	"""
	通过阶次获得所需物品
	"""
	allItem = []
	steps = U_DATA.keys()
	steps.sort()
	for k in steps:
		allItem.append( U_DATA[step]["toItemNeedItem"] ) 
	
	if len( allItem ) >= step:
		return allItem[step-1:]
	else:
		return []
	
def getNextStepItemID( srcItemID ):
	"""
	获得下一阶次的对应ID
	"""
	if P_DATA.has_key( srcItemID ):
		return P_DATA[srcItemID]["nextStepItemID"]
	else:
		return 0
	
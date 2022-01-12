# -*- coding: gb18030 -*-
import csstatus
import csdefine
from bwdebug import *
from Resource.SkillLoader import g_skills
import items
import csconst
g_items = items.instance()

# 召唤骑宠流程中使用的一些工具函数 by mushuang

def canMount( player, id, type ):
	"""
	此接口等价于原Role上的canMount
	判断当前是否能够上坐骑
	player必须是RealEntity
	"""
	# 潜行状态下不允许召唤骑宠
	if player.effect_state & csdefine.EFFECT_STATE_PROWL:
		return csstatus.VEHICLE_NOT_SNAKE
	
	# 判断是否是观察者状态
	if player.effect_state & csdefine.EFFECT_STATE_WATCHER:
		return csstatus.VEHICLE_NOT_VEND
	
	# 判断是否有不允许骑乘标志
	if player.actionSign( csdefine.ACTION_FORBID_VEHICLE ):
		return csstatus.VEHICLE_NOT_VEND

	# 判断角色是否在舞厅中
	if player.actionSign( csdefine.ACTION_ALLOW_DANCE ):
		return csstatus.JING_WU_SHI_KE_RESTRICT_CONJURE_VEHICLE
		
	# 飞行状态下不能使用除了当前坐骑之外的任何坐骑
	if isFlying( player ):
		return csstatus.CANT_SUMMON_OTHER_VEHICLE

	# 战斗状态下不允许召唤骑宠
	if player.isState( csdefine.ENTITY_STATE_FIGHT ):
		return csstatus.VEHICLE_CONJURE_STATE_FIGHT

	# 非自由状态下不允许召唤骑宠
	if not player.isState( csdefine.ENTITY_STATE_FREE ):
		return csstatus.VEHICLE_CONJURE_NOT_STATE_FREE

	# 如果空间不能飞行则不允许召唤飞行骑宠
	spaceAllowFly = eval( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_CAN_FLY ) )
	if not spaceAllowFly and type == csdefine.VEHICLE_TYPE_FLY:
		return csstatus.FLYING_NOT_ALLOWED

	# 如果空间不能召唤骑宠则不允许召唤骑宠
	spaceAllowVehicle = eval( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_CAN_VEHICLE ) )
	if not spaceAllowVehicle:
		return csstatus.VEHICLE_NOT_ALLOWED

	# 如果玩家在水域中不允许召唤陆行骑宠
	if player.onWaterArea and type == csdefine.VEHICLE_TYPE_LAND:
		return csstatus.LAND_VEHICLE_NOT_ALLOWED_ON_WATERAREA

	return csstatus.SKILL_GO_ON


def getVehicleSkillID( vehicleData ):
	"""
	获取与当前骑宠数据绑定的技能
	"""	
	itemID = vehicleData["srcItemID"]
	item = g_items.createDynamicItem( itemID )
	if item is None:
		ERROR_MSG( "Can't create binded item, itemID: %s"%itemID )
		return -1
	
	return item.getSpellID()
	
def getVehicleModelNum( vehicleData ):
	"""
	获取骑宠的模型编号
	"""
	itemID = vehicleData["srcItemID"]
	if itemID == 0:
		INFO_MSG( "Can't create binded item!", itemID )
		return -1
	item = g_items.createDynamicItem( itemID )
	if item is None:
		ERROR_MSG( "Can't create binded item!", itemID )
		return -1 
	
	return item.model()

def getDefaultVehicleData():
	"""
	获取召唤骑宠的数据的默认表示
	"""
	vehicleData = {		"id"		: 0,
				"srcItemID" 	: 0,
				"fullDegree"    : 0,
				"type"          : 0,
				"skPoint" 	: 0,
				"deadTime" 	: 0,
				"attrSkillBox" 	: [],
				"attrBuffs"	: [],
					}
	return vehicleData
	
def getDefaultVehicleData_Attr():
	"""
	获取激活骑宠的数据的默认表示
	"""
	vehicleData = {	"id"      	: 0,
			"srcItemID" : 0,
			"level"		: 1,
			"exp"		: 0,
			"deadTime"	: 0,
			"fullDegree"	: 0,
			"type"		: 0,
			"strength"	: 0,
			"intellect"	: 0,
			"dexterity"	: 0,
			"corporeity"	: 0,
			}
	return vehicleData

def resetVehicleSkills( player, callOrNot ):
	"""
	重新加载/卸载骑宠技能
	@param callOrNot 是召唤骑宠还是下骑宠
	@param callOrNot bool
	"""

	skillList = getCurrVehicleSkillIDs( player )
	for skillID in skillList:
		if not g_skills.has( skillID ):
			WARNING_MSG( "Skills(%i) does not exist!" % skillID )
			continue
		skill = g_skills[skillID]
		if callOrNot:
			skill.attach( player )
		else:
			skill.detach( player )

	actPet = player.pcg_getActPet()
	if actPet:
		vehicleJoyancyEffect = player.queryTemp( "vehicleJoyancyEffect", 0.0 )
		if callOrNot:
			actPet.entity.onVehicleAddSkills( skillList, vehicleJoyancyEffect )
		else:
			actPet.entity.onVehicleRemoveSkills( skillList, vehicleJoyancyEffect )
			
def getCurrVehicleID( player ):
	"""
	获取当前召唤骑宠ID
	"""
	if player.currVehicleData is None: return 0
	return player.currVehicleData["id"]

def getCurrAttrVehicleID( player ):
	"""
	获取当前激活骑宠ID
	"""
	if player.currAttrVehicleData is None: return 0
	return player.currAttrVehicleData["id"]
	
def getCurrVehicleSkillIDs( player ):
	"""
	获取当前召唤骑宠skillID列表
	"""
	if player.currVehicleData is None: return []
	return player.currVehicleData["attrSkillBox"]
	
def isFlying( player ):
	"""
	判断玩家是否在飞行
	"""
	buffData = player.findBuffByBuffID( csdefine.FLYING_BUFF_ID )
	
	return bool( buffData )

def isOnLandVehicle( player ):
	"""
	判断玩家是否在陆地骑宠状态
	"""
	buffData = player.findBuffByBuffID( csdefine.VEHICLE_BUFF_ID )
	
	return bool( buffData )
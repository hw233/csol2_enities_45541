# -*- coding: gb18030 -*-
#
# $Id: VisibleRule.py,v 1.11 2014-05-08 zzh Exp $

"""
模型显示规则
"""
import csdefine
import Define
import BigWorld
from gbref import rds

def queryVisibleStateByPlaneID( entity ):
	"""
	适应对象 所有
	"""
	visibleType = Define.MODEL_VISIBLE_TYPE_TRUE
	if not entity.isSameClientPlanes():
		visibleType = Define.MODEL_VISIBLE_TYPE_FALSE
	return visibleType		

def queryVisibleStateByFlag( entity ):
	"""
	根据标志位获取模型显示方式
	适用对象NPCObject

	"""
	visibleType = Define.MODEL_VISIBLE_TYPE_TRUE
	if entity.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):
		if entity.isOwnerVisible():
			visibleType = Define.MODEL_VISIBLE_TYPE_TRUE
		else:
			visibleType = Define.MODEL_VISIBLE_TYPE_FALSE
	return visibleType
				
def queryVisibleStateByFlash( entity ):
	"""
	闪屏中是否显示模型检查
	战斗实体
	"""
	visibleType = Define.MODEL_VISIBLE_TYPE_TRUE
	if hasattr( entity, "isshowModel" ) and not entity.isshowModel():
		visibleType = Define.MODEL_VISIBLE_TYPE_FALSE
	return visibleType
	
def queryVisibleStateByTelAndTest( entity ):
	"""
	传送保护状态和测试状态不显示模型
	适用对象 Pet,Role
	"""
	visibleType = Define.MODEL_VISIBLE_TYPE_TRUE
	if entity.state in [ csdefine.ENTITY_STATE_PENDING, csdefine.ENTITY_STATE_QUIZ_GAME ]:
			visibleType = Define.MODEL_VISIBLE_TYPE_FALSE
	return visibleType

def queryVisibleStateByShowSelf( entity ):
	"""
	适用对象 战斗实体
	"""
	visibleType = Define.MODEL_VISIBLE_TYPE_TRUE
	if not entity.isShowSelf:
		visibleType = Define.MODEL_VISIBLE_TYPE_FALSE
	return visibleType		
	
def queryVisibleStateBySetting1( entity ):
	"""
	适应对象Role
	"""
	type = Define.MODEL_VISIBLE_TYPE_TRUE 
	player = BigWorld.player()
	isTeamMember = player.isTeamMember( entity.id )
	if isTeamMember:
			if rds.viewInfoMgr.getSetting( "teammate", "model" ):
				type = Define.MODEL_VISIBLE_TYPE_TRUE
			else:
				type = Define.MODEL_VISIBLE_TYPE_FBUTBILL
			if  not player.isRolesAndUIVisible :
				type = Define.MODEL_VISIBLE_TYPE_FALSE
	else:
		visible = player.isRolesVisible
		roleUIVisible = player.isRolesAndUIVisible
		visible &= rds.viewInfoMgr.getSetting( "role", "model" )
		if visible and roleUIVisible:
			type = Define.MODEL_VISIBLE_TYPE_TRUE
		else:
			if not roleUIVisible :
				type = Define.MODEL_VISIBLE_TYPE_FALSE
			else:
				type = Define.MODEL_VISIBLE_TYPE_FBUTBILL
	return type
	
def queryVisibleStateBySetting2( entity ):
	"""
	配置检查
	适用对象 Pet
	"""
	player = BigWorld.player()
	owner = entity.getOwner()
	if owner and player.isTeamMember( owner.id ):
		isTeamMember = True
	else:
		isTeamMember = False
		
	visibleType = Define.MODEL_VISIBLE_TYPE_TRUE
	
	rolesVisible = player.isRolesVisible
	if isTeamMember:
		# 读取界面设置中队友宠物模型的显示设置
		if not rds.viewInfoMgr.getSetting( "teammatePet", "model" ):
			visibleType = Define.MODEL_VISIBLE_TYPE_FBUTBILL
	else:
		rolesVisible &= rds.viewInfoMgr.getSetting( "pet", "model" )
		roleUIVisible = player.isRolesAndUIVisible
		if rolesVisible and roleUIVisible:
			visibleType = Define.MODEL_VISIBLE_TYPE_TRUE
		else:
			if not roleUIVisible :
				visibleType = Define.MODEL_VISIBLE_TYPE_FALSE
			else:
				visibleType = Define.MODEL_VISIBLE_TYPE_FBUTBILL
	return visibleType
	
def queryVisibleStateByWatchState( entity ):
	"""
	观察者模型检查
	适用对象PlayerRole,Role
	"""
	type = Define.MODEL_VISIBLE_TYPE_TRUE
	if entity.effect_state & csdefine.EFFECT_STATE_WATCHER:
		if entity.id == BigWorld.player().id:
			type = Define.MODEL_VISIBLE_TYPE_SNEAK
		else:
			type = Define.MODEL_VISIBLE_TYPE_FALSE
	return type		
			
def queryVisibleStateByProwl1( entity ):
	"""
	潜行状态检查
	适用对象PlayerRole,ownPet
	"""
	type = Define.MODEL_VISIBLE_TYPE_TRUE
	if entity.effect_state & csdefine.EFFECT_STATE_PROWL:
		type = Define.MODEL_VISIBLE_TYPE_SNEAK
	return type
	
def queryVisibleStateByProwl2( entity ):
	"""
	潜行状态检查
	适用对象 Role
	"""
	type = Define.MODEL_VISIBLE_TYPE_TRUE 
	player = BigWorld.player()
	isTeamMember = player.isTeamMember( entity.id )
	# 潜行状态下
	if entity.effect_state & csdefine.EFFECT_STATE_PROWL:
		if isTeamMember:			
			type = Define.MODEL_VISIBLE_TYPE_SNEAK
		else:
			if entity.isSnake:
				type = Define.MODEL_VISIBLE_TYPE_FALSE
			else:
				type = Define.MODEL_VISIBLE_TYPE_SNEAK
		
	return type
	
def queryVisibleStateByProwl3( entity ):
	"""
	潜行状态检查
	适用对象 Pet
	"""
	player = BigWorld.player()
	owner = entity.getOwner()
	if owner and player.isTeamMember( owner.id ):
		isTeamMember = True
	else:
		isTeamMember = False
	visibleType = Define.MODEL_VISIBLE_TYPE_TRUE
	if entity.effect_state & csdefine.EFFECT_STATE_PROWL:
		if isTeamMember:							
			visibleType = Define.MODEL_VISIBLE_TYPE_SNEAK
			
		else:
			if entity.isSnake:
				visibleType = Define.MODEL_VISIBLE_TYPE_FALSE
			else:
				visibleType = Define.MODEL_VISIBLE_TYPE_SNEAK
	
	return visibleType
	
g_visibleRules = {	
		csdefine.VISIBLE_RULE_BY_PLANEID:queryVisibleStateByPlaneID,				#位面ID
		csdefine.VISIBLE_RULE_BY_FLAG:queryVisibleStateByFlag,					#标识位
		csdefine.VISIBLE_RULE_BY_FLASH:queryVisibleStateByFlash,				#闪屏
		csdefine.VISIBLE_RULE_BY_TEL_AND_TEST:queryVisibleStateByTelAndTest,	#传送状态和测试状态
		csdefine.VISIBLE_RULE_BY_SHOW_SELF:queryVisibleStateByShowSelf,			#是否显示自己属性检查
		csdefine.VISIBLE_RULE_BY_SETTING_1:queryVisibleStateBySetting1,			#Role用户配置		
		csdefine.VISIBLE_RULE_BY_SETTING_2:queryVisibleStateBySetting2,			#pet用户配置
		csdefine.VISIBLE_RULE_BY_WATCH:queryVisibleStateByWatchState,			#观察者模型
		csdefine.VISIBLE_RULE_BY_PROWL_1:queryVisibleStateByProwl1,				#PlayerRole,ownPet潜行模式
		csdefine.VISIBLE_RULE_BY_PROWL_2:queryVisibleStateByProwl2,				#Role潜行模式
		csdefine.VISIBLE_RULE_BY_PROWL_3:queryVisibleStateByProwl3,				#pet潜行模式
				
				}
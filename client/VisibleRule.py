# -*- coding: gb18030 -*-
#
# $Id: VisibleRule.py,v 1.11 2014-05-08 zzh Exp $

"""
ģ����ʾ����
"""
import csdefine
import Define
import BigWorld
from gbref import rds

def queryVisibleStateByPlaneID( entity ):
	"""
	��Ӧ���� ����
	"""
	visibleType = Define.MODEL_VISIBLE_TYPE_TRUE
	if not entity.isSameClientPlanes():
		visibleType = Define.MODEL_VISIBLE_TYPE_FALSE
	return visibleType		

def queryVisibleStateByFlag( entity ):
	"""
	���ݱ�־λ��ȡģ����ʾ��ʽ
	���ö���NPCObject

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
	�������Ƿ���ʾģ�ͼ��
	ս��ʵ��
	"""
	visibleType = Define.MODEL_VISIBLE_TYPE_TRUE
	if hasattr( entity, "isshowModel" ) and not entity.isshowModel():
		visibleType = Define.MODEL_VISIBLE_TYPE_FALSE
	return visibleType
	
def queryVisibleStateByTelAndTest( entity ):
	"""
	���ͱ���״̬�Ͳ���״̬����ʾģ��
	���ö��� Pet,Role
	"""
	visibleType = Define.MODEL_VISIBLE_TYPE_TRUE
	if entity.state in [ csdefine.ENTITY_STATE_PENDING, csdefine.ENTITY_STATE_QUIZ_GAME ]:
			visibleType = Define.MODEL_VISIBLE_TYPE_FALSE
	return visibleType

def queryVisibleStateByShowSelf( entity ):
	"""
	���ö��� ս��ʵ��
	"""
	visibleType = Define.MODEL_VISIBLE_TYPE_TRUE
	if not entity.isShowSelf:
		visibleType = Define.MODEL_VISIBLE_TYPE_FALSE
	return visibleType		
	
def queryVisibleStateBySetting1( entity ):
	"""
	��Ӧ����Role
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
	���ü��
	���ö��� Pet
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
		# ��ȡ���������ж��ѳ���ģ�͵���ʾ����
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
	�۲���ģ�ͼ��
	���ö���PlayerRole,Role
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
	Ǳ��״̬���
	���ö���PlayerRole,ownPet
	"""
	type = Define.MODEL_VISIBLE_TYPE_TRUE
	if entity.effect_state & csdefine.EFFECT_STATE_PROWL:
		type = Define.MODEL_VISIBLE_TYPE_SNEAK
	return type
	
def queryVisibleStateByProwl2( entity ):
	"""
	Ǳ��״̬���
	���ö��� Role
	"""
	type = Define.MODEL_VISIBLE_TYPE_TRUE 
	player = BigWorld.player()
	isTeamMember = player.isTeamMember( entity.id )
	# Ǳ��״̬��
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
	Ǳ��״̬���
	���ö��� Pet
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
		csdefine.VISIBLE_RULE_BY_PLANEID:queryVisibleStateByPlaneID,				#λ��ID
		csdefine.VISIBLE_RULE_BY_FLAG:queryVisibleStateByFlag,					#��ʶλ
		csdefine.VISIBLE_RULE_BY_FLASH:queryVisibleStateByFlash,				#����
		csdefine.VISIBLE_RULE_BY_TEL_AND_TEST:queryVisibleStateByTelAndTest,	#����״̬�Ͳ���״̬
		csdefine.VISIBLE_RULE_BY_SHOW_SELF:queryVisibleStateByShowSelf,			#�Ƿ���ʾ�Լ����Լ��
		csdefine.VISIBLE_RULE_BY_SETTING_1:queryVisibleStateBySetting1,			#Role�û�����		
		csdefine.VISIBLE_RULE_BY_SETTING_2:queryVisibleStateBySetting2,			#pet�û�����
		csdefine.VISIBLE_RULE_BY_WATCH:queryVisibleStateByWatchState,			#�۲���ģ��
		csdefine.VISIBLE_RULE_BY_PROWL_1:queryVisibleStateByProwl1,				#PlayerRole,ownPetǱ��ģʽ
		csdefine.VISIBLE_RULE_BY_PROWL_2:queryVisibleStateByProwl2,				#RoleǱ��ģʽ
		csdefine.VISIBLE_RULE_BY_PROWL_3:queryVisibleStateByProwl3,				#petǱ��ģʽ
				
				}
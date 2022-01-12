# -*- coding: gb18030 -*-
import csstatus
import csdefine
from bwdebug import *
from Resource.SkillLoader import g_skills
import items
import csconst
g_items = items.instance()

# �ٻ����������ʹ�õ�һЩ���ߺ��� by mushuang

def canMount( player, id, type ):
	"""
	�˽ӿڵȼ���ԭRole�ϵ�canMount
	�жϵ�ǰ�Ƿ��ܹ�������
	player������RealEntity
	"""
	# Ǳ��״̬�²������ٻ����
	if player.effect_state & csdefine.EFFECT_STATE_PROWL:
		return csstatus.VEHICLE_NOT_SNAKE
	
	# �ж��Ƿ��ǹ۲���״̬
	if player.effect_state & csdefine.EFFECT_STATE_WATCHER:
		return csstatus.VEHICLE_NOT_VEND
	
	# �ж��Ƿ��в�������˱�־
	if player.actionSign( csdefine.ACTION_FORBID_VEHICLE ):
		return csstatus.VEHICLE_NOT_VEND

	# �жϽ�ɫ�Ƿ���������
	if player.actionSign( csdefine.ACTION_ALLOW_DANCE ):
		return csstatus.JING_WU_SHI_KE_RESTRICT_CONJURE_VEHICLE
		
	# ����״̬�²���ʹ�ó��˵�ǰ����֮����κ�����
	if isFlying( player ):
		return csstatus.CANT_SUMMON_OTHER_VEHICLE

	# ս��״̬�²������ٻ����
	if player.isState( csdefine.ENTITY_STATE_FIGHT ):
		return csstatus.VEHICLE_CONJURE_STATE_FIGHT

	# ������״̬�²������ٻ����
	if not player.isState( csdefine.ENTITY_STATE_FREE ):
		return csstatus.VEHICLE_CONJURE_NOT_STATE_FREE

	# ����ռ䲻�ܷ����������ٻ��������
	spaceAllowFly = eval( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_CAN_FLY ) )
	if not spaceAllowFly and type == csdefine.VEHICLE_TYPE_FLY:
		return csstatus.FLYING_NOT_ALLOWED

	# ����ռ䲻���ٻ�����������ٻ����
	spaceAllowVehicle = eval( BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_CAN_VEHICLE ) )
	if not spaceAllowVehicle:
		return csstatus.VEHICLE_NOT_ALLOWED

	# ��������ˮ���в������ٻ�½�����
	if player.onWaterArea and type == csdefine.VEHICLE_TYPE_LAND:
		return csstatus.LAND_VEHICLE_NOT_ALLOWED_ON_WATERAREA

	return csstatus.SKILL_GO_ON


def getVehicleSkillID( vehicleData ):
	"""
	��ȡ�뵱ǰ������ݰ󶨵ļ���
	"""	
	itemID = vehicleData["srcItemID"]
	item = g_items.createDynamicItem( itemID )
	if item is None:
		ERROR_MSG( "Can't create binded item, itemID: %s"%itemID )
		return -1
	
	return item.getSpellID()
	
def getVehicleModelNum( vehicleData ):
	"""
	��ȡ����ģ�ͱ��
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
	��ȡ�ٻ��������ݵ�Ĭ�ϱ�ʾ
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
	��ȡ�����������ݵ�Ĭ�ϱ�ʾ
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
	���¼���/ж����輼��
	@param callOrNot ���ٻ���軹�������
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
	��ȡ��ǰ�ٻ����ID
	"""
	if player.currVehicleData is None: return 0
	return player.currVehicleData["id"]

def getCurrAttrVehicleID( player ):
	"""
	��ȡ��ǰ�������ID
	"""
	if player.currAttrVehicleData is None: return 0
	return player.currAttrVehicleData["id"]
	
def getCurrVehicleSkillIDs( player ):
	"""
	��ȡ��ǰ�ٻ����skillID�б�
	"""
	if player.currVehicleData is None: return []
	return player.currVehicleData["attrSkillBox"]
	
def isFlying( player ):
	"""
	�ж�����Ƿ��ڷ���
	"""
	buffData = player.findBuffByBuffID( csdefine.FLYING_BUFF_ID )
	
	return bool( buffData )

def isOnLandVehicle( player ):
	"""
	�ж�����Ƿ���½�����״̬
	"""
	buffData = player.findBuffByBuffID( csdefine.VEHICLE_BUFF_ID )
	
	return bool( buffData )
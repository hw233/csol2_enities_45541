# -*- coding: gb18030 -*-
import BigWorld
import csdefine
import csstatus
import Const
from ItemTypeEnum import CFE_FLYING_ONLY, VEHICLE_EQUIP_LIST, FLYING_VEHICLE_EQUIP_LIST,ITEM_VEHICLE_BOOK
from config.VehicleProperty import Datas as P_DATA
from config.VehicleUpStep import Datas as U_DATA

"""
�����ص�һЩ���ֺ��� by mushuang
"""

def isFlying( player ):
	"""
	�ж�����Ƿ������ڷ���״̬
	"""
	assert player.isEntityType( csdefine.ENTITY_TYPE_ROLE ), "player must be a role instance!"

	return bool( player.findBuffByBuffID( csdefine.FLYING_BUFF_ID ) )


def isOnVehicle( player ):
	"""
	�ж�����Ƿ��������״̬
	"""
	assert player.isEntityType( csdefine.ENTITY_TYPE_ROLE ), "player must be a role instance!"

	return player.vehicleDBID != 0

def isOnFlyingVehicle( player ):
	"""
	�жϵ�ǰ����Ƿ�Ϊ�������
	"""
	assert player.isEntityType( csdefine.ENTITY_TYPE_ROLE ), "player must be a role instance!"

	# �����������Ϊ�˸���ı䣬Ŀǰ��������ֻ��һ�ַ�ʽ����ͨ���������
	# Ҳ���Ժ����������ʽ���죬��ô��ʱ���ֱ����������Ƿ��ڷɶ��жϵ�
	# ǰ���Ϊ�������ķ�����ʧЧ�ˡ����ԣ����������жϵ�ǰ���Ϊ������
	# ��ͨ���˷�������Ҫֱ��ʹ��isFlying()

	return isOnVehicle( player ) and isFlying( player )

def isOnLandVehicle( player ):
	"""
	�жϵ�ǰ����Ƿ�Ϊ½�����
	"""
	assert player.isEntityType( csdefine.ENTITY_TYPE_ROLE ), "player must be a role instance!"
	return isOnVehicle( player ) and not isFlying( player )

def isFlyingVehicleEquip( item ):
	"""
	�ж�ĳ����Ʒ�Ƿ�Ϊ�������ר��
	"""
	from items.CItemBase import CItemBase
	assert isinstance( item, CItemBase ), "item must be a CItemBase instance!"

	return item.getType() in FLYING_VEHICLE_EQUIP_LIST

def isLandVehicleEquip( item ):
	"""
	�ж�ĳ����Ʒ�Ƿ�Ϊ½�����ר��
	"""
	from items.CItemBase import CItemBase
	assert isinstance( item, CItemBase ), "item must be a CItemBase instance!"

	return item.getType() in VEHICLE_EQUIP_LIST

def isVehicleEquip( item ):
	"""
	�ж�ĳ����Ʒ�Ƿ�Ϊ���װ��
	"""
	from items.CItemBase import CItemBase
	assert isinstance( item, CItemBase ), "item must be a CItemBase instance!"

	return isLandVehicleEquip( item ) or isFlyingVehicleEquip( item )

def isVehicleBook( item ):
	"""
	�ж�ĳ����Ʒ�Ƿ�Ϊ��輼����
	"""
	from items.CItemBase import CItemBase
	assert isinstance( item, CItemBase ), "item must be a CItemBase instance!"

	return item.getType() == ITEM_VEHICLE_BOOK

def isVehicleEquipUseable( equip, player ):
	"""
	�ж�װ�����װ���Ƿ���Ա�װ��
	��CVechicleEquip.canWield()����������������csstatus�е������ʾ��ϢID�����Ǽ򵥵�True/False by mushuang
	"""
	from items.CVehicleEquip import CVehicleEquip
	assert isinstance( equip, CVehicleEquip ), "equip must be a CVehicleEquip instance!"

	# �Ƿ��Ѿ��ٻ������
	if not isOnVehicle( player ):
		return csstatus.VEHICLE_NO_CONJURE

	# �Ƿ�Ϊ���װ��
	if not isVehicleEquip( equip ):
		return csstatus.VEHICLE_NO_EQUIP

	# ��輶���Ƿ�����ʹ�ô����װ��
	if player.getVehicleLevel() < equip.getReqLevel():
		return csstatus.VEHICLE_CANT_WIELD

	# �������ֻ��װ����������װ��
	if isOnFlyingVehicle( player ) and not isFlyingVehicleEquip( equip ):
		return csstatus.CANT_WIELD_LAND_VEHICLE_EQUIP

	# �������ֻ��װ����������װ��
	if isOnLandVehicle( player ) and not isLandVehicleEquip( equip ):
		return csstatus.CANT_WIELD_FLYING_VEHICLE_EQUIP

	return csstatus.KIT_EQUIP_CAN_FIT_EQUIP

def isFalling( player ):
	"""
	�ж�����Ƿ����ڵ���
	"""
	assert player.isEntityType( csdefine.ENTITY_TYPE_ROLE ), "player must be a role instance!"

	return not ( player.isOnSomething() or isFlying( player ) ) and player.getJumpState() == Const.STATE_JUMP_DOWN

def getVehicleMaxStep( id ):
	"""
	���id�������߽״�
	"""
	player = BigWorld.player()
	if not player.isEntityType( csdefine.ENTITY_TYPE_ROLE ):return 1
	vehicleData = player.vehicleDatas.get( id )
	if vehicleData is None: return 1
	return getVehicleStepBySrcID( vehicleData["srcItemID"] )
	
def getVehicleStepBySrcID( id ):
	"""
	ͨ������srcItemID����������������߽״�
	"""
	if not P_DATA[id]["nextStepItemID"]:
		return P_DATA[id]["step"]
	else:
		return getVehicleStepBySrcID( P_DATA[id]["nextStepItemID"] )
	
def getVehicleToItemNeed( step ):
	"""
	ͨ���״λ��������Ʒ
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
	�����һ�״εĶ�ӦID
	"""
	if P_DATA.has_key( srcItemID ):
		return P_DATA[srcItemID]["nextStepItemID"]
	else:
		return 0
	
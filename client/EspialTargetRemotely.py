# -*- coding: gb18030 -*-
#

import event.EventCenter as ECenter
import BigWorld
from ItemsFactory import ObjectItem as ItemInfo
import csdefine

class EspialTargetRemotely:
	"""
	Զ�̹۲�Է���ģ�飬��Ҫ����������ݺͽ��ܴ������ݵ�����
	"""
	_instance = None
	def __init__ ( self ):
		self.roleModel = ""
		
	def queryRoleEquip( self, queryName ):
		"""
		��������Զ�̲�ѯ��ҵ�װ��ģ��
		@param   queryName: Ҫ��ѯ���������
		@type	 queryName: str
		"""
		BigWorld.player().queryRoleEquip( queryName )
		
	def onQueryRoleEquip( self, roleName, raceclass, roleLevel, tongName, roleModel, equips ):
		"""
		Զ�̲�ѯ���װ���ص�
		@param		equips: װ���б�
		@type		equips: list
		"""
		self.roleModel = roleModel
		ECenter.fireEvent( "EVT_ON_SHOW_TARGET_REMOTELY" )
		#װ��		
		itemInfos = []
		for item in equips:
			itemInfo = ItemInfo( item )
			itemInfos.append( itemInfo )
		ECenter.fireEvent( "EVT_ON_ROLE_SHOW_TARGET_EQUIP_REMOTELY", itemInfos )		#֪ͨ������ʾ���װ��
		#������Ϣ
		otherInfo = {}
		otherInfo["Name"] = roleName
		otherInfo["Level"] = roleLevel
		otherInfo["Pclass"] = raceclass & csdefine.RCMASK_CLASS
		otherInfo["TongName"] = tongName
		ECenter.fireEvent( "EVT_ON_ROLE_SHOW_TARGET_TFINFO_REMOTELY", otherInfo )
		#ģ��
		
		roleModelInfo = {}
		roleModelInfo["roleID"] = roleModel["roleID"]
		roleModelInfo["roleName"] = roleName
		roleModelInfo["level"] = roleLevel
		roleModelInfo["raceclass"] = raceclass
		roleModelInfo[ "hairNumber" ] = roleModel["hairNumber"]
		roleModelInfo[ "faceNumber" ] = roleModel["faceNumber"]
		roleModelInfo[ "bodyFDict" ] = roleModel["bodyFDict"]
		roleModelInfo[ "volaFDict" ] = roleModel["volaFDict"]
		roleModelInfo[ "breechFDict" ] = roleModel["breechFDict"]
		roleModelInfo[ "feetFDict" ] = roleModel["feetFDict"]
		roleModelInfo[ "lefthandFDict" ] = roleModel["lefthandFDict"]
		roleModelInfo[ "righthandFDict" ] = roleModel["righthandFDict"]
		roleModelInfo[ "talismanNum" ] = roleModel["talismanNum"]
		roleModelInfo[ "fashionNum" ] = roleModel["fashionNum"]
		roleModelInfo[ "adornNum" ] = roleModel["adornNum"]
		roleModelInfo["headTextureID"] = ""
		ECenter.fireEvent( "EVT_ON_ROLE_SHWO_TARGET_MODEL_REMOTELY", roleModelInfo )
			
	@staticmethod
	def instance():
		"""
		��ȡģ���ʵ��
		"""
		if EspialTargetRemotely._instance is None:
			EspialTargetRemotely._instance = EspialTargetRemotely()
		return EspialTargetRemotely._instance

def instance():
	return EspialTargetRemotely.instance()

espialRemotely = EspialTargetRemotely.instance()
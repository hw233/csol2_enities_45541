# -*- coding: gb18030 -*-
#

import event.EventCenter as ECenter
import BigWorld
from ItemsFactory import ObjectItem as ItemInfo
import csdefine

class EspialTargetRemotely:
	"""
	远程观察对方的模块，主要完成请求数据和接受处理数据的任务
	"""
	_instance = None
	def __init__ ( self ):
		self.roleModel = ""
		
	def queryRoleEquip( self, queryName ):
		"""
		根据名字远程查询玩家的装备模型
		@param   queryName: 要查询的玩家名字
		@type	 queryName: str
		"""
		BigWorld.player().queryRoleEquip( queryName )
		
	def onQueryRoleEquip( self, roleName, raceclass, roleLevel, tongName, roleModel, equips ):
		"""
		远程查询玩家装备回调
		@param		equips: 装备列表
		@type		equips: list
		"""
		self.roleModel = roleModel
		ECenter.fireEvent( "EVT_ON_SHOW_TARGET_REMOTELY" )
		#装备		
		itemInfos = []
		for item in equips:
			itemInfo = ItemInfo( item )
			itemInfos.append( itemInfo )
		ECenter.fireEvent( "EVT_ON_ROLE_SHOW_TARGET_EQUIP_REMOTELY", itemInfos )		#通知界面显示玩家装备
		#其他信息
		otherInfo = {}
		otherInfo["Name"] = roleName
		otherInfo["Level"] = roleLevel
		otherInfo["Pclass"] = raceclass & csdefine.RCMASK_CLASS
		otherInfo["TongName"] = tongName
		ECenter.fireEvent( "EVT_ON_ROLE_SHOW_TARGET_TFINFO_REMOTELY", otherInfo )
		#模型
		
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
		获取模块的实例
		"""
		if EspialTargetRemotely._instance is None:
			EspialTargetRemotely._instance = EspialTargetRemotely()
		return EspialTargetRemotely._instance

def instance():
	return EspialTargetRemotely.instance()

espialRemotely = EspialTargetRemotely.instance()
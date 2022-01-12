# -*- coding: gb18030 -*-

from CItemBase import CItemBase
import csstatus
import CooldownFlyweight
from VehicleHelper import getCurrVehicleID

g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()

class CVehicleBook( CItemBase ):
	"""
	骑宠技能书
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def checkUse( self, owner ):
		"""
		检测使用者是否能使用该物品 该物品能否被使用取决于骑宠的等级，所以需要单独重载

		@param owner: 背包拥有者
		@type  owner: Entity
		@return: STATE CODE
		@rtype:  UINT16
		"""
		# 判断物品受影响的CD有没有过

		if getCurrVehicleID( owner ) == 0:
			return csstatus.LEARN_SKILL_MUST_CALL_VEHICLE

		isLifeType = self.getLifeType()
		hasLifeTime = self.getLifeTime()
		if isLifeType and not hasLifeTime:
			return csstatus.CIB_MSG_ITEM_NO_USE_TIME

		if not self.query( "spell", 0 ):
			return csstatus.CIB_MSG_ITEM_NOT_USED

		limitCD = self.query( "limitCD", [] )
		for cd in limitCD:
			timeVal = owner.getCooldown( cd )
			if not g_cooldowns[ cd ].isTimeout( timeVal ):
				return csstatus.SKILL_ITEM_NOT_READY

		return csstatus.SKILL_GO_ON

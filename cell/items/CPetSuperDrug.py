# -*- coding: gb18030 -*-

from CSuperDrug import CSuperDrug
import csstatus
import CooldownFlyweight
g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()

class CPetSuperDrug( CSuperDrug ):
	"""
	宠物消耗品
	"""
	def __init__( self, srcData ):
		"""
		"""
		CSuperDrug.__init__( self, srcData )

	def checkUse( self, owner ):
		"""
		virtual method.
		"""
		actPet = owner.pcg_getActPet()
		if actPet is None:
			return csstatus.SKILL_PET_NO_CONJURED

		if actPet.entity.level < self.getReqLevel():
			return csstatus.SKILL_PET_NEED_LEVEL

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
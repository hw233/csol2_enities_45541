# -*- coding: gb18030 -*-

from CItemBase import CItemBase
import csstatus
import CooldownFlyweight
g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()

class CMenuscriptPet( CItemBase ):
	"""
	宠物蛋
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def checkUse( self, owner ):
		"""
		virtual method.
		"""
		if owner.pcg_isFull():
			return csstatus.PET_CATCH_FAIL_OVERRUN

		if owner.level < self.getReqLevel():
			return csstatus.PET_LEVEL_CANT_FIT

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
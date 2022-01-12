# -*- coding: gb18030 -*-

from CItemBase import CItemBase
import csstatus
import CooldownFlyweight
from VehicleHelper import getCurrVehicleID

g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()

class CVehicleBook( CItemBase ):
	"""
	��輼����
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def checkUse( self, owner ):
		"""
		���ʹ�����Ƿ���ʹ�ø���Ʒ ����Ʒ�ܷ�ʹ��ȡ�������ĵȼ���������Ҫ��������

		@param owner: ����ӵ����
		@type  owner: Entity
		@return: STATE CODE
		@rtype:  UINT16
		"""
		# �ж���Ʒ��Ӱ���CD��û�й�

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

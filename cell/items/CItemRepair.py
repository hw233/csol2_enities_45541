# -*- coding: gb18030 -*-

import csdefine
import csstatus
from CItemBase import CItemBase

class CItemRepair( CItemBase ):
	"""
	����װ������Ʒ
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )
		
	def use( self, owner, target ):
		"""
		ʹ�ú�����ȫװ��
		"""
		equips = target.getItems( csdefine.KB_EQUIP_ID )
		needRep = False
		for equip in equips:
			hardMax = equip.getHardinessLimit()
			if hardMax == 0:
				continue
			hardNow = equip.getHardiness()
			if hardNow < hardMax - 1000:
				needRep = True
				break
		if needRep:
			target.repairAllEquip( csdefine.EQUIP_REPAIR_ITEM, 0, 0 )
			ud = self.getUseDegree()
			if ud > 0:
				ud -= 1
				self.setUseDegree( ud, owner )
			if ud <=0:
				owner.removeItem_( self.getOrder(), 1, csdefine.DELETE_ITEM_USE )
			return csstatus.SKILL_GO_ON
		else:
			return csstatus.EQUIP_REPAIR_ALL_MAX
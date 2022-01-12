# -*- coding: gb18030 -*-

from bwdebug import *
import csconst
import csdefine
import csstatus
from CItemBase import CItemBase

class CItemGainPotential( CItemBase ):
	"""
	获得潜能物品
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )
		
	def use( self, owner, target ):
		"""
		使用物品直接获得潜能
		"""
		potentialVal = self.query( "param1", 0 )
		pottem = csconst.ROLE_POTENTIAL_UPPER - target.potential
		gained = 0
		if pottem < potentialVal:
			if not target.addPotential( pottem, csdefine.CHANGE_POTENTIAL_USE_ITEM_2 ):
				return  csconst.SKILL_STATE_TO_ITEM_STATE
			gained = potentialVal - pottem
			self.set( "param1", gained, owner )
		else:
			if not target.addPotential( potentialVal, csdefine.CHANGE_POTENTIAL_USE_ITEM_2 ):
				return  csconst.SKILL_STATE_TO_ITEM_STATE
			gained = potentialVal
			self.set( "param1", 0 )
			owner.removeItem_( self.getOrder(), 1, csdefine.DELETE_ITEM_USE )
		INFO_MSG( "%s use gain potential item,gain:%d,itemUID:%d."%( owner.getName(), gained, self.getUid() ) )
		return csstatus.SKILL_GO_ON
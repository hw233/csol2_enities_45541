# -*- coding: gb18030 -*-

import csdefine
import csstatus
from CItemBase import CItemBase

class CItemAFTime( CItemBase ):
	"""
	自动战斗充值时间物品(司辰沙漏)
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )
		
	def use( self, owner, target ):
		"""
		充值额外自动战斗时间
		"""
		timeAdd = int( self.query( "param1", 0 ) )
		target.base.autoFightExtraTimeCharge( timeAdd )
		ud = self.getUseDegree()
		if ud > 0:
			ud -= 1
			self.setUseDegree( ud, owner )
		if ud <=0:
			owner.removeItem_( self.getOrder(), 1, csdefine.DELETE_ITEM_USE )
		return csstatus.SKILL_GO_ON
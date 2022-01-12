# -*- coding: gb18030 -*-
import BigWorld

from QuestBox import QuestBox
import ECBExtend

from bwdebug import *
import csstatus


class YeZhanFengQiBox( QuestBox ) :
	"""
	用于凤栖战场掉落积分箱子
	"""
	def __init__( self ) :
		QuestBox.__init__( self )
	
	def onItemsArrived( self, caster, itemList ):
		"""
		define method
		"""
		id = self.queryTemp( "gossipingID", 0 )
		if id != 0 and BigWorld.entities.has_key( id ):
			caster.client.onStatusMessage( csstatus.ITEM_CANNOT_TOUCH, "" )
			return
			
		self.setTemp( "gossipingID", caster.id )
		self.getCurrentSpaceBase().cell.onRolePickBox( caster.base )
		self.addTimer( 0.5, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )

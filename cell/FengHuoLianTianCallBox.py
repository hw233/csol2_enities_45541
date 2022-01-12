# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.6 2008-01-08 06:25:59 yangkai Exp $

from NPCObject import NPCObject
from interface.CombatUnit import CombatUnit
import BigWorld
import csdefine
import ECBExtend
from bwdebug import *
import csstatus
from QuestBox import QuestBox

class FengHuoLianTianCallBox( QuestBox ) :
	"""
	"""

	def __init__( self ) :
		QuestBox.__init__( self )
		#self.setEntityType( csdefine.ENTITY_TYPE_QUEST_BOX )


	def onItemsArrived( self, caster, itemList ):
		"""
		define method
		"""
		id = self.queryTemp( "gossipingID", 0 )
		if id != 0 and BigWorld.entities.has_key( id ):
			caster.client.onStatusMessage( csstatus.ITEM_CANNOT_TOUCH, "" )
			return
			
		self.setTemp( "gossipingID", caster.id )
		self.getCurrentSpaceBase().cell.addTongCallBox( caster.tong_dbID, 1 )
		self.addTimer( 0.5, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )


	
# FengHuoLianTianCallBox.py

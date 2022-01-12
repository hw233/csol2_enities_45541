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

INTEGRAL = 10

class FengHuoLianTianIntegrationBox( QuestBox ) :
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
		caster = BigWorld.entities.get( caster.id, None)
		if caster is None:
			return
		if caster.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = caster.getOwner()
			if owner.etype == "MAILBOX" :
				return csdefine.RELATION_FRIEND
			caster = owner.entity
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			self.getCurrentSpaceBase().cell.addTongFengHuoLianTianIntegral( caster.tong_dbID, INTEGRAL )
			self.addTimer( 0.5, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )


	
# FengHuoLianTianIntegrationBox.py

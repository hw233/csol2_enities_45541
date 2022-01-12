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
import cschannel_msgs
from QuestBox import QuestBox
import time

class FengHuoLianTianBattleFlag( QuestBox ) :
	"""
	"""

	def __init__( self ) :
		QuestBox.__init__( self )
		self.ownTongDBID = 0
		self.lastTime = time.time()
		self.setEntityType( csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_BATTLE_FLAG )


	def onItemsArrived( self, caster, itemList ):
		"""
		define method
		"""
		id = self.queryTemp( "gossipingID", 0 )
		if id != 0 and caster.tong_dbID == id:
			caster.client.onStatusMessage( csstatus.ITEM_CANNOT_TOUCH, "" )
			return
			
		self.setTemp( "gossipingID", caster.tong_dbID )
		self.onReceiveSpell( caster, None )
		caster = BigWorld.entities.get( caster.id, None)
		if caster is None:
			return
			
		if caster.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = caster.getOwner()
			if owner.etype == "MAILBOX" :
				return
			caster = owner.entity
			
		if self.ownTongDBID == caster.tong_dbID:
			return
			
		if self.ownTongDBID == 0:
			self.getCurrentSpaceBase().cell.addIntegralTimer( caster.tong_dbID, int(time.time() - self.lastTime), 1 )
		else:
			self.getCurrentSpaceBase().cell.addIntegralTimer( caster.tong_dbID, 2*(int( time.time() - self.lastTime )), 0 )
		self.setName( caster.tongName )
		#self.say( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_FLAG_SAY%( caster.tongName, caster.tongName ))
		self.getCurrentSpaceBase().cell.noticePlayers( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_FLAG_IS_TAKING% caster.tongName, [] )
		self.ownTongDBID = caster.tong_dbID
		self.lastTime = time.time()
		self.getCurrentSpaceBase().cell.addTongFengHuoLianTianIntegral( caster.tong_dbID, 1 )
		#self.addTimer( 0.5, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )

	def abandonBoxQuestItems( self, srcEntityID ):
		"""
		Exposed method
		"""
		pass


	
# FengHuoLianTianBattleFlag.py

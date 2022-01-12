# -*- coding: gb18030 -*-
#

from NPCObject import NPCObject
from interface.CombatUnit import CombatUnit
from csconst import g_camp_info
import BigWorld
import csdefine
import ECBExtend
from bwdebug import *
import csstatus
import Const
import cschannel_msgs
from QuestBox import QuestBox
import time

class CampFengHuoBattleFlag( QuestBox ) :
	"""
	"""

	def __init__( self ) :
		QuestBox.__init__( self )
		self.ownCamp = 0
		self.lastTime = time.time()
		self.setEntityType( csdefine.ENTITY_TYPE_CAMP_FENG_HUO_BATTLE_FLAG )


	def onItemsArrived( self, caster, itemList ):
		"""
		define method
		"""
		id = self.queryTemp( "gossipingID", 0 )
		if id != 0 and caster.getCamp() == id:
			caster.client.onStatusMessage( csstatus.ITEM_CANNOT_TOUCH, "" )
			return
			
		self.setTemp( "gossipingID", caster.getCamp() )
		self.onReceiveSpell( caster, None )
		caster = BigWorld.entities.get( caster.id, None)
		if caster is None:
			return
			
		if caster.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = caster.getOwner()
			if owner.etype == "MAILBOX" :
				return
			caster = owner.entity
			
		if self.ownCamp == caster.getCamp():
			return
			
		if self.ownCamp == 0:
			self.getCurrentSpaceBase().cell.addIntegralTimer( caster.getCamp(), int(time.time() - self.lastTime), 1 )
		else:
			self.getCurrentSpaceBase().cell.addIntegralTimer( caster.getCamp(), 2*(int( time.time() - self.lastTime )), 0 )
		campName = ""
		camp = caster.getCamp()
		if camp in [ csdefine.ENTITY_CAMP_TAOISM, csdefine.ENTITY_CAMP_DEMON ]:
			campName = g_camp_info[ camp ]
		self.setName( campName )
		#self.say( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_FLAG_SAY%( caster.tongName, caster.tongName ))
		self.getCurrentSpaceBase().cell.noticePlayers( cschannel_msgs.CAMP_FENG_HUO_FLAG_IS_TAKING% ( campName, campName ), [] )
		self.ownCamp = caster.getCamp()
		self.lastTime = time.time()
		self.getCurrentSpaceBase().cell.addCampFengHuoLianTianIntegral( caster.getCamp(), 1 )
		#self.addTimer( 0.5, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )

	def abandonBoxQuestItems( self, srcEntityID ):
		"""
		Exposed method
		"""
		pass


	
# CampFengHuoBattleFlag.py

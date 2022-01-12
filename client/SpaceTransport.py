# -*- coding: gb18030 -*-
import BigWorld
from utils import *
from bwdebug import *
import GUIFacade
from NPCObject import NPCObject
from gbref import rds
import Define

class SpaceTransport( NPCObject ):
	def __init__( self ):
		NPCObject.__init__( self )
		self.inTransport = False

	# This method is called when the entity enters the world
	# Any of our properties may have changed underneath us,
	#  so we do most of the entity setup here
	def enterWorld( self ):
		if (self.model == None):
			self.model = rds.effectMgr.createModel( ["particles/gxcone.model"] )
			rds.effectMgr.createParticleBG( self.model, "HP_root", "particles/chuansongmen/chuansongmen.xml", type = Define.TYPE_PARTICLE_NPC )

		self.transportTrapID = self.addTrapExt(self.range, self.onTransport )

	# This method is called when the entity leaves the world
	def leaveWorld( self ):
		self.delTrap( self.transportTrapID )

	def onTransport( self, entitiesInTrap ):
		player = BigWorld.player()
		#DEBUG_MSG( entitiesInTrap )
		INFO_MSG("===== enter Transport" )
		if not self.inTransport and player in entitiesInTrap:
			# 玩家进入传送门
			GUIFacade.gossipHello( self )
			self.inTransport = True
			INFO_MSG("===== in Transport" )

		# 玩家离开传送门
		if self.inTransport and not player in entitiesInTrap:
			self.onEndGossip()
			self.inTransport = False
			INFO_MSG("===== out Transport" )

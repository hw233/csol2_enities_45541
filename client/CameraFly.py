# -*- coding: gb18030 -*-

import BigWorld
import Pixie
from interface.GameObject import GameObject
import csdefine
from gbref import rds
import Define
import event.EventCenter as ECenter
import keys

"""
触发摄像机飞翔entity
"""
class CameraFly( GameObject ) :
	def __init__( self ) :
		GameObject.__init__( self )
		self.utype = csdefine.ENTITY_TYPE_MISC
		self.trapID = None
		self.isPlay = False
		self.isReady = False
		self.setSelectable( False )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def prerequisites( self ):
		"""
		This method is called before the entity enter the world
		"""
		return [ "particles/gxcone.model"]

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if not self.inWorld:
			return
		self.model = BigWorld.Model( "particles/gxcone.model" )
		self.trapID = BigWorld.addPot( self.matrix, 3.0, self.onTrap )
		GameObject.onCacheCompleted( self )

	def leaveWorld( self ):
		"""
		This method is called when the entity leaves the world
		"""
		GameObject.leaveWorld( self )
		if self.trapID is not None:
			self.onTrap( 0, 1 )
			BigWorld.delPot( self.trapID )
			self.trapID = None
		
	def setTrapState(self,state):
		"""
		设置陷阱的触发状态 可触发/不可触发 by wuxo
		"""
		self.isReady = state

	def onTrap( self, enteredTrap, handle ):
		"""
		"""
		if enteredTrap and not self.isPlay and self.isReady:
			self.isPlay = True
			BigWorld.player().startFly( self.eventID )

# -*- coding: gb18030 -*-
#
# $Id: SpaceDoor.py,v 1.18 2008-04-01 05:39:06 zhangyuxing Exp $

import BigWorld
import csdefine
from utils import *
from bwdebug import *
from interface.GameObject import GameObject
from gbref import rds
import event.EventCenter as ECenter
import time

class SpaceDoor( GameObject ):
	def __init__( self ):
		GameObject.__init__( self )
		self.inDoor = False
		
		self.setSelectable( True )
		self.canShowDescript = False
		self.destSpace = ""
		self.destPosition = ( 0, 0, 0 )
		
	# This method is called when the entity enters the world
	# Any of our properties may have changed underneath us,
	#  so we do most of the entity setup here
	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if not self.inWorld:
			return
		
		rds.npcModel.createDynamicModelBG( self.modelNumber,  self.__onModelLoad )
		if self.useRectangle:
			width, height, long = self.volume
			self.transportTrapID = self.addBoxTrapExt( self.pitch, self.yaw, self.roll, width, height, long, self.onTransport )
		else:
			self.transportTrapID = self.addTrapExt(self.radius, self.onTransport )

	def __onModelLoad( self, model ):
		if not self.inWorld : return  # 如果已不在视野则过滤
		self.setModel( model )
		self.model.motors = ()
		if self.yaw == 0.0:
			self.model.yaw = 1.0		# 原来默认为3.14，如果不设置为1.0，那么缩放模型时只往一边缩放，暂时搞不清楚
		else:
			self.model.yaw = self.yaw
		self.model.scale = ( self.modelScale, self.modelScale, 1.0 )

	# This method is called when the entity leaves the world
	def leaveWorld( self ):
		try:
			self.delTrap( self.transportTrapID )
		except ValueError, errstr:
			# this will throw error "ValueError: py_delTrap: No such trap."
			# 也许在entity离开space的时候，我们根本就不需要调用delTrap()。
			pass

	def onTransport( self, entitiesInTrap ):
		player = BigWorld.player()
		#DEBUG_MSG( entitiesInTrap )
		if not self.inDoor and player in entitiesInTrap:
			#INFO_MSG( "%i --> in trap, tell to cell." % self.id )
			if player.vehicle:
				player.vehicle.disMountEntity( player )
				BigWorld.callback( 2.0, self.onLeaveDartWhenEnterDoor )
				return
			player.beforeEnterDoor()
			#player.stopMove()
			self.cell.enterDoor()
			self.inDoor = True

		if self.inDoor and not player in entitiesInTrap:
			self.inDoor = False

	def onLeaveDartWhenEnterDoor( self ):
		"""
		"""
		player = BigWorld.player()
		player.beforeEnterDoor()
		self.cell.enterDoor()
		self.inDoor = True


	# Becoming a target
	def onTargetFocus( self ):
		self.canShowDescript = True
		if self.destSpace != "":
			ECenter.fireEvent( "EVT_ON_SHOW_RESUME", self )
			GameObject.onTargetFocus( self )
		else:
			self.cell.requestDestination()
		if rds.ruisMgr.isMouseHitScreen() :
			rds.ccursor.set( "transport" )

	# Quitting as target
	def onTargetBlur( self ):
		self.canShowDescript = False
		ECenter.fireEvent( "EVT_ON_HIDE_RESUME" )
		GameObject.onTargetBlur( self )
		rds.ccursor.set( "normal" )
		
	def onTargetClick( self, player ):
		BigWorld.player().pursueEntity(  self, 0.1 )

	def receiverDestination( self, destSpace, destPosition ):
		"""
		Define method.
		@param destSpace : 空间名，例如："fengming"
		@type destSpace : STRING
		@param destSpace : 目标位置
		@type destSpace : POSITION
		"""
		self.destSpace = destSpace
		self.destPosition = destPosition
		if self.canShowDescript:
			ECenter.fireEvent( "EVT_ON_SHOW_RESUME", self )
		
	def getDstSpaceLabel( self ):
		"""
		获得目标地图名，例如:"fengming"
		"""
		return self.destSpace
		
	def getDstPosition( self ):
		"""
		获得目的地坐标，
		
		rType : vector3
		"""
		return self.destPosition
		
# SpaceDoor.py

# -*- coding:gb18030 -*-

from SpaceMultiLine import SpaceMultiLine
from bwdebug import *

class SpaceCopyFishingJoy( SpaceMultiLine ):
	def __init__( self ):
		SpaceMultiLine.__init__( self )
		self.fishingPostionList = self.getScript().getFishingPositionList()
		self.positionState = [0] * len( self.fishingPostionList )				# 可优化为位模式表示位置使用情况
		
		self.positionState[0] = self.params["firstPlayerID"]		# 创建者会出现在第一个位置。
		self.playerMBList = []
		
	def assignFishingPosition( self, playerID ):
		for index, value in enumerate( self.positionState ):
			if value == 0:
				self.positionState[index] = playerID
				return self.fishingPostionList[index]
		ERROR_MSG( "player( %i ) enter.position is full,player more than postion." % playerID )
		return ( 0, 0, 0 )
		
	def freeFishingPosition( self, playerID ):
		index = self.positionState.index( playerID )
		self.positionState[index] = 0
		
	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		玩家进入了空间
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 玩家onEnter时的一些额外参数
		@type params: py_dict
		"""
		SpaceMultiLine.onEnter( self, baseMailbox, params )
		index = self.positionState.index( baseMailbox.id )
		baseMailbox.client.fish_enterSpace( baseMailbox.id, index )
		for playerMB in self.playerMBList:
			playerMB.client.fish_enterSpace( baseMailbox.id, index )
			baseMailbox.client.fish_enterSpace( playerMB.id, self.positionState.index( playerMB.id ) )
		self.playerMBList.append( baseMailbox )
		
	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		玩家离开空间
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 玩家onLeave时的一些额外参数
		@type params: py_dict
		"""
		index = self.positionState.index( baseMailbox.id )
		self.positionState[index] = 0
		mb = None
		for playerMB in self.playerMBList:
			playerMB.client.fish_leaveSpace( baseMailbox.id )
			if playerMB.id == baseMailbox.id:
				mb = playerMB
		self.playerMBList.remove( mb )
		SpaceMultiLine.onLeave( self, baseMailbox, params )
		
	def teleportEntity( self, position, direction, baseMailbox ):
		"""
		define method.
		传送一个entity到指定的space中
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数；
		@type params : PY_DICT = None
		"""
		position = self.assignFishingPosition( baseMailbox.id )
		DEBUG_MSG( "player( %i ) change postion to %s" % ( baseMailbox.id, str(position) ) )
		self.pushPlayerToEnterList( position, direction, baseMailbox )
		
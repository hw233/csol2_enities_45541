# -*- coding:gb18030 -*-

from SpaceDomainMultiLine import SpaceDomainMultiLine
from bwdebug import *

class SpaceDomainFishGround( SpaceDomainMultiLine ):
	def __init__( self ):
		SpaceDomainMultiLine.__init__( self )
		
	def findFreeSpace( self ):
		"""
		Virtual method.
		寻找一个空闲的副本，返回副本编号。
		
		"""
		if self.maxLine <= 0 or len( self._spacePlayerAmountLog ) <= 0:
			return 1

		# 寻找未满承载量的副本
		for spaceEnterID, playerAmount in self._spacePlayerAmountLog.iteritems():
			if playerAmount < self.newLineByPlayerAmount:
				return spaceEnterID

		# 如果还有副本未开， 则开启它
		if self.getCurrentCopyCount() < self.maxLine:
			enterIDlist = self._spaceNumber2EnterID.values()
			for i in xrange( 1, self.maxLine + 1 ):
				if not i in enterIDlist:
					return i

		return -1
		
	def createMultiLineSpaceItem( self ):
		pass
		
	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		define method.
		传送一个entity到指定的space中
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
		@type params : PY_DICT = None
		"""
		DEBUG_MSG( "params:%s" % params )
		if not params.has_key( "lineNumber" ):
			params[ "lineNumber" ] = self.findFreeSpace()
		
		if params[ "lineNumber" ] == -1:
			INFO_MSG( "fishing joy space is full of player,player( %s ) cant enter." % params["playerName"] )
			return
		
		if params[ "currSpaceClassName" ] == self.name and params[ "lineNumber" ] == params[ "currSpaceLineNumber" ]:
			params[ "ignoreFullRule" ] = True

		del params[ "currSpaceClassName" ]
		del params[ "currSpaceLineNumber" ]

		if not params.has_key( "ignoreFullRule" ) and \
			self.getSpacePlayerAmount( params[ "lineNumber" ] ) >= self.maxPlayerAmount:
			baseMailbox.client.onStatusMessage( csstatus.ACCOUNT_SELECT_SPACE_IS_FULL, "" )
			return

		spaceItem = self.findSpaceItem( params, True )
		if spaceItem.isEmpty():						# 进入一个新的空间需要把玩家创建在第一个捕鱼位，这个空间也需要得知此信息。
			spaceItem.params["firstPlayerID"] = baseMailbox.id
			position = self.getScript().getFirstFishingPosition()
			DEBUG_MSG( "player( %i ) goto empty space." % baseMailbox.id )
		pickData = self.pickToSpaceData( baseMailbox, params )
		spaceItem.enter( baseMailbox, position, direction, pickData )
		
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		重新登录直接返回到上一次登陆的地方
		"""
		baseMailbox.logonSpaceInSpaceCopy()
		
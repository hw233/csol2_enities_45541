# -*- coding: gb18030 -*-
#
# $Id: SpaceDomainCityWar.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

"""
Space domain class
"""

import time
import Language
import BigWorld
from bwdebug import *
import Function
from SpaceDomainCopy import SpaceDomainCopy
import csdefine

MAX_PLAYER = 250

# 领域类
class SpaceDomainFirstMap(SpaceDomainCopy):
	"""
	新手村副本域
	"""
	def __init__( self ):
		SpaceDomainCopy.__init__(self)
		self._spacePlayerAmountLog = {}					# 包含每个space的人数
		self._spaceNumber2EnterID = {}
		self.firstSpace = None
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
		BigWorld.globalData[ "SpaceDomain_FirstMap" ] = self
		self.addTimer( 60, 60, 9999 )
		self.addTimer( 1.0, 0, 9998 )

	def findFreeSpace( self ):
		"""
		寻找一个相对空闲的副本 返回副本编号
		"""
		if self.maxCopy <= 0 or len( self._spacePlayerAmountLog ) <= 0:
			DEBUG_MSG( "->A select 1 %s" % ( self._spacePlayerAmountLog ) )
			return 1;

		# 寻找未满50承载量的副本
		for spaceEnterID, playerAmount in self._spacePlayerAmountLog.iteritems():
			if playerAmount < 50:
				DEBUG_MSG( "->B select %d %s" % ( spaceEnterID, self._spacePlayerAmountLog ) )
				return spaceEnterID

		# 如果还有副本未开， 则开启它
		if self.getCurrentCopyCount() < self.maxCopy:
			enterIDlist = self._spaceNumber2EnterID.values()
			for i in xrange( 1, self.maxCopy + 1 ):
				if not i in enterIDlist:
					DEBUG_MSG( "->C select %d %s" % ( i, self._spacePlayerAmountLog ) )
					return i

		# 所有副本都开了，那么寻找人数最少的第一个副本
		sitems = self._spacePlayerAmountLog.items()
		enterID, playerAmountMin = sitems[0]
		for spaceEnterID, playerAmount in sitems:
			if playerAmount < playerAmountMin:
				enterID = spaceEnterID
				playerAmountMin = playerAmount

		DEBUG_MSG( "->D select %d %s" % ( enterID, self._spacePlayerAmountLog ) )
		return enterID

	def getSpacePlayerAmount( self, spaceNumber ):
		"""
		获得该副本的人数
		"""
		return self._spacePlayerAmountLog.get( spaceNumber, 0 )

	def incPlayerAmount( self, spaceNumber ):
		"""
		define method.
		增加该副本的人数
		"""
		enterID = self._spaceNumber2EnterID[ spaceNumber ]
		if enterID in self._spacePlayerAmountLog:
			self._spacePlayerAmountLog[ enterID ] += 1
		else:
			self._spacePlayerAmountLog[ enterID ] = 1

		DEBUG_MSG( "spaceNumber:%i, enterID:%i, spaceNumber2EnterID:%s, spacePlayerAmountLog:%s" % \
		( spaceNumber, enterID, self._spaceNumber2EnterID, self._spacePlayerAmountLog ) )

	def decPlayerAmount( self, spaceNumber ):
		"""
		define method.
		减少该副本的人数
		"""
		try:
			self._spacePlayerAmountLog[ self._spaceNumber2EnterID[ spaceNumber ] ] -= 1
		except:
			DEBUG_MSG( "decPlayerAmount[%i]:spacePlayerAmountLog=%s, spaceNumber2EnterID=%s" % \
				( spaceNumber, self._spacePlayerAmountLog, self._spaceNumber2EnterID ) )

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
		if not params.has_key( "spaceKey" ):
			params[ "spaceKey" ] = 1

		if self.getSpacePlayerAmount( params[ "spaceKey" ] ) >= MAX_PLAYER:
			baseMailbox.client.onStatusMessage( csstatus.ACCOUNT_SELECT_SPACE_IS_FULL, "" )
			return

		spaceItem = self.findSpaceItem( params, True )
		pickData = self.pickToSpaceData( baseMailbox, params )
		spaceItem.enter( baseMailbox, position, direction, pickData )

	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT = None
		"""
		enterID = self.findFreeSpace()
		params[ "spaceKey" ] = enterID

		if self.getSpacePlayerAmount( enterID ) >= MAX_PLAYER:
			baseMailbox.client.onStatusMessage( csstatus.ACCOUNT_SELECT_SPACE_IS_FULL_ON_LOGIN, "" )
			return

		spaceItem = self.findSpaceItem( params, True )
		spaceItem.logon( baseMailbox )

	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if cbID == 9999:
			DEBUG_MSG( "xinshoucun:%s" % self._spacePlayerAmountLog )
		elif cbID == 9998:
			self.firstSpace = self.findSpaceItem( { 'dbID' : 1 }, True )
			self.firstSpace.createBase( self.onFirstSpaceCreateBaseCallback )

	def onFirstSpaceCreateBaseCallback( self, spaceBase ):
		"""
		"""
		self.firstSpace.createCell()
		
	def createSpaceItem( self, params ):
		# 创建一个新的space item		
		spaceItem = SpaceDomainCopy.createSpaceItem( self, params )
		enterID = params["spaceKey"]
		self._spaceNumber2EnterID[ spaceItem.spaceNumber ] = enterID

		return spaceItem
#
# $Log: not supported by cvs2svn $
#
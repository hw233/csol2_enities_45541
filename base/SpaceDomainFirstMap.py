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

# ������
class SpaceDomainFirstMap(SpaceDomainCopy):
	"""
	���ִ帱����
	"""
	def __init__( self ):
		SpaceDomainCopy.__init__(self)
		self._spacePlayerAmountLog = {}					# ����ÿ��space������
		self._spaceNumber2EnterID = {}
		self.firstSpace = None
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
		BigWorld.globalData[ "SpaceDomain_FirstMap" ] = self
		self.addTimer( 60, 60, 9999 )
		self.addTimer( 1.0, 0, 9998 )

	def findFreeSpace( self ):
		"""
		Ѱ��һ����Կ��еĸ��� ���ظ������
		"""
		if self.maxCopy <= 0 or len( self._spacePlayerAmountLog ) <= 0:
			DEBUG_MSG( "->A select 1 %s" % ( self._spacePlayerAmountLog ) )
			return 1;

		# Ѱ��δ��50�������ĸ���
		for spaceEnterID, playerAmount in self._spacePlayerAmountLog.iteritems():
			if playerAmount < 50:
				DEBUG_MSG( "->B select %d %s" % ( spaceEnterID, self._spacePlayerAmountLog ) )
				return spaceEnterID

		# ������и���δ���� ������
		if self.getCurrentCopyCount() < self.maxCopy:
			enterIDlist = self._spaceNumber2EnterID.values()
			for i in xrange( 1, self.maxCopy + 1 ):
				if not i in enterIDlist:
					DEBUG_MSG( "->C select %d %s" % ( i, self._spacePlayerAmountLog ) )
					return i

		# ���и��������ˣ���ôѰ���������ٵĵ�һ������
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
		��øø���������
		"""
		return self._spacePlayerAmountLog.get( spaceNumber, 0 )

	def incPlayerAmount( self, spaceNumber ):
		"""
		define method.
		���Ӹø���������
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
		���ٸø���������
		"""
		try:
			self._spacePlayerAmountLog[ self._spaceNumber2EnterID[ spaceNumber ] ] -= 1
		except:
			DEBUG_MSG( "decPlayerAmount[%i]:spacePlayerAmountLog=%s, spaceNumber2EnterID=%s" % \
				( spaceNumber, self._spacePlayerAmountLog, self._spaceNumber2EnterID ) )

	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		define method.
		����һ��entity��ָ����space��
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		@param params: һЩ���ڸ�entity����space�Ķ�������� (domain����)
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
		��������µ�¼��ʱ�򱻵��ã������������ָ����space�г��֣�һ�������Ϊ���������ߵĵ�ͼ����
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		@param params: һЩ���ڸ�entity����space�Ķ��������(domain����)
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
		# ����һ���µ�space item		
		spaceItem = SpaceDomainCopy.createSpaceItem( self, params )
		enterID = params["spaceKey"]
		self._spaceNumber2EnterID[ spaceItem.spaceNumber ] = enterID

		return spaceItem
#
# $Log: not supported by cvs2svn $
#
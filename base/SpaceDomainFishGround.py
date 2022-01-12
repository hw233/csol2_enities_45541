# -*- coding:gb18030 -*-

from SpaceDomainMultiLine import SpaceDomainMultiLine
from bwdebug import *

class SpaceDomainFishGround( SpaceDomainMultiLine ):
	def __init__( self ):
		SpaceDomainMultiLine.__init__( self )
		
	def findFreeSpace( self ):
		"""
		Virtual method.
		Ѱ��һ�����еĸ��������ظ�����š�
		
		"""
		if self.maxLine <= 0 or len( self._spacePlayerAmountLog ) <= 0:
			return 1

		# Ѱ��δ���������ĸ���
		for spaceEnterID, playerAmount in self._spacePlayerAmountLog.iteritems():
			if playerAmount < self.newLineByPlayerAmount:
				return spaceEnterID

		# ������и���δ���� ������
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
		����һ��entity��ָ����space��
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		@param params: һЩ���ڸ�entity����space�Ķ�������� (domain����)
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
		if spaceItem.isEmpty():						# ����һ���µĿռ���Ҫ����Ҵ����ڵ�һ������λ������ռ�Ҳ��Ҫ��֪����Ϣ��
			spaceItem.params["firstPlayerID"] = baseMailbox.id
			position = self.getScript().getFirstFishingPosition()
			DEBUG_MSG( "player( %i ) goto empty space." % baseMailbox.id )
		pickData = self.pickToSpaceData( baseMailbox, params )
		spaceItem.enter( baseMailbox, position, direction, pickData )
		
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		���µ�¼ֱ�ӷ��ص���һ�ε�½�ĵط�
		"""
		baseMailbox.logonSpaceInSpaceCopy()
		
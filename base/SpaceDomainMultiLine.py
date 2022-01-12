# -*- coding: gb18030 -*-
#
# $Id: SpaceDomainMultiLine.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

"""
1.ÿ�ŷ��ߵ�ͼ����������ͬ
2.��ͼ�л���ѭ���¹���
ԭ��ͼ���͡�������������������Ŀ���ͼ���͡���������������������ʽ
��ͨ��ͼ���� ��������״̬���������ߵ�ͼ����������������������ƽ�����
��ͨ��ͼ���� ��������״̬���������ߵ�ͼ�����㹻���ߣ�������������ͬ�ߵ�ͼ
��ͨ��ͼ���� ��������״̬���������ߵ�ͼ��û���㹻���ߣ�������ƽ�����
���ߵ�ͼ�������������������������ߵ�ͼ�����㹻���ߣ���������������ͬ�ߵ�ͼ
���ߵ�ͼ�������������������������ߵ�ͼ��û���㹻���ߣ���������ƽ�����
���ߵ�ͼ������������������������ͨ��ͼ���� ��������������������¼��״̬��ֱ�ӽ���

ע��
����״ָ̬������ҽ������ߵ�ͼ����¼���䵱ǰ�ڵڼ��ߡ�
����״̬��ʾ��Ҵ�����û�н�������ߵ�ͼ����������ʱû�м�¼���ڵ�����Ϣ��

3.��������������ߡ�
4.��������ĳ���ߵ�ͼĬ�Ͽ�ʼ���ŵ�ͼ��
"""

import time
import Language
import BigWorld
from bwdebug import *
import Function
import random
from SpaceDomain import SpaceDomain
import csdefine

class SpaceDomainMultiLine( SpaceDomain ):
	"""
	�����ั����
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		self._spacePlayerAmountLog = {}					# ����ÿ��space������
		self._spaceNumber2EnterID = {}
		self.initSpaces = {}
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_MULTILINE

		self.maxPlayerAmount = self.getScript().maxPlayerAmount
		self.maxLine = self.getScript().maxLine
		self.initLine = self.getScript().initLine
		self.newLineByPlayerAmount = self.getScript().newLineByPlayerAmount
		self.currInitLine = 1
		self.createMultiLineSpaceItem()
		

	def randomLine( self ):
		"""
		����һ��������߱��
		"""
		return random.randint( 1, self.maxLine )


	def createSpaceItem( self, param ):
		"""
		virtual method.
		ģ�巽����ʹ��param���������µ�spaceItem
		"""
		lineNumber = param.get( "lineNumber" )		# dbid����������֮��ص�ObjectScripts/SpaceCopy.py����ؽӿ�
		assert lineNumber is not None, "the param dbID is necessary."

		spaceItem = SpaceDomain.createSpaceItem( self, param )
		if spaceItem:
			self.keyToSpaceNumber[ lineNumber ] = spaceItem.spaceNumber
			self._spaceNumber2EnterID[ spaceItem.spaceNumber ] = lineNumber
			self._spacePlayerAmountLog[ lineNumber ] = 0

		return spaceItem

	def findFreeSpace( self ):
		"""
		Ѱ��һ����Կ��еĸ��� ���ظ������
		"""
		if self.maxLine <= 0 or len( self._spacePlayerAmountLog ) <= 0:
			return 1;

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

		# ���и��������ˣ���ôѰ���������ٵĵ�һ������
		sitems = self._spacePlayerAmountLog.items()
		enterID, playerAmountMin = sitems[0]
		for spaceEnterID, playerAmount in sitems:
			if playerAmount < playerAmountMin:
				enterID = spaceEnterID
				playerAmountMin = playerAmount

		return enterID

	def getSpacePlayerAmount( self, spaceNumber ):
		"""
		��øø���������
		"""
		return self._spacePlayerAmountLog.get( spaceNumber, 0 )

	def incPlayerAmount( self, lineNumber ):
		"""
		define method.
		���Ӹø���������
		"""
		if lineNumber in self._spacePlayerAmountLog:
			self._spacePlayerAmountLog[ lineNumber ] += 1
		else:
			self._spacePlayerAmountLog[ lineNumber ] = 1

	def decPlayerAmount( self, lineNumber ):
		"""
		define method.
		���ٸø���������
		"""
		try:
			self._spacePlayerAmountLog[ lineNumber ] -= 1
		except:
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

		if params[ "currSpaceClassName" ] == self.name and params[ "lineNumber" ] == params[ "currSpaceLineNumber" ]:
			params[ "ignoreFullRule" ] = True

		del params[ "currSpaceClassName" ]
		del params[ "currSpaceLineNumber" ]

		if not params.has_key( "ignoreFullRule" ) and \
			self.getSpacePlayerAmount( params[ "lineNumber" ] ) >= self.maxPlayerAmount:
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
		params[ "lineNumber" ] = enterID

		if self.getSpacePlayerAmount( enterID ) >= self.maxPlayerAmount:
			baseMailbox.client.onLoginSpaceIsFull()
			return

		spaceItem = self.findSpaceItem( params, True )
		spaceItem.logon( baseMailbox )


	def onInitSpaceCreateBaseCallback( self, spaceBase ):
		"""
		����base������ϵĻص�
		"""
		spaceBase.createCell()

	def createNPCObjectFormBase( self, npcID, position, direction, state ):
		"""
		define method
		(Զ��)����һ������ҿ��ƶ��� �ö���ӵ��base����

		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		# ���__lineNumber__���ṩ�߿��Ƶģ� ���磺���ʹ�������ⲿ�ƶ���һ��Ҫˢ���ߣ���ôĳ���������������ߵĻ�
		# ������ｫ��ˢ��ָ�������ϣ� ���û��ָ���ߣ� ��ˢ��1��
		lineNumber = 1
		if state.has_key( "_lineNumber_" ):
			lineNumber = state[ "_lineNumber_" ]
			del state[ "_lineNumber_" ]
			
		number = self.keyToSpaceNumber.get( lineNumber )
		if not number:								# ������Щ��û�����ĵ�ͼ�ռ䣬�ǲ�����ˢ��
			ERROR_MSG( "space(%s) lineNumber(%i) have not created!"% ( self.name, lineNumber ) )
			return

		if lineNumber <= 0 or lineNumber > self.maxLine:
			ERROR_MSG( "space(%s) lineNumber(%i) is not exist!"% ( self.name, lineNumber ) )
			lineNumber = 1

		spaceItem = self.getSpaceItem( lineNumber )
		if not spaceItem:
			raise "space(%s) not found. npc:%s, lineNumber:%i, spaceCount:%i/%i" % ( self.getScript().className, \
			npcID, lineNumber, self.getCurrentCopyCount(), self.maxLine )

		baseMailbox = spaceItem.baseMailbox
		baseMailbox.createNPCObjectFormBase( npcID, position, direction, state )

	def createCellNPCObjectFormBase( self, npcID, position, direction, state ):
		"""
		define method
		(Զ��)����һ������ҿ��ƶ��� �ö���û��base����

		@param npcID: STRING, ����ҿ��ƶ����Ψһ��ʶ
		@param position: ������Ŀ��λ��
		@param direction: ������Ŀ�귽��
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		# ���__lineNumber__���ṩ�߿��Ƶģ� ���磺���ʹ�������ⲿ�ƶ���һ��Ҫˢ���ߣ���ôĳ���������������ߵĻ�
		# ������ｫ��ˢ��ָ�������ϣ� ���û��ָ���ߣ� ��ˢ��1��
		lineNumber = 1
		if state.has_key( "_lineNumber_" ):
			lineNumber = state[ "_lineNumber_" ]
			del state[ "_lineNumber_" ]

		if lineNumber <= 0 or lineNumber > self.maxLine:
			ERROR_MSG( "space(%s) lineNumber(%i) is not exist!"% ( self.name, lineNumber ) )
			lineNumber = 1

		spaceItem = self.getSpaceItem( lineNumber )
		baseMailbox = spaceItem.baseMailbox
		baseMailbox.cell.createNPCObject( npcID, position, direction, state )

	def createMultiLineSpaceItem( self ):
		"""
		"""
		while self.currInitLine <= self.initLine:
			space = self.findSpaceItem( { 'lineNumber' : self.currInitLine }, True )
			space.createBase( self.onInitSpaceCreateBaseCallback )
			self.initSpaces[ self.currInitLine ] = space
			self.currInitLine += 1




#
# $Log: not supported by cvs2svn $
#
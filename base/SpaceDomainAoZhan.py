# -*- coding: gb18030 -*-
import random
import BigWorld

from SpaceDomain import SpaceDomain

import csdefine

class SpaceDomainAoZhan( SpaceDomain ):
	# ������Domain
	def __init__( self ):
		SpaceDomain.__init__( self )
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
	
	def activityEnd( self ):
		"""
		�����
		"""
		for spaceNumber in self.keyToSpaceNumber.itervalues():
			spaceItem = self.getSpaceItem( spaceNumber )
			if spaceItem:
				spaceItem.baseMailbox.cell.closeActivity()
	
	def activityStart( self ):
		for spaceNumber in self.keyToSpaceNumber.itervalues():
			spaceItem = self.getSpaceItem( spaceNumber )
			if spaceItem:
				spaceItem.baseMailbox.cell.activityStart()
	
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
		BigWorld.globalData[ "AoZhanQunXiongMgr" ].requestEnterSpace( self, position, direction, baseMailbox, params )
		
	def teleportEntityMgr( self, position, direction, baseMailbox, params ):
		"""
		define method.
		����������ص�
		"""
		spaceItem = self.findSpaceItem( params, True )
		if spaceItem:
			pickData = self.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )

	
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		��������һ�����򿪷ŵģ� ��˲������½���ܹ�����һ��
		�����Լ������ĸ����У� ���������Ӧ�÷��ص���һ�ε�½�ĵط�
		"""
		baseMailbox.logonSpaceInSpaceCopy()
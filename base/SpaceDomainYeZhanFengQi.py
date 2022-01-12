# -*- coding: gb18030 -*-
import random
import BigWorld

from SpaceDomain import SpaceDomain

import csdefine

class SpaceDomainYeZhanFengQi( SpaceDomain ):
	# ҹս������
	def __init__( self ):
		SpaceDomain.__init__( self )
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
	
	def activityEnd( self ):
		"""
		�����
		"""
		for spaceNumber in self.keyToSpaceNumber:
			spaceItem = self.getSpaceItem( spaceNumber )
			if spaceItem:
				spaceItem.baseMailbox.cell.closeActivity( csdefine.FENG_QI_CLOSE_REASON_TIME_OUT )
	
	def closeSpaceItem( self, spaceNumber ):
		"""
		�ر�ָ���ĸ���
		"""
		spaceItem = self.getSpaceItem( spaceNumber )
		if spaceItem:
			spaceItem.baseMailbox.cell.closeActivity( csdefine.FENG_QI_CLOSE_REASON_MIN_LEVEL )
	
	def removeSpaceItem( self, spaceNumber ):
		"""
		virtual method.
		ģ�巽����ɾ��spaceItem
		"""
		BigWorld.globalData[ "YeZhanFengQiMgr" ].removeSpaceNumber( spaceNumber )
		self.keyToSpaceNumber.remove( spaceNumber )
		SpaceDomain.removeSpaceItem( self, spaceNumber )
	
	def createSpaceItem( self, param ):
		"""
		virtual method.
		ģ�巽����ʹ��param���������µ�spaceItem
		"""
		spaceItem = self.createSpaceItem( params )
		
		BigWorld.globalData[ "YeZhanFengQiMgr" ].addNewSpaceNumber( params[ "level" ], spaceItem.spaceNumber )
#		self.keyToSpaceNumber.append( spaceItem.spaceNumber )
		return spaceItem
		
#	def addNewItem( self, params ):
#		spaceItem = self.createSpaceItem( params )
#		BigWorld.globalData[ "YeZhanFengQiMgr" ].addNewSpaceNumber( params[ "level" ], spaceItem.spaceNumber )
#		self.keyToSpaceNumber.append( spaceItem.spaceNumber )
#		return spaceItem
	
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
		BigWorld.globalData[ "YeZhanFengQiMgr" ].requestEnterSpace( self, position, direction, baseMailbox, params )
		
	def teleportEntityMgr( self, position, direction, baseMailbox, params ):
		"""
		define method.
		����������ص�
		"""
		spaceItem = self.findSpaceItem( params, True )
		if spaceItem:
			pickData = self.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )
		else:
			BigWorld.globalData[ "YeZhanFengQiMgr" ].requestEnterSpace( self, position, direction, baseMailbox, params )
	
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		��������һ�����򿪷ŵģ� ��˲������½���ܹ�����һ��
		�����Լ������ĸ����У� ���������Ӧ�÷��ص���һ�ε�½�ĵط�
		"""
		baseMailbox.logonSpaceInSpaceCopy()
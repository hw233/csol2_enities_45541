# -*- coding: gb18030 -*-
import random
import BigWorld

from SpaceDomain import SpaceDomain

import csdefine

class SpaceDomainAoZhan( SpaceDomain ):
	# 竞争类活动Domain
	def __init__( self ):
		SpaceDomain.__init__( self )
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
	
	def activityEnd( self ):
		"""
		活动结束
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
		传送一个entity到指定的space中
		@type position : VECTOR3, 
		@type direction : VECTOR3, 
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
		@type params : PY_DICT = None
		"""
		BigWorld.globalData[ "AoZhanQunXiongMgr" ].requestEnterSpace( self, position, direction, baseMailbox, params )
		
	def teleportEntityMgr( self, position, direction, baseMailbox, params ):
		"""
		define method.
		管理器传入回调
		"""
		spaceItem = self.findSpaceItem( params, True )
		if spaceItem:
			pickData = self.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )

	
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		副本是由一定规则开放的， 因此不允许登陆后能够呆在一个
		不是自己开启的副本中， 遇到此情况应该返回到上一次登陆的地方
		"""
		baseMailbox.logonSpaceInSpaceCopy()
# -*- coding: gb18030 -*-
import random
import BigWorld

from SpaceDomain import SpaceDomain

import csdefine

class SpaceDomainYeZhanFengQi( SpaceDomain ):
	# 夜战凤栖镇
	def __init__( self ):
		SpaceDomain.__init__( self )
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
	
	def activityEnd( self ):
		"""
		活动结束
		"""
		for spaceNumber in self.keyToSpaceNumber:
			spaceItem = self.getSpaceItem( spaceNumber )
			if spaceItem:
				spaceItem.baseMailbox.cell.closeActivity( csdefine.FENG_QI_CLOSE_REASON_TIME_OUT )
	
	def closeSpaceItem( self, spaceNumber ):
		"""
		关闭指定的副本
		"""
		spaceItem = self.getSpaceItem( spaceNumber )
		if spaceItem:
			spaceItem.baseMailbox.cell.closeActivity( csdefine.FENG_QI_CLOSE_REASON_MIN_LEVEL )
	
	def removeSpaceItem( self, spaceNumber ):
		"""
		virtual method.
		模板方法；删除spaceItem
		"""
		BigWorld.globalData[ "YeZhanFengQiMgr" ].removeSpaceNumber( spaceNumber )
		self.keyToSpaceNumber.remove( spaceNumber )
		SpaceDomain.removeSpaceItem( self, spaceNumber )
	
	def createSpaceItem( self, param ):
		"""
		virtual method.
		模板方法；使用param参数创建新的spaceItem
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
		传送一个entity到指定的space中
		@type position : VECTOR3, 
		@type direction : VECTOR3, 
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
		@type params : PY_DICT = None
		"""
		BigWorld.globalData[ "YeZhanFengQiMgr" ].requestEnterSpace( self, position, direction, baseMailbox, params )
		
	def teleportEntityMgr( self, position, direction, baseMailbox, params ):
		"""
		define method.
		管理器传入回调
		"""
		spaceItem = self.findSpaceItem( params, True )
		if spaceItem:
			pickData = self.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )
		else:
			BigWorld.globalData[ "YeZhanFengQiMgr" ].requestEnterSpace( self, position, direction, baseMailbox, params )
	
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		副本是由一定规则开放的， 因此不允许登陆后能够呆在一个
		不是自己开启的副本中， 遇到此情况应该返回到上一次登陆的地方
		"""
		baseMailbox.logonSpaceInSpaceCopy()
# -*- coding: gb18030 -*-
# python
import random
import time
# bigworld
import BigWorld
# base
from SpaceDomain import SpaceDomain
# common
from bwdebug import INFO_MSG,ERROR_MSG
import csdefine

class SpaceDomainYiJieZhanChang( SpaceDomain ) :
	"""
	异界战场
	"""
	def __init__( self ) :
		SpaceDomain.__init__( self )
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
	
	def activityEnd( self, spaceNumberList ):
		"""
		活动结束
		"""
		for spaceNumber in spaceNumberList:
			spaceItem = self.getSpaceItem( spaceNumber )
			if spaceItem:
				spaceItem.baseMailbox.cell.closeActivity( csdefine.YI_JIE_CLOSE_REASON_TIME_END )
	
	def closeSpaceCopy( self, spaceNumber ):
		"""
		关闭指定副本
		"""
		spaceItem = self.getSpaceItem( spaceNumber )
		if spaceItem:
			spaceItem.baseMailbox.cell.closeActivity( csdefine.YI_JIE_CLOSE_REASON_ONE_FACTION_WIN )
	
	def removeSpaceItem( self, spaceNumber ) :
		"""
		删除 spaceItem
		"""
		BigWorld.globalData["YiJieZhanChangMgr"].removeSpaceNumber( spaceNumber )
		SpaceDomain.removeSpaceItem( self, spaceNumber )
		
	def createSpaceItem( self, param ):
		"""
		virtual method.
		模板方法；使用param参数创建新的spaceItem
		"""
		spaceItem = self.createSpaceItem( params )
		
		BigWorld.globalData["YiJieZhanChangMgr"].addNewSpaceNumber( spaceItem.spaceNumber )
#		self.keyToSpaceNumber.append( spaceItem.spaceNumber )
		return spaceItem
	
	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		<define method>
		空间管理器传入回调 
		传送一个entity到指定的space中
		@type position : VECTOR3, 
		@type direction : VECTOR3, 
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
		@type params : PY_DICT = None
		"""
		BigWorld.globalData["YiJieZhanChangMgr"].requestEnterSpace( self, position, direction, baseMailbox, params )
	
	def teleportEntityToYiJie( self, position, direction, baseMailbox, params ) :
		"""
		<define method>
		异界战场管理器传入回调,传送一个entity到指定的space中
		"""
		targetSpaceNumber = params["targetSpaceNumber"]
		spaceItem = self.findSpaceItem( params, True )
		faction = params.pop( "faction" )
		try :
			pickData = self.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )
			BigWorld.globalData["YiJieZhanChangMgr"].onPlayerEnterBattleground( params["dbID"], spaceItem.spaceNumber, faction )
		except :
			ERROR_MSG( "%s teleportEntity is error." % self.name )
			BigWorld.globalData["YiJieZhanChangMgr"].requestEnterSpace( self, position, direction, baseMailbox, params )
	
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		<define method>
		在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT = None
		"""
		BigWorld.globalData["YiJieZhanChangMgr"].requestEnterSpaceOnLogin( self, baseMailbox, params )
	
	def teleportEntityToYiJieOnLogin( self, baseMailbox, params ) :
		"""
		<define method>
		异界战场管理器传入回调,在玩家重新登录的时候被调用
		"""
		lastOfflinePlayerInfo = params["lastOfflinePlayerInfo"]
		spaceItem = None
		lastOfflineFaction = 0
		if lastOfflinePlayerInfo != None :
			lastOfflineSpaceNumber, lastOfflineFaction = lastOfflinePlayerInfo
			spaceItem = self.getSpaceItem( lastOfflineSpaceNumber )
		currentTime = int( time.time() )
		dTime = currentTime - params["lastOffline"]
		
		if dTime > self.getScript().maxOfflineTime :
			BigWorld.globalData["YiJieZhanChangMgr"].removeNeedShowYiJieScorePlayer( params["dbID"] )
			baseMailbox.logonSpaceInSpaceCopy()
			if spaceItem :
				spaceItem.baseMailbox.cell.playerExit( params["dbID"] )
		elif not spaceItem :
			baseMailbox.logonSpaceInSpaceCopy()
		else :
			BigWorld.globalData["YiJieZhanChangMgr"].removeNeedShowYiJieScorePlayer( params["dbID"] )
			spaceItem.logon( baseMailbox )

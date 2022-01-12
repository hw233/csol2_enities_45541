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
	���ս��
	"""
	def __init__( self ) :
		SpaceDomain.__init__( self )
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
	
	def activityEnd( self, spaceNumberList ):
		"""
		�����
		"""
		for spaceNumber in spaceNumberList:
			spaceItem = self.getSpaceItem( spaceNumber )
			if spaceItem:
				spaceItem.baseMailbox.cell.closeActivity( csdefine.YI_JIE_CLOSE_REASON_TIME_END )
	
	def closeSpaceCopy( self, spaceNumber ):
		"""
		�ر�ָ������
		"""
		spaceItem = self.getSpaceItem( spaceNumber )
		if spaceItem:
			spaceItem.baseMailbox.cell.closeActivity( csdefine.YI_JIE_CLOSE_REASON_ONE_FACTION_WIN )
	
	def removeSpaceItem( self, spaceNumber ) :
		"""
		ɾ�� spaceItem
		"""
		BigWorld.globalData["YiJieZhanChangMgr"].removeSpaceNumber( spaceNumber )
		SpaceDomain.removeSpaceItem( self, spaceNumber )
		
	def createSpaceItem( self, param ):
		"""
		virtual method.
		ģ�巽����ʹ��param���������µ�spaceItem
		"""
		spaceItem = self.createSpaceItem( params )
		
		BigWorld.globalData["YiJieZhanChangMgr"].addNewSpaceNumber( spaceItem.spaceNumber )
#		self.keyToSpaceNumber.append( spaceItem.spaceNumber )
		return spaceItem
	
	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		<define method>
		�ռ����������ص� 
		����һ��entity��ָ����space��
		@type position : VECTOR3, 
		@type direction : VECTOR3, 
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: һЩ���ڸ�entity����space�Ķ�������� (domain����)
		@type params : PY_DICT = None
		"""
		BigWorld.globalData["YiJieZhanChangMgr"].requestEnterSpace( self, position, direction, baseMailbox, params )
	
	def teleportEntityToYiJie( self, position, direction, baseMailbox, params ) :
		"""
		<define method>
		���ս������������ص�,����һ��entity��ָ����space��
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
		��������µ�¼��ʱ�򱻵��ã������������ָ����space�г��֣�һ�������Ϊ���������ߵĵ�ͼ����
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: һЩ���ڸ�entity����space�Ķ��������(domain����)
		@type params : PY_DICT = None
		"""
		BigWorld.globalData["YiJieZhanChangMgr"].requestEnterSpaceOnLogin( self, baseMailbox, params )
	
	def teleportEntityToYiJieOnLogin( self, baseMailbox, params ) :
		"""
		<define method>
		���ս������������ص�,��������µ�¼��ʱ�򱻵���
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

# -*- coding: gb18030 -*-

import time
import Language
import BigWorld
from bwdebug import *
import Function
from SpaceDomain import SpaceDomain
import csdefine

class SpaceDomainCityWar(SpaceDomain):
	"""
	����ս���������� 
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
		self.checkTongManagerTimerID = self.addTimer( 8, 8, 0 )		

	def createSpaceItem( self, param ):
		#virtual method.
		#ģ�巽����ʹ��param���������µ�spaceItem
		spaceKey = param.get( "spaceKey" )
		spaceItem = SpaceDomain.createSpaceItem( self, param )
		self.keyToSpaceNumber[ spaceKey ] = spaceItem.spaceNumber
		return spaceItem

	def onSpaceCloseNotify( self, spaceNumber ):
		"""
		define method.
		�ռ�رգ�space entity����֪ͨ��
		@param 	spaceNumber		:		spaceNumber
		@type 	spaceNumber		:		int32
		"""
		SpaceDomain.onSpaceCloseNotify( self, spaceNumber )

	def teleportEntity( self, position, direction, baseMailbox, params ):
		#define method.
		#����һ��entity��ָ����space��

		BigWorld.globalData[ "TongManager" ].onEnterCityWarSpace( self, baseMailbox, params )
	
	def onEnterWarSpace( self, baseMailbox, params ):
		#define method.
		#����������ս��
		DEBUG_MSG( "params=",  params )
		isLogin = params.has_key( "login" )
		if not isLogin:
			spaceItem = self.findSpaceItem( params, True )
			
			position = (0, 0, 0)
			direction = (0, 0, 0)
			if params[ "left" ] == params[ "tongDBID" ]:
				position, direction = self.getScript().right_playerEnterPoint
			elif params[ "right" ] == params[ "tongDBID" ]:
				position, direction = self.getScript().left_playerEnterPoint
			else:
				position, direction = self.getScript().defend_playerEnterPoint
			
			pickData = self.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )
		else:
			self.onLoginWarSpace( baseMailbox, params )
	
	def onLoginWarSpace( self, baseMailbox, params ):
		# ����ڳ�ս�����е�½
		baseMailbox.logonSpaceInSpaceCopy()

	def teleportEntityOnLogin( self, baseMailbox, params ):
		#define method.
		#��������µ�¼��ʱ�򱻵��ã������������ָ����space�г��֣�һ�������Ϊ���������ߵĵ�ͼ����
		params[ "login" ] = True
		BigWorld.globalData[ "TongManager" ].onEnterCityWarSpace( self, baseMailbox, params )

	def closeCityWarRoom( self, cityName ):
		#define method.
		#��ǰ������ĳ��ս��
		for key, vaule in self.keyToSpaceNumber.iteritems():
			if cityName in key:
				space = self.getSpaceItem( vaule )
				if space and space.hasCell and space.baseMailbox:
					space.baseMailbox.closeCityWarRoom()
			
	def onTimer( self, timerID, cbID ):
		if self.checkTongManagerTimerID == timerID: # ���tongmanager�Ƿ��ʼ���� ���Լ�ע�����
			if BigWorld.globalData.has_key( "TongManager" ):
				BigWorld.globalData[ "TongManager" ].registerCityWarDomain( self )
				self.delTimer( self.checkTongManagerTimerID )
				self.checkTongManagerTimerID = 0
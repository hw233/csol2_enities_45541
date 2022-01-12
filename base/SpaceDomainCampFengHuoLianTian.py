# -*- coding: gb18030 -*-

import time
import Language
import BigWorld
from bwdebug import *
import Function
from SpaceDomain import SpaceDomain
import csdefine

class SpaceDomainCampFengHuoLianTian(SpaceDomain):
	"""
	��Ӫ���ս������������ 
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
		self.checkTongManagerTimerID = self.addTimer( 8, 8, 0 )

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

		BigWorld.globalData[ "CampMgr" ].onEnterCampFengHuoSpace( self, baseMailbox, params )
	
	def onEnterWarSpace( self, baseMailbox, params ):
		#define method.
		#����������ս��
		DEBUG_MSG( "params=",  params )
		isLogin = params.has_key( "login" )
		if not isLogin:
			spaceItem = self.findSpaceItem( params, True )
			
			position = (0, 0, 0)
			direction = (0, 0, 0)
			if params[ "left" ] == params[ "camp" ]:
				position, direction = self.getScript().left_playerEnterPoint
			elif params[ "right" ] == params[ "camp" ]:
				position, direction = self.getScript().right_playerEnterPoint
			
			pickData = self.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )
		else:
			self.onLoginCampFengHuoSpace( baseMailbox, params )
	
	def onLoginCampFengHuoSpace( self, baseMailbox, params ):
		# �������Ӫ����ս������������죩�����е�½
		spaceItem = self.findSpaceItem( params, False )
		if spaceItem:
			spaceItem.logon( baseMailbox )
		else:
			baseMailbox.logonSpaceInSpaceCopy()

	def teleportEntityOnLogin( self, baseMailbox, params ):
		#define method.
		#��������µ�¼��ʱ�򱻵��ã������������ָ����space�г��֣�һ�������Ϊ���������ߵĵ�ͼ����
		params[ "login" ] = True
		BigWorld.globalData[ "CampMgr" ].onEnterCampFengHuoSpace( self, baseMailbox, params )

	def closeCampFengHuoRoom( self ):
		#define method.
		#��ǰ������ĳ��ս��
		for key,value in self.keyToSpaceNumber.iteritems():
			space = self.getSpaceItem( value )
			if space and space.hasCell and space.baseMailbox:
				space.baseMailbox.closeCampFengHuoRoom()
			
	def onTimer( self, timerID, cbID ):
		if self.checkTongManagerTimerID == timerID: # ���tongmanager�Ƿ��ʼ���� ���Լ�ע�����
			if BigWorld.globalData.has_key( "CampMgr" ):
				BigWorld.globalData[ "CampMgr" ].registerCampFengHuoDomain( self )
				self.delTimer( self.checkTongManagerTimerID )
				self.checkTongManagerTimerID = 0
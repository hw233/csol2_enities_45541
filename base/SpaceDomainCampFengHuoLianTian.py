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
	阵营夺城战复赛副本领域 
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
		self.checkTongManagerTimerID = self.addTimer( 8, 8, 0 )

	def onSpaceCloseNotify( self, spaceNumber ):
		"""
		define method.
		空间关闭，space entity销毁通知。
		@param 	spaceNumber		:		spaceNumber
		@type 	spaceNumber		:		int32
		"""
		SpaceDomain.onSpaceCloseNotify( self, spaceNumber )

	def teleportEntity( self, position, direction, baseMailbox, params ):
		#define method.
		#传送一个entity到指定的space中

		BigWorld.globalData[ "CampMgr" ].onEnterCampFengHuoSpace( self, baseMailbox, params )
	
	def onEnterWarSpace( self, baseMailbox, params ):
		#define method.
		#玩家请求进入战场
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
		# 玩家在阵营城市战复赛（烽火连天）副本中登陆
		spaceItem = self.findSpaceItem( params, False )
		if spaceItem:
			spaceItem.logon( baseMailbox )
		else:
			baseMailbox.logonSpaceInSpaceCopy()

	def teleportEntityOnLogin( self, baseMailbox, params ):
		#define method.
		#在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		params[ "login" ] = True
		BigWorld.globalData[ "CampMgr" ].onEnterCampFengHuoSpace( self, baseMailbox, params )

	def closeCampFengHuoRoom( self ):
		#define method.
		#提前结束掉某场战争
		for key,value in self.keyToSpaceNumber.iteritems():
			space = self.getSpaceItem( value )
			if space and space.hasCell and space.baseMailbox:
				space.baseMailbox.closeCampFengHuoRoom()
			
	def onTimer( self, timerID, cbID ):
		if self.checkTongManagerTimerID == timerID: # 检查tongmanager是否初始化， 把自己注册给他
			if BigWorld.globalData.has_key( "CampMgr" ):
				BigWorld.globalData[ "CampMgr" ].registerCampFengHuoDomain( self )
				self.delTimer( self.checkTongManagerTimerID )
				self.checkTongManagerTimerID = 0
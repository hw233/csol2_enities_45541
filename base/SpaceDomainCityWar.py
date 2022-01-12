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
	城市战场副本领域 
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
		self.checkTongManagerTimerID = self.addTimer( 8, 8, 0 )		

	def createSpaceItem( self, param ):
		#virtual method.
		#模板方法；使用param参数创建新的spaceItem
		spaceKey = param.get( "spaceKey" )
		spaceItem = SpaceDomain.createSpaceItem( self, param )
		self.keyToSpaceNumber[ spaceKey ] = spaceItem.spaceNumber
		return spaceItem

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

		BigWorld.globalData[ "TongManager" ].onEnterCityWarSpace( self, baseMailbox, params )
	
	def onEnterWarSpace( self, baseMailbox, params ):
		#define method.
		#玩家请求进入战场
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
		# 玩家在城战副本中登陆
		baseMailbox.logonSpaceInSpaceCopy()

	def teleportEntityOnLogin( self, baseMailbox, params ):
		#define method.
		#在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		params[ "login" ] = True
		BigWorld.globalData[ "TongManager" ].onEnterCityWarSpace( self, baseMailbox, params )

	def closeCityWarRoom( self, cityName ):
		#define method.
		#提前结束掉某场战争
		for key, vaule in self.keyToSpaceNumber.iteritems():
			if cityName in key:
				space = self.getSpaceItem( vaule )
				if space and space.hasCell and space.baseMailbox:
					space.baseMailbox.closeCityWarRoom()
			
	def onTimer( self, timerID, cbID ):
		if self.checkTongManagerTimerID == timerID: # 检查tongmanager是否初始化， 把自己注册给他
			if BigWorld.globalData.has_key( "TongManager" ):
				BigWorld.globalData[ "TongManager" ].registerCityWarDomain( self )
				self.delTimer( self.checkTongManagerTimerID )
				self.checkTongManagerTimerID = 0
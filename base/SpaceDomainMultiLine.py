# -*- coding: gb18030 -*-
#
# $Id: SpaceDomainMultiLine.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

"""
1.每张分线地图分线数量不同
2.地图切换遵循以下规则
原地图类型　　　　　　　　　　目标地图类型　　　　　　　　　处理方式
普通地图、副 本（无线状态）　　分线地图　　　　　　　　　　　平衡分配
普通地图、副 本（有线状态）　　分线地图（有足够的线）　　　　进入同线地图
普通地图、副 本（有线状态）　　分线地图（没有足够的线）　　　平衡分配
分线地图　　　　　　　　　　　分线地图（有足够的线）　　　　　进入同线地图
分线地图　　　　　　　　　　　分线地图（没有足够的线）　　　　平衡分配
分线地图　　　　　　　　　　　普通地图、副 本　　　　　　　　记录线状态，直接进入

注：
有线状态指的是玩家进过分线地图，记录了其当前在第几线。
无线状态表示玩家从来都没有进入过分线地图，所以其暂时没有记录所在的线信息。

3.允许玩家主动换线。
4.可以配置某分线地图默认开始几张地图。
"""

import time
import Language
import BigWorld
from bwdebug import *
import Function
import random
from SpaceDomain import SpaceDomain
import csdefine

class SpaceDomainMultiLine( SpaceDomain ):
	"""
	多线类副本域
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		self._spacePlayerAmountLog = {}					# 包含每个space的人数
		self._spaceNumber2EnterID = {}
		self.initSpaces = {}
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_MULTILINE

		self.maxPlayerAmount = self.getScript().maxPlayerAmount
		self.maxLine = self.getScript().maxLine
		self.initLine = self.getScript().initLine
		self.newLineByPlayerAmount = self.getScript().newLineByPlayerAmount
		self.currInitLine = 1
		self.createMultiLineSpaceItem()
		

	def randomLine( self ):
		"""
		返回一个随机的线编号
		"""
		return random.randint( 1, self.maxLine )


	def createSpaceItem( self, param ):
		"""
		virtual method.
		模板方法；使用param参数创建新的spaceItem
		"""
		lineNumber = param.get( "lineNumber" )		# dbid参数来自与之相关的ObjectScripts/SpaceCopy.py的相关接口
		assert lineNumber is not None, "the param dbID is necessary."

		spaceItem = SpaceDomain.createSpaceItem( self, param )
		if spaceItem:
			self.keyToSpaceNumber[ lineNumber ] = spaceItem.spaceNumber
			self._spaceNumber2EnterID[ spaceItem.spaceNumber ] = lineNumber
			self._spacePlayerAmountLog[ lineNumber ] = 0

		return spaceItem

	def findFreeSpace( self ):
		"""
		寻找一个相对空闲的副本 返回副本编号
		"""
		if self.maxLine <= 0 or len( self._spacePlayerAmountLog ) <= 0:
			return 1;

		# 寻找未满承载量的副本
		for spaceEnterID, playerAmount in self._spacePlayerAmountLog.iteritems():
			if playerAmount < self.newLineByPlayerAmount:
				return spaceEnterID

		# 如果还有副本未开， 则开启它
		if self.getCurrentCopyCount() < self.maxLine:
			enterIDlist = self._spaceNumber2EnterID.values()
			for i in xrange( 1, self.maxLine + 1 ):
				if not i in enterIDlist:
					return i

		# 所有副本都开了，那么寻找人数最少的第一个副本
		sitems = self._spacePlayerAmountLog.items()
		enterID, playerAmountMin = sitems[0]
		for spaceEnterID, playerAmount in sitems:
			if playerAmount < playerAmountMin:
				enterID = spaceEnterID
				playerAmountMin = playerAmount

		return enterID

	def getSpacePlayerAmount( self, spaceNumber ):
		"""
		获得该副本的人数
		"""
		return self._spacePlayerAmountLog.get( spaceNumber, 0 )

	def incPlayerAmount( self, lineNumber ):
		"""
		define method.
		增加该副本的人数
		"""
		if lineNumber in self._spacePlayerAmountLog:
			self._spacePlayerAmountLog[ lineNumber ] += 1
		else:
			self._spacePlayerAmountLog[ lineNumber ] = 1

	def decPlayerAmount( self, lineNumber ):
		"""
		define method.
		减少该副本的人数
		"""
		try:
			self._spacePlayerAmountLog[ lineNumber ] -= 1
		except:
			pass

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
		DEBUG_MSG( "params:%s" % params )
		if not params.has_key( "lineNumber" ):
			params[ "lineNumber" ] = self.findFreeSpace()

		if params[ "currSpaceClassName" ] == self.name and params[ "lineNumber" ] == params[ "currSpaceLineNumber" ]:
			params[ "ignoreFullRule" ] = True

		del params[ "currSpaceClassName" ]
		del params[ "currSpaceLineNumber" ]

		if not params.has_key( "ignoreFullRule" ) and \
			self.getSpacePlayerAmount( params[ "lineNumber" ] ) >= self.maxPlayerAmount:
			baseMailbox.client.onStatusMessage( csstatus.ACCOUNT_SELECT_SPACE_IS_FULL, "" )
			return

		spaceItem = self.findSpaceItem( params, True )
		pickData = self.pickToSpaceData( baseMailbox, params )
		spaceItem.enter( baseMailbox, position, direction, pickData )

	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT = None
		"""
		enterID = self.findFreeSpace()
		params[ "lineNumber" ] = enterID

		if self.getSpacePlayerAmount( enterID ) >= self.maxPlayerAmount:
			baseMailbox.client.onLoginSpaceIsFull()
			return

		spaceItem = self.findSpaceItem( params, True )
		spaceItem.logon( baseMailbox )


	def onInitSpaceCreateBaseCallback( self, spaceBase ):
		"""
		副本base创建完毕的回调
		"""
		spaceBase.createCell()

	def createNPCObjectFormBase( self, npcID, position, direction, state ):
		"""
		define method
		(远程)创建一个非玩家控制对象 该对象拥有base部分

		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		# 这个__lineNumber__是提供线控制的， 比如：如果使用者在外部制定了一条要刷的线，那么某个副本如果有这个线的话
		# 这个怪物将被刷到指定的线上， 如果没有指定线， 将刷到1线
		lineNumber = 1
		if state.has_key( "_lineNumber_" ):
			lineNumber = state[ "_lineNumber_" ]
			del state[ "_lineNumber_" ]
			
		number = self.keyToSpaceNumber.get( lineNumber )
		if not number:								# 对于那些还没创建的地图空间，是不允许刷怪
			ERROR_MSG( "space(%s) lineNumber(%i) have not created!"% ( self.name, lineNumber ) )
			return

		if lineNumber <= 0 or lineNumber > self.maxLine:
			ERROR_MSG( "space(%s) lineNumber(%i) is not exist!"% ( self.name, lineNumber ) )
			lineNumber = 1

		spaceItem = self.getSpaceItem( lineNumber )
		if not spaceItem:
			raise "space(%s) not found. npc:%s, lineNumber:%i, spaceCount:%i/%i" % ( self.getScript().className, \
			npcID, lineNumber, self.getCurrentCopyCount(), self.maxLine )

		baseMailbox = spaceItem.baseMailbox
		baseMailbox.createNPCObjectFormBase( npcID, position, direction, state )

	def createCellNPCObjectFormBase( self, npcID, position, direction, state ):
		"""
		define method
		(远程)创建一个非玩家控制对象 该对象没有base部分

		@param npcID: STRING, 非玩家控制对象的唯一标识
		@param position: 创建的目标位置
		@param direction: 创建的目标方向
		@param state: see also: cell::BigWorld.createEntity()
		@return: None
		"""
		# 这个__lineNumber__是提供线控制的， 比如：如果使用者在外部制定了一条要刷的线，那么某个副本如果有这个线的话
		# 这个怪物将被刷到指定的线上， 如果没有指定线， 将刷到1线
		lineNumber = 1
		if state.has_key( "_lineNumber_" ):
			lineNumber = state[ "_lineNumber_" ]
			del state[ "_lineNumber_" ]

		if lineNumber <= 0 or lineNumber > self.maxLine:
			ERROR_MSG( "space(%s) lineNumber(%i) is not exist!"% ( self.name, lineNumber ) )
			lineNumber = 1

		spaceItem = self.getSpaceItem( lineNumber )
		baseMailbox = spaceItem.baseMailbox
		baseMailbox.cell.createNPCObject( npcID, position, direction, state )

	def createMultiLineSpaceItem( self ):
		"""
		"""
		while self.currInitLine <= self.initLine:
			space = self.findSpaceItem( { 'lineNumber' : self.currInitLine }, True )
			space.createBase( self.onInitSpaceCreateBaseCallback )
			self.initSpaces[ self.currInitLine ] = space
			self.currInitLine += 1




#
# $Log: not supported by cvs2svn $
#
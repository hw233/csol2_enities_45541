# -*- coding: gb18030 -*-

import time
import random

import BigWorld
from bwdebug import *

# 有生命物品检测时间间隔
LIFE_ITEM_TIME_INTERVAL = 1.0

class LifeItemMgr( BigWorld.Base ):
	"""
	有生命的物品管理器
	"""

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )

		self.datas = []
		self.uidMapMailBox = {}

		# 把自己注册为globalData全局实体
		self.registerGlobally( "LifeItemMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register LifeItemMgr Fail!" )
			# again
			self.registerGlobally( "LifeItemMgr", self._onRegisterManager )
		else:
			# 注册到所有的服务器中
			BigWorld.globalData["LifeItemMgr"] = self
			INFO_MSG("LifeItemMgr Create Complete!")
			self.addTimer( 0, LIFE_ITEM_TIME_INTERVAL, 0 )

	def onTimer( self, id, userData ):
		"""
		定时处理函数
		"""
		nowTime = time.time()

		for lifeTime, uid in self.datas[:]:
			if lifeTime <= nowTime:
				self.datas.remove( ( lifeTime, uid ) )
				baseMailBox = self.uidMapMailBox.get( uid )
				if baseMailBox: baseMailBox.cell.onItemLifeOver( uid )
			else:
				break

	def addItems( self, baseMailBox, uids, lifeTimes ):
		"""
		Define method
		添加一系列物品到管理器中
		"""
		for uid, lifeTime in zip( uids, lifeTimes ):
			index = self.getIndex( lifeTime )
			self.datas.insert( index, ( lifeTime, uid ) )
			self.uidMapMailBox[uid] = baseMailBox

	def removeItems( self, baseMailBox, uids, lifeTimes ):
		"""
		Define method
		从管理器中移除一系列物品
		"""
		for uid, lifeTime in zip( uids, lifeTimes ):
			data = ( lifeTime, uid )
			if data in self.datas:
				self.datas.remove( data )
			if uid in self.uidMapMailBox:
				self.uidMapMailBox.pop( uid )

	def getIndex( self, lifeTime ):
		"""
		根据中分原则查找lifeTime临近的索引，保证列表顺序排列
		"""

		count = len( self.datas )
		if count == 0: return 0

		if lifeTime <= self.datas[0][0]: return 0
		if lifeTime >= self.datas[-1][0]: return count

		startIndex = 0
		middleIndex = count/2
		endIndex = count - 1

		while 1:
			if ( endIndex - startIndex ) <= 1:
				return endIndex
			mValue = self.datas[middleIndex][0]
			if mValue == lifeTime:
				return middleIndex
			elif mValue < lifeTime:
				startIndex = middleIndex
				middleIndex = middleIndex + ( endIndex - middleIndex )/2
			else:
				endIndex = middleIndex
				middleIndex = middleIndex - ( middleIndex - startIndex )/2

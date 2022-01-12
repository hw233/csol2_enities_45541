# -*- coding: gb18030 -*-

"""
此模块只在cellApp和baseApp下使用，client不需要此模块。
"""
# $Id: TimeSave.py,v 1.4 2008-04-30 01:38:06 kebiao Exp $

import BigWorld
import time
import csconst
from bwdebug import *

class TimeSave:
	"""
	设计思想：
	          |-> 下线不保存
	cooldown <              |-> 下线仍然计时
	          |-> 下线保存 <
	                        |-> 下线暂停计时
	在cell部份的TimeSave，所有的cooldown都使用int(BigWorld.time() * C_SERVER_TIME_AMEND)来处理，
	在传输到BaseApp时有另外一个TimeSave模块处理cooldown的保存，这样我们就可以保证只使用一种时间类型与client交互，减少与client交互的复杂性。
	calculateTime()方法是根据给定的延迟计算cooldown的时间并返回。
	isTimeout()则判断当前的cooldown是否已过去。
	"""
	def __init__( self, section = None ):
		if section is None:
			self._id = 0						# INT16, 也可以表示cooldown的类型
			self._isSave = True					# 下线是否保存
			self._alwayCalc = False				# 如果下线保存，那么下线后是否还继续计算时间？
		else:
			self.initFromSection( section )

	def init( self, id, isSave, alwayCalc = False ):
		"""
		@param id: INT16
		@type id: INT16
		@type isSave: BOOL
		@type alwayCalc: BOOL
		"""
		self._id = id						# INT16, 也可以表示cooldown的类型
		self._isSave = isSave				# 下线是否保存
		self._alwayCalc = alwayCalc			# 如果下线保存，那么下线后是否还继续计算时间？

	def initFromSection( self, section ):
		self._id = section.readInt( "id" )
		self._isSave = bool( section.readInt( "isSave" ) )
		if self._isSave:
			self._alwayCalc = bool( section.readInt( "offlineAvailable" ) )
		else:
			self._alwayCalc = False

	def getID( self ):
		return self._id

	def isSave( self ):
		return self._isSave

	def isTimeout( self, cooldownTime ):
		"""
		判断是否时间已过

		@return: BOOL
		"""
		return time.time() >= ( cooldownTime - 0.1 )

	def calculateTime( self, timeVal ):
		"""
		以当前时间计算延迟值

		@param timeVal: 延迟值
		@type  timeVal: FLOAT
		@return: 返回最新的cooldown时间
		@rtype:  INT32
		"""
		return time.time() + timeVal

#end of class: CooldownType


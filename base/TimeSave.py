# -*- coding: gb18030 -*-

"""
此模块只在baseApp下使用。
"""
# $Id: TimeSave.py,v 1.5 2008-06-10 03:42:44 phw Exp $

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
	在BaseApp，下线不保存的一律掉弃，而下线保存的则使用真实时间来记录。
	在保存的时候由baseApp调用calculateOnSave()方法转换当前记录下的时间，
	而读取的时候由baseApp调用calculateOnLoad()方法转换保存下来的时间；
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

	def isAlwayCalc( self ):
		return self._alwayCalc

	def isTimeout( self, cooldownTime ):
		"""
		判断是否时间已过

		@param cooldownTime: time.time()
		@type  cooldownTime: INT32
		@return: BOOL
		"""
		return int( time.time() ) >= cooldownTime

	def calculateOnLoad( self, coolDown ):
		"""
		在加载人物数据的时候恢复coolDown。
		1、如果该coolDown是下线后计时，则需要重新计算coolDown的当前剩余时间（lastTime）。
		2、如果该coolDown是下线后不计时，则需要重新计算coolDown的结束时间（endTime）。

		@type  coolDown: 自定义coolDown数据类型，参见defs/alias.xml
		@rtype coolDown: 自定义coolDown数据类型，参见defs/alias.xml
		"""
		endTime = coolDown[2]
		if self.isTimeout( endTime ): return coolDown
		newCoolDown = list( coolDown )
		lastTime = coolDown[0]

		if self._alwayCalc:
			newLastTime = int( endTime - time.time() )
			newCoolDown[0] = newLastTime
		else:
			newEndTime = int( time.time() + lastTime )
			newCoolDown[2] = newEndTime

		return newCoolDown

	def calculateOnSave( self, coolDown ):
		"""
		在保存人物数据的时候保存coolDown。
		这里只需要计算该coolDown的当前剩余时间(lastTime)。

		@type  coolDown: 自定义coolDown数据类型，参见defs/alias.xml
		@rtype coolDown: 自定义coolDown数据类型，参见defs/alias.xml
		"""
		endTime = coolDown[2]
		if self.isTimeout( endTime ): return coolDown
		newCoolDown = list( coolDown )

		newLastTime = int( endTime - time.time() )
		newCoolDown[0] = newLastTime
		return newCoolDown

#end of class: CooldownType


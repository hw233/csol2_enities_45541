# -*- coding: gb18030 -*-

# ------------------------------------------------
# from engine
import BigWorld
# ------------------------------------------------
# from python
import time
import random
# ------------------------------------------------
# from common
import csconst
from bwdebug import *
# ------------------------------------------------
# from current directory
from CopyEvent.CopyStageCondition import CopyStageCondition

# ------------------------------------------------


# --------------------------------------------------------------------
# 公共条件
#
# 建议后续制作人员把添加的一些公共条件放在这里，
# 把自己副本的专有条件单独放在一起，由于工具制作会比较晚，
# 这样方便程序人员查看使用，也更有序。
# --------------------------------------------------------------------

class CopyStageCondition_Share_spaceDataReach( CopyStageCondition ) :
	"""
	某类副本内容数据达到一定数值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		CopyStageCondition.__init__( self )
		self.spaceDataID = 0
		self.threshold = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.spaceDataID = section["param1"].asInt
		self.threshold = section["param2"].asInt

	def check( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		currentValue = int( BigWorld.getSpaceDataFirstForKey( spaceEntity.spaceID, self.spaceDataID ) )
		if currentValue == self.threshold :
			return True
		else :
			return False

class CopyStageCondition_Share_hasUserTimer( CopyStageCondition ) :
	"""
	当前副本是否有一用户自定义timer
	"""
	def __init__( self ):
		"""
		初始化
		"""
		CopyStageCondition.__init__( self )
		self.uArg = -1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.uArg = section["param1"].asInt

	def check( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		return spaceEntity.hasUserTimer( self.uArg )

class CopyStageCondition_Share_isUserTimer( CopyStageCondition ) :
	"""
	是否是某一用户自定义timer
	"""
	def __init__( self ):
		"""
		初始化
		"""
		CopyStageCondition.__init__( self )
		self.uArg = -1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.uArg = section["param1"].asInt

	def check( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		return params["userArg"] == self.uArg

class CopyStageCondition_Share_isMonsterTypeDied(CopyStageCondition):
	"""
	是否是指定类型的怪物
	"""
	def __init__( self ):
		"""
		初始化
		"""
		CopyStageCondition.__init__( self )
		self.class_name = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.class_name = section.readString("param1")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		return self.class_name == params["monsterClassName"]


class CopyStageCondition_Share_rateLessThan(CopyStageCondition):
	"""
	概率判断,小于某一数值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		CopyStageCondition.__init__( self )
		self.rate = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.rate = section.readFloat("param1")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		return random.random() < self.rate


class CopyStageCondition_Share_timeModZero(CopyStageCondition):
	"""
	对时间点取模是否为零，用于时间间隔判断
	"""
	def __init__( self ):
		"""
		初始化
		"""
		CopyStageCondition.__init__( self )
		self.time_flag = ""
		self.mod = 1.0
		self.sensitivity = 0.5

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.time_flag = section.readString("param1")
		if section.readString("param2") != "":
			self.mod = section.readFloat("param2")
		if section.readString("param3") != "":
			self.sensitivity = section.readFloat("param3")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		escape = time.time() - spaceEntity.queryTemp(self.time_flag)
		mod = escape % self.mod

		INFO_MSG("Time mod result: %f, mod: %f, sensitivity: %f" % (mod, self.mod, self.sensitivity))

		return (mod - 0) < self.sensitivity or (self.mod - mod) < self.sensitivity


class CopyStageCondition_Share_timeEscapeNotReach(CopyStageCondition):
	"""
	距时间点经过的时间值小于指定值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		CopyStageCondition.__init__( self )
		self.time_flag = ""
		self.value = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.time_flag = section.readString("param1")
		self.value = section.readFloat("param2")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		escape = time.time() - spaceEntity.queryTemp(self.time_flag)
		return escape < self.value


class CopyStageCondition_Share_timeEscapePass(CopyStageCondition):
	"""
	距时间点经过的时间值大于指定值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		CopyStageCondition.__init__( self )
		self.time_flag = ""
		self.value = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.time_flag = section.readString("param1")
		self.value = section.readFloat("param2")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		escape = time.time() - spaceEntity.queryTemp(self.time_flag)
		return escape > self.value


class CopyStageCondition_Share_tempFlagHasSet(CopyStageCondition):
	"""
	判断指定标识是否被设置
	"""
	def __init__( self ):
		"""
		初始化
		"""
		CopyStageCondition.__init__( self )
		self.temp_flag = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.temp_flag = section.readString("param1")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		return spaceEntity.queryTemp(self.temp_flag) != None


class CopyStageCondition_Share_tempFlagNotSet(CopyStageCondition):
	"""
	判断指定标识是否未被设置
	"""
	def __init__( self ):
		"""
		初始化
		"""
		CopyStageCondition.__init__( self )
		self.temp_flag = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.temp_flag = section.readString("param1")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		return spaceEntity.queryTemp(self.temp_flag) == None


class CopyStageCondition_Share_npcRecordLessThan(CopyStageCondition):
	"""
	判断指定NPC数量是否小于某个数值
	"""
	def __init__( self ):
		"""
		初始化
		"""
		CopyStageCondition.__init__( self )
		self.class_name = ""
		self.value = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.class_name = section.readString("param1")
		self.value = section.readInt("param2")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		record = spaceEntity.queryTemp("NPC_AMOUNT_RECORD")
		if record is None:
			return True

		return record.get(self.class_name, 0) < self.value


class CopyStageCondition_Share_isCertainMonsters( CopyStageCondition ) :
	"""
	是否是指定的某些怪物类型,此条件用于有额外参数 params["monsterClassName"] 的事件
	"""
	def __init__( self ):
		"""
		初始化
		"""
		CopyStageCondition.__init__( self )
		self.classNames = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		classNames = section.readString("param1")
		self.classNames = classNames.split()

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		className = params["monsterClassName"]
		return className in self.classNames


class CopyStageCondition_Share_isNotCertainMonsters( CopyStageCondition ) :
	"""
	是否不是指定的某些怪物类型,此条件用于有额外参数 params["monsterClassName"] 的事件
	"""
	def __init__( self ):
		"""
		初始化
		"""
		CopyStageCondition.__init__( self )
		self.classNames = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		classNames = section.readString("param1")
		self.classNames = classNames.split()

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		className = params["monsterClassName"]
		return className not in self.classNames

# --------------------------------------------------------------------
# 公共条件结束
# --------------------------------------------------------------------

# **************************************************************************************

# --------------------------------------------------------------------
# 炼妖壶副本开始
# --------------------------------------------------------------------

class CopyStageCondition_MMT_evilSoulPercent(CopyStageCondition):
	"""
	妖气比例判断
	"""
	def __init__( self ):
		"""
		初始化
		"""
		CopyStageCondition.__init__( self )
		self.percent = 0
		self.total = 300.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.percent = section.readFloat("param1")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		current = spaceEntity.queryTemp("YAOQI_VALUE", 0)
		return current / self.total >= self.percent

# --------------------------------------------------------------------
# 炼妖壶副本结束
# --------------------------------------------------------------------

# **************************************************************************************

# --------------------------------------------------------------------
# 防守副本开始
# --------------------------------------------------------------------

class CopyStageCondition_FangShou_isTheArea(CopyStageCondition):
	"""
	判断是否是某一防守区域的机关开启
	"""
	def __init__( self ):
		"""
		初始化
		"""
		CopyStageCondition.__init__( self )
		self.areaName = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.areaName = section.readString("param1")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		return params[ "areaName" ] == self.areaName


# --------------------------------------------------------------------
# 防守副本结束
# --------------------------------------------------------------------

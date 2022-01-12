# -*- coding: gb18030 -*-

# ------------------------------------------------
# from python
import time
import copy
import re
import math
import random
# ------------------------------------------------
# from engine
import BigWorld
# ------------------------------------------------
# from common
from bwdebug import *
from Function import Functor
import csdefine
import csconst
# ------------------------------------------------
# from locale_default
import csstatus
import cschannel_msgs
# ------------------------------------------------
# from cell
import Love3
import Const
from ObjectScripts.GameObjectFactory import g_objFactory
# ------------------------------------------------
# from current directory
from CopyEvent.CopyStageAction import CopyStageAction

# ------------------------------------------------


# --------------------------------------------------------------------
# 公共行为
#
# 建议后续制作人员把添加的一些公共行为放在这里，
# 把自己副本的专有行为单独放在一起，由于工具制作会比较晚，
# 这样方便程序人员查看使用，也更有序。
# --------------------------------------------------------------------

class CopyStageAction_Share_doNextStage( CopyStageAction ):
	"""
	结束当前关卡，进入下一关卡。
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		spaceEntity.getScript().getCurrentStage( spaceEntity ).endStage( spaceEntity )


class CopyStageAction_Share_closeSpace( CopyStageAction ):
	"""
	踢出副本内所有玩家，关闭副本
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		spaceEntity.getScript().kickAllPlayer( spaceEntity )
		spaceEntity.addUserTimer( 10, 0, Const.SPACE_TIMER_ARG_CLOSE_SPACE )


class CopyStageAction_Share_notifySpawnMonster( CopyStageAction ):
	"""
	通知指定 MonsterType 的刷新点刷怪，用于刷新点 SpawnPointCopyTemplate 及其子类。
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.monsterType = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.monsterType = section["param1"].asInt

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		spaceEntity.base.spawnMonsters( {"monsterType":  self.monsterType, "level": spaceEntity.params["copyLevel"] } )


class CopyStageAction_Share_setSpaceData( CopyStageAction ):
	"""
	改变副本内容显示数据
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.spaceDataID = 0
		self.changeValue = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.spaceDataID = section["param1"].asInt
		self.changeValue = section["param2"].asInt

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		currentValue = int( BigWorld.getSpaceDataFirstForKey( spaceEntity.spaceID, self.spaceDataID ) )
		BigWorld.setSpaceData( spaceEntity.spaceID, self.spaceDataID, currentValue +  self.changeValue )


class CopyStageAction_Share_broadcastStatusMessage( CopyStageAction ):
	"""
	向副本内所有玩家广播一条状态消息
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.messageID = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.messageID = section[ "param1" ].asInt

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		for e in spaceEntity._players:
			e.client.onStatusMessage( self.messageID, "" )


class CopyStageAction_Share_addUserTimer( CopyStageAction ):
	"""
	添加一个用户自定义timer
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.start = 0
		self.interal = 0
		self.uArg = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.start = section["param1"].asFloat
		self.interal = section["param2"].asFloat
		self.uArg = section["param3"].asInt

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		spaceEntity.addUserTimer( self.start, self.interal, self.uArg, params )


class CopyStageAction_Share_cancelUserTimer( CopyStageAction ):
	"""
	撤销一个用户自定义timer
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.uArg = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.uArg = section["param1"].asInt

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		spaceEntity.cancelUserTimer( self.uArg )


class CopyStageAction_Share_broadcastDirectMessage( CopyStageAction ):
	"""
	向副本内所有玩家广播一条直接的消息
	param1	: 频道列表，只能配置在 csdefine.py 中定义的频道，频道之间用空格隔开，如 <param1> 14 18 </param1>
	param2	: 发言者名称，如 <param2> 混沌队长 </param2>
	param3	: 消息内容，如 <param2> 任何人休想擅闯此地 </param2>
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.chids = ( 14, 18 )				# 默认频道为 ( SY, SC ), 系统频道 和 在屏幕中间提示的频道
		self.spkName = ""
		self.msg = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		param1 = section["param1"].asString
		if param1 != "" :
			self.chids = tuple( param1.split() )
		self.spkName = section["param2"].asString
		self.msg = section["param3"].asString

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		for playerBase in spaceEntity._players :
			playerBase.client.onDirectMessage( self.chids, self.spkName, self.msg )


class CopyStageAction_Share_broadcastGMMessage( CopyStageAction ):
	"""
	向副本内的玩家广播(GM/公告频道)
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.message_id = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.message_id = eval("cschannel_msgs.%s" % section.readString("param1"))

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event		 :	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		for e in spaceEntity._players :
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", self.message_id, [] )


class CopyStageAction_Share_portraitTalk( CopyStageAction ):
	"""
	出现带NPC头像的对话提示
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.type = 0
		self.headTextureID = ""
		self.text = ""
		self.monsterName = ""
		self.lastTime = 0.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.type = section.readInt( "param1" )
		self.headTextureID = section.readString( "param2" )

		self.text = getattr(cschannel_msgs, section.readString("param3"), None)
		if self.text is None:
			self.text = section.readString("param3")

		self.monsterName = section.readString( "param4" )
		self.lastTime = section.readFloat( "param5" )

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event		 :	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		for e in spaceEntity._players :
			e.client.showHeadPortraitAndText(self.type, self.monsterName, self.headTextureID, self.text, self.lastTime)
			if self.monsterName:
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, self.monsterName, self.text, [] )
			else:
				e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_MESSAGE, 0, e.getName(), self.text, [] )


class CopyStageAction_Share_triggerEvent( CopyStageAction ):
	"""
	触发事件
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.event_id = 0
		self.params = {}

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.event_id = eval("csdefine.%s" % section.readString("param1"))
		self.params = eval("{%s}" % re.sub("\r?\n", "", section.readString("param2")))

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event		 :	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		current_stage = spaceEntity.getScript().getCurrentStage(spaceEntity)
		current_stage.doAllEvent(spaceEntity, self.event_id, self.params.copy())


class CopyStageAction_Share_loopEvent( CopyStageAction ):
	"""
	循环触发事件
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.event_id = 0
		self.params = {}
		self.repeat = 0
		self.counter = 0
		self.interval = 1.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.event_id = eval("csdefine.%s" % section.readString("param1"))
		if section.readString("param2"):
			self.interval = section.readFloat("param2")
		self.repeat = section.readInt("param3")
		self.params = eval("{%s}" % re.sub("\r?\n", "", section.readString("param4")))

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event		 :	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		if spaceEntity.queryTemp("TIMER_OF_TEMPLATE_EVENT_%s" % self.event_id) == None:
			self.startLoop(spaceEntity, params)
		else:
			uarg = spaceEntity.queryTemp("TIMER_OF_TEMPLATE_EVENT_%s" % self.event_id)

			if not spaceEntity.hasUserTimer(uarg):
				self.startLoop(spaceEntity, params)
			else:
				INFO_MSG("Event %s timer %s ticks." % (self.event_id, uarg))

				self.onLoop(spaceEntity, params)

	def startLoop(self, spaceEntity, params):
		"""开启循环"""
		if self.repeat > 0:
			self.counter = self.repeat

		params = self.params.copy()
		params[ "eventType" ] = self._eventID
		params[ "eventInStage" ] = self._eventInStage
		params[ "actionInEvent" ] = self._indexInEvent
		params[ "stageInCopy" ] = self._stageInCopy

		uarg = spaceEntity.addUserTimer( self.interval, self.interval, 0, params )
		spaceEntity.setTemp("TIMER_OF_TEMPLATE_EVENT_%s" % self.event_id, uarg)

		INFO_MSG("Add event %s timer : %s" % (self.event_id, uarg))

	def onLoop(self, spaceEntity, params):
		"""循环回调"""
		if self.repeat > 0 and self.counter == 0:
			spaceEntity.cancelUserTimer(spaceEntity.popTemp("TIMER_OF_TEMPLATE_EVENT_%s" % self.event_id))
		else:
			self.counter -= 1
			current_stage = spaceEntity.getScript().getCurrentStage(spaceEntity)
			current_stage.doAllEvent(spaceEntity, self.event_id, params)


class CopyStageAction_Share_stopEvent( CopyStageAction ):
	"""
	停止循环事件
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.event_id = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.event_id = eval("csdefine.%s" % section.readString("param1"))

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event		 :	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		uarg = spaceEntity.popTemp("TIMER_OF_TEMPLATE_EVENT_%s" % self.event_id)

		INFO_MSG("Stop event %s timer : %s" % (self.event_id, uarg))

		if uarg is not None:
			spaceEntity.cancelUserTimer(uarg)


class CopyStageAction_Share_createEntityRandomRange( CopyStageAction ):
	"""
	随机范围内的位置刷怪
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.class_name = 0
		self.center = None
		self.max_radius = 0
		self.min_radius = 0
		self.params = {}

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.class_name = section.readString("param1")
		self.center = eval("(%s)" % re.sub(" +", ",", section.readString("param2")))
		self.max_radius = section.readFloat("param3")
		self.min_radius = section.readFloat("param4")
		self.params = eval("{%s}" % re.sub("\r?\n", "", section.readString("param5")))

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event		 :	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		random_radius = self.min_radius + (self.max_radius - self.min_radius) * random.random()
		random_yaw = 2 * math.pi * random.random()

		x, y, z = self.center
		x += random_radius * math.sin(random_yaw)
		z += random_radius * math.cos(random_yaw)

		INFO_MSG("Create entity %s: space: %s, pos:%s, dir:%s, params:%s" %\
			(self.class_name, spaceEntity.getScript().className, (x, y, z),\
			(0, 0, 0), self.params))

		g_objFactory.createEntity(self.class_name, spaceEntity.spaceID,
			(x, y, z), (0,0,0), self.params.copy())


class CopyStageAction_Share_createEntityRandomPos( CopyStageAction ):
	"""
	从指定位置随机抽取一个位置刷怪
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.class_name = 0
		self.spawn_points = ()
		self.spawn_count = 1
		self.params = {}

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.class_name = section.readString("param1")
		self.spawn_points = eval("(%s)" % re.sub("\r?\n", "", section.readString("param2")))
		if section.readString("param3") != "":
			self.spawn_count = section.readInt("param3")
		self.params = eval("{%s}" % re.sub("\r?\n", "", section.readString("param4")))

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event		 :	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		count = self.spawn_count
		while count > 0:
			pos, dir = random.choice(self.spawn_points)

			INFO_MSG("Create entity %s: space: %s, pos:%s, dir:%s, params:%s" %\
				(self.class_name, spaceEntity.getScript().className, pos,\
				dir, self.params))

			g_objFactory.createEntity(self.class_name, spaceEntity.spaceID,
				pos, dir, self.params.copy())

			count -= 1


class CopyStageAction_Share_recordTime(CopyStageAction):
	"""
	记录时间点
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.time_flag = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.time_flag = section.readString("param1")

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event		 :	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		INFO_MSG("Record time to flag %s at %f" % (self.time_flag, time.time()))

		spaceEntity.setTemp(self.time_flag, time.time())


class CopyStageAction_Share_setTemp(CopyStageAction):
	"""
	设置副本临时变量
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.temp_flag = ""
		self.temp_value = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.temp_flag = section.readString("param1")
		self.temp_value = section.readInt("param2")

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event		 :	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		INFO_MSG("Set flag %s to value %d" % (self.temp_flag, self.temp_value))

		spaceEntity.setTemp(self.temp_flag, self.temp_value)


class CopyStageAction_Share_removeTemp(CopyStageAction):
	"""
	移除副本临时变量
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.temp_flag = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.temp_flag = section.readString("param1")

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event		 :	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		INFO_MSG("Remove flag %s" % self.temp_flag)

		spaceEntity.removeTemp(self.temp_flag)


class CopyStageAction_Share_incNpcRecord(CopyStageAction):
	"""
	增加NPC的数量记录，用于限制某类NPC的数量
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.class_name = ""
		self.inc_value = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.class_name = section.readString("param1")
		self.inc_value = section.readInt("param2")

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event		 :	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		record = spaceEntity.queryTemp("NPC_AMOUNT_RECORD")
		if record is None:
			record = {}
			spaceEntity.setTemp("NPC_AMOUNT_RECORD", record)

		current = record.get(self.class_name, 0)
		record[self.class_name] = current + self.inc_value

		INFO_MSG("Increase npc %s record of space %s to %i" %\
			(self.class_name, spaceEntity.getScript().className, record[self.class_name]))


class CopyStageAction_Share_decNpcRecord(CopyStageAction):
	"""
	减少NPC的数量记录，用于限制某类NPC的数量
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.class_name = ""
		self.dec_value = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.class_name = section.readString("param1")
		self.dec_value = section.readInt("param2")

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event		 :	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		record = spaceEntity.queryTemp("NPC_AMOUNT_RECORD")
		if record is None:
			record = {}
			spaceEntity.setTemp("NPC_AMOUNT_RECORD", record)

		current = record.get(self.class_name, 0)
		record[self.class_name] = current - self.dec_value

		INFO_MSG("Decrease npc %s record of space %s to %i" %\
			(self.class_name, spaceEntity.getScript().className, record[self.class_name]))

# --------------------------------------------------------------------
# 公共行为结束
# --------------------------------------------------------------------

# **************************************************************************************

# --------------------------------------------------------------------
# 混沌副本开始
# --------------------------------------------------------------------

class CopyStageAction_HunDun_onFirstEnter( CopyStageAction ):
	"""
	混沌副本第一个玩家进入副本后的处理,建立副本与玩家队伍之间的关联。
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		BigWorld.globalData['Hundun_%i' % params['teamID'] ] = True
		spaceEntity.setTemp('globalkey','Hundun_%i' % params['teamID'])

class CopyStageAction_HunDun_onBossAppear( CopyStageAction ):
	"""
	混沌副本BOSS出场喊话
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		for e in spaceEntity._players :
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.BCT_HUNDUN_BOSS_NOTIFY, [] )

class CopyStageAction_HunDun_addIntegral( CopyStageAction ):
	"""
	增加混沌积分
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.addValue = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.addValue = section["param1"].asInt

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		for e in spaceEntity._players:
			if BigWorld.entities.has_key( e.id ):
				if BigWorld.entities[e.id].isReal():
					jifen = BigWorld.entities[e.id].query( "hundun_jifen", 0 )
					BigWorld.entities[e.id].set( "hundun_jifen",jifen + self.addValue )
					BigWorld.entities[e.id].client.onStatusMessage( csstatus.HUNDUN_CURRENT_JIFEN, str(( jifen + self.addValue, )) )

class CopyStageAction_HunDun_createSpaceDoor( CopyStageAction ):
	"""
	创建混沌副本中BOSS死亡后的传送门
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		doordict = {"name" : cschannel_msgs.HUN_DUN_RU_QIN_CHUAN_SONG_DIAN}
		doordict["radius"] = 2.0
		doordict["destSpace"] = spaceEntity.params["spaceLabel"]
		doordict["destPosition"] = spaceEntity.params["position"]
		doordict["destDirection"] = ( 0, 0, 0 )
		doordict["modelNumber"] = "gw7123"
		doordict["modelScale"] = 25
		BigWorld.createEntity( "SpaceDoor", spaceEntity.spaceID, (111.796,-0.789,35.983), (0, 0, 0), doordict )

class CopyStageAction_HunDun_destroyEnterNPC( CopyStageAction ):
	"""
	销毁混沌副本的进入NPC
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		for key in BigWorld.globalData.keys():
			if type(key) == type("cellApp_") and "cellApp_" in key:
				BigWorld.executeRemoteScript( "BigWorld.cellAppData['%s'].entityFunc( %i, '%s' )"%( key + "_actions", spaceEntity.params["enterMonsterID"], "destroy" ), BigWorld.globalData[key] )

class CopyStageAction_HunDun_initSpaceData( CopyStageAction ):
	"""
	混沌副本数据初始化
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		if "HD_%i"%spaceEntity.params["teamID"] in BigWorld.cellAppData.keys():
			del BigWorld.cellAppData["HD_%i"%spaceEntity.params["teamID"]]

		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, cschannel_msgs.ACTIVITY_MONSTERACTIVITY )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, 3600 )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, cschannel_msgs.WIZCOMMAND_HUN__RU_QIN )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, -1 )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, 30 )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 1 )

# --------------------------------------------------------------------
# 混沌副本结束
# --------------------------------------------------------------------

# **************************************************************************************

# --------------------------------------------------------------------
# 炼妖壶副本开始
# --------------------------------------------------------------------
class CopyStageAction_MMT_addEvilSoul(CopyStageAction):
	"""
	炼妖壶副本增加妖气
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.add_count = 0
		self.total = 300.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.add_count = section.readInt("param1")

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event		 :	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		current = spaceEntity.queryTemp("YAOQI_VALUE", 0)
		current += self.add_count
		spaceEntity.setTemp("YAOQI_VALUE", current)

		INFO_MSG("Add yaoqi to %d" % current)

		percent = current / self.total
		BigWorld.setSpaceData(spaceEntity.spaceID, csconst.SPACE_COPY_MMP_YAOQI_PERCENT, percent)


class CopyStageAction_MMT_addElixirToKiller(CopyStageAction):
	"""
	炼妖壶副本给击杀者增加妖丹
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )
		self.add_count = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )
		self.add_count = section.readInt("param1")

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event		 :	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		if not BigWorld.entities.has_key(params["monsterID"]):
			ERROR_MSG("Can't find monster by id %s" % params["monsterID"])
			return

		# 使用字典在副本身上记录玩家的妖丹数量
		elixir_record = spaceEntity.queryTemp("elixir_record")
		if elixir_record is None:
			elixir_record = {}
			spaceEntity.setTemp("elixir_record", elixir_record)

		monster = BigWorld.entities[params["monsterID"]]
		for injurer_id in monster.damageList:
			if not BigWorld.entities.has_key(injurer_id):
				WARNING_MSG("Can't find injurer by id %s" % injurer_id)
			else:
				injurer = BigWorld.entities[injurer_id]
				if not hasattr(injurer, "databaseID"):
					continue

				elixir = elixir_record.get(injurer.databaseID, 0)
				elixir += self.add_count
				elixir_record[injurer.databaseID] = elixir

				INFO_MSG("Add yaodan of %i to %d" % (injurer_id, elixir))

class CopyStageAction_MMT_evilWind(CopyStageAction):
	"""
	吹妖风
	"""
	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	event		:	拥有此行为的 event （ 做此支持是为了得到或写 CopyStageEvent 的动态数据 ）
		@type	event		 :	instance of CopyStageEvent
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		"""
		INFO_MSG("Blow evil wind. to be implemented.")

# --------------------------------------------------------------------
# 炼妖壶副本结束
# --------------------------------------------------------------------

# **************************************************************************************

# --------------------------------------------------------------------
# 防守副本开始
# --------------------------------------------------------------------

class CopyStageAction_FangShou_spawnMonster( CopyStageAction ):
	"""
	防守副本刷怪
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		currentMonsterWave = spaceEntity.queryTemp( "currentMonsterWave",0 )
		if currentMonsterWave >= Const.COPY_FANG_SHOU_MONSTER_WAVE_MAX :
			return

		if currentMonsterWave == Const.COPY_FANG_SHOU_FIRST_BOSS_WAVE - 1 :
			spaceEntity.base.spawnMonsters( { "monsterType" : 1, "level": spaceEntity.params["copyLevel"] } )		# 刷新第一个BOSS
		elif currentMonsterWave == Const.COPY_FANG_SHOU_SECOND_BOSS_WAVE - 1 :
			spaceEntity.base.spawnMonsters( { "monsterType" : 2, "level": spaceEntity.params["copyLevel"] } )		# 刷新第二个BOSS
			spaceEntity.cancelUserTimer( 1 )													# 撤销刷怪timer
		else :
			spaceEntity.base.spawnMonsters( { "monsterType" : 0, "level": spaceEntity.params["copyLevel"] } )		# 刷新小怪
			spaceEntity.addUserTimer( 1, 0, Const.SPACE_TIMER_ARG_FANG_SHOU_DELAY_SPAWN_MONSTER )

		currentMonsterWave += 1
		spaceEntity.setTemp( "currentMonsterWave" , currentMonsterWave )
		leaveWave = Const.COPY_FANG_SHOU_MONSTER_WAVE_MAX - currentMonsterWave
		if leaveWave != 0 :
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_BATCH_TIME, "1_%i_%i"%( Const.COPY_FANG_SHOU_EACH_WAVE_TIME, int( time.time() ) ) )
		else :
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NEXT_BATCH_TIME, "1_%i_%i"%( 0, int( time.time() ) ) )
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_WAVE, leaveWave )

class CopyStageAction_FangShou_onEnterCopy( CopyStageAction ):
	"""
	进入防守副本
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		roleBase = params["baseMailbox"]
		roleBase.cell.fangShou_onEnterCopy()

class CopyStageAction_FangShou_onLeaveCopy( CopyStageAction ):
	"""
	离开防守副本
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		roleBase = params["baseMailbox"]
		roleBase.cell.fangShou_onLeaveCopy()

class CopyStageAction_FangShou_onGearStarting( CopyStageAction ):
	"""
	防守副本机关开启
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		areaName = params["areaName"]
		for playerBase in spaceEntity._players :
			playerBase.cell.fangShou_addAreaGearStartMark( areaName )
		fangShouTowers = spaceEntity.queryTemp( "FangShouTowers" )
		if fangShouTowers and fangShouTowers.has_key( areaName ) :
			for towerID in fangShouTowers[ areaName ] :
				Love3.callEntityMedthod( towerID, "effectStateDec", ( csdefine.EFFECT_STATE_ALL_NO_FIGHT, ) )

class CopyStageAction_FangShou_initSpaceData( CopyStageAction ):
	"""
	防守副本数据初始化
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )								# 开始时间
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, Const.COPY_FANG_SHOU_LAST_TIME )				# 持续时间
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, Const.COPY_FANG_SHOU_MONSTER_TOTALS )	# 剩余小怪
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, Const.COPY_FANG_SHOU_BOSS_TOTALS )			# 剩余BOSS
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_WAVE, Const.COPY_FANG_SHOU_MONSTER_WAVE_MAX )		# 剩余怪物波数
		BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NPC_HP_PRECENT, 100 )									# NPC血量百分比

class CopyStageAction_FangShou_onNpcHPChanged( CopyStageAction ):
	"""
	防守副本NPC血量改变处理
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		hp = params["hp"]
		hp_max = params["hp_max"]
		currentPercent = int( hp * 1.0 / hp_max * 100 )
		lastPercent = int( spaceEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_NPC_HP_PRECENT ) )
		if currentPercent != lastPercent :
			BigWorld.setSpaceData( spaceEntity.spaceID, csconst.SPACE_SPACEDATA_NPC_HP_PRECENT, currentPercent )

class CopyStageAction_FangShou_onTowerCreate( CopyStageAction ):
	"""
	防守副本防御塔创建时记录该防御塔的 id
	"""
	def __init__( self ):
		CopyStageAction.__init__( self )

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		CopyStageAction.init( self, section )

	def do( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	执行此 CopyStageEvent 的 spaceEntity
		@type	spaceEntity ：	空间 entity
		@param	params		:	副本事件的额外参数 （ 做此支持是为了得到副本事件的动态数据 ）
		@type	params		 :	PY_DICT
		"""
		currentArea = params["currentArea"]
		towerID = params["towerID"]
		towers = spaceEntity.queryTemp( "FangShouTowers", None )
		if towers == None :
			spaceEntity.setTemp( "FangShouTowers", { Const.COPY_FANG_SHOU_AREA_FIRST : [], \
													 Const.COPY_FANG_SHOU_AREA_SECOND : [], \
													 Const.COPY_FANG_SHOU_AREA_THRID : [], \
													 Const.COPY_FANG_SHOU_AREA_FORTH : [], } )
		towers = spaceEntity.queryTemp( "FangShouTowers" )
		towers[ currentArea ].append( towerID )

# --------------------------------------------------------------------
# 防守副本结束
# --------------------------------------------------------------------
# -*- coding: gb18030 -*-

# $Id: AIBase.py,v 1.10 2008-05-04 09:05:21 kebiao Exp $

import sys
import csstatus
import Resource.AIData
from bwdebug import *
from AIEAISet import AIEAISet
from AISAISet import AISAISet
from AISetSystemDefLevel import AISetSystemDefLevel
from AISetSystemTempLevel import AISetSystemTempLevel
g_aiActions = Resource.AIData.aiAction_instance()
g_aiConditions = Resource.AIData.aiConditon_instance()
from CPUCal import CPU_CostCal
import csdefine
	
class AIBase:
	def __init__( self ):
		self._id = 0							# AI 的 id  int
		self._name = ""							# AI 的 名称 string
		self._conditions = []					# AI 的 条件 instance of the AICondition of array
		self._actions = []						# AI 的 执行动作 instance of the AIAction of array
		self._activeRate = 100					# AI的活动概率， 默认100%
		self._duration = -1						# AI的持续时间，默认为-1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		self._id = section["id"].asInt
		self._name = section.readString( "name" )
		self._activeRate = section.readInt( "activeProb" )
		if section.has_key( "duration" ):
			self._duration = section.readFloat( "duration" )

		if section.has_key( "condition" ):
			for sec in section[ "condition" ].values():
				if sec.has_key( "isActivated" ) and sec[ "isActivated" ].asInt == 0:
					continue
				inst = g_aiConditions[ sec["id"].asInt ]()
				inst.setAIDataID( self._id )
				inst.init( sec )
				self._conditions.append( inst )

		if section.has_key( "action" ):
			for sec in section[ "action" ].values():
				if sec.has_key( "isActivated" ) and sec[ "isActivated" ].asInt == 0:
					continue
				try:
					inst = g_aiActions[ sec["id"].asInt ]()
				except KeyError, errstr:
					ERROR_MSG( "%i: no such ai action. action id = %i." % ( self._id, sec["id"].asInt ) )
					continue
				try:
					inst.setAIDataID( self._id )
					inst.init( sec )
				except Exception, errstr:
					ERROR_MSG( "%i: action(id = %i) init error." % ( self._id, sec["id"].asInt ) )
					sys.excepthook(*sys.exc_info())
					continue

				self._actions.append( inst )

	def getID( self ):
		"""
		取得AI id
		"""
		return self._id

	def getName( self ):
		"""
		取得AI名称
		"""
		return self._name

	def getActiveRate( self ):
		"""
		取得AI执行概率
		"""
		return self._activeRate

	def getDuration( self ):
		"""
		取得AI执行时间
		"""
		return self._duration

	def reset( self, entity ):
		"""
		vitural method
		重置此AI
		"""
		pass

	def check( self, entity ):
		"""
		vitural method
		@param	entity	: 	执行此AI的entity
		@type	entity	:	entity
		"""
		# 判断是否满足所有条件
		for condtion in self._conditions:
			CPU_CostCal( csdefine.CPU_COST_AI_SC, csdefine.AI_CONDITION, condtion.getID() )
			result = condtion.check( self, entity )
			CPU_CostCal( csdefine.CPU_COST_AI_SC, csdefine.AI_CONDITION, condtion.getID() )
			if not result:
				nTitle=getattr(entity,"title")
				if nTitle == "debug" or entity.queryTemp("debug",0) == 1:
					DEBUG_MSG_FOR_AI( entity, "    条件判定失败，条件ID: %i,条件索引: %i"%( condtion.getID(), self._conditions.index( condtion )+1 ),"AI_DEBUG_LOG: (NPCID %i className %s ) AICondtion( ID %i, index %i ) result False" % ( entity.id, entity.className, condtion.getID(), self._conditions.index( condtion )+1 ) )
				return False
		return True

	def do( self, entity ):
		"""
		vitural method
		@param	entity	: 	执行此AI的entity
		@type	entity	:	entity
		"""
		if self._duration != -1 and self._duration > 0:
			entity.nextAIInterval.append( self._duration )

		# 执行所有行为
		for action in self._actions:
			CPU_CostCal( csdefine.CPU_COST_AI_SC, csdefine.AI_ACTION, action.getID() )
			action.do( self, entity )
			CPU_CostCal( csdefine.CPU_COST_AI_SC, csdefine.AI_ACTION, action.getID() )

	def attach( self, entity ):
		"""
		vitural method
		@param	entity	: 	执行此AI的entity
		@type	entity	:	entity
		"""
		pass

	def detach( self, entity ):
		"""
		vitural method
		@param	entity	: 	执行此AI的entity
		@type	entity	:	entity
		"""
		pass

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看AIObjImpl；
		此接口默认返回：{ "param": None }，即表示无动态数据。
		
		@return: 返回一个AI类型的字典。AI类型详细定义请参照defs/alias.xml文件
		"""
		return {  "param" : None }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的ai。详细字典数据格式请参数AIObjImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的ai中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。
		
		@type data: dict
		"""
		return self

#
# $Log: not supported by cvs2svn $
# Revision 1.9  2008/04/22 04:16:34  kebiao
# 添加了初始化部分
#
# Revision 1.8  2008/04/18 07:17:43  kebiao
# 去掉SAI EAI的设置 由配置相应动作去决定
#
# Revision 1.7  2008/04/02 03:43:42  kebiao
# 去掉支持配置一次性运行属性
#
# Revision 1.5  2008/03/29 07:04:50  kebiao
# configureEAIID 设置为list
#
# Revision 1.4  2008/03/29 03:57:23  kebiao
# 调整接口及部分属性 SAI，EAI的操作方式
#
# Revision 1.3  2008/03/29 02:10:42  kebiao
# no message
#
# Revision 1.2  2008/03/27 09:11:10  kebiao
# 去掉isActive相关支持
#
# Revision 1.1  2008/03/25 07:43:09  kebiao
# 添加AI相关
#
#
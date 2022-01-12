# -*- coding: gb18030 -*-
#
"""
游戏公告服务器支持

游戏服务器每10分钟向数据库请求一次数据，方式是每个小时的10分20分...60分。如当前为55分，那么下次取数据的时间为60分，
所以需要在5分钟内修改数据，超过60分即生效。（建议每次设定都提前10分钟，如 20分时发布某公告，那么在10分之前写入数据）

与北京商量后该模块遵循以下原则:
1.开始时间不能大于结束时间。
2.已经开始的活动或者公告不能修改.但是可以删除。在游戏服务器获取数据后立刻相应的处理。公告不再发送，活动立刻停止。

"""

import BigWorld
import Const
import time
import csdefine
import Love3
from bwdebug import *
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

class GameBroadcast(BigWorld.Base):
	"""
	定时日志任务
	"""
	def __init__( self ):
		"""
		初始化
		"""
		self.registerGlobally( "GameBroadcast", self._onRegisterManager )		#注册自己到全局中
		self.broadcastDatas = {}
		self.actionDatas    = {}
		self.updateTime		= 0
		self.timer_id		= 0

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register GameBroadcast Fail!" )
			self.registerGlobally( "GameBroadcast", self._onRegisterManager )
		else:
			BigWorld.globalData["GameBroadcast"] = self		# 注册到所有的服务器中
			INFO_MSG("GameBroadcast Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
					  	"GameBroadcast" : "updataBroadcast",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )

	def updataBroadcast( self ):
		"""
		@define method
		更新公告数据
		"""
		BigWorld.executeRawDatabaseCommand( "call GAMEBROADCAST()", self.updateDatas )

	def updateDatas( self, results, rows, errstr ):
		"""
		刷新数据
		"""
		if errstr:
			ERROR_MSG( "update gamebroadcast datas  failed, please check the mysql Stored Procedure is correct: %s" % errstr  )
			return

		sql = "select id,operationstart,distance,operationend,actiontype,content from custom_GameBroadcast where mark = 1"
		BigWorld.executeRawDatabaseCommand( sql, self.onGetDatas )


	def onGetDatas( self, results, rows, errstr):
		"""
		获取了排名数据
		"""
		if errstr:
			ERROR_MSG( "get gamebroadcast datas  failed, please check the mysql Stored Procedure is correct: %s" % errstr  )
			return
		self.updateTime = time.time()
		run = False		# 标记此次数据是否有添加
		for result in results:
			key = int(result[0])
			atype = int(result[4])
			pdict = {}
			if  atype == 0:		# 喊话类型的数据
				pdict = self.broadcastDatas
			elif atype == 1:			# 活动类型的数据
				pdict = self.actionDatas

			if  pdict.has_key( key ):
				pdict[key]["version"]	=	self.updateTime
			else:
				pdict[key] = { "operationstart"	:	result[1],
								"interval"		:	int(result[2]),
								"operationend"	:	result[3],
								"content"		:	result[5],
								"version"		:	self.updateTime,
								"executeState"	:	0,
								}
				run = True

		if not self.timer_id and run:
			self.timer_id = self.addTimer( 0, 1.0 )

	def date2time( self, date ):
		"""
		日期转秒时间
		"""
		tdate =time.strptime(date,"%Y-%m-%d %H:%M:%S")
		return time.mktime(tdate )

	def onTimer( self, id, userArg ):
		"""
		"""
		INFO_MSG( "=======================================================>>>>>>>>>>b" )
		now = time.time()
		run = False
		for key,value in self.broadcastDatas.items():
			startTime = self.date2time(value["operationstart"])
			endTime   = self.date2time(value["operationend"])
			if value["version"] != self.updateTime:
				INFO_MSG( "version 不匹配 不发送该公告" )
				self.broadcastDatas.pop(key)
				continue
			if now >= endTime:
				INFO_MSG( "公告时间结束。不再发送" )
				self.broadcastDatas.pop(key)
				continue	# 已经结束不做处理
			if now >= startTime:
				interval = now - ( value["executeState"] + value["interval"])
				if interval >=0:
					if interval <= value["interval"]:		# 表示上一次发送时间和现在间隔未超过一个间隔时间
						Love3.g_baseApp.anonymityBroadcast( value["content"], [] )
						value["executeState"] = now
						INFO_MSG( "时间正常,发送公告" )
					else:		# 修正发送时间
						value["executeState"] = now - ( now - startTime ) % value["interval"]
						INFO_MSG( "修正公告时间" )
			run = True

		global actions
		for key,value in self.actionDatas.items():
			startTime = self.date2time(value["operationstart"])
			endTime   = self.date2time(value["operationend"])
			if value["version"] != self.updateTime:					# 表示任务被终止
				if value["executeState"] == 1:						# 表示还未关闭
					actions[ value["content"] ].onEnd()				# 结束掉
					value["executeState"] = 0
					INFO_MSG( "status = 1, 关闭活动" )
				self.actionDatas.pop(key)
				continue
			if now >= endTime:										# 如果已经到结束时间
				if value["executeState"] == 1:						# 表示还未关闭
					actions[ value["content"] ].onEnd()					# 结束掉
					value["executeState"] = 0
					INFO_MSG( "时间到，关闭活动" )
				self.actionDatas.pop(key)
				continue
			if now >= startTime:									# 在执行时间内
				if value["executeState"] == 0:						# 表示还未开始执行
					actions[ value["content"] ].onBegin()			# 开始活动
					value["executeState"] = 1
					INFO_MSG( "开启活动" )
			run = True
		if not run:
			INFO_MSG( "delteTimer==============>>>>" )
			self.delTimer( self.timer_id )
			self.timer_id = 0



class Action_SysMultExpMgr:
	"""
	多倍经验
	"""
	@classmethod
	def onBegin( self ):
		"""
		活动开始
		"""
		BigWorld.globalData["SysMultExpMgr"].onStart2()

	@classmethod
	def onEnd( self ):
		"""
		活动结束
		"""
		BigWorld.globalData["SysMultExpMgr"].onEnd2()

class Action_LuckyBoxActivityMgr:
	"""
	天降宝盒
	"""
	@classmethod
	def onBegin( self ):
		"""
		活动开始
		"""
		BigWorld.globalData["LuckyBoxActivityMgr"].onStartLuckyBox()

	@classmethod
	def onEnd( self ):
		"""
		活动结束
		"""
		BigWorld.globalData["LuckyBoxActivityMgr"].onEndLuckyBox()


actions = {
			"Action_SysMultExpMgr" : Action_SysMultExpMgr,
			"Action_LuckyBoxActivityMgr" : Action_LuckyBoxActivityMgr,
			}
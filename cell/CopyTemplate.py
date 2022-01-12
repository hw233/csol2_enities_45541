# -*- coding: gb18030 -*-

# ------------------------------------------------
# from engine
import BigWorld
# ------------------------------------------------
# from common
from Function import Functor
from bwdebug import WARNING_MSG,ERROR_MSG
# ------------------------------------------------
# from cell
from SpaceCopy import SpaceCopy
import Const

# ------------------------------------------------


class CopyTemplate( SpaceCopy ):
	
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		self.copyUserTimers = {}
		self._delayActionUserArg = Const.SPACE_TIMER_USER_ARG_MAX
		self.getScript().doFirstStage( self )
	
	def addUserTimer( self, start, interval = 0.0, uArg = 0,  params = {} ) :
		"""
		# 添加用户自定义timer
		# 此函数的添加用于包装拓展引擎 addTimer 方法的功能，方便使用。
		# 使用该方法添加的 timer，cancel 时需要使用 cancelCallbackTimer 方法予以撤销。
		# 当然使用者也可以继续使用 addTimer 方法，但需注意对应修改相应的 onTimer 方法。
		# 但建议后续继承者添加和撤销 timer 行为时使用 CopyStageAction12 和 CopyStageAction13，尽量避免重写副本脚本。
		
		@param	start			:	开始第一次回调时间
		@type	start			:	FLOAT
		@param	callbackName 	:	回调函数的名称，需在使用该方法的 spaceScript 上定义，格式为 def callbackName( self, selfEntity, params ) :
		@type	callbackName 	:	STRING
		@param	interval		:	回调时间间隔
		@type	interval		:	FLOAT
		@param	params			:	回调函数的参数
		@type	params			:	PY_DICT
		
		"""
		if uArg == 0 :
			self._delayActionUserArg += 1
			uArg = self._delayActionUserArg
		
		params["userArg"] = uArg
		timerID =  self.addTimer( start, interval, uArg )
		if interval == 0 :
			params["autoCancel"] = True
		self.copyUserTimers[ uArg ] = ( timerID, params )
		return uArg
	
	def onTeleportReady( self, baseMailbox ):
		"""
		define method
		此接口用于通知角色加载地图完毕，可以移动了，可以正常和其他游戏内容交流。
		@param baseMailbox: 要离开此space的entity mailbox
		"""
		self.getScript().onTeleportReady( self, baseMailbox )
	
	def onTimer( self, timerID, userArg ):
		"""
		# 覆盖底层的onTimer()处理机制
		"""
		if userArg in self.copyUserTimers :
			params = self.copyUserTimers[ userArg ][1]
			self.getScript().onTimer( self, timerID, userArg, params )
			if params.has_key( "autoCancel" ) :
				del self.copyUserTimers[ userArg ]
	
	def hasUserTimer( self, uArg ) :
		"""
		判断是否有某一用户自定义timer
		"""
		return uArg in self.copyUserTimers
	
	def cancelUserTimer( self, uArg ) :
		"""
		撤销用户自定义timer
		"""
		try :
			timerID = self.copyUserTimers[ uArg ][0]
		except :
			ERROR_MSG( "the uArg %s timer cant't found. " % uArg )
			return
		self.cancel( timerID )
		del self.copyUserTimers[ uArg ]
	
	def onDestroy( self ):
		"""
		cell 被删除时发生
		"""
		self.copyUserTimers = {}
		SpaceCopy.onDestroy( self )
	
	def getCopyShareTempMapping( self ) :
		return self.copyShareTempMapping
	
	def setCopyShareTemp( self, key, value ) :
		"""
		添加一条副本共享数据
		此处添加的 key 都要在 ObjectScripts.CopyTemplate.py 文件中定义，方便后续查看。
		
		@param   key: 任何PYTHON原类型(建议使用字符串)
		@param value: 任何PYTHON原类型(建议使用数字或字符串)
		"""
		self.copyShareTempMapping[ key ] = value
	
	def removeCopyShareTemp( self, key ) :
		"""
		移除一条副本共享数据
		"""
		self.copyShareTempMapping.pop( key, None )
	
	def queryCopyShareTemp( self, key, default = None ) :
		"""
		根据关键字查询副本共享数据 copyShareTempMapping 中与之对应的值
		@return: 如果关键字不存在则返回 default 值
		"""
		try :
			return self.copyShareTempMapping[ key ]
		except KeyError :
			return default
	
	def popCopyShareTemp( self, key, default = None ) :
		"""
		移除并返回一个关键字为 key 的副本共享数据
		@return : 如果关键字不存在则返回 default 值
		"""
		return self.copyShareTempMapping.pop( key, default )
	
	
# -*- coding: gb18030 -*-

from bwdebug import *

# ------------------------------------------------------------------------------
# Class ActionMgr:
# 动作管理器
# ------------------------------------------------------------------------------
class ActionMgr:
	__instance = None

	def __init__( self ):
		assert ActionMgr.__instance is None

	@classmethod
	def instance( SELF ):
		if SELF.__instance is None:
			SELF.__instance = ActionMgr()
		return SELF.__instance

	def playAction( self, model, actionName, time = 0.0, callback = None ):
		"""
		在指定时间后给指定模型播放一个动作并回调callback
		@type		model		: pyModel
		@param		model		: 模型
		@type		actionName	: String
		@param		actionName	: 动画名字
		@type		time		: Float
		@param		time		: 延迟播放动作时间
		@type		callback	: Func
		@param		callback	: 回调的函数
		@return					: None
		"""
		if model is None:
			if callable( callback ):
				callback()
			return
		if not model.inWorld:
			if callable( callback ):
				callback()
			return
		if not model.hasAction( actionName ):
			ERROR_MSG( "Model(%s) can't find action(%s)" %( model.sources, actionName ) )
			if callable( callback ):
				callback()
			return
		model.action( actionName )( time, callback )


	def stopAction( self, model, actionName ):
		"""
		停止指定模型指定动作
		@type		model		: pyModel
		@param		model		: 模型
		@type		actionName	: String
		@param		actionName	: 动画名字
		@return					: None
		"""
		if model is None: return
		if not model.inWorld: return
		if not model.hasAction( actionName ):
			ERROR_MSG( "Model(%s) can't find action(%s)" %( model.sources, actionName ) )
			return
		model.action( actionName ).stop()

	def playActions( self, model, actionNames, time = 0.0, callbacks = [] ):
		"""
		在指定时间后给指定模型播放一个动作序列并回调，并支持每个动作完成回调
		@type		model		: pyModel
		@param		model		: 模型
		@type		actionNames	: List of String
		@param		actionNames	: 动画名字列表
		@type		time		: Float
		@param		time		: 回调延迟时间
		@type		callback	: Func
		@param		callback	: 回调的函数
		@return					: None
		"""
		if model is None:
			for callback in callbacks:
				if callable( callback ):
					callback()
			return
		if not model.inWorld:
			for callback in callbacks:
				if callable( callback ):
					callback()
			return

		actionNamesCount = len( actionNames )
		if actionNamesCount == 0:
			for callback in callbacks:
				if callable( callback ):
					callback()
			return
		callbackTemps = list( callbacks )
		callbacksCount = len( callbackTemps )
		if callbacksCount < actionNamesCount:
			callbackTemps.extend( [None] * ( actionNamesCount - callbacksCount ) )

		data = zip( actionNames, callbackTemps )
		codeList = [ "action('%s')( %f, callbackTemps[%i] )" %( k[0], time, index ) for index, k in enumerate( data ) ]
		codeString = "model."
		codeString += ".".join( codeList )
		try:
			eval( codeString )
		except Exception, err :
			ERROR_MSG( "Model(%s) play actions(%s) error!" %( model.sources, actionNames ) )
			for callback in callbacks:
				if callable( callback ):
					callback()

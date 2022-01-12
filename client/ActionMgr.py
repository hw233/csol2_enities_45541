# -*- coding: gb18030 -*-

from bwdebug import *

# ------------------------------------------------------------------------------
# Class ActionMgr:
# ����������
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
		��ָ��ʱ����ָ��ģ�Ͳ���һ���������ص�callback
		@type		model		: pyModel
		@param		model		: ģ��
		@type		actionName	: String
		@param		actionName	: ��������
		@type		time		: Float
		@param		time		: �ӳٲ��Ŷ���ʱ��
		@type		callback	: Func
		@param		callback	: �ص��ĺ���
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
		ָֹͣ��ģ��ָ������
		@type		model		: pyModel
		@param		model		: ģ��
		@type		actionName	: String
		@param		actionName	: ��������
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
		��ָ��ʱ����ָ��ģ�Ͳ���һ���������в��ص�����֧��ÿ��������ɻص�
		@type		model		: pyModel
		@param		model		: ģ��
		@type		actionNames	: List of String
		@param		actionNames	: ���������б�
		@type		time		: Float
		@param		time		: �ص��ӳ�ʱ��
		@type		callback	: Func
		@param		callback	: �ص��ĺ���
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

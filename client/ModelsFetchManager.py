# -*- coding: gb18030 -*-

"""
ģ�ͼ��ع���ģ�顣
Ŀ�꣺�������ṩһ���Թؼ��ֶ�Ӧ��ģ��·���ͻص���
�������ڲ��������ϸ�ڣ����ȫ�����غ�ص������ߵĻص�������
"""

import BigWorld
from bwdebug import *
from Function import Functor

class ModelsFetchTask:
	"""
	ģ�ͼ�����
	ʹ�÷�����
	def callbackFunc( models_dict ):
		print models_dict
	task = ModelsFetchTask( hair = "avatar/nvjianke/hair.model",
						body = ( "avatar/nvjianke/shangshen_l000.model", "avatar/nvjianke/shoutao_l010.model", ... ) )
	task = ModelsFetchTask( {"hair" : "avatar/nvjianke/hair.model",
						"body" : ( "avatar/nvjianke/shangshen_l000.model", "avatar/nvjianke/shoutao_l010.model", ... ) } , {"":} )
	task.do( callbackFunc )
	"""
	def __init__( self, *args, **key_work ):
		"""
		"""
		self._models = {}
		self._callbackFunc = None
		self.loaded = False		# ��ʾ�Ƿ��Ѽ������

		for arg in args:
			assert isinstance( arg, dict ), args
			self._models.update( arg )
		self._models.update( key_work )

		for key, val in self._models.iteritems():
			if isinstance( val, str ):
				self._models[key] = ( val, )
			else:
				assert isinstance( val, ( tuple, list ) ), self._models

	def do( self, callback ):
		"""
		@param callback: callback function describe as "def func( model_dict )"
		"""
		assert self.loaded == False, self._models
		self._callbackFunc = callback
		self._fetchOne()

	def _fetchOne( self ):
		"""
		ÿ�δӺ�̨�м���һ��Model
		"""
		for key, val in self._models.iteritems():
			if isinstance( val, ( tuple, list ) ):
				params = list( val )
				if len( params ) == 0: params.append( "" )
				callback = Functor( self._onFetchCallback, key )
				params.append( callback )
				BigWorld.fetchModel( *params )
				return
		if callable( self._callbackFunc ):
			self.loaded = True
			self._callbackFunc( self._models )

	def _onFetchCallback( self, key, model ):
		"""
		Model������ɻص��ӿ�
		"""
		if model is None:
			msg = "\nCan't build models below:\n"
			paths = self._models[key]
			for path in paths:
				msg += 5 * "\t" + path + "\n"
			DEBUG_MSG( msg )

		self._models[key] = model
		self._fetchOne()

class ModelsFetchManager:
	"""
	ͳһ��ģ�ͼ��ع�������
	�÷���
	def callbackFunc( models_dict ):
		print models_dict
	ModelFetchManager.instance().fetchModels( hair = "avatar/nvjianke/hair.model",
							body = ( "avatar/nvjianke/shangshen_l000.model", "avatar/nvjianke/shoutao_l010.model", ... ),
							callback )
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		assert ModelsFetchManager._instance is None
		self._tasks = []		# [ ( ModelsFetchTask, callback, entityID ), ... ]
		self._lastTask = None	# ���ڼ�¼��ǰ���ڼ��ص�ģ��

	@classmethod
	def instance( SELF ):
		if SELF._instance is None:
			SELF._instance = SELF()
		return SELF._instance

	def fetchModels( self, entityID, callback = None, *args, **key_work ):
		"""
		@param callback: see also ModelsFetchTask::do()
		"""
		task = ModelsFetchTask( *args, **key_work )

		if self._lastTask is None:
			self._lastTask = ( task, callback, entityID )
			task.do( self._onFetchCallback )
		else:
			self._tasks.append( ( task, callback, entityID ) )

	def _onFetchCallback( self, models_dict ):
		"""
		"""
		callback = self._lastTask[1]
		if callable( callback ):
			try:
				callback( models_dict )
			except:
				pass

		if len( self._tasks ):
			self._lastTask = self._tasks.pop( 0 )	# �Ƚ��ȳ�
			self._lastTask[0].do( self._onFetchCallback )	
		else:
			self._lastTask = None

	def freeFetchModelTask( self, entityID ):
		"""
		ͨ��entityID�ͷ�һЩ����
		"""
		for index in xrange( len( self._tasks ) - 1, -1, -1 ):
			task = self._tasks[index]
			if task == self._lastTask: continue
			if task[2] == entityID:
				self._tasks.pop( index )

	def resetFetchModelTask( self ):
		"""
		��ռ�������
		"""
		self._lastTask = None
		self._tasks = []

# ModelsFetchManager.py

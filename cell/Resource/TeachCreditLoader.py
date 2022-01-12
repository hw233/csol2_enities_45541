# -*- coding: gb18030 -*-


import Language
from bwdebug import *
from config.server import LevelMapTeachCredit


class TeachCreditLoader:
	"""
	称号配置加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert TeachCreditLoader._instance is None
		TeachCreditLoader._instance = self
		self._data = {}
		for item in  LevelMapTeachCredit.Datas:
			self._data[item["level"]] = { "teachCredit":item["teachCredit"], "exp":item["exp"], "money":item["money"] }
			
	def getTeachCredit( self, level ):
		"""
		根据级别获得对应的功勋值
		
		@param level: 级别
		"""
		try:
			return self._data[level]["teachCredit"]
		except KeyError:
			ERROR_MSG( "level %i has no teachCredit." % ( level ) )
			return 0
			
	def getExp( self, level ):
		"""
		根据级别获得对应的功勋值
		
		@param level: 级别
		"""
		try:
			return self._data[level]["exp"]
		except KeyError:
			ERROR_MSG( "level %i has no exp." % ( level ) )
			return 0
			
	def getMoney( self, level ):
		"""
		根据级别获得对应的功勋值
		
		@param level: 级别
		"""
		try:
			return self._data[level]["money"]
		except KeyError:
			ERROR_MSG( "level %i has no money." % ( level ) )
			return 0
			
	@classmethod
	def instance( SELF ):
		"""
		"""
		if SELF._instance is None:
			SELF._instance = TeachCreditLoader()
		return SELF._instance
		

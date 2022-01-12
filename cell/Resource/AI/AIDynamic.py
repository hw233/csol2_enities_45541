# -*- coding: gb18030 -*-

# $Id: AIDynamic.py,v 1.1 2008-04-22 04:15:58 kebiao Exp $

import BigWorld
import csstatus
import csdefine
from AIBase import *
from bwdebug import *

class AIDynamic( AIBase ):
	"""
	存有动态数据的AI， 此AI支持临时记录数据，或者改变原有基础数据
	"""
	def __init__( self ):
		AIBase.__init__( self )
		self._buffer = {}				# 用于记录动态数据的缓冲器
		
	def init( self, section ):
		"""
		virtual method
		@param	section	: 	存储数据的数据段
		@type	section	:	PyDataSection
		"""
		AIBase.init( self, section )

	def setTemp( self, key, val ):
		"""
		对该AI设置临时的数据
		@param key: 该数据记录的关键字
		@param val: 该条数据记录的值 建议设置为python类型，  不包括任何实例
		"""
		self._buffer[ key ] = val
		
	def removeTemp( self, key ):
		"""
		对该AI删除临时的数据
		@param key: 该数据记录的关键字
		"""
		if self._buffer.has_key( key ):
			del self._buffer[ key ]

	def popTemp( self, key, defRetVal ):
		"""
		对该AI删除临时的数据
		@param key: 该数据记录的关键字
		@param defRetVal: 设置如果没有找到存在的数据 默认返回某值
		"""
		if self._buffer.has_key( key ):
			val = self._buffer[ key ]
			del self._buffer[ key ]
			return val
		return defRetVal
		
	def queryTemp( self, key, defRetVal ):
		"""
		对该AI删除临时的数据
		@param key		: 该数据记录的关键字
		@param defRetVal: 设置如果没有找到存在的数据 默认返回某值
		"""
		if self._buffer.has_key( key ):
			return self._buffer[ key ]
		return defRetVal
		
	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看AIObjImpl；
		此接口默认返回：{ "param": None }，即表示无动态数据。
		
		@return: 返回一个AI类型的字典。AI类型详细定义请参照defs/alias.xml文件
		"""
		return {  "param" : self._buffer }
		
	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的ai。详细字典数据格式请参数AIObjImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的ai中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。
		
		@type data: dict
		"""
		obj = self.__class__()
		obj.__dict__.update( self.__dict__ )
		obj._buffer = data[ "param" ]
		return obj
		
#
# $Log: not supported by cvs2svn $
#
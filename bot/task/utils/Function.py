# -*- coding: gb18030 -*-
#
# $Id: Function.py,v 1.23 2008-08-26 02:29:59 kebiao Exp $

"""
公共函数模块
"""

import re
import os
import types
import inspect
import random
import time
import math
import zlib
import base64


def getMethodName( method ) :
	"""
	获取方法名
	@type				method : method
	@param				mehtod : 必须是实例方法或类方法
	@rtype					   : str
	@return					   : 返回方法名
	"""
	assert inspect.ismethod( method ), \
		"%s is not a method" % str( method )				# 必须是实例方法或类方法
	funcName = method.im_func.func_name						# 获取方法名
	imSelf = method.im_self									# 获取方法所属的实例
	if hasattr( imSelf, funcName ) :						# 如果在实例中能直接找到方法
		return funcName										# 则说明不是 private 方法，直接返回方法名

	if type( imSelf ) is types.ClassType or \
		type( imSelf ) is types.TypeType :					# 如果是类方法
			clses = inspect.getmro( method.im_self )		# 则，通过 im_self 获取方法实例的所有基类
	else :
		clses = inspect.getmro( method.im_class )			# 则，通过 im_class 获取方法实例的所有基类
	for cls in clses :										# 通过方法名逐个基类寻找
		methodName = "_%s%s" % ( cls.__name__, funcName )	# 为私有方法添加类前缀
		methodName = re.sub( "^_*", "_", methodName )
		tmpMethod = getattr( imSelf, methodName, None )		# 获取私有方法
		if tmpMethod is None : continue						# 如果私有方法不属于此类，则继续
		if tmpMethod != method : continue					# 如果遇到相同名称的另一个基类中的私有方法，则继续
		return methodName									# 否则，返回找到的方法名
	raise "%s is not a method" % str( method )				# 理论上这里不会被执行


# --------------------------------------------------------------------
class Functor:
	"""
	构造任意参数的Callback函数类。
		@ivar _fn:			Callback函数
		@type _fn:			function
		@ivar _args:		参数
		@type _args:		tuple
	"""

	def __init__( self, fn, *args ):
		"""
		构造函数。
			@param fn:			Callback函数
			@type fn:			function
			@param args:		参数
			@type args:			tuple
		"""
		self._fn = fn
		self._args = args

	def __call__( self, *args ):
		"""
		调用Callback函数fn。
			@param args:		参数
			@type args:			tuple
			@return:			Callback函数的返回值
		"""
		return self._fn( *( self._args + args ) )


# --------------------------------------------------------------------
def random_position(center, range):
	"""在指定位置周围生成随机位置"""
	r_yaw = random.random() * 2 * math.pi
	r_range = random.random() * range

	x, y, z = center
	x += math.sin(r_yaw) * r_range
	z += math.cos(r_yaw) * r_range

	return (x, y, z)

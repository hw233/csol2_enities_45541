# -*- coding: gb18030 -*-
#
# $Id: Function.py,v 1.23 2008-08-26 02:29:59 kebiao Exp $

"""
��������ģ��
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
	��ȡ������
	@type				method : method
	@param				mehtod : ������ʵ���������෽��
	@rtype					   : str
	@return					   : ���ط�����
	"""
	assert inspect.ismethod( method ), \
		"%s is not a method" % str( method )				# ������ʵ���������෽��
	funcName = method.im_func.func_name						# ��ȡ������
	imSelf = method.im_self									# ��ȡ����������ʵ��
	if hasattr( imSelf, funcName ) :						# �����ʵ������ֱ���ҵ�����
		return funcName										# ��˵������ private ������ֱ�ӷ��ط�����

	if type( imSelf ) is types.ClassType or \
		type( imSelf ) is types.TypeType :					# ������෽��
			clses = inspect.getmro( method.im_self )		# ��ͨ�� im_self ��ȡ����ʵ�������л���
	else :
		clses = inspect.getmro( method.im_class )			# ��ͨ�� im_class ��ȡ����ʵ�������л���
	for cls in clses :										# ͨ���������������Ѱ��
		methodName = "_%s%s" % ( cls.__name__, funcName )	# Ϊ˽�з��������ǰ׺
		methodName = re.sub( "^_*", "_", methodName )
		tmpMethod = getattr( imSelf, methodName, None )		# ��ȡ˽�з���
		if tmpMethod is None : continue						# ���˽�з��������ڴ��࣬�����
		if tmpMethod != method : continue					# ���������ͬ���Ƶ���һ�������е�˽�з����������
		return methodName									# ���򣬷����ҵ��ķ�����
	raise "%s is not a method" % str( method )				# ���������ﲻ�ᱻִ��


# --------------------------------------------------------------------
class Functor:
	"""
	�������������Callback�����ࡣ
		@ivar _fn:			Callback����
		@type _fn:			function
		@ivar _args:		����
		@type _args:		tuple
	"""

	def __init__( self, fn, *args ):
		"""
		���캯����
			@param fn:			Callback����
			@type fn:			function
			@param args:		����
			@type args:			tuple
		"""
		self._fn = fn
		self._args = args

	def __call__( self, *args ):
		"""
		����Callback����fn��
			@param args:		����
			@type args:			tuple
			@return:			Callback�����ķ���ֵ
		"""
		return self._fn( *( self._args + args ) )


# --------------------------------------------------------------------
def random_position(center, range):
	"""��ָ��λ����Χ�������λ��"""
	r_yaw = random.random() * 2 * math.pi
	r_range = random.random() * range

	x, y, z = center
	x += math.sin(r_yaw) * r_range
	z += math.cos(r_yaw) * r_range

	return (x, y, z)

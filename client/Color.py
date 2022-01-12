# -*- coding: gb18030 -*-
#
# $Id: Font.py,v 1.4 2008-03-19 10:31:21 huangyongwei Exp $

"""
��ģ����ʵ����ͨ�������ڶ�����ɫ���ƻ�ȡ���Ӧ����ɫֵ

2009.02.23: writen by huangyongwei
"""

import Language
from AbstractTemplates import Singleton
from bwdebug import *
from config.client import colors

class Colors( Singleton ) :
	def __init__( self ) :
		self.__colors = colors.Datas


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		return "Colors" + self.__colors.__repr__()

	def __str__( self ) :
		return "Colors" + self.__colors.__str__()

	def __iter__( self ) :
		return self.__colors.__iter__()

	def __contains__( self, name ) :
		"""
		�ж���ɫ�����Ƿ����
		"""
		return name in self.__colors

	def __len__( self ) :
		"""
		��ȡ�������ɫ����
		"""
		return self.__colors.__len__()

	def __getitem__( self, name ) :
		"""
		ͨ�������ж������ɫ���ƻ�ȡ���Ӧ����ɫֵ
		@type			name : str
		@param			name : ��ɫ���ƣ��������ж��壩
		@rtype				 : tuple
		@return				 : ��Χ����ɫֵ������alpha ���� 255����( r, g, b, 255 )
		"""
		if name in self.__colors :
			return self.__colors[name]
		ERROR_MSG( "color '%s' is not exist!" % name )
		return ( 255, 255, 255, 255 )

	def __getattr__( self, attrName ) :
		attrs = ( "has_key", "keys", "values", "items", "values", "iteritems", "iterkeys", "itervalues" )
		if attrName in attrs :
			return getattr( self.__colors, attrName )
		raise AttributeError( "AttributeError: '%s' object has no attribute %s" % ( self.__class__.__name__, attrName ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def get( self, name, default = None ) :
		"""
		������ɫ���ƻ�ȡ��ɫ
		@type			name	: str
		@param			name	: ��ɫ����
		@type			default : tupe/Color
		@param			default : Ĭ����ɫ���Ҳ�����ɫʱ����Ĭ����ɫ��
		"""
		if name in self.__colors :
			return self.__colors[name]
		elif default is not None :
			return default
		ERROR_MSG( "color '%s' is not exist!" % name )
		return ( 255, 255, 255, 255 )



# --------------------------------------------------------------------
# global functions
# --------------------------------------------------------------------
def intColor2RGBColor( intColor ) :
	"""
	��������ʽ����ɫֵת��Ϊ RGB ��ɫ
	ע�⣺���ܴ� alpha ֵ
	"""
	r = ( intColor & 0xff0000 ) >> 16
	g = ( intColor & 0x00ff00 ) >> 8
	b = intColor & 0x0000ff
	return r, g, b


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
cscolors = Colors()

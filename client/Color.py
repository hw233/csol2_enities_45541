# -*- coding: gb18030 -*-
#
# $Id: Font.py,v 1.4 2008-03-19 10:31:21 huangyongwei Exp $

"""
该模块是实现了通过创世内定的颜色名称获取其对应的颜色值

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
		判断颜色名字是否存在
		"""
		return name in self.__colors

	def __len__( self ) :
		"""
		获取定义的颜色数量
		"""
		return self.__colors.__len__()

	def __getitem__( self, name ) :
		"""
		通过配置中定义的颜色名称获取其对应的颜色值
		@type			name : str
		@param			name : 颜色名称（在配置中定义）
		@rtype				 : tuple
		@return				 : 四围的颜色值（不过alpha 总是 255）：( r, g, b, 255 )
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
		根据颜色名称获取颜色
		@type			name	: str
		@param			name	: 颜色名称
		@type			default : tupe/Color
		@param			default : 默认颜色（找不到颜色时返回默认颜色）
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
	把整数形式的颜色值转化为 RGB 颜色
	注意：不能带 alpha 值
	"""
	r = ( intColor & 0xff0000 ) >> 16
	g = ( intColor & 0x00ff00 ) >> 8
	b = intColor & 0x0000ff
	return r, g, b


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
cscolors = Colors()

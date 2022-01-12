#
# -*- coding: gb18030 -*-
# $Id: share.py,v 1.2 2008-05-19 04:52:17 huangyongwei Exp $
#

"""
implement various functions shared by all plugins

2008.05.15: writen by huangyongwei
"""

import re
import Language
import csstring
from AbstractTemplates import Singleton
from bwdebug import *
from Color import cscolors, intColor2RGBColor

class DefaultParser( Singleton ) :
	"""
	默认的属性解释器，其能解释的规范如下：
	① 该解释器解释以大括号括回来的属性串
	② 属性键与值的关系通过等号来表达
	③ 多个属性之间以英文分号分隔
	④ 倘若属性值带有分号，则需要以单引号将串括起来
	如："{ aa = 1222; bb = AADFASDF; cc = 'aasdfasdf'; dd = 23,23,5; ee = ( 3, 4, 5 ) }"
	"""

	def __init__( self ) :
		# 括号内容匹配模式
		self.__scopePattern = re.compile( r"\{.*(?<!\\)\}" )
		# 分号分隔匹配模式
		self.__splitPattern = re.compile( r"\w+\s*=\s*[^'].*?(?=;)|\w+\s*=\s*'.*?'|\w+\s*=\s*[^'].*|\w+\s*=\s*'.*" )

		# 整数匹配模式（包括负整数）
		self.__intPattern = re.compile( r"^\d+$|^[\+\-]\d+$" )
		# 浮点数匹配模式（包括负）
		self.__floatPattern = re.compile( r"^\d+$|^[\+\-]\d+$|^[\+\-]{0,1}\d*\.\d+$|^[\+\-]{0,1}\d+\.$" )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getFormatScope( self, text ) :
		"""
		截取格式化文本
		@type				text : str
		@param				text : 格式化所囊括的全部文本
		@rtype					 : tuple
		@return					 : ( 格式化文本, 除去格式化文本后的剩余文本 )
		"""
		wtext = csstring.toWideString( text )					# 这里使用宽字符的目的是防止中文被截断
		match = self.__scopePattern.search( wtext )
		if match is None : return "", text						# 没有大括符，则返回全部文本
		start, end = match.start(), match.end()
		if start != 0 : return "", text							# 不是紧接着大括符，则返回全部文本
		scopeText = wtext[1 : end - 1].strip()					# 格式化文本( 去掉两边的括号 )
		scopeText = scopeText.replace( "\\}", "}" )
		scopeText = csstring.toString( scopeText )
		leaveText = csstring.toString( wtext[end:] )			# 剩余文本
		return scopeText, leaveText

	def getAttrInfos( self, attrsText ) :
		"""
		通过格式化文本获取属性值
		@type				attrsText : str
		@param				attrsText : 格式化文本
		@rtype						  : dict
		@return						  : 格式化属性字典
		"""
		attrs = {}
		strAttrs = self.__splitPattern.findall( attrsText )
		for strAttr in strAttrs :
			strKey, strValue = strAttr.split( "=" )
			strKey = strKey.strip()
			strValue = strValue.strip()
			if strValue.startswith( '\'' ) :
				strValue = strValue[1:-1]
			attrs[strKey] = strValue
		return attrs

	# -------------------------------------------------
	def tranInt( self, strInt, default = None ) :
		"""
		将 int 型字符串转换为 int 类型值
		@type			strInt	: str
		@param			strInt	: 字符串形式的 int
		@type			default : int
		@param			default : 如果转换失败，返回的值
		@rtype					: int
		@return					: int 类型值
		"""
		strInt = strInt.strip()
		eles = self.__intPattern.findall( strInt )
		if len( eles ) == 1 :								# 如果是整数字符串
			return int( strInt )							# 强制类型转换后返回
		else :												# 否则
			f = self.tranFloat( strInt )		 			# 试图首先转换为浮点形式
			if f is not None : return int( f )				# 如果是浮点数，则强制转换为整数返回
		return default

	def tranFloat( self, strFloat, default = None ) :
		"""
		将 int 型字符串转换为 int 类型值
		@type			strInt	: str
		@param			strInt	: 字符串形式的 int
		@type			default : int
		@param			default : 转换失败时返回的值
		@rtype					: int
		@return					: int 类型值
		"""
		strFloat = strFloat.strip()
		eles = self.__floatPattern.findall( strFloat )
		if len( eles ) == 1 :
			return float( strFloat )
		return default

	def tranCustom( self, s, Type, default = None ) :
		"""
		将一个字符串转换为用户自定的类型
		@type				s		: str
		@param				s		: 要转换的值的字符串形式
		@type				Type	: types.Type
		@param				Type	: 指定的类型
		@type				default	: all types
		@param				default	: 转换失败时返回的值
		"""
		if Type is int :
			return self.tranInt( s, default )
		if Type is float :
			return self.tranFloat( s, default )
		try : return Type( s )
		except : return default

	# -------------------------------------------------
	def tranTuple( self, strTuple, types, default = None ) :
		"""
		根据字符串形式的 tuple 获取 tuple
		@type				strTuple : str
		@param				strTuple : 字符串形式的 tuple
		@type				types	 : list
		@param				types	 : 各个元素的类型
		@type				default	 : tuple
		@param				default	 : 解释失败时返回的默认值
		@rtype						 : None / tuple
		@return						 : 如果不是正确 tuple，则返回 None，否则返回转义后的 tuple
		"""
		strTuple = strTuple.strip()
		if strTuple.startswith( '(' ) :								# 如果是有括号的 tuple
			strTuple = strTuple[1:-1]								# 则去掉两边的括号
		strEles = strTuple.split( ',' )								# 拆分各元素
		if len( strEles ) < len( types ) :
			return default

		eles = ()
		for idx, Type in enumerate( types ) :						# 逐个强制类型转换
			strEle = strEles[idx].strip()							# 元素在的字符串形式
			value = self.tranCustom( strEle, Type )					# 调用转换函数
			if value is None : return default						# 转换失败
			eles += ( value, )
		return eles

	def tranColor( self, strColor, defColor = None ) :
		"""
		获取颜色，获取失败则返回 defColor
		@type				strColor : str
		@param				strColor : 颜色串，或系统颜色名字
		@type				defColor : tuple
		@param				defColor : 如果解释失败返回的默认颜色
		@rtype						 : None / tuple
		@return						 : 如果不是正确的颜色串，则返回 None，否则返回颜色值
		"""
		strColor = strColor.lower()
		if strColor in cscolors :
			return cscolors[strColor]

		rgba = self.tranTuple( strColor, 4 * [int] )		# 假设为四维颜色
		if rgba is not None : return rgba
		rgb = self.tranTuple( strColor, 3 * [int] )			# 假设为三维颜色
		if rgb is not None : return rgb

		try :
			return intColor2RGBColor( int( strColor, 16 ) )	# 十六进制颜色
		except :
			pass
		return defColor


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
defParser = DefaultParser()

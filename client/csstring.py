# -*- coding: gb18030 -*-
#
# $Id: Font.py,v 1.4 2008-03-19 10:31:21 huangyongwei Exp $

"""
实现字符串拉杂功能的封装
2010.01.22: writen by huangyongwei
2010.02.02: add KeyCharParser
"""

import re
import csol
from keys import *

# --------------------------------------------------------------------
# 字符与按键转换问题
# --------------------------------------------------------------------
# 英文标点符号
g_en_interpunctions = set( [",", ".", "!", ";", "?", "'", "\"", ":", \
							"(", ")", "[", "]", "{", "}", "<", ">", ] )

# 中文标点符号（不包括破折号和尖括号）
g_ch_interpunctions = set( ["，", "。", "！", "；", "？", "‘", "’", \
							"“", "”", "：" "（", "）", "、", "〔", \
							"〕", "｛", "｝", "《", "》", ] )

# 标点符号
g_interpunctions = set()
g_interpunctions.update( g_en_interpunctions )
g_interpunctions.update( g_ch_interpunctions )

# 特殊符号
g_special_emblems = set( [ "~", "`", "@", "#", "$", "%", "^", "&", \
							"+", "-", "*", "/", "\\", "=", \
							"＋", "－", "×", "＝", \
							"～", "·", "￥", "％", "……", \
							] )

# 所有符号
g_emblems = set()
g_emblems.update( g_interpunctions )
g_emblems.update( g_special_emblems )

class KeyCharParser( object ) :
	"""
	字符解释器
	"""
	__cc_keychar_map = {}													# 键值与字符的映射，False 表示没有按下 shift 键，True 表示按下 shift 键
	__cc_keychar_map[KEY_GRAVE] 		= { False : '`', True : '~' }
	__cc_keychar_map[KEY_1] 			= { False : '1', True : '!' }
	__cc_keychar_map[KEY_2]				= { False : '2', True : '@' }
	__cc_keychar_map[KEY_3]				= { False : '3', True : '#' }
	__cc_keychar_map[KEY_4] 			= { False : '4', True : '$' }
	__cc_keychar_map[KEY_5] 			= { False : '5', True : '%' }
	__cc_keychar_map[KEY_6] 			= { False : '6', True : '^' }
	__cc_keychar_map[KEY_7] 			= { False : '7', True : '&' }
	__cc_keychar_map[KEY_8] 			= { False : '8', True : '*' }
	__cc_keychar_map[KEY_9] 			= { False : '9', True : '(' }
	__cc_keychar_map[KEY_0] 			= { False : '0', True : ')' }
	__cc_keychar_map[KEY_MINUS] 		= { False : '-', True : '_' }
	__cc_keychar_map[KEY_EQUALS]		= { False : '=', True : '+' }
	__cc_keychar_map[KEY_BACKSLASH] 	= { False : '\\', True : '|' }

	__cc_keychar_map[KEY_LBRACKET]		= { False : '[', True : '{' }
	__cc_keychar_map[KEY_RBRACKET]		= { False : ']', True : '}' }
	__cc_keychar_map[KEY_SEMICOLON]		= { False : ';', True : ':' }
	__cc_keychar_map[KEY_APOSTROPHE]	= { False : '\'', True : '\"' }
	__cc_keychar_map[KEY_COMMA]			= { False : ',', True : '<' }
	__cc_keychar_map[KEY_PERIOD]		= { False : '.', True : '>' }
	__cc_keychar_map[KEY_SLASH]			= { False : '/', True : '?' }

	__cc_keychar_map[KEY_SPACE]			= { False : ' ', True : ' ' }

	__cc_keychar_map[KEY_NUMPAD1] 		= { False : '1', True : '1' }
	__cc_keychar_map[KEY_NUMPAD2] 		= { False : '2', True : '2' }
	__cc_keychar_map[KEY_NUMPAD3] 		= { False : '3', True : '3' }
	__cc_keychar_map[KEY_NUMPAD4] 		= { False : '4', True : '4' }
	__cc_keychar_map[KEY_NUMPAD5] 		= { False : '5', True : '5' }
	__cc_keychar_map[KEY_NUMPAD6] 		= { False : '6', True : '6' }
	__cc_keychar_map[KEY_NUMPAD7] 		= { False : '7', True : '7' }
	__cc_keychar_map[KEY_NUMPAD8] 		= { False : '8', True : '8' }
	__cc_keychar_map[KEY_NUMPAD9] 		= { False : '9', True : '9' }
	__cc_keychar_map[KEY_NUMPAD0] 		= { False : '0', True : '0' }
	__cc_keychar_map[KEY_NUMPADPERIOD]	= { False : '.', True : '.' }
	__cc_keychar_map[KEY_NUMPADSLASH]	= { False : '/', True : '/' }
	__cc_keychar_map[KEY_NUMPADSTAR]	= { False : '*', True : '*' }
	__cc_keychar_map[KEY_ADD]			= { False : '+', True : '+' }
	__cc_keychar_map[KEY_NUMPADMINUS]	= { False : '-', True : '-' }

	def __init__( self ) :
		raise TypeError( "the KeyCharParser cannot be instantiated!" )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def keyToChar( SELF, key, shift ) :
		"""
		将键值转换为字符
		@type			key	  : MACRO DEFINATION
		@param			key	  : 在 keys.py 中定义的键值
		@type			shift : bool
		@param			shift : 是否按下 shift 键
		"""
		ch = ''
		chs = keyToString( key )
		#chs = BigWorld.keyToString( key )
		if len( chs ) == 1 :
			ch = chs
			if not ch.isdigit() :						# 如果是字符键
				upper = csol.getKeyState( "CAPSLOCK" )	# 是否按下 capslock 键
				if not( upper ^ shift ) :				# 是否处于小写模式
					ch = ch.lower()
				return ch
		if SELF.__cc_keychar_map.has_key( key ) :		# 其他键
			ch = SELF.__cc_keychar_map[key][shift]
		return ch


# --------------------------------------------------------------------
# 字符串编码问题
# --------------------------------------------------------------------
def toWideString( s ) :
	"""
	将 ascii 转换为 unicude 字符串
	@type				s : str
	@param				s : ascii 字符串
	@rtype				  : unicode
	@return				  : 宽字符串
	"""
	if type( s ) is str :
		return csol.asWideString( s )
	return s

def toString( us ) :
	"""
	将 unicode 字符串转换为 ascii 字符串
	@type				s : unicode
	@param				s : 宽字符串
	@rtype				  : str
	@return				  : ascii 字符串
	"""
	if type( us ) is unicode :
		return csol.asString( us )
	return us


# --------------------------------------------------------------------
# 字符匹配问题
# --------------------------------------------------------------------
__spacePatten = re.compile( toWideString( "[\s　]+" ) )						# 匹配空格的模式
__escEmbs = "".join( [re.escape( toWideString( i ) ) for i in g_emblems] )
__backwardEmbPatten = re.compile( "[%s]+" % __escEmbs )						# 往回查找时匹配标点的模式
__forwardEmbPatten = re.compile( "[%s]+" % __escEmbs )						# 向前查找时匹配标点的模式
__escStartPattern = re.compile( "[%s\s]+" % __escEmbs )						# 匹配首字符是标点的模式
del __escEmbs

def getFirstWordEnd( text ) :
	"""
	获取字符串中第一个单词的结束位置
	规则：以空格结尾标记为单词，该单词囊括其后面的所有空格（纯空格也算一个单词）
	@type			text : basestring( str/unicode )
	@param			text : 任意字符串
	@rtype				 : int
	@return				 : 返回第一个单词的结束索引
	"""
	index = len( text )
	m = __spacePatten.search( text )
	if m : index = m.end()
	m = __forwardEmbPatten.search( text[:index] )
	if m :
		start = m.start()
		index = start
		if start == 0 :								# 首字符是标点
			m = __escStartPattern.search( text )
			if m : index = m.end()
	return index

def getLastWordStart( text ) :
	"""
	获取字符串中最后一个单词的起始位置（如果单词后面有空格，则该单词囊括后面的空格）
	@type			text : basestring( str/unicode )
	@param			text : 任意字符串
	@rtype				 : int
	@return				 : 返回最后一个单词的起始索引
	"""
	rvtext = text[::-1]
	rvtext = rvtext.lstrip()
	index = len( rvtext )
	sm = __spacePatten.search( rvtext )
	if sm : index = sm.start()
	im = __backwardEmbPatten.search( rvtext[:index] )
	if im :
		start = im.start()
		if start == 0 : index = im.end()
		else : index = start
	return len( rvtext ) - index

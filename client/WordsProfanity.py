# -*- coding: gb18030 -*-
#
# $Id: ChatProfanity.py,v 1.7 2008-06-20 06:15:57 wangshufeng Exp $

"""
亵渎词汇处理模块
2010.04.30: tidy up by huangyongwei
"""

import re
import time
import Language
from bwdebug import *
from Language import DECODE_NAME
import csol

MAX_ROW_LENGTH		= 2000

class WordsProfanity:
	__inst = None

	def __init__( self ):
		assert WordsProfanity.__inst is None, "instance already exist in"
		WordsProfanity.__inst = self
		self.__enRePattern = re.compile( "[a-zA-Z0-9]+" ) 		# 英文正则模板
		self.__chRePattern = re.compile( u"[\u4e00-\u9FA5]+" )	# 中文正则模板
		#self.__msgRePattern = None								# 消息过滤正则模板
		#self.__nameRePattern = None								# 角色、宠物名称过滤正则模板
		self.__msgRePatternList = None								# 消息过滤正则模板列表
		self.__nameRePatternList = None								# 角色、宠物名称过滤正则模板列表

	@staticmethod
	def instance() :
		if WordsProfanity.__inst is None :
			WordsProfanity.__inst = WordsProfanity()
		return WordsProfanity.__inst


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __buildUKeywordRePattern( path ) :
		"""
		根据指定的 unicode 关键字配置路径创建正则表达式模板
		"""
		reList = []
		sect = Language.openConfigSection( path )
		if sect is None :
			ERROR_MSG( "path '%s' is not exist!" % path )
			return None

		Language.purgeConfig( path )
		strWords = re.sub( "(\r\n|\n)+", "\n", sect.asBinary )		# 去掉多余的换行
		keywords = []
		amount = 0
		for keyword in strWords.splitlines() :
			ukeyword = keyword.decode( DECODE_NAME )
			keywords.append( re.escape( ukeyword ) )				# 将关键字转换为相应的编码
			amount += 1
			if ( amount % MAX_ROW_LENGTH == 0 ):
				ptn = "|".join( keywords )
				reList.append( re.compile( ptn, re.I ) )
				keywords = []
		if ( amount % MAX_ROW_LENGTH != 0 ):
			ptn = "|".join( keywords )
			reList.append( re.compile( ptn, re.I ) )
		#ptn = "|".join( keywords )
		#print "type is",type(re.compile( ptn, re.I ))
		return reList
		#return re.compile( ptn, re.I )

	# --------------------------------------------
	@staticmethod
	def __dashKeyword( matchobj ) :
		"""
		关键字替换器
		"""
		return "*" * len( matchobj.group( 0 ) )

	@staticmethod
	#def __searchKeyword( rePattern, text ) :
	def __searchKeyword( rePatternList, text ) :
		"""
		根据指定匹配器检索文本的关键字
		"""
		for rePattern in rePatternList:
			txType = type( text )
			if txType is unicode :
				newText = text.encode( DECODE_NAME )
				length = len(newText)
				newText = csol.asSimplifiedString( newText )[0:length]				#底层的繁体转简体
				newText = newText.decode( DECODE_NAME )
				match = rePattern.search( newText )
				if match : return match.group()
			elif txType is str :
				length = len(text)
				newText = csol.asSimplifiedString( text )[0:length]				#底层的繁体转简体
				match = rePattern.search( newText.decode( DECODE_NAME ) )
				if match : return match.group().encode( DECODE_NAME )
		return None

#		txType = type( text )
#		if txType is unicode :
#			match = rePattern.search( text )
#			if match : return match.group()
#		elif txType is str :
#			match = rePattern.search( text.decode( DECODE_NAME ) )
#			if match : return match.group().encode( DECODE_NAME )
#		return None


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def initialize( self ) :
		"""
		初始化（独立出初始化函数的目的是，可以选择初始化时间，而不需要在 import 的时候就必需进行初始化）
		"""
		#self.__msgRePattern = self.__buildUKeywordRePattern( "config/profanitytables/ChatProfanity.txt" )
		#self.__nameRePattern = self.__buildUKeywordRePattern( "config/profanitytables/NameProfanity.txt" )
		self.__msgRePatternList = self.__buildUKeywordRePattern( "config/profanitytables/ChatProfanity.txt" )
		self.__nameRePatternList = self.__buildUKeywordRePattern( "config/profanitytables/NameProfanity.txt" )

	# -------------------------------------------------
	def isPureString( self, string ) :
		"""
		是否是一个纯字符串 (只有英文字符，数字，中文字 不包含任何符号的字符串)
		/[\x00-\uFF]/   	符号
	    /[\u4E00-\u9FA5]/   汉字
	    /[\u0000-\u00FF]/   半角符号
	    /[\uFF00-\uFFFF]/   全角符号
		@type			string : str/unicode
		@param			string : 要判别的字符串
		@rtype				   : bool
		@return				   : 如果是纯字符串数字和英文字母，中文字的字符串，则返回 True
		"""
		if type( string ) is str :
			ustring = unicode( string, DECODE_NAME )
		elif type( string ) is unicode :
			ustring = string
		else :
			TypeError( "argument 'string' must be a string or unicode string!" )
		enstrs = self.__enRePattern.findall( ustring )		# 查询英文字母和数字
		chstrs = self.__chRePattern.findall( ustring )		# 查询中文
		count = 0
		for s in enstrs : count += len( s )
		for s in chstrs : count += len( s ) << 1
		return len( string ) == count

	# ---------------------------------------
	def filterMsg( self, msg ) :
		"""
		过滤消息
		@type			msg : str/unicode
		@param			msg : 要过滤的消息串
		@rtype				: str/unicode
		@return				: 返回替换后的字符串( 如果传入的是 unicode，则返回的也是 unicode )
		"""
		#if not self.__msgRePattern : return msg							# 没有过滤词汇
		if not self.__msgRePatternList : return msg							# 没有过滤词汇
		if type( msg ) is str :
			length = len( msg )
			copyMsg = csol.asSimplifiedString( msg )[0:length]
			copyMsg = copyMsg.decode( DECODE_NAME )
			msg = msg.decode( DECODE_NAME )								# 解码宽字符
			positionList = self.findAllProfanityPositions( copyMsg )
			positionList = sorted( positionList, compareList )
			msg = self.replaceMsg( msg, positionList )
			return msg.encode( DECODE_NAME )
		elif type( msg ) is unicode :
			length = len( msg.encode( DECODE_NAME ) )
			copyMsg = csol.asSimplifiedString( msg.encode( DECODE_NAME ) )[0:length]
			copyMsg = copyMsg.decode( DECODE_NAME )
			positionList = self.findAllProfanityPositions( copyMsg )
			positionList = sorted( positionList, compareList )
			msg = self.replaceMsg( msg, positionList )
			return msg
		raise TypeError( "argument 'msg' must be a string or unicode string!" )

	def findAllProfanityPositions( self, msg ):
		"""
		查找消息中包含的所有的屏蔽字段，返回这些屏蔽字段在消息中的起始位置和终点位置的列表
		@type				name : str/unicode
		@param				name : 要检测的名字
		@rtype					 : [iterator1,iterator2,...]
		@return					 : 如果存在亵渎词汇，则返回所有匹配到的消息中的起始位置和终点位置的列表，否则返回 None
		"""
		positionList = []
		for msgRePattern in self.__msgRePatternList:
			msgIterator = msgRePattern.finditer( msg )
			for match in msgIterator:
				positionList.append( match.span() )
		return positionList

	def replaceMsg( self, msg, positionList ):
		length = len(msg)
		newMsg = []
		j = 0
		if not positionList:
			return msg
		for i in xrange(length):
			if i >= positionList[j][0] and i < positionList[j][1]:
					newMsg.append("*")
			else:
				flag = True
				while( j < len(positionList) ):
					if i >= positionList[j][1]:
						j = j + 1
					else:
						if i >= positionList[j][0]:
							newMsg.append("*")
							flag = False
						break
				if j >= len(positionList):
					newMsg.append(msg[i:])
					break
				if flag:
					newMsg.append(msg[i])
		return "".join(newMsg)

	def searchNameProfanity( self, name ) :
		"""
		检测名字是否包含过滤表中的词汇，如果有，则返回第一个亵渎词汇
		@type				name : str/unicode
		@param				name : 要检测的名字
		@rtype					 : str/None
		@return					 : 如果存在亵渎词汇，则返回第一个亵渎词汇，否则返回 None
		"""
		if not self.__nameRePatternList : return None
		#return self.__searchKeyword( self.__nameRePattern, name )
		return self.__searchKeyword( self.__nameRePatternList, name )

	def searchMsgProfanity( self, msg ) :
		"""
		检测消息文本是否包含过滤表中的词汇，如果有，则返回第一个亵渎词汇
		@type				msg : str/unicode
		@param				msg : 要检测的消息文本
		@rtype					: str/None
		@return					: 如果存在亵渎词汇，则返回第一个亵渎词汇，否则返回 None
		"""
		if not self.__msgRePatternList : return None
		#return self.__searchKeyword( self.__msgRePattern, msg )
		return self.__searchKeyword( self.__msgRePatternList, msg )

def compareList( tuple1, tuple2 ):
	if tuple1[ 0 ] > tuple2[ 0 ]:
		return 1
	elif tuple1[ 0 ] == tuple2[ 0 ]:
		return 0
	elif tuple1[ 0 ] < tuple2[ 0 ]:
		return -1

# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
wordsProfanity = WordsProfanity.instance()

# -*- coding: gb18030 -*-
#
# $Id: ChatProfanity.py,v 1.7 2008-06-20 06:15:57 wangshufeng Exp $

"""
���´ʻ㴦��ģ��
2010.04.30: tidy up by huangyongwei
"""

import re
import time
import Language
from bwdebug import *
from Language import DECODE_NAME

MAX_ROW_LENGTH		= 2000

class ChatProfanity:
	__inst = None

	def __init__( self ):
		assert ChatProfanity.__inst is None, "instance already exist in"
		ChatProfanity.__inst = self
		self.__enRePattern = re.compile( "[a-zA-Z0-9]+" ) 		# Ӣ������ģ��
		self.__chRePattern = re.compile( u"[\u4e00-\u9FA5]+" )	# ��������ģ��
		#self.__msgRePattern = None								# ��Ϣ��������ģ��
		#self.__nameRePattern = None								# ��ɫ���������ƹ�������ģ��
		self.__msgRePatternList = None								# ��Ϣ��������ģ���б�
		self.__nameRePatternList = None								# ��ɫ���������ƹ�������ģ���б�

	@staticmethod
	def instance() :
		if ChatProfanity.__inst is None :
			ChatProfanity.__inst = ChatProfanity()
		return ChatProfanity.__inst


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __buildUKeywordRePattern( path ) :
		"""
		����ָ���� unicode �ؼ�������·������������ʽģ��
		"""
		reList = []
		sect = Language.openConfigSection( path )
		if sect is None :
			ERROR_MSG( "path '%s' is not exist!" % path )
			return None

		Language.purgeConfig( path )
		strWords = re.sub( "(\r\n|\n)+", "\n", sect.asBinary )		# ȥ������Ļ���
		keywords = []
		amount = 0
		for keyword in strWords.splitlines() :
			ukeyword = keyword.decode( DECODE_NAME )
			keywords.append( re.escape( ukeyword ) )				# ���ؼ���ת��Ϊ��Ӧ�ı���
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
		�ؼ����滻��
		"""
		return "*" * len( matchobj.group( 0 ) )

	@staticmethod
	#def __searchKeyword( rePattern, text ) :
	def __searchKeyword( rePatternList, text ) :
		"""
		����ָ��ƥ���������ı��Ĺؼ���
		"""
		for rePattern in rePatternList:
			txType = type( text )
			if txType is unicode :
				match = rePattern.search( text )
				if match : return match.group()
			elif txType is str :
				match = rePattern.search( text.decode( DECODE_NAME ) )
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
		��ʼ������������ʼ��������Ŀ���ǣ�����ѡ���ʼ��ʱ�䣬������Ҫ�� import ��ʱ��ͱ�����г�ʼ����
		"""
		#self.__msgRePattern = self.__buildUKeywordRePattern( "config/profanitytables/ChatProfanity.txt" )
		#self.__nameRePattern = self.__buildUKeywordRePattern( "config/profanitytables/NameProfanity.txt" )
		self.__msgRePatternList = self.__buildUKeywordRePattern( "config/profanitytables/ChatProfanity.txt" )
		self.__nameRePatternList = self.__buildUKeywordRePattern( "config/profanitytables/NameProfanity.txt" )

	# -------------------------------------------------
	def isPureString( self, string ) :
		"""
		�Ƿ���һ�����ַ��� (ֻ��Ӣ���ַ������֣������� �������κη��ŵ��ַ���)
		/[\x00-\uFF]/   	����
	    /[\u4E00-\u9FA5]/   ����
	    /[\u0000-\u00FF]/   ��Ƿ���
	    /[\uFF00-\uFFFF]/   ȫ�Ƿ���
		@type			string : str/unicode
		@param			string : Ҫ�б���ַ���
		@rtype				   : bool
		@return				   : ����Ǵ��ַ������ֺ�Ӣ����ĸ�������ֵ��ַ������򷵻� True
		"""
		if type( string ) is str :
			ustring = unicode( string, DECODE_NAME )
		elif type( string ) is unicode :
			ustring = string
		else :
			TypeError( "argument 'string' must be a string or unicode string!" )
		enstrs = self.__enRePattern.findall( ustring )		# ��ѯӢ����ĸ������
		chstrs = self.__chRePattern.findall( ustring )		# ��ѯ����
		count = 0
		for s in enstrs : count += len( s )
		for s in chstrs : count += len( s ) << 1
		return len( string ) == count

	# ---------------------------------------
	def filterMsg( self, msg ) :
		"""
		������Ϣ
		@type			msg : str/unicode
		@param			msg : Ҫ���˵���Ϣ��
		@rtype				: str/unicode
		@return				: �����滻����ַ���( ���������� unicode���򷵻ص�Ҳ�� unicode )
		"""
		#if not self.__msgRePattern : return msg							# û�й��˴ʻ�
		if not self.__msgRePatternList : return msg							# û�й��˴ʻ�
		if type( msg ) is str :
			msg = msg.decode( DECODE_NAME )								# ������ַ�
			newMsg = msg
			for msgRePattern in self.__msgRePatternList:
				#if msgRePattern.search( msg ):
				newMsg = msgRePattern.sub( self.__dashKeyword, msg )
				msg = newMsg
				if newMsg == "*"*len(newMsg):
					break
			return newMsg.encode( DECODE_NAME )
			#return msg.encode( DECODE_NAME )
			#newMsg = self.__msgRePattern.sub( self.__dashKeyword, msg )
			#return newMsg.encode( DECODE_NAME )							# �������
		elif type( msg ) is unicode :
			newMsg = msg
			for msgRePattern in self.__msgRePatternList:
				#if msgRePattern.search( msg ):
				newMsg = msgRePattern.sub( self.__dashKeyword, msg )
				msg = newMsg
				if newMsg == "*"*len(newMsg):
					break
			return newMsg
			#return msg
			#return self.__msgRePattern.sub( self.__dashKeyword, msg )
		raise TypeError( "argument 'msg' must be a string or unicode string!" )

	def searchNameProfanity( self, name ) :
		"""
		��������Ƿ�������˱��еĴʻ㣬����У��򷵻ص�һ�����´ʻ�
		@type				name : str/unicode
		@param				name : Ҫ��������
		@rtype					 : str/None
		@return					 : ����������´ʻ㣬�򷵻ص�һ�����´ʻ㣬���򷵻� None
		"""
		if not self.__nameRePatternList : return None
		#return self.__searchKeyword( self.__nameRePattern, name )
		return self.__searchKeyword( self.__nameRePatternList, name )

	def searchMsgProfanity( self, msg ) :
		"""
		�����Ϣ�ı��Ƿ�������˱��еĴʻ㣬����У��򷵻ص�һ�����´ʻ�
		@type				msg : str/unicode
		@param				msg : Ҫ������Ϣ�ı�
		@rtype					: str/None
		@return					: ����������´ʻ㣬�򷵻ص�һ�����´ʻ㣬���򷵻� None
		"""
		if not self.__msgRePatternList : return None
		#return self.__searchKeyword( self.__msgRePattern, msg )
		return self.__searchKeyword( self.__msgRePatternList, msg )


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
chatProfanity = ChatProfanity.instance()

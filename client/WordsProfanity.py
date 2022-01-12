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
import csol

MAX_ROW_LENGTH		= 2000

class WordsProfanity:
	__inst = None

	def __init__( self ):
		assert WordsProfanity.__inst is None, "instance already exist in"
		WordsProfanity.__inst = self
		self.__enRePattern = re.compile( "[a-zA-Z0-9]+" ) 		# Ӣ������ģ��
		self.__chRePattern = re.compile( u"[\u4e00-\u9FA5]+" )	# ��������ģ��
		#self.__msgRePattern = None								# ��Ϣ��������ģ��
		#self.__nameRePattern = None								# ��ɫ���������ƹ�������ģ��
		self.__msgRePatternList = None								# ��Ϣ��������ģ���б�
		self.__nameRePatternList = None								# ��ɫ���������ƹ�������ģ���б�

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
				newText = text.encode( DECODE_NAME )
				length = len(newText)
				newText = csol.asSimplifiedString( newText )[0:length]				#�ײ�ķ���ת����
				newText = newText.decode( DECODE_NAME )
				match = rePattern.search( newText )
				if match : return match.group()
			elif txType is str :
				length = len(text)
				newText = csol.asSimplifiedString( text )[0:length]				#�ײ�ķ���ת����
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
			length = len( msg )
			copyMsg = csol.asSimplifiedString( msg )[0:length]
			copyMsg = copyMsg.decode( DECODE_NAME )
			msg = msg.decode( DECODE_NAME )								# ������ַ�
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
		������Ϣ�а��������е������ֶΣ�������Щ�����ֶ�����Ϣ�е���ʼλ�ú��յ�λ�õ��б�
		@type				name : str/unicode
		@param				name : Ҫ��������
		@rtype					 : [iterator1,iterator2,...]
		@return					 : ����������´ʻ㣬�򷵻�����ƥ�䵽����Ϣ�е���ʼλ�ú��յ�λ�õ��б����򷵻� None
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

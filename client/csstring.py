# -*- coding: gb18030 -*-
#
# $Id: Font.py,v 1.4 2008-03-19 10:31:21 huangyongwei Exp $

"""
ʵ���ַ������ӹ��ܵķ�װ
2010.01.22: writen by huangyongwei
2010.02.02: add KeyCharParser
"""

import re
import csol
from keys import *

# --------------------------------------------------------------------
# �ַ��밴��ת������
# --------------------------------------------------------------------
# Ӣ�ı�����
g_en_interpunctions = set( [",", ".", "!", ";", "?", "'", "\"", ":", \
							"(", ")", "[", "]", "{", "}", "<", ">", ] )

# ���ı����ţ����������ۺźͼ����ţ�
g_ch_interpunctions = set( ["��", "��", "��", "��", "��", "��", "��", \
							"��", "��", "��" "��", "��", "��", "��", \
							"��", "��", "��", "��", "��", ] )

# ������
g_interpunctions = set()
g_interpunctions.update( g_en_interpunctions )
g_interpunctions.update( g_ch_interpunctions )

# �������
g_special_emblems = set( [ "~", "`", "@", "#", "$", "%", "^", "&", \
							"+", "-", "*", "/", "\\", "=", \
							"��", "��", "��", "��", \
							"��", "��", "��", "��", "����", \
							] )

# ���з���
g_emblems = set()
g_emblems.update( g_interpunctions )
g_emblems.update( g_special_emblems )

class KeyCharParser( object ) :
	"""
	�ַ�������
	"""
	__cc_keychar_map = {}													# ��ֵ���ַ���ӳ�䣬False ��ʾû�а��� shift ����True ��ʾ���� shift ��
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
		����ֵת��Ϊ�ַ�
		@type			key	  : MACRO DEFINATION
		@param			key	  : �� keys.py �ж���ļ�ֵ
		@type			shift : bool
		@param			shift : �Ƿ��� shift ��
		"""
		ch = ''
		chs = keyToString( key )
		#chs = BigWorld.keyToString( key )
		if len( chs ) == 1 :
			ch = chs
			if not ch.isdigit() :						# ������ַ���
				upper = csol.getKeyState( "CAPSLOCK" )	# �Ƿ��� capslock ��
				if not( upper ^ shift ) :				# �Ƿ���Сдģʽ
					ch = ch.lower()
				return ch
		if SELF.__cc_keychar_map.has_key( key ) :		# ������
			ch = SELF.__cc_keychar_map[key][shift]
		return ch


# --------------------------------------------------------------------
# �ַ�����������
# --------------------------------------------------------------------
def toWideString( s ) :
	"""
	�� ascii ת��Ϊ unicude �ַ���
	@type				s : str
	@param				s : ascii �ַ���
	@rtype				  : unicode
	@return				  : ���ַ���
	"""
	if type( s ) is str :
		return csol.asWideString( s )
	return s

def toString( us ) :
	"""
	�� unicode �ַ���ת��Ϊ ascii �ַ���
	@type				s : unicode
	@param				s : ���ַ���
	@rtype				  : str
	@return				  : ascii �ַ���
	"""
	if type( us ) is unicode :
		return csol.asString( us )
	return us


# --------------------------------------------------------------------
# �ַ�ƥ������
# --------------------------------------------------------------------
__spacePatten = re.compile( toWideString( "[\s��]+" ) )						# ƥ��ո��ģʽ
__escEmbs = "".join( [re.escape( toWideString( i ) ) for i in g_emblems] )
__backwardEmbPatten = re.compile( "[%s]+" % __escEmbs )						# ���ز���ʱƥ�����ģʽ
__forwardEmbPatten = re.compile( "[%s]+" % __escEmbs )						# ��ǰ����ʱƥ�����ģʽ
__escStartPattern = re.compile( "[%s\s]+" % __escEmbs )						# ƥ�����ַ��Ǳ���ģʽ
del __escEmbs

def getFirstWordEnd( text ) :
	"""
	��ȡ�ַ����е�һ�����ʵĽ���λ��
	�����Կո��β���Ϊ���ʣ��õ����������������пո񣨴��ո�Ҳ��һ�����ʣ�
	@type			text : basestring( str/unicode )
	@param			text : �����ַ���
	@rtype				 : int
	@return				 : ���ص�һ�����ʵĽ�������
	"""
	index = len( text )
	m = __spacePatten.search( text )
	if m : index = m.end()
	m = __forwardEmbPatten.search( text[:index] )
	if m :
		start = m.start()
		index = start
		if start == 0 :								# ���ַ��Ǳ��
			m = __escStartPattern.search( text )
			if m : index = m.end()
	return index

def getLastWordStart( text ) :
	"""
	��ȡ�ַ��������һ�����ʵ���ʼλ�ã�������ʺ����пո���õ�����������Ŀո�
	@type			text : basestring( str/unicode )
	@param			text : �����ַ���
	@rtype				 : int
	@return				 : �������һ�����ʵ���ʼ����
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

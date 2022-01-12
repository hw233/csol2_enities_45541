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
	Ĭ�ϵ����Խ����������ܽ��͵Ĺ淶���£�
	�� �ý����������Դ����������������Դ�
	�� ���Լ���ֵ�Ĺ�ϵͨ���Ⱥ������
	�� �������֮����Ӣ�ķֺŷָ�
	�� ��������ֵ���зֺţ�����Ҫ�Ե����Ž���������
	�磺"{ aa = 1222; bb = AADFASDF; cc = 'aasdfasdf'; dd = 23,23,5; ee = ( 3, 4, 5 ) }"
	"""

	def __init__( self ) :
		# ��������ƥ��ģʽ
		self.__scopePattern = re.compile( r"\{.*(?<!\\)\}" )
		# �ֺŷָ�ƥ��ģʽ
		self.__splitPattern = re.compile( r"\w+\s*=\s*[^'].*?(?=;)|\w+\s*=\s*'.*?'|\w+\s*=\s*[^'].*|\w+\s*=\s*'.*" )

		# ����ƥ��ģʽ��������������
		self.__intPattern = re.compile( r"^\d+$|^[\+\-]\d+$" )
		# ������ƥ��ģʽ����������
		self.__floatPattern = re.compile( r"^\d+$|^[\+\-]\d+$|^[\+\-]{0,1}\d*\.\d+$|^[\+\-]{0,1}\d+\.$" )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getFormatScope( self, text ) :
		"""
		��ȡ��ʽ���ı�
		@type				text : str
		@param				text : ��ʽ����������ȫ���ı�
		@rtype					 : tuple
		@return					 : ( ��ʽ���ı�, ��ȥ��ʽ���ı����ʣ���ı� )
		"""
		wtext = csstring.toWideString( text )					# ����ʹ�ÿ��ַ���Ŀ���Ƿ�ֹ���ı��ض�
		match = self.__scopePattern.search( wtext )
		if match is None : return "", text						# û�д��������򷵻�ȫ���ı�
		start, end = match.start(), match.end()
		if start != 0 : return "", text							# ���ǽ����Ŵ��������򷵻�ȫ���ı�
		scopeText = wtext[1 : end - 1].strip()					# ��ʽ���ı�( ȥ�����ߵ����� )
		scopeText = scopeText.replace( "\\}", "}" )
		scopeText = csstring.toString( scopeText )
		leaveText = csstring.toString( wtext[end:] )			# ʣ���ı�
		return scopeText, leaveText

	def getAttrInfos( self, attrsText ) :
		"""
		ͨ����ʽ���ı���ȡ����ֵ
		@type				attrsText : str
		@param				attrsText : ��ʽ���ı�
		@rtype						  : dict
		@return						  : ��ʽ�������ֵ�
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
		�� int ���ַ���ת��Ϊ int ����ֵ
		@type			strInt	: str
		@param			strInt	: �ַ�����ʽ�� int
		@type			default : int
		@param			default : ���ת��ʧ�ܣ����ص�ֵ
		@rtype					: int
		@return					: int ����ֵ
		"""
		strInt = strInt.strip()
		eles = self.__intPattern.findall( strInt )
		if len( eles ) == 1 :								# ����������ַ���
			return int( strInt )							# ǿ������ת���󷵻�
		else :												# ����
			f = self.tranFloat( strInt )		 			# ��ͼ����ת��Ϊ������ʽ
			if f is not None : return int( f )				# ����Ǹ���������ǿ��ת��Ϊ��������
		return default

	def tranFloat( self, strFloat, default = None ) :
		"""
		�� int ���ַ���ת��Ϊ int ����ֵ
		@type			strInt	: str
		@param			strInt	: �ַ�����ʽ�� int
		@type			default : int
		@param			default : ת��ʧ��ʱ���ص�ֵ
		@rtype					: int
		@return					: int ����ֵ
		"""
		strFloat = strFloat.strip()
		eles = self.__floatPattern.findall( strFloat )
		if len( eles ) == 1 :
			return float( strFloat )
		return default

	def tranCustom( self, s, Type, default = None ) :
		"""
		��һ���ַ���ת��Ϊ�û��Զ�������
		@type				s		: str
		@param				s		: Ҫת����ֵ���ַ�����ʽ
		@type				Type	: types.Type
		@param				Type	: ָ��������
		@type				default	: all types
		@param				default	: ת��ʧ��ʱ���ص�ֵ
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
		�����ַ�����ʽ�� tuple ��ȡ tuple
		@type				strTuple : str
		@param				strTuple : �ַ�����ʽ�� tuple
		@type				types	 : list
		@param				types	 : ����Ԫ�ص�����
		@type				default	 : tuple
		@param				default	 : ����ʧ��ʱ���ص�Ĭ��ֵ
		@rtype						 : None / tuple
		@return						 : ���������ȷ tuple���򷵻� None�����򷵻�ת���� tuple
		"""
		strTuple = strTuple.strip()
		if strTuple.startswith( '(' ) :								# ����������ŵ� tuple
			strTuple = strTuple[1:-1]								# ��ȥ�����ߵ�����
		strEles = strTuple.split( ',' )								# ��ָ�Ԫ��
		if len( strEles ) < len( types ) :
			return default

		eles = ()
		for idx, Type in enumerate( types ) :						# ���ǿ������ת��
			strEle = strEles[idx].strip()							# Ԫ���ڵ��ַ�����ʽ
			value = self.tranCustom( strEle, Type )					# ����ת������
			if value is None : return default						# ת��ʧ��
			eles += ( value, )
		return eles

	def tranColor( self, strColor, defColor = None ) :
		"""
		��ȡ��ɫ����ȡʧ���򷵻� defColor
		@type				strColor : str
		@param				strColor : ��ɫ������ϵͳ��ɫ����
		@type				defColor : tuple
		@param				defColor : �������ʧ�ܷ��ص�Ĭ����ɫ
		@rtype						 : None / tuple
		@return						 : ���������ȷ����ɫ�����򷵻� None�����򷵻���ɫֵ
		"""
		strColor = strColor.lower()
		if strColor in cscolors :
			return cscolors[strColor]

		rgba = self.tranTuple( strColor, 4 * [int] )		# ����Ϊ��ά��ɫ
		if rgba is not None : return rgba
		rgb = self.tranTuple( strColor, 3 * [int] )			# ����Ϊ��ά��ɫ
		if rgb is not None : return rgb

		try :
			return intColor2RGBColor( int( strColor, 16 ) )	# ʮ��������ɫ
		except :
			pass
		return defColor


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
defParser = DefaultParser()

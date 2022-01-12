# -*- coding: gb18030 -*-
#
"""
����ϵͳ for Role ����
"""
# $Id: Bitarray.py,v 1.2 2006-01-24 02:29:10 phw Exp $


C_MAX_LEN = 1024
# -3 ����Ϊ�һ�������16���Ƶ�Long���ַ�����Ҫ��ȥ"0x"��"L"�����ַ�, ��4����Ϊ���16��������ÿ���ֽ�(8λ)ֻ�ܱ�ʾһ��4λ��ֵ��
C_MAX_BIT = (C_MAX_LEN - 3) * 4
C_KEY_BITARRAY = "bitarray"

from bwdebug import *

class Bitarray:
	def __init__( self ):
		self.value = 0L
	
	def checkBit( self, index ):
		"""
		���ĳһλ�Ƿ�Ϊ1
		
		@param index: λ����������128��ʾ��128λ
		@type  index: UINT16
		@return: BOOL
		@rtype:  BOOL
		"""
		return (self.value & (1 << index)) != 0L
	
	def setBit( self, index ):
		"""
		����ĳһλΪ1
		
		@param index: λ����������128��ʾ��128λ
		@type  index: UINT16
		@return: ��
		"""
		assert C_MAX_BIT >= index
		self.value |= 1 << index
	
	def unsetBit( self, index ):
		"""
		����ĳһλΪ0
		
		@param index: λ����������128��ʾ��128λ
		@type  index: UINT16
		@return: ��
		"""
		assert C_MAX_BIT >= index
		v = 1 << index
		self.value = (self.value | v) ^ v		# ��ȷ��������ֵ�������ȡ����



	##################################################################
	# BigWorld �Ľӿ�                                                #
	##################################################################
	def addToStream( self, obj ):
		"""
		����ת��Ϊ��(Stream)��
		
		@return: str
		"""
		return hex(obj.value)

	def addToSection( self, obj, section ):
		"""
		����ʵ������ת��ΪXML Data
		
		@param section: See Also L{writeSection<writeSection>}
		@return: ��
		"""
		section.writeString( C_KEY_BITARRAY, hex(obj.value) )

	def createFromStream( self, stream ):
		"""
		����(Stream)��װ������
		
		@param	stream: [in] ���ַ���
		@type	stream: str
		@return: 		self.defaultValue()
		@rtype: 		Bitarray
		@see: 			L{loadFromStream<loadFromStream>}
		"""
		obj = self.defaultValue()
		obj.value = long( stream, 16 )
		return obj

	def createFromSection( self, section ):
		"""
		��XML Data��װ������
		
		@param section: [in] See Also L{loadFromSection<loadFromSection>}
		@return: 		self.defaultValue()
		@rtype: 		Bitarray
		@see: 			L{loadFromSection<loadFromSection>}
		"""
		obj = self.defaultValue()
		try:
			obj.value = long( section[C_KEY_BITARRAY].asString, 16 )
		except AttributeError, errstr:
			WARNING_MSG( errstr )
		return obj

	def fromStreamToSection( self, stream, section ):
		"""
		�����ݴ���(Stream)ת��ΪXML Data
		
		@param stream: [in] ���ַ���
		@type stream: str
		@param section: [out] XML Data���ݶ�
		@type section: Language.PyDataSection
		@return: ��
		"""
		section.writeString( C_KEY_BITARRAY, stream )

	def fromSectionToStream( self, section ):
		"""
		���ݴ�XML Dataת��Ϊ��(Stream)
		
		@param section: [in] XML Data���ݶ�
		@type section: Language.PyDataSection
		@return: ��(Stream)�ַ���
		@rtype: str
		"""
		return section[C_KEY_BITARRAY].asString

	def bindSectionToDB( self, binding ):
		"""
		����Database��ṹ
		
		@param binding: ����C++ʵ�ֵ�PythonObject��������д��ṹ���ο��ĵ�server_scripting_guide 8.3
		@return: ��
		"""
		binding.bind( C_KEY_BITARRAY, "STRING", C_MAX_LEN )
		

	def defaultValue( self ):
		"""
		ȡ��һ����Ĭ��ʵ��
		
		@return: Bitarrayʵ��
		@rtype: Bitarray
		"""
		return Bitarray()

instance = Bitarray()

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2005/08/05 10:28:35  phw
# ����������������־�õ�"λ����"�Զ�������
#
#

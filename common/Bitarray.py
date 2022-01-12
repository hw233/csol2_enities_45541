# -*- coding: gb18030 -*-
#
"""
任务系统 for Role 部份
"""
# $Id: Bitarray.py,v 1.2 2006-01-24 02:29:10 phw Exp $


C_MAX_LEN = 1024
# -3 是因为我会把它变成16进制的Long型字符串，要减去"0x"和"L"三个字符, 乘4是因为变成16进制数后每个字节(8位)只能表示一个4位的值。
C_MAX_BIT = (C_MAX_LEN - 3) * 4
C_KEY_BITARRAY = "bitarray"

from bwdebug import *

class Bitarray:
	def __init__( self ):
		self.value = 0L
	
	def checkBit( self, index ):
		"""
		检查某一位是否为1
		
		@param index: 位的索引，如128表示第128位
		@type  index: UINT16
		@return: BOOL
		@rtype:  BOOL
		"""
		return (self.value & (1 << index)) != 0L
	
	def setBit( self, index ):
		"""
		设置某一位为1
		
		@param index: 位的索引，如128表示第128位
		@type  index: UINT16
		@return: 无
		"""
		assert C_MAX_BIT >= index
		self.value |= 1 << index
	
	def unsetBit( self, index ):
		"""
		设置某一位为0
		
		@param index: 位的索引，如128表示第128位
		@type  index: UINT16
		@return: 无
		"""
		assert C_MAX_BIT >= index
		v = 1 << index
		self.value = (self.value | v) ^ v		# 先确保里面有值再做异或取消掉



	##################################################################
	# BigWorld 的接口                                                #
	##################################################################
	def addToStream( self, obj ):
		"""
		数据转换为流(Stream)；
		
		@return: str
		"""
		return hex(obj.value)

	def addToSection( self, obj, section ):
		"""
		把类实例数据转换为XML Data
		
		@param section: See Also L{writeSection<writeSection>}
		@return: 无
		"""
		section.writeString( C_KEY_BITARRAY, hex(obj.value) )

	def createFromStream( self, stream ):
		"""
		从流(Stream)中装载数据
		
		@param	stream: [in] 流字符串
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
		从XML Data中装载数据
		
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
		把数据从流(Stream)转换为XML Data
		
		@param stream: [in] 流字符串
		@type stream: str
		@param section: [out] XML Data数据段
		@type section: Language.PyDataSection
		@return: 无
		"""
		section.writeString( C_KEY_BITARRAY, stream )

	def fromSectionToStream( self, section ):
		"""
		数据从XML Data转换为流(Stream)
		
		@param section: [in] XML Data数据段
		@type section: Language.PyDataSection
		@return: 流(Stream)字符串
		@rtype: str
		"""
		return section[C_KEY_BITARRAY].asString

	def bindSectionToDB( self, binding ):
		"""
		定义Database表结构
		
		@param binding: 引擎C++实现的PythonObject，用来填写表结构；参考文档server_scripting_guide 8.3
		@return: 无
		"""
		binding.bind( C_KEY_BITARRAY, "STRING", C_MAX_LEN )
		

	def defaultValue( self ):
		"""
		取得一个的默认实例
		
		@return: Bitarray实例
		@rtype: Bitarray
		"""
		return Bitarray()

instance = Bitarray()

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2005/08/05 10:28:35  phw
# 给任务的永久任务标志用的"位数组"自定义类型
#
#

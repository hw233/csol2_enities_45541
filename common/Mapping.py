# -*- coding: gb18030 -*-

"""
"""

# $Id: Mapping.py,v 1.4 2006-04-28 13:42:50 phw Exp $

import cPickle
import struct
from bwdebug import *


g_blankDictStream =  struct.pack( "B", len(cPickle.dumps( {}, 2 )) ) + cPickle.dumps( {}, 2 )

class Mapping:
	"""
	使用dict模拟mud里的mapping, 用于保存临时或永久的数据。
	
	注意：由于需要传输，因此这个mapping的key和value只允许接收python里的内置类型：int、long、float、dict、tuple、list、string。
	"""
	def __init__( self ):
		pass

	##################################################################
	# BigWorld User Defined Type 的接口                              #
	##################################################################
	def addToStream( self, obj ):
		"""
		数据转换为流(Stream)；
		
		@return: str
		"""
		if len( obj ) == 0:
			return g_blankDictStream
		
		s = cPickle.dumps( obj, 2 )
		sl = len(s)
		if sl >= 255:
			sh = struct.pack( "<I", (sl << 8) | 0xFF )
		else:
			sh = struct.pack( "B", sl )
		return sh + s

	def addToSection( self, obj, section ):
		"""
		把类实例数据转换为XML Data
		
		@param section: See Also L{writeSection<writeSection>}
		@return: 无
		"""
		section.writeBlob( "mapping", self.addToStream( obj ) )

	def createFromStream( self, stream ):
		"""
		从流(Stream)中装载数据
		
		@param	stream: [in] 流字符串
		@type	stream: str
		@return: 		self.defaultValue()
		@rtype: 		Mapping
		@see: 			L{loadFromStream<loadFromStream>}
		"""
		try:
			# 理论上这里根本不可能出错，但在实际的运行中确实是出现的错误，
			# 其中一种出错的情况初步估计是由于更新了*.py后没有删除*.pyc
			# 就运行服务器，某些.pyc更新失败，在运行期出现了莫其情况而引发。
			# 做此处理的目的在于希望不会因为某些数据有问题而发服务器崩溃的行为。
			(sl,) = struct.unpack( "B", stream[0] )
		except Exception, err:
			sys.excepthook( Exception, err, sys.exc_traceback )
			STREAM_MSG( stream, ";;; len( stream ) == %i" % len( stream ) )
			return self.defaultValue()
		
		if sl == 255:
			s = stream[4:]
		else:
			s = stream[1:]
		
		try:
			obj = cPickle.loads( s )
		except Exception, err:
			sys.excepthook( Exception, err, sys.exc_traceback )
			STREAM_MSG( stream, ";;; len( stream ) == %i" % len( stream ) )
			return self.defaultValue()
		return obj

	def createFromSection( self, section ):
		"""
		从XML Data中装载数据
		
		@param section: [in] See Also L{loadFromSection<loadFromSection>}
		@return: 		self.defaultValue()
		@rtype: 		Mapping
		@see: 			L{loadFromSection<loadFromSection>}
		"""
		try:
			s = section.readBlob( "mapping" )
		except Exception, e:
			ERROR_MSG( e )
		
		return cPickle.loads( s )

	def fromStreamToSection( self, stream, section ):
		"""
		把数据从流(Stream)转换为XML Data
		
		@param stream: [in] 流字符串
		@type stream: str
		@param section: [out] XML Data数据段
		@type section: Language.PyDataSection
		@return: 无
		"""
		#obj = self.createFromStream( stream )
		#self.addToSection( obj, section )
		section.writeBlob( "mapping", stream )

	def fromSectionToStream( self, section ):
		"""
		数据从XML Data转换为流(Stream)
		
		@param section: [in] XML Data数据段
		@type section: Language.PyDataSection
		@return: 流(Stream)字符串
		@rtype: str
		"""
		#obj = self.createFromSection( section )
		#return self.addToStream( obj )
		return section.readBlob( "mapping" )

	def bindSectionToDB( self, binding ):
		"""
		定义Database表结构
		
		@param binding: 引擎C++实现的PythonObject，用来填写表结构；参考文档server_scripting_guide 8.3
		@return: 无
		"""
		binding.bind( "mapping", "BLOB", 4096 )

	def defaultValue( self ):
		"""
		取得一个的默认实例
		
		@return: Mapping实例
		@rtype: Mapping
		"""
		return {}

instance = Mapping()


#
# $Log: not supported by cvs2svn $
# Revision 1.3  2006/03/27 07:40:09  phw
# 修正了addToStream()和createFromStream()
#
# Revision 1.2  2006/03/20 03:18:54  wanhaipeng
# Mark stream.将来要改对！！！
#
# Revision 1.1  2006/01/24 02:31:33  phw
# no message
#
#

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
	ʹ��dictģ��mud���mapping, ���ڱ�����ʱ�����õ����ݡ�
	
	ע�⣺������Ҫ���䣬������mapping��key��valueֻ�������python����������ͣ�int��long��float��dict��tuple��list��string��
	"""
	def __init__( self ):
		pass

	##################################################################
	# BigWorld User Defined Type �Ľӿ�                              #
	##################################################################
	def addToStream( self, obj ):
		"""
		����ת��Ϊ��(Stream)��
		
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
		����ʵ������ת��ΪXML Data
		
		@param section: See Also L{writeSection<writeSection>}
		@return: ��
		"""
		section.writeBlob( "mapping", self.addToStream( obj ) )

	def createFromStream( self, stream ):
		"""
		����(Stream)��װ������
		
		@param	stream: [in] ���ַ���
		@type	stream: str
		@return: 		self.defaultValue()
		@rtype: 		Mapping
		@see: 			L{loadFromStream<loadFromStream>}
		"""
		try:
			# ������������������ܳ�������ʵ�ʵ�������ȷʵ�ǳ��ֵĴ���
			# ����һ�ֳ��������������������ڸ�����*.py��û��ɾ��*.pyc
			# �����з�������ĳЩ.pyc����ʧ�ܣ��������ڳ�����Ī�������������
			# ���˴����Ŀ������ϣ��������ΪĳЩ���������������������������Ϊ��
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
		��XML Data��װ������
		
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
		�����ݴ���(Stream)ת��ΪXML Data
		
		@param stream: [in] ���ַ���
		@type stream: str
		@param section: [out] XML Data���ݶ�
		@type section: Language.PyDataSection
		@return: ��
		"""
		#obj = self.createFromStream( stream )
		#self.addToSection( obj, section )
		section.writeBlob( "mapping", stream )

	def fromSectionToStream( self, section ):
		"""
		���ݴ�XML Dataת��Ϊ��(Stream)
		
		@param section: [in] XML Data���ݶ�
		@type section: Language.PyDataSection
		@return: ��(Stream)�ַ���
		@rtype: str
		"""
		#obj = self.createFromSection( section )
		#return self.addToStream( obj )
		return section.readBlob( "mapping" )

	def bindSectionToDB( self, binding ):
		"""
		����Database��ṹ
		
		@param binding: ����C++ʵ�ֵ�PythonObject��������д��ṹ���ο��ĵ�server_scripting_guide 8.3
		@return: ��
		"""
		binding.bind( "mapping", "BLOB", 4096 )

	def defaultValue( self ):
		"""
		ȡ��һ����Ĭ��ʵ��
		
		@return: Mappingʵ��
		@rtype: Mapping
		"""
		return {}

instance = Mapping()


#
# $Log: not supported by cvs2svn $
# Revision 1.3  2006/03/27 07:40:09  phw
# ������addToStream()��createFromStream()
#
# Revision 1.2  2006/03/20 03:18:54  wanhaipeng
# Mark stream.����Ҫ�Ķԣ�����
#
# Revision 1.1  2006/01/24 02:31:33  phw
# no message
#
#

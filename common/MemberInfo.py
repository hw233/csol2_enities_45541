# -*- coding: gb18030 -*-
#
# $Id: MemberInfo.py,v 1.1 2005-12-19 08:47:00 xuning Exp $


"""
�����Ա��Ϣ�Զ�������
"""

C_MEMBERINFO	= "minf"
C_MID			= "mid"
C_MNAME			= "name"
C_MRACECLASS	= "race"
C_MRANK			= "rank"
C_MPOINT		= "point"
C_MTITLE		= "title"
C_MLEVEL		= "level"
C_MSPACE		= "space"


import cPickle as cp
from bwdebug import *

class MemberInfo:
	def __init__( self ):
		"""
		"""
		pass
	
	##################################################################
	# BigWorld �Ľӿ�                                                #
	##################################################################
	def addToStream( self, obj ):
		"""
		����ת��Ϊ��(Stream)
		"""
		return cp.dumps( obj, 1 )

	def addToSection( self, obj, section ):
		"""
		����ʵ������ת��ΪXML Data
		"""
		for k, v in obj.items():
			sect = section.createSection( C_MEMBERINFO )
			sect.writeInt( C_MID, k )
			sect.writeString( C_MNAME, v["name"] )
			sect.writeInt( C_MRACECLASS, v["raceclass"] )
			sect.writeInt( C_MRANK, v["rank"] )
			sect.writeInt( C_MPOINT, v["point"] )
			sect.writeString( C_MTITLE, v["title"] )
			sect.writeInt( C_MLEVEL, v["level"] )
			sect.writeString( C_MSPACE, v["space"] )

	def createFromStream( self, stream ):
		"""
		����(Stream)��װ������
		"""
		return cp.loads( stream )

	def createFromSection( self, section ):
		"""
		��XML Data��װ������
		"""
		obj = dict()
		for v in section.values():
			sub = dict()
			sub["name"] = v.readString( C_MNAME )
			sub["reaceclass"] = v.readInt( C_MRACECLASS )
			sub["rank"] = v.readInt( C_MRANK )
			sub["point"] = v.readInt( C_MPOINT )
			sub["title"] = v.readString( C_MTITLE )
			sub["level"] = v.readInt( C_MLEVEL )
			sub["space"] = v.readString( C_MSPACE )
			obj[v.readInt( C_MID )] = sub

		return obj

	def fromStreamToSection( self, stream, section ):
		"""
		�����ݴ���(Stream)ת��ΪXML Data
		"""
		obj = self.createFromStream( stream )
		self.addToSection( obj, section )

	def fromSectionToStream( self, section ):
		"""
		���ݴ�XML Dataת��Ϊ��(Stream)
		"""
		obj = self.createFromSection( section )
		return self.addToStream( obj )

	def bindSectionToDB( self, binding ):
		"""
		����Database��ṹ
		
		@param binding: ����C++ʵ�ֵ�PythonObject��������д��ṹ���ο��ĵ�server_scripting_guide 8.3
		@return: ��
		"""
		binding.beginTable( C_MEMBERINFO )
		binding.bind( C_MID, "INT32", 4 )
		binding.bind( C_MNAME, "STRING", 64 )
		binding.bind( C_MRACECLASS, "UINT32", 4 )
		binding.bind( C_MRANK, "UINT8", 1 )
		binding.bind( C_MPOINT, "UINT32", 4 )
		binding.bind( C_MTITLE, "STRING", 64 )
		binding.bind( C_MLEVEL, "UINT8", 1 )
		binding.bind( C_MSPACE, "STRING", 64 )
		binding.endTable()
	
	def defaultValue( self ):
		"""
		"""
		return dict()


instance = MemberInfo()

#
# $Log: not supported by cvs2svn $
#

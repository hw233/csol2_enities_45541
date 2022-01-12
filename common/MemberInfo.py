# -*- coding: gb18030 -*-
#
# $Id: MemberInfo.py,v 1.1 2005-12-19 08:47:00 xuning Exp $


"""
工会会员信息自定义类型
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
	# BigWorld 的接口                                                #
	##################################################################
	def addToStream( self, obj ):
		"""
		数据转换为流(Stream)
		"""
		return cp.dumps( obj, 1 )

	def addToSection( self, obj, section ):
		"""
		把类实例数据转换为XML Data
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
		从流(Stream)中装载数据
		"""
		return cp.loads( stream )

	def createFromSection( self, section ):
		"""
		从XML Data中装载数据
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
		把数据从流(Stream)转换为XML Data
		"""
		obj = self.createFromStream( stream )
		self.addToSection( obj, section )

	def fromSectionToStream( self, section ):
		"""
		数据从XML Data转换为流(Stream)
		"""
		obj = self.createFromSection( section )
		return self.addToStream( obj )

	def bindSectionToDB( self, binding ):
		"""
		定义Database表结构
		
		@param binding: 引擎C++实现的PythonObject，用来填写表结构；参考文档server_scripting_guide 8.3
		@return: 无
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

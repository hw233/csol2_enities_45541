# -*- coding: gb18030 -*-

# $Id: FamilyDatasImpl.py,v 1.1 2008-05-09 03:14:51 kebiao Exp $

from bwdebug import *

class OnlineMemberType( dict ):
	"""
	实现cell部份的数据创建、还原
	"""
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		dat = []
		d = { "values" : dat }
		for dbid, mailbox in obj.iteritems():
			x = {}
			x[ "dbid" ] = dbid
			x[ "mb" ] = mailbox
			dat.append( x )
		return d
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = OnlineMemberType()
		for dct in dict["values"]:
			obj[ dct[ "dbid" ] ] = dct[ "mb" ]
		return obj
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, OnlineMemberType )

	def getStartCooldownTime( self, cd ):
		return self[ cd ][ 0 ]

	def getEndCooldownTime( self, cd ):
		return self[ cd ][ 1 ]
		
instance = OnlineMemberType()


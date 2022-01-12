# -*- coding: gb18030 -*-

from bwdebug import *

class LivingSkillImpl( dict ):
	"""
	实现cell部份的生活技能数据创建、还原
	"""
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		dat = []
		d = { "values" : dat }
		for cd, tdata in obj.iteritems():
			x = {}
			x[ "skillID" ] = cd
			x[ "sleight" ] = tdata[ 0 ]
			x[ "sleightLevel" ] = tdata[ 1 ]
			dat.append( x )
		return d
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = LivingSkillImpl()
		for dct in dict["values"]:
			obj[ dct[ "skillID" ] ] = ( dct[ "sleight" ], dct[ "sleightLevel" ] )
		return obj
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, LivingSkillImpl )

instance = LivingSkillImpl()


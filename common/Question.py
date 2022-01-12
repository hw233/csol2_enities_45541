# -*- coding: gb18030 -*-
#

import BigWorld
import csdefine
import time
import cPickle



class Question:
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.index 			= ""
		self.buffID			= 0
		self.questDes 		= ""
		self.answers		= {}


	##################################################################
	# BigWorld 的接口												#
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		return { "index" 			: obj.index,
		         "buffID" 			: obj.buffID,
		         "questDes" 		: obj.questDes,
		         "answers"			: obj.answers,
			}                         

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = Question()
		obj.index 			= dict["index"]
		obj.buffID 			= dict["buffID"]
		obj.questDes 		= dict["questDes"]
		obj.answers			= dict["answers"]
		return obj

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, Question )

instance = Question()
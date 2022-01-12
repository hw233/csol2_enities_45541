# -*- coding: gb18030 -*-
# $Id: $



class QuestDartRecord:
	"""
	一组循环任务记录
	"""
	def __init__( self ):
		"""
		"""
		self.dartCount		= 0 	#当天第几次运镖
		self.date			= 0		#运镖时间
	

	
	##################################################################
	# BigWorld User Defined Type 的接口                              #
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.
		
		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		if isinstance( obj, dict ):	
			return obj
		return { "dartCount" : obj.dartCount, "date" : obj.date }
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = QuestDartRecord()
		if dict.has_key( 'dartCount' ):	
			obj.dartCount = dict["dartCount"]
		if dict.has_key( 'date' ):
			obj.date = dict["date"]
		return obj
	
	def isSameType( self, obj ):
		"""
		"""
		return isinstance( obj, ( QuestDartRecord, dict ) )
		
instance = QuestDartRecord()
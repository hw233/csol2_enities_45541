# -*- coding: gb18030 -*-
# $Id: $



class QuestDartRecord:
	"""
	һ��ѭ�������¼
	"""
	def __init__( self ):
		"""
		"""
		self.dartCount		= 0 	#����ڼ�������
		self.date			= 0		#����ʱ��
	

	
	##################################################################
	# BigWorld User Defined Type �Ľӿ�                              #
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
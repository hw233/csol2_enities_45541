# -*- coding: gb18030 -*-
# $Id: $



class SunBathRecord:
	"""
	日光浴数据记录
	"""
	def __init__( self ):
		"""
		"""
		self.sunBathCount	= 0 	# 当天日光浴的时间（ 单位是秒 ）
		self.date			= 0		# 进行日光浴的具体日期
		self.prayCount		= 0		# 许愿次数
		self.prayDate		= 0		# 许愿日期
		self.auguryCount	= 0		# 占卜次数
		self.auguryDate		= 0		# 占卜日期
		self.auguryTime		= 0		# 记录最近一次占卜时间
		self.proofFriendCount	= 0	# 龙王见证情缘的次数
		self.proofFriendDate	= 0	# 龙王见证情缘的日期
	
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
		return { "sunBathCount" : obj.sunBathCount, "auguryCount" : obj.auguryCount, "auguryDate" : obj.auguryDate, "auguryTime" : obj.auguryTime, "date" : obj.date, "proofFriendCount":obj.proofFriendCount, "proofFriendDate":obj.proofFriendDate }
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = SunBathRecord()
		if dict.has_key( 'sunBathCount' ):	
			obj.sunBathCount = dict["sunBathCount"]
		if dict.has_key( 'auguryCount' ):	
			obj.auguryCount = dict["auguryCount"]
		if dict.has_key( 'auguryDate' ):	
			obj.auguryDate = dict["auguryDate"]
		if dict.has_key( 'auguryTime' ):	
			obj.auguryTime = dict["auguryTime"]
		if dict.has_key( 'date' ):
			obj.date = dict["date"]
		if dict.has_key( 'proofFriendCount' ):
			obj.date = dict["proofFriendCount"]
		if dict.has_key( 'proofFriendDate' ):
			obj.date = dict["proofFriendDate"]
		return obj
	
	def isSameType( self, obj ):
		"""
		"""
		return isinstance( obj, ( SunBathRecord, dict ) )
		
instance = SunBathRecord()
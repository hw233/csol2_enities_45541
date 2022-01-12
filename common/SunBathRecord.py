# -*- coding: gb18030 -*-
# $Id: $



class SunBathRecord:
	"""
	�չ�ԡ���ݼ�¼
	"""
	def __init__( self ):
		"""
		"""
		self.sunBathCount	= 0 	# �����չ�ԡ��ʱ�䣨 ��λ���� ��
		self.date			= 0		# �����չ�ԡ�ľ�������
		self.prayCount		= 0		# ��Ը����
		self.prayDate		= 0		# ��Ը����
		self.auguryCount	= 0		# ռ������
		self.auguryDate		= 0		# ռ������
		self.auguryTime		= 0		# ��¼���һ��ռ��ʱ��
		self.proofFriendCount	= 0	# ������֤��Ե�Ĵ���
		self.proofFriendDate	= 0	# ������֤��Ե������
	
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
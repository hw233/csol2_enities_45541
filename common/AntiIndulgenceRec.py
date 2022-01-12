# -*- coding: gb18030 -*-
#
# δ�����˷�����ϵͳ��������ʱ���¼ 2009-03-18 SongPeifang
#
"""
@summary	:	������ϵͳ���߼�����ʱ���¼
"""
class AntiIndulgenceRec:
	"""
	������ϵͳ���߼�����ʱ���¼
	"""
	def __init__( self ):
		"""
		"""
		self.total_online	= 0 	# ���������ۼ�ʱ��(��λ�Ƿ���)
		self.total_offline	= 0 	# ���������ۼ�ʱ��(��λ�Ƿ���)
		self.last_offline	= 0		# ������ߵ�ʱ��(��)
	
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
		return { "total_online" : obj.total_online, "total_offline" : obj.total_offline, "last_offline" : obj.last_offline }
		
	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.
		
		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = AntiIndulgenceRec()
		if dict.has_key( 'total_online' ):	
			obj.total_online = dict["total_online"]
		if dict.has_key( 'total_offline' ):	
			obj.total_offline = dict["total_offline"]
		if dict.has_key( 'last_offline' ):	
			obj.last_offline = dict["last_offline"]
		return obj
	
	def isSameType( self, obj ):
		"""
		"""
		return isinstance( obj, ( AntiIndulgenceRec, dict ) )
		
instance = AntiIndulgenceRec()
# -*- coding: gb18030 -*-


class InvoiceDataType:
	"""
	"""
	def getDictFromObj( self, obj ):
		"""
		"""
		return obj
		
	def createObjFromDict( self, dictData ):
		"""
		"""
		return dictData
		
	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.
		
		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return True
		
		
instance = InvoiceDataType()
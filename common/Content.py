# -*- coding: gb18030 -*-



class Content:
	"""
	内容
	"""
	def __init__( self ):
		"""
		"""
		self.key = ""												#一个内容关联的 临时 属性的 "key"
		self.val1 = 0												
		self.val2 = 0
		
	def beginContent( self, obj ):
		"""
		内容开始
		"""
		pass
	
	def onContent( self, obj ):
		"""
		内容执行
		"""
		pass
	
	def doContent( self, obj ):
		"""
		"""
		self.beginContent( obj )
		self.onContent( obj )
	
	def onConditionChange( self, obj, params ):
		"""
		一个条件发生变化，通知内容
		"""
		if not self.doConditionChange( obj, params ):
			return
		self.val1 += 1
		if self.val1 >= self.val2:
			self.endContent( obj )
	
	def doConditionChange(  self, obj, params ):
		"""
		对条件进行处理
		"""
		return True

	def endContent( self, obj ):
		"""
		内容结束
		"""
		obj.onContentFinish()


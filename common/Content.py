# -*- coding: gb18030 -*-



class Content:
	"""
	����
	"""
	def __init__( self ):
		"""
		"""
		self.key = ""												#һ�����ݹ����� ��ʱ ���Ե� "key"
		self.val1 = 0												
		self.val2 = 0
		
	def beginContent( self, obj ):
		"""
		���ݿ�ʼ
		"""
		pass
	
	def onContent( self, obj ):
		"""
		����ִ��
		"""
		pass
	
	def doContent( self, obj ):
		"""
		"""
		self.beginContent( obj )
		self.onContent( obj )
	
	def onConditionChange( self, obj, params ):
		"""
		һ�����������仯��֪ͨ����
		"""
		if not self.doConditionChange( obj, params ):
			return
		self.val1 += 1
		if self.val1 >= self.val2:
			self.endContent( obj )
	
	def doConditionChange(  self, obj, params ):
		"""
		���������д���
		"""
		return True

	def endContent( self, obj ):
		"""
		���ݽ���
		"""
		obj.onContentFinish()


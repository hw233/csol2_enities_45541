# -*- coding: gb18030 -*-

class DaoXinGrid:
	"""
	���ĸ���
	"""
	def __init__( self, storageID, orderID, isActive, UID ):
		self.parentStorage = storageID
		self.orderID = orderID			# ���ڰ���λID
		self.active = isActive			# �Ƿ񼤻�
		self.canEquip = False 			# �Ƿ����װ��
		self.daofaUID = UID 			# ����UID

	def hasDaofa( self ):
		"""
		�жϸ��������Ƿ�װ���˵���
		"""
		return self.daofaUID != 0

	def getOrder( self ):
		"""
		��ǰ�������ڰ���λ
		"""
		return self.orderID

	def isActive( self ):
		"""
		�����Ƿ񼤻�
		"""
		return self.active

	def setActive( self, isActive ):
		"""
		���ø��Ӽ���
		"""
		self.active = isActive

	def getDaofaUID( self ):
		"""
		��õ���
		"""
		return self.daofaUID

	def removeDaofa( self,uid ):
		"""
		�Ƴ�����
		"""
		self.daofaUID = 0
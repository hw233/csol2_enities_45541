# -*- coding: gb18030 -*-

class DaoXinGrid:
	"""
	道心格子
	"""
	def __init__( self, storageID, orderID, isActive, UID ):
		self.parentStorage = storageID
		self.orderID = orderID			# 所在包裹位ID
		self.active = isActive			# 是否激活
		self.canEquip = False 			# 是否可以装备
		self.daofaUID = UID 			# 道法UID

	def hasDaofa( self ):
		"""
		判断格子里面是否装备了道心
		"""
		return self.daofaUID != 0

	def getOrder( self ):
		"""
		当前格子所在包裹位
		"""
		return self.orderID

	def isActive( self ):
		"""
		格子是否激活
		"""
		return self.active

	def setActive( self, isActive ):
		"""
		设置格子激活
		"""
		self.active = isActive

	def getDaofaUID( self ):
		"""
		获得道法
		"""
		return self.daofaUID

	def removeDaofa( self,uid ):
		"""
		移除道法
		"""
		self.daofaUID = 0
# -*- coding: gb18030 -*-

from DaoXinGrid import DaoXinGrid
import csdefine

class DaoXinStorage:
	"""
	道心容器
	"""
	def __init__( self, activeOrder, maxSpace, storageID ):
		self.gridList = {}
		self.activeOrder = activeOrder 	# 默认开启1个格子
		self.maxSpace = maxSpace
		self.storageID = storageID
		self.initDaoXinGrid()

	def initDaoXinGrid( self ):
		"""
		初始化所有的格子
		"""
		for i in xrange( self.maxSpace ):
			isActive = False
			if i <= self.activeOrder:
				isActive = True
			self.gridList[i] = DaoXinGrid(  self.storageID, i, isActive, 0 )

	def addDaofa( self, orderID, uid ):
		"""
		将道法放置到道心的某个格子上
		"""
		if orderID >  self.activeOrder:	# 如果目标位置未激活，不做任何操作
			return False
		self.gridList[ orderID ] = DaoXinGrid( self.storageID, orderID, 1, uid )

	def removeDaofa( self, orderID, uid ):
		"""
		移除一个道法
		"""
		self.gridList[ orderID ].removeDafa( uid )

	def getDaofaList( self ):
		"""
		获得包裹中的道法
		"""
		daofaUIDList = []
		for index, grid in self.gridList.iteritems():
			uid = grid.getDaofaUID()
			if index <= self.activeOrder and uid != 0:
				daofaUIDList.append( grid.getDaofaUID() )
		return daofaUIDList

	def setActiveOrder( self, order  ):
		"""
		设置激活格子序号
		"""
		self.activeOrder = order

class ZhengDaoStorage:
	"""
	证道容器类,不继承道心容器
	"""
	def __init__( self, activeOrder, maxSpace, storageID ):
		self.daofaList = []
		self.activeOrder = activeOrder
		self.maxSpace  = maxSpace
		self.storageID = storageID
	
	def addDaofa( self, orderID, uid ):
		"""
		添加道法
		"""
		self.daofaList.append( uid  )
	
	def removeDaofa( self,orderID, uid ):
		"""
		移除道法
		"""
		self.daofaList.remove( uid )

	def getDaofaList( self ):
		"""
		获得道法
		"""
		return self.daofaList

class DaoXinComStorage( DaoXinStorage ):
	"""
	道心普通容器类
	"""
	def __init__( self, activeOrder, maxSpace, storageID ):
		DaoXinStorage.__init__( self, activeOrder, maxSpace, storageID )

class DaoXinEquipStorage( DaoXinStorage ):
	"""
	角色道心容器类，主要用于装备道心
	"""
	def __init__( self, activeOrder, maxSpace, storageID ):
		DaoXinStorage.__init__( self, activeOrder, maxSpace, storageID )


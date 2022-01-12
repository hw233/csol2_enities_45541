# -*- coding: gb18030 -*-

from DaoXinGrid import DaoXinGrid
import csdefine
from bwdebug import *

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

	def addDaofa( self, owner, orderID, uid, isInitAdded = False, isInEquipSwap = False ):
		"""
		将道法放置到道心的某个格子上
		"""
		if orderID >  self.activeOrder:	# 如果目标位置未激活，不做任何操作
			return False
		self.gridList[ orderID ] = DaoXinGrid( self.storageID, orderID, 1, uid )

	def removeDaofa( self, owner, orderID, uid, isInEquipSwap = False ):
		"""
		移除一个道法
		"""
		self.gridList[ orderID ].removeDaofa( uid )

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
		if order >= self.maxSpace:
			return 
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

	def addDaofa( self, owner, orderID, uid, isInitAdded = False, isInEquipSwap = False ):
		"""
		添加道法
		"""
		self.daofaList.append( uid  )
	
	def removeDaofa( self, owner,orderID, uid, isInEquipSwap = False ):
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

	def addDaofa( self, owner, orderID, uid, isInitAdded = False, isInEquipSwap = False ):
		"""
		将道法装备到玩家身上
		"""
		if orderID >  self.activeOrder:	# 如果目标位置未激活，不做任何操作
			return 
		self.gridList[ orderID ] = DaoXinGrid( self.storageID, orderID, 1, uid )
		daofa = owner.uidToDaofa( uid )
		owner.addEquipeDaofa( daofa )
		if isInitAdded:						#初始化添加
			return 
		# 准备道法
		
		if isInEquipSwap:						#在装备道心内移动，则不需要重新再装备
			return
		owner.cell.wieldDaofa( daofa )

	def removeDaofa( self, owner, orderID, uid, isInEquipSwap = False ):
		"""
		移除一个道法
		"""
		self.gridList[ orderID ].removeDaofa( uid )
		daofa = None
		for df in owner.equipDaofa:
			if df.getUID() == uid:
				daofa = df
				break
		# 移除装备属性
		if daofa:
			owner.removeEquipDaofa( daofa.getUID() )
			if not isInEquipSwap:
				owner.cell.unwieldDaofa( daofa )
		else:
			ERROR_MSG( "Remove a not equipDaofa daofa , uid  %i, orderID %i" % ( uid, orderID ) )
			daofa = owner.uidToDaofa( uid )
			if not daofa:
				ERROR_MSG( "Daofa: uid %i, orderID %i is not existe in role %s" % ( uid, orderID, owner.getNameAndID() ) )


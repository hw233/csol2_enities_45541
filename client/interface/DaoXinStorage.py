# -*- coding: gb18030 -*-

from DaoXinGrid import DaoXinGrid
import csdefine

class DaoXinStorage:
	"""
	��������
	"""
	def __init__( self, activeOrder, maxSpace, storageID ):
		self.gridList = {}
		self.activeOrder = activeOrder 	# Ĭ�Ͽ���1������
		self.maxSpace = maxSpace
		self.storageID = storageID
		self.initDaoXinGrid()

	def initDaoXinGrid( self ):
		"""
		��ʼ�����еĸ���
		"""
		for i in xrange( self.maxSpace ):
			isActive = False
			if i <= self.activeOrder:
				isActive = True
			self.gridList[i] = DaoXinGrid(  self.storageID, i, isActive, 0 )

	def addDaofa( self, orderID, uid ):
		"""
		���������õ����ĵ�ĳ��������
		"""
		if orderID >  self.activeOrder:	# ���Ŀ��λ��δ��������κβ���
			return False
		self.gridList[ orderID ] = DaoXinGrid( self.storageID, orderID, 1, uid )

	def removeDaofa( self, orderID, uid ):
		"""
		�Ƴ�һ������
		"""
		self.gridList[ orderID ].removeDafa( uid )

	def getDaofaList( self ):
		"""
		��ð����еĵ���
		"""
		daofaUIDList = []
		for index, grid in self.gridList.iteritems():
			uid = grid.getDaofaUID()
			if index <= self.activeOrder and uid != 0:
				daofaUIDList.append( grid.getDaofaUID() )
		return daofaUIDList

	def setActiveOrder( self, order  ):
		"""
		���ü���������
		"""
		self.activeOrder = order

class ZhengDaoStorage:
	"""
	֤��������,���̳е�������
	"""
	def __init__( self, activeOrder, maxSpace, storageID ):
		self.daofaList = []
		self.activeOrder = activeOrder
		self.maxSpace  = maxSpace
		self.storageID = storageID
	
	def addDaofa( self, orderID, uid ):
		"""
		��ӵ���
		"""
		self.daofaList.append( uid  )
	
	def removeDaofa( self,orderID, uid ):
		"""
		�Ƴ�����
		"""
		self.daofaList.remove( uid )

	def getDaofaList( self ):
		"""
		��õ���
		"""
		return self.daofaList

class DaoXinComStorage( DaoXinStorage ):
	"""
	������ͨ������
	"""
	def __init__( self, activeOrder, maxSpace, storageID ):
		DaoXinStorage.__init__( self, activeOrder, maxSpace, storageID )

class DaoXinEquipStorage( DaoXinStorage ):
	"""
	��ɫ���������࣬��Ҫ����װ������
	"""
	def __init__( self, activeOrder, maxSpace, storageID ):
		DaoXinStorage.__init__( self, activeOrder, maxSpace, storageID )


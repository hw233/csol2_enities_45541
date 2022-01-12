# -*- coding: gb18030 -*-

from DaoXinGrid import DaoXinGrid
import csdefine
from bwdebug import *

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

	def addDaofa( self, owner, orderID, uid, isInitAdded = False, isInEquipSwap = False ):
		"""
		���������õ����ĵ�ĳ��������
		"""
		if orderID >  self.activeOrder:	# ���Ŀ��λ��δ��������κβ���
			return False
		self.gridList[ orderID ] = DaoXinGrid( self.storageID, orderID, 1, uid )

	def removeDaofa( self, owner, orderID, uid, isInEquipSwap = False ):
		"""
		�Ƴ�һ������
		"""
		self.gridList[ orderID ].removeDaofa( uid )

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
		if order >= self.maxSpace:
			return 
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

	def addDaofa( self, owner, orderID, uid, isInitAdded = False, isInEquipSwap = False ):
		"""
		��ӵ���
		"""
		self.daofaList.append( uid  )
	
	def removeDaofa( self, owner,orderID, uid, isInEquipSwap = False ):
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

	def addDaofa( self, owner, orderID, uid, isInitAdded = False, isInEquipSwap = False ):
		"""
		������װ�����������
		"""
		if orderID >  self.activeOrder:	# ���Ŀ��λ��δ��������κβ���
			return 
		self.gridList[ orderID ] = DaoXinGrid( self.storageID, orderID, 1, uid )
		daofa = owner.uidToDaofa( uid )
		owner.addEquipeDaofa( daofa )
		if isInitAdded:						#��ʼ�����
			return 
		# ׼������
		
		if isInEquipSwap:						#��װ���������ƶ�������Ҫ������װ��
			return
		owner.cell.wieldDaofa( daofa )

	def removeDaofa( self, owner, orderID, uid, isInEquipSwap = False ):
		"""
		�Ƴ�һ������
		"""
		self.gridList[ orderID ].removeDaofa( uid )
		daofa = None
		for df in owner.equipDaofa:
			if df.getUID() == uid:
				daofa = df
				break
		# �Ƴ�װ������
		if daofa:
			owner.removeEquipDaofa( daofa.getUID() )
			if not isInEquipSwap:
				owner.cell.unwieldDaofa( daofa )
		else:
			ERROR_MSG( "Remove a not equipDaofa daofa , uid  %i, orderID %i" % ( uid, orderID ) )
			daofa = owner.uidToDaofa( uid )
			if not daofa:
				ERROR_MSG( "Daofa: uid %i, orderID %i is not existe in role %s" % ( uid, orderID, owner.getNameAndID() ) )


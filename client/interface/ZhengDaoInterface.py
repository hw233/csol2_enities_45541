# -*- coding: gb18030 -*-

from DaoXinStorage import *
from bwdebug import *
import event.EventCenter as ECenter
import csdefine

class ZhengDaoInterface:
	"""
	֤��ϵͳ�ӿ�
	"""
	def __init__( self ):
		self.daoXinBags = {}
		self.daofa = []
		self.activeGuide = []
		self.activeGrid = []
		self.daofaList = []

	def onJiYuanChanged( self, jiyuan ):
		"""
		define method
		��Եֵ�ı�
		"""
		self.jiyuan = jiyuan
		ECenter.fireEvent( "EVT_ON_SERMON_JIYUAN_CHANGED", jiyuan )
	
	def onDaofaChanged( self, daofa ):
		"""
		define method
		�������ݸı�
		"""
		for df in self.daofa:
			if df.getUID() == daofa.getUID():
				index = self.daofa.index( df )
				self.daofa[ index ] = daofa
				ECenter.fireEvent( "EVT_ON_SERMON_DAOFA_CHANGED", daofa )
				break

	def onActiveGuideChanged( self, activeGuide ):
		"""
		define method
		���ʦ�ı�
		"""
		self.activeGuide = activeGuide
		ECenter.fireEvent( "EVT_ON_SERMON_ACTIVE_GUIDE_CHANGE", activeGuide )

	def onActiveGridChanged( self, activeGrid ):
		"""
		define method
		������Ӹı�
		"""
		self.activeGrid = activeGrid
		for grid in self.activeGrid:
			print grid["daoXinID"], " ", grid["actOrder"]
		self.updateStorages()

	def onZDScoreChanged( self, score ):
		"""
		define method
		֤�����ָı�
		"""
		self.ZDScore = score 
		ECenter.fireEvent( "EVT_ON_SERMON_SCORE_CHANGED", score )

	def onZDRecordChanged( self, record ):
		"""
		define method
		֤�������ı�
		"""
		self.ZDRecord = record
		ECenter.fireEvent( "EVT_ON_SERMON_RECORD_CHANGED", record )

	def onYBActGuideChanged( self, record ):
		"""
		define method
		Ԫ���ٻ���ʦ�����ı�
		"""
		self.ybActGuideRecord = record

	def updateStorages( self ):
		"""
		��ʼ��֤���漰�����а���
		"""
		if len( self.daoXinBags ) == 0:
			self.daoXinBags = {	csdefine.KB_ZHENG_DAO_ID: ZhengDaoStorage( self.getActiveOrder( csdefine.KB_ZHENG_DAO_ID ), csdefine.KB_ZD_MAX_SPACE,  csdefine.KB_ZHENG_DAO_ID),
								csdefine.KB_COM_DAO_XIN_ID: DaoXinComStorage( self.getActiveOrder( csdefine.KB_COM_DAO_XIN_ID ), csdefine.KB_ZD_MAX_SPACE, csdefine.KB_COM_DAO_XIN_ID ),
								csdefine.KB_EQUIP_DAO_XIN_ID: DaoXinEquipStorage( self.getActiveOrder( csdefine.KB_EQUIP_DAO_XIN_ID ), csdefine.KB_ZD_MAX_EQUIP_SPACE, csdefine.KB_EQUIP_DAO_XIN_ID ),
								}
		
		for grid in self.activeGrid:
			daoxinID, order  = grid["daoXinID"], grid["actOrder"]
			if self.daoXinBags[ daoxinID ].activeOrder == order:
				continue
				self.daoXinBags[daoXinID].setActiveOrder( order )
				for orderID in self.daoXinBags[daoXinID].gridList.keys():
					if orderID <= order:
						self.daoXinBags[daoXinID].gridList[orderID].setActive( 1 )

	def getActiveOrder( self ,daoXinID ):
		"""
		��õ��ĵļ���������
		"""
		if daoXinID == csdefine.KB_ZHENG_DAO_ID:	# ֤������
			return csdefine.KB_ZD_MAX_SPACE - 1
		
		for record in self.activeGrid:
			dxid, activeOrder = record[ "daoXinID"], record["actOrder"]
			if dxid == daoXinID:
				return activeOrder

	def onAddDaofa( self, daofa ):
		"""
		define method 
		��ӵ���
		"""
		self.daofa.append( daofa )
		daoxinID, orderID = daofa.getDaoXinID(), daofa.getOrder()
		uid = daofa.getUID()
		self.daoXinBags[ daoxinID ].addDaofa( orderID, uid )
		ECenter.fireEvent( "EVT_ON_SERMON_ADD_DAOFA", daoxinID, orderID, uid )

	def onRemoveDaofa( self, uid, isPickup ):
		"""
		define method
		�Ƴ�����
		"""
		daofa = self.uidToDaofa( uid )
		daoxinID, orderID = daofa.getDaoXinID(), daofa.getOrder()
		self.daofa.remove( daofa )
		self.daoXinBags[daoxinID].removeDaofa( orderID, daofa.getUID() )
		ECenter.fireEvent( "EVT_ON_SERMON_REMOVE_DAOFA", daoxinID, orderID, uid, isPickup )
		
	def uidToDaofa( self, uid ):
		"""
		������Ʒ��uid�����Ʒ��ʵ��
		"""
		for daofa in self.daofa:
			if daofa.getUID() == uid:
				return daofa

	def getAllZhengDaoData( self ):
		"""
		��ȡ֤��ϵͳ���������ݣ������ã�
		"""
		print "-----------activeGrid------------"
		for grid in self.activeGrid:
			print grid["daoXinID"], "  ", grid["actOrder"]
		print "-----------daofaList-------------"
		for daoxinID in self.daoXinBags.keys():
			print self.daoXinBags[daoxinID].getDaofaList()
		print "---------- daofa-----------------"
		for daofa in self.daofa:
			print "UID:", daofa.getUID(), "DXID:", daofa.getDaoXinID(), "Order:", daofa.getOrder(), "QUA:", daofa.getQuality(), "ID:", daofa.getType(), "Exp:", daofa.exp, "Level:", daofa.level, "isLocked:", daofa.getLockState()
		print "----------------------------------"
		print "JIYUAN:", self.jiyuan, "ZDScore:", self.ZDScore, "ActiveGuid��", self.activeGuide
		print "Free zhengdao:", self.ZDRecord.getDegree(), "lastTime:", self.ZDRecord._lastTime

	def onActiveGridCost( self, orderID, yuanbao ):
		"""
		�����������Ԫ����
		"""
		ECenter.fireEvent( "EVT_ON_SERMON_ACTIVE_GRID_COST", orderID, yuanbao )

	def grid_activeResult( self, daoxinID, orderID, result ):
		"""
		���Ӽ�����
		"""
		ECenter.fireEvent( "EVT_ON_SERMON_ACTIVE_GRID_RESULT", daoxinID, orderID, result )
	
	def autoCompose( self, storageIndex ):
		"""
		һ���ϳ�
		"""
		self.base.autoCompose( storageIndex )
	
	def autoPickUp( self ):
		"""
		һ��ʰȡ
		"""
		self.base.autoPickUp()
	
	def autoZhengDao( self ):
		"""
		һ��֤��
		"""
		self.base.autoZhengDao()
	
	def pickUpDaofa( self, uid ):
		"""
		ʰȡ����
		"""
		self.base.pickUpDaofa( uid )
	
	def sellDaofa( self, uid ):
		"""
		��������
		"""
		self.base.sellDaofa( uid )
	
	def clickGuide( self, guideLevel ):
		"""
		���ʦ
		"""
		self.base.clickGuide( guideLevel )
	
	def getActiveGridCost( self, orderID ):
		"""
		���󼤻���ĸ���
		"""
		self.base.getActiveGridCost( orderID )
	
	def confirmActiveGrid( self, orderID ):
		"""
		ȷ�ϼ�����ĸ���
		"""
		self.base.confirmActiveGrid( orderID )
	
	def moveDaofaTo( self, srcUID, dstDaoxinID, dstOrder ):
		"""
		�϶�����
		"""
		self.base.moveDaofaTo( srcUID, dstDaoxinID, dstOrder )
	
	def autoMoveDaofaTo( self, srcUID, dstDaoxinID ):
		"""
		�Զ��ƶ����ĵ�Ŀ����
		"""
		self.base.autoMoveDaofaTo( srcUID, dstDaoxinID )
		
	def confirmComposeDaofa( self, srcUID, dstUID ):
		"""
		��������
		"""
		self.base.confirmComposeDaofa( srcUID, dstUID )

	def onComposeDaofa( self, srcUID, dstUID, exp ):
		"""
		�ϳɵ���
		"""
		srcDaofa = self.uidToDaofa( srcUID )
		dstDaofa = self.uidToDaofa( dstUID )
		ECenter.fireEvent( "EVT_ON_SERMON_COMPOSE_DAOFA_CONFIRM", srcUID, dstUID, exp )

	def ybActiveGuide( self, guideLevel, yuanbao ):
		"""
		Ԫ���ٻ���ʦ
		"""
		self.base.yuanBaoActiveGuide( guideLevel, yuanbao )

	def lockDaofa( self, uid ):
		"""
		��������
		"""
		self.base.lockDaofa( uid )

	def onLockDaofa( self, uid ):
		"""
		define method
		����\��������
		"""
		daofa = self.uidToDaofa( uid )
		ECenter.fireEvent( "EVT_ON_SERMON_LOCK_DAOFA", daofa )

	def request_scoreShopData( self ):
		"""
		������ֶһ���������
		"""
		self.base.request_scoreShopData()

	def receive_scoreShopData( self, speDaofa ):
		"""
		define method
		���յ�������
		"""
		quality, type, score, level = speDaofa[0], speDaofa[1], speDaofa[2], speDaofa[3]
		ECenter.fireEvent( "EVT_ON_SERMON_RECEIVE_SHOP_ITEM", speDaofa )
		self.daofaList.append( speDaofa )

	def scoreExchangeDaofa( self, quality, type  ):
		"""
		�һ�����
		"""
		self.base.scoreExchangeDaofa( quality, type )
	
	def confirmRemoveDaofa( self, uid ):
		"""
		ȷ���Ƴ�����
		"""
		self.base.confirmRemoveDaofa( uid )
	
	def confirmAutoCompose( self, daoxinID ):
		"""
		һ���ϳ�ȷ��
		"""
		self.base.confirmAutoCompose( daoxinID )

	def onAutoCompose( self, daoxinID, uid ):
		"""
		define method
		һ���ϳ�ȷ��
		"""
		ECenter.fireEvent( "EVT_ON_SERMON_AUTO_COMPOSE_CONFIRM", daoxinID, uid )
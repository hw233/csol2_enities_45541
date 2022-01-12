# -*- coding: gb18030 -*-

from DaoXinStorage import *
from bwdebug import *
import event.EventCenter as ECenter
import csdefine

class ZhengDaoInterface:
	"""
	证道系统接口
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
		机缘值改变
		"""
		self.jiyuan = jiyuan
		ECenter.fireEvent( "EVT_ON_SERMON_JIYUAN_CHANGED", jiyuan )
	
	def onDaofaChanged( self, daofa ):
		"""
		define method
		道法数据改变
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
		激活导师改变
		"""
		self.activeGuide = activeGuide
		ECenter.fireEvent( "EVT_ON_SERMON_ACTIVE_GUIDE_CHANGE", activeGuide )

	def onActiveGridChanged( self, activeGrid ):
		"""
		define method
		激活格子改变
		"""
		self.activeGrid = activeGrid
		for grid in self.activeGrid:
			print grid["daoXinID"], " ", grid["actOrder"]
		self.updateStorages()

	def onZDScoreChanged( self, score ):
		"""
		define method
		证道积分改变
		"""
		self.ZDScore = score 
		ECenter.fireEvent( "EVT_ON_SERMON_SCORE_CHANGED", score )

	def onZDRecordChanged( self, record ):
		"""
		define method
		证道次数改变
		"""
		self.ZDRecord = record
		ECenter.fireEvent( "EVT_ON_SERMON_RECORD_CHANGED", record )

	def onYBActGuideChanged( self, record ):
		"""
		define method
		元宝召唤导师次数改变
		"""
		self.ybActGuideRecord = record

	def updateStorages( self ):
		"""
		初始化证道涉及的所有包裹
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
		获得道心的激活格子序号
		"""
		if daoXinID == csdefine.KB_ZHENG_DAO_ID:	# 证道包裹
			return csdefine.KB_ZD_MAX_SPACE - 1
		
		for record in self.activeGrid:
			dxid, activeOrder = record[ "daoXinID"], record["actOrder"]
			if dxid == daoXinID:
				return activeOrder

	def onAddDaofa( self, daofa ):
		"""
		define method 
		添加道法
		"""
		self.daofa.append( daofa )
		daoxinID, orderID = daofa.getDaoXinID(), daofa.getOrder()
		uid = daofa.getUID()
		self.daoXinBags[ daoxinID ].addDaofa( orderID, uid )
		ECenter.fireEvent( "EVT_ON_SERMON_ADD_DAOFA", daoxinID, orderID, uid )

	def onRemoveDaofa( self, uid, isPickup ):
		"""
		define method
		移除道法
		"""
		daofa = self.uidToDaofa( uid )
		daoxinID, orderID = daofa.getDaoXinID(), daofa.getOrder()
		self.daofa.remove( daofa )
		self.daoXinBags[daoxinID].removeDaofa( orderID, daofa.getUID() )
		ECenter.fireEvent( "EVT_ON_SERMON_REMOVE_DAOFA", daoxinID, orderID, uid, isPickup )
		
	def uidToDaofa( self, uid ):
		"""
		根绝物品的uid获得物品的实例
		"""
		for daofa in self.daofa:
			if daofa.getUID() == uid:
				return daofa

	def getAllZhengDaoData( self ):
		"""
		获取证道系统的所有数据（调试用）
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
		print "JIYUAN:", self.jiyuan, "ZDScore:", self.ZDScore, "ActiveGuid：", self.activeGuide
		print "Free zhengdao:", self.ZDRecord.getDegree(), "lastTime:", self.ZDRecord._lastTime

	def onActiveGridCost( self, orderID, yuanbao ):
		"""
		激活格子所需元宝数
		"""
		ECenter.fireEvent( "EVT_ON_SERMON_ACTIVE_GRID_COST", orderID, yuanbao )

	def grid_activeResult( self, daoxinID, orderID, result ):
		"""
		格子激活结果
		"""
		ECenter.fireEvent( "EVT_ON_SERMON_ACTIVE_GRID_RESULT", daoxinID, orderID, result )
	
	def autoCompose( self, storageIndex ):
		"""
		一键合成
		"""
		self.base.autoCompose( storageIndex )
	
	def autoPickUp( self ):
		"""
		一键拾取
		"""
		self.base.autoPickUp()
	
	def autoZhengDao( self ):
		"""
		一键证道
		"""
		self.base.autoZhengDao()
	
	def pickUpDaofa( self, uid ):
		"""
		拾取道法
		"""
		self.base.pickUpDaofa( uid )
	
	def sellDaofa( self, uid ):
		"""
		卖出道法
		"""
		self.base.sellDaofa( uid )
	
	def clickGuide( self, guideLevel ):
		"""
		激活导师
		"""
		self.base.clickGuide( guideLevel )
	
	def getActiveGridCost( self, orderID ):
		"""
		请求激活道心格子
		"""
		self.base.getActiveGridCost( orderID )
	
	def confirmActiveGrid( self, orderID ):
		"""
		确认激活道心格子
		"""
		self.base.confirmActiveGrid( orderID )
	
	def moveDaofaTo( self, srcUID, dstDaoxinID, dstOrder ):
		"""
		拖动道心
		"""
		self.base.moveDaofaTo( srcUID, dstDaoxinID, dstOrder )
	
	def autoMoveDaofaTo( self, srcUID, dstDaoxinID ):
		"""
		自动移动道心到目标栏
		"""
		self.base.autoMoveDaofaTo( srcUID, dstDaoxinID )
		
	def confirmComposeDaofa( self, srcUID, dstUID ):
		"""
		道法吞噬
		"""
		self.base.confirmComposeDaofa( srcUID, dstUID )

	def onComposeDaofa( self, srcUID, dstUID, exp ):
		"""
		合成道法
		"""
		srcDaofa = self.uidToDaofa( srcUID )
		dstDaofa = self.uidToDaofa( dstUID )
		ECenter.fireEvent( "EVT_ON_SERMON_COMPOSE_DAOFA_CONFIRM", srcUID, dstUID, exp )

	def ybActiveGuide( self, guideLevel, yuanbao ):
		"""
		元宝召唤导师
		"""
		self.base.yuanBaoActiveGuide( guideLevel, yuanbao )

	def lockDaofa( self, uid ):
		"""
		道法锁定
		"""
		self.base.lockDaofa( uid )

	def onLockDaofa( self, uid ):
		"""
		define method
		锁定\解锁道法
		"""
		daofa = self.uidToDaofa( uid )
		ECenter.fireEvent( "EVT_ON_SERMON_LOCK_DAOFA", daofa )

	def request_scoreShopData( self ):
		"""
		请求积分兑换道法数据
		"""
		self.base.request_scoreShopData()

	def receive_scoreShopData( self, speDaofa ):
		"""
		define method
		接收道法数据
		"""
		quality, type, score, level = speDaofa[0], speDaofa[1], speDaofa[2], speDaofa[3]
		ECenter.fireEvent( "EVT_ON_SERMON_RECEIVE_SHOP_ITEM", speDaofa )
		self.daofaList.append( speDaofa )

	def scoreExchangeDaofa( self, quality, type  ):
		"""
		兑换道法
		"""
		self.base.scoreExchangeDaofa( quality, type )
	
	def confirmRemoveDaofa( self, uid ):
		"""
		确认移除道法
		"""
		self.base.confirmRemoveDaofa( uid )
	
	def confirmAutoCompose( self, daoxinID ):
		"""
		一键合成确认
		"""
		self.base.confirmAutoCompose( daoxinID )

	def onAutoCompose( self, daoxinID, uid ):
		"""
		define method
		一件合成确认
		"""
		ECenter.fireEvent( "EVT_ON_SERMON_AUTO_COMPOSE_CONFIRM", daoxinID, uid )
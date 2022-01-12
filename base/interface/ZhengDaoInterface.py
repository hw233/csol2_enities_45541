# -*- coding: gb18030 -*-

from DaoXinStorage import *
from ZDDataLoader import *
from Function import newUID
from DaofaTypeImpl import instance as g_daofa

from bwdebug import *
import csstatus
import csdefine
import ItemTypeEnum
import random
import copy
import csconst

g_ZDGuide = ZDGuidDataLoader.instance()
g_ZDType = DaofaTypeRateLoader.instance()
g_daofaData = DaofaDataLoader.instance()
g_daofaShop = ZDScoreShopLoader.instance()

FREE_ZHENG_DAO_TIMES = 1
YUAN_BAO_ACTIVE_GUIDE_TIMES = 1
DAO_XIN_ORIGINAL_GRID = { csdefine.KB_COM_DAO_XIN_ID: 9, csdefine.KB_EQUIP_DAO_XIN_ID: 0 } 

class ZhengDaoInterface:
	"""
	证道系统接口
	"""
	def __init__( self ):
		self.equipDaofa = []
		if not self.ZDRecord.checklastTime():
			self.ZDRecord.reset()
		if not self.ybActGuideRecord.checklastTime():
			self.ybActGuideRecord.reset()

	def onGetCell( self ):
		"""
		玩家cell创建完毕
		"""
		self.initZDDatas()

	def initZDDatas( self ):
		"""
		初始化证道系统数据
		"""
		if len( self.activeGuide  ) == 0:	# 保证导师1是激活的
			self.activeGuide.append( 1 )
		
		if len( self.activeGrid ) == 0:		# 初始化道心格子
			levelDiff = 0
			if self.level >= 30:
				levelDiff = ( self.level - 30 ) / 10
			activeEquipOrder = min( levelDiff, csdefine.KB_ZD_MAX_EQUIP_SPACE -1  )
			self.activeGrid = [{ "daoXinID":csdefine.KB_ZHENG_DAO_ID, "actOrder":  csdefine.KB_ZD_MAX_SPACE -1 , },
								{ "daoXinID":csdefine.KB_COM_DAO_XIN_ID, "actOrder":  DAO_XIN_ORIGINAL_GRID[ csdefine.KB_COM_DAO_XIN_ID ], },
								{ "daoXinID":csdefine.KB_EQUIP_DAO_XIN_ID, "actOrder":  activeEquipOrder, },
							]
		self.initStorages()					# 初始化证道包裹

	def getActiveOrder( self ,daoXinID ):
		"""
		获得道心的激活格子序号
		"""
		if daoXinID == csdefine.KB_ZHENG_DAO_ID:	# 证道包裹
			return csdefine.KB_ZD_MAX_SPACE -1
		
		for record in self.activeGrid:
			dxid, activeOrder = record[ "daoXinID"], record["actOrder"]
			if dxid == daoXinID:
				return activeOrder

	def initStorages( self ):
		"""
		初始化证道涉及的所有包裹
		"""
		self.daoXinBags = {	csdefine.KB_ZHENG_DAO_ID: ZhengDaoStorage( self.getActiveOrder( csdefine.KB_ZHENG_DAO_ID ), csdefine.KB_ZD_MAX_SPACE,  csdefine.KB_ZHENG_DAO_ID),
							csdefine.KB_COM_DAO_XIN_ID: DaoXinComStorage( self.getActiveOrder( csdefine.KB_COM_DAO_XIN_ID ), csdefine.KB_ZD_MAX_SPACE, csdefine.KB_COM_DAO_XIN_ID ),
							csdefine.KB_EQUIP_DAO_XIN_ID: DaoXinEquipStorage( self.getActiveOrder( csdefine.KB_EQUIP_DAO_XIN_ID ), csdefine.KB_ZD_MAX_EQUIP_SPACE, csdefine.KB_EQUIP_DAO_XIN_ID ),
							}
		
		illegalList = []		# 非法数据列表
		for daofa in self.daofa:
			daoXinID, orderID = daofa.getDaoXinID(), daofa.getOrder()
			if daoXinID == 0 or daofa.getType() not in g_daofaData.getAllTypeByQuality( daofa.getQuality() ):
				illegalList.append( daofa )
				continue
			
			self.daoXinBags[ daoXinID ].addDaofa( self, orderID, daofa.getUID(), True )
		
		for daofa in illegalList: # 移除非法数据
			self.daofa.remove( daofa )

	def daofa_updateClient( self ):
		"""
		请求更新客户端道法
		"""
		self.client.onActiveGuideChanged( self.activeGuide ) # 发送导师数据
		self.client.onActiveGridChanged( self.activeGrid )   # 发送道心格子数据
		for daofa in self.daofa:
			self.client.onAddDaofa( daofa )
		self.client.onInitialized( csdefine.ROLE_INIT_DAOFA )

	def zd_onLevelUp( self ):
		"""
		角色等级发生变化
		"""
		# 激活装备道心格子
		if self.level < 30:
			return 
		
		order = ( self.level - 30 ) / 10
		if order != 0:
			self.activeDaoXinGrid( csdefine.KB_EQUIP_DAO_XIN_ID, order )
			self.client.grid_activeResult( csdefine.KB_EQUIP_DAO_XIN_ID, order, 1 )

	def add_jiyuan( self, jiyuan ):
		"""
		获得机缘
		"""
		self.jiyuan += jiyuan
		self.client.onJiYuanChanged( self.jiyuan )

	def pay_jiyuan( self, needJiYuan ):
		"""
		消耗机缘
		"""
		assert self.jiyuan >= needJiYuan, " NeedJiYuan %i is bigger than self.jiyuan %i " % ( needJiYuan, self.jiyuan )

		self.jiyuan -= needJiYuan
		self.jiyuan = max( 0, self.jiyuan )
		self.client.onJiYuanChanged( self.jiyuan )

	def set_jiyuan( self, jiyuan ):
		"""
		设置机缘值
		"""
		self.jiyuan = jiyuan
		self.client.onJiYuanChanged( self.jiyuan )

	def addDaofa( self, daoxinID, orderID, daofa, isInEquipSwap = False ):
		"""
		添加道法
		"""
		daofa.setOrder( orderID )
		daofa.setDaoXinID( daoxinID )
		self.daofa.append( daofa )
		self.daoXinBags[ daoxinID ].addDaofa( self, orderID, daofa.getUID(), isInEquipSwap )
		self.client.onAddDaofa( daofa )
		INFO_MSG( "%s: UID %s, type %i, level %i, exp %i, quality %i ,order %i, daoXinID % i " % ( self.getNameAndID(), daofa.getUID(), daofa.type, daofa.level, daofa.exp, daofa.quality, daofa.order, daofa.daoXinID ) )

	def removeDaofa( self, daoxinID, orderID, daofa, isPickup = False, isInEquipSwap = False ):
		"""
		移除道法
		"""
		self.daoXinBags[daoxinID].removeDaofa( self, orderID, daofa.getUID(), isInEquipSwap )	# 包裹移除道法
		for daofaInst in self.daofa:
			if daofaInst.getUID() == daofa.getUID():
				self.daofa.remove( daofaInst )
				break
		self.client.onRemoveDaofa( daofa.getUID(), isPickup )
		INFO_MSG( " %s :UID %s, type %i, level %i, exp %i, quality %i ,order %i, daoXinID % i " % ( self.getNameAndID(), daofa.getUID(), daofa.type, daofa.level, daofa.exp, daofa.quality, daofa.order, daofa.daoXinID ) )

	def cleanAllDaofa( self ):
		"""
		清空身上所有的道法( 调试用 )
		"""
		daofaList = copy.deepcopy( self.daofa )
		for daofa in daofaList:
			if daofa.getDaoXinID() == csdefine.KB_EQUIP_DAO_XIN_ID:			# 装备在身上的道法不清楚
				continue
			self.removeDaofa( daofa.getDaoXinID(), daofa.getOrder(), daofa )
		INFO_MSG( "Role %s has cleaned all daofa except equiped! Remaining daofa is %s " % ( self.getNameAndID(),  self.daofa ) )

	def guideActive( self, guideLevel ):
		"""
		导师激活，根据要求，导师1是永远激活的
		"""
		activeRate = g_ZDGuide.getNextGuideActiveRate( guideLevel )
		rate = random.random()
		if rate < activeRate:	# 可以激活下一个导师
			self.activeGuide.append( guideLevel + 1 )

		if guideLevel != 1:		# 一旦被点击，就会变为未激活状态
			self.activeGuide.remove( guideLevel )
		
		self.activeGuide = list( set( self.activeGuide ) ) # 去重，排序
		self.client.onActiveGuideChanged( self.activeGuide )
		INFO_MSG( " %s: All active guide is %s after click guide %i" % ( self.getNameAndID(), self.activeGuide, guideLevel ) )

	def add_ZDScore( self , score ):
		"""
		添加证道积分
		"""
		self.ZDScore += score
		self.client.onZDScoreChanged( self.ZDScore )

	def pay_ZDScore( self, score ):
		"""
		消耗证道积分
		"""
		self.ZDScore -= score
		self.ZDScore = max( 0, self.ZDScore )
		self.client.onZDScoreChanged( self.ZDScore )

	def gain_ZDScore( self, guideLevel ):
		"""
		获得积分
		"""
		guidScore = g_ZDGuide.getScoreByLevel( self.level, guideLevel )
		self.add_ZDScore( guidScore )

	def set_ZDScore( self, score ):
		"""
		设置积分
		"""
		self.ZDScore = score
		self.client.onZDScoreChanged( self.ZDScore )

	def isDayFirstZD( self ):
		"""
		是否每天第一次证道
		"""
		if not self.ZDRecord.checklastTime():
			self.ZDRecord.reset()
		if self.ZDRecord.getDegree() >= FREE_ZHENG_DAO_TIMES:
			return False
		return True

	def enoughJiYuan( self, guideLevel ):
		"""
		判断是否有足够的机缘
		"""
		needJiYuan = g_ZDGuide.getCostJYByLevel( self.level, guideLevel )
		if not needJiYuan or  self.jiyuan < needJiYuan:
			return False
		return True

	def getDaoXinFreeOrder( self, dxid ):
		"""
		获得包裹里面空余的包裹位
		return order
		"""
		if dxid == csdefine.KB_ZHENG_DAO_ID:	# 证道包裹单独处理
			if len( self.daoXinBags[ dxid ].daofaList ) < csdefine.KB_ZD_MAX_SPACE:
				return len( self.daoXinBags[ dxid ].daofaList )
		else:	# 道心界面处理
			for index, grid in self.daoXinBags[ dxid ].gridList.iteritems():
				if not grid.hasDaofa() and grid.isActive():
					return grid.getOrder()
		return -1

	def createDaofa( self, guideLevel ):
		"""
		根据导师等级创建一个道法
		"""
		type = 0
		quality = g_ZDGuide.getQuality( self.level, guideLevel )	# 先根据导师获得道法的品质
		if not quality:
			return
		if quality != 1:
			type = g_ZDType.getType( quality )						# 根据道法的品质获得道法的类型，白色品质没有类型
		else:
			type = g_daofaData.getQuaWhiteType()
		orderID = self.getDaoXinFreeOrder( csdefine.KB_ZHENG_DAO_ID )
		dict = { "uid" :newUID(), "type":type, "level":1, "exp":0, "quality":quality, "order": orderID, "daoXinID":  csdefine.KB_ZHENG_DAO_ID ,"isLocked": 0, }
		daofa = g_daofa.createObjFromDict( dict )

		self.addDaofa( csdefine.KB_ZHENG_DAO_ID, orderID, daofa )	# 添加道法到证道界面包裹

	def doZhengDao( self, guideLevel ):
		"""
		证道
		"""
		if not self.isDayFirstZD():
			needJiYuan = g_ZDGuide.getCostJYByLevel( self.level, guideLevel )
			self.pay_jiyuan( needJiYuan )				# 消耗机缘
		else:
			self.ZDRecord.incrDegree()					# 免费证道次数增加
			self.client.onZDRecordChanged( self.ZDRecord )
		
		self.createDaofa( guideLevel ) 					# 创建道法
		self.guideActive( guideLevel )					# 激活导师
		self.gain_ZDScore( guideLevel )					# 获得积分

	def uidToDaofa( self, uid ):
		"""
		根绝物品的uid获得物品的实例
		"""
		for daofa in self.daofa:
			if daofa.getUID() == uid:
				return daofa

	def swapDaofa( self, srcDaoxin, dstDaoxin, orderID, uid, isPickup = False ):
		"""
		改变道法的位置
		srcDaoxin：道法所在的原始包裹
		dstDaoxin：道法将要移动到的目标包裹
		orderID: 目标包裹可以放置的位置
		"""
		if dstDaoxin == csdefine.KB_ZHENG_DAO_ID: # 如果目标位置已经存在道法，则返回
			if self.daoXinBags[ dstDaoxin ].daofaList[ orderID ] != 0:
				return
		else:
			if self.isGridHasDaofa( dstDaoxin, orderID ):
				return
		daofa = self.uidToDaofa( uid )
		srcOrder = daofa.getOrder()
		self.addDaofa( dstDaoxin, orderID, daofa )
		self.removeDaofa( srcDaoxin, srcOrder, daofa, isPickup )

	def resortDaofa( self ):
		"""
		对包裹内的道法重新排序
		"""
		for daofa in self.daofa:
			for uid in self.daoXinBags[ csdefine.KB_ZHENG_DAO_ID ].daofaList:
				order = self.daoXinBags[ csdefine.KB_ZHENG_DAO_ID ].daofaList.index( uid )
				if daofa.getUID() == uid and daofa.getOrder() != order:
					daofa.setOrder( order )
					self.client.onDaofaChanged( daofa )

	def autoZhengDaoCheck( self ):
		"""
		一键证道判断，主要判断机缘值和包裹是否已满
		"""
		if self.level < 30:
			return False
		
		# 证道包裹是否已满
		if len( self.daoXinBags[ csdefine.KB_ZHENG_DAO_ID ].daofaList ) >= csdefine.KB_ZD_MAX_SPACE:
			self.statusMessage( csstatus.ZHENG_DAO_STORAGE_IS_FULL )
			return False
		
		# 能否免费证道
		if not self.isDayFirstZD():
			if not self.enoughJiYuan( 1 ):
				self.statusMessage( csstatus.ZHENG_DAO_NOT_ENOUGH_JIYUAN )
				return False
		
		return True

	def clickGuide( self, guideLevel ):
		"""
		Exposed Method
		点击导师按钮
		guideLevel: 导师等级 
		"""
		# 导师未激活
		if  guideLevel not in self.activeGuide:
			ERROR_MSG( "Guide  %i is not active！"  % guideLevel )
			return
		
		# 证道包裹是否已满
		if len( self.daoXinBags[ csdefine.KB_ZHENG_DAO_ID ].daofaList ) >= csdefine.KB_ZD_MAX_SPACE:
			self.statusMessage( csstatus.ZHENG_DAO_STORAGE_IS_FULL )
			return
		
		# 机缘值是否足够
		if not self.isDayFirstZD():
			if not self.enoughJiYuan( guideLevel ):
				self.statusMessage( csstatus.ZHENG_DAO_NOT_ENOUGH_JIYUAN )
				return
		
		self.doZhengDao( guideLevel )

	def sellDaofa( self, uid ):
		"""
		Exposed Method
		点击卖出按钮
		orderID: 道法所在包裹位ID
		"""
		daofa = self.uidToDaofa( uid )
		if daofa:
			jiyuan = daofa.getJiYuan()
			self.add_jiyuan( jiyuan )			# 获得机缘值
			self.removeDaofa( csdefine.KB_ZHENG_DAO_ID, daofa.getOrder(), daofa )	# 移除道法
			self.resortDaofa()		# 对证道包裹中的道法重新排序

	def pickUpDaofa( self, uid ):
		"""
		Exposed Method
		拾取道法
		"""
		daofa = self.uidToDaofa( uid )
		if daofa.getDaoXinID() != csdefine.KB_ZHENG_DAO_ID or daofa.getQuality() == ItemTypeEnum.CQT_WHITE:
			ERROR_MSG( "Can't pick up daofa from this bag %i " % daofa.getDaoXinID() )
			return
		
		orderID = self.getDaoXinFreeOrder( csdefine.KB_COM_DAO_XIN_ID )
		if orderID == -1:	# 找不到空闲的ID
			self.statusMessage( csstatus.ZHENG_DAO_DAO_XIN_IS_FULL )
			return
		
		self.swapDaofa( csdefine.KB_ZHENG_DAO_ID, csdefine.KB_COM_DAO_XIN_ID, orderID, daofa.getUID(), True )
		self.resortDaofa() # 对证道包裹中的道法重新排序

	def autoZhengDao( self ):
		"""
		Exposed Method
		一键证道
		"""
		nonSelectGuidList = []	# 不可选导师列表
		guideList = []			# 导师列表
		
		while( self.autoZhengDaoCheck() ):
			# 选择最高等级的导师
			guideLevel = self.activeGuide[ -1 ]
			if guideLevel in nonSelectGuidList:
				minLevel = min( nonSelectGuidList )
				guideList = sorted( self.activeGuide, reverse = True )
				for level in guideList:
					if level < minLevel:
						guideLevel = level
						break
			
			if not self.isDayFirstZD():
				if not self.enoughJiYuan( guideLevel ) and guideLevel > 1:
					nonSelectGuidList.append( guideLevel )
					continue
			self.doZhengDao( guideLevel )

	def autoPickUp( self ):
		"""
		Exposed Method
		一键拾取，按顺序拾取
		"""
		# 判断道心包裹是否已满
		freeGridList= []
		for index, grid in self.daoXinBags[ csdefine.KB_COM_DAO_XIN_ID ].gridList.iteritems():
			if not grid.hasDaofa() and grid.isActive():
				freeGridList.append( grid.getOrder() )
		if len( freeGridList ) == 0:
			self.statusMessage( csstatus.ZHENG_DAO_DAO_XIN_IS_FULL )
			return
		
		# 拾取道法
		for uid in self.daoXinBags[ csdefine.KB_ZHENG_DAO_ID ].daofaList[ : ]:
			if len( freeGridList ) > 0:	# 道心还有空间
				daofa = self.uidToDaofa( uid )
				if daofa.getQuality() != ItemTypeEnum.CQT_WHITE:
					self.swapDaofa( csdefine.KB_ZHENG_DAO_ID, csdefine.KB_COM_DAO_XIN_ID, freeGridList.pop( 0 ), daofa.getUID(), True )
				continue
			break
		
		self.resortDaofa() # 对证道包裹中的道法重新排序

	def autoCompose( self, daoXinID ):
		"""
		Exposed Method
		一键合成,卖出所有的白色品质的道法,将所有非白色品质的道法，合并至道法队列中第一个品质最高的道法，
		并将合并结果移动至第一个可放置位置
		"""
		supUID, composedList = self.getHighestQuaDaofa( daoXinID )
		self.client.onAutoCompose( daoXinID, supUID )

	def confirmAutoCompose( self, daoxinID ):
		"""
		Exposed Method
		确认一键合成
		"""
		# 卖出所有的白色品质的道法
		if daoxinID == csdefine.KB_ZHENG_DAO_ID:
			self.sellWhiteDaofa()
		
		# 合成道法
		self.autoComposeDaofa( daoxinID )
		self.resortDaofa()

	def getHighestQuaDaofa( self, daoxinID ):
		"""
		获取当前包裹内品质最高的道法
		"""
		supQuality = 2
		order = 0
		composedList = []
		supUID = 0
		# 先选择品质最高的
		if daoxinID == csdefine.KB_ZHENG_DAO_ID: # 证道包裹
			daofaList = self.daoXinBags[ daoxinID ].daofaList[ : ]
		elif daoxinID == csdefine.KB_COM_DAO_XIN_ID:
			daofaList = self.daoXinBags[ daoxinID ].getDaofaList()
		else:
			ERROR_MSG( " DaoXinBag %i can't auto compose daofa" )
			return supUID, composedList
		if len( daofaList ) <= 0:
			return supUID, composedList
		
		for uid in daofaList:
			daofa = self.uidToDaofa( uid )
			if daofa.getQuality() < ItemTypeEnum.CQT_BLUE or daofa.getLockState():
				continue
			if not supUID:
				supUID = uid
			composedList.append( daofa )
			if daofa.getQuality() > supQuality:
				supQuality = daofa.getQuality()
				order = daofaList.index( uid )
				supUID = uid
		
		return supUID, composedList

	def sellWhiteDaofa( self ):
		"""
		卖出证道包裹中所有的白色品质的道法
		"""
		for uid in self.daoXinBags[ csdefine.KB_ZHENG_DAO_ID ].daofaList[ : ]:
			daofa = self.uidToDaofa( uid )
			if daofa.getQuality() == ItemTypeEnum.CQT_WHITE:
				jiyuan = daofa.getJiYuan()
				self.add_jiyuan( jiyuan )			# 获得机缘值
				self.removeDaofa( csdefine.KB_ZHENG_DAO_ID, daofa.getOrder(), daofa )	# 移除道法

	def autoComposeDaofa( self, daoxinID ):
		"""
		一键合成道法
		"""
		exp = 0
		supUID, composedList = self.getHighestQuaDaofa( daoxinID )
		
		supDaofa = self.uidToDaofa( supUID )
		if len( composedList ) <= 0:
			return 
		composedList.remove( supDaofa )
		# 获取剩下的所有道法的经验
		maxLevel = csconst.DAOFA_MAX_LEVEL[ supDaofa.getQuality() ]
		
		for daofa in composedList:
			if supDaofa.getLevel() == maxLevel:
				self.statusMessage( csstatus.ZHENG_DAO_DAOFA_EXP_FULL, supDaofa.getName() )
				break
			# 道法增加经验
			tempExp = daofa.getQualityExp() + daofa.getExp()
			supDaofa.addExp( tempExp )
			exp += tempExp
			# 移除道法
			self.removeDaofa( daoxinID, daofa.getOrder(), daofa )
		
		self.updateDaofa( supDaofa )
		INFO_MSG( "AutComposed Daofa: daoXinID: %i , order %i , qulity %i , type %i " % ( supDaofa.getDaoXinID(), supDaofa.getOrder(), supDaofa.getQuality(),supDaofa.type ) )

	def getActiveGridCost( self, orderID ):
		"""
		Exposed Method
		获取道心中某一个未激活格子的消耗
		"""
		if self.daoXinBags[ csdefine.KB_COM_DAO_XIN_ID ].gridList[ orderID ].isActive():	# 已经激活，返回
			return
		
		costYuanBao = self.getGridCostYB( orderID )
		# 通知客户端需要消耗的元宝，以窗口形式弹出
		self.client.onActiveGridCost( orderID, costYuanBao )

	def getGridCostYB( self, orderID ):
		"""
		获取解锁格子的花费
		"""
		origOrder = DAO_XIN_ORIGINAL_GRID[ csdefine.KB_COM_DAO_XIN_ID ]	# 默认开启格子序号
		activedOrder = self.getActiveOrder( csdefine.KB_COM_DAO_XIN_ID )# 已激活格子序号
		totalNum = orderID - origOrder
		activeNum = activedOrder - origOrder
		costYuanBao = ( totalNum * ( totalNum + 1 ) - activeNum * ( activeNum + 1 ) )   / 2 * 100 
		return costYuanBao

	def confirmActiveGrid( self, orderID ):
		"""
		Exposed Method
		客户端确认开启格子
		"""
		costYuanBao = self.getGridCostYB( orderID )
		# 支付元宝
		if self.payGold( costYuanBao, csdefine.CHANGE_GOLD_ZD_ACTIVE_GRID ):
			self.activeDaoXinGrid( csdefine.KB_COM_DAO_XIN_ID, orderID )
			self.client.grid_activeResult( csdefine.KB_COM_DAO_XIN_ID, orderID, 1 )
		else:
			self.statusMessage( csstatus.ZHENG_DAO_ACTIVE_GRID_FAIL_LACK_GOLD )
			self.client.grid_activeResult( csdefine.KB_COM_DAO_XIN_ID, orderID, 0 )

	def activeDaoXinGrid( self, daoXinID, orderID ):
		"""
		激活格子
		"""
		# 激活格子序号大于或者等于道心最大空间
		if orderID >= self.daoXinBags[ daoXinID].maxSpace:
			return 
		
		# 玩家数据更新
		for grid in self.activeGrid:
			if grid["daoXinID"] == daoXinID:
				grid["actOrder"] = orderID
				break
		
		# 道心包裹更新
		self.daoXinBags[daoXinID].setActiveOrder( orderID )
		for order in self.daoXinBags[daoXinID].gridList.keys():
			if order <= orderID:
				self.daoXinBags[daoXinID].gridList[order].setActive( 1 )
		
		self.client.onActiveGridChanged( self.activeGrid )

	def moveDaofaTo( self, srcUID, dstDaoXinID, dstOrder ):
		"""
		Exposed Method
		道法拖动处理
		"""
		# 如果目标位置未激活则返回
		if self.daoXinBags[ dstDaoXinID ].activeOrder < dstOrder:
			return 
		srcDaofa = self.uidToDaofa( srcUID )
 		srcDaoxinID = srcDaofa.getDaoXinID()
 		srcOrder = srcDaofa.getOrder()
		# 拖动到普通道心
		if dstDaoXinID == csdefine.KB_COM_DAO_XIN_ID:
			if self.isGridHasDaofa( dstDaoXinID, dstOrder ):		# 目标位置有道法
				dstDaofa = self.getDaofaByOrder( dstDaoXinID, dstOrder )
				self.composeDaofa( srcDaofa, dstDaofa )				# 合成道法
			elif srcDaoxinID != dstDaoXinID:						# 从装备道心到普通道心
				self.swapDaofa( srcDaoxinID, dstDaoXinID, dstOrder, srcUID )
			else:
				self.updateDaofa( srcDaofa, dstDaoXinID, dstOrder )	# 同道心内拖动

		# 拖动到装备道心
		elif dstDaoXinID == csdefine.KB_EQUIP_DAO_XIN_ID:
			if self.isGridHasDaofa( dstDaoXinID, dstOrder ):		# 目标位置有道法
				dstDaofa = self.getDaofaByOrder( dstDaoXinID, dstOrder )
				self.composeDaofa( srcDaofa, dstDaofa )				# 合成道法
			else:
				if srcDaoxinID != dstDaoXinID:						# 装备道法
					# 判断玩家身上是否有同类型的道法，有则拖动失败
					for uid in self.daoXinBags[ dstDaoXinID ].getDaofaList():
						eqDaofa = self.uidToDaofa( uid )
						if srcDaofa.getType() == eqDaofa.getType():
							self.statusMessage( csstatus.ZHENG_DAO_NOT_EAUIP_SAME_TYPE_DAOFA )
							return
					self.swapDaofa( srcDaoxinID, dstDaoXinID, dstOrder, srcUID )
				else:
					self.updateDaofa( srcDaofa, dstDaoXinID, dstOrder, True )	# 同装备道心内拖动
		else:
			INFO_MSG( " Some error has occured !")

	def composeDaofa( self, srcDaofa, dstDaofa ):
		"""
		合成道法
		"""
		# 道法合成
		maxLevel = csconst.DAOFA_MAX_LEVEL[ dstDaofa.quality ]
		
		if dstDaofa.getLevel() == maxLevel:
			self.statusMessage( csstatus.ZHENG_DAO_DAOFA_EXP_FULL, dstDaofa.getName() )
			return
		exp = srcDaofa.getQualityExp() + srcDaofa.getExp()
		self.client.onComposeDaofa( srcDaofa.getUID(), dstDaofa.getUID(), exp )

	def confirmComposeDaofa( self, srcUID, dstUID ):
		"""
		Exposed Method
		确认合成道法
		"""
		srcDaofa = self.uidToDaofa( srcUID )
		dstDaofa = self.uidToDaofa( dstUID )
		exp = srcDaofa.getQualityExp() + srcDaofa.getExp()
		dstDaofa.addExp( exp )
		# 更新道法
		self.updateDaofa( dstDaofa )
		# 移除被合成道法
		self.removeDaofa( srcDaofa.getDaoXinID(), srcDaofa.getOrder(), srcDaofa )

	def isGridHasDaofa( self, daoXinID, order ):
		"""
		某个格子是否有道法
		"""
		return self.daoXinBags[ daoXinID ].gridList[ order ].hasDaofa()

	def getDaofaByOrder( self, dxid, order ):
		"""
		根据道法位置获得道法
		"""
		uid = self.daoXinBags[ dxid ].gridList[ order ].getDaofaUID()
		if uid == 0:
			return 0
		daofa = self.uidToDaofa( uid ) 
		return daofa

	def updateDaofa( self, daofa, dxid = 0, order = 0, isInEquipSwap = False ):
		"""
		更新道法数据,如果是改变位置信息则需要传递目标位置的参数
		isInEquipSwap 是否为装备道心内移动
		"""
		newDafa = copy.deepcopy( daofa )
		if dxid != 0: # 同包裹内改变位置才调用updateDaofa
			newDafa.setDaoXinID( dxid )
			newDafa.setOrder( order )
		
		for df in self.daofa:
			if df.getUID() == daofa.getUID():
				self.removeDaofa( df.getDaoXinID(), df.getOrder(), df, False, isInEquipSwap )		# 删除原来道法
				self.addDaofa( newDafa.getDaoXinID(), newDafa.getOrder(), newDafa, isInEquipSwap )	# 添加新道法
				break

	def addEquipeDaofa( self, daofa ):
		"""
		添加已经装备的道法
		"""
		df = copy.deepcopy( daofa )
		self.equipDaofa.append( df )

	def removeEquipDaofa( self, uid ):
		"""
		移除已经卸载的道法
		"""
		for df in self.equipDaofa:
			if df.getUID() == uid:
				self.equipDaofa.remove( df )

	def yuanBaoActiveGuide( self, guideLevel, costYuanBao ):
		"""
		Exposed Method
		元宝召唤导师
		"""
		if guideLevel in self.activeGuide or self.ybActGuideRecord.getDegree() >= YUAN_BAO_ACTIVE_GUIDE_TIMES:
			INFO_MSG( " Guide % is active or ybActive guide times is %i" % ( guideLevel, self.ybActGuideRecord.getDegree() ) )
			return
		
		if self.payGold( costYuanBao, csdefine.CHANGE_GOLD_ZD_ACTIVE_GUIDE ):
			self.activeGuide.append( guideLevel )					# 激活导师
			self.activeGuide = list( set( self.activeGuide ) )
			self.client.onActiveGuideChanged( self.activeGuide )
			
			self.ybActGuideRecord.incrDegree()						# 元宝召唤导师次数增加
			self.client.onYBActGuideChanged( self.ybActGuideRecord )
		else:
			self.statusMessage( csstatus.ZHENG_DAO_ACTIVE_GRID_FAIL_LACK_GOLD )

	def lockDaofa( self, uid ):
		"""
		Exposed Method
		道法锁定
		"""
		daofa = self.uidToDaofa( uid )
		if daofa.getLockState():
			daofa.setLock( 0 )
		else:
			daofa.setLock( 1 )
		self.client.onDaofaChanged( daofa )
		self.client.onLockDaofa( uid )

	# ---------------------------
	# 积分兑换相关
	# ---------------------------
	def request_scoreShopData( self ):
		"""
		Exposed Mehod
		客户端请求可兑换道法数据
		"""
		for df in g_daofaShop.datas:
			daofaData = df.getDataList()
			if len( daofaData ) > 0:
				self.client.receive_scoreShopData( daofaData )

	def scoreExchangeDaofa( self, quality, type ):
		"""
		define method
		积分兑换道法
		"""
		speDaofa = g_daofaShop.getSpecialDaofa( quality, type )
		quality, type, score, level = speDaofa[0], speDaofa[1], speDaofa[2], speDaofa[3]
		if self.ZDScore - score >= 0:
			orderID = self.getDaoXinFreeOrder( csdefine.KB_COM_DAO_XIN_ID )
			if orderID == -1:	# 找不到空闲的ID
				self.statusMessage( csstatus.ZHENG_DAO_DAO_XIN_FULL_CANT_EXCHENG )
				return
			
			exp = self.getDaofaLevelExp( level, quality  )
			dict = { "uid" :newUID(), "type":type, "level":level, "exp":exp, "quality":quality, "order": orderID, "daoXinID":  csdefine.KB_COM_DAO_XIN_ID ,"isLocked": 0, }
			daofa = g_daofa.createObjFromDict( dict )
			self.addDaofa( csdefine.KB_COM_DAO_XIN_ID, orderID, daofa )		# 添加道法到道心界面
			self.pay_ZDScore( score )	# 消耗积分
		else:
			self.statusMessage( csstatus.ZHENG_DAO_NOT_ENOUGH_SCORE )

	def confirmRemoveDaofa( self, uid ):
		"""
		Exposed Mehod
		丢弃道法
		"""
		daofa = self.uidToDaofa( uid )
		if not daofa:
			return 
		self.removeDaofa( daofa.getDaoXinID(), daofa.getOrder(), daofa  )

	def getDaofaLevelExp( self, level, quality ):
		"""
		根据等级获取对应的经验值
		"""
		exp = 0
		for lv in csconst.DAOFA_UPGRADE_EXP.keys():
			if lv < level: 
				exp += csconst.DAOFA_UPGRADE_EXP[ level - 1 ][ quality ]
		return exp

	def dynamicCreateDaofa( self, quality, type, level ):
		"""
		动态创建道法
		"""
		orderID = self.getDaoXinFreeOrder( csdefine.KB_COM_DAO_XIN_ID )
		if orderID == -1:	# 找不到空闲的ID
			self.statusMessage( csstatus.ZHENG_DAO_DAO_XIN_IS_FULL )
			return
		exp = self.getDaofaLevelExp( level, quality  )
		dict = { "uid" :newUID(), "type":type, "level":level, "exp":exp, "quality":quality, "order": orderID, "daoXinID":  csdefine.KB_COM_DAO_XIN_ID ,"isLocked": 0, }
		daofa = g_daofa.createObjFromDict( dict )
		self.addDaofa( csdefine.KB_COM_DAO_XIN_ID, orderID, daofa )			# 添加道法到道心界面
	
	def autoMoveDaofaTo( self, srcUID, dstDaoXinID ):
		"""
		Exposed Method
		自动移动道心到目标道心栏第一个空位
		"""
		srcDaofa = self.uidToDaofa( srcUID )
		if srcDaofa is None:return
 		srcDaoxinID = srcDaofa.getDaoXinID()
 		srcOrder = srcDaofa.getOrder()
		if dstDaoXinID == csdefine.KB_COM_DAO_XIN_ID:			#从道心装备栏卸载道心到普通
			dstOrder = self.getDaoXinFreeOrder( dstDaoXinID )
			if dstOrder == -1:	# 找不到空闲的ID
				self.statusMessage( csstatus.ZHENG_DAO_DAO_XIN_IS_FULL )
				return
			self.swapDaofa( srcDaoxinID, dstDaoXinID, dstOrder, srcUID )
		elif dstDaoXinID == csdefine.KB_EQUIP_DAO_XIN_ID:		#从普通道心栏装备道心到道心装备栏
			# 判断玩家身上是否有同类型的道法，有则装备失败
			dstOrder = self.getDaoXinFreeOrder( dstDaoXinID )
			if dstOrder == -1:	# 找不到空闲的ID
				self.statusMessage( csstatus.ZHENG_DAO_DAO_XIN_IS_FULL )
				return
			for uid in self.daoXinBags[ dstDaoXinID ].getDaofaList():
				eqDaofa = self.uidToDaofa( uid )
				if srcDaofa.getType() == eqDaofa.getType():
					self.statusMessage( csstatus.ZHENG_DAO_NOT_EAUIP_SAME_TYPE_DAOFA )
					return
			self.swapDaofa( srcDaoxinID, dstDaoXinID, dstOrder, srcUID )
		else:
			INFO_MSG( " Some error has occured !")
			
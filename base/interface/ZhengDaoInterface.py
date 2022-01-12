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
	֤��ϵͳ�ӿ�
	"""
	def __init__( self ):
		self.equipDaofa = []
		if not self.ZDRecord.checklastTime():
			self.ZDRecord.reset()
		if not self.ybActGuideRecord.checklastTime():
			self.ybActGuideRecord.reset()

	def onGetCell( self ):
		"""
		���cell�������
		"""
		self.initZDDatas()

	def initZDDatas( self ):
		"""
		��ʼ��֤��ϵͳ����
		"""
		if len( self.activeGuide  ) == 0:	# ��֤��ʦ1�Ǽ����
			self.activeGuide.append( 1 )
		
		if len( self.activeGrid ) == 0:		# ��ʼ�����ĸ���
			levelDiff = 0
			if self.level >= 30:
				levelDiff = ( self.level - 30 ) / 10
			activeEquipOrder = min( levelDiff, csdefine.KB_ZD_MAX_EQUIP_SPACE -1  )
			self.activeGrid = [{ "daoXinID":csdefine.KB_ZHENG_DAO_ID, "actOrder":  csdefine.KB_ZD_MAX_SPACE -1 , },
								{ "daoXinID":csdefine.KB_COM_DAO_XIN_ID, "actOrder":  DAO_XIN_ORIGINAL_GRID[ csdefine.KB_COM_DAO_XIN_ID ], },
								{ "daoXinID":csdefine.KB_EQUIP_DAO_XIN_ID, "actOrder":  activeEquipOrder, },
							]
		self.initStorages()					# ��ʼ��֤������

	def getActiveOrder( self ,daoXinID ):
		"""
		��õ��ĵļ���������
		"""
		if daoXinID == csdefine.KB_ZHENG_DAO_ID:	# ֤������
			return csdefine.KB_ZD_MAX_SPACE -1
		
		for record in self.activeGrid:
			dxid, activeOrder = record[ "daoXinID"], record["actOrder"]
			if dxid == daoXinID:
				return activeOrder

	def initStorages( self ):
		"""
		��ʼ��֤���漰�����а���
		"""
		self.daoXinBags = {	csdefine.KB_ZHENG_DAO_ID: ZhengDaoStorage( self.getActiveOrder( csdefine.KB_ZHENG_DAO_ID ), csdefine.KB_ZD_MAX_SPACE,  csdefine.KB_ZHENG_DAO_ID),
							csdefine.KB_COM_DAO_XIN_ID: DaoXinComStorage( self.getActiveOrder( csdefine.KB_COM_DAO_XIN_ID ), csdefine.KB_ZD_MAX_SPACE, csdefine.KB_COM_DAO_XIN_ID ),
							csdefine.KB_EQUIP_DAO_XIN_ID: DaoXinEquipStorage( self.getActiveOrder( csdefine.KB_EQUIP_DAO_XIN_ID ), csdefine.KB_ZD_MAX_EQUIP_SPACE, csdefine.KB_EQUIP_DAO_XIN_ID ),
							}
		
		illegalList = []		# �Ƿ������б�
		for daofa in self.daofa:
			daoXinID, orderID = daofa.getDaoXinID(), daofa.getOrder()
			if daoXinID == 0 or daofa.getType() not in g_daofaData.getAllTypeByQuality( daofa.getQuality() ):
				illegalList.append( daofa )
				continue
			
			self.daoXinBags[ daoXinID ].addDaofa( self, orderID, daofa.getUID(), True )
		
		for daofa in illegalList: # �Ƴ��Ƿ�����
			self.daofa.remove( daofa )

	def daofa_updateClient( self ):
		"""
		������¿ͻ��˵���
		"""
		self.client.onActiveGuideChanged( self.activeGuide ) # ���͵�ʦ����
		self.client.onActiveGridChanged( self.activeGrid )   # ���͵��ĸ�������
		for daofa in self.daofa:
			self.client.onAddDaofa( daofa )
		self.client.onInitialized( csdefine.ROLE_INIT_DAOFA )

	def zd_onLevelUp( self ):
		"""
		��ɫ�ȼ������仯
		"""
		# ����װ�����ĸ���
		if self.level < 30:
			return 
		
		order = ( self.level - 30 ) / 10
		if order != 0:
			self.activeDaoXinGrid( csdefine.KB_EQUIP_DAO_XIN_ID, order )
			self.client.grid_activeResult( csdefine.KB_EQUIP_DAO_XIN_ID, order, 1 )

	def add_jiyuan( self, jiyuan ):
		"""
		��û�Ե
		"""
		self.jiyuan += jiyuan
		self.client.onJiYuanChanged( self.jiyuan )

	def pay_jiyuan( self, needJiYuan ):
		"""
		���Ļ�Ե
		"""
		assert self.jiyuan >= needJiYuan, " NeedJiYuan %i is bigger than self.jiyuan %i " % ( needJiYuan, self.jiyuan )

		self.jiyuan -= needJiYuan
		self.jiyuan = max( 0, self.jiyuan )
		self.client.onJiYuanChanged( self.jiyuan )

	def set_jiyuan( self, jiyuan ):
		"""
		���û�Եֵ
		"""
		self.jiyuan = jiyuan
		self.client.onJiYuanChanged( self.jiyuan )

	def addDaofa( self, daoxinID, orderID, daofa, isInEquipSwap = False ):
		"""
		��ӵ���
		"""
		daofa.setOrder( orderID )
		daofa.setDaoXinID( daoxinID )
		self.daofa.append( daofa )
		self.daoXinBags[ daoxinID ].addDaofa( self, orderID, daofa.getUID(), isInEquipSwap )
		self.client.onAddDaofa( daofa )
		INFO_MSG( "%s: UID %s, type %i, level %i, exp %i, quality %i ,order %i, daoXinID % i " % ( self.getNameAndID(), daofa.getUID(), daofa.type, daofa.level, daofa.exp, daofa.quality, daofa.order, daofa.daoXinID ) )

	def removeDaofa( self, daoxinID, orderID, daofa, isPickup = False, isInEquipSwap = False ):
		"""
		�Ƴ�����
		"""
		self.daoXinBags[daoxinID].removeDaofa( self, orderID, daofa.getUID(), isInEquipSwap )	# �����Ƴ�����
		for daofaInst in self.daofa:
			if daofaInst.getUID() == daofa.getUID():
				self.daofa.remove( daofaInst )
				break
		self.client.onRemoveDaofa( daofa.getUID(), isPickup )
		INFO_MSG( " %s :UID %s, type %i, level %i, exp %i, quality %i ,order %i, daoXinID % i " % ( self.getNameAndID(), daofa.getUID(), daofa.type, daofa.level, daofa.exp, daofa.quality, daofa.order, daofa.daoXinID ) )

	def cleanAllDaofa( self ):
		"""
		����������еĵ���( ������ )
		"""
		daofaList = copy.deepcopy( self.daofa )
		for daofa in daofaList:
			if daofa.getDaoXinID() == csdefine.KB_EQUIP_DAO_XIN_ID:			# װ�������ϵĵ��������
				continue
			self.removeDaofa( daofa.getDaoXinID(), daofa.getOrder(), daofa )
		INFO_MSG( "Role %s has cleaned all daofa except equiped! Remaining daofa is %s " % ( self.getNameAndID(),  self.daofa ) )

	def guideActive( self, guideLevel ):
		"""
		��ʦ�������Ҫ�󣬵�ʦ1����Զ�����
		"""
		activeRate = g_ZDGuide.getNextGuideActiveRate( guideLevel )
		rate = random.random()
		if rate < activeRate:	# ���Լ�����һ����ʦ
			self.activeGuide.append( guideLevel + 1 )

		if guideLevel != 1:		# һ����������ͻ��Ϊδ����״̬
			self.activeGuide.remove( guideLevel )
		
		self.activeGuide = list( set( self.activeGuide ) ) # ȥ�أ�����
		self.client.onActiveGuideChanged( self.activeGuide )
		INFO_MSG( " %s: All active guide is %s after click guide %i" % ( self.getNameAndID(), self.activeGuide, guideLevel ) )

	def add_ZDScore( self , score ):
		"""
		���֤������
		"""
		self.ZDScore += score
		self.client.onZDScoreChanged( self.ZDScore )

	def pay_ZDScore( self, score ):
		"""
		����֤������
		"""
		self.ZDScore -= score
		self.ZDScore = max( 0, self.ZDScore )
		self.client.onZDScoreChanged( self.ZDScore )

	def gain_ZDScore( self, guideLevel ):
		"""
		��û���
		"""
		guidScore = g_ZDGuide.getScoreByLevel( self.level, guideLevel )
		self.add_ZDScore( guidScore )

	def set_ZDScore( self, score ):
		"""
		���û���
		"""
		self.ZDScore = score
		self.client.onZDScoreChanged( self.ZDScore )

	def isDayFirstZD( self ):
		"""
		�Ƿ�ÿ���һ��֤��
		"""
		if not self.ZDRecord.checklastTime():
			self.ZDRecord.reset()
		if self.ZDRecord.getDegree() >= FREE_ZHENG_DAO_TIMES:
			return False
		return True

	def enoughJiYuan( self, guideLevel ):
		"""
		�ж��Ƿ����㹻�Ļ�Ե
		"""
		needJiYuan = g_ZDGuide.getCostJYByLevel( self.level, guideLevel )
		if not needJiYuan or  self.jiyuan < needJiYuan:
			return False
		return True

	def getDaoXinFreeOrder( self, dxid ):
		"""
		��ð����������İ���λ
		return order
		"""
		if dxid == csdefine.KB_ZHENG_DAO_ID:	# ֤��������������
			if len( self.daoXinBags[ dxid ].daofaList ) < csdefine.KB_ZD_MAX_SPACE:
				return len( self.daoXinBags[ dxid ].daofaList )
		else:	# ���Ľ��洦��
			for index, grid in self.daoXinBags[ dxid ].gridList.iteritems():
				if not grid.hasDaofa() and grid.isActive():
					return grid.getOrder()
		return -1

	def createDaofa( self, guideLevel ):
		"""
		���ݵ�ʦ�ȼ�����һ������
		"""
		type = 0
		quality = g_ZDGuide.getQuality( self.level, guideLevel )	# �ȸ��ݵ�ʦ��õ�����Ʒ��
		if not quality:
			return
		if quality != 1:
			type = g_ZDType.getType( quality )						# ���ݵ�����Ʒ�ʻ�õ��������ͣ���ɫƷ��û������
		else:
			type = g_daofaData.getQuaWhiteType()
		orderID = self.getDaoXinFreeOrder( csdefine.KB_ZHENG_DAO_ID )
		dict = { "uid" :newUID(), "type":type, "level":1, "exp":0, "quality":quality, "order": orderID, "daoXinID":  csdefine.KB_ZHENG_DAO_ID ,"isLocked": 0, }
		daofa = g_daofa.createObjFromDict( dict )

		self.addDaofa( csdefine.KB_ZHENG_DAO_ID, orderID, daofa )	# ��ӵ�����֤���������

	def doZhengDao( self, guideLevel ):
		"""
		֤��
		"""
		if not self.isDayFirstZD():
			needJiYuan = g_ZDGuide.getCostJYByLevel( self.level, guideLevel )
			self.pay_jiyuan( needJiYuan )				# ���Ļ�Ե
		else:
			self.ZDRecord.incrDegree()					# ���֤����������
			self.client.onZDRecordChanged( self.ZDRecord )
		
		self.createDaofa( guideLevel ) 					# ��������
		self.guideActive( guideLevel )					# ���ʦ
		self.gain_ZDScore( guideLevel )					# ��û���

	def uidToDaofa( self, uid ):
		"""
		������Ʒ��uid�����Ʒ��ʵ��
		"""
		for daofa in self.daofa:
			if daofa.getUID() == uid:
				return daofa

	def swapDaofa( self, srcDaoxin, dstDaoxin, orderID, uid, isPickup = False ):
		"""
		�ı������λ��
		srcDaoxin���������ڵ�ԭʼ����
		dstDaoxin��������Ҫ�ƶ�����Ŀ�����
		orderID: Ŀ��������Է��õ�λ��
		"""
		if dstDaoxin == csdefine.KB_ZHENG_DAO_ID: # ���Ŀ��λ���Ѿ����ڵ������򷵻�
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
		�԰����ڵĵ�����������
		"""
		for daofa in self.daofa:
			for uid in self.daoXinBags[ csdefine.KB_ZHENG_DAO_ID ].daofaList:
				order = self.daoXinBags[ csdefine.KB_ZHENG_DAO_ID ].daofaList.index( uid )
				if daofa.getUID() == uid and daofa.getOrder() != order:
					daofa.setOrder( order )
					self.client.onDaofaChanged( daofa )

	def autoZhengDaoCheck( self ):
		"""
		һ��֤���жϣ���Ҫ�жϻ�Եֵ�Ͱ����Ƿ�����
		"""
		if self.level < 30:
			return False
		
		# ֤�������Ƿ�����
		if len( self.daoXinBags[ csdefine.KB_ZHENG_DAO_ID ].daofaList ) >= csdefine.KB_ZD_MAX_SPACE:
			self.statusMessage( csstatus.ZHENG_DAO_STORAGE_IS_FULL )
			return False
		
		# �ܷ����֤��
		if not self.isDayFirstZD():
			if not self.enoughJiYuan( 1 ):
				self.statusMessage( csstatus.ZHENG_DAO_NOT_ENOUGH_JIYUAN )
				return False
		
		return True

	def clickGuide( self, guideLevel ):
		"""
		Exposed Method
		�����ʦ��ť
		guideLevel: ��ʦ�ȼ� 
		"""
		# ��ʦδ����
		if  guideLevel not in self.activeGuide:
			ERROR_MSG( "Guide  %i is not active��"  % guideLevel )
			return
		
		# ֤�������Ƿ�����
		if len( self.daoXinBags[ csdefine.KB_ZHENG_DAO_ID ].daofaList ) >= csdefine.KB_ZD_MAX_SPACE:
			self.statusMessage( csstatus.ZHENG_DAO_STORAGE_IS_FULL )
			return
		
		# ��Եֵ�Ƿ��㹻
		if not self.isDayFirstZD():
			if not self.enoughJiYuan( guideLevel ):
				self.statusMessage( csstatus.ZHENG_DAO_NOT_ENOUGH_JIYUAN )
				return
		
		self.doZhengDao( guideLevel )

	def sellDaofa( self, uid ):
		"""
		Exposed Method
		���������ť
		orderID: �������ڰ���λID
		"""
		daofa = self.uidToDaofa( uid )
		if daofa:
			jiyuan = daofa.getJiYuan()
			self.add_jiyuan( jiyuan )			# ��û�Եֵ
			self.removeDaofa( csdefine.KB_ZHENG_DAO_ID, daofa.getOrder(), daofa )	# �Ƴ�����
			self.resortDaofa()		# ��֤�������еĵ�����������

	def pickUpDaofa( self, uid ):
		"""
		Exposed Method
		ʰȡ����
		"""
		daofa = self.uidToDaofa( uid )
		if daofa.getDaoXinID() != csdefine.KB_ZHENG_DAO_ID or daofa.getQuality() == ItemTypeEnum.CQT_WHITE:
			ERROR_MSG( "Can't pick up daofa from this bag %i " % daofa.getDaoXinID() )
			return
		
		orderID = self.getDaoXinFreeOrder( csdefine.KB_COM_DAO_XIN_ID )
		if orderID == -1:	# �Ҳ������е�ID
			self.statusMessage( csstatus.ZHENG_DAO_DAO_XIN_IS_FULL )
			return
		
		self.swapDaofa( csdefine.KB_ZHENG_DAO_ID, csdefine.KB_COM_DAO_XIN_ID, orderID, daofa.getUID(), True )
		self.resortDaofa() # ��֤�������еĵ�����������

	def autoZhengDao( self ):
		"""
		Exposed Method
		һ��֤��
		"""
		nonSelectGuidList = []	# ����ѡ��ʦ�б�
		guideList = []			# ��ʦ�б�
		
		while( self.autoZhengDaoCheck() ):
			# ѡ����ߵȼ��ĵ�ʦ
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
		һ��ʰȡ����˳��ʰȡ
		"""
		# �жϵ��İ����Ƿ�����
		freeGridList= []
		for index, grid in self.daoXinBags[ csdefine.KB_COM_DAO_XIN_ID ].gridList.iteritems():
			if not grid.hasDaofa() and grid.isActive():
				freeGridList.append( grid.getOrder() )
		if len( freeGridList ) == 0:
			self.statusMessage( csstatus.ZHENG_DAO_DAO_XIN_IS_FULL )
			return
		
		# ʰȡ����
		for uid in self.daoXinBags[ csdefine.KB_ZHENG_DAO_ID ].daofaList[ : ]:
			if len( freeGridList ) > 0:	# ���Ļ��пռ�
				daofa = self.uidToDaofa( uid )
				if daofa.getQuality() != ItemTypeEnum.CQT_WHITE:
					self.swapDaofa( csdefine.KB_ZHENG_DAO_ID, csdefine.KB_COM_DAO_XIN_ID, freeGridList.pop( 0 ), daofa.getUID(), True )
				continue
			break
		
		self.resortDaofa() # ��֤�������еĵ�����������

	def autoCompose( self, daoXinID ):
		"""
		Exposed Method
		һ���ϳ�,�������еİ�ɫƷ�ʵĵ���,�����зǰ�ɫƷ�ʵĵ������ϲ������������е�һ��Ʒ����ߵĵ�����
		�����ϲ�����ƶ�����һ���ɷ���λ��
		"""
		supUID, composedList = self.getHighestQuaDaofa( daoXinID )
		self.client.onAutoCompose( daoXinID, supUID )

	def confirmAutoCompose( self, daoxinID ):
		"""
		Exposed Method
		ȷ��һ���ϳ�
		"""
		# �������еİ�ɫƷ�ʵĵ���
		if daoxinID == csdefine.KB_ZHENG_DAO_ID:
			self.sellWhiteDaofa()
		
		# �ϳɵ���
		self.autoComposeDaofa( daoxinID )
		self.resortDaofa()

	def getHighestQuaDaofa( self, daoxinID ):
		"""
		��ȡ��ǰ������Ʒ����ߵĵ���
		"""
		supQuality = 2
		order = 0
		composedList = []
		supUID = 0
		# ��ѡ��Ʒ����ߵ�
		if daoxinID == csdefine.KB_ZHENG_DAO_ID: # ֤������
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
		����֤�����������еİ�ɫƷ�ʵĵ���
		"""
		for uid in self.daoXinBags[ csdefine.KB_ZHENG_DAO_ID ].daofaList[ : ]:
			daofa = self.uidToDaofa( uid )
			if daofa.getQuality() == ItemTypeEnum.CQT_WHITE:
				jiyuan = daofa.getJiYuan()
				self.add_jiyuan( jiyuan )			# ��û�Եֵ
				self.removeDaofa( csdefine.KB_ZHENG_DAO_ID, daofa.getOrder(), daofa )	# �Ƴ�����

	def autoComposeDaofa( self, daoxinID ):
		"""
		һ���ϳɵ���
		"""
		exp = 0
		supUID, composedList = self.getHighestQuaDaofa( daoxinID )
		
		supDaofa = self.uidToDaofa( supUID )
		if len( composedList ) <= 0:
			return 
		composedList.remove( supDaofa )
		# ��ȡʣ�µ����е����ľ���
		maxLevel = csconst.DAOFA_MAX_LEVEL[ supDaofa.getQuality() ]
		
		for daofa in composedList:
			if supDaofa.getLevel() == maxLevel:
				self.statusMessage( csstatus.ZHENG_DAO_DAOFA_EXP_FULL, supDaofa.getName() )
				break
			# �������Ӿ���
			tempExp = daofa.getQualityExp() + daofa.getExp()
			supDaofa.addExp( tempExp )
			exp += tempExp
			# �Ƴ�����
			self.removeDaofa( daoxinID, daofa.getOrder(), daofa )
		
		self.updateDaofa( supDaofa )
		INFO_MSG( "AutComposed Daofa: daoXinID: %i , order %i , qulity %i , type %i " % ( supDaofa.getDaoXinID(), supDaofa.getOrder(), supDaofa.getQuality(),supDaofa.type ) )

	def getActiveGridCost( self, orderID ):
		"""
		Exposed Method
		��ȡ������ĳһ��δ������ӵ�����
		"""
		if self.daoXinBags[ csdefine.KB_COM_DAO_XIN_ID ].gridList[ orderID ].isActive():	# �Ѿ��������
			return
		
		costYuanBao = self.getGridCostYB( orderID )
		# ֪ͨ�ͻ�����Ҫ���ĵ�Ԫ�����Դ�����ʽ����
		self.client.onActiveGridCost( orderID, costYuanBao )

	def getGridCostYB( self, orderID ):
		"""
		��ȡ�������ӵĻ���
		"""
		origOrder = DAO_XIN_ORIGINAL_GRID[ csdefine.KB_COM_DAO_XIN_ID ]	# Ĭ�Ͽ����������
		activedOrder = self.getActiveOrder( csdefine.KB_COM_DAO_XIN_ID )# �Ѽ���������
		totalNum = orderID - origOrder
		activeNum = activedOrder - origOrder
		costYuanBao = ( totalNum * ( totalNum + 1 ) - activeNum * ( activeNum + 1 ) )   / 2 * 100 
		return costYuanBao

	def confirmActiveGrid( self, orderID ):
		"""
		Exposed Method
		�ͻ���ȷ�Ͽ�������
		"""
		costYuanBao = self.getGridCostYB( orderID )
		# ֧��Ԫ��
		if self.payGold( costYuanBao, csdefine.CHANGE_GOLD_ZD_ACTIVE_GRID ):
			self.activeDaoXinGrid( csdefine.KB_COM_DAO_XIN_ID, orderID )
			self.client.grid_activeResult( csdefine.KB_COM_DAO_XIN_ID, orderID, 1 )
		else:
			self.statusMessage( csstatus.ZHENG_DAO_ACTIVE_GRID_FAIL_LACK_GOLD )
			self.client.grid_activeResult( csdefine.KB_COM_DAO_XIN_ID, orderID, 0 )

	def activeDaoXinGrid( self, daoXinID, orderID ):
		"""
		�������
		"""
		# ���������Ŵ��ڻ��ߵ��ڵ������ռ�
		if orderID >= self.daoXinBags[ daoXinID].maxSpace:
			return 
		
		# ������ݸ���
		for grid in self.activeGrid:
			if grid["daoXinID"] == daoXinID:
				grid["actOrder"] = orderID
				break
		
		# ���İ�������
		self.daoXinBags[daoXinID].setActiveOrder( orderID )
		for order in self.daoXinBags[daoXinID].gridList.keys():
			if order <= orderID:
				self.daoXinBags[daoXinID].gridList[order].setActive( 1 )
		
		self.client.onActiveGridChanged( self.activeGrid )

	def moveDaofaTo( self, srcUID, dstDaoXinID, dstOrder ):
		"""
		Exposed Method
		�����϶�����
		"""
		# ���Ŀ��λ��δ�����򷵻�
		if self.daoXinBags[ dstDaoXinID ].activeOrder < dstOrder:
			return 
		srcDaofa = self.uidToDaofa( srcUID )
 		srcDaoxinID = srcDaofa.getDaoXinID()
 		srcOrder = srcDaofa.getOrder()
		# �϶�����ͨ����
		if dstDaoXinID == csdefine.KB_COM_DAO_XIN_ID:
			if self.isGridHasDaofa( dstDaoXinID, dstOrder ):		# Ŀ��λ���е���
				dstDaofa = self.getDaofaByOrder( dstDaoXinID, dstOrder )
				self.composeDaofa( srcDaofa, dstDaofa )				# �ϳɵ���
			elif srcDaoxinID != dstDaoXinID:						# ��װ�����ĵ���ͨ����
				self.swapDaofa( srcDaoxinID, dstDaoXinID, dstOrder, srcUID )
			else:
				self.updateDaofa( srcDaofa, dstDaoXinID, dstOrder )	# ͬ�������϶�

		# �϶���װ������
		elif dstDaoXinID == csdefine.KB_EQUIP_DAO_XIN_ID:
			if self.isGridHasDaofa( dstDaoXinID, dstOrder ):		# Ŀ��λ���е���
				dstDaofa = self.getDaofaByOrder( dstDaoXinID, dstOrder )
				self.composeDaofa( srcDaofa, dstDaofa )				# �ϳɵ���
			else:
				if srcDaoxinID != dstDaoXinID:						# װ������
					# �ж���������Ƿ���ͬ���͵ĵ����������϶�ʧ��
					for uid in self.daoXinBags[ dstDaoXinID ].getDaofaList():
						eqDaofa = self.uidToDaofa( uid )
						if srcDaofa.getType() == eqDaofa.getType():
							self.statusMessage( csstatus.ZHENG_DAO_NOT_EAUIP_SAME_TYPE_DAOFA )
							return
					self.swapDaofa( srcDaoxinID, dstDaoXinID, dstOrder, srcUID )
				else:
					self.updateDaofa( srcDaofa, dstDaoXinID, dstOrder, True )	# ͬװ���������϶�
		else:
			INFO_MSG( " Some error has occured !")

	def composeDaofa( self, srcDaofa, dstDaofa ):
		"""
		�ϳɵ���
		"""
		# �����ϳ�
		maxLevel = csconst.DAOFA_MAX_LEVEL[ dstDaofa.quality ]
		
		if dstDaofa.getLevel() == maxLevel:
			self.statusMessage( csstatus.ZHENG_DAO_DAOFA_EXP_FULL, dstDaofa.getName() )
			return
		exp = srcDaofa.getQualityExp() + srcDaofa.getExp()
		self.client.onComposeDaofa( srcDaofa.getUID(), dstDaofa.getUID(), exp )

	def confirmComposeDaofa( self, srcUID, dstUID ):
		"""
		Exposed Method
		ȷ�Ϻϳɵ���
		"""
		srcDaofa = self.uidToDaofa( srcUID )
		dstDaofa = self.uidToDaofa( dstUID )
		exp = srcDaofa.getQualityExp() + srcDaofa.getExp()
		dstDaofa.addExp( exp )
		# ���µ���
		self.updateDaofa( dstDaofa )
		# �Ƴ����ϳɵ���
		self.removeDaofa( srcDaofa.getDaoXinID(), srcDaofa.getOrder(), srcDaofa )

	def isGridHasDaofa( self, daoXinID, order ):
		"""
		ĳ�������Ƿ��е���
		"""
		return self.daoXinBags[ daoXinID ].gridList[ order ].hasDaofa()

	def getDaofaByOrder( self, dxid, order ):
		"""
		���ݵ���λ�û�õ���
		"""
		uid = self.daoXinBags[ dxid ].gridList[ order ].getDaofaUID()
		if uid == 0:
			return 0
		daofa = self.uidToDaofa( uid ) 
		return daofa

	def updateDaofa( self, daofa, dxid = 0, order = 0, isInEquipSwap = False ):
		"""
		���µ�������,����Ǹı�λ����Ϣ����Ҫ����Ŀ��λ�õĲ���
		isInEquipSwap �Ƿ�Ϊװ���������ƶ�
		"""
		newDafa = copy.deepcopy( daofa )
		if dxid != 0: # ͬ�����ڸı�λ�òŵ���updateDaofa
			newDafa.setDaoXinID( dxid )
			newDafa.setOrder( order )
		
		for df in self.daofa:
			if df.getUID() == daofa.getUID():
				self.removeDaofa( df.getDaoXinID(), df.getOrder(), df, False, isInEquipSwap )		# ɾ��ԭ������
				self.addDaofa( newDafa.getDaoXinID(), newDafa.getOrder(), newDafa, isInEquipSwap )	# ����µ���
				break

	def addEquipeDaofa( self, daofa ):
		"""
		����Ѿ�װ���ĵ���
		"""
		df = copy.deepcopy( daofa )
		self.equipDaofa.append( df )

	def removeEquipDaofa( self, uid ):
		"""
		�Ƴ��Ѿ�ж�صĵ���
		"""
		for df in self.equipDaofa:
			if df.getUID() == uid:
				self.equipDaofa.remove( df )

	def yuanBaoActiveGuide( self, guideLevel, costYuanBao ):
		"""
		Exposed Method
		Ԫ���ٻ���ʦ
		"""
		if guideLevel in self.activeGuide or self.ybActGuideRecord.getDegree() >= YUAN_BAO_ACTIVE_GUIDE_TIMES:
			INFO_MSG( " Guide % is active or ybActive guide times is %i" % ( guideLevel, self.ybActGuideRecord.getDegree() ) )
			return
		
		if self.payGold( costYuanBao, csdefine.CHANGE_GOLD_ZD_ACTIVE_GUIDE ):
			self.activeGuide.append( guideLevel )					# ���ʦ
			self.activeGuide = list( set( self.activeGuide ) )
			self.client.onActiveGuideChanged( self.activeGuide )
			
			self.ybActGuideRecord.incrDegree()						# Ԫ���ٻ���ʦ��������
			self.client.onYBActGuideChanged( self.ybActGuideRecord )
		else:
			self.statusMessage( csstatus.ZHENG_DAO_ACTIVE_GRID_FAIL_LACK_GOLD )

	def lockDaofa( self, uid ):
		"""
		Exposed Method
		��������
		"""
		daofa = self.uidToDaofa( uid )
		if daofa.getLockState():
			daofa.setLock( 0 )
		else:
			daofa.setLock( 1 )
		self.client.onDaofaChanged( daofa )
		self.client.onLockDaofa( uid )

	# ---------------------------
	# ���ֶһ����
	# ---------------------------
	def request_scoreShopData( self ):
		"""
		Exposed Mehod
		�ͻ�������ɶһ���������
		"""
		for df in g_daofaShop.datas:
			daofaData = df.getDataList()
			if len( daofaData ) > 0:
				self.client.receive_scoreShopData( daofaData )

	def scoreExchangeDaofa( self, quality, type ):
		"""
		define method
		���ֶһ�����
		"""
		speDaofa = g_daofaShop.getSpecialDaofa( quality, type )
		quality, type, score, level = speDaofa[0], speDaofa[1], speDaofa[2], speDaofa[3]
		if self.ZDScore - score >= 0:
			orderID = self.getDaoXinFreeOrder( csdefine.KB_COM_DAO_XIN_ID )
			if orderID == -1:	# �Ҳ������е�ID
				self.statusMessage( csstatus.ZHENG_DAO_DAO_XIN_FULL_CANT_EXCHENG )
				return
			
			exp = self.getDaofaLevelExp( level, quality  )
			dict = { "uid" :newUID(), "type":type, "level":level, "exp":exp, "quality":quality, "order": orderID, "daoXinID":  csdefine.KB_COM_DAO_XIN_ID ,"isLocked": 0, }
			daofa = g_daofa.createObjFromDict( dict )
			self.addDaofa( csdefine.KB_COM_DAO_XIN_ID, orderID, daofa )		# ��ӵ��������Ľ���
			self.pay_ZDScore( score )	# ���Ļ���
		else:
			self.statusMessage( csstatus.ZHENG_DAO_NOT_ENOUGH_SCORE )

	def confirmRemoveDaofa( self, uid ):
		"""
		Exposed Mehod
		��������
		"""
		daofa = self.uidToDaofa( uid )
		if not daofa:
			return 
		self.removeDaofa( daofa.getDaoXinID(), daofa.getOrder(), daofa  )

	def getDaofaLevelExp( self, level, quality ):
		"""
		���ݵȼ���ȡ��Ӧ�ľ���ֵ
		"""
		exp = 0
		for lv in csconst.DAOFA_UPGRADE_EXP.keys():
			if lv < level: 
				exp += csconst.DAOFA_UPGRADE_EXP[ level - 1 ][ quality ]
		return exp

	def dynamicCreateDaofa( self, quality, type, level ):
		"""
		��̬��������
		"""
		orderID = self.getDaoXinFreeOrder( csdefine.KB_COM_DAO_XIN_ID )
		if orderID == -1:	# �Ҳ������е�ID
			self.statusMessage( csstatus.ZHENG_DAO_DAO_XIN_IS_FULL )
			return
		exp = self.getDaofaLevelExp( level, quality  )
		dict = { "uid" :newUID(), "type":type, "level":level, "exp":exp, "quality":quality, "order": orderID, "daoXinID":  csdefine.KB_COM_DAO_XIN_ID ,"isLocked": 0, }
		daofa = g_daofa.createObjFromDict( dict )
		self.addDaofa( csdefine.KB_COM_DAO_XIN_ID, orderID, daofa )			# ��ӵ��������Ľ���
	
	def autoMoveDaofaTo( self, srcUID, dstDaoXinID ):
		"""
		Exposed Method
		�Զ��ƶ����ĵ�Ŀ���������һ����λ
		"""
		srcDaofa = self.uidToDaofa( srcUID )
		if srcDaofa is None:return
 		srcDaoxinID = srcDaofa.getDaoXinID()
 		srcOrder = srcDaofa.getOrder()
		if dstDaoXinID == csdefine.KB_COM_DAO_XIN_ID:			#�ӵ���װ����ж�ص��ĵ���ͨ
			dstOrder = self.getDaoXinFreeOrder( dstDaoXinID )
			if dstOrder == -1:	# �Ҳ������е�ID
				self.statusMessage( csstatus.ZHENG_DAO_DAO_XIN_IS_FULL )
				return
			self.swapDaofa( srcDaoxinID, dstDaoXinID, dstOrder, srcUID )
		elif dstDaoXinID == csdefine.KB_EQUIP_DAO_XIN_ID:		#����ͨ������װ�����ĵ�����װ����
			# �ж���������Ƿ���ͬ���͵ĵ���������װ��ʧ��
			dstOrder = self.getDaoXinFreeOrder( dstDaoXinID )
			if dstOrder == -1:	# �Ҳ������е�ID
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
			
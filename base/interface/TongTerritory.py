# -*- coding: gb18030 -*-
#
# $Id: SpaceFace.py,v 1.10 2007-09-24 07:38:39 kebiao Exp $

"""
��Ὠ���Ľӿ�
"""
import time
import cPickle
import cschannel_msgs
import BigWorld
from bwdebug import *
from MsgLogger import g_logger
import csstatus
import csdefine
import csconst
import random
import Function
import TongBuildingData
tongBuildingDatas = TongBuildingData.instance()
tongBuildingLevel = TongBuildingData.tbl_instance()
from items.ItemDataList import ItemDataList
g_items = ItemDataList.instance()

# ���޸���ʱ��
NAGUAL_REVIVE_TIME						= 60 * 60 * 2

# ������
TASK_KEY_SHENSHOUTYPE_DATA				= 51						# ����������
TASK_KEY_BUILDLEVEL_DATA				= 53						# ������н����ļ�����Ϣ

#----------------------------------------------------------------------------------------------
CONST_PAY_BUILDING_SPEND_MONEY_TIME 	= 60 * 60					# ��⽨��ά���ѵ���ȡʱ����

class TongTerritory:
	"""
	��Ὠ���Ľӿ�
	"""
	def __init__( self ):
		self.territoryMB = None					# ��ظ�����basemailbox
		self._shenshouReviveTimeID = 0

		self.calcBuildingSpendMoney()

		# ����������
		if self.shenshouReviveTime > 0:
			self.addNagualReviveTimer()

		# ��������ظ���
		self.getTongManager().onTongEntityRequestTerritory( self, self.databaseID )

	#---------------------------------------------------------------------------------------------------------
	def onRegisterTerritory( self, territory ):
		"""
		define method.
		@param territory:��ظ�����basemailbox
		"""
		self.territoryMB = territory
		if self.isLockedTerritoryNPC:
			self.territoryMB.lockTerritoryNPC()
			for itemData in self.items:
				self.territoryMB.onRegisterTongItem( itemData[ "itemID" ], itemData[ "amount" ] )

	def onRequestCreateTongTerritory( self, spaceDomain ):
		"""
		define method.
		����ԱҪ�������ظ����� ����������������ָ�����ݴ���һ�����
		"""
		spaceDomain.onCreateTongTerritory( self.databaseID, self.level, self.jk_level, self.ssd_level, self.ck_level, \
											self.tjp_level, self.sd_level, self.yjy_level, self.shenshouType, self.shenshouReviveTime )

	#---------------------------------------------------------------------------------------------------------
	def createSendDataTask( self, memberDBID ):
		"""
		����һ����Ա���첽���ݷ�������
		"""
		# ���첽�������ݳ���Ӱ�Ὠ�����Ϣ������
		self.addSendDataTask( memberDBID, TASK_KEY_SHENSHOUTYPE_DATA, None )
		self.addSendDataTask( memberDBID, TASK_KEY_BUILDLEVEL_DATA, None )

	def onSendClientDelayDatas( self, key, memberBaseMailbox, datas ):
		"""
		�������ݵ��ͻ��� ��Ҫ���첽����һЩ������Ϣ
		@param key				: TASK_KEY_*** �����һЩ�������ؼ���
		@param memberBaseMailbox: ����ҵ�mailbox
		@param datas			:�������ݳ�
		@return type: �ɹ�����һ�����񷵻�True ���򷵻�false
		"""
		if key == TASK_KEY_SHENSHOUTYPE_DATA:
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.client.tong_onSetShenShouType( self.ssd_level, self.shenshouType )
			return True
			return True
		elif key == TASK_KEY_BUILDLEVEL_DATA:
			datas[ "tasks" ].pop( 0 )
			self.updateBuildingLevelToClient( memberBaseMailbox )
			return True
		return False

	#---------------------------------------------------------------------------------------------------------
	def chargeSpendMoney( self ):
		"""
		define method.
		��ά����
		"""
		if self.spendMoney > 0:
			return
		self.onPayBuildingSpendMoney()
		
	def onPayBuildingSpendMoney( self ):
		"""
		��ȡά����
		"""
		tm = time.time()

		# ��ص�ά���� = ���н�����ά����֮��
		payMoney = int( self.buildingSpendMoney )
		
		if payMoney > self.getValidMoney():		# Ҫ���ñ����ʽ���
			for memberDBID, info in self._memberInfos.items():
				self.getMailMgr().send( None,  info.getName(), csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
					cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.TONG_INFO_28, cschannel_msgs.TONG_INFO_29, 0, "" )
			
		if payMoney > self.money:
			self.spendMoney = payMoney - self.money
			if not self.isLockedTerritoryNPC:
				self.isLockedTerritoryNPC = True
				if self.territoryMB:
					self.territoryMB.lockTerritoryNPC()

		self.payMoney( payMoney, False, csdefine.TONG_CHANGE_MONEY_PAYSPENDMONEY )
		DEBUG_MSG( "Tong[%i,%s] PayBuildingSpendMoney: spendMoney=%i, payMoney=%i, time:%i" % ( self.databaseID, self.playerName, self.spendMoney, payMoney, time.time() ) )

		self.statusMessageToOnlineMember( csstatus.TONG_WHF_BU_ZU, Function.switchMoney( payMoney ) )

		self.writeToDB()

	#---------------------------------------------------------------------------------------------------------
	def onMoneyChanged( self ):
		"""
		����Ǯ�ı���
		"""
		if self.spendMoney <= 0 or self.money < self.spendMoney:
			return

		self.giveBuildingSpendMoney()

	#---------------------------------------------------------------------------------------------------------
	def giveBuildingSpendMoney( self ):
		"""
		define method.
		��������ά����
		"""
		DEBUG_MSG( "Tong[%i,%s] spendMoney=%i, tongMoney=%i" % ( self.databaseID, self.playerName, self.spendMoney, self.money ) )
		if self.spendMoney <= 0 or self.money < self.spendMoney:
			return

		spendMoney = self.spendMoney
		self.spendMoney = 0
		self.payMoney( spendMoney, False, csdefine.TONG_CHANGE_MONEY_PAYSPENDMONEY )

		# ��������NPC������ ������
		if self.isLockedTerritoryNPC:
			self.isLockedTerritoryNPC = False
			if self.territoryMB:
				self.territoryMB.unLockTerritoryNPC()

	#---------------------------------------------------------------------------------------------------------
	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if self._shenshouReviveTimeID == timerID:
			self._shenshouReviveTimeID = 0
			self.shenshouReviveTime = 0
			if self.territoryMB:
				self.territoryMB.reviveNagual( 1 )

	#---------------------------------------------------------------------------------------------------------
	def onRequestBuildingSpendMoney( self, playerBase ):
		"""
		define method.
		��������ά���ѷ����ͻ���
		"""
		if self.buildingSpendMoney == 0:
			self.calcBuildingSpendMoney()
		playerBase.client.onGetBuildingSpendMoney( self.buildingSpendMoney )

	def calcBuildingSpendMoney( self ):
		"""
		���㽨����ά����
		"""
		self.buildingSpendMoney = 0	# ������ά����

		for buildingType, buildingLevel in self.newBuildLevelMapping().iteritems():
			if buildingLevel <= 0:
				continue
				
			try:
				self.buildingSpendMoney += tongBuildingDatas[ buildingType ][ buildingLevel ][ "spendMoney" ]
			except:
				EXCEHOOK_MSG(self.databaseID, buildingType, buildingLevel)

	#---------------------------------------------------------------------------------------------------------
	def newBuildLevelMapping( self ):
		"""
		����һ��ʵʱӰ��
		"""
		return {
				csdefine.TONG_BUILDING_TYPE_YSDT 	: self.level,		# ���´���
				csdefine.TONG_BUILDING_TYPE_JK 		: self.jk_level,	# ���
				csdefine.TONG_BUILDING_TYPE_SSD 	: self.ssd_level,	# ���޵�
				csdefine.TONG_BUILDING_TYPE_CK 		: self.ck_level,	# �ֿ�
				csdefine.TONG_BUILDING_TYPE_TJP 	: self.tjp_level,	# ������
				csdefine.TONG_BUILDING_TYPE_SD 		: self.sd_level,	# �̵�
				csdefine.TONG_BUILDING_TYPE_YJY 	: self.yjy_level,	# �о�Ժ
			}

	#---------------------------------------------------------------------------------------------------------
	def updateBuildingLevelToClient( self, memberBaseMailbox ):
		"""
		���°�Ὠ���ļ�����Ϣ��ĳ��Ա�ͻ���
		"""
		for item in self.newBuildLevelMapping().iteritems():
			memberBaseMailbox.client.tong_onReceiveTongBuildInfo( { "type" : item[0], "level" : item[1] } )
	
	def upgradeBuildingLevel( self ):
		"""
		���°�Ὠ���ȼ�
		"""
		for buildingType, level in self.newBuildLevelMapping().items():
			newLevel = tongBuildingLevel.getBuildingLevel( self.level, buildingType )
			if newLevel > level:
				self.onBuildingUpgrade( buildingType, level, newLevel )
		# ֪ͨ������
		if self.territoryMB:
			self.territoryMB.onBuildingLevelChanged(  self.level )

	def onBuildingUpgrade( self, buildingType, oldLevel, newLevel ):
		"""
		����������
		"""
		DEBUG_MSG( "TONG: buildingType,", buildingType, self.newBuildLevelMapping()[buildingType])
		oLevel = oldLevel
		nLevel = newLevel

		if buildingType == csdefine.TONG_BUILDING_TYPE_JK:		# ���
			self.jk_level = nLevel
		elif buildingType == csdefine.TONG_BUILDING_TYPE_SSD:	# ���޵�
			self.onShenshouBuildingUpgrade( nLevel - oLevel )
		elif buildingType == csdefine.TONG_BUILDING_TYPE_CK:	# �ֿ�
			self.ck_level = nLevel
			self.onStorageUpgrade()								# 15:08 2008-12-13,wsf
		elif buildingType == csdefine.TONG_BUILDING_TYPE_TJP:	# ������
			self.tjp_level = nLevel
		elif buildingType == csdefine.TONG_BUILDING_TYPE_SD:	# �̵�,���������������Ʒ
			self.sd_level = nLevel
			INFO_MSG( "TONG: %i reset tong items due to tong updating!" % ( self.databaseID ) )
			self.resetTongItems()
		elif buildingType == csdefine.TONG_BUILDING_TYPE_YJY:	# �о�Ժ
			self.yjy_level = nLevel
			INFO_MSG( "TONG: %i update member tong skills due to tong updating! " % ( self.databaseID ) )
			self.updateRoleTongSkills( )
		try:
			g_logger.tongBuildingChangeLog( self.databaseID, self.getName(), buildingType, oLevel, nLevel )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
			
		# ������µĽ���ά����
		self.calcBuildingSpendMoney()

		# ����Ϣ���µ��ͻ���
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			self.updateBuildingLevelToClient( emb )

		# �����ݸ��µ�������
		self.getTongManager().updateTongBuildingLevel( self.databaseID, self.jk_level, self.ssd_level, self.ck_level, self.tjp_level, self.sd_level, self.yjy_level )

	def updateRoleTongSkills( self ):
		"""
		������Ұ�Ἴ��
		"""
		for memberDBID in self._onlineMemberDBID:
			member = self.getMemberInfos( memberDBID ).getBaseMailbox()
			member.cell.tong_updateTongSkills( self.yjy_level )

	#---------------------------------------------------------------------------------------------------------
	def onSelectShouShou( self, playerBase, userGrade, shenshouType ):
		"""
		define method.
		���ѡ��������
		"""
		#�ж��Ӷ�ս�Ƿ������
		if BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ) and self.tid in BigWorld.globalData[ "TONG_ROB_WAR_START" ]:
			self.statusMessage( playerBase, csstatus.TONG_SELECT_SHENSHOU_REVIVE_INVALID1 )
			return
			
		if self.shenshouType == shenshouType:
			self.statusMessage( playerBase, csstatus.TONG_SELECT_SHENSHOU_TYPE_EXIST )
			return
		elif not self.checkMemberDutyRights( userGrade, csdefine.TONG_RIGHT_PET_SELECT ):
			self.statusMessage( playerBase, csstatus.TONG_SELECT_SHENSHOU_GRADE_INVALID )
			return
		elif self.shenshouReviveTime > 0:
			self.statusMessage( playerBase, csstatus.TONG_SELECT_SHENSHOU_REVIVE_INVALID )
			return

		self.selectShenShou( shenshouType )

	def selectShenShou( self, shenshouType ):
		"""
		ѡ����һֻ����
		"""
		self.territoryMB.onTongSelectNewShenShou( shenshouType, self.shenshouReviveTime > 0 )
		self.shenshouType = shenshouType

		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			emb.client.tong_onSetShenShouType( self.ssd_level, self.shenshouType )

	def onOpenShenShouSelectWindow( self, memberDBID ):
		"""
		define method.
		������֪ͨ������ѡ�����
		csdefine.TONG_SHENSHOU_TYPE_*
		"""
		player = self.getMemberInfos( memberDBID ).getBaseMailbox()
		player.client.tong_openShenShouSelectWindow( self.ssd_level, self.shenshouType )

	def addNagualReviveTimer( self ):
		"""
		define method.
		���ޱ�ɱ�ˣ� �����������
		"""
		addtime = 1
		if self.shenshouReviveTime <= 0:
			self.shenshouReviveTime = time.time() + NAGUAL_REVIVE_TIME
			addtime = NAGUAL_REVIVE_TIME
			if self._shenshouReviveTimeID > 0:
				self.delTimer( self._shenshouReviveTimeID )
		else:
			t = time.time()
			if t < self.shenshouReviveTime:
				addtime = self.shenshouReviveTime - time.time()

		self._shenshouReviveTimeID = self.addTimer( addtime, 0, 0 )

	def onShenshouBuildingUpgrade( self, level ):
		"""
		���޵�������
		"""
		self.ssd_level += level
		# �߻�Ҫ�����޵��֮��Ĭ�������һ������
		if self.ssd_level == 1:
			sstypes = [ csdefine.TONG_SHENSHOU_TYPE_1, csdefine.TONG_SHENSHOU_TYPE_2, \
						csdefine.TONG_SHENSHOU_TYPE_3, csdefine.TONG_SHENSHOU_TYPE_4, ]
			self.selectShenShou( random.choice( sstypes ) )
		else:
			for dbid in self._onlineMemberDBID:
				emb = self.getMemberInfos( dbid ).getBaseMailbox()
				emb.client.tong_onSetShenShouType( self.ssd_level, self.shenshouType )

	#--------------------------------------------�������������֮�佻���Ľӿ�----------------------------------
	def onInitTongItems( self, reset ):
		"""
		��ʼ�������Ʒ
		"""
		if self.territoryMB:
			self.territoryMB.onInitTongItems( self.sd_level, reset )

	def onChapmanRequestItems( self, chapmanBase ):
		"""
		define method.
		������˱������������ȡ�����Ʒ����
		"""
		for itemData in self.items:
			chapmanBase.cell.onRegisterTongItem( itemData[ "itemID" ], itemData[ "amount" ] )
		# ������ҵĹ����¼
		for record in self.weekMemberBuyItemRecord:
			chapmanBase.cell.onGetMemberBuyRecord( record )

	def onRequestOpenTongShop( self, chapmanBase, playerID, talkID ):
		"""
		define method
		�������̵�NPC�Ի�
		"""
		if self.spendMoney > 0:			# Ƿ��
			chapmanBase.cell.onRequestOpenTongShop( playerID, talkID, False )
		else:
			chapmanBase.cell.onRequestOpenTongShop( playerID, talkID, True )
		
	def onSellItems( self, roleDBID, itemID, amount ):
		"""
		define method.
		�����Ʒ�������� [ { "dbID": dbid, "record": [ { "itemID" : itemID, "amount": amount ,},  ] }, ]
		"""
		INFO_MSG( "TONG: %s has sold item %s�� amount %i to %i" % ( self.getNameAndID(), itemID, amount, roleDBID ) )
		for itemData in self.items:
			if itemData[ "itemID" ] == itemID:
				if itemData[ "amount" ] > amount:
					itemData[ "amount" ] -= amount
				else:
					self.items.remove( itemData )
				break
		
		# ����Ա���������޸�
		for item in self.weekMemberBuyItemRecord:
			if item["dbID" ] == roleDBID:
				for record in item[ "record" ]:
					if itemID == record[ "itemID"]:
						record[ "amount" ] += amount
						return
				
				item[ "record" ].append( { "itemID": itemID, "amount": amount} )
				return
		
		buyRecord = {}
		buyRecord[ "dbID" ] = roleDBID
		buyRecord[ "record" ] = []
		buyRecord[ "record" ].append( { "itemID": itemID, "amount": amount} )
		self.weekMemberBuyItemRecord.append( buyRecord )

	#-------------------------------------------------������-------------------------------------------------
	def onRequestFeteSuccessfully( self ):
		"""
		���������ɹ�
		"""
		self.territoryMB.onStartTongFete()

	def onFeteComplete( self ):
		"""
		define method.
		�������ɹ������
		"""
		self.territoryMB.onTongFeteComplete()

	def onOverFete( self ):
		"""
		define method.
		������������  ʱ�䵽��
		"""
		self.territoryMB.onOverTongFete()
	
	# ---------------------------------------------------��������̳�-----------------------------------------------
	def onInitTongSpecialItems( self, reset ):
		"""
		��ʼ�������Ʒ
		"""
		if self.territoryMB:
			self.territoryMB.onInitTongSpecialItems( self.level, reset )

	def onChapmanRequestSpecialItems( self, chapmanBase ):
		"""
		define method.
		������˱������������ȡ�����Ʒ����
		"""
		for itemData in self.specItems:
			chapmanBase.cell.onRegisterTongSpecialItem( itemData[ "itemID" ], itemData[ "amount" ] )
			
	def onRequestOpenTongSpecialShop( self, chapmanBase, playerID, talkID ):
		"""
		define method
		�����������̵�NPC�Ի�
		"""
		if self.spendMoney > 0:			# Ƿ��
			chapmanBase.cell.onRequestOpenTongSpecialShop( playerID, talkID, False )
		else:
			chapmanBase.cell.onRequestOpenTongSpecialShop( playerID, talkID, True )
	
	def onSellSpecialItems( self, playerBase, memberDBID, itemID, amount ):
		"""
		define method.
		���������Ʒ������
		"""
		#Ȩ�޼��
		player = BigWorld.entities.get( playerBase.id, None )
		if player is None:return
		playerGrade = self.getMemberInfos( player.databaseID ).getGrade()
		if not self.checkMemberDutyRights( playerGrade, csdefine.TONG_RIGHT_ASSIGN_ITEM ):
			self.statusMessage( playerBase, csstatus.TONG_ASSIGN_ITEM_FAILURE )
			return
		specItem = self.tong_getSpecialItem( itemID )
		if specItem is None:return
		reqMoney = specItem["reqMoney"]*amount
		if reqMoney > 0 :
			if not self.payMoney( reqMoney, True, csdefine.TONG_CHANGE_MONEY_BUY_SPECIAL_ITEM ):
				ERROR_MSG( "buy TongSpecial pay Money Failed." )
				return
		for itemData in self.specItems:
			if itemData[ "itemID" ] == itemID:
				if itemData[ "amount" ] > amount:
					itemData[ "amount" ] -= amount
				else:
					self.specItems.remove( itemData )
				break
		itemDatas = []
		item = g_items.createDynamicItem( itemID, amount )
		tempDict = item.addToDict()
		del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
		itemData = cPickle.dumps( tempDict, 0 )
		itemDatas.append( itemData )
		memberName = self.getMemberInfos( memberDBID ).getName()
		mailMgr = self.getMailMgr()
		mailMgr.send( None, memberName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_PLAYER, self.chiefName, cschannel_msgs.TONG_SPECIALITEM_REWARD_TITLE,"", 0, itemDatas )
		self.statusMessageToOnlineMember( csstatus.TONG_CHIEF_ASSIGN_ITEM_TO_MEMBER, self.chiefName, item.name(), memberName, memberName )
		INFO_MSG( "TONG: %s has sold specialitem %i�� amount %i to %i" % ( self.getNameAndID(), itemID, amount, memberDBID ) )
		if self.territoryMB:
			self.territoryMB.onSellSpecialItems( playerBase.id, itemID, amount )
		# ����Ϊ���ڷ�����Ʒ����
		for item in self.chiefBuySpecItemForMemberRecord:
			if item["dbID" ] == memberDBID:
				for record in item[ "record" ]:
					if itemID == record[ "itemID"]:
						record[ "amount" ] += amount
						return
				
				item[ "record" ].append( { "itemID": itemID, "amount": amount} )
				return
		
		buyRecord = {}
		buyRecord[ "dbID" ] = memberDBID
		buyRecord[ "record" ] = []
		buyRecord[ "record" ].append( { "itemID": itemID, "amount": amount} )
		self.chiefBuySpecItemForMemberRecord.append( buyRecord )
		
	def buyTongSpecialArrayFromNPC( self, chapmanBase, playerDBID, memberDBID, invoiceIDs, amountList ):
		"""
		define method.
		������������Ʒ
		"""
		moneys = 0
		invoiceList = zip( invoiceIDs, amountList )
		items = []		# ��¼ÿһ����Ʒ
		moneyList = []	# ��¼ÿһ����Ʒ�������۸�
		for invoiceID, amount in invoiceList:
			specItem = self.tong_getSpecialItem( invoiceID )
			if specItem is None:
				ERROR_MSG(  " item %i not in tongsepctiems" %invoiceID )
				return
			if specItem["amount"] < amount:			#��������
				ERROR_MSG( "not more item(id = %i), current amount = %i, sell amount = %i." % ( invoiceID, specItem["amount"], amount ) )
				return
			moneys += specItem["reqMoney"]*amount
		if self.money <  moneys:				#����ʽ𲻹�
			ERROR_MSG( "tong not enogh money" )
			return
		playerMailBox = self.getMemberInfos( playerDBID ).getBaseMailbox()
		playerMailBox.cell.buyTongSpecialArrayFromNPC( chapmanBase, memberDBID, invoiceIDs, amountList )
	
	def tong_getSpecialItem( self, itemID ):
		for itemData in self.specItems:
			if itemData["itemID"] == itemID:
				return itemData
	
	def onAddSpecialItemReward( self, itemID, amount ):
		"""
		�������ע��������Ʒ
		"""
		if self.territoryMB:
			self.territoryMB.onAddSpecialItemReward( itemID, amount )
#
# $Log: not supported by cvs2svn $
#
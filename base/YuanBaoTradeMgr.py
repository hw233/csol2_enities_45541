# -*- coding: gb18030 -*-
#

import BigWorld
import cPickle
import Love3
import csconst
import csdefine
import time
from bwdebug import *
import csstatus
from Function import Functor
import Const
import ShareTexts as ST

"""
元宝交易管理器
"""

class YBTradeDB:
	"""
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		assert YBTradeDB._instance is None		# 不允许有两个以上的实例
		self.createTable()
		YBTradeDB._instance = self
		
	@staticmethod
	def instance():
		"""
		通过 action id 获取action实例
		"""
		if YBTradeDB._instance is None:
			YBTradeDB._instance = YBTradeDB()
		return YBTradeDB._instance

	def createTable( self ):
		"""
		"""
		query = """CREATE TABLE IF NOT EXISTS `custom_ybTradeAccountTable` (
				`id`					BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_roleDBID` 		BIGINT(20),
				`sm_money`	 		BIGINT(20),
				`sm_yuanbao`		BIGINT(20),
				`sm_billcount`			TINYINT(1),
				`sm_playerName` 	TEXT NOT NULL,
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, self.__createTableCB )

		query = """CREATE TABLE IF NOT EXISTS `custom_ybTradeBillTable` (
				`id`					BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_uid`				BIGINT(20),
				`sm_type`			TINYINT(1),
				`sm_roleDBID`		BIGINT(20),
				`sm_rate`			BIGINT(20),
				`sm_deposit`			BIGINT(20),
				`sm_endTime`		BIGINT(20),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, self.__createTableCB )
		
		query = """CREATE TABLE IF NOT EXISTS `custom_ybTradeRecordTable` (
				`id`					BIGINT(20)   UNSIGNED NOT NULL AUTO_INCREMENT,
				`sm_uid`				BIGINT(20),
				`sm_roleDBID`		BIGINT(20),
				`sm_tradeType`		TINYINT(1),
				`sm_tradeState`		TINYINT(1),
				`sm_rate`			BIGINT(20),
				`sm_yb`				BIGINT(20),
				`sm_endTime`		BIGINT(20),
				PRIMARY KEY  ( `id` )
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, self.__createTableCB )

	def clearTable( self ):
		"""
		"""
		query = "delete from custom_ybTradeAccountTable"
		BigWorld.executeRawDatabaseCommand( query, self.__onClearTable )

		query = "delete from custom_ybTradeBillTable"
		BigWorld.executeRawDatabaseCommand( query, self.__onClearTable )
		
		query = "delete from custom_ybTradeRecordTable"
		BigWorld.executeRawDatabaseCommand( query, self.__onClearTable )

	def loadAccounts( self, mgr ):
		"""
		"""
		query = "select * from custom_ybTradeAccountTable"
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onLoadAccounts, mgr ) )

	def loadBills( self, mgr ):
		"""
		"""
		query = "select * from custom_ybTradeBillTable"
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onLoadBills, mgr ) )

	def loadRecords( self, mgr ):
		"""
		"""
		query = "select * from custom_ybTradeRecordTable"
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onLoadRecords, mgr ) )

	def newAccount( self, mgr, roleDBID, money, yuanbao, billcount, playerName ):
		"""
		`sm_roleDBID` 		BIGINT(20),
		`sm_money`	 		BIGINT(20),
		`sm_yuanbao`		BIGINT(20),
		`sm_billcount`			TINYINT(1),
		`sm_playerName` 	TEXT NOT NULL,
		"""
		query = "insert into custom_ybTradeAccountTable set sm_roleDBID = %d, sm_money = %d, sm_yuanbao = %d, sm_billcount = %d, sm_playerName = \'%s\'"%( roleDBID, money, yuanbao, billcount, playerName )
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__newAccountCB, mgr, roleDBID ) )

	def removeAccount( self, mgr, roleDBID ):
		"""
		"""
		query = "delete from custom_ybTradeAccountTable where sm_roleDBID = %d"%roleDBID
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__removeAccountCB, mgr, roleDBID ) )

	def updateAccount( self, mgr, roleDBID, money, yuanbao, billcount, playerMB ):
		"""
		"""
		query = "update custom_ybTradeAccountTable set sm_money = %d,  sm_yuanbao = %d, sm_billcount = %d where sm_roleDBID = %d"%( money, yuanbao, billcount, roleDBID )
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__updateAccountCB, mgr, roleDBID, money, yuanbao, billcount, playerMB ) )

	def newBill( self, mgr, uid, tick, bType, roleDBID, rate, deposit, endTime, playerMB ):
		"""
		`sm_uid`				BIGINT(20),
		`sm_type`			TINYINT(1),
		`sm_roleDBID`		BIGINT(20),
		`sm_rate`			BIGINT(20),
		`sm_deposit`			BIGINT(20),
		`sm_endTime`		BIGINT(20),
		"""
		query = "insert into custom_ybTradeBillTable set sm_uid = %d, sm_type = %d, sm_roleDBID = %d, sm_rate = %d, sm_deposit = %d, sm_endTime = %d"%( uid, bType, roleDBID, rate, deposit, endTime )
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__newBillCB, mgr, uid, tick, bType, roleDBID, rate, deposit, playerMB ) )

	def removeBill( self, mgr, tick, uid, bType, playerMB ):
		"""
		"""
		query = "delete from custom_ybTradeBillTable where sm_uid = %d"%uid
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__removeBillCB, mgr, tick, uid, bType, playerMB ) )
		
	def removeBillByRole( self, mgr, roleDBID ):
		"""
		"""
		query = "delete from custom_ybTradeBillTable where sm_roleDBID = %d"%roleDBID
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__removeBillByRole, mgr, roleDBID ) )

	def removeBillsByTick( self, mgr, tick ):
		"""
		"""
		t_tick = tick - 864000			# 在数据库上保留10天的交易记录，方便运营查询
		query = "delete from custom_ybTradeBillTable where sm_endTime <= %d"%t_tick
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__removeBillsByTick, mgr, tick ) )

	def updateBill( self, mgr, uid, tick, bType, deposit ):
		"""
		"""
		query = "update custom_ybTradeBillTable set sm_deposit = %d where sm_uid = %d"%( deposit, uid )
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__updateBillCB, mgr, uid, tick, bType, deposit ) )

	def newTradeRecord( self, mgr, uid, roleDBID, tType, tState, rate, yuanbao, endTime ):
		"""
		`sm_uid`				BIGINT(20),
		`sm_roleDBID`		BIGINT(20),
		`sm_tradeType`		TINYINT(1),
		`sm_tradeState`		TINYINT(1),
		`sm_rate`			BIGINT(20),
		`sm_yb`				BIGINT(20),
		`sm_endTime`		BIGINT(20),
		"""
		query = "insert into custom_ybTradeRecordTable set sm_uid = %d, sm_roleDBID = %d, sm_tradeType = %d, sm_tradeState = %d, sm_rate = %d, sm_yb = %d, sm_endTime = %d"%( uid, roleDBID, tType, tState, rate, yuanbao, endTime )
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__newTradeRecordCB, mgr, uid, roleDBID, tType, tState, rate, yuanbao, endTime ) )

	def removeTradeRecord( self, mgr, roleDBID ):
		"""
		"""
		query = "delete from custom_ybTradeRecordTable where sm_roleDBID = %d"%roleDBID
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__removeTradeRecordCB, mgr, roleDBID ) )

	def removeTradeRecordsByTick( self, mgr, tick ):
		"""
		"""
		query = "delete from custom_ybTradeRecordTable where sm_endTime <= %d"%tick
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__removeTradeRecordsByTick, mgr, tick ) )

	def __createTableCB( self, result, rows, errstr ):
		"""
		生成数据库表格回调函数

		param tableName:	生成的表格名字
		type tableName:		STRING
		"""
		if errstr:
			ERROR_MSG( "Create yuan bao trade table fault! %s"%errstr  )
			return
			
	def __onClearTable( self, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "clear yuan bao trade table fault! %s"%errstr  )
			return

	def __onLoadAccounts( self, mgr, result, rows, errstr ):
		"""
		"""
		if result is None:
			return
		for i in result:
			DEBUG_MSG( i )
			roleDBID = int(i[1])
			money = int(i[2])
			yuanbao = int(i[3])
			billcount = int(i[4])
			playerName = str(i[5])
			mgr.onLoadAccount( roleDBID, money, yuanbao, billcount, playerName )

	def __onLoadBills( self, mgr,  result, rows, errstr ):
		"""
		"""
		if result is None:
			return
		for i in result:
			DEBUG_MSG( i )
			uid = int(i[1])
			bType = int(i[2])
			roleDBID = int(i[3])
			rate = int(i[4])
			deposit = int(i[5])
			mgr.onLoadBill( uid, bType, roleDBID, rate, deposit )

	def __onLoadRecords( self, mgr,  result, rows, errstr ):
		"""
		"""
		if result is None:
			return
		for i in result:
			DEBUG_MSG( i )
			uid = int(i[1])
			roleDBID = int(i[2])
			tType = int(i[3])
			tState = int(i[4])
			rate = int(i[5])
			yuanbao =int(i[6])
			endTime =  int(i[7])
			mgr.onAddRecord( uid, roleDBID, tType, tState, rate, yuanbao, endTime )

	def __newAccountCB( self, mgr, roleDBID, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "newAccountCB instance fault! %s"%errstr  )
			mgr.onAddAccountFail( roleDBID )
			return
		mgr.onAddAccount( roleDBID )

	def __removeAccountCB( self, mgr, roleDBID, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "removeAccount instance fault! %s"%errstr  )
			return
		mgr.onRemoveAccount( roleDBID )

	def __updateAccountCB( self, mgr, roleDBID, money, yuanbao, billcount, playerMB, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "updateAccount fault! %s"%errstr  )
			return
		mgr.onUpDateAccount( roleDBID, money, yuanbao, billcount, playerMB )
			
	def __newBillCB( self, mgr, uid, tick, bType, roleDBID, rate, deposit, playerMB, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "newAccountCB instance fault! %s"%errstr  )
			mgr.onAddBillFail( uid, tick, bType, roleDBID )
			return
		mgr.onAddBill( uid, tick, bType, roleDBID, rate, deposit, playerMB )

	def __removeBillCB( self, mgr, tick, uid, bType, playerMB, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "removeAccount instance fault! %s"%errstr  )
			return
		mgr.onRemoveBill( tick, uid, bType, playerMB )
		
	def __removeBillByRole( self, mgr, roleDBID, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "removeAccount instance fault! %s"%errstr  )
			return
		mgr.onRemoveBillByRole( roleDBID )

	def __removeBillsByTick( self, mgr, tick, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "removeAccount instance fault! %s"%errstr  )
			return
		mgr.onClearOverDueDatas( 0, tick )

	def __updateBillCB( self, mgr, uid, tick, bType, deposit, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "updateAccount fault! %s"%errstr  )
			return
		mgr.onUpDateBill( uid, tick, bType, deposit )

	def __newTradeRecordCB( self, mgr, uid, roleDBID, tType, tState, rate, yuanbao, endTime, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "newAccountCB instance fault! %s"%errstr  )
			return
		mgr.onAddRecord( uid, roleDBID, tType, tState, rate, yuanbao, endTime )

	def __removeTradeRecordCB( self, mgr, roleDBID, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "removeAccount instance fault! %s"%errstr  )
			return
		mgr.onRemoveRecord( roleDBID )

	def __removeTradeRecordsByTick( self, mgr, tick, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "removeAccount instance fault! %s"%errstr  )
			return
		mgr.onClearOverDueDatas( 1, tick )

class YuanBaoTradeMgr( BigWorld.Base ):
	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# 把自己注册为globalData全局实体
		self.registerGlobally( "YuanBaoTradeMgr", self._onRegisterManager )
		
	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register YuanBaoTradeMgr Fail!" )
			# again
			self.registerGlobally( "YuanBaoTradeMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["YuanBaoTradeMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("YuanBaoTradeMgr Create Complete!")
		self.isStart = True			# 是否初始化状态
		self.buyBills = {}			# 求购列表
		self.sellBills = {}				# 寄售列表
		self.billRecords = {}			# 交易明细表
		self.tradeAccounts = {}		# 元宝交易账户表
		
		self.isBanned = False		# 元宝交易功能开关，供运营用
		
		self.ybtDB = YBTradeDB.instance()
		
		self.clearDatasTimer = 0	# 清除过期日志/订单计时器
		self.clearOverDueDatas()
		
	def ybt_switch( self, trigger ):
		"""
		开闭元宝交易功能
		"""
		self.isBanned = not bool( trigger )
		
	def clearOverDueDatas( self ):
		"""
		批量清除过期订单、交易明细
		"""
		if self.isBanned:		# 如果是运营手动关闭该功能，那么数据则暂不清除
			return
		tick = int( time.time() - time.timezone )/86400 * 86400 + time.timezone
		self.ybtDB.removeTradeRecordsByTick( self, tick )
		tick -= 172800
		self.ybtDB.removeBillsByTick( self, tick )
		
	def onClearOverDueDatas( self, dType, tick ):
		"""
		批量清除回调
		"""
		leftTime = 0
		if self.isStart:
			self.ybtDB.loadAccounts( self )
			self.ybtDB.loadBills( self )
			self.ybtDB.loadRecords( self )
			self.isStart = False
			t = int( time.time() )
			leftTime = int(t/86400) * 86400 + 86400 - t
		else:
			if dType == 0:
				bKey = self.buyBills.keys()
				sKey = self.sellBills.keys()
				billcountlist = {}
				for k in bKey:
					if k <= tick:
						dbs = self.buyBills.pop( k )
						for dropbill in dbs.itervalues():
							roleDBID = dropbill["roleDBID"]
							if not billcountlist.has_key( roleDBID ):		# 更新账号订单计数用
								billcountlist[roleDBID] = 1
							else:
								billcountlist[roleDBID] += 1
				for k in sKey:
					if k <= tick:
						dbs = self.sellBills.pop( k )
						for dropbill in dbs.itervalues():
							roleDBID = dropbill["roleDBID"]
							if not billcountlist.has_key( roleDBID ):		# 更新账号订单计数用
								billcountlist[roleDBID] = 1
							else:
								billcountlist[roleDBID] += 1
				# 更新账号订单计数
				for a in billcountlist:
					account = self.tradeAccounts[a]
					billcount = account["billcount"] - billcountlist[a]
					self.upDateAccount( a, account["money"], account["yb"], billcount )
			else:
				rKey = self.billRecords.keys()
				for k in rKey:
					if k <= tick: self.billRecords.pop( k )
			leftTime = 86400
		INFO_MSG( "clear daily yuan bao trade datas, type %i , tick %i ."%( dType, tick ) )
		if self.clearDatasTimer > 0:
			self.delTimer( self.clearDatasTimer )
		self.clearDatasTimer = self.addTimer( leftTime )
		INFO_MSG( "begin clear yuan bao datas timer, lefttime %i ."%leftTime )
		
	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if timerID == self.clearDatasTimer:
			self.clearOverDueDatas()
	# -----------------------------------------------------------------------------------------------------
	def addAccount( self, roleDBID, money, yuanbao, billcount, playerName ):
		"""
		添加一个账户
		"""
		if self.tradeAccounts.has_key( roleDBID ):
			ERROR_MSG( "add account error, account already exist %i ."%roleDBID )
			return
		self.tradeAccounts[roleDBID] = { 'money': money,  'yb': yuanbao, 'billcount': billcount, 'playerName': playerName }
		self.ybtDB.newAccount( self, roleDBID, money, yuanbao, billcount, playerName )
		
	def removeAccount( self, roleDBID ):
		"""
		移除一个账户
		"""
		self.ybtDB.removeAccount( self, roleDBID )
		
	def upDateAccount( self, roleDBID, money, yuanbao, billcount, playerMB = None ):
		"""
		更新一个账户的数据
		"""
		self.ybtDB.updateAccount( self, roleDBID, money, yuanbao, billcount, playerMB )
		
	def onLoadAccount( self, roleDBID, money, yuanbao, billcount, playerName ):
		"""
		加载元宝交易账户回调
		"""
		self.tradeAccounts[roleDBID] = { 'money': money,  'yb': yuanbao, 'billcount': billcount, 'playerName': playerName }
		INFO_MSG( "load yuan bao trade account successed %i ."%roleDBID )
		
	def onAddAccount( self, roleDBID ):
		"""
		添加一个账户回调
		"""
		INFO_MSG( "add yuan bao trade account %i ."%roleDBID )
		
	def onAddAccountFail( self, roleDBID ):
		"""
		添加一个账户失败回调
		"""
		if self.tradeAccounts.has_key( roleDBID ):
			self.tradeAccounts.pop( roleDBID )
		ERROR_MSG( "add yuan bao trade account fail %i ."%roleDBID )
		
	def onRemoveAccount( self, roleDBID ):
		"""
		移除一个账户回调
		"""
		if self.tradeAccounts.has_key( roleDBID ):
			accout = self.tradeAccounts.pop( roleDBID )
			INFO_MSG( "remove role yuan bao trade account %i, money %i, yuan bao %i ."%( roleDBID, account["money"], account["yb"] ) )
		else:
			INFO_MSG( "remove role yuan bao trade account empty %i"%roleDBID )
		
	def onUpDateAccount( self, roleDBID, money, yuanbao, billcount, playerMB ):
		"""
		更新一个账户的数据回调
		"""
		if playerMB is not None:
			account = self.tradeAccounts[roleDBID]
			old_yb = account["yb"]
			old_money = account["money"]
			if yuanbao == 0 and old_yb != yuanbao:
				playerMB.onDrawYB( old_yb )
			elif money == 0 and old_money != money:
				playerMB.cell.onDrawMoney( old_money )
		account = self.tradeAccounts[roleDBID]
		account['money'] = money
		account['yb'] = yuanbao
		account['billcount'] = billcount
		self.tradeAccounts[roleDBID] = account
		INFO_MSG( "update yuan bao trade account %i ."%roleDBID )
		
		
	# -----------------------------------------------------------------------------------------------------
	def addBill( self, billType, roleDBID, rate, deposit, playerMB ):
		"""
		添加一个订单
		"""
		if self.tradeAccounts.has_key( roleDBID ) and self.tradeAccounts[roleDBID]["billcount"] >= Const.YB_TRADE_BILL_LIMIT:
			ERROR_MSG( "Player %i bill limited."%roleDBID )
			return
		billDict = {
					'roleDBID'	:	roleDBID,
					'state'		:	csdefine.YB_BILL_STATE_FREE,
					'deposit'	:	deposit,
					'rate'		:	rate,
					'traderID'	:	0,
					}
		t = int( time.time() )
		uid = int( time.time()*1000 )
		endTime = int( t/86400 ) * 86400 + 259200		# 86400*3 , 订单能撑三天
		todayTick = int( time.time() - time.timezone )/86400 * 86400 + time.timezone
		if billType == csdefine.YB_BILL_TYPE_BUY:			# 求购元宝
			if not self.buyBills.has_key( todayTick ):
				self.buyBills[todayTick] = {}
			if self.buyBills[todayTick].has_key( uid ):
				ERROR_MSG( "uid already has in buy bills, tick %i ."%tick )
				return
			self.buyBills[todayTick][uid] = billDict
		elif billType == csdefine.YB_BILL_TYPE_SELL:		# 寄售元宝
			if not self.sellBills.has_key( todayTick ):
				self.sellBills[todayTick] = {}
			if self.sellBills[todayTick].has_key( uid ):
				ERROR_MSG( "uid already has in sell bills, tick %i ."%tick )
				return
			self.sellBills[todayTick][uid] = billDict
		self.ybtDB.newBill( self, uid, todayTick, billType, roleDBID, rate, deposit, endTime, playerMB )
		
	def removeBill( self, tick, uid, bType, playerMB ):
		"""
		移除一个订单
		"""
		b = self.buyBills[tick][uid] if bType == csdefine.YB_BILL_TYPE_BUY else self.sellBills[tick][uid]
		state = b["state"]
		if state == csdefine.YB_BILL_STATE_TRADE_LOCK or state == csdefine.YB_BILL_STATE_ON_TRADE:
			if playerMB is not None:
				playerMB.client.onStatusMessage( csstatus.YB_TRADE_BILL_TRADING, "" )
			return
		self.ybtDB.removeBill( self, tick, uid, bType, playerMB )
		
	def removeBillByRole( self, roleDBID ):
		"""
		根据角色来批量移除订单
		"""
		self.ybtDB.removeBillByRole( self, roleDBID )
		
	def upDateBill( self, uid, tick, bType, deposit ):
		"""
		更新一个订单的数据
		"""
		self.ybtDB.updateBill( self, uid, tick, bType, deposit )
		
	def onLoadBill( self, uid, bType, roleDBID, rate, deposit ):
		"""
		加载订单回调
		"""
		preTick = ( int( time.time() - time.timezone )/86400 * 86400 + time.timezone - 172800) * 1000
		if uid <= preTick:
			return
		billDict = {
					'roleDBID'	:	roleDBID,
					'state'		:	csdefine.YB_BILL_STATE_FREE,
					'deposit'	:	deposit,
					'rate'		:	rate,
					'traderID'	:	0,
					'traderDBID':	0,
					}
		tick = int( uid/1000 - time.timezone )/86400 * 86400 + time.timezone
		if bType == csdefine.YB_BILL_TYPE_BUY:			# 求购元宝
			if not self.buyBills.has_key( tick ):
				self.buyBills[tick] = {}
			self.buyBills[tick][uid] = billDict
		elif bType == csdefine.YB_BILL_TYPE_SELL:		# 寄售元宝
			if not self.sellBills.has_key( tick ):
				self.sellBills[tick] = {}
			self.sellBills[tick][uid] = billDict
		
	def onAddBill( self, uid, todayTick, bType, roleDBID, rate, deposit, playerMB ):
		"""
		添加一个订单回调
		"""
		if bType == csdefine.YB_BILL_TYPE_BUY:			# 求购元宝
			INFO_MSG( "add buy bill success uid %i, deposit %i, rate %i ."%( uid, deposit, rate ) )
			cost = rate*deposit
			extra = deposit * int( rate*0.11 )		# 10%手续费+1%保管费
			playerMB.cell.onEstablishBuyBill( cost+extra )
			playerMB.onEstablishBuyBill( rate )
			playerMB.client.onEstablishBuyBill( todayTick, uid, rate, deposit, extra )
		elif bType == csdefine.YB_BILL_TYPE_SELL:		# 寄售元宝
			INFO_MSG( "add sell bill success uid %i, deposit %i, rate %i ."%( uid, deposit, rate ) )
			playerMB.cell.onEstablishSellBill( deposit*rate/100 )		# 1%保管费
			playerMB.onEstablishSellBill( deposit*100, rate )
			playerMB.client.onEstablishSellBill( todayTick, uid, rate, deposit )
		account = self.tradeAccounts[roleDBID]
		self.upDateAccount( roleDBID, account["money"], account["yb"], account["billcount"] + 1 )
			
	def onAddBillFail( self, uid, tick, bType, roleDBID ):
		"""
		增加订单失败回调
		"""
		if bType == csdefine.YB_BILL_TYPE_BUY:			# 求购元宝
			self.buyBills[tick].pop(uid)
		elif bType == csdefine.YB_BILL_TYPE_SELL:		# 寄售元宝
			self.sellBills[tick].pop(uid)
		ERROR_MSG( "add bill fail %i"%roleDBID )
		
	def onRemoveBill( self, tick, uid, bType, playerMB ):
		"""
		移除一个订单回调
		"""
		bill = {}
		if bType == csdefine.YB_BILL_TYPE_BUY:			# 求购元宝
			bill = self.buyBills[tick].pop( uid )
			rate = bill["rate"]
			INFO_MSG( "remove buy bill success uid %i, deposit %i, rate %i ."%( uid, bill["deposit"], rate ) )
			deposit = int( bill["deposit"] * rate )
			if deposit > 0 and playerMB is not None:
				depositMnoney = self.switchToMoney( deposit*1.1 )
				feeMoney = self.switchToMoney( deposit*0.1 )
				playerMB.client.onStatusMessage( csstatus.YB_BUY_NEW_CANCLE, str( depositMnoney + feeMoney ) )
				playerMB.cell.onCancleBill( tick, uid, int(deposit*1.1) )
			if playerMB is None:
				self.addRecord( uid, bill["roleDBID"], csdefine.YB_RECORD_BUY_BILL, csdefine.YB_BILL_STATE_OVER_DUE, rate, deposit )	# 增加交易明细
		elif bType == csdefine.YB_BILL_TYPE_SELL:		# 寄售元宝
			bill = self.sellBills[tick].pop( uid )
			deposit = bill["deposit"]*100
			INFO_MSG( "remove sell bill success uid %i, deposit %i, rate %i ."%( uid, deposit, bill["rate"] ) )
			if deposit > 0 and playerMB is not None:
				playerMB.client.onStatusMessage( csstatus.YB_SELL_NEW_CANCLE, str( ( deposit, ) ) )
				playerMB.onCancleBill( tick, uid, deposit )
			if playerMB is None:
				self.addRecord( uid, bill["roleDBID"], csdefine.YB_RECORD_SELL_BILL, csdefine.YB_BILL_STATE_OVER_DUE, bill["rate"], deposit )	# 增加交易明细
		account = self.tradeAccounts[bill["roleDBID"]]
		self.upDateAccount( bill["roleDBID"], account["money"], account["yb"], account["billcount"] - 1 )
		
	def onRemoveBillByRole( self, roleDBID ):
		"""
		根据角色来批量移除订单回调
		"""
		pass
		
	def onUpDateBill( self, uid, tick, bType, deposit ):
		"""
		更新一个账户的数据回调
		"""
		if bType == csdefine.YB_BILL_TYPE_BUY:			# 求购元宝
			bill = self.buyBills[tick][uid]
			olddesposit = bill["deposit"]
			bill["deposit"] = deposit
			INFO_MSG( "update buy bill success uid %i, deposit %i, olddesposit %i ."%( uid, deposit, olddesposit ) )
			self.onSellYB( uid, tick, bill, deposit, olddesposit )
		elif bType == csdefine.YB_BILL_TYPE_SELL:		# 寄售元宝
			bill = self.sellBills[tick][uid]
			olddesposit = bill["deposit"]
			rate = bill["rate"]
			bill["deposit"] = deposit
			INFO_MSG( "update sell bill success uid %i, deposit %i, olddesposit %i ."%( uid, deposit, olddesposit ) )
			self.onBuyYB( uid, tick, bill, deposit, olddesposit )
			
	# -----------------------------------------------------------------------------------------------------
	def addRecord( self, uid, roleDBID, tType, tState, rate, yuanbao ):
		"""
		添加一个交易明细
		"""
		endTime = int( time.time() - time.timezone )/86400 * 86400 + time.timezone  + 86400
		self.ybtDB.newTradeRecord( self, uid, roleDBID, tType, tState, rate, yuanbao, endTime )
		
	def onAddRecord( self, uid, roleDBID, tType, tState, rate, yuanbao, endTime ):
		"""
		添加一个交易明细回调
		"""
		if endTime < time.time():
			return
		tick = int( uid/1000 - time.timezone )/86400 * 86400 + time.timezone
		if not self.billRecords.has_key( tick ):
			self.billRecords[tick] = {}
		if not self.billRecords[tick].has_key( roleDBID ):
			self.billRecords[tick][roleDBID] = []
		r = [ uid, tType, tState, rate, yuanbao, endTime ]
		self.billRecords[tick][roleDBID].append( r )
		INFO_MSG( "add trade record %s"%str( r ) )
		
	# -----------------------------------------------------------------------------------------------------
	def buyBillLock( self, id, tick, uid, playerDBID, playerMB ):
		"""
		锁定(寄售)订单
		"""
		bill = self.buyBills[tick][uid]
		preState = bill["state"]
		if preState == csdefine.YB_BILL_STATE_FREE:
			bill["state"] = csdefine.YB_BILL_STATE_TRADE_LOCK
			bill["traderID"] = id
			bill["traderDBID"] = playerDBID
			playerMB.billLockRecord( tick, uid, csdefine.YB_BILL_TYPE_SELL )
			
	def buyBillUnLock( self, tick, uid, playerMB ):
		"""
		解锁(寄售)订单
		"""
		bill = self.buyBills[tick][uid]
		bill["state"] = csdefine.YB_BILL_STATE_FREE
		bill["traderID"] = 0
		bill["traderDBID"] = 0
		playerMB.billUnLockRecord()
		
	def sellBillLock( self, id, tick, uid, playerDBID, playerMB ):
		"""
		锁定(求购)订单
		"""
		bill = self.sellBills[tick][uid]
		preState = bill["state"]
		if preState == csdefine.YB_BILL_STATE_FREE:
			bill["state"] = csdefine.YB_BILL_STATE_TRADE_LOCK
			bill["traderID"] = id
			bill["traderDBID"] = playerDBID
			playerMB.billLockRecord( tick, uid, csdefine.YB_BILL_TYPE_BUY )
			
	def sellBillUnLock( self, tick, uid, playerMB ):
		"""
		解锁(求购)订单
		"""
		bill = self.sellBills[tick][uid]
		bill["state"] = csdefine.YB_BILL_STATE_FREE
		bill["traderID"] = 0
		bill["traderDBID"] = 0
		playerMB.billUnLockRecord()
		
	# -----------------------------------------------------------------------------------------------------
	# 购买元宝
	def buyYBRequest( self, tick, uid, playerDBID, playerMB ):
		"""
		define method
		购买元宝请求
		"""
		if self.isBanned:
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BANNED, "" )
			return
		if not self.sellBills.has_key( tick ):
			ERROR_MSG( "tick error %i"%tick )
			return
		if not self.sellBills[tick].has_key( uid ):
			ERROR_MSG( "uid error %i"%uid )
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BILL_MAY_NOT_EXIST, "" )
			return
		bill = self.sellBills[tick][uid]
		if bill["roleDBID"] == playerDBID:
			ERROR_MSG( "you can't buy your own bill %i"%playerDBID )
			return
		preState = bill["state"]
		self.sellBillLock( playerMB.id, tick, uid, playerDBID, playerMB )
		playerMB.client.onBuyYBRequest( tick, uid, preState )
		
	def unBuyYB( self, tick, uid, playerID, playerMB ):
		"""
		defined method
		取消购买元宝
		"""
		if not self.sellBills.has_key( tick ):
			ERROR_MSG( "tick error %i"%tick )
			return
		if not self.sellBills[tick].has_key( uid ):
			ERROR_MSG( "uid error %i"%uid )
			return
		bill = self.sellBills[tick][uid]
		self.sellBillUnLock( tick, uid, playerMB )
		
	def buyYB( self, tick, uid, yuanbao, rate, playerMB ):
		"""
		define method
		购买元宝
		"""
		if self.isBanned:
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BANNED, "" )
			return
		if not self.sellBills.has_key( tick ):
			ERROR_MSG( "tick error %i"%tick )
			return
		if not self.sellBills[tick].has_key( uid ):
			ERROR_MSG( "uid error %i"%uid )
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BILL_MAY_NOT_EXIST, "" )
			return
		bill = self.sellBills[tick][uid]
		if bill["rate"] != rate:
			self.sellBillUnLock( tick, uid, playerMB )
			ERROR_MSG( "sell bill rate error tick %i, uid %i, rate %i ."%( tick, uid, rate ) )
			return
		if bill["traderID"] != playerMB.id:
			ERROR_MSG( "sell bill player error tick %i, uid %i, rate %i ."%( tick, uid, rate ) )
			return
		if bill["state"] == csdefine.YB_BILL_STATE_ON_TRADE:
			ERROR_MSG( "sell bill now is prossing." )
			return
		deposit = bill["deposit"]
		if deposit < yuanbao:
			self.sellBillUnLock( tick, uid, playerMB )
			playerMB.client.onBuyYB( tick, uid, deposit )
			return
		roleDBID = bill["roleDBID"]
		if not self.tradeAccounts.has_key( roleDBID ):
			ERROR_MSG( "Bill owner account error %i ."%roleDBID )
			return
		account = self.tradeAccounts[roleDBID]
		money = account["money"] + ( yuanbao * int( rate ) )
		if money >= csconst.ROLE_MONEY_UPPER_LIMIT:
			playerMB.client.onStatusMessage( csstatus.YB_MONEY_UPPER_LIMIT_CANNT_TRADE, "" )
			return
		self.upDateAccount( roleDBID, money, account["yb"], account["billcount"] )
		deposit -= yuanbao
		bill["playerMB"] = playerMB
		bill["state"] = csdefine.YB_BILL_STATE_ON_TRADE
		self.upDateBill( uid, tick, csdefine.YB_BILL_TYPE_SELL, deposit )
		
	def onBuyYB( self, uid, tick, bill, deposit, olddesposit ):
		"""
		购买元宝回调
		"""
		if not bill.has_key( "playerMB") or bill["playerMB"] is None:
			return
		playerMB = bill.pop("playerMB")
		rate = bill["rate"]
		cost = olddesposit - deposit
		pay_money = int( cost * rate * 1.1 )		# 10%手续费
		playerMB.cell.onBuyYB( pay_money )
		playerMB.onBuyYB( cost*100 )
		playerMB.client.onBuyYB( tick, uid, deposit )
		payMoney = self.switchToMoney( pay_money )
		playerMB.client.onStatusMessage( csstatus.YB_TRADE_BUY_YB_SUCCESS, str( ( cost*100, ) + payMoney ) )
		self.addRecord( uid, bill["traderDBID"], csdefine.YB_RECORD_BUY, deposit == 0, rate, cost )	# 买方增加交易明细
		self.addRecord( uid, bill["roleDBID"], csdefine.YB_RECORD_SELL_BILL, deposit == 0, rate, cost )	# 卖方增加交易明细
		self.sellBillUnLock( tick, uid, playerMB )
		# 给订单拥有者发送消息
		if deposit <= 0: bill["state"] = csdefine.YB_BILL_STATE_SELL_OUT
		roleDBID = bill["roleDBID"]
		playerName = self.tradeAccounts[roleDBID]["playerName"]
		def _onBuyYBCB( player ):
			"""
			查找玩家回调
			"""
			gain_money = cost * rate
			if player == True or player == False:
				content = ST.YBT_ON_SELL_MAIL_MSG%( gain_money )
				playerMB.cell.mail_send_on_air( playerName, csdefine.MAIL_TYPE_QUICK, ST.YBT_ON_TRADE_MAIL_TITLE, content )
			else:
				payMoney = self.switchToMoney( gain_money )
				player.client.onStatusMessage( csstatus.YB_TRADE_SUCCESSFULY_SELL, str( payMoney ) )
		BigWorld.lookUpBaseByDBID( "Role", roleDBID,  _onBuyYBCB )
		if deposit <= 0:
			self.removeBill( tick, uid, csdefine.YB_BILL_TYPE_SELL, None )
				
	# -----------------------------------------------------------------------------------------------------
	# 出售元宝
	def sellYBRequest( self, tick, uid, playerDBID, playerMB ):
		"""
		define method
		出售元宝请求
		"""
		if self.isBanned:
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BANNED, "" )
			return
		if not self.buyBills.has_key( tick ):
			ERROR_MSG( "tick error %i"%tick )
			return
		if not self.buyBills[tick].has_key( uid ):
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BILL_MAY_NOT_EXIST, "" )
			ERROR_MSG( "uid error %i"%uid )
			return
		bill = self.buyBills[tick][uid]
		if bill["roleDBID"] == playerDBID:
			ERROR_MSG( "you can't buy your own bill %i"%playerDBID )
			return
		preState = bill["state"]
		self.buyBillLock( playerMB.id, tick, uid, playerDBID, playerMB )
		playerMB.client.onSellYBRequest( tick, uid, preState )
		
	def unSellYB( self, tick, uid, playerID, playerMB ):
		"""
		defined method
		取消出售元宝
		"""
		if not self.buyBills.has_key( tick ):
			ERROR_MSG( "tick error %i"%tick )
			return
		if not self.buyBills[tick].has_key( uid ):
			ERROR_MSG( "uid error %i"%uid )
			return
		bill = self.buyBills[tick][uid]
		self.buyBillUnLock( tick, uid, playerMB )
		
	def sellYB( self, tick, uid, yuanbao, rate, playerMB ):
		"""
		define method
		出售元宝
		"""
		if self.isBanned:
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BANNED, "" )
			return
		if not self.buyBills.has_key( tick ):
			ERROR_MSG( "tick error %i"%tick )
			return
		if not self.buyBills[tick].has_key( uid ):
			ERROR_MSG( "uid error %i"%uid )
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BILL_MAY_NOT_EXIST, "" )
			return
		bill = self.buyBills[tick][uid]
		if bill["rate"] != rate:
			self.buyBillUnLock( tick, uid, playerMB )
			ERROR_MSG( "buy bill rate error tick %i, uid %i, rate %i ."%( tick, uid, rate ) )
			return
		if bill["traderID"] != playerMB.id:
			ERROR_MSG( "buy bill player error tick %i, uid %i, rate %i ."%( tick, uid, rate ) )
			return
		if bill["state"] == csdefine.YB_BILL_STATE_ON_TRADE:
			ERROR_MSG( "buy bill is processing." )
			return
		deposit = bill["deposit"]
#		money = yuanbao * rate
		if deposit < yuanbao:
			self.buyBillUnLock( tick, uid, playerMB )
			playerMB.client.onSellYB( tick, uid, deposit )
			return
		roleDBID = bill["roleDBID"]
		if not self.tradeAccounts.has_key( roleDBID ):
			ERROR_MSG( "Bill owner account error %i ."%roleDBID )
			return
		account = self.tradeAccounts[roleDBID]
		yb = account["yb"] +  yuanbao*100
		if yb >= csconst.ROLE_GOLD_UPPER_LIMIT:
			playerMB.client.onStatusMessage( csstatus.YB_GOLD_UPPER_LIMIT_CANNT_TRADE, "" )
			return
		self.upDateAccount( roleDBID, account["money"], yb, account["billcount"] )
		deposit -= yuanbao
		bill["playerMB"] = playerMB
		bill["state"] = csdefine.YB_BILL_STATE_ON_TRADE
		self.upDateBill( uid, tick, csdefine.YB_BILL_TYPE_BUY, deposit )
		
	def onSellYB( self, uid, tick, bill, deposit, olddesposit ):
		"""
		出售元宝回调
		"""
		if not bill.has_key( "playerMB") or bill["playerMB"] is None:
			return
		playerMB = bill.pop("playerMB")
		rate = bill["rate"]
		cost = olddesposit - deposit
		income = cost*100
		playerMB.onSellYB( income )
		playerMB.cell.onSellYB( cost*rate )
		playerMB.client.onSellYB( tick, uid, deposit )
		gain = self.switchToMoney( cost*rate )
		playerMB.client.onStatusMessage( csstatus.YB_TRADE_SELL_YB_SUCCESS, str( ( income, ) + gain ) )
		self.addRecord( uid, bill["traderDBID"], csdefine.YB_RECORD_SELL, deposit == 0, rate, cost )	# 卖方增加交易明细
		self.addRecord( uid, bill["roleDBID"], csdefine.YB_RECORD_BUY_BILL, deposit == 0, rate, cost )	# 买方增加交易明细
		self.buyBillUnLock( tick, uid, playerMB )
		# 给订单拥有者发送消息
		if deposit <= 0: bill["state"] = csdefine.YB_BILL_STATE_SELL_OUT
		roleDBID = bill["roleDBID"]
		playerName = self.tradeAccounts[roleDBID]["playerName"]
		def _onSellYBCB( player ):
			"""
			查找玩家回调
			"""
			if player == True or player == False:
				content = ST.YBT_ON_BUY_MAIL_MSG%income
				playerMB.cell.mail_send_on_air( playerName, csdefine.MAIL_TYPE_QUICK, ST.YBT_ON_TRADE_MAIL_TITLE, content )
			else:
				totalMoney = self.switchToMoney( int( cost*rate*1.11 ) )
				feeMoney = self.switchToMoney( int( cost*rate*0.11 ) )
				player.client.onStatusMessage( csstatus.YB_TRADE_SUCCESSFULY_BUY, str( ( income, ) + totalMoney + feeMoney ) )
		BigWorld.lookUpBaseByDBID( "Role", roleDBID, _onSellYBCB )
		if deposit <= 0:
			self.removeBill( tick, uid, csdefine.YB_BILL_TYPE_BUY, None )
			
	# -----------------------------------------------------------------------------------------------------
	# 求购订单
	def establishBuyBillRequest( self, roleDBID, playerName, playerMB ):
		"""
		define method
		请求建立求购元宝订单
		"""
		if self.isBanned:
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BANNED, "" )
			return
		result = 0
		if self.tradeAccounts.has_key( roleDBID ):
			account = self.tradeAccounts[roleDBID]
			billcount = account["billcount"]
			if billcount >= Const.YB_TRADE_BILL_LIMIT:
				result = 1
		else:
			result = 2
			self.addAccount( roleDBID, 0, 0, 0, playerName )
		playerMB.client.onEstablishBuyBillRequest( result )
		
	def establishBuyBill( self, yuanbao, rate, roleDBID, playerMB ):
		"""
		define method
		建立求购元宝订单
		"""
		if self.isBanned:
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BANNED, "" )
			return
		deposit = yuanbao
		self.addBill( csdefine.YB_BILL_TYPE_BUY, roleDBID, rate, deposit, playerMB )
		
	# -----------------------------------------------------------------------------------------------------
	# 寄售订单
	def establishSellBillRequest( self, roleDBID, playerName, playerMB ):
		"""
		define method
		请求建立寄售元宝订单
		"""
		if self.isBanned:
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BANNED, "" )
			return
		result = 0
		if self.tradeAccounts.has_key( roleDBID ):
			account = self.tradeAccounts[roleDBID]
			billcount = account["billcount"]
			if billcount >= Const.YB_TRADE_BILL_LIMIT:
				result = 1
		else:
			result = 2
			self.addAccount( roleDBID, 0, 0, 0, playerName )
		playerMB.client.onEstablishSellBillRequest( result )
		
	def establishSellBill( self, yuanbao, rate, roleDBID, playerMB ):
		"""
		define method
		建立寄售元宝订单
		"""
		if self.isBanned:
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BANNED, "" )
			return
		self.addBill( csdefine.YB_BILL_TYPE_SELL, roleDBID, rate, yuanbao, playerMB )
		
	# -----------------------------------------------------------------------------------------------------
	# 撤销订单
	def cancleBillRequest( self, tick, uid, bType, playerMB ):
		"""
		define method
		请求撤销订单
		"""
		if self.isBanned:
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BANNED, "" )
			return
		result = csdefine.YB_BILL_STATE_FREE
		if bType == csdefine.YB_BILL_TYPE_BUY:			# 求购元宝
			if not self.buyBills.has_key( tick ):
				ERROR_MSG( "cancle buy bill not found tick %i"%tick )
				return
			if not self.buyBills[tick].has_key( uid ):
				ERROR_MSG( "cancle buy bill not found uid %i"%uid )
				return
			result = self.buyBills[tick][uid]["state"]
		elif bType == csdefine.YB_BILL_TYPE_SELL:		# 寄售元宝
			if not self.sellBills.has_key( tick ):
				ERROR_MSG( "cancle sell bill not found tick %i"%tick )
				return
			if not self.sellBills[tick].has_key( uid ):
				ERROR_MSG( "cancle sell bill not found uid %i"%uid )
				return
			result = self.sellBills[tick][uid]["state"]
		playerMB.client.onCancleBillRequest( tick, uid, bType, result )
		
	def cancleBill( self, tick, uid, bType, playerMB ):
		"""
		define method
		撤销订单
		"""
		if self.isBanned:
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BANNED, "" )
			return
		if bType == csdefine.YB_BILL_TYPE_BUY:			# 求购元宝
			bb = self.buyBills
			if not bb.has_key( tick ):
				ERROR_MSG( "cancle buy bill not found tick %i"%tick )
				return
			if not bb[tick].has_key( uid ):
				ERROR_MSG( "cancle buy bill not found uid %i"%uid )
				return
		elif bType == csdefine.YB_BILL_TYPE_SELL:		# 寄售元宝
			sb = self.sellBills
			if not sb.has_key( tick ):
				ERROR_MSG( "cancle sell bill not found tick %i"%tick )
				return
			if not sb[tick].has_key( uid ):
				ERROR_MSG( "cancle sell bill not found uid %i"%uid )
				return
		self.removeBill( tick, uid, bType, playerMB )
		
	# -----------------------------------------------------------------------------------------------------
	# 取出元宝
	def drawYB( self, roleDBID, playerMB ):
		"""
		define method
		取出元宝
		"""
		if self.isBanned:
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BANNED, "" )
			return
		if not self.tradeAccounts.has_key( roleDBID ):
			ERROR_MSG( "Draw yuan bao error, can not found account %i ."%roleDBID )
			return
		account = self.tradeAccounts[roleDBID]
		self.upDateAccount( roleDBID, account["money"], 0, account["billcount"], playerMB )
		
	# -----------------------------------------------------------------------------------------------------
	# 取出金钱
	def drawMoney( self, roleDBID, playerMB ):
		"""
		define method
		取出金钱
		"""
		if self.isBanned:
			playerMB.client.onStatusMessage( csstatus.YB_TRADE_BANNED, "" )
			return
		if not self.tradeAccounts.has_key( roleDBID ):
			ERROR_MSG( "Draw yuan bao error, can not found account %i ."%roleDBID )
			return
		account = self.tradeAccounts[roleDBID]
		self.upDateAccount( roleDBID, 0, account["yb"], account["billcount"], playerMB )
		
	# -----------------------------------------------------------------------------------------------------
	# 请求信息
	def getBuyBillsInfo( self, page, number, playerDBID, playerMB ):
		"""
		define method
		向服务器请求获取购买元宝订单信息
		"""
		if self.isBanned:
			return
		sendDatas = []
		startPos = ( page - 1 ) * number - 1
		index = 0
		num = 0
		for tick, bills in self.buyBills.iteritems():
			if num >= number:
				break
			for uid, billInfo in bills.iteritems():
				if index < startPos:
					index += 1
					continue
				if billInfo["roleDBID"] == playerDBID or billInfo["deposit"] <= 0:
					index += 1
					continue
				sd = [ tick, uid, billInfo["roleDBID"], billInfo["deposit"], billInfo["rate"] ]
				sendDatas.append( sd )
				num += 1
		if len( sendDatas ) <= 0:
			return
		sd = cPickle.dumps( sendDatas, 2 )
		playerMB.client.onGetBuyBillInfo( sd )
		
	def getSellBillsInfo( self, page, number, playerDBID, playerMB ):
		"""
		define method
		向服务器请求获取出售元宝订单信息
		"""
		if self.isBanned:
			return
		sendDatas = []
		startPos = ( page - 1 ) * number - 1
		index = 0
		num = 0
		for tick, bills in self.sellBills.iteritems():
			if num >= number:
				break
			for uid, billInfo in bills.iteritems():
				if index < startPos:
					index += 1
					continue
				if billInfo["roleDBID"] == playerDBID or billInfo["deposit"] <= 0:
					index += 1
					continue
				sd = [ tick, uid, billInfo["roleDBID"], billInfo["deposit"], billInfo["rate"] ]
				sendDatas.append( sd )
				num += 1
		if len( sendDatas ) <= 0:
			return
		sd = cPickle.dumps( sendDatas, 2 )
		playerMB.client.onGetSellBillsInfo( sd )
		
	def getMyBillsInfo( self, playerDBID, playerMB ):
		"""
		define methos
		向服务器请求自己的订单的明细
		"""
		if self.isBanned:
			return
		sendDatas = []
		for t in self.billRecords.itervalues():
			if not playerDBID in t:
				continue
			sendDatas.extend(t[playerDBID])

		if len(sendDatas) > 0:
			sd = cPickle.dumps( sendDatas, 2 )
			playerMB.client.onGetMyBillsInfo( sd )
			
	def getAllMyBills( self, playerDBID, playerMB ):
		"""
		define methos
		向服务器请求自己的订单
		"""
		if self.isBanned:
			return
		sendDatas = []
		for tick, bills in self.sellBills.iteritems():
			for uid, billInfo in bills.iteritems():
				if billInfo["roleDBID"] == playerDBID:
					sendDatas.append( {tick:{uid:billInfo,0:csdefine.YB_BILL_TYPE_SELL}} )
					
		for tick, bills in self.buyBills.iteritems():
			for uid, billInfo in bills.iteritems():
				if billInfo["roleDBID"] == playerDBID:
					sendDatas.append( {tick:{uid:billInfo,0:csdefine.YB_BILL_TYPE_BUY}} )
					
		if len(sendDatas) > 0:
			sd = cPickle.dumps( sendDatas, 2 )
			playerMB.client.onGetAllMyBills( sd )
		
	def getBalanceMoney( self, playerDBID, playerMB ):
		"""
		Exposed
		向服务器请求自己的账号金钱余额
		"""
		if self.isBanned:
			return
		money = 0
		if self.tradeAccounts.has_key( playerDBID ):
			money = self.tradeAccounts[playerDBID]["money"]
		playerMB.client.onGetBalanceMoney( money )
		
	def getBalanceYB( self, playerDBID, playerMB ):
		"""
		Exposed
		向服务器请求自己的账号元宝余额
		"""
		if self.isBanned:
			return
		yuanbao = 0
		if self.tradeAccounts.has_key( playerDBID ):
			yuanbao = self.tradeAccounts[playerDBID]["yb"]
		playerMB.client.onGetBalanceYB( yuanbao )
	
	def switchToMoney( self, money ):
		"""
		铜币转换为金银铜
		"""
		gold = money/10000
		silver = money%10000/100
		coin = money%100
		return ( gold, silver, coin )
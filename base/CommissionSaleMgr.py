# -*- coding: gb18030 -*-
#

import BigWorld
import cPickle
import ItemTypeEnum
import items
import time
import csstatus
from bwdebug import *
from Function import Functor

"""
物品列表的顺序(类型）： 与数据库中的sm_type对应, see also ItemTypeEnum.py/CIST_*
"""

"""
表格名字： custom_SaleOnCommission
数据库中寄卖物品的存储格式：

注： index 是建表时设置的自动增量（4字节长度）。对于新增加的物品,这个值是在数据
库中自动生成的。

type 和 flag 主要是用于快速查询

数据库中寄卖物品的状态有4种：
	0：允许买入（允许取消寄卖），玩家查询数据库的时候只能查到这个状态下的物品数据
	1：物品卖出,没有通知卖家
	2：成功买卖的物品
	3: 成功取消寄卖的物品
"""

MAXLENGTH = 20			# 一次查询物品数目的长度
QUERY_LIMIT_TIME = 10	# 玩家查询行为的限制时间,单位为s
COMMISSION_FAILURE_TIME = 60	# 玩家买一个物品时效，超过此时间说明玩家买物品失败
QUERY_CLEAR_TIME = 60	# queryData中的数据的保存时效
RUN_TIMER = 120			# 临时数据的清理周期

g_item = items.instance()

class CommissionSaleMgr( BigWorld.Base ):
	"""
	寄卖管理器
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Base.__init__( self )

		# 把自己注册为globalData全局实体
		self.registerGlobally( "CommissionSaleMgr", self._onRegisterManager )

		# 在数据库中创建寄卖物品表custom_SaleOnCommission
		self._createCommissionTable()

		self.mutexDict = {}	# 实现玩家对寄卖物品进行操作时的互斥

		self.queryData = {}	# 玩家查询的临时数据保存{ "index":[owner,price,item,itemName,queryTime],… }
		self.queryTime = {}	# 用来限制玩家的查询频率{ "playerName":queryTime, …}

		self.addTimer( RUN_TIMER, RUN_TIMER )


	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register CommissionSaleMgr Fail!" )
			# again
			self.registerGlobally( "CommissionSaleMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["CommissionSaleMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("CommissionSaleMgr Create Complete!")


	def _createCommissionTable( self ):
		"""
		生成表格，如果custom_SaleOnCommission表格不存在，则创建它，此表只创建一次。

		表格字段如下：
		id : 		自动增量, 物品在数据库中的序列
		sm_owner : 	寄卖者的名字
		sm_price :	寄卖物品的价格
		sm_type  :	寄卖物品的类型
		sm_flag :	寄卖物品的类型辅助
		sm_item	:	一个物品的数据
		sm_itemName:	物品名字，其实通过sm_item可以查询到物品的名字，这里的作用主要是为了方便搜索
		sm_purchaser：	买者名字，寄卖的时候，这一项是空的，只有物品被买走才把玩家名字当成数据写入
		sm_commissionTime:	物品寄卖时间
		sm_endTradeTime:	物品交易完成时间(被卖出或取消寄卖)
		sm_state:	寄卖物品状态
		数据库中寄卖物品的状态有4种：
			0：允许买入（允许取消寄卖），玩家查询数据库的时候只能查到这个状态下的物品数据
			1：物品卖出,没有通知卖家
			2：成功买卖的物品
			3: 成功取消寄卖的物品
		"""
		query  = "CREATE TABLE  IF NOT EXISTS `custom_SaleOnCommission` (`id` int(11) NOT NULL auto_increment, `sm_owner` varchar(45) default \" \", `sm_price` int(11) default 0, `sm_type` int(11) default 0,`sm_occupation` int(11) default 0,`sm_wieldType` int(11) default 0,`sm_item` blob default NULL,`sm_itemName` varchar(45) default \" \",`sm_purchaser` varchar(45) default \" \",`sm_commissionTime` datetime default NULL, `sm_endTradeTime` datetime default NULL, `sm_state` int(11) default 0,PRIMARY KEY  (`id`)) ENGINE=InnoDB;"
		BigWorld.executeRawDatabaseCommand( query, self._createCommissionTableCB )


	def _createCommissionTableCB( self, result, rows, errstr ):
		"""
		生成表格回调函数
		"""
		if errstr:
			# 生成表格错误的处理
			ERROR_MSG( "Create custom_Saleoncommission Fail!" )
			return


	def saleGoods( self, sellerName, price, item ):
		"""
		Define method.
		寄卖一个物品。玩家寄卖一个物品时调用此接口

		@param sellerName:	寄卖者的名字
		@type sellerName:	STRING
		@param price:	寄卖价格
		@type price:	UINT32
		@param item:	物品
		@type item:		ITEM

		过程：	1.加入寄卖的时间信息，对物品数据进行转化
				2.把物品信息写入寄卖系统
		"""
		# itemType:物品的类型;occupation:武器的职业适性;wieldType:武器的双手适性.
		itemType = item.getType()

		if itemType > 0 and itemType < 13:		# 1-12是武器
			occupation = item.query( "reqClasses" )
			wieldType = item.query( "eq_wieldType" )
		else:
			occupation = 0
			wieldType = 0

		itemName = item.query( "name" )

		tempDict = item.addToDict()
		del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
		itemData = cPickle.dumps( tempDict, 2 )

		query = "insert into custom_SaleOnCommission ( sm_owner, sm_price, sm_type, sm_occupation, sm_wieldType, sm_item, sm_itemName, sm_commissionTime ) value ( \'%s\', %i, %i, %i, %i, \'%s\', \'%s\', now() );" \
					% ( BigWorld.escape_string( sellerName ), price, itemType, occupation, wieldType, itemData, itemName )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._saleGoodsCB, sellerName, price, item ) )


	def _saleGoodsCB( self, sellerName, price, item, result, dummy, errstr ):
		"""
		增加一个物品的回调函数

		@param sellerName:	寄卖者
		@type sellerName:	STRING
		@param price:		寄卖价格
		@type price:		INT32
		@param item:		物品
		@type item:			ITEM
		@param result、dummy、errstr: 见api文档
		"""
		if errstr:
			# 写数据库失败，把物品信息写入日志，此时物品已经从玩家背包删除。且在cell已经做过一次这样的处理
			itemData = repr( item.addToDict() )
			INFO_MSG( "error:%s vender an item. price of item: %i, item data: %s" % ( sellerName, price, itemData ) )
			return


	def buyGoods( self, index, moneyCount, playerBaseMailbox ):
		"""
		Define method.
		给玩家cell的买一个寄卖物品接口

		self.queryData的数据结构为：{ "index":[owner,price,item,queryTime],… }

		@param index：		物品在数据库中的序号
		@type index:		INT32
		@param moneyCount	买者所拥有的金币数目
		@type moneyCount:	UINT32
		@param playerBaseMailbox:	买家的mailbox
		@type playerBaseMailbox:	MAILBOX
		"""
		if not self.queryData.has_key( index ):		# 物品已经被买走，或者数据已经被清空
			return
		if self.mutexDict.has_key( index ):			# 已经有人在买了
			playerBaseMailbox.client.onStatusMessage( csstatus.CMS_ITEM_HAS_BEEN_SELLED, "" )
			return
		else:
			self.mutexDict[index] = time.time()		# 把index加入互斥字典
			# 更新相应的queryData时间，避免被ontimer清空，玩家收到物品后回来通知卖家的数据可以根据index从内存中获得，而不需要传输过多的参数
			self.queryData[index][4] = time.time()
		if int( self.queryData[index][1] ) > moneyCount:
			return

		sellerName = self.queryData[index][0]
		price = int( self.queryData[index][1] )
		itemDict = cPickle.loads( self.queryData[index][2] )
		itemDict["tmpExtra"] = cPickle.dumps( {}, 2 )
		item = g_item.createFromDict( itemDict )

		if hasattr( playerBaseMailbox, "cell" ) :	# 当前是在 CommissionSaleMgr 对应的 base中，playerBaseMailbox有可能刚刚销毁cell
			playerBaseMailbox.cell.cms_receiveSaleItem( sellerName, price, item, index )
		else:
			del self.mutexDict[ index ]


	def sendItemSuccess( self, buyerName, index ):
		"""
		Define method.
		玩家收到物品回来确认的接口

		@param buyerName:	买家的名字
		@type buyerName:	STRING
		@param sellerName:	卖家的名字
		@type sellerName:	STRING
		@param itemName:	物品的名字
		@type itemName:		STRING
		@param price:		寄卖价格
		@type price:		INT32
		@param index：		物品在数据库中的序号
		@type index:		INT32
		"""
		query = "update custom_SaleOnCommission set sm_state = 1, sm_purchaser=\'%s\' where id = %i" % ( BigWorld.escape_string( buyerName ), index )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._sendItemSuccessCB, buyerName, index ) )


	def _sendItemSuccessCB( self, buyerName, index, resultSet, rows, errstr ):
		"""
		sendItemSuccess的回调函数
		"""
		if errstr:
			INFO_MSG( "error:updated sm_state to '1' failure,the index is %i." % ( index ) )
			return

		BigWorld.lookUpBaseByName( "Role", self.queryData[index][0], Functor( self._getPlayerMailboxCB, buyerName, index ) )


	def _getPlayerMailboxCB( self, buyerName, index, callResult ):
		"""
		通过卖家名字查找卖家在线情况的回调函数

		前面参数同 sendItemSuccess
		@param callResult:	BigWorld.lookUpBaseByName的查找结果,mailbox、True、False都有可能
		@type callResult:	MAILBOX OR BOOL
		"""
		# 返回一个mailbox时,表示找到玩家且在线
		if not isinstance( callResult, bool ):		# isinstance函数见python手册
			# 把钱给卖家
			if hasattr( callResult, "cell" ):	# 当前是在 CommissionSaleMgr 对应的 base中，callResult有可能刚刚销毁cell
				callResult.cell.cms_receiveMoney( int( self.queryData[index][1] ), self.queryData[index][3], buyerName, index )
		# 走到这一步，mutexDict、queryData不可能到时效而被onTimer清空
		del self.mutexDict[ index ]
		del self.queryData[ index ]


	def sendMoneySuccess( self, index ):
		"""
		Define method.
		卖家收到钱,通知管理器的接口
		卖家在线收到钱时调用此函数;卖家不在线,重登陆收到钱时,也调用此函数

		@param index：	物品在数据库中的序号
		@type index:	INT32
		"""
		# 交易完成,写状态2
		query = "update custom_SaleOnCommission set sm_state = 2,sm_endTradeTime=now() where id = %i" % ( index )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._sendMoneySuccessCB, index ) )


	def _sendMoneySuccessCB( self, index, result, dummy, errstr ):
		"""
		sendMoneySuccess的回调函数
		"""
		if errstr:		# 更新物品状态出错,卖家下次上线还能收到钱
			INFO_MSG( "error:updated sm_state to '2' failure,the index is %i." % ( index ) )
			return


	def queryByType( self, param1, param2, param3, beginNum, callFlag, playerBaseMailbox, playerName ):
		"""
		Define method.

		按物品类型查询,为了适应武器类型物品的3层查询(详见策划文档),设置了param1,param2,param3这3个参数,这3个参数的解释由callFlag控制.
		当callFlag为1时,param1为物品类型,param2为0,param3为0,此时是按物品类型查询;
		当callFlag为2时,说明是查询武器类型的物品->武器的适用职业,param1为物品类型,param2为武器的职业,param3为0;
		当callFlag为3时,说明是查询武器类型的物品->武器的适用职业->武器的单双手适性,param1为玩家名、param2为武器的职业,param3为武器的单双手适性
		当查询的不是武器类型的物品时,仅需用到param1,因为其他物品没有武器类型物品的查询层次.

		@param param1,param2,param3: 根据callFlag参数决定这3个参数的作用
		@type param1: 		STRING
		@type param2:		STRING
		@type param3:		STRING
		@param beginNum : 	查询物品的开始位置
		@type biginNum:		INT32
		@param callFlag : 		查询的类型
		@type callFlag : 		INT8
		@param playerBaseMailbox:	玩家baseMailBox
		@type playerBaseMailbox:		MAILBOX
		@param playerName:		玩家名字
		@type playerName:		STRING
		"""
		# 限制玩家的两次查询时间间隔必须大于或等于QUERY_LIMIT_TIME
		if self.queryTime.has_key( playerName ):
			if time.time() - self.queryTime[playerName] < QUERY_LIMIT_TIME:
				return

		if callFlag == 1:
			query = "select id,sm_owner,sm_price,sm_item, sm_itemName from custom_SaleOnCommission where sm_type = %i and sm_state = 0 limit %i,%i"\
					 % ( int( param1 ), beginNum, MAXLENGTH )
			BigWorld.executeRawDatabaseCommand( query, Functor( self._queryGoodsCB, playerBaseMailbox, playerName ) )
			return
		if callFlag == 2:
			query = "select id,sm_owner,sm_price,sm_item, sm_itemName from custom_SaleOnCommission where sm_type = %i and ( sm_occupation & %i ) = sm_occupation and sm_state = 0 limit %i,%i"\
					 % ( int( param1 ), int( param2 ), beginNum, MAXLENGTH )
			BigWorld.executeRawDatabaseCommand( query, Functor( self._queryGoodsCB, playerBaseMailbox, playerName ) )
			return
		if callFlag == 3:
			query = "select id,sm_owner,sm_price,sm_item, sm_itemName from custom_SaleOnCommission where sm_type = %i and ( sm_occupation & %i ) = sm_occupation and ( sm_wieldType & %i ) = sm_wieldType and sm_state = 0 limit %i,%i"\
					 % ( int( param1 ), int( param2 ), int( param3 ), beginNum, MAXLENGTH )
			BigWorld.executeRawDatabaseCommand( query, Functor( self._queryGoodsCB, playerBaseMailbox, playerName ) )
			return


	def queryByItemName( self, itemName, beginNum, playerBaseMailbox, playerName ):
		"""
		Define method.

		按物品名字查询数据库的接口
		"""
		if self.queryTime.has_key( playerName ):
			if time.time() - self.queryTime[playerName] < QUERY_LIMIT_TIME:
				return

		query = "select id, sm_owner, sm_price, sm_item, sm_itemName from custom_SaleOnCommission where sm_itemName = \'%s\' and sm_state = 0 limit %i,%i"\
				 % ( itemName, beginNum, MAXLENGTH )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._queryGoodsCB, playerBaseMailbox, playerName ) )


	def queryOwnGoods( self, beginNum, playerBaseMailbox, playerName ):
		"""
		Define method.

		玩家查询自己寄卖物品的接口
		"""
		if self.queryTime.has_key( playerName ):
			if time.time() - self.queryTime[playerName] < QUERY_LIMIT_TIME:
				return

		query = "select id, sm_owner, sm_price, sm_item, sm_itemName from custom_SaleOnCommission where sm_owner = \'%s\' and sm_state = 0 limit %i,%i"\
					 % ( BigWorld.escape_string( playerName ), beginNum, MAXLENGTH )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._queryOwnGoodsCB,  playerBaseMailbox, playerName ) )


	def _queryGoodsCB( self, playerBaseMailbox, playerName, resultSet, rows, errstr ):
		"""
		查询寄卖物品的回调函数

		"""
		if errstr:		# 查询出错,无处理
			INFO_MSG( errstr )
			return
		if rows == 0:	# 没有查到任何数据
			return

		self.queryTime[playerName] = time.time()
		for tempGoods in resultSet:			# queryData的数据结构为{ "index":[owner,price,item,itemName,queryTime],… }
			itemName = tempGoods.pop( 4 )	# 客户端不需要此数据，减少传输量
			playerBaseMailbox.client.cms_receiveQueryInfo( tempGoods )
			tempGoods.append( itemName )	# 重新把itemName置入
			tempGoods.append( time.time() )
			self.queryData[ int( tempGoods[0] ) ] = tempGoods[1:]


	def _queryOwnGoodsCB( self, playerBaseMailbox, playerName, resultSet, rows, errstr ):
		"""
		查询自己寄卖物品的回调函数
		"""
		if errstr:		# 查询出错,无处理
			INFO_MSG( errstr )
			return
		if rows == 0:	# 没有查到任何数据
			return
		self.queryTime[playerName] = time.time()
		for tempGoods in resultSet:
			itemName = tempGoods.pop( 4 )	# 客户端不需要此数据，减少传输量
			playerBaseMailbox.client.cms_receiveOwnGoodsInfo( tempGoods )
			tempGoods.append( itemName )	# 重新把itemName置入
			tempGoods.append( time.time() )
			# queryData的数据结构为{ "index":[owner,price,item,itemName,queryTime],… }
			self.queryData[ int( tempGoods[0] ) ] = tempGoods[1:]


	def queryForLogin( self, playerBaseMailbox, playerName ):
		"""
		Define method.
		玩家上线时查询自己的寄卖信息

		@param playerName:	查询玩家的名字
		@type playerName:	STRING
		@param playerBaseMailbox:	玩家的mailbox
		@type playerBaseMailbox:	MAILBOX
		"""
		query = "select id, sm_price,sm_purchaser,sm_itemName from custom_SaleOnCommission where sm_owner=\'%s\' and sm_state = 1 " \
				% ( BigWorld.escape_string( playerName ) )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._queryForLoginCB, playerBaseMailbox ) )


	def _queryForLoginCB( self, playerBaseMailbox, resultSet, rows, errstr ):
		"""
		queryForLogin的读取数据库的回调函数
		这是玩家上上线后，查询有几个关于他卖了的物品的信息，如果没有，就返回，如果有，则接着后续处理

		@param playerBaseMailbox:	卖家base
		@type playerBaseMailbox:	MAILBOX
		@param playerName:	查询玩家的名字
		@type playerName:	STRING
		"""
		if errstr:
			INFO_MSG( errstr )
			return
		if rows == 0:
			return

		for temp in resultSet:
			if hasattr( playerBaseMailbox, "cell" ) :	#当前是在 CommissionSaleMgr 对应的 base中，  playerBaseMailbox有可能刚刚销毁cell
				playerBaseMailbox.cell.cms_receiveMoney( int( temp[1] ), temp[3], temp[2], int( temp[0] ) )


	def cancelSaleGoods( self, index, playerBaseMailbox, playerName ):
		"""
		Define method.
		玩家取消寄卖

		@param index:	物品在数据库中的索引
		@type index:	INT32
		@param playerBaseMailbox:	玩家的mailbox
		@type playerBaseMailbox:	MAILBOX
		@param playerName:	玩家名字
		@type playerName:	STRING
		"""
		if not self.queryData.has_key( index ):		# 物品已经被买走，或者数据已经被自动清空
			playerBaseMailbox.client.onStatusMessage( csstatus.CMS_QUERY_AGAIN, "" )
			return
		if self.mutexDict.has_key( index ):			# 已经有人在买了
			playerBaseMailbox.client.onStatusMessage( csstatus.CMS_ITEM_HAS_BEEN_SELLED, "" )
			return
		else:
			self.mutexDict[index] = time.time()		# 把index加入互斥字典
			self.queryData[index][4] = time.time()	# 更新相应数据的时间，避免被清空

		if self.queryData[index][0] != playerName: #不能取消别人寄卖 物品，预防作弊，无须提示
			return

		itemDict = cPickle.loads( self.queryData[index][2] )
		itemDict["tmpExtra"] = cPickle.dumps( {}, 2 )
		item = g_item.createFromDict( itemDict )

		playerBaseMailbox.cell.cms_receiveCancelItem( item, index )


	def cancelSuccess( self, index ):
		"""
		Define method.
		成功取消寄卖,玩家通知寄卖管理器的接口
		@param index:	寄卖物品的数据库索引
		@type index:	INT32
		"""
		query = "update custom_SaleOnCommission set sm_state = 3,sm_endTradeTime = now() where id = %i" %( index )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._cancelSuccessCB, index ) )


	def _cancelSuccessCB( self, index, result, dummy, errstr ):
		"""
		cancelSuccess的回调函数

		@param index:	寄卖物品的数据库索引
		@type index:	INT32
		"""
		if errstr:
			INFO_MSG( "error:updated sm_state to '3' failure when '_cancelSuccessCB',the index is %i." % ( index ) )
			return
		# 走到这一步，mutexDict、queryData不可能到时效而被ontimer清空
		del self.mutexDict[ index ]
		del self.queryData[ index ]


	def onTimer( self, id, userArg ):
		"""
		Timer
		"""
		# 先清理mutexDict
		for temp in self.mutexDict:
			if temp is not None and time.time() - self.mutexDict[temp] > COMMISSION_FAILURE_TIME:
				del self.mutexDict[temp]

		for temp in self.queryData:
			if temp is not None and time.time() - self.queryData[temp][4] > QUERY_CLEAR_TIME:
				del self.queryData[temp]

		for temp in self.queryTime:
			if temp is not None and time.time() - self.queryTime[temp] > QUERY_LIMIT_TIME:
				del self.queryTime[temp]




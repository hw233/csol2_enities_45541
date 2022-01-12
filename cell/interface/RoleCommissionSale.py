# -*- coding: gb18030 -*-
#

import BigWorld
from bwdebug import *
import csdefine
import csconst
import csstatus
import ItemBagRole
import cPickle
import items

g_items = items.instance()	# 在创建一个物品时需要

class RoleCommissionSale:
	"""
	寄卖系统玩家cell端接口
	"""
	def __init__( self ):
		"""
		"""
		# persistent的数据，如果不为0就去读数据库，如果为0就表明无寄卖信息不用检查数据库
		# 避免每次上线都进行读取数据库操作，这个值默认为0，不为0时表示玩家在数据库中寄卖的物品数量，在玩家有寄卖活动时更新
		# self.cms_itemNum = 0


	def __operateVerify( self, entityID ):
		"""
		验证是否能够进行寄卖操作

		@param entityID:寄卖npc的id
		@type entityID: OBJECT_ID
		"""
		if self.level < 10:		# 寄卖的最小级别为10
			return False

		# 尝试一下是否能找到该NPC
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			return False

		# 判断是否在允许交易范围内
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )	# 暂时使用IV_TRADER_TOO_FAR
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return False

		# 会有统一的判断对应的交易npc的做法，暂时不使用wangshufeng
		#if not npc.commissionNPC:	# 验证是否是寄卖npc
		#	return False

		# 在npc的def里加入：
		#<commissionNPC>
		#	<Type>			BOOL			</Type>
		#	<Flags>			CELL_PUBLIC		</Flags>
		#	<Persistent>		false			</Persistent>
		#	<Default>		1			</Default>
		#</commissionNPC>

		return True


	def cms_enterTrade( self, entityID ):
		"""
		Define method.
		被寄卖npc调用

		@param entityID:	寄卖NPC的id
		@type entityID:		OBJECT_ID
		"""
		if not self.__operateVerify( entityID ):
			return

		self.client.cms_enterTrade()	# 通知客户端打开寄卖界面


	def cms_saleGoods( self, srcEntityID, price, uid, entityID ):
		"""
		Exposed method.
		寄卖一个物品
		@param srcEntityID：隐含调用者ID
		@type srcEntityID:	OBJECT_ID
		@param price：		寄卖的价格
		@type price:		UINT32
		@param uid：		物品的唯一ID
		@type uid:			INT64

		过程：	1：处理各种寄卖的条件判断，任何一个条件不符合直接返回。在客户端也会有类似的判断，提示信息也在客户端那边返回。
				2：处理寄卖对玩家的影响。（钱少了，物品没了）
				3：记录这个影响到日志，方便在有问题的时候查看。
				4：将这个寄卖的命令和信息提交到base的 寄卖管理器。
		"""
		if srcEntityID != self.id:
			return False

		if not self.__operateVerify( entityID ):
			return

		if not self.cms_itemNum < csconst.COMMISSION_ITEMS_UPPER_LIMIT:
			self.statusMessage( csstatus.CMS_ITEM_OVERSTEP )
			return

		item = self.getItemByUid_( uid )
		# 背包里无此物品
		if item == None:
			return

		# 检查自身的钱数是否能够支付寄卖费用
		value = price * csconst.COMMISSION_CHARGE_PERCENT
		if self.money < int( value ):
			return

		# 收取玩家寄卖费用，把物品从玩家背包删除
		self.payMoney( value, csdefine.CHANGE_MONEY_SALEGOODS )
		self.removeItemByUid_( item.uid, reason = csdefine.DELETE_ITEM_SALEGOODS )
		self.cms_itemNum += 1	# 每寄卖一件物品，此数据增1

		# 把物品数据写入日志，以备物品传输出错处理
		itemData = repr( item.addToDict() )
		INFO_MSG( "INFO:%s vender an item. price of item: %i, item data: %s" % ( self.playerName, price, itemData ) )

		# 把物品发送给寄卖系统
		self._getCommissionSaleMgr().saleGoods( self.playerName, price, item )


	def cms_buyGoods( self, srcEntityID, index, entityID ):
		"""
		Exposed method.
		从寄卖系统买入一个物品

		@param srcEntityID：隐含传送过来的调用者id
		@type srcEntityID:	OBJECT_ID
		@param index：		物品的序号
		@type index:		INT32

		过程：	1：处理各种简单买的条件判断，任何一个条件不符合直接返回。在客户端也会有类似的判断，提示信息也在客户端那边返回。
					物品的数据要从数据库中读出，所以这里的条件判断没有涉及到物品信息。
				2：将这个买物品的命令和信息提交到base的 寄卖管理器。
		"""
		if srcEntityID != self.id:
			return False

		if not self.__operateVerify( entityID ):
			return

		tempOrder = self.getNormalKitbagFreeOrder()
		if tempOrder == -1:
			self.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return

		self._getCommissionSaleMgr().buyGoods( index, self.money, self.base )


	def cms_receiveSaleItem( self, owner, price, item, index ):
		"""
		Define method.
		给玩家发送一个物品

		@param owner:	寄卖物品的所有者
		@type owner:	STRING
		@param price:	寄卖物品的价格
		@type price:	INT32
		@param item:	寄卖物品
		@type item:		ITEM
		@param index:	物品索引
		@type item:		INT32
		"""
		# 再一次检查玩家是否够钱
		if self.money < price:
			return

		self.payMoney( price, csdefine.CHANGE_MONEY_RECEIVESALEITEM )
		self.addItem( item, csdefine.ADD_ITEM_RECEIVESALEITEM )
		itemName = item.query( "name" )

		self._getCommissionSaleMgr().sendItemSuccess( self.playerName, index )


	def cms_receiveCancelItem( self, item, index ):
		"""
		Define method.

		玩家取消寄卖物品的接口
		"""
		self.cms_itemNum -= 1
		self.addItem( item, csdefine.ADD_ITEM_RECEIVECANCELITEM )
		self._getCommissionSaleMgr().cancelSuccess( index )


	def cms_receiveMoney( self, price, itemName, buyerName, index ):
		"""
		Define method.
		通知卖家物品卖出

		@param price: 	物品的价格
		@type price: 	UNINT32
		@param itemID: 	物品的id
		@type itemID: 	STRING
		@buyerName: 	买物品的玩家名字
		@type buyerName: STRING
		@param index:	物品索引
		@type item:		INT32

		过程：	1：金钱太多的处理
				2：玩家成功获得寄卖金钱的统治
		"""
		if self.testAddMoney( price ) > 0:
			self.statusMessage( csstatus.CIB_MONEY_OVERFLOW )
			return

		if self.gainMoney( price, csdefine.CHANGE_MONEY_CMS_RECEIVEMONEY ) == False:
			# 下次上线再重新获得
			return

		self.cms_itemNum -= 1
		# 收钱时写个日志
		INFO_MSG( "vender receive the money for commission.verderName:'%s', price: '%i',itemIndex:'%i' "\
			 % ( self.playerName, price, index ) )
		self._getCommissionSaleMgr().sendMoneySuccess( index )
		self.statusMessage( csstatus.CMS_NOTIFY_VENDER, itemName, buyerName )


	def cms_cancelSaleGoods( self, srcEntityID, index, entityID ):
		"""
		Exposed method.
		取消寄卖物品

		@param srcEntityID:	客户端隐式传给cell的调用者id
		@type srcEntityID:	OBJECT_ID
		@param index:    	物品序号
		@type index:		INT32
		@param entityID: 	寄卖NPC的id
		@type entityID:		OBJECT_ID

		过程：	1：处理简单的取消条件判断
				2：将取消寄卖物品命令和相关信息发送到base的 寄卖管理器
		"""
		if srcEntityID != self.id:
			return False

		if not self.__operateVerify( entityID ):
			return

		# getNormalKitbagFreeOrder(),有空位则返回一个order；否则返回-1
		if self.getNormalKitbagFreeOrder() == -1:	# 背包没有空格
			self.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return

		self._getCommissionSaleMgr().cancelSaleGoods( index, self.base, self.playerName )


	def _getCommissionSaleMgr( self ):
		"""
		获得全局的寄卖管理器

		@return: CommissionSaleMgr的base mailbox
		"""
		# 如果产生异常就表示有bug
		return BigWorld.globalData["CommissionSaleMgr"]


	def cms_queryByType( self, srcEntityID, param1, param2, param3, beginNum, callFlag, entityID ):
		"""
		Exposed method.

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
		@param call : 		查询的类型
		@type call : 		INT8
		@param entityID: 	寄卖NPC的id
		@type entityID:		OBJECT_ID
		"""
		if srcEntityID != self.id:
			return False

		if not self.__operateVerify( entityID ):
			return

		self._getCommissionSaleMgr().queryByType( param1, param2, param3, beginNum, callFlag, self.base, self.playerName )


	def cms_queryByItemName( self, srcEntityID, itemName, beginNum, entityID ):
		"""
		Exposed method.

		给客户端提供的根据物品名字查询的接口
		@param entityID: 	寄卖NPC的id
		@type entityID:		OBJECT_ID
		"""
		if srcEntityID != self.id:
			return False

		if not self.__operateVerify( entityID ):
			return

		self._getCommissionSaleMgr().queryByItemName( itemName, beginNum, self.base, self.playerName )


	def cms_queryOwnGoods( self, srcEntityID, beginNum, entityID ):
		"""
		Exposed method.
		查询自己寄卖物品的接口
		@param entityID: 	寄卖NPC的id
		@type entityID:		OBJECT_ID
		"""
		if srcEntityID != self.id:
			return False

		if not self.__operateVerify( entityID ):
			return

		self._getCommissionSaleMgr().queryOwnGoods( beginNum, self.base, self.playerName )
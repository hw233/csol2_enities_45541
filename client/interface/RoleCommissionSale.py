# -*- coding: gb18030 -*-



MONEY_CHECK = 1		# checkAndNotify函数用来检查money的标志
import GUIFacade
import items
import cPickle
import csdefine

g_item = items.instance()	# 将在客户端把寄卖管理器发过来的数据还原成一个item

class RoleCommissionSale:
	"""
	玩家寄卖系统客户端接口
	"""

	def __init__( self ):
		"""
		"""
		pass

	def cms_enterTrade( self ):
		"""
		Define method.

		提供给玩家cell打开客户端寄卖界面的接口
		"""
		pass	# 界面暂时不考虑


	def cms_saleGoods( self, price, uid, entityID ):
		"""
		寄卖一个物品

		@param price：	寄卖的价格
		@type price:	UINT32
		@param uid:	物品所在背包号
		@type uid:	INT64
		@param amount:	寄卖物品的数量
		@type amount:	INT16
		@param entityID:寄卖npc的id
		@type entityID:	OBJECT_ID
		"""
		self.cell.cms_saleGoods( price, uid, entityID )


	def cms_buyGoods( self, index, entityID ):
		"""
		买入一个寄卖物品

		@param index:	买入物品在数据库中的序号
		@type index:	INT32
		@param entityID:npcID
		@type entityID:	OBJECT_ID
		"""
		self.cell.cms_buyGoods( index, entityID )


	def cms_receiveQueryInfo( self, tempList ):
		"""
		define method
		返回查询结果

		tempList的数据结构为[index，owner，price，item]
		@param tempList:	物品数据列表
		@type tempList:		ARRAY of STRING
		"""
		# 把数据发送给界面wsf
		print tempList


	def cms_receiveOwnGoodsInfo( self, tempList ):
		"""
		Define method.
		接收查询自己寄卖物品数据的客户端接口

		tempList的数据结构为[index，owner，price，item]
		@param goodsList:	物品数据列表
		@type goodsList:	ARRAY of STRING
		"""
		# 把数据发送给界面wsf
		print tempList


	def cms_queryByType( self, param1, param2, param3, beginNum, callFlag, entityID ):
		"""
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
		@param traderID:	寄卖npc的id
		@type traderID:		INT32
		"""
		self.cell.cms_queryByType( param1, param2, param3, beginNum, callFlag, entityID )


	def cms_queryByItemName( self, itemName, beginNum, entityID ):
		"""
		按物品名字查询的客户端接口

		@type itemName:		物品名字
		@type itemName:		STRING
		@param beginNum : 	查询物品的开始位置
		@type biginNum:		INT32
		@param entityID:	寄卖npc的id
		@type entityID:		INT32
		"""
		self.cell.cms_queryByItemName( itemName, beginNum, entityID )


	def cms_queryOwnGoods( self, beginNum, entityID ):
		"""
		查询自己寄卖物品的接口，在寄卖界面点击“出售道具”，转入出售道具窗口同时从数据库获得自己寄卖的物品

		参数请参照cms_queryByItemName
		"""
		self.cell.cms_queryOwnGoods( beginNum, entityID )


	def cms_cancelSaleGoods( self, index, entityID ):
		"""
		取消一个寄卖物品

		@param index:	买入物品在数据库中的序号
		@type index:	INT32
		@param entityID:	寄卖npc的id
		@type entityID:		INT32
		"""
		self.cell.cms_cancelSaleGoods( index, entityID )
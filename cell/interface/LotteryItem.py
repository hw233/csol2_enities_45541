# -*- coding: gb18030 -*-
#
# $Id: LotteryItem.py

import items
import random
import csconst
import csdefine
import ECBExtend
import ItemTypeEnum
import Const
from bwdebug import *
from MsgLogger import g_logger
import sys

#锦囊
from items.ItemDropLoader import ItemDropLotteryLoader
from items.EquipEffectLoader import EquipEffectLoader

g_itemDropLotteryLoader = ItemDropLotteryLoader.instance()
g_items = items.instance()

class LotteryItem:
	"""
	锦囊系统的相关代码，这部分代码没有写到物品中的原因是，锦囊在抽出物品后，需要有存储相关的数据到人物身上，
	在人物中途下线后，物品需要被存储到数据库中，在玩家下一次上线后补充带玩家身上。
	"""
	def __init__( self ):
		self.__ItemDropAmount = [ [0, 1 ], [0, 1 ], [0, 3 ], [0, 5], [0, 7], [0, 50], [0, 1] ]	#记录掉落的各等级的物品列表。
							#tuple第一个值表示实际随机出的该等级的物品个数，第二个值表示可以随机出的该等级物品的数量

	def onRoleOff( self ):
		"""
		玩家下线，查看是否有物品没有领取
		"""
		if self.havelotteryItem():
			self.addlotteryItem()

	def onlottery( self, lotteryUid ):
		"""
		开始随机物品，并存储
		"""
		self.clearlottery()
		self.lotterytimes += 1
		self.lotteryUid = lotteryUid				#记录锦囊的位置
		itemIDs = []
		if self.lotterytimes != 50:
			factitemIDs    = self.getDrops( 2, True   ) #使用真实掉率随机两个物品
			falsityitemIDs = self.getDrops( 10, False ) #使用显示掉率随机十个物品
			itemIDs = factitemIDs + falsityitemIDs
		else:											#每50次使用显示掉率随机全部物品一次
			itemIDs = self.getDrops( 12, False ) 		#使用显示掉率随机十个物品
			self.lotterytimes = 0

		for index in xrange( len( itemIDs ) ):
			item = None
			if itemIDs[ index ][0] == "equip":
				level =  self.getLevel()
				level += random.randint( -5, 5 )
				level = max( 1, level )
				level = min( csconst.ROLE_LEVEL_UPPER_LIMIT, level )
				itemInfo = g_itemDropLotteryLoader.getEquipDropInfo( level )
				if not itemInfo:
					try:
						g_logger.lotteryExceptLog("error", "CLottery Item getEquipDropInfo failed, equip level(%s)" % level )
					except:
						g_logger.logExceptLog( GET_ERROR_MSG() )
					self.clearlottery()
					return
				itemID, quality, prefix, odds = itemInfo
				item = g_items.createDynamicItem( int( itemID ) , 1 )
				if quality != 0 and prefix != 0:		#手写装备不需要设置品质和前缀
					item.setQuality( quality )
					item.setPrefix( prefix )
					if not item.createRandomEffect():
						try:
							g_logger.lotteryExceptLog( "error","CLottery Item CreatEquip Failed, createRandomEffect failed,item_id(%s),quality(%s),prefix(%s),odds(%s)" % (itemID, quality, prefix, odds) )
						except:
							g_logger.logExceptLog( GET_ERROR_MSG() )
						self.clearlottery()
						return
			else:
				item = g_items.createDynamicItem( int( itemIDs[ index ][0] ), itemIDs[index][1] )
				if not item:
					try:
						g_logger.lotteryExceptLog( "error", "Create Item Failed, itemID(%s), amount(%s)" % ( itemIDs[ index ][0], itemIDs[index][1] )  )
					except:
						g_logger.logExceptLog( GET_ERROR_MSG() )
					self.clearlottery()
					return
			self.AllLotteryItems.append( item )

		finallyPosA = 0								#默认的开始时两个物品的位置
		finallyPosB = 1

		insertPosA = random.randint( 0, 11 )		#将候补的物品随机插入到列表的后面位置中
		if insertPosA != finallyPosA:
			temp = self.AllLotteryItems[ insertPosA ]
			self.AllLotteryItems[ insertPosA ] = self.AllLotteryItems[ finallyPosA ]
			self.AllLotteryItems[ finallyPosA ] = temp
			if insertPosA == finallyPosB:
				finallyPosB = finallyPosA
			finallyPosA = insertPosA

		insertPosB = random.randint( 0, 11 )		#将候补的物品随机插入到列表的后面位置中
		if insertPosB != finallyPosB:
			temp = self.AllLotteryItems[ insertPosB ]
			self.AllLotteryItems[ insertPosB ] = self.AllLotteryItems[ finallyPosB ]
			self.AllLotteryItems[ finallyPosB ] = temp
			if insertPosB == finallyPosA:				#当随机到的B物品的位置是A物品所在的位置
				finallyPosA = finallyPosB				#那么A物品就被替换到了1号位置 更改A物品的索引位置
			finallyPosB = insertPosB


		self.lotteryItem = self.AllLotteryItems[ finallyPosA ]	#记录当默认给玩家的物品
		if not self.lotteryItem or len( self.AllLotteryItems) != 12 or not self.AllLotteryItems[ finallyPosB ]:
			try:
				g_logger.lotteryExceptLog( "error", "lotteryItem is none: finallyPosA = %s,finallyPosB = %s, self.AllLotteryItems = %s " \
				% ( finallyPosA,finallyPosB,self.AllLotteryItems ) )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			self.clearlottery()
			return

		self.setTemp( "lotterydefaultIndex", finallyPosA )		#记录候补物品A的位置
		self.setTemp( "lotteryAlternateIndex", finallyPosB )	#记录候补物品B的位置
		self.setTemp( "sendlotteryindex" , 0 )					#记录向客户端发送物品的索引起始位置
		self.addTimer( 0.0, csconst.ROLE_INIT_INTERVAL, ECBExtend.SHOW_LOTTER_ITEMS )	#向客户端发送数据
		self.client.showlotteryWindow()							#最后显示界面
		self.lotteryState = True								#走到这里说明此次开启成功，设置锦囊状态为开启中.

	def showLotterItems( self, timerID, cbid ):
		"""
		向客户端发送物品的数据 一次4个 总共12个
		"""
		begin = self.queryTempInt( "sendlotteryindex" )	#获取发送的开始位置
		AllItem = len( self.AllLotteryItems )
		end   = min( AllItem, begin + Const.LT_SENDNUM )	#计算发送的终止位置

		if begin < AllItem:
			self.addTempInt( "sendlotteryindex", Const.LT_SENDNUM )
		else: #如果是发送最后一次 那么清除掉索引 将候补物品的位置发送给客户端
			AIndex = self.queryTempInt( "lotterydefaultIndex" )
			BIndex = self.queryTempInt( "lotteryAlternateIndex" )
			self.client.lotteryABIndex( AIndex, BIndex )	#通知客户端两个物品的位置(实际上只有A和B可能会被玩家得到)
			self.removeTemp( "sendlotteryindex" )
			self.cancel( timerID )

		for index in xrange(begin, end):
			item = self.AllLotteryItems[ index ]
			self.client.updateLotterItems( item, index )

	def getPerhapsDropID( self, fact):
		"""
		根据掉率的类型，返回最有可能掉落的物品ID
		@type  fact        : bool
		@param fact        : 是否按照真实掉率来返回( 锦囊记录了两套掉率,一套实际的,一套虚假的 )
		@return type       : string
		@return parame     : 返回有可能掉落的物品ID（装备是一个大的类型,具体的装备还需要到世界掉落中去查找）
		"""
		odds = "fact_odds"
		if not fact:
			odds = "falsity_odds"

		randomValue = g_itemDropLotteryLoader.randomValue( fact )
		datas = g_itemDropLotteryLoader.getDropDatas()

		while 1:
			for data in datas:
				level = data["itemLevel"]
				factNum = self.__ItemDropAmount[level - 1 ][0 ]
				maxNum  = self.__ItemDropAmount[level - 1 ][1 ]
				if randomValue <= data[ odds ] and ( factNum < maxNum or fact ):
				#当随机的掉率小于该物品的掉率并且当前该等级的物品数量不超过应该随机出的数量上限或者使用的是真实掉率
					self.__ItemDropAmount[level - 1 ][0 ] += 1	#增加计数
					return ( data["id"],data["amount"] )
			randomValue = g_itemDropLotteryLoader.randomValue( fact, randomValue )	#再次随机一个物品，掉率的上限是上一次掉率

		DEBUG_MSG( "ItemDropLotteryLoader::getPerhapsDrop no item accord with claim " )
		return (0,0)


	def getDrops( self, amount, fact ):
		"""
		获取指定数量的掉落的物品ID
		@type  amount : int
		@param amount : 指定的掉落的数量
		@type  fact   : bool
		@param fact   : 掉落是否使用真实的掉率
		"""
		itemIDs = []
		for i in xrange( amount ):
			id,amount = self.getPerhapsDropID( fact )
			itemIDs.append( ( id, amount ) )
		return itemIDs

	def setlotteryItem( self, Item ):
		"""
		设置锦囊抽出的物品
		"""
		self.lotteryItem = Item

	def changelotteryItem( self, srcEntityID ):
		"""
		将当前抽出的物品更换成候补物品（该动作不可逆）
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			self.lotteryState = False
			self.clearlottery()	#清除掉原来的数据
			return
		AlternateIndex = self.queryTempInt( "lotteryAlternateIndex" )
		self.removeTemp( "lotteryAlternateIndex" )
		self.lotteryItem = self.AllLotteryItems[AlternateIndex]

	def getlotteryItem( self, srcEntityID ):
		"""
		将物品奖励给玩家
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			self.lotteryState = False
			self.clearlottery()	#清除掉原来的数据
			return
		self.addlotteryItem()

	def addlotteryItem( self ):
		"""
		把物品加到玩家背包
		"""
		self.lotteryState = False
		if not self.lotteryItem:
			self.clearlottery()
			return
		item = self.getItemByUid_( self.lotteryUid )
		if item is None:
			self.clearlottery()
			return
		item.unfreeze()
		item.onSpellOver( self )
		if self.lotteryItem.id == 60101001: #如果物品是金钱
			self.gainMoney( self.lotteryItem.getAmount(), csdefine.CHANGE_MONEY_LOTTERYITEM )
		else:
			if item.isBinded():	# 根据绿色精神，锦囊开物不强制绑定 by 姜毅
				self.lotteryItem.setBindType( ItemTypeEnum.CBT_PICKUP, self )
			self.addItemAndRadio( self.lotteryItem, ItemTypeEnum.ITEM_GET_CARD, reason =  csdefine.ADD_ITEM_ADDLOTTERYITEM )
		self.clearlottery()

	def havelotteryItem( self ):
		"""
		判断玩家是否有锦囊奖励没有领取
		"""
		return self.lotteryState

	def clearlottery( self ):
		"""
		清除锦囊的数据
		"""
		self.lotteryItem = None
		self.lotteryUid = 0
		self.AllLotteryItems = []
		self.__ItemDropAmount = [ [0, 1 ], [0, 1 ], [0, 3 ], [0, 5], [0, 7], [0, 50], [0, 1] ]	#记录掉落的各等级的物品列表。

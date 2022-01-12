# -*- coding: gb18030 -*-

import BigWorld
import cschannel_msgs
import ShareTexts as ST
from NPC import NPC
import cPickle
import items
g_items = items.instance()
import time
import csdefine
from Function import Functor
from bwdebug import *
import csstatus
from MsgLogger import g_logger

DESTROY_CBID = 89328

TI_SHOU_BAG_SIZE = 30

class TiShouNPC( NPC ):
	"""
	替售NPC
	"""
	def __init__( self ):
		"""
		"""
		NPC.__init__( self )
		self.tiShouItems 	= {}												# { uid01:{"item":item01,"price":price} ... }
		self.tiShouPets 	= {}												# { dbid01:{"pet":pet01,"price":price}, ... }
		self.tishouMoney 	= 0
		self.tiShouRecord	= []
		self.shopName 		= ""
		self.ownerName		= ""
		self.destroyTime	= 0
		self.ownerDBID		= 0



	def startTS( self ):
		"""
		开始寄售
		"""
		BigWorld.globalData["TiShouMgr"].startTS( self.ownerDBID )


	def stopTS( self ):
		"""
		结束寄售
		"""
		BigWorld.globalData["TiShouMgr"].stopTS( self.ownerDBID )


	def queryTSItems( self, playerBaseMB ):
		"""
		define method
		查询替售物品信息
		"""
		for info in self.tiShouItems.itervalues():
			if "item" in info:
				playerBaseMB.client.newTSItem( info["item"], info["price"], self.ownerDBID )

	def addTSItem( self, item, price, itemType, level, quality, metier, ownerDBID, playerBaseMB, roleProcess ):
		"""
		define method
		放入一个物品用于寄售
		"""
		if len( self.tiShouItems ) == TI_SHOU_BAG_SIZE:
			return
		
		self.tiShouItems[item.uid] = {"item":item, "price":price}
		BigWorld.globalData["TiShouMgr"].addTSItem( item, price, itemType, level, quality, metier, ownerDBID, self.shopName, self.ownerName, self.id, roleProcess )
		if playerBaseMB:
			playerBaseMB.cell.onAddTSItem( item.uid )
			playerBaseMB.client.newTSItem( item, price, self.ownerDBID  )

	def takeTSItem( self, uid, playerBaseMB, ownerDBID, roleProcess, itemID, amount  ):
		"""
		define method
		取走一个替售物品
		"""
		if not uid in self.tiShouItems:
			playerBaseMB.client.removeTSItemFromQueryInterFace( uid )
			playerBaseMB.client.onStatusMessage( csstatus.TI_SHOU_ITEM_NOT_EXIST, "" )
			return
		if itemID != self.tiShouItems[uid]["item"].id:
			playerBaseMB.client.onStatusMessage( csstatus.TI_SHOU_ITEM_ID_NOT_CORRECT, "" )
			return
		if amount != self.tiShouItems[uid]["item"].amount:
			playerBaseMB.client.onStatusMessage( csstatus.TI_SHOU_ITEM_COUNT_NOT_CORRECT, "" )
			return

		playerBaseMB.cell.onReceiveTSItem( self.tiShouItems[uid]["item"], 0 )
		BigWorld.globalData["TiShouMgr"].setTSItemDelFlag( uid, ownerDBID, roleProcess )
		playerBaseMB.client.removeTSItemFromQueryInterFace( uid )
		playerBaseMB.client.removeTSItem( uid, self.ownerDBID  )
		del self.tiShouItems[uid]

	def buyTSItem( self, uid, playerBaseMB, playerName, maxMoney, buyerDBID, itemID, amount, price  ):
		"""
		define method
		买一个替售物品
		"""
		if not uid in self.tiShouItems:
			playerBaseMB.client.removeTSItemFromQueryInterFace( uid )
			playerBaseMB.client.onStatusMessage( csstatus.TI_SHOU_ITEM_NOT_EXIST, "" )
			return

		if price != self.tiShouItems[uid]["price"]:
			playerBaseMB.client.onStatusMessage( csstatus.TI_SHOU_ITEM_PRICE_CHANGED, "" )
			playerBaseMB.client.updateTSItemPrice( uid, self.tiShouItems[uid]["price"], self.ownerDBID  )
			return

		if itemID != self.tiShouItems[uid]["item"].id:
			return
		if amount != self.tiShouItems[uid]["item"].amount:
			return

		if maxMoney < self.tiShouItems[uid]["price"]:
			playerBaseMB.client.onStatusMessage( csstatus.TI_SHOU_ITEM_NOT_ENOUGH_MONEY, "" )
			return
		timeTuple = time.localtime()
		playerBaseMB.cell.onReceiveTSItem( self.tiShouItems[uid]["item"], self.tiShouItems[uid]["price"] )
		self.tiShouRecord.append( [ playerName, cschannel_msgs.TONGCITYWAR_WU_PIN+self.tiShouItems[uid]["item"].name(), self.tiShouItems[uid]["price"],  cschannel_msgs.TONGCITYWAR_VOICE_1%(timeTuple[0],timeTuple[1],timeTuple[2],timeTuple[3],timeTuple[4]), amount ] )
		INFO_MSG( "店主:(%s)"%self.ownerName +  playerName + " " + "%i年%i月%i日%i时%i分"%(timeTuple[0],timeTuple[1],timeTuple[2],timeTuple[3],timeTuple[4]) + "用%i买走"%self.tiShouItems[uid]["price"] + "物品:%s"%self.tiShouItems[uid]["item"].name()  )
		BigWorld.lookUpBaseByName( "Role", self.ownerName, Functor( onNotifyGoodsSelled, cschannel_msgs.TONGCITYWAR_WU_PIN+self.tiShouItems[uid]["item"].name() ) )
		self._removeTSItemOnBuy( uid, playerBaseMB )
		
		try:
			g_logger.tiShouBuyItemLog( buyerDBID, playerName, self.ownerDBID, self.ownerName, uid, self.tiShouItems[uid]["item"].name(), amount, price )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG()  )

	def updateTSItemPrice( self, uid, price, ownerDBID, playerBaseMB ):
		"""
		define method
		"""
		if not uid in self.tiShouItems:
			return

		self.tiShouItems[uid]["price"] = price
		

		BigWorld.globalData["TiShouMgr"].updateTSItemPrice( uid, price, ownerDBID )
		playerBaseMB.client.updateTSItemPrice( uid, price, self.ownerDBID  )
		timeTuple = time.localtime()
		INFO_MSG( "店主:(%s)"%self.ownerName  + " " + "%i年%i月%i日%i时%i分"%(timeTuple[0],timeTuple[1],timeTuple[2],timeTuple[3],timeTuple[4]) + "更改物品%s价格为：%i"% ( self.tiShouItems[uid]["item"].name(), self.tiShouItems[uid]["price"])  )


	def queryTSPets( self, playerBaseMB ):
		"""
		define method
		"""
		for info in self.tiShouPets.itervalues():
			if "pet" in info:
				playerBaseMB.client.newTSPet( info["pet"], info["price"], self.ownerDBID  )


	def addTSPet( self, epitome, price, ownerDBID, playerBaseMB, roleProcess ):
		"""
		define method
		"""
		# 由于要对宠物售卖做全方位等级限制，所以需要把宠物等级和可携带等级都传过去 by 姜毅
		level	= epitome.getAttr("level")						# 等级
		
		species = epitome.getAttr("species")
		era 	= csdefine.PET_HIERARCHY_MASK & species         # 第几代宠物
		gender  = epitome.getAttr("gender")                     # 性别
		matier 	= csdefine.PET_TYPE_MASK & species     		     # 职业
		breed 	= epitome.getAttr("procreated")                 # 繁殖与否

		self.tiShouPets[epitome.databaseID] = {"pet":epitome, "price":price }
		BigWorld.globalData["TiShouMgr"].addTSPet( epitome, price, level, era, gender, matier, breed, ownerDBID, self.shopName, self.ownerName, self.id, roleProcess )
		if playerBaseMB:
			playerBaseMB.client.newTSPet( epitome, price, self.ownerDBID  )

	def takeTSPet( self, dbid, playerBaseMB, ownerDBID, roleProcess ):
		"""
		define method
		"""
		if not dbid in self.tiShouPets:
			return
		playerBaseMB.onReceiveTSPet( self.tiShouPets[dbid]["pet"], 0 )
		BigWorld.globalData["TiShouMgr"].setTSPetDelFlag( dbid, ownerDBID, roleProcess )
		playerBaseMB.client.removeTSPetFromQueryInterFace( dbid )
		playerBaseMB.client.removeTSPet( dbid, self.ownerDBID  )
		del self.tiShouPets[dbid]



	def removeTSPet( self, dbid, ownerDBID, playerBaseMB ):
		"""
		"""
		BigWorld.globalData["TiShouMgr"].removeTSPet( dbid, ownerDBID )
		playerBaseMB.client.removeTSPetFromQueryInterFace( dbid )
		playerBaseMB.client.removeTSPet( dbid, self.ownerDBID  )
		del self.tiShouPets[dbid]

	def buyTSPet( self, dbid, playerBaseMB, playerName, level, maxMoney, playerDBID, price ):
		"""
		define method
		"""
		if not dbid in self.tiShouPets:
			playerBaseMB.client.removeTSPetFromQueryInterFace( dbid )
			playerBaseMB.client.onStatusMessage( csstatus.TI_SHOU_PET_NOT_EXIST, "" )
			return

		if price != self.tiShouPets[dbid]["price"]:
			playerBaseMB.client.onStatusMessage( csstatus.TI_SHOU_PET_PRICE_CHANGED, "" )
			playerBaseMB.client.updateTSPetPrice( dbid, self.tiShouPets[dbid]["price"], self.ownerDBID  )
			return

		if maxMoney < self.tiShouPets[dbid]["price"]:
			playerBaseMB.client.onStatusMessage( csstatus.TI_SHOU_PET_NOT_ENOUGH_MONEY, "" )
			return
			
		takeLevel = self.tiShouPets[dbid]["pet"].getAttr("takeLevel")
		petLevel = self.tiShouPets[dbid]["pet"].level
		if level < takeLevel or level + 5 < petLevel:
			playerBaseMB.client.onStatusMessage( csstatus.TI_SHOU_PET_LEVEL_TOO_LOW, "" )
			return
			
		timeTuple = time.localtime()

		playerBaseMB.onReceiveTSPet( self.tiShouPets[dbid]["pet"], self.tiShouPets[dbid]["price"] )
		self.tiShouRecord.append( [ playerName, cschannel_msgs.TI_SHOU_INFO_1+self.tiShouPets[dbid]["pet"].getDisplayName(),  self.tiShouPets[dbid]["price"],  cschannel_msgs.TONGCITYWAR_VOICE_1%(timeTuple[0],timeTuple[1],timeTuple[2],timeTuple[3],timeTuple[4]), 1 ]  )
		INFO_MSG( "店主:(%s)"%self.ownerName +  playerName + " " + "%i年%i月%i日%i时%i分"%(timeTuple[0],timeTuple[1],timeTuple[2],timeTuple[3],timeTuple[4]) + "用%i买走"%self.tiShouPets[dbid]["price"] + "宠物:%s"%self.tiShouPets[dbid]["pet"].getDisplayName()  )
		BigWorld.lookUpBaseByName( "Role", self.ownerName, Functor( onNotifyGoodsSelled, cschannel_msgs.TI_SHOU_INFO_1+self.tiShouPets[dbid]["pet"].getDisplayName() ) )
		self._addTSMoney( int( self.tiShouPets[dbid]["price"] * 0.99 ) )
		playerBaseMB.client.onStatusMessage( csstatus.TI_SHOU_PET_BUY_SUCCESS, str(( self.tiShouPets[dbid]["pet"].getDisplayName(), )) )
		self.removeTSPet( dbid, playerDBID, playerBaseMB )
		
		try:
			g_logger.tiShouBuyPetLog( playerDBID, playerName, self.ownerDBID, self.ownerName, dbid, self.tiShouPets[dbid]["price"] )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def updateTSPetPrice( self, dbid, price, ownerDBID, playerBaseMB ):
		"""
		define method
		"""
		if not dbid in self.tiShouPets:
			return

		self.tiShouPets[dbid]["price"] = price

		BigWorld.globalData["TiShouMgr"].updateTSPetPrice( dbid, price, ownerDBID )
		playerBaseMB.client.updateTSPetPrice( dbid, price, self.ownerDBID  )
		timeTuple = time.localtime()
		INFO_MSG( "店主:(%s)"%self.ownerName + " " + "%i年%i月%i日%i时%i分"%(timeTuple[0],timeTuple[1],timeTuple[2],timeTuple[3],timeTuple[4]) + "更改宠物%s价格为：%i"% ( self.tiShouPets[dbid]["pet"].getDisplayName(), self.tiShouPets[dbid]["price"])  )


	def takeTSMoney( self, playerBase, ownerDBID ):
		"""
		define method
		"""
		money = self.tishouMoney
		if money <= 0:
			return
		self._addTSMoney( -money, ownerDBID )
		playerBase.cell.addTSMoney( money )


	def setTSInfo( self, shopName, ownerName, destroyTime, ownerDBID ):
		"""
		define method
		"""
		self.shopName = shopName
		self.ownerName = ownerName
		self.ownerDBID	= ownerDBID
		if self.destroyTime != destroyTime:
			self.destroyTime = destroyTime
			self.addTimer( destroyTime - time.time(), 0, DESTROY_CBID )


	def initTSItem( self, item, price ):
		"""
		define method
		放入一个物品用于寄售
		"""
		self.tiShouItems[item.uid] = {"item":item, "price":price}



	def initTSPet( self, epitome, price, ownerDBID ):
		"""
		define method
		放入一个物品用于寄售
		"""
		self.tiShouPets[epitome.databaseID] = {"pet":epitome, "price":price }


	def queryTSRecord( self, playerBase ):
		"""
		define method
		"""
		for i in self.tiShouRecord:
			playerBase.client.onReceiveTSRecord( i[0], i[1], i[2], i[3], i[4] )


	def takeTiShouMoneyAway( self ):
		"""
		define method
		"""
		self.tishouMoney = 0

	def initTiShouMoney( self, money ):
		"""
		define method
		初始化替售金钱
		"""
		self.tishouMoney = money


	def _removeTSItemOnBuy( self, uid, playerBaseMB ):
		"""
		"""
		self._addTSMoney( int( self.tiShouItems[uid]["price"] * 0.99 ) )
		self._removeTSItem( uid, playerBaseMB )

	def _removeTSItem( self, uid, playerBaseMB ):
		"""
		"""
		BigWorld.globalData["TiShouMgr"].removeTSItem( uid )
		playerBaseMB.client.removeTSItemFromQueryInterFace( uid )
		playerBaseMB.client.removeTSItem( uid, self.ownerDBID  )
		del self.tiShouItems[uid]

	def _addTSMoney( self, money ):
		"""
		"""
		self.tishouMoney += money
		BigWorld.globalData["TiShouMgr"].updateTSRecordMoney( self.ownerDBID, self.tishouMoney )



	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if cbID == DESTROY_CBID:
			BigWorld.globalData["TiShouMgr"].removeUnit( self.id )
			self.destroyCellEntity()
			BigWorld.lookUpBaseByName( "Role", self.ownerName, onSearchOwner )
			BigWorld.globalData["MailMgr"].sendWithMailbox( None, None, self.ownerName, 1, csdefine.MAIL_SENDER_TYPE_NPC, cschannel_msgs.FAMILY_INFO_2, cschannel_msgs.TI_SHOU_INFO_2, cschannel_msgs.TI_SHOU_INFO_3, 0, "" )


def onSearchOwner( playerBase ):
	"""
	"""
	if playerBase == True or playerBase == False:
		pass
	else:
		playerBase.cell.removeTSFlag()

def onNotifyGoodsSelled( goodsName, playerBase ) :
	"""
	物品卖出时通知卖家
	"""
	if playerBase == True or playerBase == False:
		pass
	else:
		playerBase.client.onStatusMessage( csstatus.TI_SHOU_PET_SELL_SUCCESS, str(( goodsName, )) )

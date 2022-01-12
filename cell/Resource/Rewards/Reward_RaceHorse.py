# -*- coding: gb18030 -*-

from Reward import Reward
import Language
import csdefine
import csconst
import csstatus
import items
from bwdebug import *
g_items = items.instance()
EXTRA_EXP_ITEM = 40501010	#额外经验 物品 ID
EXTRA_MONEY_ITEM = 40501011	#额外金钱 物品 ID


class Reward_RaceHorse( Reward ):
	"""
	赛马奖励
	"""
	def __init__( self ):
		"""
		只通过公式计算，没有表格
		"""
		self.type = csdefine.REWARD_RACE_HORSE
		Reward.__init__( self )


	def do( self, playerEntity ):
		"""
		1。(401.587*Lv^1.5+1058.730)*名次^-1.000
		2。金钱奖励=角色等级*(20-名次)^2.8（和经验奖励公式一样，因为单位是铜币，所以奖励的并不算多）
		"""
		pass

		place = playerEntity.query( "raceHorse_place", 0 )
		if place == 0:
			return
		
		if place <= 20:
			value = playerEntity.level*( 21 - place )**2.8
		else:
			value = playerEntity.level

		exp 	= csconst.ACTIVITY_GET_EXP( csdefine.ACTIVITY_SAI_MA, playerEntity.level, place )
		money 	= value

		count = playerEntity.queryRaceItemCount( EXTRA_MONEY_ITEM )
		money += int(money * 0.2 * count)

		count = playerEntity.queryRaceItemCount( EXTRA_EXP_ITEM )
		exp += int(exp * 0.2 * count)

		playerEntity.gainMoney( money, csdefine.CHANGE_MONEY_REWARD_RACEHORSE )
		playerEntity.addExp( exp, csdefine.CHANGE_EXP_RACEHORSE )

		INFO_MSG( "player %s(%i) place(%d) in raceHorse,win money(%d) and exp(%d)" % ( playerEntity.playerName, playerEntity.id, place, money, exp ) )

g_RH = Reward_RaceHorse()


class Reward_RaceHorse_Items( Reward ):
	"""
	赛马物品奖励
	"""
	def __init__( self ):
		"""
		"""
		self.rewardItemsDict = {}		# like: {名次:["物品1","物品2",...],...}
		self.type = csdefine.REWARD_RACE_HORSE_ITEMS
		Reward.__init__( self )
		self.sec = Language.openConfigSection( "" )

		for e in self.sec.values():
			rewardItems = e.readString( "rewardItems" )
			self.rewardItemsDict[e.readInt( "raceHorse_place" )] = rewardItems.split( ";" )

	def do( self, playerEntity ):
		"""
		奖励
		"""
		place = playerEntity.query( "raceHorse_place", 0 )
		if place == 0:
			playerEntity.statusMessage( csstatus.ROLE_RACE_NOT_PLACE )
			return

		rewardItemsList = []
		itemArray = []
		rewardItemsList = self.rewardItemsDict.get( place )		# 根据名次，取得奖励物品list
		
		if rewardItemsList is None:
			return
		for itemID in rewardItemsList:
			if itemID == '':
				continue
			item = g_items.createDynamicItem( int(itemID) , 1 )
			itemArray.append( item )

		if  playerEntity.checkItemsPlaceIntoNK_( itemArray ) == csdefine.KITBAG_NO_MORE_SPACE:
			playerEntity.statusMessage( csstatus.NPC_TRADE_SPACE_NOT_ENOUGH )
			return

		playerEntity.set( "raceHorse_place", 0 )

		for item in itemArray:
			playerEntity.addItem( item, csdefine.ADD_ITEM_RACEHORSE )

g_RH_Items = Reward_RaceHorse_Items()

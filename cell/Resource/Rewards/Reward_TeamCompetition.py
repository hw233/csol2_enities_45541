# -*- coding: gb18030 -*-

from Reward import Reward
import csdefine
import random
import Language
from LevelEXP import RoleLevelEXP as RLevelEXP
from items.ItemDropLoader import ItemDropInWorldLoader
import items
import ItemTypeEnum
from bwdebug import *
g_items = items.instance()
g_itemDropInWorld = ItemDropInWorldLoader.instance()


class Reward_TeamCompetition_Exp( Reward ):
	"""
	组队竞赛经验奖励
	该接口已废除，改为配置奖励工具管理 by 姜毅
	"""
	def __init__( self ):
		"""
		"""
		self.type = csdefine.REWARD_TEAMCOMPETITION_EXP
		self.sect = None
		Reward.__init__( self )


	def do( self, playerEntity ):
		"""
		"""
		if self.sect is None:
			return False
		l = playerEntity.getLevel() / 10
		c = playerEntity.queryTemp( "teamPlace" )

		if c > 10:
			# 这时说明没有产生第一名(比如玩家进去以后没有人死)，如果这种情况发生了
			# 就应该大家都没有奖励
			# 否则玩家排名会是默认的127而导致出错
			return False

		rate = self.sect[str(l) + "_" + str(c)]["r_param1"].asFloat

		playerEntity.addExp( RLevelEXP.getEXPMax( playerEntity.level ) * rate, csdefine.CHANGE_EXP_TEAMCOMPETITION )

		return True


class Reward_TeamCompetition_Items( Reward ):
	"""
	组队竞赛物品奖励
	"""
	def __init__( self ):
		"""
		"""
		self.type = csdefine.REWARD_TEAMCOMPETITION_ITEMS
		self.sect = Language.openConfigSection( "config/server/rewards/Reward_TeamCompetition_Items.xml" )
		self.dict = {}

		for iSect in self.sect.values():
			if iSect.name in self.dict:
				self.dict[iSect.name].append( ( iSect["r_param2"].asFloat , iSect["r_param1"].asString ) )
			else:
				self.dict[iSect.name] = [( iSect["r_param2"].asFloat , iSect["r_param1"].asString) ]

		Reward.__init__( self )


	def do( self, playerEntity ):
		"""
		"""
		if playerEntity.getNormalKitbagFreeOrderCount() < 1:
			return False

		l = str(playerEntity.getLevel() / 10 )

		tl = self.dict[str(l)]

		ra = random.random()

		g = 0
		j = ""

		for i in tl:
			g += i[0]
			if g > ra:
				j = i[1]
				break

		itemID = 0
		quality = 0

		if "-" in j:
			lev = random.randint( int(j.split(":")[0].split("-")[0]), int(j.split(":")[0].split("-")[0]) + 1 )

			rateList = g_itemDropInWorld.getDropItems( lev )

			for i in xrange( 0, 100):
				if type( rateList ) == type( [] ):
					rateList = random.choice( rateList )
				else:
					itemID = rateList[0]
					break
			quality = int( j.split(":")[1] )
		else:
			ls = j.split(";")
			if "" in ls:
				ls.remove("")
			itemID = int( random.choice( ls ) )

		if type( itemID ) == type( [] ) or type( itemID ) == type( () ):
			itemID = random.choice( itemID )[0]
		item = g_items.createDynamicItem( itemID , 1 )
		if item is None:
			ERROR_MSG( "TeamCompetition reward has no such item. %s" % itemID )
			return False
		if item.isEquip():
			if quality != 0:
				item.setQuality( quality )
				if quality == ItemTypeEnum.CQT_GREEN:
					preList = ItemTypeEnum.CPT_GREEN
				else:
					preList = ItemTypeEnum.CPT_NO_GREEN
				prefix = random.choice( preList )
				item.setPrefix( prefix )
				item.createRandomEffect()
		playerEntity.addItem( item, csdefine.ADD_ITEM_TEAMCOMPETITION )
		return True


g_TCRExp = Reward_TeamCompetition_Exp()
g_TCRItems = Reward_TeamCompetition_Items()
# -*- coding: gb18030 -*-
#
# $Id: MonsterDropManager.py

"""
管理怪物的死亡掉落
"""
import sys
import random
import BigWorld
import csdefine
import csconst
from bwdebug import *
from Love3 import g_rewards
from items.ItemDropLoader import SpecialDropLoader
g_SpecialDrop = SpecialDropLoader.instance()


class MonsterDropManager:
	"""
	怪物掉落的管理
	"""
	_instance = None

	def __init__( self ):
		pass

	def getDropItems( self, scriptMonster, monster ):
		"""
		获取掉落的物品列表
		@param scriptMonster : 怪物的脚本的实例
		@param monster       : 怪物entity实例
		注：列表中存放的直接是物品实例
		"""
		dropInfos = scriptMonster.getEntityProperty( "drops" )
		luckyDrop = scriptMonster.getEntityProperty( "luckyDropOdds" )

		itemDrops = []
		# 获得天降宝盒掉落
		luckyItemList = self.getLuckyBoxDropItems( monster )
		if luckyItemList:
			itemDrops.extend( luckyItemList )

		if dropInfos:
			for info in dropInfos:
				itemDrops.extend( self.dropItems( monster,info['dropType'],info['dropAmount'],info['dropOdds'] ) )
			if luckyDrop and random.random()*100 < luckyDrop:	# 如果触发大爆 那么再走一次掉落
				for info in dropInfos:
					itemDrops.extend( self.dropItems( monster,info['dropType'],info['dropAmount'],info['dropOdds'] ) )

		return itemDrops

	def getLuckyBoxDropItems( self, monster ):
		"""
		额外掉落
		"""
		itemList = []
		if not BigWorld.globalData.has_key("LuckyActivity"):
			return itemList
		dropKeys = BigWorld.globalData["LuckyActivity"]
		for dk, rewardID in dropKeys.iteritems():
			awarder = g_rewards.fetch( rewardID, monster )
			if not awarder is None:
				for item in awarder.items:
					item.set( "level", monster.level )
					itemList.append( item )
					DEBUG_MSG( "Lucky Drop(%s), item(%d)"%( dk, item.id ) )
		return itemList

	def getDropItemOwners( self, monster ):
		"""
		virtual method
		获取掉落物品拥有者
		@param monster: 与全局数据对应的继承于Monster的real Monster entity实例
		@type  monster: Monster
		@return :array of entityID, tuple like as [ entityID1,...]
		"""
		bootyOwner = monster.getBootyOwner()
		owners = []
		# 如果是宠物分配权在这里才转交给role 避免打乱宠物其他方面计算 如经验
		# 这段代码应该是兼容ghost的情况的
		# bootyOwner( entityID, TeamID )
		if bootyOwner[0] != 0:
			e = BigWorld.entities[ bootyOwner[0] ]
			if e.isEntityType( csdefine.ENTITY_TYPE_PET ) :
				owner = e.getOwner()
				e = owner.entity
				if owner.etype == "MAILBOX" :
					bootyOwner = ( e.id, 0 )
				elif e.isInTeam():
					bootyOwner = ( 0, e.getTeamMailbox().id )
				else:
					bootyOwner = ( e.id, 0 )

		if bootyOwner[0] != 0:
			owners = [ bootyOwner[0], ]
		if bootyOwner[1] != 0:
			members = monster.searchTeamMember( bootyOwner[1], 100 )
			if len( members ) == 0:
				owners = []
			elif len( members ) >= 1:
				entity = members[0]
				if entity.pickUpState == csdefine.TEAM_PICKUP_STATE_FREE:
					owners = entity.getFreePickerIDs()
				elif entity.pickUpState == csdefine.TEAM_PICKUP_STATE_ORDER:
					owners = [ entity.getOrderPickerID( members ) ]
					entity.onChangeLastPickerNotify( members, owners[0] )

		return owners

	def dropItems( self,monster,index,amount,odds ):
		"""
		获取怪物的掉落
		"""
		dropList = []
		datas = g_SpecialDrop.getDropDatas()		#获取特殊掉落的数据
		instance = datas.get(index, None)
		if not instance:
			ERROR_MSG( "has no special drop type : %s, please check out in SpecialDropAmend.xml" % index )
			return []
		for time in xrange( amount ):
			if random.random() < odds:
				item = instance.getDropItem( monster)
				if item is None:		#itemID为0表示没有找到该等级应该掉落的物品
					continue
				#owner = self.getDropItemOwners( monster )
				dropList.append( item )
		return dropList

	@classmethod
	def instance( self ):
		if self._instance == None:
			self._instance = MonsterDropManager()
		return self._instance
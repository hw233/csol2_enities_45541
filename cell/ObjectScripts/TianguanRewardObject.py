# -*- coding: gb18030 -*-
#
# $Id: TianguanObject.py,v 1.2 2008-08-20 01:23:53 zhangyuxing Exp $

from bwdebug import *
from items.ItemDropLoader import ItemDropInWorldLoader
import NPCObject
import ECBExtend
import BigWorld
import Language
import random
import items
import csdefine
import ItemTypeEnum
import sys

g_items = items.instance()
g_itemDropInWorld = ItemDropInWorldLoader.instance()

MEMBER_ITEMS_COUNT = 3
CREATOR_ITEMS_COUNT = 5


wieldTypeList = [ ItemTypeEnum.CEL_HEAD, \
				ItemTypeEnum.CEL_NECK, \
				ItemTypeEnum.CEL_BODY, \
				ItemTypeEnum.CEL_BREECH, \
				ItemTypeEnum.CEL_VOLA, \
				ItemTypeEnum.CEL_HAUNCH, \
				ItemTypeEnum.CEL_CUFF, \
				ItemTypeEnum.CEL_LEFTHAND, \
				ItemTypeEnum.CEL_FEET, \
				ItemTypeEnum.CEL_LEFTFINGER, \
				]


class TianguanRewardObject( NPCObject.NPCObject ):
	def __init__( self ):
		"""
		"""
		NPCObject.NPCObject.__init__( self )
		self.RewardSection = Language.openConfigSection("config/server/TianguanRewards.xml")

	def touch( self, selfEntity, player ):
		"""
		"""
		tempList = selfEntity.queryTemp( "reward_players", [] )
		if player.getName() not in tempList:
			self.dropRewardItemEntity( selfEntity, player )
			tempList.append( player.getName() )
			selfEntity.setTemp( "reward_players", tempList )

	def dropRewardItemEntity( self, selfEntity, player ):
		"""
		"""
		pos = selfEntity.position											# ���ﵱǰλ��
		spaceID = selfEntity.spaceID
		direction = selfEntity.direction
		tmpList = self.getRewardsItems( selfEntity, player )				# ����itemID
		tmpList = self.antiIndulgenceFilter( tmpList, player )				# ������ϵͳ����
		if len( tmpList ) == 0 : return

		# ��ʼ������
		itemsData = []
		for i in xrange( 0, len(tmpList), 2 ):
			tempD = tmpList[i]
			while type( tempD ) != type(0):
				tempD = random.choice( tempD )[0]

			itemID = tempD
			quality = tmpList[i+1]
			#x1, z1 = itemDistr.pop(0)										# ȡ��ƫ��λ��
			x1 = random.random() * 4 - 2
			z1 = random.random() * 4 - 2
			x, y, z = x1 + pos[0], pos[1], z1 + pos[2]						# ��������õ�λ��
			#print "position( %i, %i, %i ), itemID = %i" % ( x, y, z, e )
			# ӵ����
			propDict = { "ownerIDs": player }

			item = g_items.createDynamicItem( itemID , 1 )
			if item is None:
				ERROR_MSG( "Tianguan reward has no such item. %s" % itemID )
				return
			if quality != 0:
				item.setQuality( quality )
				if quality == ItemTypeEnum.CQT_GREEN:
					preList = ItemTypeEnum.CPT_GREEN
				else:
					preList = ItemTypeEnum.CPT_NO_GREEN
				prefix = random.choice( preList )
				item.setPrefix( prefix )
				item.createRandomEffect()

			itemsData.append( item )

			LOG_MSG( "NPCClass(%s), NPCName(%s), itemID(%s), itemName(%s), itemAmount(%i)"\
				%( selfEntity.className, selfEntity.getName(), item.id, item.name(), item.amount ) )

		print "------->>>>>>>>itemsData = ", itemsData
		teamMailbox = player.getTeamMailbox()
		teamID = 0
		if teamMailbox != None:
			teamID = player.getTeamMailbox().id
		bootyOwner = ( player.id, 0 )
		itemBox = BigWorld.createEntity( "DroppedBox", spaceID, ( x, y, z ), direction, {} )
		itemBox.init( bootyOwner, itemsData )

	def getRewardsItems( self, selfEntity, player ):
		"""
		"""
		if not selfEntity.queryTemp( "spaceLevel", 0 ):
			return []
		level = selfEntity.queryTemp( "spaceLevel" )
		rewardSectionList = []										#��¼�����ʺ���ε����section
		for i in self.RewardSection.values():
			levelRange = i['levelRange'].asString
			levels = levelRange.split('-')
			minLevel = int(levels[0])
			maxLevel = int(levels[1])
			if minLevel <= level and maxLevel >= level:
				rewardSectionList.append( i )

		itemCount = MEMBER_ITEMS_COUNT								#������Ʒ����Ŀ

		total = 0
		rewardRates = []
		for i in rewardSectionList:									#
			total += i['rate'].asInt
			rewardRates.append( total )

		itemList = []
		for k in xrange( 0, itemCount ):
			j = random.randint( 1, total+1)
			for i in rewardRates:
				if j <= i:
					itemsStr = rewardSectionList[rewardRates.index(i)]['items'].asString
					tempitemList = itemsStr.split(';')
					tempitemList.remove("")
					if len(tempitemList) == 1:						#װ������
						itemEquipData = tempitemList[0].split(':')
						if len( itemEquipData ) == 2:		#�޵��䲿λ ��ʽ 20-30:5;(npc�ȼ���Χ:Ʒ��;)
							levels = itemEquipData[0].split('-')
							minEquipLevel = levels[0]
							maxEquipLevel = levels[1]
							quality = int( itemEquipData[1] )
							eq_wieldType = random.choice( wieldTypeList )	#���һ�����䲿λ
							dropItemList = g_itemDropInWorld.getSpecialItem( quality, random.randint( int(minEquipLevel), int(maxEquipLevel) ), eq_wieldType )
							if dropItemList is not None:
								itemList.extend( [ dropItemList[0], quality ] )
						elif len( itemEquipData ) == 3:		#�е��䲿λ ��ʽ 20-30:5:2;(npc�ȼ���Χ:Ʒ��:��λ;)
							levels = itemEquipData[0].split('-')
							minEquipLevel = levels[0]
							maxEquipLevel = levels[1]
							quality = int( itemEquipData[1] )
							eq_wieldType = int( itemEquipData[2] )
							dropItemList = g_itemDropInWorld.getSpecialItem( quality, random.randint( int(minEquipLevel), int(maxEquipLevel) ), eq_wieldType )
							if dropItemList is not None:
								itemList.extend( [ dropItemList[0], quality ] )
						else:
							itemList.append( int( random.choice(tempitemList) ) )
							itemList.append( 0 )
					else:
						itemList.append(  int( random.choice(tempitemList) )  )
						itemList.append( 0 )
					break

		return itemList

	def antiIndulgenceFilter( self, itemsData, player ):
		"""
		������ϵͳ���˸��˵�����Ʒ����Ӳ��ܵĵ��䲻��Ӱ�죬Ӱ����Ƿ��䣩
		"""
		if player != None:
			gameYield = player.wallow_getLucreRate()
			print "------->>>>>gameYield = ", gameYield
			newData = []
			if gameYield >= 1.0:
				return itemsData
			elif itemsData == 0:
				return newData
			else:
				for i in itemsData:
					if random.random() <= gameYield:
						newData.append( i )
				return newData
		return itemsData
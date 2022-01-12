# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
from Function import Function
import time
import csdefine
import Language
import items
import csstatus
import sys

g_items = items.instance()

class FuncDartReward( Function ):
	"""
	����������ȡ����һ�ܽ���
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.param1 = section['param1'].asInt					#����ֵ
		self.rewardSection = Language.openConfigSection("config/server/DartRewards.xml")

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if player.iskitbagsLocked():	# ����������by����
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		currentWeak = ( int(time.time()) / (3600 * 24) + 3 ) / 7

		if player.dartRewardRecord != currentWeak:
			player.dartRewardRecord = currentWeak
			prestige = player.getPrestige( self.param1 )
			for index in xrange( len( self.rewardSection ) ):
				childSection = self.rewardSection.child( index )
				minPresitige = childSection.readInt( "minPresitige" )
				maxPresitige = childSection.readInt( "maxPresitige" )
				if prestige >= minPresitige and maxPresitige >= prestige:
					itemsStr = childSection.readString( 'items' )
					if  itemsStr != "":
						for i in itemsStr.split('|'):
							itemData = i.split(":")
							for i in range(0, int(itemData[1])):
								item = g_items.createDynamicItem( int(itemData[0]), 1 )
								player.addItem( item, csdefine.ADD_ITEM_DARTREWARD )

					player.addExp( childSection.readInt( 'exp' ), csdefine.CHANGE_EXP_DARTREWARD )
					player.gainMoney( childSection.readInt( 'money' ), csdefine.CHANGE_MONEY_DARTREWARD )
					return

			player.statusMessage( csstatus.ROLE_QUEST_DART_REWARD_NOT_ENOUGH_PRESITIGE )
		else:
			player.statusMessage( csstatus.ROLE_QUEST_DART_REWARD_HAS_GET )

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return player.getPrestige( self.param1 ) > 0


#
# $Log: not supported by cvs2svn $

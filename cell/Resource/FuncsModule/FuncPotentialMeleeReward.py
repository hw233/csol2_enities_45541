# -*- coding: gb18030 -*-
#
# $Id: FuncTeleport.py,v 1.16 2008-07-24 08:46:32 kebiao Exp $

"""
"""
from Function import Function
from bwdebug import *
import random
import math
import csstatus
import csdefine
import items
import time
import re
import sys
import csconst
import BigWorld

class FuncPotentialMeleeReward( Function ):
	"""
	Ǳ���Ҷ�����
	"""
	def __init__( self, section ):
		"""
		param1: spaceName
		param2: x, y, z
		param3: d1, d2, d3
		param4: radius

		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		pass


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
		# phw 20091212: ������룬�ڼ��˵�����£���Щ������п����޷���ȡ������
		# ԭ����tempMapping������cell_private�ģ���������NPC����ͬһ��cellapp�����޷���ȡ���ݣ�������쳣��
		rewardPlayers = talkEntity.queryTemp( "rewardPlayers" )
		rewardedPlayers = talkEntity.queryTemp( "rewardedPlayers" )
		if rewardedPlayers == None:
			rewardedPlayers = []
			talkEntity.setTemp( "rewardedPlayers", rewardedPlayers )
				
		DEBUG_MSG( "������ȡ��������:%s" % rewardPlayers )
		if not player.databaseID in rewardPlayers:
			if player.databaseID in rewardedPlayers:
				player.statusMessage( csstatus.POTENTIAL_MELEE_REWARD_NOT_FOUND )
			else:
				player.statusMessage( csstatus.POTENTIAL_MELEE_REWARD_NOT_FOUND1 )
			return

		item = items.instance().createDynamicItem( 60101004, 1 )
		item.set( "level", talkEntity.queryTemp( "playerLevel" ) )
		spaceLabel = BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY )
		
		if spaceLabel == "fu_ben_exp_melee":
			item.set( "aType", csdefine.ACTIVITY_JING_YAN_LUAN_DOU )
		else:
			item.set( "aType", csdefine.ACTIVITY_QIAN_NENG_LUAN_DOU )
			
		if player.checkItemsPlaceIntoNK_( [ item ] ) == csdefine.KITBAG_CAN_HOLD:
			player.addItemAndNotify_( item, csdefine.ADD_ITEM_POTENTIALMELEE )
			rewardPlayers.remove( player.databaseID )
			rewardedPlayers.append( player.databaseID )
			return
			
		player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )

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
		return True
#
# $Log: not supported by cvs2svn $
#

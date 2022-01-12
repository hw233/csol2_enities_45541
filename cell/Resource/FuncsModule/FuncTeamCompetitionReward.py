# -*- coding: gb18030 -*-
#

"""
"""
from Function import Function
import BigWorld
import csdefine
import time
import Language
import csstatus
from Resource.Rewards.RewardManager import g_rewardMgr

class FuncTeamCompetitionReward( Function ):
	"""
	��ȡ��Ӿ�������
	"""
	def __init__( self, section ):
		"""
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
		
		if not g_rewardMgr.rewards( player, csdefine.REWARD_TEAMCOMPETITION_ITEMS ):
			player.client.onStatusMessage( csstatus.KITBAG_IS_FULL, "" )
			return
		#player.addItem( player.createDynamicItem( self._itemID ) )
		player.setRoleRecord( "teamCompetitionWiner", "0" )
		

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��
		@return: True/False
		@rtype:	bool
		"""
		return False


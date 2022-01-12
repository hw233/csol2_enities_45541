# -*- coding: gb18030 -*-
#
# ��ȡ˫����������
#

from Function import Function
import BigWorld
import csdefine

class FuncMultiRewardQuest( Function ):
	"""
	��ȡ�������Ʒ
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.itemID = section.readInt( "param1" )
		self.questID = section.readInt( "param2" )
		self.multiRate = section.readInt( "param3" )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		item = player.findItemFromNKCK_( self.itemID )
		player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_CIFU )	# �Ƴ����������Ʒ
		player.setTemp( 'multi_rewards', 2 )
		player.questAcceptForce( player.id, self.questID, 0 )
		player.questsTable[self.questID].set( 'multi_rewards', self.multiRate )
		player.removeTemp( 'multi_rewards' )
		player.endGossip( talkEntity )
		

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
		item = player.findItemFromNKCK_( self.itemID )
		val1 = item is not None
		val2 = player.has_quest( self.questID )
		val3 = player.getQuest( self.questID ) is not None and player.getQuest( self.questID ).checkRequirement( player )
		return val1 and not val2 and val3
		
# -*- coding: gb18030 -*-
#created by dqh
# $Id: Exp $


from Function import Function
import BigWorld
import csdefine
import csstatus
from bwdebug import *

class FuncCompleteQuestWithItem( Function ):
	"""
	���ָ��������Ŀ����ٸ������һ����Ʒ
	"""
	def __init__( self, section ):
		"""
		@param param : ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param : pyDataSection
		"""
		Function.__init__( self, section  )
		
		self._itemID = section.readInt( "param1")			# ��ƷID
		self._questID = section.readInt( "param2" )			# ����ID
		self._taskIndex = section.readInt( "param3" )		# ����Ŀ������

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player     : ���
		@type  player     : Entity
		@param talkEntity : һ����չ�Ĳ���
		@type  talkEntity : entity
		@return           : None
		"""
		player.endGossip( talkEntity )
		
		#�����Ʒ
		item = player.createDynamicItem( self._itemID )
		if item is None:
			ERROR_MSG( "Player(%d):Item(%s) is none, quest(%s) can'be done" % ( player.id, str( self._itemID ), str( self._questID )) )
			return
		checkReult = player.checkItemsPlaceIntoNK_( [item] )
		if checkReult != csdefine.KITBAG_CAN_HOLD:
			player.statusMessage( csstatus.ROLE_QUEST_GET_FU_BI_CANNOT_GET_ITEM )
			return
		player.addItem( item, reason = csdefine.ADD_ITEM_QUEST )
		
		player.questTaskIncreaseState( self._questID, self._taskIndex )

	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��
		
		@param player		: ���
		@type  player		: Entity
		@param talkEntity	: һ����չ�Ĳ���
		@type  talkEntity	: entity
		@return				: True/False
		@rtype				: bool
		"""
		quest = player.getQuest( self._questID )
		return quest and quest.query( player ) == csdefine.QUEST_STATE_NOT_FINISH	#���������û�����
		

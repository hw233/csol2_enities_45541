# -*- coding: gb18030 -*-
#
"""
����ĶԻ� 2009-06-10 SongPeifang
"""

from bwdebug import *
import cschannel_msgs
import ShareTexts as ST
from Function import Function
from SkillTargetObjImpl import createTargetObjEntity
import csdefine
import csstatus

class FuncFishingForFree( Function ):
	"""
	�����ȡ����ʱ��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._p1 = section.readInt( "param1" )		# ÿ�ο�����ȡ��ʱ��
		self._p2 = section.readInt( "param2" )		# ÿ�������ȡ�Ĵ���
		self._p3 = section.readString( "param3" )	# ������ȡ�����Ķ԰�
		self._p4 = section.readInt( "param4" )		# ��ȡ����ʱ��ļ���ID

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		Function.do( self, player, talkEntity )

		if not player.fishingRecord.checklastTime():
			# ����һ���������ʱ����ȡ������¼
			player.fishingRecord.reset()

		if player.fishingRecord._degree >= self._p2:
			# ����ÿ����������ȡ�Ĵ�����
			player.setGossipText( self._p3 )
			player.sendGossipComplete( talkEntity.id )
			return

		target = createTargetObjEntity( player )
		if player.intonating():
			# ��������ͷż��ܵ�ʱ������ȡ
			player.setGossipText( cschannel_msgs.FISHING_VOICE_1 )
			player.sendGossipComplete( talkEntity.id )
			return

		talkEntity.spellTarget( self._p4, player.id )
		player.fishingRecord.incrDegree()
		minutes = self._p1 / 60
		player.setGossipText( cschannel_msgs.FISHING_VOICE_2 % minutes )
		player.sendGossipComplete( talkEntity.id )

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


class FuncFishingInCharge( Function ):
	"""
	���泡��������ȡ����ʱ��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._p1 = section.readInt( "param1" )		# ÿ�ο�����ȡ��ʱ��
		self._p2 = section.readInt( "param2" )		# ��ȡʱ��Ҫ����ƷID
		self._p3 = section.readInt( "param3" )		# ��ȡ����ʱ��ļ���ID

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		Function.do( self, player, talkEntity )

		item = player.findItemFromNKCK_( self._p2 )
		if not item:
			player.setGossipText( cschannel_msgs.FISHING_VOICE_3 )
			player.sendGossipComplete( talkEntity.id )
			return

		target = createTargetObjEntity( player )
		if player.intonating():
			# ��������ͷż��ܵ�ʱ������ȡ
			player.setGossipText( cschannel_msgs.FISHING_VOICE_1 )
			player.sendGossipComplete( talkEntity.id )
			return

		talkEntity.spellTarget( self._p3, player.id )
		player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_FISHINGINCHARGE )	# �Ƴ����������Ʒ
		minutes = self._p1 / 60
		player.setGossipText( cschannel_msgs.FISHING_VOICE_2 % minutes )
		player.sendGossipComplete( talkEntity.id )

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
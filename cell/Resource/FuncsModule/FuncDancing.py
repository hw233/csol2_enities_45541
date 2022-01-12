# -*- coding: gb18030 -*-

from bwdebug import *
from Function import Function
import csconst
import csstatus


class FuncDancePractice( Function ):
	"""
	��ϰ����
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		�Ի�ѡ����Ч�Լ��
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		if not player.queryTemp("danceType"):
			return True
		return False
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		�����Ի�ѡ��Ҫ��������
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		#DEBUG_MSG( "-->>rlt_askForStartAlly" )
		chellengeIndex = player.queryTemp("challengeIndex", 0)
		talkEntity.startDancePractice(chellengeIndex)
		player.endGossip( talkEntity )
		
class FuncDanceChallenge( Function ):
	"""
	��ս����
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		�Ի�ѡ����Ч�Լ��
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		if player.queryTemp("danceType"):
			return True
		return False
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		�����Ի�ѡ��Ҫ��������
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		#DEBUG_MSG( "-->>rlt_askForStartAlly" )
		chellengeIndex = player.queryTemp("challengeIndex", 0)
		if not chellengeIndex :
			ERRO_MSG("can't find challengeIndex in role %s"%player.playerName)
		talkEntity.startDanceChallenge(chellengeIndex)
		player.endGossip( talkEntity )

class FuncPlayAction( Function ):
	"""
	���Ŷ�����param1Ϊ���Ŷ�������ID��param2ΪҪ˵�Ļ�(Ϊ��ʱ��ֻ���Ŷ�������˵��)��˵������ͷ��������ʽ�������������ʾ��
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.param1 = section['param1'].asInt  #����ID���˼������Լ����Ŷ�����
		self.param2 = section['param2'].asString  #Ҫ˵�Ļ�
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		�Ի�ѡ����Ч�Լ��
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		�����Ի�ѡ��Ҫ��������
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		DEBUG_MSG( "DanceNPC dance and say!" )
		if self.param2:
			talkEntity.say(self.param2)
		talkEntity.planesOtherClients( "playAction", (self.param1,) )
		DEBUG_MSG( "DanceNPC dance and say over!" )
		player.endGossip( talkEntity )
		
class FuncQueryDanceExp(Function):
	"""
	��ѯ��ǰ��õ���������������
	"""
	def __init__( self, section ):
		Function.__init__( self, section )
		self.param1 = section['param1'].asInt  #0��ʾ��������ͨ���飬1Ϊ��������
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		�Ի�ѡ����Ч�Լ��
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):		
		"""
		Virtual method.
		�����Ի�ѡ��Ҫ��������
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""	
		BigWorld.globalData["DanceMgr"].queryDanceExp(player.playerName, player.base , self.param1, player.level)
		player.endGossip( talkEntity )
		
class FuncGetDanceExp(Function):
	"""
	��ѯ��ǰ��õ���������������
	"""
	def __init__( self, section ):
		Function.__init__( self, section )
		self.param1 = section['param1'].asInt   #0��ʾ��������ͨ���飬1Ϊ��������
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		�Ի�ѡ����Ч�Լ��
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):		
		"""
		Virtual method.
		�����Ի�ѡ��Ҫ��������
		
		@param player: ���entity
		@param talkEntity: npc entity
		"""	
		BigWorld.globalData["DanceMgr"].getDanceExp(player.playerName, player.base , self.param1, player.level)
		player.endGossip( talkEntity )	
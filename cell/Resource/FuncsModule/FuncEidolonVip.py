# -*- coding:gb18030 -*-

import csstatus
from Function import Function
import ECBExtend
from bwdebug import *
from Resource.QuestLoader import QuestsFlyweight
import csdefine

def checkVip( player, talkEntity, needVipLevel ):
	"""
	1�����player��talkEntity��owner����2
	2�����player��talkEntity owner�Ķ��ѣ���4
	3�����player vip�����Ƿ����ʹ�ô˹���
	4����鹲���vip�����Ƿ����ʹ�ô˹���
	"""
	if talkEntity.ownerID == player.id:
		if needVipLevel > player.vip:
			return csstatus.EIDOLON_VIP_LEVEL_LIMIT, ( needVipLevel, )
		return csstatus.EIDOLON_CAN_TALK_FUNCTION, ()
	else:
		teamMailbox = player.getTeamMailbox()
		if teamMailbox is not None and teamMailbox.id == talkEntity.ownerTeamID:	# player��ownerͬһ������
			if needVipLevel > talkEntity.shareVIPLevel:
				return csstatus.EIDOLON_VIP_LEVEL_LIMIT, ( needVipLevel, )
			else:
				return csstatus.EIDOLON_CAN_TALK_FUNCTION, ()
		return csstatus.EIDOLON_NOT_SAME_TEAM, ()
		
class VipFunction( Function ):
	"""
	vip���ܻ���
	"""
	def __init__( self, section ):
		"""
		param1���÷�����vip����;�Ƿ���1Ϊ����0Ϊ������
		"""
		Function.__init__( self, section )
		data = [ int( s ) for s in section.readString( "param1" ).split( ";" ) ]
		self.needVipLevel = data[0]	# ʹ�ô˹��������vip�ȼ�
		self.canShare = data[1]		# �Ƿ���Թ���
		
	def valid( self, player, talkEntity ):
		"""
		"""
		if talkEntity.ownerID == player.id:
			return True
		teamMailbox = player.getTeamMailbox()
		if teamMailbox is None:
			return False
		if teamMailbox.id != talkEntity.ownerTeamID:	# player��ownerͬһ������
			return False
		return True
		
class FuncVipTradeWithNPC( VipFunction ):
	"""
	vip���˽���
	"""
	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )
		if talkEntity is None:
			return
		statusID, paramTuple = checkVip( player, talkEntity, self.needVipLevel )
		if statusID != csstatus.EIDOLON_CAN_TALK_FUNCTION:
			player.statusMessage( statusID, *paramTuple )
			return
		if player.iskitbagsLocked():	# ����������by����
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		player.client.enterTradeWithNPC( talkEntity.id )
		
		
class FuncVipWarehouse( VipFunction ):
	"""
	Ǯׯvip����
	"""
	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )
		if talkEntity is None:
			return
		if player.iskitbagsLocked():	# ����������by����
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		statusID, paramTuple = checkVip( player, talkEntity, self.needVipLevel )
		if statusID != csstatus.EIDOLON_CAN_TALK_FUNCTION:
			player.statusMessage( statusID, *paramTuple )
			return
		player.client.enterBank( talkEntity.id )
		
		
class FuncVipMail( VipFunction ):
	"""
	�ʼ�vip����
	"""
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
		if talkEntity is None:
			return
		if player.iskitbagsLocked():	# ����������by����
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		statusID, paramTuple = checkVip( player, talkEntity, self.needVipLevel )
		if statusID != csstatus.EIDOLON_CAN_TALK_FUNCTION:
			player.statusMessage( statusID, *paramTuple )
			return
		player.client.enterMailWithNPC( talkEntity.id )
		
		
class FuncVipCheckConvert( VipFunction ):
	"""
	���vip��������vip������ת����Ӧ�ĶԻ�������رնԻ�
	"""
	def __init__( self, section ):
		"""
		"""
		VipFunction.__init__( self, section )
		self._functionName = section.readString( "param2" )		# �������������ĶԻ����ܱ�ǩ
		
	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )
		if talkEntity is None:
			return
		statusID, paramTuple = checkVip( player, talkEntity, self.needVipLevel )
		if statusID != csstatus.EIDOLON_CAN_TALK_FUNCTION:
			player.statusMessage( statusID, *paramTuple )
			return
		player.setTemp( "talkID", self._functionName )
		player.setTemp( "talkNPCID", talkEntity.id )
		player.addTimer( 0.2, 0, ECBExtend.AUTO_TALK_CBID )
		
		
class FuncVipAcceptQuest( Function ):
	"""
	ͨ���Ի���������
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.questID = section.readInt( "param1" )
		
	def do( self, player, talkEntity = None ):
		"""
		"""
		quest = QuestsFlyweight.instance()[self.questID]
		state = quest.query( player )
		if state != csdefine.QUEST_STATE_NOT_HAVE:
			INFO_MSG( "can't accept quest %i, state = %i." % ( self.questID, state ) )
			player.statusMessage( csstatus.EIDOLON_CANT_ACCEPT_QUEST )
			return
		quest.accept( player )
		
	def valid( self, player, talkEntity = None ):
		"""
		"""
		return True
		
class FuncWithdrawEidolon( Function ):
	"""
	����С����
	"""
	def valid( self, player, talkEntity ):
		"""
		"""
		if talkEntity.ownerID == player.id:
			return True
		return False
		
	def do( self, player, talkEntity ):
		"""
		"""
		player.withdrawEidolon( player.id )
		
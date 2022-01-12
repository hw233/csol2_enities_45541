# -*- coding:gb18030 -*-

import csstatus
from Function import Function
import ECBExtend
from bwdebug import *
from Resource.QuestLoader import QuestsFlyweight
import csdefine

def checkVip( player, talkEntity, needVipLevel ):
	"""
	1、如果player是talkEntity的owner，则2
	2、如果player是talkEntity owner的队友，则4
	3、检查player vip级别是否可以使用此功能
	4、检查共享的vip级别是否可以使用此功能
	"""
	if talkEntity.ownerID == player.id:
		if needVipLevel > player.vip:
			return csstatus.EIDOLON_VIP_LEVEL_LIMIT, ( needVipLevel, )
		return csstatus.EIDOLON_CAN_TALK_FUNCTION, ()
	else:
		teamMailbox = player.getTeamMailbox()
		if teamMailbox is not None and teamMailbox.id == talkEntity.ownerTeamID:	# player和owner同一个队伍
			if needVipLevel > talkEntity.shareVIPLevel:
				return csstatus.EIDOLON_VIP_LEVEL_LIMIT, ( needVipLevel, )
			else:
				return csstatus.EIDOLON_CAN_TALK_FUNCTION, ()
		return csstatus.EIDOLON_NOT_SAME_TEAM, ()
		
class VipFunction( Function ):
	"""
	vip功能基类
	"""
	def __init__( self, section ):
		"""
		param1配置方法：vip级别;是否共享。1为共享，0为不共享。
		"""
		Function.__init__( self, section )
		data = [ int( s ) for s in section.readString( "param1" ).split( ";" ) ]
		self.needVipLevel = data[0]	# 使用此功能所需的vip等级
		self.canShare = data[1]		# 是否可以共享
		
	def valid( self, player, talkEntity ):
		"""
		"""
		if talkEntity.ownerID == player.id:
			return True
		teamMailbox = player.getTeamMailbox()
		if teamMailbox is None:
			return False
		if teamMailbox.id != talkEntity.ownerTeamID:	# player和owner同一个队伍
			return False
		return True
		
class FuncVipTradeWithNPC( VipFunction ):
	"""
	vip商人交易
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
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		player.client.enterTradeWithNPC( talkEntity.id )
		
		
class FuncVipWarehouse( VipFunction ):
	"""
	钱庄vip功能
	"""
	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )
		if talkEntity is None:
			return
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		statusID, paramTuple = checkVip( player, talkEntity, self.needVipLevel )
		if statusID != csstatus.EIDOLON_CAN_TALK_FUNCTION:
			player.statusMessage( statusID, *paramTuple )
			return
		player.client.enterBank( talkEntity.id )
		
		
class FuncVipMail( VipFunction ):
	"""
	邮件vip功能
	"""
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if talkEntity is None:
			return
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		statusID, paramTuple = checkVip( player, talkEntity, self.needVipLevel )
		if statusID != csstatus.EIDOLON_CAN_TALK_FUNCTION:
			player.statusMessage( statusID, *paramTuple )
			return
		player.client.enterMailWithNPC( talkEntity.id )
		
		
class FuncVipCheckConvert( VipFunction ):
	"""
	检测vip级别，满足vip条件则转到相应的对话，否则关闭对话
	"""
	def __init__( self, section ):
		"""
		"""
		VipFunction.__init__( self, section )
		self._functionName = section.readString( "param2" )		# 满足条件触发的对话功能标签
		
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
	通过对话接受任务
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
	回收小精灵
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
		
# -*- coding: gb18030 -*-

from SpaceCopy import SpaceCopy
import csconst
import time
import BigWorld
import csdefine
import cschannel_msgs
import Love3


class SpaceCopyRabbitRun( SpaceCopy ):
	"""
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		self.winers = []
		self.addTimer( BigWorld.globalData["AS_RabbitRun_Start_Time"] - time.time() - csconst.RABBIT_RUN_TIME_TO_CHANGE_BODY, 0.0, 100001 )
		self.addTimer( BigWorld.globalData["AS_RabbitRun_Start_Time"] - time.time() - csconst.RABBIT_RUN_CANT_ENTER_TIME, 0.0, 100004 )
		self.addTimer( csconst.RABBIT_RUN_ACTIVITY_TIME, 0.0, 100003 )

	
	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceCopy.onTimer( self, id, userArg )
		
		k = 0
		if userArg == 100001:
			for i in self._players.values():
				k += 1
				if k % csconst.RABBIT_RUN_WOLF_CONTROL_NUM == 0:
					i.cell.remoteCall( "changeToWolf", () )
				else:
					i.cell.remoteCall( "changeToRabbit", () )
			if len( self._players ) < csconst.RABBIT_RUN_NEED_PLAYER_AMOUNT:
				for i in self._players.values():
					i.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.MID_AUTUMIN_RABBIT_RUN_PLAYER_NOT_ENOUGH, [] )
				self.addTimer( 20, 0.0, 100002 )
		if userArg == 100002:
			for i in self._players.values():
				i.cell.gotoForetime()
		if userArg == 100003:
			for i in self._players.values():
				i.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.MID_AUTUMIN_RABBIT_RUN_OVER_FOR_TIME, [] )
			self.addTimer( 20, 0.0, 100002 )
		if userArg == 100004:
			BigWorld.globalData["ActivityBroadcastMgr"].onMidAutumnRabbitRunEnd()
		

	def onArriveDestination( self, playerName, mailbox ):
		"""
		"""
		self.winers.append( mailbox.id )
		if len( self.winers ) <= 30:						#30名以内都算作胜利
			mailbox.cell.winInRabbitRun( len( self.winers ) )
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.MID_AUTUMIN_RABBIT_RUN_CELEBRATE %( playerName,len( self.winers )  ), [] )
		else:
			for i in self._players.values():
				i.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.MID_AUTUMIN_RABBIT_RUN_OVER_FOR_WIN, [] )
			self.addTimer( 20, 0.0, 100002 )



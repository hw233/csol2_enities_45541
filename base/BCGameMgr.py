# -*- coding: gb18030 -*-
#
# 变身大赛管理器 2009-01-17 SongPeifang
#
import Love3
import csdefine
import BigWorld
import cschannel_msgs
from bwdebug import *
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from MsgLogger import g_logger

BC_GAME_LOGIN	= 0					# 变身大赛开始报名
BC_GAME_BEGIN	= 1					# 变身大赛正式开始
BC_GAME_RELOAD	= 2					# 变身大赛结束活动
LOIN_TIME		= 600				# 变身大赛报名时间限制为10分钟

class BCGameMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.registerGlobally( "BCGameMgr", self._onRegisterManager )
		self._loginTime		= LOIN_TIME	# 从报名到活动开始的等待时间为300秒
		self._competitorCount = {}		# 参加变身大赛的人数
		self._canLogin		= False		# 允许报名参加变身大赛
		self.BCNPCs			= {}		# 所有的变身NPC

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register BCGameMgr Fail!" )
			self.registerGlobally( "BCGameMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["BCGameMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("BCGameMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"BCGameMgr_start_notice" : "onStartNotice",
						"BCGameMgr_end" : "onEnd",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )

	def registerBCNPC( self, lineNumber, baseMailbox ):
		"""
		define method.
		注册每条线的BCNPC
		"""
		self.BCNPCs[ lineNumber ] = baseMailbox

	def onStartNotice( self ):
		"""
		define method.
		活动开始通知
		"""
		self._loginTime = LOIN_TIME				# 比赛开始后要恢复至10分钟
		self.onTimer( 0, BC_GAME_LOGIN )
		INFO_MSG( "BCGameMgr.", "notice", "" )

	def onTimer( self, id, userArg ):
		"""
		通知所有玩家变身大赛开始
		"""
		if userArg == BC_GAME_LOGIN:
			# 开始发出变身大赛的公告
			leftLoginTime = int( int( self._loginTime ) / 60 )
			if self._loginTime > 0 and leftLoginTime in [ 10, 5, 3, 1 ]:
				# 变身大赛在10分，5分、3分、1分钟时均要发公告
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BSDS_PREPARE_NOTIFY % leftLoginTime, [] )
			self.changeLoginState( True )
			if self._loginTime <= 0:
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BSDS_BEGIN_NOTIFY, [] )
				self.addTimer( 5, 0, BC_GAME_BEGIN )	# 变身大赛5秒之后开始！
				self.changeLoginState( False )			# 此时不再允许报名了
			else:
				self.addTimer( 60, 0, BC_GAME_LOGIN )
			self._loginTime -= 60

		elif userArg == BC_GAME_BEGIN:
			# 变身大赛开始！
			self.onGameBegin()

	def onGameBegin( self ):
		"""
		变身大赛开始
		"""
		hasMembers = False
		for competitorCount in self._competitorCount.itervalues():
			if competitorCount > 0:
				hasMembers = True
		if not hasMembers:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BSDS_END_NO_PARTICIPANT, [] )

		if len( self.BCNPCs ) <= 0:
			ERROR_MSG( "未知错误，找不到变身大赛的NPC,可能还未被创建。" )
			return

		for lineNumber, bcNPCMailBox in self.BCNPCs.iteritems():
			if self._competitorCount.get( lineNumber, 0 ) <= 0:
				continue
			bcNPCMailBox.cell.bcGameStart()
			self.setMemberCount( lineNumber, 0 )	# 参赛人数在这里又置回0了

		try:
			g_logger.actStartLog( csdefine.ACTIVITY_BIAN_SHEN_DA_SAI )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def setMemberCount( self, lineNumber, count ):
		"""
		Define Method.
		设置报名人数
		"""
		self._competitorCount[ lineNumber ] = count

	def changeLoginState( self, canLogin ):
		"""
		设置是否可以报名
		"""
		self._canLogin = canLogin
		for lineNumber, bcNPCMailBox in self.BCNPCs.iteritems():
			bcNPCMailBox.cell.getLoginState( canLogin )

	def onEnd( self ):
		"""
		define method.
		活动结束
		"""
		self._loginTime = LOIN_TIME				# 比赛结束后要恢复至10分钟
		INFO_MSG( "BCGameMgr.", "end", "" )
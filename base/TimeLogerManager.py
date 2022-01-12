# -*- coding: gb18030 -*-
#
"""
定时日志任务
"""
import BigWorld
import ShareTexts as ST
import Const
import time
import csdefine
from MsgLogger import g_logger
from bwdebug import *

class TimeLogerManager(BigWorld.Base):
	"""
	定时日志任务
	"""
	def __init__( self ):
		"""
		初始化
		"""
		self.registerGlobally( "TimeLogerManager", self._onRegisterManager )		#注册自己到全局中

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register TimeLogerManager Fail!" )
			self.registerGlobally( "TimeLogerManager", self._onRegisterManager )
		else:
			BigWorld.globalData["TimeLogerManager"] = self		# 注册到所有的服务器中
			INFO_MSG("TimeLogerManager Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"* * * * *" : "playerCount",			#每分钟统计一次人数   * * * * * 分 时 日 月 周
						"1 * * * *" : "log_wealthRanking",		#每小时统计一次财富
						#"0 0 * * *" : "log_classlevelRanking",	#每天统计一次职业和等级
						"0 0 * * *" : "log_tongRanking",		#帮会统计信息
						"0 0 * * *" : "updateRanking",			#每天统计一次玩家的等级排名
					  }

		for cmd, callbackName in taskEvents.iteritems():
			BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )

	def playerCount( self ):
		"""
		@define method
		统计玩家的在线人数
		"""
		waitAcountNum = 0
		loginAcountNum = 0
		totalPlayerNum = 0
		for key, value in BigWorld.baseAppData.items():
			if isinstance( key, str ):
				if key.startswith( Const.PREFIX_GBAE_WAIT_NUM ):
					waitAcountNum += value
				elif key.startswith( Const.PREFIX_GBAE_LOGIN_NUM ):
					loginAcountNum += value
				elif key.startswith( Const.PREFIX_GBAE_PLAYER_NUM ):
					totalPlayerNum += value
		# 写入在线玩家的日志
		try:
			g_logger.countRoleLog( waitAcountNum, loginAcountNum, totalPlayerNum )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )


	def log_wealthRanking( self ):
		"""
		@define method
		财富统计
		"""
		sql = "select id, sm_playerName, sm_money from tbl_Role order by sm_money desc limit %s" % Const.WEALTH_RANKING_NUM
		BigWorld.executeRawDatabaseCommand( sql, self.onGetWealthDatas )

	def onGetWealthDatas( self, results, rows, errstr ):
		"""
		当获取了财富排名
		"""
		if errstr:
			ERROR_MSG( "get wealth ranking failed: %s" % errstr  )
			return
		if not results:
			return False
		now = time.time()
		for result in results:
			dbid 		= result[0]
			playerName	= result[1]
			money		= result[2]
			try:
				g_logger.countWealthLog( dbid, playerName, money, now )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

	def log_classlevelRanking( self ):
		"""
		@define method
		等级和职业分布统计
		"""
		sql = "select sm_level,sm_raceclass,count( sm_raceclass ) from tbl_Role group by sm_level, sm_raceclass & 0xf0"
		BigWorld.executeRawDatabaseCommand( sql, self.onGetClassLevelDatas )

	def onGetClassLevelDatas( self, results, rows, errstr ):
		"""
		当获取了职业和等级的数据
		"""
		if errstr:
			ERROR_MSG( "get classlevel ranking failed: %s" % errstr  )
			return
		if not results:
			return False
		datas = {}
		now = time.time()
		for result in results:
			level 		= int(result[0])
			raceclass	= int(result[1])&csdefine.RCMASK_CLASS
			num			= int(result[2])
			msg = "%s:%s " % ( raceclass, num )
			if not datas.has_key(level):
				datas[level] = msg
			else:
				datas[level] += msg
		for key,values in datas.iteritems():
			try:
				g_logger.countLevelLog( key, values, now )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

	def log_tongRanking( self ):
		"""
		@define method
		帮会统计信息
		"""
		sql =	""" select c.id,c.sm_playerName,c.sm_level,c.sm_money,count(a.sm_level),sum(a.sm_level)/count(a.sm_level),
					max(a.sm_level),min(a.sm_level) from tbl_Role as a,(select b.id,b.sm_money,b.sm_playerName,b.sm_level
					from tbl_TongEntity as b) as c where a.sm_tong_dbID = c.id group by a.sm_tong_dbID;"""

		BigWorld.executeRawDatabaseCommand( sql, self.onGetTongInfos )

	def onGetTongInfos( self, results, rows, errstr ):
		"""
		获取了成员的DBID
		"""
		if errstr:
			ERROR_MSG( "get tong member level ranking failed: %s" % errstr  )
			return
		if not results:
			return
		for result in results:
			try:
				g_logger.countTongInfoLog( result[1],result[2],result[3],result[4],int(float(result[5])),result[6],result[7] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

	def updateRanking( self ):
		"""
		等级排行榜记录
		"""
		BigWorld.executeRawDatabaseCommand( "call UPDATERANKING()", self.onGetRankingDatas )

	def onGetRankingDatas( self, results, rows, errstr):
		"""
		获取了排名数据
		"""
		if errstr:
			ERROR_MSG( "update ranking failed, please check the mysql Stored Procedure is correct: %s" % errstr  )
			return
		BigWorld.baseAppData["GameRankingManager"].LoadRankingDatas()			# 通知排行榜更新数据


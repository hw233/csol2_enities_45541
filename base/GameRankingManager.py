# -*- coding: gb18030 -*-
#

import BigWorld
import Const
import csconst
import time
from bwdebug import *


class GameRankingManager( BigWorld.Base ):
	"""
	游戏排行榜接口
	"""
	def __init__( self ):
		"""
		初始化 获取所有的数据
		"""
		self.registerGlobally( "GameRankingManager", self._onRegisterManager )		#注册自己到全局中
		self.rankings 		= {}													#数据
		self.updateTime		= 0														#数据更新的时间
		self.oldrankings	= {}													#旧数据
		self.newflag = False
		self.oldflag = False		



	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register GameRankingManager Fail!" )
			self.registerGlobally( "GameRankingManager", self._onRegisterManager )
		else:
			BigWorld.baseAppData["GameRankingManager"] = self		# 注册到所有的服务器中
			INFO_MSG("GameRankingManager Create Complete!")
			self.LoadRankingDatas()									# 启动完毕 去加载所有的排行数据

	def LoadRankingDatas( self ):
		"""
		加载所有的排名数据
		"""
		self.newflag = False
		self.oldflag = False
		def onGetDatas(results, rows, errstr):
			"""
			获取了排名数据
			"""
			if errstr:
				ERROR_MSG( "get player level ranking failed: %s" % errstr  )
				return
			if not results:
				return
			self.rankings = {}
			for result in results:
				if self.rankings.has_key( int(result[0]) ):
					self.rankings[ int(result[0]) ].append(result[1:])
				else:
					self.rankings[ int(result[0]) ] = [result[1:] ]
			self.updateTime = int(time.time())							# 更新数据刷新的时间
			INFO_MSG("update Ranking List time is %s ,rankDatas = %s"%(str(self.updateTime), self.rankings))
			self.newflag = True
			if self.newflag and self.oldflag:
				calSort()
				
		def onGetOldDatas( results, rows, errstr ):
			if errstr:
				ERROR_MSG( "get player level ranking failed: %s" % errstr  )
				return
			if not results:
				return
			self.oldrankings = {}
			for result in results:
				if self.oldrankings.has_key( int(result[0]) ):
					self.oldrankings[ int(result[0]) ].append(result[1:])
				else:
					self.oldrankings[ int(result[0]) ] = [result[1:] ]	
			self.oldflag = True	
			if self.newflag and self.oldflag:
				calSort()

		def calSort():
			print "calSort()",self.newflag, self.oldflag
			for key, value in self.rankings.items():
				newindex = 1
				for item in value:
					playername = item[1]
					oldindex = getIndex(key, playername)
					if oldindex:
						self.rankings[key][newindex - 1][0] = oldindex - newindex
					else:
						self.rankings[key][newindex - 1][0] = len(self.rankings[key]) + 1 - newindex
					newindex += 1			
		
		def getIndex( type ,playername):
			playernamelist = [item[1] for item in self.oldrankings[type]]
			if type in self.oldrankings.keys() and self.oldrankings[type] is not None:
				playernamelist = [item[1] for item in self.oldrankings[type]]
				if playername in playernamelist:
					return playernamelist.index(playername) + 1
			elif type in self.oldrankings.keys():
				return len(self.oldrankings[type]) + 1
			else:
				return len(self.rankings[type]) + 1
		
		sqlnew = "select type,param1,param2,param3,param4,param5,param6 from custom_Ranking order by id ASC"
		BigWorld.executeRawDatabaseCommand( sqlnew, onGetDatas )
		sqlold = "select type,param1,param2,param3,param4,param5,param6 from custom_oldRanking order by id ASC"
		BigWorld.executeRawDatabaseCommand( sqlold, onGetOldDatas )


	def getRankingDatas( self, rtype ):
		"""
		获取排名的数据
		@type  rtype:UINT8
		@param rtype:数据的类型
		"""
		try:
			return self.rankings[rtype]
		except:
			return []

	def getRankingDatasEx( self, rtype, begin, num ):
		"""
		获取排名的数据 可以指定开始的数据和条数
		@type  rtype:int
		@param rtype:数据的类型
		@type  begin:int
		@param begin:开始的索引
		@type    num:int
		@param   num:数量
		"""
		try:
			return self.rankings[rtype][begin:begin+num]
		except:
			return []

	def showGameRanking( self, role ):
		"""
		@define method
		通知玩家客户端接收数据
		@type  role : mailbox
		@param role : 玩家的mailbox
		"""
		role.client.onShowGameRanking( self.updateTime )

	def queryRankingData( self, role, rankingType, beginIndex  ):
		"""
		@define method
		通知玩家客户端接收数据
		@type  role : mailbox
		@param role : 玩家的mailbox
		@type  rankingType: UINT8
		@param rankingType: 数据的类型 如 帮会排行数据
		@type  beginIndex : UINT8
		@param beginIndex : 数据发送的起始位置
		"""
		datas = self.getRankingDatasEx(rankingType, beginIndex, csconst.GAMERANKING_SEND_DATANUM )
		if not datas:
			role.client.onQueryRankingEnd( rankingType )
		else:
			role.client.onQueryRankingData( rankingType,beginIndex,datas )

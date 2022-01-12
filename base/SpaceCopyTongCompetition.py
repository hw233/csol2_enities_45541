# -*- coding: gb18030 -*-

import BigWorld
from SpaceCopy import SpaceCopy
import csstatus
import csdefine
import time
import Love3
import cschannel_msgs
import RoleMatchRecorder
from bwdebug import *


class SpaceCopyTongCompetition( SpaceCopy ):
	"""
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		self.tongInfos = {}
		self.tongScoreInfos = {} # 用于积分界面

	def onEnter( self, baseMailbox, params ):
		"""
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
		tongDBID = params["tongDBID"]
		tongName = params["tongName"]
		timeNum = int( time.time() )

		if tongDBID in self.tongInfos:
			self.tongInfos[ tongDBID ][-1].append( baseMailbox )
			self.tongScoreInfos[ tongDBID ][-1].append( baseMailbox )
		else:
			self.tongInfos[ tongDBID ] = [ tongName, 0, 1, timeNum, [ baseMailbox ] ]		# 字典如{ tongDBID:[tongName,TongScore,amount,timeNum,[basemailbox1,...]] }
			self.tongScoreInfos[ tongDBID ] = [ tongName, 0, 1, timeNum, [ baseMailbox ] ]		

		#通知TongCompetitionMgr
		tongCompetitionMgr = BigWorld.globalData["TongCompetitionMgr"]
		tongCompetitionMgr.onEnterSpace(self, baseMailbox, tongDBID)

	def onLeave( self, baseMailbox, params ):
		"""
		"""
		SpaceCopy.onLeave( self, baseMailbox, params )

		#通知TongCompetitionMgr
		tongCompetitionMgr = BigWorld.globalData["TongCompetitionMgr"]
		tongCompetitionMgr.onLevelSpace(self, baseMailbox)

		playerDBID = BigWorld.globalData[ "tongComPlayerDBID" ]
		for dbid in self.tongScoreInfos:
			for k in self.tongScoreInfos[ dbid ][ -1 ]:
				if k.id == baseMailbox.id:
					tongScore = self.tongScoreInfos[ dbid ][ 1 ]
					RoleMatchRecorder.update( playerDBID, csdefine.MATCH_TYPE_TONG_COMPETITION, tongScore, None )		# 记录比赛日志
					INFO_MSG( "tongCompetition:playerDBID = %i tongScore = %i" % ( playerDBID, tongScore ) )

		for i in self.tongInfos:
			if baseMailbox in self.tongInfos[ i ][ -1 ]:
				amount = len( self.tongInfos[ i ][ -1 ] )
				amount -= 1
				self.tongInfos[ i ][ 2 ] = amount
			membersMailbox = self.tongInfos[ i ][ -1 ]
			for j in membersMailbox:
				if j.id == baseMailbox.id:
					self.tongInfos[ i ][ -1 ].remove(j)
					if len( self.tongInfos[ i ][ -1 ] ) == 0:
						self.tongInfos.pop(i)
					return

	def onRoleDied( self, roleID, roleTongDBID, killerID, killerTongDBID ):
		"""
		define method
		"""
		if killerTongDBID in self.tongInfos:
			self.tongInfos[ killerTongDBID ][ 1 ] += 1		# 帮会竞技积分+1
			self.tongScoreInfos[ killerTongDBID ][ 1 ] += 1		
			membersMailbox = self.tongInfos[ killerTongDBID ][ -1 ]		# 副本内的帮会玩家mailbox
			for i in membersMailbox:
				if i.id != killerID:		# 同帮会的其他人积分也要+1
					i.cell.addTongScore( 1 )
					i.client.onStatusMessage( csstatus.TONG_COMPETITION_ADD_TONGSCORE, "" )

	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT = None
		"""

		baseMailbox.logonSpaceInSpaceCopy()

	def queryTongWinner( self ):
		"""
		define method
		"""
		self.cell.onQueryTongWinner( self.getTongWinner() )


	def getTongWinner( self ):
		"""
		时间到了，判断冠军
		"""
		if len( self.tongInfos ) == 1:				# 副本只剩一个帮会的情况
			tongDBID = self.tongInfos.keys()[ 0 ]
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TONGCOMPETITION_WINNER % self.tongInfos[ tongDBID ][ 0 ], [] )
			return tongDBID

		def func( item1, item2 ):
			if item1[1] == item2[1] and item1[2] == item2[2]:		# 如果积分和人数都相等时，则按照生成时间的先后进行判断
				return -cmp( item1[3], item2[3] )
			if item1[1] == item2[1]:		# 如果只是积分相等时，则按照在场的帮会人数进行判断
				return cmp( item1[2], item2[2] )
			return cmp( item1[1], item2[1] )		# 首先判断哪个帮会的积分最高

		tongInfoList = self.tongInfos.values()
		tongInfoList.sort( cmp = func, reverse = True )
		tongName = tongInfoList[0][0]
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TONGCOMPETITION_WINNER % tongName, [] )
		for tongDBID in self.tongInfos.keys():
			if self.tongInfos[ tongDBID ][ 0 ] == tongName:
				return tongDBID


	def notifyTongWinner( self ):
		"""
		define method.
		"""
		if len( self.tongInfos ) == 1:				# 副本只剩一个帮会的情况
			tongDBID = self.tongInfos.keys()[ 0 ]
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TONGCOMPETITION_WINNER % self.tongInfos[ tongDBID ][ 0 ], [] )

	def queryTongCompInfo( self, baseMailbox ):
		"""
		define method
		获取帮会竞技的排名情况，用于界面
		"""
		if len( self.tongInfos ) == 1:				# 副本只剩一个帮会的情况
			tongDBID = self.tongInfos.keys()[ 0 ]
			tongName = self.tongInfos[ tongDBID ][ 0 ]
			tongInfoList = self.tongInfos.values()

		def func( item1, item2 ):
			if item1[1] == item2[1] and item1[2] == item2[2]:		# 如果积分和人数都相等时，则按照生成时间的先后进行判断
				return -cmp( item1[3], item2[3] )
			if item1[1] == item2[1]:		# 如果只是积分相等时，则按照在场的帮会人数进行判断
				return cmp( item1[2], item2[2] )
			return cmp( item1[1], item2[1] )		# 首先判断哪个帮会的积分最高

		for tongDBID in self.tongScoreInfos:
			tongInfoList = self.tongScoreInfos.values()
			tongInfoList.sort( cmp = func, reverse = True )

			index = 0
			for i in tongInfoList:
				tongName = i[0]
				tongScore = i[1]
				index += 1
				if self.tongScoreInfos[ tongDBID ][ 0 ] == tongName:
					baseMailbox.client.onTongCompetitionInfo( tongDBID, tongName, tongScore, index )

		baseMailbox.client.updataTongCompetitionInfo()

	def removePlayer( self, baseMailbox ):
		"""
		define method.
		"""
		# 字典如{ tongDBID:[tongName,TongScore,amount,timeNum,[basemailbox1,...]] }
		for i in self.tongInfos:
			membersMailbox = self.tongInfos[ i ][ -1 ] 
			for j in membersMailbox:
				if j.id == baseMailbox.id:
					self.tongInfos[ i ][ -1 ].remove(j)
					if len( self.tongInfos[ i ][ -1 ] ) == 0:
						self.tongInfos.pop(i)
					return


# -*- coding: gb18030 -*-


import time
from SpaceCopy import SpaceCopy
import cschannel_msgs
import ShareTexts as ST
import Love3
import csdefine
import BigWorld

INIT_PLACE = 127				#初始化的排名

class SpaceCopyTeamCompetition( SpaceCopy ):
	"""
	"""
	def __init__(self):
		SpaceCopy.__init__( self )

		"""
		组织好组队竞赛的数据
		"""
		self.teamInfo = {}
		self.firstPlaceTeamID 	= 0														#第一名队伍ID
		self.lastPlace		 	= INIT_PLACE											#最后一个排名， INIT_PLACE不算
		self.copyLevel			= 0


	def onEnter( self, baseMailbox, params ):
		"""
		"""
		self.newComer( baseMailbox, params )
		SpaceCopy.onEnter( self, baseMailbox, params )
		if self.copyLevel == 0:
			self.copyLevel = params["copyLevel"]

	def onLeave( self, baseMailbox, params ):
		"""
		"""
		self.newLeaver( baseMailbox, params )
		SpaceCopy.onLeave( self, baseMailbox, params )

	def newComer( self, baseMailbox, params ):
		"""
		一个角色进来。
		处理：
			生成新的队伍数据或者更改已有队伍数据
		"""
		teamID = params["teamID"]
		if teamID in self.teamInfo:
			self.teamInfo[teamID]["membersID"].append( params["dbID"] )
			if self.teamInfo[teamID]["leaderName" ] == "":
				self.teamInfo[teamID]["leaderName" ] = params["teamLeaderName"]
		else:
			self.teamInfo[teamID] = { "membersID" : [  params["dbID"] ], "leaderName" : params["teamLeaderName"], "point": 0, "place" : INIT_PLACE  }

	def newLeaver( self, baseMailbox, params ):
		"""
		一个角色出去。
		处理：
			角色离开副本造成的队伍信息发生改变
		"""
		leavingTeamID = params["teamID"]
		point = self.teamInfo[leavingTeamID]["point"]
		place = self.teamInfo[leavingTeamID]["place"]

		if leavingTeamID in self.teamInfo:
			if params["dbID"] in self.teamInfo[leavingTeamID]["membersID"]:
				self.teamInfo[leavingTeamID]["membersID"].remove( params["dbID"] )
		else:
			print "not in space team:", leavingTeamID
			return
			
		if len( self.teamInfo[leavingTeamID]["membersID"] ) == 0:		# 一个队伍都跑光了
			# 将队长名字置空，客户端多特殊处理，判断队长名字空时，就剔除掉
			self.teamInfo[leavingTeamID]["leaderName"] = ""
			# 以下very难看的代码：这个队伍滚光时，成绩也得清掉 by 姜毅
			minPlace = INIT_PLACE
			self.teamInfo[leavingTeamID]["place"] = INIT_PLACE
			self.teamInfo[leavingTeamID]["point"] = 0
			for iTeamID in self.teamInfo:
				if iTeamID == leavingTeamID:
					continue
				iInfo = self.teamInfo[iTeamID]
				if iInfo["place"] > place:
					self.teamInfo[iTeamID]["place"] -= 1
					iInfo = self.teamInfo[iTeamID]
				if iInfo["place"] < minPlace:
					minPlace = iInfo["place"]
					self.firstPlaceTeamID = iTeamID
			#for id, ib in self._players.iteritems():
			#	self.queryCompetitionInfo( ib )
		else:															# 队伍还有人在副本里，要判断玩家离开是否引起排名变化
			if self.teamInfo[leavingTeamID]["place"] == INIT_PLACE:
				return
			newPlace = self.getPlace( leavingTeamID )
			if newPlace > place:
				for teamID in self.teamInfo:
					if place < self.teamInfo[teamID]["place"] <= newPlace:
						self.teamInfo[teamID]["place"] = self.teamInfo[teamID]["place"] - 1
				self.teamInfo[leavingTeamID]["place"] = newPlace

	def getPlaceTeamID( self, place ):
		"""
		获得上一名的队伍ID
		"""

		if self.lastPlace == INIT_PLACE:
			return 0

		for iTeamID, iInfo in self.teamInfo.iteritems():
			if iInfo["place"] == place:
				return iTeamID

		return 0

	def getPointPlaceTeamsID( self, memberNum,place, point ):
		"""
		获得小于指定分数，但是小于指定名次的队伍ID
		"""
		teamsID = []
		for iTeamID, iInfo in self.teamInfo.iteritems():
			if iInfo["point"] < point:
				if iInfo["place"] < place:
					teamsID.append( iTeamID )
			elif iInfo["point"] == point:
				if len(iInfo["membersID"]) < memberNum and iInfo["place"] < place:
					teamsID.append( iTeamID )
		return teamsID


	def getPlace( self, teamID ):
		"""
		获得排名
		"""
		length = 0
		teamInfo = self.teamInfo[teamID]
		for iValue in self.teamInfo.itervalues():
			if iValue["point"] > teamInfo["point"]:
				length += 1
			elif iValue["point"] == teamInfo["point"]:
				if len( iValue["membersID"] ) >= len(teamInfo["membersID"]):
					length += 1
		return length


	def onPlayerDied( self, killerTeamID,roleTeamID,roleDBID,isRoleLeave ):
		"""
		define method
		"""
		if not killerTeamID in self.teamInfo:
			return
		
		if isRoleLeave:
			if roleDBID in self.teamInfo[roleTeamID]["membersID"]:
				self.teamInfo[roleTeamID]["membersID"].remove( roleDBID )
				self.teamInfo[roleTeamID]["membersID"]
		self.teamInfo[killerTeamID]["point"] = self.teamInfo[killerTeamID]["point"] + 1
		point = self.teamInfo[killerTeamID]["point"]
		place = self.teamInfo[killerTeamID]["place"]
		memberNum = len(self.teamInfo[killerTeamID]["membersID"])


		if self.lastPlace == INIT_PLACE:								#第一个得分的情况
			self.teamInfo[killerTeamID]["place"] = 1
			self.lastPlace = 1
			self.firstPlaceTeamID = killerTeamID
			return

		if place == 1:													#第一名得分的情况
			self.firstPlaceTeamID = killerTeamID
			return

		if place == INIT_PLACE:											#第一次得分的情况
			self.lastPlace = self.lastPlace + 1
			self.teamInfo[killerTeamID]["place"] = self.lastPlace


		teamsID = self.getPointPlaceTeamsID( memberNum,place, point )

		for iID in teamsID:
			self.teamInfo[iID]["place"] += 1

		self.teamInfo[killerTeamID]["place"] = self.getPlace( killerTeamID )
		for teamID in self.teamInfo:
			if self.teamInfo[teamID]["place"] == 1:
				self.firstPlaceTeamID = teamID

	def requestReward( self, teamID, baseMailbox ):
		"""
		define method
		addTeamCompetitionReward( placeList.index( BigWorld.entities[e.id].teamMailbox.id ) + 1 )
		"""
		if self.teamInfo[teamID]["place"] > 10:
			# 只给前10个玩家给予奖励
			return
		baseMailbox.cell.addTeamCompetitionReward( self.teamInfo[teamID]["place"] )


	def notifyWinner( self ):
		"""
		define method
		胜利通告
		"""		
		if self.firstPlaceTeamID:
			BigWorld.globalData["TeamCompetitionMgr"].setChampionBox( self.firstPlaceTeamID )
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.ZU_DUI_JING_JI_INFO_2 % ( self.teamInfo[self.firstPlaceTeamID]["leaderName"], self.copyLevel * 10 , self.copyLevel * 10 + 9 ), [] )

	def setWinner( self,winnerTeamID ):
		"""
		define method
		
		当只有一个队伍进入副本或提前结束但没有玩家死亡时，调用此方法设置冠军队伍ID
		"""
		self.teamInfo[winnerTeamID]["place"] = 1
		self.firstPlaceTeamID = winnerTeamID
	
	def queryCompetitionInfo( self, baseMailbox ):
		"""
		define method
		"""
		for iID,iValue in self.teamInfo.iteritems():
			baseMailbox.client.onTeamCompetitionInfo( iID, iValue["leaderName"], iValue["point"], iValue["place"] )

		baseMailbox.client.updataTeamCompetitionInfo()
# -*- coding: gb18030 -*-
#
#$Id:$

import time

import BigWorld
from bwdebug import *
import csdefine
import csstatus
import csconst
import cschannel_msgs
import Love3
from Function import Functor
from Message_logger import *
from ActivityLog import g_activityLog as g_aLog

class FamilyChallengeMgr:
	"""
	家族挑战管理
	"""
	def __init__( self ):
		"""
		"""
		self._challengeTimerDict = {}

	def onManagerInitOver( self ):
		"""
		virtual method.
		家族系统启动完毕通知
		"""
		self.challengeTimerInit()

	def isChallenging( self, srcFamilyDBID, dstFamilyDBID ):
		"""
		是否正在挑战中

		@param srcFamilyDBID : 发起的家族dbid
		@type srcFamilyDBID : DATABASE_ID
		@param dstFamilyDBID : 目标家族dbid
		@type dstFamilyDBID : DATABASE_ID
		"""
		for info in self.challengeFamilyData:
			if set( [ srcFamilyDBID, dstFamilyDBID ] ) == set( [ info[ "srcFamilyDBID" ], info[ "dstFamilyDBID" ] ] ):
				return True
		return False

	def hadJoinedChallenge( self, familyDBID ):
		"""
		家族是否参与挑战中
		"""
		for info in self.challengeFamilyData:
			if familyDBID == info[ "srcFamilyDBID" ] or familyDBID == info[ "dstFamilyDBID" ]:
				return True
		return False

	def validateChallenge( self, playerBase, srcFamilyDBID, familyName ):
		"""
		Define method.
		请求挑战familyName的家族
		功能：验证是否能够挑战

		@param playerBase : 发起的家族族长base
		@type playerBase : MAILBOX
		@param srcFamilyDBID : 发起的家族dbid
		@type srcFamilyDBID : DATABASE_ID
		@param familyName : 目标家族名字
		@type familyName : STRING
		"""
		if not self.hasFamilyName( familyName ):					# 不存在这个家族
			playerBase.client.onStatusMessage( csstatus.FAMILY_CHALLENGE_NOT_EXIST, "" )
			playerBase.cell.family_challengeFail()
			return

		dstFamilyDBID = self.getFamilyDBID( familyName )
		if self.isChallenging( srcFamilyDBID, dstFamilyDBID ):		# 已经在挑战中了
			playerBase.client.onStatusMessage( csstatus.FAMILY_ALREADY_CHALLENGE, "" )
			playerBase.cell.family_challengeFail()
			return

		playerBase.cell.family_startChallenge()

		dstFamilyName = familyName
		srcFamilyName = self.getFamilyName( srcFamilyDBID )

		#(csol-7884) 家族挑战赛(家族A的dbid 家族A的名字 家族B的dbid 家族B的名字)
		try:
			LOG_GAME_ACTIONS( "family_challenge", srcFamilyDBID, srcFamilyName, dstFamilyDBID, dstFamilyName )
		except:
			LOG_EXCEPTION("log_error", "error", ERROR_MESSAGE() )




	def startChallenge( self, playerBase, srcFamilyDBID, familyName, challengeTime ):
		"""
		Define method.

		开始家族挑战
		@param playerBase : 发起的家族族长base
		@type playerBase : MAILBOX
		@param srcFamilyDBID : 发起的家族dbid
		@type srcFamilyDBID : DATABASE_ID
		@param familyName : 目标家族名字
		@type familyName : STRING
		@param challengeTime : 挑战的时间
		@type challengeTime : INT8
		"""
		# 联合查询，返回[ [ familyDBID, tongName ], [ familyDBID, tongName ] ],以便得知tongName对应的是哪个family。如果family没有帮会，则没有数据。
		sql = "select a.id,b.sm_playerName from `tbl_FamilyEntity` as a, `tbl_TongEntity` as b where a.sm_tongDBID = b.id and ( a.sm_playerName = '%s'  or a.id = %i )" \
					% ( BigWorld.escape_string( familyName ), srcFamilyDBID )
		BigWorld.executeRawDatabaseCommand( sql, Functor( self._getTongDBIDForChallenge, playerBase, srcFamilyDBID, familyName, challengeTime ) )


	def _getTongDBIDForChallenge( self, playerBase, srcFamilyDBID, familyName, challengeTime, results, rows, errstr ):
		"""
		从数据库获取家族所属帮会的名字

		@param playerBase : 发起的家族族长base
		@type playerBase : MAILBOX
		@param srcFamilyDBID : 发起的家族dbid
		@type srcFamilyDBID : DATABASE_ID
		@param familyName : 目标家族名字
		@type familyName : STRING
		@param challengeTime : 挑战的时间
		@type challengeTime : INT8
		"""
		if errstr:
			ERROR_MSG( "read database is failed。srcFamilyDBID(%i),dstFamilyName(%s)" % ( srcFamilyDBID, familyName ) )
			return
		dstFamilyDBID = self.getFamilyDBID( familyName )

		srcTongName = ""
		dstTongName = ""
		if results:			# 如果取到了帮会名字数据
			for result in results:
				if int( result[ 0 ] ) == srcFamilyDBID:
					srcTongName = result[1]
				else:
					dstTongName = result[1]

		srcFamilyName = self.getFamilyName( srcFamilyDBID )

		persistentTime = float( challengeTime * 3600 )
		tempTime = time.time() + persistentTime
		# 如果两个家族同时向对方发起挑战，异步情况可能会造成两个族长都被扣钱，但是只加入一个家族挑战信息
		if not self.isChallenging( srcFamilyDBID, dstFamilyDBID ):
			temp = { "srcFamilyDBID" : srcFamilyDBID,
					"dstFamilyDBID" : dstFamilyDBID,
					"srcFamilyName" : srcFamilyName,
					"dstFamilyName" : familyName,
					"srcTongName" : srcTongName,
					"dstTongName" : dstTongName,
					"limitTime" : tempTime
					}
			self.challengeFamilyData.append( temp )
			self._challengeTimerDict[ self.addTimer( persistentTime ) ] = temp	# 保持一个映射，以方便处理timer
		s = cschannel_msgs.BCT_JZTZ_BEGIN % ( self.getFamilyName( srcFamilyDBID ), familyName, challengeTime )
		Love3.g_baseApp.anonymityBroadcast( s, [] )

		# 给所有在线成员发送目标家族名和到期时间
		srcFamily = self.findFamily( srcFamilyDBID )
		if srcFamily is not None:
			srcFamily.startChallenge( dstFamilyDBID, familyName, dstTongName, persistentTime )
		dstFamily = self.findFamily( dstFamilyDBID )
		if dstFamily is not None:
			dstFamily.startChallenge( srcFamilyDBID, self.getFamilyName( srcFamilyDBID ), srcTongName, persistentTime )

		pType = csdefine.ACTIVITY_PARENT_TYPE_OTHER
		aType = csdefine.ACTIVITY_JIA_ZU_TIAO_ZHAN
		action1 = csdefine.ACTIVITY_COMPETITION_GROUP_JOIN
		action2 = csdefine.ACTIVITY_COMPETITION_TIME
		g_aLog.addLog( pType, aType, action1, srcFamilyDBID )
		g_aLog.addLog( pType, aType, action1, dstFamilyDBID )
		g_aLog.addLog( pType, aType, action2, persistentTime )



	def onTimer( self, timerID, cbID ):
		"""
		timer触发
		"""
		if timerID in self._challengeTimerDict:				# 如果是家族挑战结束的timer
			info = self._challengeTimerDict[ timerID ]
			srcFamilyDBID = info[ "srcFamilyDBID" ]
			dstFamilyDBID = info[ "dstFamilyDBID" ]
			srcFamily = self.findFamily( srcFamilyDBID )
			if srcFamily is not None:
				srcFamily.endChallenge( dstFamilyDBID )
			dstFamily = self.findFamily( dstFamilyDBID )
			if dstFamily is not None:
				dstFamily.endChallenge( srcFamilyDBID )

			del self._challengeTimerDict[ timerID ]
			for temp in self.challengeFamilyData:
				if temp["srcFamilyDBID"] == srcFamilyDBID and temp[ "dstFamilyDBID" ] == dstFamilyDBID:
					self.challengeFamilyData.remove( temp )
					break

	def challengeTimerInit( self ):
		"""
		家族挑战系统初始化
		"""
		removeList = []
		for info in self.challengeFamilyData:
			now = time.time()
			limitTime = info[ "limitTime" ]
			if limitTime + 1 < now:			# 如果一秒钟后到期也移除挑战家族信息，考虑到网络传输延时情况等
				removeList.append( info )
			else:
				self._challengeTimerDict[ self.addTimer( now - limitTime ) ] = info
		for info in removeList:
			self.challengeFamilyData.remove( info )

	def getChallengeInfo( self, familyDBID ):
		"""
		根据家族dbid获得挑战信息。

		@param familyDBID : 家族dbid
		@type familyDBID : DATABASE_ID

		@rtype : [{"enemyDBID":familyDBID, "limitTime":limitTime}, ...]
		"""
		temp = []
		for info in self.challengeFamilyData:
			if familyDBID == info[ "srcFamilyDBID" ]:
				tempDict = {"enemyDBID":info[ "dstFamilyDBID" ],  "enemyName":info[ "dstFamilyName" ], "tongName":info[ "dstTongName" ], "limitTime":info[ "limitTime" ]}
				temp.append( tempDict )
			elif familyDBID == info[ "dstFamilyDBID" ]:
				tempDict = {"enemyDBID":info[ "srcFamilyDBID" ], "enemyName":info[ "srcFamilyName" ], "tongName":info[ "srcTongName" ], "limitTime":info[ "limitTime" ]}
				temp.append( tempDict )
		return temp

	def onChallengeNotify( self, familyDBID, baseEntity, baseEntityDBID ):
		"""
		通知客户端挑战相关信息

		@param familyDBID : 家族dbid
		@type familyDBID : DATABASE_ID
		@param baseEntity : 玩家的base
		@type baseEntity : MAILBOX
		@param baseEntityDBID : 玩家dbid
		@type baseEntityDBID : DATABASE_ID
		"""
		challengeInfos = self.getChallengeInfo( familyDBID )
		for info in challengeInfos:
			enemyDBID = info["enemyDBID"]
			baseEntity.cell.family_challengeNotify( enemyDBID )
			baseEntity.client.family_challengeNotify( self.getFamilyName( enemyDBID ), info[ "tongName" ], info["limitTime"] - time.time() )

	def onMemberLoginFamily( self, familyDBID, baseEntity, baseEntityDBID ):
		"""
		家族成员登陆，家族挑战信息处理

		@param familyDBID : 家族dbid
		@type familyDBID : DATABASE_ID
		@param baseEntity : 玩家的base
		@type baseEntity : MAILBOX
		@param baseEntityDBID : 玩家dbid
		@type baseEntityDBID : DATABASE_ID
		"""
		self.onChallengeNotify( familyDBID, baseEntity, baseEntityDBID )

	def onAcceptJoin( self, familyDBID, baseEntity, baseEntityDBID ):
		"""
		define method.
		有新成员加入家族了
		"""
		self.onChallengeNotify( familyDBID, baseEntity, baseEntityDBID )

	def onMemberKicked( self, baseEntity, familyDBID ):
		"""
		define method.
		某成员被踢了
		@param familyDBID : 家族dbid
		@type familyDBID : DATABASE_ID
		@param targetEntity : 玩家的base
		@type targetEntity : MAILBOX
		"""
		challengeInfos = self.getChallengeInfo( familyDBID )
		for info in challengeInfos:
			self.__exitChallenge( baseEntity, info["enemyDBID"], info["enemyName"] )

	def onMemberQuit( self, baseEntity, familyDBID ):
		"""
		define method.
		成员退出家族
		@param familyDBID : 家族dbid
		@type familyDBID  : DATABASE_ID
		@param baseEntity : 玩家的base
		@type baseEntity  : MAILBOX
		"""
		challengeInfos = self.getChallengeInfo( familyDBID )
		for info in challengeInfos:
			self.__exitChallenge( baseEntity, info["enemyDBID"], info["enemyName"] )

	def __exitChallenge( self, baseEntity, familyDBID, familyName ):
		"""
		"""
		# 自己退出挑战赛
		baseEntity.cell.exitChallenge( familyDBID, familyName )

		# 通知对方的家族此人退赛
		enemyFamilyDBID = 0
		for info in self.challengeFamilyData:
			if familyDBID == info[ "srcFamilyDBID" ]:
				enemyFamilyDBID = info[ "dstFamilyDBID" ]
				break
			elif familyDBID == info[ "dstFamilyDBID" ]:
				enemyFamilyDBID = info[ "srcFamilyDBID" ]
				break
		if enemyFamilyDBID == 0 : return
		enemyFamilyEntity = self.findFamily( enemyFamilyDBID )
		if enemyFamilyEntity :
			enemyFamilyEntity.challengeFamilyMemberExit( baseEntity.id )
#$Log:$
#

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
	������ս����
	"""
	def __init__( self ):
		"""
		"""
		self._challengeTimerDict = {}

	def onManagerInitOver( self ):
		"""
		virtual method.
		����ϵͳ�������֪ͨ
		"""
		self.challengeTimerInit()

	def isChallenging( self, srcFamilyDBID, dstFamilyDBID ):
		"""
		�Ƿ�������ս��

		@param srcFamilyDBID : ����ļ���dbid
		@type srcFamilyDBID : DATABASE_ID
		@param dstFamilyDBID : Ŀ�����dbid
		@type dstFamilyDBID : DATABASE_ID
		"""
		for info in self.challengeFamilyData:
			if set( [ srcFamilyDBID, dstFamilyDBID ] ) == set( [ info[ "srcFamilyDBID" ], info[ "dstFamilyDBID" ] ] ):
				return True
		return False

	def hadJoinedChallenge( self, familyDBID ):
		"""
		�����Ƿ������ս��
		"""
		for info in self.challengeFamilyData:
			if familyDBID == info[ "srcFamilyDBID" ] or familyDBID == info[ "dstFamilyDBID" ]:
				return True
		return False

	def validateChallenge( self, playerBase, srcFamilyDBID, familyName ):
		"""
		Define method.
		������սfamilyName�ļ���
		���ܣ���֤�Ƿ��ܹ���ս

		@param playerBase : ����ļ����峤base
		@type playerBase : MAILBOX
		@param srcFamilyDBID : ����ļ���dbid
		@type srcFamilyDBID : DATABASE_ID
		@param familyName : Ŀ���������
		@type familyName : STRING
		"""
		if not self.hasFamilyName( familyName ):					# �������������
			playerBase.client.onStatusMessage( csstatus.FAMILY_CHALLENGE_NOT_EXIST, "" )
			playerBase.cell.family_challengeFail()
			return

		dstFamilyDBID = self.getFamilyDBID( familyName )
		if self.isChallenging( srcFamilyDBID, dstFamilyDBID ):		# �Ѿ�����ս����
			playerBase.client.onStatusMessage( csstatus.FAMILY_ALREADY_CHALLENGE, "" )
			playerBase.cell.family_challengeFail()
			return

		playerBase.cell.family_startChallenge()

		dstFamilyName = familyName
		srcFamilyName = self.getFamilyName( srcFamilyDBID )

		#(csol-7884) ������ս��(����A��dbid ����A������ ����B��dbid ����B������)
		try:
			LOG_GAME_ACTIONS( "family_challenge", srcFamilyDBID, srcFamilyName, dstFamilyDBID, dstFamilyName )
		except:
			LOG_EXCEPTION("log_error", "error", ERROR_MESSAGE() )




	def startChallenge( self, playerBase, srcFamilyDBID, familyName, challengeTime ):
		"""
		Define method.

		��ʼ������ս
		@param playerBase : ����ļ����峤base
		@type playerBase : MAILBOX
		@param srcFamilyDBID : ����ļ���dbid
		@type srcFamilyDBID : DATABASE_ID
		@param familyName : Ŀ���������
		@type familyName : STRING
		@param challengeTime : ��ս��ʱ��
		@type challengeTime : INT8
		"""
		# ���ϲ�ѯ������[ [ familyDBID, tongName ], [ familyDBID, tongName ] ],�Ա��֪tongName��Ӧ�����ĸ�family�����familyû�а�ᣬ��û�����ݡ�
		sql = "select a.id,b.sm_playerName from `tbl_FamilyEntity` as a, `tbl_TongEntity` as b where a.sm_tongDBID = b.id and ( a.sm_playerName = '%s'  or a.id = %i )" \
					% ( BigWorld.escape_string( familyName ), srcFamilyDBID )
		BigWorld.executeRawDatabaseCommand( sql, Functor( self._getTongDBIDForChallenge, playerBase, srcFamilyDBID, familyName, challengeTime ) )


	def _getTongDBIDForChallenge( self, playerBase, srcFamilyDBID, familyName, challengeTime, results, rows, errstr ):
		"""
		�����ݿ��ȡ����������������

		@param playerBase : ����ļ����峤base
		@type playerBase : MAILBOX
		@param srcFamilyDBID : ����ļ���dbid
		@type srcFamilyDBID : DATABASE_ID
		@param familyName : Ŀ���������
		@type familyName : STRING
		@param challengeTime : ��ս��ʱ��
		@type challengeTime : INT8
		"""
		if errstr:
			ERROR_MSG( "read database is failed��srcFamilyDBID(%i),dstFamilyName(%s)" % ( srcFamilyDBID, familyName ) )
			return
		dstFamilyDBID = self.getFamilyDBID( familyName )

		srcTongName = ""
		dstTongName = ""
		if results:			# ���ȡ���˰����������
			for result in results:
				if int( result[ 0 ] ) == srcFamilyDBID:
					srcTongName = result[1]
				else:
					dstTongName = result[1]

		srcFamilyName = self.getFamilyName( srcFamilyDBID )

		persistentTime = float( challengeTime * 3600 )
		tempTime = time.time() + persistentTime
		# �����������ͬʱ��Է�������ս���첽������ܻ���������峤������Ǯ������ֻ����һ��������ս��Ϣ
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
			self._challengeTimerDict[ self.addTimer( persistentTime ) ] = temp	# ����һ��ӳ�䣬�Է��㴦��timer
		s = cschannel_msgs.BCT_JZTZ_BEGIN % ( self.getFamilyName( srcFamilyDBID ), familyName, challengeTime )
		Love3.g_baseApp.anonymityBroadcast( s, [] )

		# ���������߳�Ա����Ŀ��������͵���ʱ��
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
		timer����
		"""
		if timerID in self._challengeTimerDict:				# ����Ǽ�����ս������timer
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
		������սϵͳ��ʼ��
		"""
		removeList = []
		for info in self.challengeFamilyData:
			now = time.time()
			limitTime = info[ "limitTime" ]
			if limitTime + 1 < now:			# ���һ���Ӻ���Ҳ�Ƴ���ս������Ϣ�����ǵ����紫����ʱ�����
				removeList.append( info )
			else:
				self._challengeTimerDict[ self.addTimer( now - limitTime ) ] = info
		for info in removeList:
			self.challengeFamilyData.remove( info )

	def getChallengeInfo( self, familyDBID ):
		"""
		���ݼ���dbid�����ս��Ϣ��

		@param familyDBID : ����dbid
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
		֪ͨ�ͻ�����ս�����Ϣ

		@param familyDBID : ����dbid
		@type familyDBID : DATABASE_ID
		@param baseEntity : ��ҵ�base
		@type baseEntity : MAILBOX
		@param baseEntityDBID : ���dbid
		@type baseEntityDBID : DATABASE_ID
		"""
		challengeInfos = self.getChallengeInfo( familyDBID )
		for info in challengeInfos:
			enemyDBID = info["enemyDBID"]
			baseEntity.cell.family_challengeNotify( enemyDBID )
			baseEntity.client.family_challengeNotify( self.getFamilyName( enemyDBID ), info[ "tongName" ], info["limitTime"] - time.time() )

	def onMemberLoginFamily( self, familyDBID, baseEntity, baseEntityDBID ):
		"""
		�����Ա��½��������ս��Ϣ����

		@param familyDBID : ����dbid
		@type familyDBID : DATABASE_ID
		@param baseEntity : ��ҵ�base
		@type baseEntity : MAILBOX
		@param baseEntityDBID : ���dbid
		@type baseEntityDBID : DATABASE_ID
		"""
		self.onChallengeNotify( familyDBID, baseEntity, baseEntityDBID )

	def onAcceptJoin( self, familyDBID, baseEntity, baseEntityDBID ):
		"""
		define method.
		���³�Ա���������
		"""
		self.onChallengeNotify( familyDBID, baseEntity, baseEntityDBID )

	def onMemberKicked( self, baseEntity, familyDBID ):
		"""
		define method.
		ĳ��Ա������
		@param familyDBID : ����dbid
		@type familyDBID : DATABASE_ID
		@param targetEntity : ��ҵ�base
		@type targetEntity : MAILBOX
		"""
		challengeInfos = self.getChallengeInfo( familyDBID )
		for info in challengeInfos:
			self.__exitChallenge( baseEntity, info["enemyDBID"], info["enemyName"] )

	def onMemberQuit( self, baseEntity, familyDBID ):
		"""
		define method.
		��Ա�˳�����
		@param familyDBID : ����dbid
		@type familyDBID  : DATABASE_ID
		@param baseEntity : ��ҵ�base
		@type baseEntity  : MAILBOX
		"""
		challengeInfos = self.getChallengeInfo( familyDBID )
		for info in challengeInfos:
			self.__exitChallenge( baseEntity, info["enemyDBID"], info["enemyName"] )

	def __exitChallenge( self, baseEntity, familyDBID, familyName ):
		"""
		"""
		# �Լ��˳���ս��
		baseEntity.cell.exitChallenge( familyDBID, familyName )

		# ֪ͨ�Է��ļ����������
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

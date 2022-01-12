# -*- coding: gb18030 -*-
#
# ������������� 2009-01-17 SongPeifang
#
import Love3
import csdefine
import BigWorld
import cschannel_msgs
from bwdebug import *
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from MsgLogger import g_logger

BC_GAME_LOGIN	= 0					# ���������ʼ����
BC_GAME_BEGIN	= 1					# ���������ʽ��ʼ
BC_GAME_RELOAD	= 2					# ������������
LOIN_TIME		= 600				# �����������ʱ������Ϊ10����

class BCGameMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.registerGlobally( "BCGameMgr", self._onRegisterManager )
		self._loginTime		= LOIN_TIME	# �ӱ��������ʼ�ĵȴ�ʱ��Ϊ300��
		self._competitorCount = {}		# �μӱ������������
		self._canLogin		= False		# �������μӱ������
		self.BCNPCs			= {}		# ���еı���NPC

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register BCGameMgr Fail!" )
			self.registerGlobally( "BCGameMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["BCGameMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("BCGameMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
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
		ע��ÿ���ߵ�BCNPC
		"""
		self.BCNPCs[ lineNumber ] = baseMailbox

	def onStartNotice( self ):
		"""
		define method.
		���ʼ֪ͨ
		"""
		self._loginTime = LOIN_TIME				# ������ʼ��Ҫ�ָ���10����
		self.onTimer( 0, BC_GAME_LOGIN )
		INFO_MSG( "BCGameMgr.", "notice", "" )

	def onTimer( self, id, userArg ):
		"""
		֪ͨ������ұ��������ʼ
		"""
		if userArg == BC_GAME_LOGIN:
			# ��ʼ������������Ĺ���
			leftLoginTime = int( int( self._loginTime ) / 60 )
			if self._loginTime > 0 and leftLoginTime in [ 10, 5, 3, 1 ]:
				# ���������10�֣�5�֡�3�֡�1����ʱ��Ҫ������
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BSDS_PREPARE_NOTIFY % leftLoginTime, [] )
			self.changeLoginState( True )
			if self._loginTime <= 0:
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BSDS_BEGIN_NOTIFY, [] )
				self.addTimer( 5, 0, BC_GAME_BEGIN )	# �������5��֮��ʼ��
				self.changeLoginState( False )			# ��ʱ������������
			else:
				self.addTimer( 60, 0, BC_GAME_LOGIN )
			self._loginTime -= 60

		elif userArg == BC_GAME_BEGIN:
			# ���������ʼ��
			self.onGameBegin()

	def onGameBegin( self ):
		"""
		���������ʼ
		"""
		hasMembers = False
		for competitorCount in self._competitorCount.itervalues():
			if competitorCount > 0:
				hasMembers = True
		if not hasMembers:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_BSDS_END_NO_PARTICIPANT, [] )

		if len( self.BCNPCs ) <= 0:
			ERROR_MSG( "δ֪�����Ҳ������������NPC,���ܻ�δ��������" )
			return

		for lineNumber, bcNPCMailBox in self.BCNPCs.iteritems():
			if self._competitorCount.get( lineNumber, 0 ) <= 0:
				continue
			bcNPCMailBox.cell.bcGameStart()
			self.setMemberCount( lineNumber, 0 )	# �����������������û�0��

		try:
			g_logger.actStartLog( csdefine.ACTIVITY_BIAN_SHEN_DA_SAI )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def setMemberCount( self, lineNumber, count ):
		"""
		Define Method.
		���ñ�������
		"""
		self._competitorCount[ lineNumber ] = count

	def changeLoginState( self, canLogin ):
		"""
		�����Ƿ���Ա���
		"""
		self._canLogin = canLogin
		for lineNumber, bcNPCMailBox in self.BCNPCs.iteritems():
			bcNPCMailBox.cell.getLoginState( canLogin )

	def onEnd( self ):
		"""
		define method.
		�����
		"""
		self._loginTime = LOIN_TIME				# ����������Ҫ�ָ���10����
		INFO_MSG( "BCGameMgr.", "end", "" )
# -*- coding: gb18030 -*-

from bwdebug import *
import BigWorld
import Love3
import csdefine
import csconst
import cschannel_msgs
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()


TEN_MIN = 10 * 60			# 10����
FIVE_MIN = 5 * 60			# 5����
ONE_MIN = 60				# 1����
TWENTY_MIN = 20 * 60		# 20����
TOW_HOUR = 	2 * 3600		# 2Сʱ

NOTIFY_MAX_COUNT = TOW_HOUR / TWENTY_MIN - 2	# ���һ��Ҫ֪ͨ���Σ���ʼ�ͽ�������Ҫ֪ͨ��

# timer id
TIMER_TEN_MIN_REMAIN = 1	# ���ʼǰ10���ӵ�timer
TIMER_FIVE_MIN_REMAIN = 2	# ���ʼǰ5���ӵ�timer
TIMER_ONE_MIN_REMAIN = 3	# ���ʼǰ1���ӵ�timer
TIMER_ACTIVITY_START = 4	# ���ʼ
TIMER_ACTIVITY_END = 5		# �����
TIMER_ACTIVITY_BEING = 6	# �������


class LuckyBoxActivityMgr( BigWorld.Base ):
	"""
	�콵���л������
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.activityNotifyCount = 0	# �������֪ͨ����

		self.registerGlobally( "LuckyBoxActivityMgr", self.registerGloballyCB )


	def registerGloballyCB( self, complete ):
		"""
		ע��ȫ��ʵ���Ļص�
		"""
		if not complete:
			ERROR_MSG( "--->>>Register globally error." )
			self.registerGlobally( "LuckyBoxActivityMgr", self.registerGloballyCB )
		else:
			BigWorld.globalData[ "LuckyBoxActivityMgr" ] = self
			INFO_MSG( "--->>>Register globally complete." )
			self.registerCrond()

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		crond = BigWorld.globalData["Crond"]
		for taskEventKey, taskEvents in csconst.DROP_TASKEVENTS.iteritems():
			for taskName, callbackName in taskEvents.iteritems():
				for cmd in g_CrondDatas.getTaskCmds( taskName ):
					crond.addScheme( cmd, self, callbackName )
			crond.addAutoStartScheme( taskEventKey, self, taskEvents[taskEventKey] )
		BigWorld.globalData["LuckyActivity"] = {}
		
	def onStartLuckyBox( self ):
		"""
		define method.
		�콵���л��ʼ֪ͨ
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TJBH_TIMER_ACTIVITY_START, [] )
		# BigWorld.globalData[ key ] = csconst.LUCKY_BOX_DROP_RATE
		f = BigWorld.globalData["LuckyActivity"]
		f["AS_LuckyBoxActivityStart"] = csdefine.RCG_LUCKY_BOX
		BigWorld.globalData["LuckyActivity"] = f
		self.addTimer( TWENTY_MIN, 0, TIMER_ACTIVITY_BEING )		# ��ʮ���Ӻ�һ����е�֪ͨ
		INFO_MSG( "LuckyBoxActivityMgr", "start", "Lucky" )
			
	def onStartMidAut( self ):
		"""
		define method.
		���������ʼ֪ͨ
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_MADROP_ACTIVITY_START, [] )
		f = BigWorld.globalData["LuckyActivity"]
		f["AS_MidActivityStart"] = csdefine.RCG_MID_AUTUMN
		BigWorld.globalData["LuckyActivity"] = f
		INFO_MSG( "LuckyBoxActivityMgr", "start", "MidAut" )

	def onTimer( self, controllerID, userArg ):
		"""
		"""
		if userArg == TIMER_ACTIVITY_BEING:
			self.activityNotifyCount += 1
			DEBUG_MSG( "---->>.NOTIFY" )
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TJBH_TIMER_ACTIVITY_BEING, [] )
			if self.activityNotifyCount < NOTIFY_MAX_COUNT:
				self.addTimer( TWENTY_MIN, 0, TIMER_ACTIVITY_BEING )	# ��ʮ���Ӻ�һ����е�֪ͨ
			elif self.activityNotifyCount == NOTIFY_MAX_COUNT:
				self.activityNotifyCount = 0
			
	def onEndLuckyBox( self ):
		"""
		�ر��콵���л
		"""
		# ��ֹ�������ڻ��ʼʱ��֮������ ���Ҳ����ñ��
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TJBH_TIMER_ACTIVITY_END, [] )
		if BigWorld.globalData["LuckyActivity"].has_key( "AS_LuckyBoxActivityStart" ):
			f = BigWorld.globalData["LuckyActivity"]
			f.pop( "AS_LuckyBoxActivityStart" )
			BigWorld.globalData["LuckyActivity"] = f
		
		INFO_MSG( "LuckyBoxActivityMgr", "end", "Lucky" )
			
	def onEndMidAut( self ):
		"""
		�ر��������
		"""
		# ��ֹ�������ڻ��ʼʱ��֮������ ���Ҳ����ñ��
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_MADROP_ACTIVITY_END, [] )
		if BigWorld.globalData["LuckyActivity"].has_key( "AS_MidActivityStart" ):
			f = BigWorld.globalData["LuckyActivity"]
			f.pop( "AS_MidActivityStart" )
			BigWorld.globalData["LuckyActivity"] = f
		
		INFO_MSG( "LuckyBoxActivityMgr", "end", "MidAut" )
		
	def onStartLuckyBoxNotice( self ):
		"""
		define method.
		�콵���л��ʼ֪ͨ
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TJBH_TIMER_TEN_MIN_REMAIN, [] )
		INFO_MSG( "LuckyBoxActivityMgr", "notice", "Lucky" )
		
	def onStartMidAutNotice( self ):
		"""
		define method.
		���������ʼ֪ͨ
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_MADROP_ACTIVITY_START, [] )
		INFO_MSG( "LuckyBoxActivityMgr", "notice", "MidAut" )
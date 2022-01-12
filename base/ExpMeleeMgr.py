# -*- coding: gb18030 -*-
#
# �����Ҷ�������
#
import Love3
import csdefine
import BigWorld
import random
import Math
import time
import cschannel_msgs
from bwdebug import *
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

class ExpMeleeMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "ExpMeleeMgr", self._onRegisterManager )
		self.checkStartMeleeTimerID = 0
		#self.checkEndMeleeTimerID = 0
		#self.meleeSpaces = []
		self.globalChatMeleeTimerID = 0

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register ExpMeleeMgr Fail!" )
			self.registerGlobally( "ExpMeleeMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["ExpMeleeMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("ExpMeleeMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"ExpMelee_start" : "onStart",
						"ExpMelee_end" : "onEnd",
					  }
		
		crond = BigWorld.globalData["Crond"]
		
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )
		
		crond.addAutoStartScheme( "ExpMelee_start", self, "onStart" )
		

	def onRegisterSpace( self, spaceBase ):
		"""
		define method.
		ע�����п����Ļ����base
		"""
		return
		self.meleeSpaces.append( spaceBase )

	def onUnRegisterSpace( self, spaceBaseID ):
		"""
		define method.
		ȡ��ע������base
		"""
		return
		for i, s in enumerate( self.meleeSpaces ):
			if s.id == spaceBaseID:
				self.meleeSpaces.pop( i )
				return

	def onStart( self ):
		"""
		define method.
		�����Ҷ���ʼ
		"""
		if BigWorld.globalData.has_key( "AS_ExpMelee" ):
			curTime = time.localtime()
			ERROR_MSG( "�����Ҷ�����ڽ��У�%i��%i����ͼ�ٴο�ʼ�����Ҷ���"%(curTime[3],curTime[4] ) )
			return
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JYLD_PRE_NOTIFY, [] )
		self.checkStartMeleeTimerID = self.addTimer( 10 * 60, 0, 0 )
		INFO_MSG( "ExpMeleeMgr", "start", "" )

	def onEnd( self ):
		"""
		define method.
		�����Ҷ�����
		"""
		if not BigWorld.globalData.has_key( "AS_ExpMelee" ):
			curTime = time.localtime()
			ERROR_MSG( "�����Ҷ���Ѿ�������%i��%i����ͼ�ٴιرվ����Ҷ���"%(curTime[3],curTime[4] ) )
			return

		if BigWorld.globalData.has_key( "AS_ExpMelee" ):
			del BigWorld.globalData[ "AS_ExpMelee" ]

		self.delTimer( self.globalChatMeleeTimerID )
		self.globalChatMeleeTimerID = 0
		
		INFO_MSG( "ExpMeleeMgr", "end", "" )


		#self.checkEndMeleeTimerID = self.addTimer( 60, 0, 4*60 )
		#for s in self.meleeSpaces:
		#	s.cell.onMeleeMsg( 300 )

	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if self.checkStartMeleeTimerID == timerID:
			self.delTimer( self.checkStartMeleeTimerID )
			self.checkStartMeleeTimerID = 0
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JYLD_IS_DOING, [] )
			self.globalChatMeleeTimerID = self.addTimer( 3600, 0, 60*60 )
			BigWorld.globalData[ "AS_ExpMelee" ] = True
		elif self.globalChatMeleeTimerID == timerID:		# ���1Сʱ֪ͨһ��
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JYLD_IS_DOING, [] )
			self.globalChatMeleeTimerID = self.addTimer( 3600, 0, 60*60 )
# -*- coding: gb18030 -*-
#

# $Id:  Exp $

import BigWorld
from bwdebug import *
import csdefine
import cschannel_msgs
import Love3
import time
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()


class CollectPointManager( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "CollectPointManager", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register CollectPointManager Fail!" )
			# again
			self.registerGlobally( "CollectPointManager", self._onRegisterManager )
		else:
			BigWorld.globalData["CollectPointManager"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("CollectPointManager Create Complete!")
			self.registerCrond()



	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"collect_start_notice" : "onStartNotice",
					  	"collect_Start" : "onStart",
						"collect_End" :	"onEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )

		crond.addAutoStartScheme( "collect_Start", self, "onStart" )

	def onStart( self ):
		"""
		define method.
		�������ʼ
		"""
		if BigWorld.globalData.has_key( "AS_collectStart" ) and BigWorld.globalData[ "AS_collectStart" ] == True:
			curTime = time.localtime()
			ERROR_MSG( "�ɼ�����ڽ��У�%i��%i����ͼ�ٴο�ʼ�ɼ����"%(curTime[3],curTime[4] ) )
			return
		BigWorld.globalData[ "AS_collectStart" ] = True
		INFO_MSG( "CollectPointManager" , "start", "" )


	def onEnd( self ):
		"""
		define method.
		���������
		"""
		if not BigWorld.globalData.has_key( "AS_collectStart" ):
			curTime = time.localtime()
			ERROR_MSG( "�ɼ���Ѿ�������%i��%i����ͼ�ٴν����ɼ����"%(curTime[3],curTime[4] ) )
			return
		BigWorld.globalData[ "AS_collectStart" ] = False
		INFO_MSG( "CollectPointManager" , "end", "" )

	def onStartNotice( self ):
		"""
		define method.
		���ʼ֪ͨ
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TEAM_COLLECT, [] )
		INFO_MSG( "CollectPointManager" , "notice", "" )

# -*- coding: gb18030 -*-
#
# ϵͳ�౶���� kebiao
#
import Love3
import csdefine
import cschannel_msgs
import BigWorld
import random
import Math
from bwdebug import *
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

CONST_EXP_RATE = 1.0

class SysMultExpMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "SysMultExpMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register SysMultExpMgr Fail!" )
			self.registerGlobally( "SysMultExpMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["SysMultExpMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("SysMultExpMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"SysMultExpMgr_ready" : "onReady",
						"SysMultExpMgr_start2" : "onStart2",
						"SysMultExpMgr_end2" : "onEnd2",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )

		crond.addAutoStartScheme( "SysMultExpMgr_start2", self, "onStart2" )

	def onReady( self ):
		"""
		define method.
		֪ͨ10����֮��ʼ
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_DBJY_WILL_BEGIN_NOTIFY, [] )
		INFO_MSG( "SysMultExpMgr", "notice", "" )
		

	def open( self, mult ):
		"""
		define method.
		2�����鿪ʼ
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_DBJY_GODSEND_NOTIFY % ( mult * 100 ), [] )
		BigWorld.globalData[ "AS_SysMultExp" ] = mult

	def onStart2( self ):
		"""
		define method.
		2�����鿪ʼ
		"""
		self.open( CONST_EXP_RATE )
		INFO_MSG( "SysMultExpMgr", "start", "" )

	def onEnd2( self ):
		"""
		define method.
		2���������
		"""
		if BigWorld.globalData.has_key( "AS_SysMultExp" ):
			del BigWorld.globalData[ "AS_SysMultExp" ]
		
		INFO_MSG( "SysMultExpMgr", "end", "" )

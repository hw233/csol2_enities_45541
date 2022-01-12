# -*- coding: gb18030 -*-
#

# $Id: DartManager.py,v 1.1 2008-09-05 03:41:04 zhangyuxing Exp $

import Love3
import BigWorld
from bwdebug import *
from Function import Functor
import csstatus
import Love3
import csdefine
import cschannel_msgs
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
import time

"""
��ʱ� -- �����
"""


TIANGUAN_START = 1
TIANGUAN_RELOAD = 6

class TianguanMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "TianguanMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register TianguanMgr Fail!" )
			# again
			self.registerGlobally( "TianguanMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["TianguanMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("TianguanMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"TianguanMgr_start_notice" : "onStartNotice",
					  	"TianguanMgr_start" : "onStart",
					  	"TianguanMgr_end" : "onEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )
		crond.addAutoStartScheme( "TianguanMgr_start", self, "onStart" )

	def onStart( self ):
		"""
		define method.
		���ʼ
		"""
		if BigWorld.globalData.has_key( "AS_Tianguan" ):
			curTime = time.localtime()
			ERROR_MSG( "��ػ���ڽ��У�%i��%i����ͼ�ٴο�ʼ��ء�"%(curTime[3],curTime[4] ) )
			return
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TGHD_WILL_OPEN_NOTIFY , [])
		BigWorld.globalData[ "AS_Tianguan" ] = True
		INFO_MSG( "TianguanMgr", "start", "" )

	def onEnd( self ):
		"""
		define method.
		�����
		"""
		# ��ֹ�������ڻ��ʼʱ��֮������ ���Ҳ����ñ��
		if not BigWorld.globalData.has_key( "AS_Tianguan" ):
			curTime = time.localtime()
			ERROR_MSG( "��ػ�Ѿ�������%i��%i����ͼ�ٴν�����ء�"%(curTime[3],curTime[4] ) )
			return

		if BigWorld.globalData.has_key( "AS_Tianguan" ):
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TGHD_WILL_OPEN_NOTIFY, [] )
			del BigWorld.globalData[ "AS_Tianguan" ]
		
		INFO_MSG( "TianguanMgr", "end", "" )

	def onStartNotice( self ):
		"""
		define method.
		���ʼ֪ͨ
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TGHD_BEGIN_NOTIFY, [] )
		INFO_MSG( "TianguanMgr", "notice", "" )
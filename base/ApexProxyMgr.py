# -*- coding: gb18030 -*-
#
# $Id: ApexProxy.py,v 1.119 2009-06-25 03:50:30 LuoCD Exp $


"""
反外挂代理管理类。

"""

import BigWorld
import ApexProxy
from bwdebug import *

APEXPROXY_KILL_TIMER = 1
APEXPROXY_SEND_TIMER = 2

class ApexProxyMgr( BigWorld.Base ):
	def __init__( self ):
		BigWorld.Base.__init__( self )
		INFO_MSG("init ApexProxyMgr")
		self.apexProxy = ApexProxy.ApexProxy( )
		if(self.apexProxy.getApexStartFlag()):
			self.apexProxy.startApexProxy()
			self.addTimer( 1, 1, APEXPROXY_KILL_TIMER )
			self.addTimer( 1, 1, APEXPROXY_SEND_TIMER )

	def onGetApexProxy( self ):
		"""
		外面获取对象ApexProxy 方法 apexProxy = BigWorld.globalData[ "ApexProxyMgr" ].onGetApexProxy()
		"""
		return self.apexProxy
	
	def onTimer( self, timerID, userArg ):
		"""
		处理两个事情：踢人或发消息到客户端
		"""
		if userArg == APEXPROXY_KILL_TIMER:
			self.apexProxy.ApexKillRole( )
		elif  userArg == APEXPROXY_SEND_TIMER:
			self.apexProxy.SendMsgToClient( )
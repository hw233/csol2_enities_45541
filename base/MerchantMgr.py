# -*- coding: gb18030 -*-
#
# $Id: Exp $


import time
import csdefine
import csstatus
import BigWorld
from bwdebug import *
import Love3
import Language
import random
import Love3
import cschannel_msgs
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

"""
定时活动 -- 跑商
"""

TWO_HOUR = 7200

AREA_CONDITION_CHANGE = 1								#地区物品价格发生变化

class MerchantMgr( BigWorld.Base ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.areaConditionSection = Language.openConfigSection( "config/server/AreaMerchantCondition.xml" )

		BigWorld.globalData["MerchantHighArea"] = ""
		BigWorld.globalData["MerchantHighItem"] = 0
		BigWorld.globalData["MerchantHighPercent"] = 1.0
		BigWorld.globalData["MerchantHighText"] = ""

		BigWorld.globalData["MerchantLowArea"] = ""
		BigWorld.globalData["MerchantLowItem"] = 0
		BigWorld.globalData["MerchantLowPercent"] = 1.0
		BigWorld.globalData["MerchantLowText"] = ""

		# 把自己注册为globalData全局实体
		self.conditionDict = {}
		self.registerGlobally( "MerchantMgr", self._onRegisterManager )
		self.setConditionDict()

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register MerchantMgr Fail!" )
			# again
			self.registerGlobally( "MerchantMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["MerchantMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("MerchantMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"Merchant_Area_Condition_Change" : "onAreaCondtionChange",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )

	def onAreaCondtionChange( self ):
		"""
		define method.
		任务管理器通知时间到
		"""
		index = random.randint( 0, len( self.conditionDict['good'] ) -1 )
		BigWorld.globalData["MerchantHighArea"] = self.conditionDict['good'][index]['area'].asString
		BigWorld.globalData["MerchantHighItem"] = self.conditionDict['good'][index]['itemID'].asInt
		BigWorld.globalData["MerchantHighPercent"] = self.conditionDict['good'][index]['percent'].asFloat
		BigWorld.globalData["MerchantHighText"] = self.conditionDict['good'][index]['text'].asString
		Love3.g_baseApp.anonymityBroadcast( BigWorld.globalData["MerchantHighText"], [] )

		index = random.randint( 0, len( self.conditionDict['bad'] ) -1 )

		while self.conditionDict['bad'][index]['itemID'].asInt == BigWorld.globalData["MerchantHighItem"]:
			index = random.randint( 0, len( self.conditionDict['bad'] ) -1 )

		BigWorld.globalData["MerchantLowArea"] = self.conditionDict['bad'][index]['area'].asString
		BigWorld.globalData["MerchantLowItem"] = self.conditionDict['bad'][index]['itemID'].asInt
		BigWorld.globalData["MerchantLowPercent"] = self.conditionDict['bad'][index]['percent'].asFloat
		BigWorld.globalData["MerchantLowText"] = self.conditionDict['bad'][index]['text'].asString
		Love3.g_baseApp.anonymityBroadcast( BigWorld.globalData["MerchantLowText"], [] )

	def setConditionDict( self ):
		"""
		"""
		for node in self.areaConditionSection.values():
			if node['percent'].asFloat < 1.0:
				if not self.conditionDict.has_key( 'bad' ):
					self.conditionDict['bad'] = [node]
				else:
					self.conditionDict['bad'].append( node )
			else:
				if not self.conditionDict.has_key( 'good' ):
					self.conditionDict['good'] = [node]
				else:
					self.conditionDict['good'].append( node )

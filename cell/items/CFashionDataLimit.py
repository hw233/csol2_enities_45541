# -*- coding: gb18030 -*-

import time
from bwdebug import *
import csdefine
from CrondScheme import *
from CEquip import CEquip

class CFashionDateLimit( CEquip ):
	"""
	通过特殊日期限制的时装
	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )
		# 在物品配置里添加活动日期时刻
		# cmd格式为活动日程表cmd格式 : min hour day mon week
		# example : 0 * * * 7
		self._cmd = self.queryTemp( "param1", "" )

	def activaLifeTime( self, owner = None ):
		"""
		激活一个物品的使用时间
		如果存活类型是下线计时，那么owner必须为None
		因为它不应该通知addLifeItemsToManage
		
		这里通过活动日程与当前时间差来设置一个时间
		"""
		t = time.time()
		year, month, day, hour, minute = time.localtime( t )[:5]
		scheme = Scheme()
		scheme.init( cmd )
		nextTime = scheme.calculateNext( year, month, day, hour, minute )
		interval = nextTime - t
		self.setLifeTime( interval, owner )
		CEquip.activaLifeTime( self, owner )
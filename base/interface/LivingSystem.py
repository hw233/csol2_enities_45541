# -*- coding: gb18030 -*-
#

"""
生活系统模块
"""
import time
from bwdebug import *
import csdefine
import ECBExtend
import Const

class LivingSystem:
	"""
	"""
	def __init__( self ):
		"""
		初始化状态。要在Fight初始化之前
		"""
		self.vimChargeTimer = None
		
	def checkOverDay( self ):
		"""
		检测是否跨日期 by 姜毅
		"""
		t = self.getToday0Tick()
		return self.role_last_offline < t
		
	def checkOverVimTick( self ):
		"""
		检测是否跨充活力值时刻
		
		如果同日内上线时是过了4点的间隔，则先充活力值
		"""
		tick = Const.VIM_RESET_TIME + self.getToday0Tick()
		if time.time() >= tick:
			return self.role_last_offline < tick
		else:
			return self.role_last_offline < (tick-86400)
		
	def getToday0Tick( self ):
		"""
		获得当天0时时刻
		该接口看起来比较诡异，主要是对付时区引起的0时时刻不一致问题
		例如，目前俺们处于东8时区，从格林威治时间开始算，直接用time.time()/86400*86400的话，得到的不是零时而是早上8点
		所以，需要加上时区的差值timezone来调整0点时间，以获得当前机器时区的0点时刻
		"""
		return int( time.time() - time.timezone )/86400 * 86400 + time.timezone

	def chargeVimTimer( self ):
		"""
		补充活力值计时器
		"""
		if self.checkOverVimTick():		# 如果符合充值条件（4点前下线4点后上线）则先充值
			INFO_MSG( "chargeVimTimer: role %s(%i) can charge vim now %i."%( self.getName(), self.databaseID, int(time.time()) ) )
			self.cell.chargeVim()
			
		nowTime = int( time.time() )
		tick = Const.VIM_RESET_TIME + int( self.getToday0Tick() )	# 当日充值时刻（4点）
		leftTime = tick - nowTime
		if leftTime < 0:
			leftTime += 86400
			
		INFO_MSG( "chargeVimTimer: role name %s, tick %i, time %i, left time %i, last off line %i ."%( self.getName(), tick, nowTime, leftTime, self.role_last_offline ) )
		assert leftTime >= 0, "current time: %s, left time: %s" % ( nowTime, leftTime )
		self.vimChargeTimer = self.addTimer( leftTime + 10, 0.0, ECBExtend.LIVING_SYSTEM_VIM_CHARGER )	# 以整数化的时间作为参数
		
	def onTimer_livingSystemVimCharger( self, id, arg ):
		"""
		够钟补充活力值了
		"""
		INFO_MSG( "onTimer_livingSystemVimCharger role %s(%s) DBID %s"%( self.getName(), self.id, self.databaseID ) )
		self.cell.chargeVim()
		self.vimChargeTimer = self.addTimer( 86400, 0.0, ECBExtend.LIVING_SYSTEM_VIM_CHARGER )	# 以整数化的时间作为参数
		
	def liv_onLeave( self ):
		"""
		玩家下线时的一些处理
		"""
		if self.vimChargeTimer is not None:
			self.delTimer( self.vimChargeTimer )
			self.vimChargeTimer = None
		
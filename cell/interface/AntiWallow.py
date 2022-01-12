# -*- coding: gb18030 -*-
#
"""
防沉迷系统模块
2010.06.09: rewriten by huangyongwei
"""

import BigWorld
import csdefine
import csstatus
import csconst
import ECBExtend

# --------------------------------------------------------------------
OLTIME_HALF_LUCRE	= 3 * 3600					# 收益减半的在线时间点
OLTIME_NO_LUCRE		= 5 * 3600					# 零收益的在线时间点

NOTIFY_INTERVALS = {
	csdefine.WALLOW_STATE_COMMON	 : 3600,	# 正常游戏情况下，提示的时间间隔
	csdefine.WALLOW_STATE_HALF_LUCRE : 1800,	# 收益减半情况下，提示的时间间隔
	csdefine.WALLOW_STATE_NO_LUCRE	 : 60 * 15,	# 零收益情况下，提示的时间间隔
	}

NOTIFY_MSGS = {
	csdefine.WALLOW_STATE_COMMON	 : csstatus.ANTI_WALLOW_COMMON,
	csdefine.WALLOW_STATE_HALF_LUCRE : csstatus.ANTI_WALLOW_HALF_LUCRE,
	csdefine.WALLOW_STATE_NO_LUCRE	 : csstatus.ANTI_WALLOW_NO_LOCRE,
	}

class AntiWallow :
	"""
	未成年人防沉迷系统
	"""
	def __init__( self ) :
		"""
		初始化
		"""
		self.__lucreRate = 1.0					# 收益率（CELL_PUBLIC）
		self.cWallow_isAdult = False			# 是否是成年人（CELL_PRIVATE）

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __enterTiredState( self ) :
		"""
		进入疲劳状态
		"""
		self.__leaveUnhealthyState()
		spellID = 780001001
		self.spellTarget( spellID, self.id )
		self.__lucreRate = 0.5
		self.statusMessage( csstatus.ANTI_WALLOW_ENTER_HALF_LUCRE, OLTIME_HALF_LUCRE / 3600 )

	def __leaveTiredState( self ) :
		"""
		离开疲劳状态
		"""
		tiredBuffID = 299009
		self.removeAllBuffByBuffID( tiredBuffID, [csdefine.BUFF_INTERRUPT_NONE] )
		self.__lucreRate = 1.0

	def __enterUnhealthyState( self ) :
		"""
		进入不健康状态
		"""
		self.__leaveTiredState()
		spellID = 780002001
		self.spellTarget( spellID, self.id )
		self.__lucreRate = 0.0
		self.statusMessage( csstatus.ANTI_WALLOW_NO_LOCRE )

	def __leaveUnhealthyState( self ) :
		"""
		离开不健康状态
		"""
		unhealthyBuffID = 299010
		self.removeAllBuffByBuffID( unhealthyBuffID, [csdefine.BUFF_INTERRUPT_NONE] )
		self.__lucreRate = 1.0


	# ----------------------------------------------------------------
	# defined methods
	# ----------------------------------------------------------------
	def wallow_setAgeState( self, isAdult ) :
		"""
		defined.
		设置年龄状态
		@type			isAdult : BOOL
		@param			isAdult : 是否是成年
		注意：只给 base 调用
		"""
		self.cWallow_isAdult = isAdult
		self.__leaveTiredState()
		self.__leaveUnhealthyState()

	def wallow_onWallowNotify( self, state, olTime ) :
		"""
		defined.
		沉迷提醒
		@type			state  : MACRO DEFINATION
		@param			state  : 收益状态，在 csdefine 中定义：WALLOW_XXX
		@type			olTime : INT64
		@param			olTime : 在线时间
		注意：只给 base 调用
		"""
		if not self.wallow_isEffected() :
			return
		assert state in csconst.WALLOW_STATES, "Error anti-wallow state: %i" % state
		notifyInterval = NOTIFY_INTERVALS[state]									# 下次通知时间间隔
		nextNotifyTime = notifyInterval
		if state == csdefine.WALLOW_STATE_COMMON :
			if olTime > 0 :
				nextNotifyTime = notifyInterval - ( olTime % notifyInterval )
		elif state == csdefine.WALLOW_STATE_HALF_LUCRE :
			self.__enterTiredState()
			startTime = olTime - OLTIME_HALF_LUCRE
			if startTime > 0 :
				nextNotifyTime = notifyInterval - ( startTime % notifyInterval )
		elif state == csdefine.WALLOW_STATE_NO_LUCRE :
			self.__enterUnhealthyState()
			startTime = olTime - OLTIME_NO_LUCRE
			if startTime > 0 :
				nextNotifyTime = notifyInterval - ( startTime % notifyInterval )
		self.cancel( self.__notifyTimerID )
		self.__onlineTime = olTime
		self.addTimer( nextNotifyTime, 0, ECBExtend.WALLOW_PERIODIC_NOTIFY_CBID )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onWallowNotify( self, timerID, cbID ) :
		"""
		定期通知客户端
		"""
		state = csdefine.WALLOW_STATE_COMMON
		msgArg = ()
		if self.__onlineTime > OLTIME_NO_LUCRE :
			state = csdefine.WALLOW_STATE_NO_LUCRE
		elif self.__onlineTime > OLTIME_HALF_LUCRE :
			state = csdefine.WALLOW_STATE_HALF_LUCRE
		else :
			msgArg = ( self.__onlineTime / 3600, )
		interval = NOTIFY_INTERVALS[state]
		self.statusMessage( NOTIFY_MSGS[state], *msgArg )
		self.__notifyTimerID = self.addTimer( interval, 0, ECBExtend.WALLOW_PERIODIC_NOTIFY_CBID )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def wallow_isEffected( self ) :
		"""
		是否受防沉迷系统影响
		for real & ghost
		"""
		return BigWorld.globalData["AntiWallow_isApply"] and not self.cWallow_isAdult

	def wallow_getLucreRate( self ) :
		"""
		获取收益率
		for real & ghost
		"""
		return self.__lucreRate

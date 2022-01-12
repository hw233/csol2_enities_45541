# -*- coding: gb18030 -*-
#
"""
������ϵͳģ��
2010.06.09: rewriten by huangyongwei
"""

import BigWorld
import csdefine
import csstatus
import csconst
import ECBExtend

# --------------------------------------------------------------------
OLTIME_HALF_LUCRE	= 3 * 3600					# ������������ʱ���
OLTIME_NO_LUCRE		= 5 * 3600					# �����������ʱ���

NOTIFY_INTERVALS = {
	csdefine.WALLOW_STATE_COMMON	 : 3600,	# ������Ϸ����£���ʾ��ʱ����
	csdefine.WALLOW_STATE_HALF_LUCRE : 1800,	# �����������£���ʾ��ʱ����
	csdefine.WALLOW_STATE_NO_LUCRE	 : 60 * 15,	# ����������£���ʾ��ʱ����
	}

NOTIFY_MSGS = {
	csdefine.WALLOW_STATE_COMMON	 : csstatus.ANTI_WALLOW_COMMON,
	csdefine.WALLOW_STATE_HALF_LUCRE : csstatus.ANTI_WALLOW_HALF_LUCRE,
	csdefine.WALLOW_STATE_NO_LUCRE	 : csstatus.ANTI_WALLOW_NO_LOCRE,
	}

class AntiWallow :
	"""
	δ�����˷�����ϵͳ
	"""
	def __init__( self ) :
		"""
		��ʼ��
		"""
		self.__lucreRate = 1.0					# �����ʣ�CELL_PUBLIC��
		self.cWallow_isAdult = False			# �Ƿ��ǳ����ˣ�CELL_PRIVATE��

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __enterTiredState( self ) :
		"""
		����ƣ��״̬
		"""
		self.__leaveUnhealthyState()
		spellID = 780001001
		self.spellTarget( spellID, self.id )
		self.__lucreRate = 0.5
		self.statusMessage( csstatus.ANTI_WALLOW_ENTER_HALF_LUCRE, OLTIME_HALF_LUCRE / 3600 )

	def __leaveTiredState( self ) :
		"""
		�뿪ƣ��״̬
		"""
		tiredBuffID = 299009
		self.removeAllBuffByBuffID( tiredBuffID, [csdefine.BUFF_INTERRUPT_NONE] )
		self.__lucreRate = 1.0

	def __enterUnhealthyState( self ) :
		"""
		���벻����״̬
		"""
		self.__leaveTiredState()
		spellID = 780002001
		self.spellTarget( spellID, self.id )
		self.__lucreRate = 0.0
		self.statusMessage( csstatus.ANTI_WALLOW_NO_LOCRE )

	def __leaveUnhealthyState( self ) :
		"""
		�뿪������״̬
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
		��������״̬
		@type			isAdult : BOOL
		@param			isAdult : �Ƿ��ǳ���
		ע�⣺ֻ�� base ����
		"""
		self.cWallow_isAdult = isAdult
		self.__leaveTiredState()
		self.__leaveUnhealthyState()

	def wallow_onWallowNotify( self, state, olTime ) :
		"""
		defined.
		��������
		@type			state  : MACRO DEFINATION
		@param			state  : ����״̬���� csdefine �ж��壺WALLOW_XXX
		@type			olTime : INT64
		@param			olTime : ����ʱ��
		ע�⣺ֻ�� base ����
		"""
		if not self.wallow_isEffected() :
			return
		assert state in csconst.WALLOW_STATES, "Error anti-wallow state: %i" % state
		notifyInterval = NOTIFY_INTERVALS[state]									# �´�֪ͨʱ����
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
		����֪ͨ�ͻ���
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
		�Ƿ��ܷ�����ϵͳӰ��
		for real & ghost
		"""
		return BigWorld.globalData["AntiWallow_isApply"] and not self.cWallow_isAdult

	def wallow_getLucreRate( self ) :
		"""
		��ȡ������
		for real & ghost
		"""
		return self.__lucreRate

# -*- coding: gb18030 -*-
#

"""
����ϵͳģ��
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
		��ʼ��״̬��Ҫ��Fight��ʼ��֮ǰ
		"""
		self.vimChargeTimer = None
		
	def checkOverDay( self ):
		"""
		����Ƿ������ by ����
		"""
		t = self.getToday0Tick()
		return self.role_last_offline < t
		
	def checkOverVimTick( self ):
		"""
		����Ƿ������ֵʱ��
		
		���ͬ��������ʱ�ǹ���4��ļ�������ȳ����ֵ
		"""
		tick = Const.VIM_RESET_TIME + self.getToday0Tick()
		if time.time() >= tick:
			return self.role_last_offline < tick
		else:
			return self.role_last_offline < (tick-86400)
		
	def getToday0Tick( self ):
		"""
		��õ���0ʱʱ��
		�ýӿڿ������ȽϹ��죬��Ҫ�ǶԸ�ʱ�������0ʱʱ�̲�һ������
		���磬Ŀǰ���Ǵ��ڶ�8ʱ�����Ӹ�������ʱ�俪ʼ�㣬ֱ����time.time()/86400*86400�Ļ����õ��Ĳ�����ʱ��������8��
		���ԣ���Ҫ����ʱ���Ĳ�ֵtimezone������0��ʱ�䣬�Ի�õ�ǰ����ʱ����0��ʱ��
		"""
		return int( time.time() - time.timezone )/86400 * 86400 + time.timezone

	def chargeVimTimer( self ):
		"""
		�������ֵ��ʱ��
		"""
		if self.checkOverVimTick():		# ������ϳ�ֵ������4��ǰ����4������ߣ����ȳ�ֵ
			INFO_MSG( "chargeVimTimer: role %s(%i) can charge vim now %i."%( self.getName(), self.databaseID, int(time.time()) ) )
			self.cell.chargeVim()
			
		nowTime = int( time.time() )
		tick = Const.VIM_RESET_TIME + int( self.getToday0Tick() )	# ���ճ�ֵʱ�̣�4�㣩
		leftTime = tick - nowTime
		if leftTime < 0:
			leftTime += 86400
			
		INFO_MSG( "chargeVimTimer: role name %s, tick %i, time %i, left time %i, last off line %i ."%( self.getName(), tick, nowTime, leftTime, self.role_last_offline ) )
		assert leftTime >= 0, "current time: %s, left time: %s" % ( nowTime, leftTime )
		self.vimChargeTimer = self.addTimer( leftTime + 10, 0.0, ECBExtend.LIVING_SYSTEM_VIM_CHARGER )	# ����������ʱ����Ϊ����
		
	def onTimer_livingSystemVimCharger( self, id, arg ):
		"""
		���Ӳ������ֵ��
		"""
		INFO_MSG( "onTimer_livingSystemVimCharger role %s(%s) DBID %s"%( self.getName(), self.id, self.databaseID ) )
		self.cell.chargeVim()
		self.vimChargeTimer = self.addTimer( 86400, 0.0, ECBExtend.LIVING_SYSTEM_VIM_CHARGER )	# ����������ʱ����Ϊ����
		
	def liv_onLeave( self ):
		"""
		�������ʱ��һЩ����
		"""
		if self.vimChargeTimer is not None:
			self.delTimer( self.vimChargeTimer )
			self.vimChargeTimer = None
		
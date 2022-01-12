# -*- coding: utf-8 -*-

from bwdebug import *
import BigWorld
import Pixie
import Define
import Math
import time
import csol

# ------------------------------------------------------------------------------
# Class EnvironmentsEffectMgr:
# ����Ч��������
# ���ڹ��������˼�汾�߻���Ҫ�ĵ�ͼ����Ч��
# ����ر���Ч����������պС����Ͽ�����Ч�����ر���պС�
# Ч��֮��Ĺ��ɽ��ɽű���ģ��ʵ�֡�
# ------------------------------------------------------------------------------
PER_TICK_TIME		= 60.0			# ����ʱ�������룩

DAY_START_TIME		= 8.50			# ������ʼ����ʱ��
DAY_END_TIME		= 9.00			# ������������ʱ��
NIGHT_START_TIME	= 23.50			# ��ڿ�ʼ����ʱ��
NIGHT_END_TIME		= 24.00			# ��ڽ�������ʱ��


FOG_DENSITY_MIN		= 0.1			# ����ܶ���СЧ��
FOG_DENSITY_MAX		= 1.5			# ����ܶ����Ч��
FOG_AMOUNT_MIN		= 0.0			# ��Ӱ����պеĽ�����СЧ��
FOG_AMOUNT_MAX		= 0.8			# ��Ӱ����պеĽ������Ч��
FOG_NEAR_MIN		= 0.0			# �����ɢ�ܶ���СЧ��
FOG_NEAR_MAX		= 0.5			# �����ɢ�ܶ����Ч��

class EnvironmentsEffectMgr:
	__instance = None

	def __init__( self ):
		assert EnvironmentsEffectMgr.__instance is None
		self.timerID = 0

	@classmethod
	def instance( SELF ):
		if SELF.__instance is None:
			SELF.__instance = EnvironmentsEffectMgr()
		return SELF.__instance

	def start( self ):
		"""
		�������
		"""
		self.startTimer()
		self.timerID = BigWorld.callback( PER_TICK_TIME, self.start )

	def stop( self ):
		"""
		�رռ��
		"""
		BigWorld.cancelCallback( self.timerID )

	def updateTime( self ):
		"""
		ͬ����ʵʱ�䣬���õ�ͼ��TimeOfDayΪ��ʵʱ��
		"""
		self.startTimer()

	def startTimer( self ):
		"""
		"""
		currTime = time.localtime()
		hour = currTime[3]
		per = currTime[4]
		changePer = per/60.0
		changeTime = hour + changePer
		self.onTimeChange( changeTime )

	def onTimeChange( self, changeTime ):
		"""
		Ч������
		"""
		if changeTime >= DAY_START_TIME and changeTime <= DAY_END_TIME:
			# ����ʱ��Ӱ����Ч��
			csol.enableTimeOfDay( True )
			csol.setGameTime( changeTime )
			# ������
			csol.enableFog( True )
			p = 1 - ( changeTime - DAY_START_TIME)/( DAY_END_TIME - DAY_START_TIME )
			# ʹ���������������
			csol.useFixedFogAmount( True )
			fogAmount = FOG_AMOUNT_MIN + ( FOG_AMOUNT_MAX - FOG_AMOUNT_MIN ) * p
			csol.fixedFogAmount( fogAmount )
			# ����ʱ��ֵȷ�����ܶȱ���
			fogDensity = FOG_DENSITY_MIN + ( FOG_DENSITY_MAX - FOG_DENSITY_MIN ) * p
			if fogDensity < 0.1: fogDensity = 0.1
			csol.useFixedDensity( True )
			csol.fixedDensity( fogDensity )
			# ʹ����near��������
			csol.useFixedNearMultiplier( True )
			nearAmount = FOG_NEAR_MIN + ( FOG_NEAR_MAX - FOG_NEAR_MIN ) * p
			csol.fixedNearMultiplier( nearAmount )
		elif changeTime > DAY_END_TIME and changeTime < NIGHT_START_TIME:
			# �ر�ʱ��Ӱ����Ч��
			csol.enableTimeOfDay( False )
			# �ر���
			csol.enableFog( False )
		elif changeTime >= NIGHT_START_TIME and changeTime <= NIGHT_END_TIME:
			# ����ʱ��Ӱ����Ч��
			csol.enableTimeOfDay( True )
			csol.setGameTime( changeTime )
			# ������
			csol.enableFog( True )
			p = ( changeTime - NIGHT_START_TIME)/( NIGHT_END_TIME - NIGHT_START_TIME )
			# ʹ���������������
			csol.useFixedFogAmount( True )
			fogAmount = FOG_AMOUNT_MIN + ( FOG_AMOUNT_MAX - FOG_AMOUNT_MIN ) * p
			csol.fixedFogAmount( fogAmount )
			# ����ʱ��ֵȷ�����ܶȱ���
			fogDensity = FOG_DENSITY_MIN + ( FOG_DENSITY_MAX - FOG_DENSITY_MIN ) * p
			if fogDensity < 0.1: fogDensity = 0.1
			csol.useFixedDensity( True )
			csol.fixedDensity( fogDensity )
			# ʹ����near��������
			nearAmount = FOG_NEAR_MIN + ( FOG_NEAR_MAX - FOG_NEAR_MIN ) * p
			csol.useFixedNearMultiplier( True )
			csol.fixedNearMultiplier( nearAmount )
		else:
			# ����ʱ��Ӱ����Ч��
			csol.enableTimeOfDay( True )
			csol.setGameTime( changeTime )
			# ������
			csol.enableFog( True )
			# ʹ���������������
			csol.useFixedFogAmount( True )
			csol.fixedFogAmount( FOG_AMOUNT_MAX )
			# ʹ��������ܶȱ���
			csol.useFixedDensity( True )
			csol.fixedDensity( FOG_DENSITY_MAX )
			# ʹ�������near��������
			csol.useFixedNearMultiplier( True )
			csol.fixedNearMultiplier( FOG_NEAR_MAX )

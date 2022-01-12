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
# 坏境效果管理器
# 用于管理天上人间版本策划想要的地图环境效果
# 白天关闭雾效果，开启天空盒。晚上开启雾效果，关闭天空盒。
# 效果之间的过渡将由脚本层模拟实现。
# ------------------------------------------------------------------------------
PER_TICK_TIME		= 60.0			# 渐变时间间隔（秒）

DAY_START_TIME		= 8.50			# 天亮开始渐变时间
DAY_END_TIME		= 9.00			# 天亮结束渐变时间
NIGHT_START_TIME	= 23.50			# 天黑开始渐变时间
NIGHT_END_TIME		= 24.00			# 天黑结束渐变时间


FOG_DENSITY_MIN		= 0.1			# 雾的密度最小效果
FOG_DENSITY_MAX		= 1.5			# 雾的密度最大效果
FOG_AMOUNT_MIN		= 0.0			# 雾影响天空盒的渐变最小效果
FOG_AMOUNT_MAX		= 0.8			# 雾影响天空盒的渐变最大效果
FOG_NEAR_MIN		= 0.0			# 雾的扩散密度最小效果
FOG_NEAR_MAX		= 0.5			# 雾的扩散密度最大效果

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
		开启检测
		"""
		self.startTimer()
		self.timerID = BigWorld.callback( PER_TICK_TIME, self.start )

	def stop( self ):
		"""
		关闭检测
		"""
		BigWorld.cancelCallback( self.timerID )

	def updateTime( self ):
		"""
		同步现实时间，设置地图的TimeOfDay为现实时间
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
		效果设置
		"""
		if changeTime >= DAY_START_TIME and changeTime <= DAY_END_TIME:
			# 开启时间影响雾效果
			csol.enableTimeOfDay( True )
			csol.setGameTime( changeTime )
			# 开启雾化
			csol.enableFog( True )
			p = 1 - ( changeTime - DAY_START_TIME)/( DAY_END_TIME - DAY_START_TIME )
			# 使用天空雾化比例因子
			csol.useFixedFogAmount( True )
			fogAmount = FOG_AMOUNT_MIN + ( FOG_AMOUNT_MAX - FOG_AMOUNT_MIN ) * p
			csol.fixedFogAmount( fogAmount )
			# 根据时间值确定雾密度比例
			fogDensity = FOG_DENSITY_MIN + ( FOG_DENSITY_MAX - FOG_DENSITY_MIN ) * p
			if fogDensity < 0.1: fogDensity = 0.1
			csol.useFixedDensity( True )
			csol.fixedDensity( fogDensity )
			# 使用雾化near比例因子
			csol.useFixedNearMultiplier( True )
			nearAmount = FOG_NEAR_MIN + ( FOG_NEAR_MAX - FOG_NEAR_MIN ) * p
			csol.fixedNearMultiplier( nearAmount )
		elif changeTime > DAY_END_TIME and changeTime < NIGHT_START_TIME:
			# 关闭时间影响雾效果
			csol.enableTimeOfDay( False )
			# 关闭雾化
			csol.enableFog( False )
		elif changeTime >= NIGHT_START_TIME and changeTime <= NIGHT_END_TIME:
			# 开启时间影响雾效果
			csol.enableTimeOfDay( True )
			csol.setGameTime( changeTime )
			# 开启雾化
			csol.enableFog( True )
			p = ( changeTime - NIGHT_START_TIME)/( NIGHT_END_TIME - NIGHT_START_TIME )
			# 使用天空雾化比例因子
			csol.useFixedFogAmount( True )
			fogAmount = FOG_AMOUNT_MIN + ( FOG_AMOUNT_MAX - FOG_AMOUNT_MIN ) * p
			csol.fixedFogAmount( fogAmount )
			# 根据时间值确定雾密度比例
			fogDensity = FOG_DENSITY_MIN + ( FOG_DENSITY_MAX - FOG_DENSITY_MIN ) * p
			if fogDensity < 0.1: fogDensity = 0.1
			csol.useFixedDensity( True )
			csol.fixedDensity( fogDensity )
			# 使用雾化near比例因子
			nearAmount = FOG_NEAR_MIN + ( FOG_NEAR_MAX - FOG_NEAR_MIN ) * p
			csol.useFixedNearMultiplier( True )
			csol.fixedNearMultiplier( nearAmount )
		else:
			# 开启时间影响雾效果
			csol.enableTimeOfDay( True )
			csol.setGameTime( changeTime )
			# 开启雾化
			csol.enableFog( True )
			# 使用天空雾化比例因子
			csol.useFixedFogAmount( True )
			csol.fixedFogAmount( FOG_AMOUNT_MAX )
			# 使用最大雾密度比例
			csol.useFixedDensity( True )
			csol.fixedDensity( FOG_DENSITY_MAX )
			# 使用最大雾化near比例因子
			csol.useFixedNearMultiplier( True )
			csol.fixedNearMultiplier( FOG_NEAR_MAX )

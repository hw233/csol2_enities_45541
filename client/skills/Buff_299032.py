# -*- coding: gb18030 -*-
#
# edit by wuxo 2012-2-29 实现40级副本 玩家飞行骑宠按照路径移动

"""
BUFF技能类。
"""

import BigWorld
from gbref import rds
from bwdebug import *
from SpellBase import Buff
from Buff_onPatrol import Buff_onPatrol
from Function import Functor
import event.EventCenter as ECenter

class Buff_299032( Buff_onPatrol ):
	"""
	玩家飞行骑宠按照路径进行圆滑曲线移动
	"""
	def __init__( self ):
		"""
		从sect构造SkillBase
		@param sect:			技能配置文件的XML Root Section
		@type sect:				DataSection
		"""
		Buff_onPatrol.__init__( self )
		self._flyPath  = ""
		self._startPosCount = 0
		self._isLoopPoint   = 0
		self._isHideUI = 0
		self._linkFlyPath = "" #传送无缝连接的飞行路线
		self._cbid = 0
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置字典数据
		@type dict:				Python dict
		"""
		Buff_onPatrol.init( self, dict )
		paths = str( dict[ "Param2" ] ).split(";")
		if len( paths ) > 0:
			self._flyPath = paths[0]
		if len( paths ) > 1:
			self._linkFlyPath = paths[1]
		
		flyInfos = str( dict[ "Param3" ] ).split(";") # "3;4;50"
		if len(flyInfos) > 2:
			self._startPosCount = int( flyInfos[0] )
			self._isLoopPoint = int( flyInfos[1] )
		if len(flyInfos) > 3:
			self._isHideUI = int( flyInfos[3] )
		
	def cast( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff_onPatrol.cast( self, caster, target )
		if target.id == BigWorld.player().id:
			self.onVehicleModelLoadFinish()
	
	def onVehicleModelLoadFinish( self ):
		if BigWorld.player().onFlyModelLoadFinished is False:
			self._cbid = BigWorld.callback( 0.1, self.onVehicleModelLoadFinish ) #检测模型是否加载完成，加载完成就开始飞行，如果没有加载完，就每隔0.1秒再检测一次
		else:
			BigWorld.player().physics.fall = False
			rds.roleFlyMgr.startRoleFly( self._flyPath, self._startPosCount, self._isLoopPoint)
			if self._isHideUI:
				ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", not self._isHideUI )
			BigWorld.player().onFlyModelLoadFinished = False
			BigWorld.player().continueFlyPath = self._linkFlyPath
		
	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff_onPatrol.end( self, caster, target )
		if self._cbid > 0:
			BigWorld.cancelCallback( self._cbid )
		if target.id == BigWorld.player().id:
			rds.roleFlyMgr.stopFly( False )
			BigWorld.player().physics.fall = True
			if self._isHideUI:
				ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", self._isHideUI )
		
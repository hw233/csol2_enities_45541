# -*- coding: gb18030 -*-

import BigWorld
import Math
import csconst
import ECBExtend
from SkillTrap import SkillTrap
from bwdebug import *

class MoveTrap( SkillTrap ):
	"""
	可移动的陷阱
	"""
	def __init__( self ):
		"""
		"""
		SkillTrap.__init__( self )
		self.dstPos = Math.Vector3()
		self.isSafe = True
		self.lifeTimer = 0

	def setDstPos( self, pos ):
		"""
		设置运动到的目标点
		"""
		if not self.isReal():
			self.remoteCall( "setDstPos", ( pos ) )
		else:
			self.dstPos = Math.Vector3( pos )

	def setSafe( self, isSafe ):
		"""
		设置陷阱是否无效
		"""
		if not self.isReal():
			self.remoteCall( "setSafe", ( isSafe ) )
		else:
			self.isSafe = isSafe

	def setLifeTime( self, lifeTime ):
		"""
		设置陷阱存活时间
		"""
		if not self.isReal():
			self.remoteCall( "setLifeTime", ( lifeTime ) )
		else:
			# 开启存活Timer
			self.lifetime = lifeTime
			self.lifeTimer = self.addTimer( lifeTime, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )

	def delayLineToPoint( self, delayTime ):
		"""
		延迟运动
		"""
		self.addTimer( delayTime, 0, ECBExtend.DELAY_LINE_TO_POINT_TIMER_CBID )

	def onDelayLineToPointTimer( self, timerID, cbID ):
		"""
		开始运动到目标点
		"""
		self.setSafe( False ) 		# 设置陷阱为有效
		self.startEnterTrapDo()		# 进入陷阱检测
		self.planesAllClients( "moveToPosFC", ( self.dstPos, self.move_speed, True ) ) # 客户端飞行表现
		self.lineToPoint( self.dstPos, self.move_speed, True )		 # 服务器飞行表现

	def enterTrapDo( self, entity ):
		"""
		进入陷阱调用
		"""
		if self.isSafe: return  # 如果陷阱无效
		SkillTrap.enterTrapDo( self, entity )

	def leaveTrapDo( self, entity ):
		"""
		离开陷阱调用
		"""
		if self.isSafe: return	# 如果陷阱无效
		SkillTrap.leaveTrapDo( self, entity )

	def onDestroySelfTimer( self, timerID, cbID ):
		"""
		virtual method.
		删除自身
		"""
		self.delayDestroySelf()

	def delayDestroySelf( self ):
		"""
		延迟销毁自身，需要做entity离开陷阱
		"""
		if self.isTrigger and self.lifeTimer > 0:	# 被提前触发销毁了
			self.cancel( self.lifeTimer )
			self.lifeTimer = 0
		self.planesAllClients( "onDestroy", () )	 # 客户端表现
		self.setSafe( True )		 # 设为无效
		self.addTimer( csconst.MOVE_TRAP_DELAY_DESTROY_TIME, 0, ECBExtend.DELAY_DESTROY_SELF_TIMER_CBID )

	def onDelayDestroySelfTimer( self, timerID, cbID ):
		"""
		正式销毁自身
		"""
		self.destroy()

	def startEnterTrapDo( self ):
		"""
		刚开始运动的时候再作一次进入陷阱检测。
		防止如果陷阱与目标刚好在很近的位置而没有伤害的情况出现
		"""
		entities = self.entitiesInRangeExt( self.radius )
		for entity in entities:
			if abs( entity.position.y - self.position.y ) < self.radius:
				self.enterTrapDo( entity )

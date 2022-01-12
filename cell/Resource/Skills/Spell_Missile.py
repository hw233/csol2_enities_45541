# -*- coding: gb18030 -*-

import BigWorld
import Math
import math
import csarithmetic
from SpellBase import *

CIR_ANGLE = 360.0

class Spell_Missile( Spell):
	"""
	导弹技能
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.radius = 0.0				# 导弹触发半径
		self.isDisposable = 0			# 是否一次性导弹（即触发一次就销毁）
		self.enterSpell = 0				# 触发导弹施放的技能
		self.leaveSpell = 0				# 离开导弹施放的技能
		self.modelNumber =  ""			# 导弹对应的模型(带光效的)
		self.modelScale = 1.0			# 导弹模型缩放比例
		self.speed = 0.0				# 导弹移动速度
		self.distance = 0.0				# 导弹飞行距离
		self.mount = 0					# 导弹个数
		self.angle = CIR_ANGLE			# 导弹发射角度
		self.offsetAngle = 0.0			# 导弹向右偏移角度
		self.delayTime = 0.0			# 导弹延迟运动时间

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		d1 = str( dict["param1"] ).split(";")
		if len( d1 ) >= 2:
			self.radius = float( d1[0] )
			self.isDisposable = int ( d1[1] )
		d2 = str( dict["param2"] ).split(";")
		if len( d2 ) >= 2:
			self.enterSpell = int( d2[0] )
			self.leaveSpell = int( d2[1] )
		d3 = str( dict["param3"] ).split(";")
		if len( d3 ) >= 2:
			self.modelNumber = str( d3[0] )
			self.modelScale = float( d3[1] )
		d4 = str( dict["param4"] ).split(";")
		if len( d4 ) >= 2:
			self.speed = float( d4[0] )
			self.distance = float( d4[1] )
			try:
				self.delayTime = float( d4[2] )
			except:
				self.delayTime = 0.0	# 默认不延迟
		d5 = str( dict["param5"] ).split(";")
		if len( d5 ) >= 3:
			self.mount = int( d5[0] )
			self.angle = float( d5[1] )
			self.offsetAngle = float( d5[2] )

	def _getDict( self, caster, target ):
		"""
		"""
		dict = { "radius" : self.radius, \
			"enterSpell" : self.enterSpell, \
			"leaveSpell" : self.leaveSpell, \
			"originSkill" : self.getID(), \
			"modelNumber" : self.modelNumber, \
			"isDisposable" : self.isDisposable, \
			"lifetime" : 0, \
			"casterID" : caster.id, \
			"uname" : self.getName(), \
			"isSafe" : True  }  # 陷阱刚开始创建默认为无效

		return dict

	def use( self, caster, target ):
		"""
		预处理，创建导弹entity
		"""
		pos = caster.position
		spaceID = caster.spaceID
		yaw = caster.yaw
		dir = caster.direction
		trapList = []
		for i in range( self.mount ):
			trap = caster.createEntityNearPlanes( "MoveTrap", pos, dir, self._getDict( caster, target ) )
			trap.position = pos						# 修正导弹的位置
			trap.modelScale = self.modelScale		# 设置导弹模型的缩放比例
			trap.move_speed = self.speed			# 设置导弹速度
			mount = float( self.mount )
			i = float( i )
			# 导弹发射角度的计算
			# 发射角度 = 角色当前角度 + 导弹向右偏移角度 + 导弹发射角度/2 - 导弹发射角度*每个导弹的偏移角度百分比
			if self.angle == CIR_ANGLE:		# 导弹发射角度为360度的特殊情况
				y = yaw + (math.pi*2) * (self.offsetAngle/CIR_ANGLE) + (math.pi*2) * (i/mount)
			else:
				try:
					y = yaw + (math.pi*2) * (self.offsetAngle/CIR_ANGLE) + (math.pi*2) * (self.angle/(CIR_ANGLE*2.0)) - (math.pi*2) * (self.angle/CIR_ANGLE) * (i/(mount-1.0))
				except:		# 导弹数量等于1的情况
					y = yaw + (math.pi*2) * (self.offsetAngle/CIR_ANGLE)
			direction = Math.Vector3( math.sin( y ), 0, math.cos( y ) )
			direction.normalise()
			dstPos = pos + direction * self.distance
			endDstPos = csarithmetic.getCollidePoint( spaceID, pos, dstPos )	# 作碰撞
			lifeTime = endDstPos.flatDistTo( pos ) / self.speed		# 重新计算存活时间
			lifeTime += self.getIntonateTime( caster )  # 加上预处理时间（即吟唱时间）
			lifeTime += self.delayTime	# 加上延迟运动时间
			trap.setLifeTime( lifeTime )
			trap.setDstPos( endDstPos )
			trapList.append( trap )

		caster.setTemp( "MOVE_TRAP_LIST", trapList )
		Spell.use( self, caster, target )

	def cast( self, caster, target ):
		"""
		施放技能，导弹该出发了
		"""
		Spell.cast( self, caster, target )  # 客户端光效等

		trapList = caster.queryTemp( "MOVE_TRAP_LIST", [] )
		for trap in trapList:
			trap.delayLineToPoint( self.delayTime )		# 延迟运动

	def onSpellInterrupted( self, caster ):
		"""
		当施法被打断时的通知；
		打断后需要做一些事情,销毁导弹
		"""
		trapList = caster.queryTemp( "MOVE_TRAP_LIST", [] )
		for trap in trapList:
			trap.destroy()
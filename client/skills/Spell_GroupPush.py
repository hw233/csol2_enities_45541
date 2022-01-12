# -*- coding: gb18030 -*-

"""
Spell技能类。
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csarithmetic
import Math
import math
from gbref import rds

class Spell_GroupPush( Spell ):
	"""
	群体位移
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )

		# 施法者位移数据
		self.casterMoveSpeed = 0.0
		self.casterMoveDistance = 0.0
		# 受术者位移数据
		self.targetMoveSpeed = 0.0
		self.targetMoveDistance = 0.0

		self.param1 = 0
		self.param2 = 0

	def init( self, data ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, data )

		param1 = data["param1"].split(";")
		self.param1 = len( param1 )
		if self.param1 >= 2:
			self.casterMoveSpeed = float( param1[0] )
			self.casterMoveDistance = float( param1[1] )
		param2 = data["param2"].split(";")
		self.param2 = len( param2 )
		if self.param2 >= 2:
			self.targetMoveSpeed = float( param2[0] )
			self.targetMoveDistance = float( param2[1] )

	def cast( self, caster, targetObject ):
		"""
		virtual method
		系统施放，没有吟唱体，所以都是瞬发
		"""
		Spell.cast( self, caster, targetObject )

		target = targetObject.getObject()
		# 施法者位移
		if self.casterMoveDistance == 0.0:
			yaw = target.yaw
			dstPos = target.position - Math.Vector3( math.sin(yaw), 0, math.cos(yaw) ) * target.distanceBB( target )
		else:
			direction = Math.Vector3( target.position ) - Math.Vector3( caster.position )
			direction.normalise()
			if direction == Math.Vector3():    #施法者与受术者刚好在一个位置
				yaw = caster.yaw
				direction = direction - ( Math.Vector3( math.sin(yaw), 0, math.cos(yaw) ) )
			dstPos = caster.position + direction * self.casterMoveDistance
		endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
		if self.casterMoveSpeed and self.param1 >= 2:
			if caster == BigWorld.player():
				def __onMoveOver( success ):
					caster.stopMove()
					if not  success:
						DEBUG_MSG( "player move is failed." )
					rds.skillEffect.interrupt( caster )#光效中断
				caster.moveToDirectly( endDstPos, __onMoveOver )

	def receiveSpell( self, target, casterID, damageType, damage  ):
		"""
		接受技能处理

		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		player = BigWorld.player()
		caster = None
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				#这里会出错误的原因是 在服务器上一个entity对另一个entity施法 服务器上是看的到施法者的
				#而客户端可能会因为某原因 如：网络延迟 而在本机没有更新到AOI中的那个施法者entity所以
				#会产生这种错误 written by kebiao.  2008.1.8
				return

		# 动作光效部分
		self._skillAE( player, target, caster, damageType, damage  )

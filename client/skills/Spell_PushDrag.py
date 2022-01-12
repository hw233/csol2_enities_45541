# -*- coding:gb18030 -*-

"""
Spell技能类
"""
from SpellBase.Spell import Spell
from bwdebug import *
import BigWorld
import Math
import Define

class Spell_PushDrag( Spell ):
	"""
    增进玩家间互动的娱乐道具 
	"""
	def __init__( self ):
		"""
		构造函数
		"""
		Spell.__init__( self )
		self.targetMoveDistance = 0.0				# 水平连线方向的移动位移，为正表示将技能目标沿水平连线往外推若干米，若为负则表示将技能目标沿水平连线往释放者方向拉近若干米，若填0则直接拉到施法者面前

	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		if dict["param1"]:
			self.targetMoveDistance = float( dict["param1"] )

	def cast( self, caster, targetObject ):
		"""
		virtual method.
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		target = targetObject.getObject()
		if target.id == BigWorld.player().id:
			def moveOver( success ):
				target.stopMove()
				if not  success:
					DEBUG_MSG( "player move is failed." )
			direction = Math.Vector3( target.position ) - Math.Vector3( caster.position )	   # 得到水平连线的向量
			direction.normalise()					# 获得单位向量

			# 当受术者起始位置与施法者位置刚好在同一个点的情况
			if direction == Math.Vector3():
				direction = Math.Vector3( caster.position )
				direction.normalise()

			# 得到受术者目标点
			if self.targetMoveDistance == 0.0:
				dstPos = caster.position
			else:
				dstPos = target.position + direction * self.targetMoveDistance
			dstPos = Math.Vector3( dstPos )
			if target.isMoving():
				target.stopMove()
				target.moveToDirectly( dstPos, moveOver )
			else:
				target.moveToDirectly( dstPos, moveOver )

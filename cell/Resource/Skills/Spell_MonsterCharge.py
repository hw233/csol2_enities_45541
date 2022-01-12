# -*- coding:gb18030 -*-

#edit by wuxo 2014-1-8
"""
怪物专用冲锋技能
支持冲锋多少米、冲锋到目标boundingbox前
"""

import Math
import csdefine
import csarithmetic
from Spell_PhysSkillImprove import Spell_PhysSkillImprove

class Spell_MonsterCharge( Spell_PhysSkillImprove ):
	"""
	怪物专用冲锋技能
	"""
	def __init__( self ):
		"""
		"""
		Spell_PhysSkillImprove.__init__( self )
		self.casterMoveDistance = 0.0	#冲刺距离
		self.casterMoveSpeed    = 0.0	#冲刺速度
		self.traceDis           = 0.0  #保持靠近距离
		self.delayTime  	= 0.0 #技能伤害效果延迟时间

	def init( self, data ):
		"""
		"""
		Spell_PhysSkillImprove.init( self, data )
		param2 = data["param2"].split(";")
		if len( param2 ) > 0:
			self.casterMoveSpeed = float( param2[0] )
		if len( param2 ) > 1:	
			self.casterMoveDistance = float( param2[1] )
		if len( param2 ) > 2:	
			self.traceDis = float( param2[2] )	

	def calcDelay( self, caster, target ):
		"""
		virtual method.
		取得伤害延迟
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: float(秒)
		"""
		return  self.delayTime

	def cast( self, caster, target ) :
		"""
		virtual method
		"""
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ): return #怪物专用
		# 施法者位移
		en = target.getObject()
		dis = self.getDistance( caster, en )
		self.delayTime = dis / self.casterMoveSpeed
		if self.casterMoveSpeed and dis:
			direction = en.position - caster.position
			direction.normalise()
			dstPos = caster.position + direction * dis
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, Math.Vector3( endDstPos[0],endDstPos[1]+3,endDstPos[2]), Math.Vector3( endDstPos[0],endDstPos[1]-3,endDstPos[2]) )
			caster.moveToPosFC( endDstPos, self.casterMoveSpeed, True )
		Spell_PhysSkillImprove.cast( self, caster, target )
	
	def getDistance( self, caster, target ):
		"""
		获得施法者要冲刺的距离
		"""
		if self.casterMoveDistance > 0.0: #如果配置了冲刺距离
			return self.casterMoveDistance
		else:  #没有配置冲刺距离，就采用boundingbox距离计算
			return caster.distanceBB( target ) - self.traceDis
	
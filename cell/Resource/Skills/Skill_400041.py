# -*- coding:gb18030 -*-

from Skill_Posture import Skill_Posture

class Skill_400041( Skill_Posture ):
	"""
	姿态技能 心魔
	
	例：每等级提高X点法术命中
	"""
	def init( self, data ):
		"""
		"""
		Skill_Posture.init( self, data )
		self._param2 = float( data[ "param2" ] if len( data[ "param2" ] ) > 0 else 0 ) * 100
		
	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		为目标附上一个效果，通常被附上的效果是实例自身，它可以通过detach()去掉这个效果。具体效果由各派生类自行决定。
		
		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		if not ownerEntity.isPosture( self.getEffectPosture() ):
			return
		ownerEntity.magic_hitProbability_value += self._param2
		ownerEntity.calcMagicHitProbability()
		
	def detach( self, ownerEntity ):
		"""
		virtual method
		执行与attach()的反向操作

		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		if not ownerEntity.isPosture( self.getEffectPosture() ):
			return
		ownerEntity.magic_hitProbability_value -= self._param2
		ownerEntity.calcMagicHitProbability()
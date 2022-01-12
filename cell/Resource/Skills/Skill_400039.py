# -*- coding: gb18030 -*-
#


from Skill_Posture import Skill_Posture
from bwdebug import *

class Skill_400039( Skill_Posture ):
	"""
	姿态被动技能
	
	每等级提高X点暴击
	"""
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Skill_Posture.init( self, dict )
		self._param2 = float( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 ) * 100
		
	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		为目标附上一个效果，通常被附上的效果是实例自身，它可以通过detach()去掉这个效果。具体效果由各派生类自行决定。
		
		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		if not ownerEntity.isPosture( self.getEffectPosture() ):
			return
		ownerEntity.double_hit_probability_value += self._param2
		ownerEntity.calcDoubleHitProbability()
		
	def detach( self, ownerEntity ):
		"""
		virtual method
		执行与attach()的反向操作

		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		if not ownerEntity.isPosture( self.getEffectPosture() ):
			return
		ownerEntity.double_hit_probability_value -= self._param2
		ownerEntity.calcDoubleHitProbability()
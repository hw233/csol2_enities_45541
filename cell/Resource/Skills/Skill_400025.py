# -*- coding: gb18030 -*-
#


from SpellBase import *
from Skill_Normal import Skill_Normal
import csdefine
import random

class Skill_400025( Skill_Normal ):
	"""
	提高你的法术攻击力，数值相当于智力值*2%。

	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Skill_Normal.__init__( self )
	
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )
		self._param = float( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0.0 ) 	
		
	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		为目标附上一个效果，通常被附上的效果是实例自身，它可以通过detach()去掉这个效果。具体效果由各派生类自行决定。
		
		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.magic_damage_value += int( ownerEntity.intellect * self._param )
		ownerEntity.calcMagicDamage()
		
	def detach( self, ownerEntity ):
		"""
		virtual method
		执行与attach()的反向操作

		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.magic_damage_value -= int( ownerEntity.intellect * self._param )
		ownerEntity.calcMagicDamage()
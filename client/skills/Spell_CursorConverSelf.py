# -*- coding: gb18030 -*-

"""
Spell技能类。
"""
import BigWorld
import Math
import gbref
from SpellBase import *
import csstatus
from Spell_Cursor import Spell_Cursor
import SkillTargetObjImpl
from Function import Functor

"""
向当前鼠标方向的位置进行施法
"""
class Spell_CursorConverSelf( Spell_Cursor ):
	def __init__( self ):
		"""
		"""
		Spell_Cursor.__init__( self )
	
	def spell( self, caster, target ):
		spellTarget = SkillTargetObjImpl.createTargetObjEntity( caster )
		Spell_Cursor.spell(self, caster, spellTarget)
	
	def validTarget( self, caster, target ):
		return csstatus.SKILL_GO_ON

class Spell_CursorMultAttack( Spell_CursorConverSelf ):
	# 鼠标方向分多次伤害
	def __init__( self ):
		Spell_CursorConverSelf.__init__( self )

	def init( self, dict ):
		Spell_CursorConverSelf.init( self, dict )
		self._attackCount = int( dict[ "param1" ] )
		if self._attackCount <= 0: self._attackCount = 1
	
	def receiveSpell( self, target, casterID, damageType, damage ):
		"""
		接受技能处理
		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		player = BigWorld.player()
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				#这里会出错误的原因是 在服务器上一个entity对另一个entity施法 服务器上是看的到施法者的
				#而客户端可能会因为某原因 如：网络延迟 而在本机没有更新到AOI中的那个施法者entity所以
				#会产生这种错误 written by kebiao.  2008.1.8
				return
		else:
			caster = None

		count = 1
		if damage > 0:
			p2 = damage
			param2 /= self._attackCount
			if target.HP < p2:
				count = target.HP / damage + 1
			else:
				count = self._attackCount
		# 动作光效部分
		self._skillAE( player, target, caster, damageType, damage  )
		self.showSkillInfo( count, player, target, casterID, damageType, damage  )

	def showSkillInfo( self, attackCount, player, target, casterID, param1, param2 ):
		"""
		# 伤害信息提示
		"""
		if target.isAlive():
			target.onReceiveDamage( casterID, self, param1, param2 )							# 系统信息
			if attackCount > 1:
				BigWorld.callback( 0.3, Functor( self.showSkillInfo, attackCount - 1, player, target, casterID, param1, param2 ) )

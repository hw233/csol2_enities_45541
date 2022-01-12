# -*- coding:gb18030 -*-

from bwdebug import *
from Buff_Normal import Buff_Normal
import csdefine

class Buff_62010( Buff_Normal ):
	"""
	持续损失生命，普通物理攻击同时对目标周围x个敌人造成伤害。
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self.HPReducePercent = 0.0		# hp减少比例
		self.endBuffHPPercent = 0.0		# hp减少到此比例则卸载buff
		self.attackCount = 0			# 额外伤害的敌人数
		self.range = 0					# 影响的范围
		
	def init( self, data ):
		"""
		"""
		Buff_Normal.init( self, data )
		hpPercentList = ( data["Param1"] if len( data["Param1"] ) > 0 else "0;0" ).split( ";" )
		self.HPReducePercent = float( hpPercentList[0] ) / 100
		self.endBuffHPPercent = float( hpPercentList[1] ) / 100
		self.attackCount = int( data["Param2"] if len( data["Param2"] ) > 0 else 0 )
		self.range = float( data["Param3"] if len( data["Param3"] ) > 0 else 0 )
		
	def doBegin( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.addHP( -int( self.HPReducePercent * receiver.HP_Max ) )
		receiver.appendAttackerAfterDamage( buffData[ "skill" ] )
		
	def doReload( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.appendAttackerAfterDamage( buffData[ "skill" ] )
		
	def doLoop( self, receiver, buffData ):
		"""
		virtual method.
		"""
		damage = int( self.HPReducePercent * receiver.HP_Max )
		receiver.addHP( -damage )
		receiver.client.receiveSpell( 0, self.getID(), 0, damage, 0 )	# 用于客户端表现 by 姜毅
		if float( receiver.HP ) / receiver.HP_Max < self.endBuffHPPercent:
			return False
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		"""
		virtual method.
		"""
		receiver.removeAttackerAfterDamage( buffData[ "skill" ].getUID() )
		Buff_Normal.doEnd( self, receiver, buffData )
		
	def springOnDamage( self, caster, receiver, skill, damage ):
		"""
		受到伤害时触发
		"""
		if skill.getType() != csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL:
			return
			
		entityList = receiver.entitiesInRangeExt( self.range, None, receiver.position )
		entityCount = self.attackCount
		for entity in entityList:
			if caster.queryRelation( entity ) == csdefine.RELATION_ANTAGONIZE and entity.id != receiver.id:
				# 防御减伤、护盾吸收后的伤害必中
				damage = self.calcDamageScissor( caster, entity, self.calcDamage( caster, entity, damage ) )
				entity.receiveSpell( caster.id, self.getID(), csdefine.DAMAGE_TYPE_PHYSICS_NORMAL, damage, 0 )
				entity.receiveDamage( caster.id, self.getID(), csdefine.DAMAGE_TYPE_PHYSICS_NORMAL, damage )
				entityCount -= 1
				if entityCount == 0:
					break
					
		
# -*- coding:gb18030 -*-

from Buff_Shield import Buff_Shield
from Function import newUID
import time

class Buff_1114( Buff_Shield ):
	"""
	不死，保证entity的血量在某一个百分比，用于保证npc的血量使npc不被秒杀可以执行一些必要的ai
	"""
	def __init__( self ):
		Buff_Shield.__init__( self )
		self.holdPercent = 0.0	# 必须要hold住的血量百分比
		
	def init( self, data ):
		Buff_Shield.init( self, data )
		self.holdPercent = int( data["Param1"] ) / 100.0 if len( data["Param1"] ) else 0
		
	def doShield( self, receiver, damageType, damage ):
		"""
		virtual method.
		执行护盾自身功能  如：法术形转化伤害为MP 
		注意: 此接口不可手动删除该护盾
		@param receiver: 受术者
		@param damageType: 伤害类型
		@param damage : 本次伤害值
		@rtype: 返回被消减后的伤害值
		"""
		damageInfo = receiver.queryTemp( "shieldDamage_1114", [ 0, 0 ] )		# 伤害会有时间戳属性，以便判断伤害在此次攻击中是否有效
		now = int( time.time() )
		if damageInfo[1] != now:
			damageInfo[0] = 0
			damageInfo[1] = now
		existDamage = damageInfo[0]
		maxDamage = max( 0, receiver.HP - receiver.HP_Max * self.holdPercent )	# 当血量低于指定百分比时抵消所有伤害
		finalDamage = maxDamage - existDamage
		if damage > finalDamage:
			damage = finalDamage
		damageInfo[0] = damage + existDamage
		receiver.setTemp( "shieldDamage_1114", damageInfo )	# 一次攻击有可能有多种伤害类型而且会分别计算，记录伤害总量和伤害发生时间
		return damage
		
	def isDisabled( self, receiver ):
		"""
		virtual method.
		护盾是否失效
		@param receiver: 受术者
		"""
		return False
		
	def doBegin( self, receiver, buffData ):
		Buff_Shield.doBegin( self, receiver, buffData )
		buffData[ "skill" ] = self.createFromDict( { "uid":newUID() } )
		receiver.appendShield( buffData[ "skill" ] )
		
	def doReload( self, receiver, buffData ):
		Buff_Shield.doReload( self, receiver, buffData )
		receiver.appendShield( buffData[ "skill" ] )
		
	def doEnd( self, receiver, buffData ):
		Buff_Shield.doEnd( self, receiver, buffData )
		receiver.removeShield( buffData[ "skill" ].getUID() )
		receiver.removeTemp( "shieldDamage_1114" )
		
	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。
		
		@type data: dict
		"""
		obj = Buff_1114()
		obj.__dict__.update( self.__dict__ )
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
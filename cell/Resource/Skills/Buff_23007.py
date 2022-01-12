# -*- coding: gb18030 -*-
#

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
from Buff_Shield import Buff_Shield
from Function import newUID
"""
"""

class Buff_23007( Buff_Shield ):
	"""
	"需增加Buff_23007，技能使用已有的普通BUFF脚本。
	角色存在此DEBUFF时，所受到的任何伤害都降低一定百分比A，并将剩余部分的一定百分比B伤害转给施法者。施法者所受到的伤害也会降低百分比A，但不再转出剩余部分，并且收到队友转入的伤害不再经过百分比A的削减。
	在寻找施法者时按指定的范围内寻找，如寻找不到施法者，百分比B的伤害不转出。"
	"""
	def __init__( self ):
		"""
		"""
		Buff_Shield.__init__( self )
		self._p1 = 0
		self._p2 = 0
		self._damage = 0
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Shield.init( self, dict )
		self._p1 = int( dict[ "Param1" ] ) / 100.0
		self._p2 = int( dict[ "Param2" ] ) / 100.0
		self._radius = float( dict[ "Param3" ] )
		
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
		val = damage * self._p1
		dval = ( damage - val ) * self._p2
		self._damage += dval
		return dval
		
	def isDisabled( self, receiver ):
		"""
		virtual method.
		护盾是否失效
		@param receiver: 受术者
		"""
		return False
		
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Shield.doBegin( self, receiver, buffData )
		self._damage = 0
		buffData[ "skill" ] = self.createFromDict( self.addToDict() )
		receiver.appendShield( buffData[ "skill" ] )
		
	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Shield.doReload( self, receiver, buffData )
		receiver.appendShield( buffData[ "skill" ] )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Shield.doEnd( self, receiver, buffData )
		receiver.removeShield( buffData[ "skill" ].getUID() )

	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		用于buff，表示buff在每一次心跳时应该做什么。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL；如果允许继续则返回True，否则返回False
		@rtype:  BOOL
		"""
		if self._damage > 0:
			caster = BigWorld.entities.get( buffData[ "caster" ] )
			if caster and caster != receiver and caster.position.flatDistTo( receiver.position ) <= self._radius:
				caster.receiveSpell( 0, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF, self._damage, 0 )
				caster.receiveDamage( 0, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF, self._damage )
			else:
				receiver.receiveSpell( 0, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF, self._damage, 0 )
				receiver.receiveDamage( 0, self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF, self._damage )
				
			self._damage = 0
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。

		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : self._damage }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		obj = Buff_23007()
		obj.__dict__.update( self.__dict__ )

		obj._damage = data["param"]

		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
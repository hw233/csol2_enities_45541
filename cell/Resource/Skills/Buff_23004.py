# -*- coding: gb18030 -*-
#
# $Id: Buff_23003.py,v 1.3 2008-02-28 08:25:56 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Function import newUID
from Buff_Shield import Buff_Shield

class Buff_23004( Buff_Shield ):
	"""
	example:使角色受到伤害的12%由出战宠物承担，持续60秒。出战宠物死亡或被收回都会让该效果消失。
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Shield.__init__( self )
		self._param = {}

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Shield.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0

	def isDisabled( self, receiver ):
		"""
		virtual method.
		护盾是否失效
		@param receiver: 受术者
		"""
		return self._param.has_key( "disabled" )#由于护盾是被动态创建出来的 因此可以判断自身数据

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
		buffData[ "skill" ] = self.createFromDict( { "param":{} } )
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
		buffData[ "skill" ] = self.createFromDict( { "param":{} } )
		receiver.appendShield( buffData[ "skill" ] )

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
		"""
		if not receiver.pcg_actPet.isActive() or receiver.pcg_actPet.entity == None:
			receiver.removeShield( self.getUID() )
			return False
		"""
		return Buff_Shield.doLoop( self, receiver, buffData )

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
		actPet = receiver.pcg_getActPet()
		if self.isDisabled( receiver ) or not actPet :		# 角色无效，或者没有出征宠物
			self._param["disabled"] = True
			return damage

		shieldDamage = int( damage * self._p1 )

		# 这里必须判断real 否则可能会被设置2次， 具体看shieldConsume机制
		if actPet.etype == "REAL" :
			actPet.entity.receiveDamage( 0, self.getSourceSkillID(), csdefine.DAMAGE_TYPE_VOID, shieldDamage ) # 因为是护盾吸收的伤害，所以施法者ID为0

		return damage - shieldDamage

	def addToDict( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看SkillTypeImpl；
		此接口默认返回：{"id":self._id, "param":None}，即表示无动态数据。

		@return: 返回一个SKILL类型的字典。SKILL类型详细定义请参照defs/alias.xml文件
		"""
		return { "param" : self._param }

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		obj = Buff_23004()
		obj.__dict__.update( self.__dict__ )
		obj._param = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj

#
# $Log: not supported by cvs2svn $
#
# -*- coding: gb18030 -*-
#
# $Id: $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus
from Function import newUID
from SpellBase import *
from Buff_Shield import Buff_Shield

class Buff_15008( Buff_Shield ):
	"""
	吸收一定量的所有元素伤害 
	"""
	def __init__( self ):
		"""
		"""
		Buff_Shield.__init__( self )
		self._p1 = 0
		self._param = {}
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Shield.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) 	
		
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
		if self.isDisabled( receiver ) or \
			( not damageType & csdefine.DAMAGE_TYPE_ELEM_HUO and \
			not damageType & csdefine.DAMAGE_TYPE_ELEM_XUAN and \
			not damageType & csdefine.DAMAGE_TYPE_ELEM_LEI and \
			not damageType & csdefine.DAMAGE_TYPE_ELEM_BING ):
			return damage
			
		if self._param["p1"] > damage:
			self._param["p1"] -= damage
			damage = 0
		else:
			damage -= self._param["p1"]
			self._param["disabled"] = True
		return damage
		
	def isDisabled( self, receiver ):
		"""
		virtual method.
		护盾是否失效
		@param receiver: 受术者
		"""
		return self._param.has_key( "disabled" )
		
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
		self._param = { "p1" : self._p1 }
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
		obj = Buff_15008()
		obj.__dict__.update( self.__dict__ )
		obj._param = data["param"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj
		
		
#$Log: not supported by cvs2svn $
#
#
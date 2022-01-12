# -*- coding: gb18030 -*-

#霸体buff
#不受位移技能效果的影响,不受眩晕、定身、昏睡BUFF效果的影响,不处理受击动作的播放
#by wuxo 2012-3-21 
	

"""
持续性效果
"""

# common
import csdefine
import csstatus
from bwdebug import *
# cell
from Buff_Normal import Buff_Normal



class Buff_11001( Buff_Normal ):
	"""
	霸体buffer
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._immuneBuffs = []		#免疫的buff id
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		if dict[ "Param1" ] != "":
			self._immuneBuffs =  eval( dict[ "Param1" ] )
		
	def springOnImmunityBuff( self, caster, receiver, buffData ):
		"""
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		buff = buffData[ "skill" ]
		bid = buff.getBuffID()
		if bid in self._immuneBuffs: #要免疫的buff
			return csstatus.SKILL_BUFF_IS_RESIST
		return csstatus.SKILL_GO_ON
		
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
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.effectStateInc( csdefine.EFFECT_STATE_HEGEMONY_BODY )
		receiver.appendImmunityBuff( buffData[ "skill" ] )
		
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
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.appendImmunityBuff( buffData[ "skill" ] )
		
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。
		
		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.effectStateDec( csdefine.EFFECT_STATE_HEGEMONY_BODY )
		receiver.removeImmunityBuff( buffData[ "skill" ].getUID() )
		
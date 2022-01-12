# -*- coding: gb18030 -*-

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from SpellBase import *
from Buff_Normal import Buff_Normal


class Buff_20003( Buff_Normal ):
	"""
	隐身，效果和gm指令watch相同
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		


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
		actPet = receiver.pcg_getActPet()
		if actPet: actPet.entity.withdraw( csdefine.PET_WITHDRAW_BUFF )
		
		receiver.effectStateInc( csdefine.EFFECT_STATE_WATCHER )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )


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
		
		actPet = receiver.pcg_getActPet()
		if actPet: actPet.entity.withdraw( csdefine.PET_WITHDRAW_BUFF )
		
		receiver.effectStateInc( csdefine.EFFECT_STATE_WATCHER )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )


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
		
		receiver.effectStateDec( csdefine.EFFECT_STATE_WATCHER )
		receiver.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )


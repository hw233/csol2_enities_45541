# -*- coding: gb18030 -*-
#
# $Id: Buff_108003.py,v 1.12 2008-07-04 03:50:57 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import random
import time
import csconst
from Resource.SkillLoader import g_skills

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_JUMP

class Buff_299024( Buff_Normal ):
	"""
	example:小兔赛马等待
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._loopSpeed = 1
		self.param1 = int( dict["Param1"] )
		self.param2 = int( dict["Param2"] )

	def receive( self, caster, receiver ):
		"""
		用于给目标施加一个buff，所有的buff的接收都必须通过此接口，
		此接口必须判断接收者是否为realEntity，
		如果否则必须要通过receiver.receiveOnReal()接口处理。

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		Buff_Normal.receive( self, caster, receiver )

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
		# 执行附加效果
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_FIX )

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
		# 执行附加效果
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_FIX )

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
		receiver.effectStateDec( csdefine.EFFECT_STATE_FIX )
		receiver.actCounterDec( STATES )
		if receiver.findBuffByID( csconst.RABBIT_RUN_CATCH_RABBIT_RABBIT_BUFF_ID ) is not None:
			g_skills[self.param1].getBuffLink(0).getBuff().receive( None, receiver )
		if receiver.findBuffByID( csconst.RABBIT_RUN_CATCH_RABBIT_WOLF_BUFF_ID ) is not None:
			g_skills[self.param2].getBuffLink(0).getBuff().receive( None, receiver )

	def calculateTime( self, caster ):
		"""
		virtual method.
		取得持续时间
		"""

		leaveTime = BigWorld.globalData["AS_RabbitRun_Start_Time"] - time.time() + 0.5

		if leaveTime <= 0: return 1
		return int( time.time() + leaveTime )

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
		spaceType = receiver.getCurrentSpaceData( csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY )
		if not spaceType == str( csdefine.SPACE_TYPE_RABBIT_RUN ):
			return False
		#if BigWorld.globalData["AS_RabbitRun_Start_Time"] - time.time() < 0:
		#	return False
		return Buff_Normal.doLoop( self, receiver, buffData )
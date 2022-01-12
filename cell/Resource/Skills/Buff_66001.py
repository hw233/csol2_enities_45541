# -*- coding: gb18030 -*-
#
# $Id: Buff_1003.py,v 1.2 2007-12-13 04:59:55 huangyongwei Exp $

"""
持续性效果
"""
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import BigWorld
import csconst
import csstatus
import csdefine
import ECBExtend

class Buff_66001( Buff_Normal ):
	"""
	净化怪物
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
		#if not receiver.hasFlag( csdefine.ENTITY_FLAG_SPEAKER ) and receiver.getState() != csdefine.ENTITY_STATE_PENDING:
		receiver.state = csdefine.ENTITY_STATE_FREE
		receiver.changeToNPC()
	
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
		#if not receiver.hasFlag( csdefine.ENTITY_FLAG_SPEAKER ) and receiver.getState() != csdefine.ENTITY_STATE_PENDING:
		receiver.state = csdefine.ENTITY_STATE_FREE
		receiver.changeToNPC()
		
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
		pID = receiver.queryTemp( "evolute_player_id", 0 )
		if BigWorld.entities.has_key( pID ):
			player = BigWorld.entities[pID]
			receiver.getScript().dropItemBox( receiver, receiver.getBootyOwner() )	# 掉落任务物品（如果有的话）
			player.questMonsterEvoluted( receiver.className )
		receiver.state = csdefine.ENTITY_STATE_FREE
		receiver.addTimer( 3, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )
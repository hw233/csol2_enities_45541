# -*- coding: gb18030 -*-
#
# $Id: Buff_22001.py,v 1.2 2008-05-19 08:01:12 kebiao Exp $

"""
获得钓鱼时间buff
"""

import BigWorld
import csconst
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_99013( Buff_Normal ):
	"""
	获得钓鱼时间的buff。
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

	def receive( self, caster, receiver ):
		"""
		用于给目标施加一个buff，所有的buff的接收都必须通过此接口，
		此接口必须判断接收者是否为realEntity，
		如果否则必须要通过receiver.receiveOnReal()接口处理。

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者，None表示不存在
		@type  receiver: Entity
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( casterID, self )
			return

		if receiver.getState() == csdefine.ENTITY_STATE_DEAD:
			return

		buffs = receiver.findBuffsByBuffID( self._buffID )
		#判断是否有相同的buff
		if len( buffs ) > 0:
			# 已存在相同类型的buff
			self.doAppend( receiver, buffs[0] )
		else:
			receiver.addBuff( self.getNewBuffData( caster, receiver ) )
		receiver.statusMessage( csstatus.SKILL_CAST_ADD_FISH_TIME, self._persistent / 60 )

	def doAppend( self, receiver, buffIndex ):
		"""
		Virtual method.
		对一个或多个已经存在的同类型BUFF进行追加操作
		具体对BUFF数据追加什么由继承者决定
		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffs: 玩家身上同类型的BUFF所在attrbuffs的位置,BUFFDAT 可以通过 receiver.getBuff( buffIndex ) 获取
		"""
		buffdata = receiver.getBuff( buffIndex )
		sk = buffdata["skill"]
		buffdata["persistent"] += self._persistent
		receiver.client.onUpdateBuffData( buffIndex, buffdata )

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
		receiver.setTemp( "has_fishing_time", True )	# 记录玩家是否能钓鱼的标记
		Buff_Normal.doReload( self, receiver, buffData )

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
		receiver.setTemp( "has_fishing_time", True )	# 记录玩家是否能钓鱼的标记
		Buff_Normal.doBegin( self, receiver, buffData )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		if receiver.getState() == csdefine.ENTITY_STATE_CHANGING:
			# 使用引路蜂要取消变身状态
			receiver.end_body_changing( receiver.id,"" )
		receiver.removeTemp( "has_fishing_time" )	# 清除掉记录玩家是否能钓鱼的标记
# -*- coding: gb18030 -*-
#
# $Id: Buff_12010.py,v 1.9 2008-07-04 03:50:57 kebiao Exp $

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
import csconst

class Buff_12010( Buff_Normal ):
	"""
	example:无敌R	BUFF	免疫所有效果并且所有伤害减免率增加100%。	存在该效果时，所有非单位来源的负面影响都不会对自己产生效果，并且信息提示“免疫”。

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
		self.spaceNames = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" ) .split("|")

	def springOnImmunityBuff( self, caster, receiver, buffData ):
		"""
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		buff = buffData[ "skill" ]
		isRayRingEffect = buff.isRayRingEffect()

		if not isRayRingEffect and buff.isMalignant(): #是恶性但不是光环效果 那么免疫
			return csstatus.SKILL_BUFF_IS_RESIST
		elif isRayRingEffect:   # 是光环效果
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				# 策划规定， 如果是自己释放的恶性光环效果， 则无敌可以免疫
				if buffData[ "caster" ] != caster.id:
					buffData[ "state" ] |= csdefine.BUFF_STATE_DISABLED
				else:
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
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #首先添加抵抗
		dels = []

		for idx in receiver.getBuffIndexsByEffectType( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ):
			buff = receiver.getBuff( idx )["skill"]
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				# 策划规定， 如果是自己释放的恶性光环效果， 则无敌可以免疫
				if buffData[ "caster" ] == receiver.id:
					dels.append( idx )
				else:
					receiver.addBuffState( idx, csdefine.BUFF_STATE_DISABLED )

		for i in dels:
			receiver.removeBuff( i, [ 0 ] )

		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )

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
		spaceType = receiver.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if not spaceType in self.spaceNames:
			return False
		return Buff_Normal.doLoop( self, receiver, buffData )

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
		dels = []

		for idx in receiver.getBuffIndexsByEffectType( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ):
			buff = receiver.getBuff( idx )["skill"]
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				# 策划规定， 如果是自己释放的恶性光环效果， 则无敌可以免疫
				if buffData[ "caster" ] == receiver.id:
					dels.append( idx )
				else:
					receiver.addBuffState( idx, csdefine.BUFF_STATE_DISABLED )

		for i in dels:
			receiver.removeBuff( i, [ 0 ] )

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
		receiver.removeImmunityBuff( buffData[ "skill" ].getUID() )

		for idx in receiver.getBuffIndexsByEffectType( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ):
			buff = receiver.getBuff( idx )["skill"]
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				# 策划规定， 如果是自己释放的恶性光环效果， 则无敌可以免疫
				if buffData[ "caster" ] != receiver.id:
					receiver.removeBuffState( idx, csdefine.BUFF_STATE_DISABLED )

		receiver.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
#
# $Log: not supported by cvs2svn $
# Revision 1.8  2008/07/03 02:49:39  kebiao
# 改变 睡眠 定身等效果的实现
#
# Revision 1.7  2008/05/28 02:09:42  kebiao
# 去掉代码中 抛出中断BUFF码  由低层机制实现
#
# Revision 1.6  2008/02/28 08:25:56  kebiao
# 改变删除技能时的方式
#
# Revision 1.5  2007/12/25 03:09:16  kebiao
# 调整效果记录属性为effectLog
#
# Revision 1.4  2007/12/24 09:12:24  kebiao
# 修正删除BUFF时索引错误BUG
#
# Revision 1.3  2007/12/22 07:36:43  kebiao
# ADD:IMPORT csstatus
#
# Revision 1.2  2007/12/22 02:26:57  kebiao
# 调整免疫相关接口
#
# Revision 1.1  2007/12/20 06:10:56  kebiao
# no message
#
#
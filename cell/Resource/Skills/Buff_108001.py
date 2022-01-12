# -*- coding: gb18030 -*-
#
# $Id: Buff_108001.py,v 1.12 2008-07-04 03:50:57 kebiao Exp $

"""
持续性效果
"""
import random
import BigWorld

import csstatus
import csdefine
from bwdebug import *

import Const
from SpellBase import *
from Buff_Normal import Buff_Normal

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_JUMP

class Buff_108001( Buff_Normal ):
	"""
	example:眩晕
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
		if receiver.attrIntonateTimer > 0 and receiver.attrIntonateSkill.getType() in Const.INTERRUPTED_BASE_TYPE or\
			( receiver.attrHomingSpell and receiver.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			receiver.interruptSpell( csstatus.SKILL_IN_BLACKOUT )
		# 执行附加效果
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_VERTIGO )
		if receiver.isMoving():
			# 加入移动限制，以确保buff对移动限制效果生效 by姜毅
			receiver.stopMoving()

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
		receiver.effectStateInc( csdefine.EFFECT_STATE_VERTIGO )
		if receiver.isMoving():
			# 加入移动限制，以确保buff对移动限制效果生效 by姜毅
			receiver.stopMoving()
		
		
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
		receiver.effectStateDec( csdefine.EFFECT_STATE_VERTIGO )
		receiver.actCounterDec( STATES )
		
		
#
# $Log: not supported by cvs2svn $
# Revision 1.11  2008/07/04 01:03:58  kebiao
# 增加了禁止跳跃状态
#
# Revision 1.10  2008/07/03 02:49:39  kebiao
# 改变 睡眠 定身等效果的实现
#
# Revision 1.9  2007/12/25 03:09:16  kebiao
# 调整效果记录属性为effectLog
#
# Revision 1.8  2007/12/22 03:27:26  kebiao
# 修正添加BUFF错误
#
# Revision 1.7  2007/12/22 02:26:57  kebiao
# 调整免疫相关接口
#
# Revision 1.6  2007/12/13 00:48:08  kebiao
# 重新修正了状态改变部分，因为底层有相关冲突机制 因此这里就不再关心冲突问题
#
# Revision 1.5  2007/12/12 06:42:50  kebiao
# 调整判断方式
#
# Revision 1.4  2007/12/12 04:21:10  kebiao
# 修改眩晕等状态判断
#
# Revision 1.3  2007/12/11 04:05:17  kebiao
# 加入抵抗BUFF支持
#
# Revision 1.2  2007/12/05 05:48:59  kebiao
# 调整规则和打断等状态
#
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
# 
#
# -*- coding: gb18030 -*-
#
# $Id: Buff_102004.py,v 1.1 2007-12-26 07:11:35 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_14003( Buff_Normal ):
	"""
	example:节能	10秒内，你所释放的下一个技能不消耗任何法力值。

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
	
	def springOnUseSkill( self, caster, skill ):
		"""
		使用技能被触发
		"""
		if skill.getType() != csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL and skill.getType() != csdefine.BASE_SKILL_TYPE_ITEM:
			caster.removeAllBuffByID( self.getBuffID(), csdefine.BUFF_INTERRUPT_NONE )
		
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
		receiver.appendOnUseSkill( buffData[ "skill" ] )
		receiver.phyManaVal_value -= 1000
		receiver.magicManaVal_value -= 1000
		
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
		receiver.appendOnUseSkill( buffData[ "skill" ] )
		receiver.phyManaVal_value -= 1000
		receiver.magicManaVal_value -= 1000
		
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
		receiver.removeOnUseSkill( buffData[ "skill" ].getUID() )
		receiver.phyManaVal_value += 1000
		receiver.magicManaVal_value += 1000
		
#
# $Log: not supported by cvs2svn $
#
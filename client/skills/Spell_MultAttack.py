# -*- coding: gb18030 -*-
#
# $Id: Spell_MultAttack.py,v 1.14 2008-08-06 06:17:09 qilan Exp $

"""
Spell技能类。
"""
import BigWorld
from bwdebug import *
from SpellBase import *
from event.EventCenter import *
import ItemTypeEnum
import csstatus
from Function import Functor

class Spell_MultAttack( Spell ):
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		self._attackCount = int( dict[ "param1" ] )
		if self._attackCount <= 0: self._attackCount = 1

	def receiveSpell( self, target, casterID, damageType, damage  ):
		"""
		接受技能处理

		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		player = BigWorld.player()
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				#这里会出错误的原因是 在服务器上一个entity对另一个entity施法 服务器上是看的到施法者的
				#而客户端可能会因为某原因 如：网络延迟 而在本机没有更新到AOI中的那个施法者entity所以
				#会产生这种错误 written by kebiao.  2008.1.8
				return
		else:
			caster = None

		count = 1
		if damage > 0:
			p2 = damage
			damage /= self._attackCount
			if target.HP < p2:
				count = target.HP / damage + 1
			else:
				count = self._attackCount
		# 动作光效部分
		self._skillAE( player, target, caster, damageType, damage  )
		self.showSkillInfo( count, player, target, casterID, damageType, damage  )

	def showSkillInfo( self, attackCount, player, target, casterID, damageType, damage  ):
		"""
		# 伤害信息提示
		"""
		if target.isAlive():
			target.onReceiveDamage( casterID, self, damageType, damage  )							# 系统信息
			if attackCount > 1:
				BigWorld.callback( 0.3, Functor( self.showSkillInfo, attackCount - 1, player, target, casterID, damageType, damage  ) )

#
# $Log: not supported by cvs2svn $
# Revision 1.13  2008/08/06 05:50:33  kebiao
# 调整receiveDamage接口参数 skill.receiveSpell 去掉skillID
#
# Revision 1.12  2008/08/06 03:31:31  kebiao
# 调整receiveDamage接口参数 skill.receiveSpell 去掉skillID
#
# Revision 1.11  2008/08/05 02:04:43  qilan
# 调整伤害系统信息接口
#
# Revision 1.10  2008/07/07 09:17:24  kebiao
# 修改任务对话
#
# Revision 1.9  2008/07/05 01:07:13  kebiao
# no message
#
# Revision 1.8  2008/07/04 04:00:05  kebiao
# no message
#
# Revision 1.7  2008/07/04 01:06:14  zhangyuxing
# 怪物死亡后，不在提示信息
#
# Revision 1.6  2008/05/29 05:56:17  kebiao
# no message
#
# Revision 1.5  2008/05/28 07:47:46  kebiao
# no message
#
# Revision 1.3  2008/05/28 07:31:56  kebiao
# no message
#
#
# -*- coding: gb18030 -*-
#
# $Id: Spell_322370.py,v 1.6 2008-08-06 06:11:18 kebiao Exp $

"""
Spell技能类。
"""
import BigWorld
from bwdebug import *
from skills.Spell_Item import Spell_Item
import ItemTypeEnum
import csstatus
import SkillTargetObjImpl
from gbref import rds

class Spell_322370( Spell_Item ):
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell_Item.init( self, dict )

	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		#对动作而言，我只会播放一次
		pet = caster.pcg_getActPet()
		if pet is None: return
		self.pose.cast( pet, self.getID(), targetObject )
		targetPet = SkillTargetObjImpl.createTargetObjEntity( targetObject.getObject().pcg_getActPet() )
		if targetPet is None: return
		rds.skillEffect.playCastEffects( pet, targetPet, self.getID() )

	def receiveSpell( self, target, casterID, damageType, damage ):
		"""
		接受技能处理

		@type   casterID: OBJECT_ID
		@type    skillID: INT
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

		# 动作光效部分
		pass

#
# $Log: not supported by cvs2svn $
# Revision 1.5  2008/08/06 03:31:31  kebiao
# 调整receiveDamage接口参数 skill.receiveSpell 去掉skillID
#
# Revision 1.4  2008/07/21 03:04:09  huangyongwei
# caster.pcg_getOutPet(),
# 改为
# caster.pcg_getActPet(),
#
# Revision 1.3  2008/03/31 08:39:23  kebiao
# no message
#
#
#
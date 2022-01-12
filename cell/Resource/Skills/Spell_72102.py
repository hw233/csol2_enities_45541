# -*- coding: gb18030 -*-
#
# $Id: Spell_72102.py,v 1.1 16:41 2010-7-21 jianyi Exp $

import random
from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus
import ItemTypeEnum
import CooldownFlyweight

from Spell_BuffNormal import Spell_BuffNormal_With_Homing

g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()

BUFF_TARGET_CASTER = 1
BUFF_TARGET_RECEIVER = 2

class Spell_72102( Spell_BuffNormal_With_Homing ):
	"""
	神器技能，在成功产生buff时添加一个内部CD
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal_With_Homing.__init__( self )
		
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_BuffNormal_With_Homing.init( self, dict )
		icd = dict["param3"].split(" ") if len( dict["param3"] ) > 0 else []
		self._internalCD = []
		for i in icd:
			datas = i.split(":")
			self._internalCD.append( (int(datas[0]), int(datas[1]) ) )
		
		
	def receiveLinkBuff( self, caster, receiver ):
		"""
		给entity附加buff的效果
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 施展对象
		@type  receiver: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		if len( self._buffLink ) <= 0:
			return
		
		buff_successed = False
		for bl in self._buffLink:
			if not self.canLinkBuff( caster, receiver, bl ):
				continue
				
			buff = bl.getBuff()
			if buff.param3 is None or buff.param3 == "":
				continue
				
			if int(buff.param3) == BUFF_TARGET_CASTER:
				buff.receive( caster, caster )
			elif int(buff.param3) == BUFF_TARGET_RECEIVER:
				buff.receive( caster, receiver )
			buff_successed = True
		
		if buff_successed:
			self.setInternalCooldownInIntonate( caster )	# 设置内部CD
			
		# 蛋疼到 无以复加 的神器技能提示
		if buff_successed and caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			weapon = caster.getItem_( ItemTypeEnum.CEL_RIGHTHAND )
			if weapon and weapon.getType() in ItemTypeEnum.WEAPON_LIST and weapon.getGodWeaponSkillID() == self.getID():
				caster.statusMessage( csstatus.GW_SKILL_TRIGGERED, self.getName() )
			
	def setInternalCooldownInIntonate( self, caster ):
		"""
		特殊需求
		给施法者设置法术该技能内部的cooldown时间(buff成功释放时)

		@return: None
		"""
		endTime = 0
		if len( self._internalCD ) <= 0:
			ERROR_MSG( "Internal cooldown config error, skill: %i ."%self.getID() )
			return
		for cd, time in self._internalCD:
			try:
				endTime = g_cooldowns[ cd ].calculateTime( time )
			except:
				EXCEHOOK_MSG("skillID:%d" % self.getID())
			if caster.getCooldown( cd ) < endTime:
				caster.changeCooldown( cd, time, time, endTime )
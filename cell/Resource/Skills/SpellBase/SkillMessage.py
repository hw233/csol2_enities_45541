# -*- coding: gb18030 -*-
#
# $Id: SkillMessage.py,v 1.5 2008-08-11 06:05:50 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csstatus
import csdefine
from bwdebug import *


#spell 技能相关处理
def spell_ConsumeMP( skill, caster, receiver, damage ):
	"""
	技能产生MP消耗
	"""
	if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		#你的%s使%s损失%i点法力值。
		if caster.isReal():
			caster.statusMessage( csstatus.SKILL_SPELL_CONSUME_MP_TO, skill.getName(), receiver.getName(), damage )
		else:
			caster.remoteCall( "statusMessage", ( csstatus.SKILL_SPELL_CONSUME_MP_TO, skill.getName(), receiver.getName(), damage ) )

	if caster.id != receiver.id and receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		#%s的%s使你损失%i点法力值。
		if receiver.isReal():
			receiver.statusMessage( csstatus.SKILL_SPELL_CONSUME_MP, caster.getName(), skill.getName(), damage )
		else:
			receiver.remoteCall( "statusMessage", ( csstatus.SKILL_SPELL_CONSUME_MP, caster.getName(), skill.getName(), damage ) )

def spell_DamageSuck( caster, receiver, damage ):
	"""
	BUFF伤害吸收
	"""
	if caster and receiver != caster.id:
		if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			caster.statusMessage( csstatus.SKILL_DAMAGE_SUCK_TO, receiver.getName(), damage )

	if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		if receiver.isReal():
			#%i点伤害被护盾吸收。
			if receiver.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
				receiver.statusMessage( csstatus.SKILL_DAMAGE_SUCK, damage )
		else:
			if receiver.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
				receiver.remoteCall( "statusMessage", ( csstatus.SKILL_DAMAGE_SUCK, damage ) )

#buff 相关处理
def buff_ConsumeMP( buffData, receiver, value ):
	"""
	显示BUFF产生MP类消耗信息
	"""
	casterID = buffData[ "caster" ]
	if receiver.MP < value:		# 每次消耗的法力值不能大于目标所剩法力
		value = receiver.MP
	if casterID != 0 and BigWorld.entities.has_key( casterID ):
		caster = BigWorld.entities[ casterID ]
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if caster.isReal():
				#你的%s使%s损失了%i点法力值。
				caster.statusMessage( csstatus.SKILL_BUFF_CONSUME_MP_TO, buffData[ "skill" ].getName(), receiver.getName(), value )
			else:
				caster.remoteCall( "statusMessage", ( csstatus.SKILL_BUFF_CONSUME_MP_TO, buffData[ "skill" ].getName(), receiver.getName(), value ) )

	if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		if receiver.isReal():
			receiver.statusMessage( csstatus.SKILL_BUFF_CONSUME_MP, buffData[ "skill" ].getName(), value )
		else:
			receiver.remoteCall( "statusMessage", ( csstatus.SKILL_BUFF_CONSUME_MP, buffData[ "skill" ].getName(), value ) )

def buff_CureHP( buffData, receiver, value ):
	"""
	BUFF治疗HP
	"""
	#治疗效果提示修改by wuxo 2012-5-18
	if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		#SKILL_HP_BUFF_CURE:%s恢复了你%i点生命值。
		receiver.statusMessage( csstatus.SKILL_HP_BUFF_CURE, buffData[ "skill" ].getName(), value )
	elif receiver.isEntityType( csdefine.ENTITY_TYPE_PET ):
		#SKILL_HP_CURE_BUFF_PET:%s为你的宠物恢复了%i点生命值。
		receiver.statusMessage( csstatus.SKILL_HP_CURE_BUFF_PET, buffData[ "skill" ].getName(), value )

	if receiver.targetID == receiver.id:
		return
	
	#目标不需要知道恢复信息
	#try:
	#	target = BigWorld.entities[ receiver.targetID ]
	#except:
	#	return
	#
	#if target.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
	#	if target.isReal():
	#		target.statusMessage( csstatus.SKILL_HP_BUFF_CURE, buffData[ "skill" ].getName(), receiver.getName(), value )
	#	else:
	#		target.remoteCall( "statusMessage", ( csstatus.SKILL_HP_BUFF_CURE, buffData[ "skill" ].getName(), receiver.getName(), value ) )

def buff_CureMP( buffData, receiver, value ):
	"""
	BUFF治疗MP
	"""
	if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		receiver.statusMessage( csstatus.SKILL_MP_BUFF_CURE, buffData[ "skill" ].getName(), value )
	elif receiver.isEntityType( csdefine.ENTITY_TYPE_PET ):
		receiver.statusMessage( csstatus.SKILL_MP_CURE_BUFF_PET, buffData[ "skill" ].getName(), value )

def buff_ReboundEffect( buffData, caster, receiver ):
	"""
	BUFF反射不良效果
	"""
	buff = buffData[ "skill" ]
	receiver.statusMessage( csstatus.SKILL_SPELL_REBOUND_EFFECT_TO, caster.getName(), buff.getName() )
	if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		if caster.isReal():
			caster.statusMessage( csstatus.SKILL_SPELL_REBOUND_EFFECT, receiver.getName(), buff.getName() )
		else:
			caster.remoteCall( "statusMessage", ( csstatus.SKILL_SPELL_REBOUND_EFFECT, receiver.getName(), buff.getName() ) )

def buff_ReboundDamageMagic( caster, receiver, damage ):
	"""
	BUFF反射不良法术伤害
	"""
	receiver.statusMessage( csstatus.SKILL_BUFF_REBOUND_MAGIC_TO, caster.getName(), damage )
	
	if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		if caster.isReal():
			caster.statusMessage( csstatus.SKILL_BUFF_REBOUND_MAGIC, receiver.getName(), damage )
		else:
			caster.remoteCall( "statusMessage", ( csstatus.SKILL_BUFF_REBOUND_MAGIC, receiver.getName(), damage ) )
			
def buff_DamageSuck( buffData, receiver, damage ):
	"""
	BUFF伤害吸收
	"""
	receiver.statusMessage( csstatus.SKILL_DAMAGE_SUCK, damage )
	casterID = buffData[ "caster" ]
	if casterID != 0 and BigWorld.entities.has_key( casterID ):
		caster = BigWorld.entities[ casterID ]
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if caster.isReal():
				caster.statusMessage( csstatus.SKILL_DAMAGE_SUCK_TO, receiver.getName(), damage )
			else:
				caster.remoteCall( "statusMessage", ( csstatus.SKILL_DAMAGE_SUCK_TO, receiver.getName(), damage ) )
#
# $Log: not supported by cvs2svn $
# Revision 1.4  2008/08/11 05:53:48  kebiao
# 修改spell_DamageSuck可能没有施法者
#
# Revision 1.3  2008/06/13 02:09:57  kebiao
# 增加对宠物使用HP MP增加时的消息处理；
#
# Revision 1.2  2008/02/25 09:27:11  kebiao
# 修改 护盾减伤相关
#
# Revision 1.1  2008/02/13 09:32:23  kebiao
# no message
#
#
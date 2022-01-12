# -*- coding: gb18030 -*-
#
# $Id: SkillMessage.py,v 1.5 2008-08-11 06:05:50 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csstatus
import csdefine
from bwdebug import *


#spell ������ش���
def spell_ConsumeMP( skill, caster, receiver, damage ):
	"""
	���ܲ���MP����
	"""
	if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		#���%sʹ%s��ʧ%i�㷨��ֵ��
		if caster.isReal():
			caster.statusMessage( csstatus.SKILL_SPELL_CONSUME_MP_TO, skill.getName(), receiver.getName(), damage )
		else:
			caster.remoteCall( "statusMessage", ( csstatus.SKILL_SPELL_CONSUME_MP_TO, skill.getName(), receiver.getName(), damage ) )

	if caster.id != receiver.id and receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		#%s��%sʹ����ʧ%i�㷨��ֵ��
		if receiver.isReal():
			receiver.statusMessage( csstatus.SKILL_SPELL_CONSUME_MP, caster.getName(), skill.getName(), damage )
		else:
			receiver.remoteCall( "statusMessage", ( csstatus.SKILL_SPELL_CONSUME_MP, caster.getName(), skill.getName(), damage ) )

def spell_DamageSuck( caster, receiver, damage ):
	"""
	BUFF�˺�����
	"""
	if caster and receiver != caster.id:
		if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			caster.statusMessage( csstatus.SKILL_DAMAGE_SUCK_TO, receiver.getName(), damage )

	if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		if receiver.isReal():
			#%i���˺����������ա�
			if receiver.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
				receiver.statusMessage( csstatus.SKILL_DAMAGE_SUCK, damage )
		else:
			if receiver.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
				receiver.remoteCall( "statusMessage", ( csstatus.SKILL_DAMAGE_SUCK, damage ) )

#buff ��ش���
def buff_ConsumeMP( buffData, receiver, value ):
	"""
	��ʾBUFF����MP��������Ϣ
	"""
	casterID = buffData[ "caster" ]
	if receiver.MP < value:		# ÿ�����ĵķ���ֵ���ܴ���Ŀ����ʣ����
		value = receiver.MP
	if casterID != 0 and BigWorld.entities.has_key( casterID ):
		caster = BigWorld.entities[ casterID ]
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if caster.isReal():
				#���%sʹ%s��ʧ��%i�㷨��ֵ��
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
	BUFF����HP
	"""
	#����Ч����ʾ�޸�by wuxo 2012-5-18
	if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		#SKILL_HP_BUFF_CURE:%s�ָ�����%i������ֵ��
		receiver.statusMessage( csstatus.SKILL_HP_BUFF_CURE, buffData[ "skill" ].getName(), value )
	elif receiver.isEntityType( csdefine.ENTITY_TYPE_PET ):
		#SKILL_HP_CURE_BUFF_PET:%sΪ��ĳ���ָ���%i������ֵ��
		receiver.statusMessage( csstatus.SKILL_HP_CURE_BUFF_PET, buffData[ "skill" ].getName(), value )

	if receiver.targetID == receiver.id:
		return
	
	#Ŀ�겻��Ҫ֪���ָ���Ϣ
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
	BUFF����MP
	"""
	if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		receiver.statusMessage( csstatus.SKILL_MP_BUFF_CURE, buffData[ "skill" ].getName(), value )
	elif receiver.isEntityType( csdefine.ENTITY_TYPE_PET ):
		receiver.statusMessage( csstatus.SKILL_MP_CURE_BUFF_PET, buffData[ "skill" ].getName(), value )

def buff_ReboundEffect( buffData, caster, receiver ):
	"""
	BUFF���䲻��Ч��
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
	BUFF���䲻�������˺�
	"""
	receiver.statusMessage( csstatus.SKILL_BUFF_REBOUND_MAGIC_TO, caster.getName(), damage )
	
	if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
		if caster.isReal():
			caster.statusMessage( csstatus.SKILL_BUFF_REBOUND_MAGIC, receiver.getName(), damage )
		else:
			caster.remoteCall( "statusMessage", ( csstatus.SKILL_BUFF_REBOUND_MAGIC, receiver.getName(), damage ) )
			
def buff_DamageSuck( buffData, receiver, damage ):
	"""
	BUFF�˺�����
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
# �޸�spell_DamageSuck����û��ʩ����
#
# Revision 1.3  2008/06/13 02:09:57  kebiao
# ���ӶԳ���ʹ��HP MP����ʱ����Ϣ����
#
# Revision 1.2  2008/02/25 09:27:11  kebiao
# �޸� ���ܼ������
#
# Revision 1.1  2008/02/13 09:32:23  kebiao
# no message
#
#
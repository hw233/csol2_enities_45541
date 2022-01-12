# -*- coding: gb18030 -*-
#
# $Id: Spell_ConjureVehicle.py,v 1.1 2008-09-04 06:43:15 yangkai Exp $

"""
"""
import csconst
from SpellBase import Spell
import csstatus
from bwdebug import *
from Resource.SkillLoader import g_skills
from VehicleHelper import canMount,getVehicleSkillID



class Spell_ConjureVehicle( Spell ):
	"""
	�ٻ���輼��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		
	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		
		targetEntity = target.getObject()
		if not targetEntity:
			ERROR_MSG( "Can't find target entity!" )
			return
		
		vehicleData = caster.queryTemp( "conjureVehicleData", {} )
		
		# ���������ˣ���ô�������ٻ����
		state = canMount( targetEntity, vehicleData["id"], vehicleData["type"] )
		if state != csstatus.SKILL_GO_ON :
			return state
		if  vehicleData["level"] - caster.level >= csconst.VEHICLE_DIS_LEVEL_MAX:
			return csstatus.VEHICLE_NO_CONJURE
			
		skillID = getVehicleSkillID( vehicleData )
		try:
			skill = g_skills[ skillID ]
		except:
			ERROR_MSG( "Can't load vehicle binded skill: %s"%skillID )
			return csstatus.SKILL_CANT_CAST
		
		# �����Ҫ�ٻ����󶨵ļ��ܷ�����ٻ�������ô�����ٻ����
		status = skill.useableCheck( caster, target )
		if status != csstatus.SKILL_GO_ON:
			return status
		
		return Spell.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method = 0
		���ÿһ�������߽�����������������˺����ı����Եȵȡ�ͨ������´˽ӿ�����onArrive()���ã�
		�������п�����SpellUnit::receiveOnreal()�������ã����ڴ���һЩ��Ҫ�������ߵ�real entity�����������顣
		�������Ƿ���Ҫ��real entity���Ͻ��գ��ɼ����������receive()�������жϣ������ṩ��ػ��ơ�
		ע���˽ӿ�Ϊ�ɰ��е�onReceive()

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		receiverEntity = caster
		
		vehicleData = receiverEntity.popTemp( "conjureVehicleData", {} )
		if not vehicleData:
			ERROR_MSG( "Can't find vehicle data! player(%s)" %receiverEntity.playerName  )
			return
		receiverEntity.onConjureVehicle( vehicleData )
		

# $Log: not supported by cvs2svn $

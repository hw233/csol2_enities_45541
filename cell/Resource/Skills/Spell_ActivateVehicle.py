# -*- coding: gb18030 -*-
#
# edit by wuxo 2013-3-27

from Spell_BuffNormal import Spell_BuffNormal
import csstatus
from bwdebug import *

class Spell_ActivateVehicle( Spell_BuffNormal ):
	"""
	������輼��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_BuffNormal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )
		
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
		return Spell_BuffNormal.useableCheck( self, caster, target )

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
		#������������ϵ������������buff��Ϊ��currAttrVehicleData���Կ��ܻ���buffend�б�Ĭ�ϸ�ֵ
		receiverEntity.cancelActiveVehicle()
		
		vehicleData = receiverEntity.popTemp( "activateVehicleData", {} )
		if not vehicleData:
			return
		receiverEntity.onactivateVehicle( vehicleData )
		self.receiveLinkBuff( receiverEntity, receiverEntity )



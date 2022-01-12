# -*- coding:gb18030 -*-

#edit by wuxo 2012-8-31
import csdefine
from Spell_BuffNormal import Spell_BuffNormal
import csstatus
from VehicleHelper import getCurrVehicleID

class Spell_WaterMoving( Spell_BuffNormal):
	"""
	�Ṧϵͳ-����Ѹ���ƶ�buff�ļ���
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		self.needEnergy = 0
		
	def init( self, data ):
		"""
		"""
		Spell_BuffNormal.init( self, data )
		self.needEnergy = int( data["buff"][0]["Param2"] )
		
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
		#if getCurrVehicleID( caster ): # �����޷��ͷ��Ṧ����
		#	return csstatus.SKILL_NO_MSG 
		if caster.energy < self.needEnergy or caster.getState() == csdefine.ENTITY_STATE_FIGHT : #�ж���Ծ����ֵ
			return csstatus.SKILL_NO_MSG 
		return Spell_BuffNormal.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		if receiver.findBuffByBuffID(22130):
			return
		self.receiveLinkBuff( caster, receiver )


# -*- coding: gb18030 -*-
#�滻��Ҽ���

"""
������Ч��
"""

# bigworld
import ResMgr
import BigWorld
# common
import csstatus
import csdefine
import csconst
from bwdebug import *
from Function import newUID
# cell
from Buff_Normal import Buff_Normal
from VehicleHelper import getCurrVehicleID

class Buff_22134( Buff_Normal ):
	"""
	�滻��Ҽ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self.replaceSkills = []		# ���buff�����ֻ��ʹ����Щ����
		self.flag = 0 #�Ƿ��жϿռ似��
		self.notUseSelfSkill = 0 #�Ƿ���ʹ���Լ��ļ���

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		skills = dict["Param1"].split(";")
		self.replaceSkills = [ int( i ) for i in skills ]
		if dict["Param2"]!="":
			self.flag = int( dict["Param2"] )
		if dict["Param3"]!="":
			self.notUseSelfSkill = int( dict["Param3"] )

	def springOnImmunityBuff( self, caster, receiver, buffData ):
		"""
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		buff = buffData[ "skill" ]
		if buff.isRayRingEffect() :						# �ǹ⻷Ч��
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				# �߻��涨�� ������Լ��ͷŵĶ��Թ⻷Ч���� ���޵п�������
				if buffData[ "caster" ] != caster.id:
					buffData[ "state" ] |= csdefine.BUFF_STATE_DISABLED
				else:
					return csstatus.SKILL_BUFF_IS_RESIST
		elif buff.isMalignant() :						# �Ƕ��Ե����ǹ⻷Ч�� ��ô����
			return csstatus.SKILL_BUFF_IS_RESIST
		return csstatus.SKILL_GO_ON

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.setTemp( "FLY_TEL_SKILL_FLAG", self.flag )
		receiver.setTemp( "NOT_USE_SELF_SKILL_FLAG", self.notUseSelfSkill )
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #������ӵֿ�

		actPet = receiver.pcg_getActPet()
		if actPet :
			actPet.entity.changeState( csdefine.ENTITY_STATE_FREE )
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )

		# �������
		if getCurrVehicleID( receiver ):
			receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )

		if self.replaceSkills :
			receiver.client.initSpaceSkills( self.replaceSkills, csdefine.SPACE_TYPE_PLOT_LV40 )				# �滻��Ҽ�����
	
	def doReload( self, receiver, buffData ):
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.setTemp( "FLY_TEL_SKILL_FLAG", self.flag )
		receiver.setTemp( "NOT_USE_SELF_SKILL_FLAG", self.notUseSelfSkill )
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #������ӵֿ�
		
		actPet = receiver.pcg_getActPet()
		if actPet :
			actPet.entity.changeState( csdefine.ENTITY_STATE_FREE )
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )
		
		if self.replaceSkills :
			receiver.client.initSpaceSkills( self.replaceSkills, csdefine.SPACE_TYPE_PLOT_LV40 )				# �滻��Ҽ�����

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeTemp( "FLY_TEL_SKILL_FLAG" )
		receiver.removeTemp( "NOT_USE_SELF_SKILL_FLAG" )
		receiver.removeImmunityBuff( buffData[ "skill" ].getUID() )
		if self.replaceSkills :
			receiver.client.onCloseCopySpaceInterface()# ֪ͨ�����б����


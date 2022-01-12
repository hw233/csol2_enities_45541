# -*- coding: gb18030 -*-
#
# �������﹥��������ָ��·��Ѳ�ߣ����޶����ʹ��ָ���ļ���
# by ganjinxing 2011-11-26

#�Է���·�߽������߻� �Ƶ��ͻ��˽��� modify by wuxo 2012-3-2

"""
������Ч��
"""

# bigworld
import Math
import ResMgr
import BigWorld
# common
import csstatus
import csdefine
import csconst
from bwdebug import *
from Function import newUID
# cell
from SpellBase import *
from Buff_Normal import Buff_Normal
from VehicleHelper import getCurrVehicleID

STATES = csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_VEHICLE | csdefine.ACTION_FORBID_CALL_PET


class Buff_299032( Buff_Normal ):
	"""
	example:��贫��	BUFF	��ɫ�ڴ��ڼ䲻�ᱻ������ ���ᱻ��ҿ��ƣ� ���Ϸ���ģ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self.replaceSkills = []		# ���buff�����ֻ��ʹ����Щ����
		self.max_speed     =  0.0	#�ڴ�״̬�����������ٶ�
		self.requestSkills = []		#�ڷ����п��ܲ��ŵļ����б�
		self.flag = 0 #�Ƿ��жϿռ似��
		self.notUseSelfSkill = 0 #�Ƿ���ʹ���Լ��ļ���
		self.flyPos = ()	# ��ɳ�ʼλ��

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		skills = dict["Param1"].split(";")
		if len( skills ) > 1 :
			self.replaceSkills = eval( skills[0] )
			self.requestSkills = eval( skills[1] )
		if len( skills ) > 2 :
			self.flag = int( skills[2] )
		if len( skills ) > 3 :
			self.notUseSelfSkill = int( skills[3] )

		flyInfos = str( dict[ "Param3" ] ).split(";") 
		if len(flyInfos) > 2:
			self.max_speed = float(flyInfos[2])

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
		receiver.setTemp( "TEL_SKILLS", self.requestSkills )
		receiver.setTemp( "FLY_TEL_SKILL_FLAG", self.flag )
		receiver.setTemp( "NOT_USE_SELF_SKILL_FLAG", self.notUseSelfSkill )
		receiver.move_speed = self.max_speed
		receiver.updateTopSpeed()
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #������ӵֿ�

		if not self.flyPos:	# ��¼��ɳ�ʼλ��
			self.flyPos = Math.Vector3( receiver.position )

		actPet = receiver.pcg_getActPet()
		if actPet:
			actPet.entity.changeState( csdefine.ENTITY_STATE_FREE )
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )

		# �������
		if getCurrVehicleID( receiver ):
			receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )

		receiver.addFlag( csdefine.ROLE_FLAG_FLY_TELEPORT )

		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )

		if self.replaceSkills:
			receiver.client.initSpaceSkills( self.replaceSkills, csdefine.SPACE_TYPE_PLOT_LV40 )				# �滻��Ҽ�����

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�����¼��صĴ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		# ��ʱ��ʵ�����ߺ����Ѳ��
		Buff_Normal.doReload( self, receiver, buffData )
		if self.flyPos:	# �ص���ʼλ��
			receiver.position = self.flyPos
		# Ȼ�������buff
		receiver.removeBuffByBuffID( self._buffID, [csdefine.BUFF_INTERRUPT_NONE] )

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
		receiver.vehicleModelNum = 0	# ������vehicleModelNum
		receiver.removeFlag( csdefine.ROLE_FLAG_FLY_TELEPORT )
		receiver.removeImmunityBuff( buffData[ "skill" ].getUID() )
		receiver.actCounterDec( STATES )
		receiver.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )
		receiver.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		if self.replaceSkills:
			receiver.client.onCloseCopySpaceInterface()							# ֪ͨ�����б����
		receiver.calcMoveSpeed()
		receiver.removeTemp( "TEL_SKILLS" )
		receiver.removeTemp( "FLY_TEL_SKILL_FLAG" )
		receiver.removeTemp( "NOT_USE_SELF_SKILL_FLAG" )

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		if self.getUID() == 0:
			self.setUID( newUID() )

		return { "param": { "flyPos" : self.flyPos, "uid" : self.getUID() } }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = Buff_299032()
		obj.__dict__.update( self.__dict__ )
		obj.flyPos = data["param"]["flyPos"]

		if not data.has_key( "uid" ) or data["uid"] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data["uid"] )
		return obj

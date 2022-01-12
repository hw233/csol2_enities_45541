# -*- coding: gb18030 -*-

# 

import BigWorld
import csdefine
import csstatus
import ItemTypeEnum
import random
from SpellBase import *
from bwdebug import *
from Spell_BuffNormal import Spell_BuffNormal_With_Homing
import CooldownFlyweight
g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()

BUFF_TARGET_CASTER = 1
BUFF_TARGET_RECEIVER = 2

class Spell_721019( Spell_BuffNormal_With_Homing ):
	"""
	ϵͳ����
	"�ü���ͬʱ���ڶ�Ŀ���DEBUFF�Ͷ������BUFF����ͨBUFF���ܲ�������Ҫ��
	ͬʱ�������ж����ȶ�Ŀ���DEBUFFʩ�ųɹ���Ŀ���ô�DEBUFF�������ܲ����������BUFF
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
		icd = dict["param3"].split(" ") if len( dict["param3"] ) > 0 else []
		self._internalCD = []
		for i in icd:
			datas = i.split(":")
			self._internalCD.append( (int(datas[0]), int(datas[1]) ) )

	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		���ÿһ�������߽�����������������˺����ı����Եȵȡ�ͨ������´˽ӿ�����onArrive()���ã�
		�������п�����SpellUnit::receiveOnreal()�������ã����ڴ���һЩ��Ҫ�������ߵ�real entity�����������顣
		�������Ƿ���Ҫ��real entity���Ͻ��գ��ɼ����������receive()�������жϣ������ṩ��ػ��ơ�
		ע���˽ӿ�Ϊ�ɰ��е�onReceive()

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		self.receiveLinkBuff( caster, receiver )
		
	def receiveLinkBuff( self, caster, receiver ):
		"""
		��entity����buff��Ч��
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: ʩչ����
		@type  receiver: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		if len( self._buffLink ) <= 0:
			return
		_buff = self._buffLink[0]
		rate = _buff.getLinkRate()
		odd = random.randint( 1, 100 )
		# �в����������жϻ���
		if odd > rate:
			return
		self.setInternalCooldownInIntonate( caster )	# �����ڲ�CD
		buff_successed = False
		for bl in self._buffLink:
			buff = bl.getBuff()
			if buff.param3 is None or buff.param3 == "":
				continue
			if int(buff.param3) == BUFF_TARGET_CASTER:
				buff.receive( caster, caster )
			elif int(buff.param3) == BUFF_TARGET_RECEIVER:
				buff.receive( caster, receiver )
			buff_successed = True
		# ���۵� ���Ը��� ������������ʾ
		if buff_successed and caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			weapon = caster.getItem_( ItemTypeEnum.CEL_RIGHTHAND )
			if weapon and weapon.getType() in ItemTypeEnum.WEAPON_LIST and weapon.getGodWeaponSkillID() == self.getID():
				caster.statusMessage( csstatus.GW_SKILL_TRIGGERED, self.getName() )
			
	def cast( self, caster, target ):
		"""
		ȥ������ӿ��й����������ܵļ�⣬��˵�����Ǿ�������������ֶ������ʺ��ӵײ���
		"""
		self.setCooldownInIntonateOver( caster )
		# ��������
		self.doRequire_( caster )
		#֪ͨ���пͻ��˲��Ŷ���/����������
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )

		#��֤�ͻ��˺ͷ������˴����������һ��
		delay = self.calcDelay( caster, target )
		if delay <= 0.1:
			# ˲��
			caster.addCastQueue( self, target, 0.1 )
		else:
			# �ӳ�
			caster.addCastQueue( self, target, delay )

		# ����ʩ�����֪ͨ����һ���ܴ�����Ŷ(�Ƿ��ܴ����Ѿ���ʩ��û�κι�ϵ��)��
		# �����channel����(δʵ��)��ֻ�еȷ�����������ܵ���
		self.onSkillCastOver_( caster, target )
			
	def setInternalCooldownInIntonate( self, caster ):
		"""
		��������
		��ʩ�������÷����ü����ڲ���cooldownʱ��(buff�ɹ��ͷ�ʱ)

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
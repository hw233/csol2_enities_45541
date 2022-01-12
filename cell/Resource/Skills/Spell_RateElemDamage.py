# -*- coding: gb18030 -*-
#
# $Id: Spell_RateElemDamage.py,v 11:09 2010-8-27 jiangyi Exp $

import random
import csdefine
import csstatus
import ItemTypeEnum
import CooldownFlyweight
from bwdebug import *
from Spell_ElemDamage import Spell_ElemDamage
from SpellBase import *

g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()

class Spell_RateElemDamage( Spell_ElemDamage ):
	"""
	һ�����ʲ���Ԫ���˺�����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_ElemDamage.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		self._rate = int( dict["param1"] if len(dict["param1"]) > 0 else 0 )	# 0 ~ 100
		icd = dict["param3"].split(" ") if len( dict["param3"] ) > 0 else []
		self._internalCD = []
		for i in icd:
			datas = i.split(":")
			self._internalCD.append( (int(datas[0]), int(datas[1]) ) )
		Spell_ElemDamage.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if random.uniform(0,100) > self._rate:
			return
		self.setInternalCooldownInIntonate( caster )	# �����ڲ�CD
		# ���۵� ���Ը��� ������������ʾ
		if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			weapon = caster.getItem_( ItemTypeEnum.CEL_RIGHTHAND )
			if weapon and weapon.getType() in ItemTypeEnum.WEAPON_LIST and weapon.getGodWeaponSkillID() == self.getID():
				caster.statusMessage( csstatus.GW_SKILL_TRIGGERED, self.getName() )
		if receiver.isDestroyed:
			return

		damageType = self._damageType
		
		# ����������
		hit = self.calcHitProbability( caster, receiver )
		if receiver.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0 or not random.random() < hit:
			# ���㿪�˲���������û���㣬��˳�����п��ܴ��ڵģ���Ҫ֪ͨ�ܵ�0���˺�
			receiver.receiveSpell( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0, 0 )
			receiver.receiveDamage( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0 )
			return
		
		# ���㼼�ܹ������ͼ���ֱ���˺�
		skillDamage = self.calcSkillHitStrength( caster, receiver, 0, 0 )
		attackdamage = self.calcDamage( caster, receiver, skillDamage )

		# ����Ԫ���˺� Ԫ���˺��б� ������ֱ�Ϊ �����ױ�4��Ԫ�����������˺�
		elemDamageList = self.calcElemDamage( caster, receiver )

		# �����ܻ�װ���˺�
		equipmentDamage = int( skillDamage - attackdamage )
		receiver.equipDamage( equipmentDamage )

		# �ж��Ƿ񱬻�
		if self.isDoubleHit( caster, receiver ):
			damageType |= csdefine.DAMAGE_TYPE_FLAG_DOUBLE
			dm = self.calcDoubleMultiple( caster )
			# ��ͨ�˺�����
			attackdamage *= dm
			# Ԫ�ر���
			elemDamageList = [ x * dm for x in elemDamageList ]
			# ִ�гɹ����������Ϊ
			caster.doAttackerOnDoubleHit( receiver, damageType )	# �����ߴ���
			receiver.doVictimOnDoubleHit( caster, damageType )   	# �ܻ��ߴ���

		# ����˴ι������м� ִ�гɹ��мܺ����Ϊ
		if self.isResistHit( caster, receiver ):
			caster.doAttackerOnResistHit( receiver, damageType )	# �����ߴ���
			receiver.doVictimOnResistHit( caster, damageType )   	# �ܻ��ߴ���
			attackdamage -= attackdamage * receiver.resist_hit_derate
			damageType |= csdefine.DAMAGE_TYPE_RESIST_HIT

		# �˺�����  ��Ϊ�������֮���������ܻ�ο��˴ε�������������˺����Դ˽ӿڲ��ܷŵ�receiveDamage��
		attackdamage = self.calcDamageScissor( caster, receiver, attackdamage )

		# Ԫ���˺�����
		self.calcElemDamageScissor( receiver, elemDamageList )

		# ����ԭʼ�����˺�
		basedamage = attackdamage + elemDamageList[0] + elemDamageList[1] + elemDamageList[2] + elemDamageList[3]
		
		# �������� ��Ϊ�������֮���������ܻ�ο��˴ε�������������˺����Դ˽ӿڲ��ܷŵ�receiveDamage��
		finiDamage = self.calcShieldSuck( caster, receiver, attackdamage, self._damageType, elemDamageList )
		
		# ����Ԫ���˺�
		finiDamage_ss = finiDamage + elemDamageList[0] + elemDamageList[1] + elemDamageList[2] + elemDamageList[3]

		# ��ʾ�������ֿ����˺�
		if basedamage - finiDamage_ss > 0:
			SkillMessage.spell_DamageSuck( caster, receiver, int( basedamage - finiDamage_ss  ) )
		
		#�������С��Ƶд�����ʵ�ʼ��� 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		finiDamage *= rm
		elemDamageList = [ x * rm for x in elemDamageList ]
		
		finiDamage +=  elemDamageList[0] + elemDamageList[1] + elemDamageList[2] + elemDamageList[3]
		
		# �������ҵȼ������ɵ��˺��䶯 by����
		finiDamage = self.damageWithLevelWave( caster, receiver, finiDamage )

		# �����ֻ����˺� ����Ҳ�����1���˺�
		self.persentDamage( caster, receiver, damageType, max( 1, int( finiDamage ) ) )
		self.receiveLinkBuff( caster, receiver )					# ���ն����CombatSpellЧ����ͨ����buff(������ڵĻ�)
		
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
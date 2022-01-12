# -*- coding: gb18030 -*-
#


from SpellBase import *
from Skill_Normal import Skill_Normal
import csdefine
import csstatus
import ItemTypeEnum
import random
from bwdebug import *
from Spell_BuffNormal import Spell_BuffNormal
import CooldownFlyweight
g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()

class Skill_711016( Skill_Normal ):
	"""
	ÿһ��������ħ��

	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Skill_Normal.__init__( self )
	
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )
		self._p1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )  / 100.0	
		self.odd = int( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 )
		icd = dict["param3"].split(" ") if len( dict["param3"] ) > 0 else []
		self._internalCD = []
		for i in icd:
			datas = i.split(":")
			self._internalCD.append( (int(datas[0]), int(datas[1]) ) )

	def springOnHit( self, caster, receiver, damageType ):
		"""
		��������ʱ����Ϣ�ص�
		@param   caster: ʩ����
		@type    caster: Entity
		@param   receiver: ������
		@type    receiver: Entity
		"""
		n_odd = random.randint(0,100)
		if self.odd > 0 and n_odd > self.odd:
			return
		self.setInternalCooldownInIntonate( caster )	# �����ڲ�CD
		damage = caster.queryTemp( "lastDPS", 0 )
		if damage > 0:
			mpAdd = int( damage * self._p1 )
			if mpAdd > 0:
				caster.addMP( mpAdd )
				#%s�ָ�����%i�㷨��ֵ��
				caster.statusMessage( csstatus.SKILL_MP_BUFF_CURE, self.getName(), mpAdd )
		# ���۵� ���Ը��� ������������ʾ
		if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
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
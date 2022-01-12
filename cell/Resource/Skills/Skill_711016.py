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
	每一击概率吸魔。

	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Skill_Normal.__init__( self )
	
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
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
		技能命中时的消息回调
		@param   caster: 施法者
		@type    caster: Entity
		@param   receiver: 受术者
		@type    receiver: Entity
		"""
		n_odd = random.randint(0,100)
		if self.odd > 0 and n_odd > self.odd:
			return
		self.setInternalCooldownInIntonate( caster )	# 设置内部CD
		damage = caster.queryTemp( "lastDPS", 0 )
		if damage > 0:
			mpAdd = int( damage * self._p1 )
			if mpAdd > 0:
				caster.addMP( mpAdd )
				#%s恢复了你%i点法力值。
				caster.statusMessage( csstatus.SKILL_MP_BUFF_CURE, self.getName(), mpAdd )
		# 蛋疼到 无以复加 的神器技能提示
		if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			weapon = caster.getItem_( ItemTypeEnum.CEL_RIGHTHAND )
			if weapon and weapon.getType() in ItemTypeEnum.WEAPON_LIST and weapon.getGodWeaponSkillID() == self.getID():
				caster.statusMessage( csstatus.GW_SKILL_TRIGGERED, self.getName() )
			
	def cast( self, caster, target ):
		"""
		去除父类接口中关于引导技能的检测，话说俺到是觉得引导检测这种东西不适合扔底层咧
		"""
		self.setCooldownInIntonateOver( caster )
		# 处理消耗
		self.doRequire_( caster )
		#通知所有客户端播放动作/做其他事情
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )

		#保证客户端和服务器端处理的受术者一致
		delay = self.calcDelay( caster, target )
		if delay <= 0.1:
			# 瞬发
			caster.addCastQueue( self, target, 0.1 )
		else:
			# 延迟
			caster.addCastQueue( self, target, delay )

		# 法术施放完毕通知，不一定能打中人哦(是否能打中已经和施法没任何关系了)！
		# 如果是channel法术(未实现)，只有等法术结束后才能调用
		self.onSkillCastOver_( caster, target )
			
	def setInternalCooldownInIntonate( self, caster ):
		"""
		特殊需求
		给施法者设置法术该技能内部的cooldown时间(buff成功释放时)

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
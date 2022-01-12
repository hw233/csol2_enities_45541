# -*- coding:gb18030 -*-

from bwdebug import *
import csstatus
from Love3 import g_skills
from Spell_Item import Spell_Item

class Spell_344027( Spell_Item ):
	"""
	增加采集技能熟练度，此物品技能只能对自己释放，因为释放技能时无法检查目标的采集技能数据
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		self.skillID = 0
		self.sleight = 0
		
	def init( self, data ):
		"""
		"""
		Spell_Item.init( self, data )
		self.skillID = int( data["param1"] if data["param1"] > 0 else 0 )	# 要增加熟练度的采集技能id
		self.sleight = int( data["param2"] if data["param2"] > 0 else 0 )	# 要增加的熟练度
		
	def useableCheck( self, caster, target ):
		"""
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		主要是屏蔽信息，避免不能使用物品时提示使用技能
		"""
		if not caster.liv_hasLearnSkill( self.skillID ):
			return csstatus.LIVING_SKILL_HASNT_LEARN
		if caster.isSleightLevelMax( self.skillID ):
			return csstatus.LIVING_CANT_LEVEL_UP_SKILL
		return Spell_Item.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		"""
		skillInstance = g_skills[self.skillID]
		skillName = ""
		if skillInstance is None:
			ERROR_MSG( "Living skill %s is None."%(self.skillID) )
		else:
			skillName = skillInstance.getName()
		receiver.addSleight( self.skillID, self.sleight )
		receiver.statusMessage( csstatus.LIVING_SKILL_SLE_UP, skillName, receiver.getSleight( self.skillID ), receiver.getSleightMax( self.skillID ) )
		
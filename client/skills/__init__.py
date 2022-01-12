# -*- coding: gb18030 -*-
#
# $Id: __init__.py,v 1.35 2008-08-30 09:33:15 qilan Exp $
# 采用python字典方式重构 By qiulinhui @ 15:42 2009-4-18

from bwdebug import *
from SpellBase import *
from SmartImport import smartImport
from SkillTeachLoader import g_skillTeachDatas
import ItemTypeEnum
import Function
import csdefine
#from config.skill.Skill import Datas as SkillData
from config.skill.Skill.SkillDataMgr import Datas as SkillData
#
# 局部全局变量：所有的技能和Buff Dictionary
# Role/Monster通过_g_skills中的Skill来实现技能的动作和效果
# 每个技能一个Skill，Skill和角色无关
# 为什么不是Role.skills？避免出现大量的Skill对象挤在内存里，参见LightWeight设计模式。
# HashKey: Skill ID
#
_g_skills = {}
_g_skillData = SkillData  #引用config.skill.Skill.Datas

def _loadSkill( skillDict ):
	"""
	装载一个技能或Buff，不需被外部模块调用。
	"""
	inst = None
	classType = skillDict["Class" ]
	className = skillDict["ClientClass"]
	if len( className ) > 0:
		inst = smartImport( "skills." + className )()
	elif classType.startswith( "Buff_" ):
		inst = Buff()
	elif classType.startswith( "Skill_" ):
		inst = Skill()
	elif classType.startswith( "Spell_" ):
		inst = Spell()
	elif classType.startswith( "SpellBase.HomingSpell" ):
		inst = Spell()
	else:
		DEBUG_MSG( "Skill config file not found the class[%s-%s]." % ( classType, className ) )
	inst.init( skillDict )
	return inst


def getNormalAttack():
	"""
	获得普通物理攻击的Spell。
	"""
	return getSkill( csdefine.SKILL_ID_PHYSICS )

def getSkill( skillID ):
	"""
	获得Skill ID对应的Skill。
	@param skillID:			Skill ID
	@type skillID:			Integer
	"""
	global _g_skills
	try:
		return _g_skills[ skillID ]
	except:
		DEBUG_MSG( "load skill %i." % skillID )

		global _g_skillData
		# 此处主要是兼容 BUFF的加载， skillID / 100 是去掉了BUFF的编号的
		# 如果找不到该技能 我们则把他当作一个BUFFID看待 尝试去掉BUFF位 看是不是有父体技能
		if not _g_skillData.has_key( skillID ):
			buffID = skillID / 100
			if _g_skillData.has_key( buffID ):
				skillDict = _g_skillData[ buffID ]
				if skillDict is None :													# 08.07.23 -- hyw
					ERROR_MSG( "skill config '%i' is not exist!" % buffID )
					return
				skill = _loadSkill( skillDict ) #调用register接口注册到_g_skills字典数据
				_g_skills[ buffID ] = skill
				try:
					return _g_skills[ skillID ]
				except:
					ERROR_MSG( "buff config '%i' is not exist!" % skillID )
					return
			else:
				ERROR_MSG( "load skill %i is Error. can't find the section." % skillID )
				return
		else:
			skillDict = _g_skillData[ skillID ]
			if skillDict is None:													# 08.07.23 -- hyw
				ERROR_MSG( "skill config '%i' is not exist!" % skillID )
				return
			skill = _loadSkill( skillDict )
			_g_skills[ skillID ] = skill
			return skill

def register( key, skill ):
	"""
	"""
	global _g_skills
	assert not _g_skills.has_key( key ) and skill != None, "KEY %s skill %i" % ( key, skill != None )
	_g_skills[ key ] = skill



def binarySearchSKillID( playerLv, skillID ):	# 15:00 2008-11-24,wsf
	"""
	在_g_skillData数据里，使用2分查找适合playerLv的技能id

	@param playerLv : 玩家级别
	@type playerLv : UINT8
	@param skillID : 高等级技能
	@type skillID : INT64
	"""
	global _g_skillData

	headString = str( skillID )[:-3]		# 获得技能id的第一段
	tailInt = int( str( skillID )[-3:] )	# 获得技能的级别
	min = 001
	max = tailInt
	fitSkillID = -1
	while min <= max:
		mid = ( min + max ) / 2
		midStr = str( mid )
		while len( midStr ) < 3:	# 不够3位就补0
			midStr = "0" + midStr
		tempSkillID = int( headString + midStr )
		if not _g_skillData.has_key( tempSkillID ):
			return fitSkillID

		castObjLevelMin = _g_skillData[ tempSkillID ]["CastObjLevelMin"]
		if castObjLevelMin == playerLv:
			return tempSkillID
		if castObjLevelMin < playerLv:
			min = mid + 1
			fitSkillID = tempSkillID
		else:
			max = mid - 1
	return fitSkillID

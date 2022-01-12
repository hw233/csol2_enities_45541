# -*- coding: gb18030 -*-
#
# $Id: __init__.py,v 1.35 2008-08-30 09:33:15 qilan Exp $
# ����python�ֵ䷽ʽ�ع� By qiulinhui @ 15:42 2009-4-18

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
# �ֲ�ȫ�ֱ��������еļ��ܺ�Buff Dictionary
# Role/Monsterͨ��_g_skills�е�Skill��ʵ�ּ��ܵĶ�����Ч��
# ÿ������һ��Skill��Skill�ͽ�ɫ�޹�
# Ϊʲô����Role.skills��������ִ�����Skill�������ڴ���μ�LightWeight���ģʽ��
# HashKey: Skill ID
#
_g_skills = {}
_g_skillData = SkillData  #����config.skill.Skill.Datas

def _loadSkill( skillDict ):
	"""
	װ��һ�����ܻ�Buff�����豻�ⲿģ����á�
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
	�����ͨ��������Spell��
	"""
	return getSkill( csdefine.SKILL_ID_PHYSICS )

def getSkill( skillID ):
	"""
	���Skill ID��Ӧ��Skill��
	@param skillID:			Skill ID
	@type skillID:			Integer
	"""
	global _g_skills
	try:
		return _g_skills[ skillID ]
	except:
		DEBUG_MSG( "load skill %i." % skillID )

		global _g_skillData
		# �˴���Ҫ�Ǽ��� BUFF�ļ��أ� skillID / 100 ��ȥ����BUFF�ı�ŵ�
		# ����Ҳ����ü��� �������������һ��BUFFID���� ����ȥ��BUFFλ ���ǲ����и��弼��
		if not _g_skillData.has_key( skillID ):
			buffID = skillID / 100
			if _g_skillData.has_key( buffID ):
				skillDict = _g_skillData[ buffID ]
				if skillDict is None :													# 08.07.23 -- hyw
					ERROR_MSG( "skill config '%i' is not exist!" % buffID )
					return
				skill = _loadSkill( skillDict ) #����register�ӿ�ע�ᵽ_g_skills�ֵ�����
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
	��_g_skillData�����ʹ��2�ֲ����ʺ�playerLv�ļ���id

	@param playerLv : ��Ҽ���
	@type playerLv : UINT8
	@param skillID : �ߵȼ�����
	@type skillID : INT64
	"""
	global _g_skillData

	headString = str( skillID )[:-3]		# ��ü���id�ĵ�һ��
	tailInt = int( str( skillID )[-3:] )	# ��ü��ܵļ���
	min = 001
	max = tailInt
	fitSkillID = -1
	while min <= max:
		mid = ( min + max ) / 2
		midStr = str( mid )
		while len( midStr ) < 3:	# ����3λ�Ͳ�0
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

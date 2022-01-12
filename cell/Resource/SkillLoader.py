# -*- coding: gb18030 -*-
#
# $Id: SkillLoader.py,v 1.15 2008-07-18 04:12:55 kebiao Exp $

"""
技能资源加载部分。
"""

import Language
from bwdebug import *
from SmartImport import smartImport
from Skills import SpellBase
from csdefine import *


class SkillLoader:
	_instance = None
	def __init__( self ):
		"""
		构造函数。
		"""
		assert SkillLoader._instance is None		# 不允许有两个以上的实例
		self._datas = {}	# key is Skill::_id and value is instance of Skill which derive from it.
		SpellBase.Skill.setInstance( self )
		SkillLoader._instance = self


	@staticmethod
	def instance():
		"""
		通过 action id 获取action实例
		"""
		if SkillLoader._instance is None:
			SkillLoader._instance = SkillLoader()
		return SkillLoader._instance

	def __getitem__( self, key ):
		"""
		取得Skill实例
		"""
		try:
			return self._datas[ key ]
		except:
			return self.loadSkill( str( key ) )
	
	def loadSkill( self, skillID ):
		"""
		指定加载某技能或者BUFF
		@type		skillID: string
		"""
		from config.skill.Skill.SkillDataMgr import Datas as SKILL_DATA
		DEBUG_MSG( "load skill %s." % skillID )
		buffID = 0
		iskillID = int( skillID )
		print "=====>>>>>iskillID = ", iskillID
		if not SKILL_DATA.has_key( iskillID ):
			buffID = iskillID
			iskillID /= 100
			print "=====>>>>>buffID = ", buffID
			if not SKILL_DATA.has_key( iskillID ):
				raise KeyError, "skill or buff config '%s' is not exist!" % buffID
		
		dictData = SKILL_DATA[ iskillID ]
		#instance = smartImport( "Resource.Skills." + dictData["Class"] )()
		scriptName,className = dictData["Class"].split(":")
		instance = getattr( SKILL_DATA.getScript( scriptName ),className )()
		instance.init( dictData )
		iskillID = int( instance.getID() )
		assert not self._datas.has_key( iskillID ), "id: %s, class: Resource.Skills.%s is exist already " % ( iskillID, dictData["Class"] )
		self.register( iskillID, instance )
		if buffID > 0:
			return self._datas[buffID]
		return self._datas[iskillID]
		
	def has( self, skillID ):
		"""
		@type		skillID: int
		"""
		from config.skill.Skill.SkillDataMgr import Datas as SKILL_DATA
		return skillID in self._datas or SKILL_DATA.has_key( skillID )

	def register( self, key, skill ):
		"""
		"""
		self._datas[key] = skill


class BuffLimit:
	"""
	BUFF的限定规则， 包括 BUFF的类型叠加上限 和 BUFF来源之间的相互制约关系
	"""
	_instance = None
	def __init__( self, bufflimitPath = None ):
		"""
		构造函数。
		@param configPath:	技能配置文件路径
		@type  configPath:	string
		"""
		assert BuffLimit._instance is None		# 不允许有两个以上的实例

		self._buffClassLimit = {} # BUFF大类的同性质（BUFF，DEBUFF）同类型的同时存在的最大数量 { buff: {X大类:最多存在5个,...}, debuff:{...} }
		self._buffOriginLimit = {} #BUFF小类(来源)同时存在的条件 {该小类: [不可和其小类同时存在,不可和其小类同时存在 ... ] }
		BuffLimit._instance = self

		if bufflimitPath is not None:
			self.load( bufflimitPath )

	@staticmethod
	def instance():
		"""
		通过 action id 获取action实例
		"""
		if BuffLimit._instance is None:
			BuffLimit._instance = BuffLimit()
		return BuffLimit._instance

	def load( self, filePath ):
		"""
		加载BUFF限制数据。
		self._buffClassLimit = {} # BUFF大类的同性质（BUFF，DEBUFF）同类型的同时存在的最大数量 { buff: {X大类:最多存在5个,...}, debuff:{...} }
		self._buffOriginLimit = {} #BUFF小类(来源)同时存在的条件 {该小类: [不可和其小类同时存在,不可和其小类同时存在 ... ] }
		@param configPath:	技能配置文件路径
		@type  configPath:	string
		"""
		sec = Language.openConfigSection(filePath)
		if sec is None:
			raise SystemError, "Can not Load %s " % filePath

		self._buffClassLimit = {
			SKILL_EFFECT_STATE_BENIGN : {},
			SKILL_EFFECT_STATE_MALIGNANT : {},
			SKILL_EFFECT_STATE_NONE : {}
		}

		for subsec in sec["BUFF_LIMIT"].values():
			self._buffClassLimit[SKILL_EFFECT_STATE_BENIGN][ eval( subsec.name ) ] = subsec[ "BUFF" ].asInt
			self._buffClassLimit[SKILL_EFFECT_STATE_MALIGNANT][ eval( subsec.name ) ] = subsec[ "DEBUFF" ].asInt
			self._buffClassLimit[SKILL_EFFECT_STATE_NONE][ eval( subsec.name ) ] = subsec[ "XBUFF" ].asInt
		for subsec in sec["BUFF_ORIGIN_LIMIT"].values():
			self._buffOriginLimit[ eval( subsec.name ) ] = tuple( eval( '(' + subsec.asString.replace(' ','').replace('\r','').replace('\n','') + ',)' ) )

	def getBuffLimit( self, type, effectType ):
		"""
		取得该BUFF类型的最大上限
		@param effectType: 良性，恶性
		@param type：缓慢作用效果	影响行为效果	治疗效果变化	易伤效果	特殊符合类	免疫效果
		"""
		return self._buffClassLimit[ effectType ][ type ]

	def getSourceLimit( self, sourceType ):
		"""
		取得该BUFF来源类型所受限的其他的来源类型
		@param sourceType: 来源类型
		"""
		return self._buffOriginLimit[ sourceType ]

def instance():
	return SkillLoader.instance()
def buffLimitInstance():
	return BuffLimit.instance()

g_skills = SkillLoader.instance()
g_buffLimit = BuffLimit.instance()


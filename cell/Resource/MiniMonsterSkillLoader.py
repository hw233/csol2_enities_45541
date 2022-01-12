# -*- coding: gb18030 -*-
"""
加载MiniMonster的技能配置
"""

from bwdebug import *
import Language

class MiniMonsterSkillLoader:
	"""
	精简型怪物技能配置加载
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert MiniMonsterSkillLoader._instance is None
		self.miniMonsterSkill = {} 	# 精简怪物技能配置表
		self.load( "config/server/gameObject/MiniMonsterSkill.xml" )
		MiniMonsterSkillLoader._instance = self

	@staticmethod
	def instance():
		"""
		"""
		if MiniMonsterSkillLoader._instance is None:
			MiniMonsterSkillLoader._instance = MiniMonsterSkillLoader()
		return MiniMonsterSkillLoader._instance

	def load( self, configFile ):
		"""
		读取精简怪物技能配置表
		"""
		if len( configFile ) <= 0:
			return
		sect = Language.openConfigSection( configFile )
		assert sect is not None, "Open %s false." % configFile
		for node in sect.values():
			className = node["className"].asString
			if not self.miniMonsterSkill.has_key( className ):
				self.miniMonsterSkill[className] = []
			self.miniMonsterSkill[ className ] = node["skillID"].asInt

		# 读取完毕则关闭打开的文件
		Language.purgeConfig( configFile )

	def getSkillIDByClassName( self, className ):
		"""
		根据className获得skillID
		"""
		skillID = 1
		try:
			skillID = self.miniMonsterSkill[className ]
		except:
			ERROR_MSG( "ClassName %s has not in config MiniMonsterSkill.xml " % className )
		return skillID

g_MiniMonsterSkill = MiniMonsterSkillLoader.instance()
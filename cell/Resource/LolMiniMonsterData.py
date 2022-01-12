# -*- coding: gb18030 -*-
"""
加载MiniMonster_Lol的巡逻及敌对怪物数据
"""

from bwdebug import *
import Language

class LolMiniMonsterData:
	"""
	英雄联盟副本小怪数据
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert LolMiniMonsterData._instance is None
		self.lolMiniMonsterData = {} 	# 精简怪物技能配置表
		self.load( "config/server/LolMiniMonsterData.xml" )
		LolMiniMonsterData._instance = self

	@staticmethod
	def instance():
		"""
		"""
		if LolMiniMonsterData._instance is None:
			LolMiniMonsterData._instance = LolMiniMonsterData()
		return LolMiniMonsterData._instance

	def load( self, configFile ):
		"""
		英雄联盟副本怪物数据加载
		"""
		if len( configFile ) <= 0:
			return
		sect = Language.openConfigSection( configFile )
		assert sect is not None, "Open %s false." % configFile
		for node in sect.values():
			className = node["className"].asString
			if not self.lolMiniMonsterData.has_key( className ):
				self.lolMiniMonsterData[className] = {}
			self.lolMiniMonsterData[ className ]["patrolList"]= node["patrolList"].asString
			self.lolMiniMonsterData[ className ]["enemyIDs"] = node["enemyIDs"].asString

		# 读取完毕则关闭打开的文件
		Language.purgeConfig( configFile )

	def getLolMiniMonsterData( self, className ):
		"""
		根据className获得skillID
		"""
		data = {}
		try:
			data = self.lolMiniMonsterData[className ]
		except:
			ERROR_MSG( "ClassName %s has not in config LolMiniMonsterData.xml " % className )
		return data

g_MiniMonsterSkill = LolMiniMonsterData.instance()
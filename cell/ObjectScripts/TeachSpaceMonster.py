# -*- coding:gb18030 -*-

from Monster import Monster
from LevelEXP import TeachSpaceAmendExp

class TeachSpaceMonster( Monster ):
	"""
	师徒副本小怪脚本
	"""
	def getExpAmendRate( self, levelFall ):
		"""
		根据等级差获得经验修正值
		
		@param levelFall : 玩家和怪物的等级差
		"""
		return TeachSpaceAmendExp.instance().getLevelRate( levelFall )
		
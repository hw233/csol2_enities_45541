# -*- coding: gb18030 -*-

import Language
from bwdebug import *
from config.server import NPCExcData

class NPCExcDataLoader:
	"""
	NPC攻击力配置表加载
	DPS、DPS波动、攻击速度、攻击距离、法术攻击、物理防御、法术防御
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert NPCExcDataLoader._instance is None
		# key == 对应的怪物职业
		# value == 在该职业下的数据字典
		#		key == 对应的怪物等级
		# 		value == 在该等级下的属性值
		# like as { 战士 : { 等级 : { DPS : xxx, DPS波动 : xxx, 攻击速度 : xxx, 攻击距离 : xxx, 法术攻击 : xxx, 物理防御 : xxx, 法术防御 : xxx }, ... }, ...}
		self._datas = NPCExcData.Datas
		NPCExcDataLoader._instance = self

	def get( self, raceclass, level  ):
		"""
		返回属性配置
		"""
		try:
			# 需要执行(raceclass >> 4) & 0xf的原因是因为当前entity.getClass()返回的是一个左移了4位的值，详看csdefine.CLASS_*
			return self._datas[(raceclass >> 4) & 0xf][level]
		except:
			if level != 0:
				ERROR_MSG( "( Raceclass %i, Level %i ) can not find in table NPCExcDataConfig" % ( raceclass, level ) )
			return {
					"data_dps" : 5.0,
					"data_dpsWave": -0.28,
					"data_speed": 0.0,
					"data_range": 0.0,
					"data_magicDamage": 10,
					"data_physicsArmor": 100,
					"data_magicArmor": 100,
					}

	@staticmethod
	def instance():
		"""
		"""
		if NPCExcDataLoader._instance is None:
			NPCExcDataLoader._instance = NPCExcDataLoader()
		return NPCExcDataLoader._instance
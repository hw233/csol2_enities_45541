# -*- coding: gb18030 -*-
#
# 算卦占卜
#

import Language
from bwdebug import *
from csarithmetic import getRandomElement

class SuanGuaZhanBuLoader:
	"""
	用物品换物品的表格加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert SuanGuaZhanBuLoader._instance is None
		SuanGuaZhanBuLoader._instance = self

	def load( self, configPath ):
		"""
		加载配置表
		"""
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s false." % configPath

		self._money = section.readString( "money" )	# 占卜金钱消耗，配置："30-59,60-89,90-119,120-150;1,2,5,15"
		self._skills = section.readString( "skills" )	# 占卜技能和机率，配置："ID1:机率1;ID2:机率2"

		self._expendKey = []	# [[30, 59], [60, 89], [90, 119], [120, 150]]
		self._expendValue = []	# [1,2,5,15]
		keyStr = self._money.split( ";" )[0]
		valStr = self._money.split( ";" )[1]
		for e in keyStr.split(","):
			self._expendKey.append( [ int(e.split( "-" )[0]), int(e.split( "-" )[1]) ] )
		for e in valStr.split(","):
			self._expendValue.append( int(e) )

		self._skillIDList = []				# 存放技能的ID
		self._skillOddsList = []			# 存放技能ID对应的机率数组
		for e in self._skills.split( ";" ):
			self._skillIDList.append( str( e.split( ":" )[0] ) )
			self._skillOddsList.append( float( e.split( ":" )[1] ) )

		# 清除缓冲
		Language.purgeConfig( configPath )

	def getNeedMoney( self, level ):
		"""
		获取需要消耗金钱
		"""
		index = 0
		for e in self._expendKey:
			if level <= e[1] and level >= e[0]:
				index = self._expendKey.index( e )
				break
		return int( self._expendValue[index] )

	def getRandomSkill( self ):
		"""
		获取一个随机技能
		"""
		return int( getRandomElement( self._skillIDList, self._skillOddsList ) )

	@classmethod
	def instance( SELF ):
		"""
		"""
		if SELF._instance is None:
			SELF._instance = SuanGuaZhanBuLoader()
		return SELF._instance

g_SuanGuaZhanBuLoader = SuanGuaZhanBuLoader.instance()
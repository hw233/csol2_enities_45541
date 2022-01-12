# -*- coding: gb18030 -*-
#
# $Id: LevelEXP.py,v 1.5 2008-01-08 06:39:22 yangkai Exp $

"""
@summary			:	加载经验值等级模块
2007/08/01: modified by huangyongwei
"""

import Language
from bwdebug import *
from config import VehicleExp
from config import Fodders
from config import pet_exp
from config import role_exp
from config import AmendExp as amend_exp
from config import TeachSpaceMonsterAmendExp as teach_space_amend_exp
from config import tong_exp


# --------------------------------------------------------------------
# about role
# --------------------------------------------------------------------
class RoleLevelEXP :
	__maxLevel = 1
	__data = {}

	@classmethod
	def initialize( SELF ) :
		SELF.__maxLevel = role_exp.MaxLevel
		SELF.__data = role_exp.Datas

	@classmethod
	def getEXPMax( SELF, level ):
		"""
		get match exp value
		@type			level : int
		@param			level : level of the pet
		@rtype				  : INT32
		@return				  : EXP value
		"""
		try : return SELF.__data[level]
		except :
			ERROR_MSG( "error level or you haven't initialized!" )
		return 0

	@classmethod
	def getMaxLevel( SELF ):
		"""
		get the max. of the pet
		@rtype				: int
		@return				: the max level
		"""
		return SELF.__maxLevel


# --------------------------------------------------------------------
# about pet
# --------------------------------------------------------------------
class PetLevelEXP :
	__maxLevel = 1
	__data = {}

	@classmethod
	def initialize( SELF ) :
		SELF.__maxLevel = pet_exp.MaxLevel
		SELF.__data = pet_exp.Datas

	@classmethod
	def getEXPMax( SELF, level ):
		"""
		get match exp value
		@type			level : int
		@param			level : level of the pet
		@rtype				  : INT32
		@return				  : EXP value
		"""
		try : return SELF.__data[level]
		except :
			ERROR_MSG( "error level or you haven't initialized!" )
		return 0

	@classmethod
	def getMaxLevel( SELF ):
		"""
		get the max. of the pet
		@rtype				: int
		@return				: the max level
		"""
		return SELF.__maxLevel

# --------------------------------------------------------------------
# about Vehicle
# --------------------------------------------------------------------
class VehicleLevelExp:
	"""
	骑宠等级经验值
	@ivar _data: 全局数据字典;  like as {key：value }
	@type _data: dict
	"""
	_instance = None

	def __init__( self, xmlConf = None ):
		assert VehicleLevelExp._instance is None, "instance already exist in"
		self._datas = VehicleExp.Datas
		self._fodders = Fodders.Fodders

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = VehicleLevelExp()
		return self._instance

	def getExp( self, level ):
		"""
		获取骑宠当前等级升级所需经验值
		@type  xmlConf	: string
		@param xmlConf	: 配置文件名
		@return			: None
		"""
		try:
			return self._datas[ level ]["exp"]
		except:
			ERROR_MSG( "Can't find VehicleLevelExp config by level(%s)" % level )
			return 0

	
	def getFodderID( self, srcItemID ):
		"""
		获取骑宠喂食所需物品对应ID
		@type  level	: INT
		@param level	: 当前等级
		@return			: INT32
		"""
		try:
			return self._fodders[srcItemID]
		except:
			ERROR_MSG( "Can't find VehicleFodder config." )
			return []

# --------------------------------------------------------------------
# about Exp amend
# --------------------------------------------------------------------
class AmendExp:
	"""
	修正经验模块，用于玩家与怪物等级差值的经验修正
	@ivar _data: 全局数据字典;  like as {key：value }
	@type _data: dict
	"""
	_instance = None

	def __init__( self, xmlConf = None ):
		assert AmendExp._instance is None, "instance already exist in"
		self._datas = amend_exp.Datas

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = AmendExp()
		return self._instance

	def getLevelRate( self, waveLevel ):
		"""
		get match exp value
		@type			waveLevel : int
		@param			waveLevel : Role.level - NPC.level
		@rtype				  : float
		@return				  : EXP Rate
		"""
		try:
			return self._datas[waveLevel]
		except:
			# 玩家至少能获得10%的经验
			return 0.1
			
class TeachSpaceAmendExp:
	"""
	师徒副本怪物经验修正，用于玩家与师徒副本怪物等级差值的经验修正
	@ivar _data: 全局数据字典;  like as {key：value }
	@type _data: dict
	"""
	_instance = None
	def __init__( self ):
		assert TeachSpaceAmendExp._instance is None, "instance already has a presence!!"
		self._datas = teach_space_amend_exp.Datas
		
	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = TeachSpaceAmendExp()
		return self._instance
		
	def getLevelRate( self, waveLevel ):
		"""
		get match exp value
		@type			waveLevel : int
		@param			waveLevel : Role.level - NPC.level
		@rtype				  : float
		@return				  : EXP Rate
		"""
		try:
			return self._datas[waveLevel]
		except:
			# 玩家至少能获得10%的经验
			return 0.1
			

# --------------------------------------------------------------------
# about tong
# --------------------------------------------------------------------
class TongLevelEXP :
	__maxLevel = 1
	__data = {}

	@classmethod
	def initialize( SELF ) :
		SELF.__maxLevel = tong_exp.MaxLevel
		SELF.__data = tong_exp.Datas

	@classmethod
	def getEXPMax( SELF, level ):
		"""
		get match exp value
		@type			level : int
		@param			level : level of the pet
		@rtype				  : INT32
		@return				  : EXP value
		"""
		try : 
			return SELF.__data[level]
		except :
			ERROR_MSG( "error level or you haven't initialized!" )
			return 0

	@classmethod
	def getMaxLevel( SELF ):
		"""
		get the max. of the pet
		@rtype				: int
		@return				: the max level
		"""
		return SELF.__maxLevel

# -*- coding: gb18030 -*-
#
# $Id: LevelEXP.py,v 1.5 2008-01-08 06:39:22 yangkai Exp $

"""
@summary			:	���ؾ���ֵ�ȼ�ģ��
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
	���ȼ�����ֵ
	@ivar _data: ȫ�������ֵ�;  like as {key��value }
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
		��ȡ��赱ǰ�ȼ��������辭��ֵ
		@type  xmlConf	: string
		@param xmlConf	: �����ļ���
		@return			: None
		"""
		try:
			return self._datas[ level ]["exp"]
		except:
			ERROR_MSG( "Can't find VehicleLevelExp config by level(%s)" % level )
			return 0

	
	def getFodderID( self, srcItemID ):
		"""
		��ȡ���ιʳ������Ʒ��ӦID
		@type  level	: INT
		@param level	: ��ǰ�ȼ�
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
	��������ģ�飬������������ȼ���ֵ�ľ�������
	@ivar _data: ȫ�������ֵ�;  like as {key��value }
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
			# ��������ܻ��10%�ľ���
			return 0.1
			
class TeachSpaceAmendExp:
	"""
	ʦͽ�������ﾭ�����������������ʦͽ��������ȼ���ֵ�ľ�������
	@ivar _data: ȫ�������ֵ�;  like as {key��value }
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
			# ��������ܻ��10%�ľ���
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

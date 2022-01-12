# -*- coding: gb18030 -*-

from bwdebug import *
import Language
import random
import csconst
from config.item import TalismanExtraParam
from config.item import TalismanGrade
from config.item import TalismanPotential
from config.item import TalismanSkill
from config.item import TalismanFlawConfig

class TalismanEffectLoader:
	"""
	�����������ü���
	"""
	_instance = None

	def __init__( self ):
		assert TalismanEffectLoader._instance is None, "instance already exist in"
		self._aDatas = TalismanGrade.Datas		# like as { grade : { "tm_upItem" : itemID, ... }, ... }
		self._gDatas = TalismanExtraParam.server_gDatas		# like as { id : { "tm_odds" : odds, "tm_effectID" : effectID, ... }
		self._tDatas = TalismanExtraParam.server_tDatas		# like as { grade : [tm_id,....] , ... }
		self._sDatas = TalismanSkill.sDatas		# like as { level : odds, ... }
		self._pDatas = TalismanPotential.Datas		# like as { skill_level, potential, ... }
		self._eDatas = TalismanSkill.Datas
		self._fDatas = TalismanFlawConfig.Datas
		self._iDatas = {}
		self._baseUpParam = 0.0
		self.load( )

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = TalismanEffectLoader()
		return self._instance

	def load( self  ):
		"""
		���ط����Զ�����������
		@return:        None
		"""
		self.__loadBaseParamConfig()
		self.__loadItemConfig()

	def __loadBaseParamConfig( self, xmlConf = "config/item/TalismanBaseParam.xml" ):
		"""
		���ط�����������������������
		@type  xmlConf: string
		@param xmlConf: �����ļ���
		@return:        None
		"""
		successCount = 0
		failedCount = 0
		section = Language.openConfigSection( xmlConf )
		if section is None:
			raise SystemError, "Can not Load : %s " % xmlConf
		for csect in section.values():
			self._baseUpParam = csect["tm_baseParam"].asFloat
			successCount += 1
		DEBUG_MSG("Loading TalismanBaseParam config successCount = %i , failedCount = %i" % ( successCount, failedCount ))
		Language.purgeConfig( xmlConf )

	def __loadItemConfig( self, xmlConf = "config/item/TalismanItemSkill.xml" ):
		"""
		���ط�������Ӧ����
		@type  xmlConf: string
		@param xmlConf: �����ļ���
		@return:        None
		"""
		successCount = 0
		failedCount = 0
		section = Language.openConfigSection( xmlConf )
		if section is None:
			raise SystemError, "Can not Load : %s " % xmlConf
		for csect in section.values():
			tm_itemID = csect["tm_itemID"]
			if tm_itemID is None:
				failedCount += 1
				continue
			skillIDs = [ int(k) for k in csect["tm_skillID"].asString.split(";") ]
			self._iDatas[tm_itemID.asInt] = skillIDs
			successCount += 1
		DEBUG_MSG("Loading TalismanItemSkill successCount = %i , failedCount = %i" % ( successCount, failedCount ))
		Language.purgeConfig( xmlConf )

	def getOdds( self, level ):
		"""
		��ȡ������ǰ�ȼ�������ü��ܵĸ���
		@type	level	:	INT8
		@param	level	:	�����ȼ�
		@return			��	Float
		"""
		try:
			return self._sDatas[level]
		except KeyError:
			ERROR_MSG( "Can't find OddsConfig by level(%s)" % level )
			return 0.0

	def getPotential( self, skillLevel ):
		"""
		��ȡ�������ܵ�ǰ�ȼ����������Ǳ�ܵ�
		@type	skillLevel	:	INT8
		@param	skillLevel	:	�������ܵȼ�
		@return				��	INT32
		"""
		try:
			return self._pDatas[skillLevel+1]
		except KeyError:
			ERROR_MSG( "Can't find PotentialConfig by SkillLevel(%s)" % skillLevel )
			return 0

	def getMaxExp( self, explevel ):
		"""
		��ȡ������������ľ���
		@type	explevel	:	INT8
		@param	explevel	:	�����ȼ�
		@return				��	INT32
		"""
		try:
			return self._eDatas[explevel+1]
		except KeyError:
			ERROR_MSG( "Can't find TalisExpConfig by explevel(%s)" % explevel )
			return 0

	def getSkillListByID( self, itemID ):
		"""
		��ȡ������Ӧ���ܱ�
		@type	itemID	:	INT8
		@param	itemID	:	�����ȼ�
		@return			��	LIST
		"""
		try:
			return self._iDatas[itemID]
		except KeyError:
			ERROR_MSG( "Can't find TalismanItemSkill by itemID(%s)" % itemID )
			return []

	def getEffectID( self, tmID ):
		"""
		���ݷ����Զ�������ID��ȡ��Ӧ��װ��ID
		@type	tmID	:	INT8
		@param	tmID	:	�����Զ�������ID
		@return			:	int16
		"""
		try:
			return self._gDatas[tmID]["tm_effectID"]
		except KeyError:
			ERROR_MSG( "Can't find tm_EffectID config by tmID(%s)" % tmID )
			return 0

	def getInitValue( self, tmID ):
		"""
		���ݷ����Զ�������ID��ȡ��Ӧ��װ��ID����ʱ�ĳ�ֵ
		@type	tmID	:	INT8
		@param	tmID	:	�����Զ�������ID
		@return			:	Float
		"""
		try:
			return self._gDatas[tmID]["tm_initValue"]
		except KeyError:
			ERROR_MSG( "Can't find tm_initValue config by tmID(%s)" % tmID )
			return 0.0

	def getUpParam( self, tmID ):
		"""
		���ݷ����Զ�������ID��ȡ��Ӧ��װ��ID����ʱ��Ŀ��Ʋ���
		@type	tmID	:	INT8
		@param	tmID	:	�����Զ�������ID
		@return			:	Float
		"""
		try:
			return self._gDatas[tmID]["tm_upParam"]
		except KeyError:
			ERROR_MSG( "Can't find tm_upParam config by tmID(%s)" % tmID )
			return 0.0

	def getBaseUpParam( self ):
		"""
		��ȡ�������������������Ʋ���
		"""
		return self._baseUpParam

	def getEffects( self, grade ):
		"""
		���ݷ�����Ʒ�������ȡ��������
		@type	tmID	:	INT8
		@param	tmID	:	�����Զ�������ID
		@return			:	Int8
		"""
		# ����й����б��Ƿ������Զ�Ӧ�ĸ�������û��������
		data = self._tDatas.get( grade )
		if data is None: return 0
		r = random.random()
		for id, odds in data:
			if r <= odds:
				return id
		return 0

	def getUpItem( self, grade ):
		"""
		��ȡ����Ʒ������������Ʒ
		@type	grade	:	INT8
		@param	grade	:	����Ʒ��
		@return			:	INT
		"""
		try:
			return self._aDatas[grade]["tm_upItem"]
		except KeyError:
			ERROR_MSG( "Can't find tm_upItem config by grade(%s)" % grade )
			return 0

	def getUpItemAmount( self, grade ):
		"""
		��ȡ����Ʒ������������Ʒ����
		@type	grade	:	INT8
		@param	grade	:	����Ʒ��
		@return			:	INT
		"""
		try:
			return self._aDatas[grade]["tm_upItemAmount"]
		except KeyError:
			ERROR_MSG( "Can't find tm_upItemAmount config by grade(%s)" % grade )
			return 0

	def getActivatItem( self, grade ):
		"""
		��ȡ����Ʒ����������������Ʒ
		@type	grade	:	INT8
		@param	grade	:	����Ʒ��
		@return			:	INT
		"""
		try:
			return self._aDatas[grade]["tm_activatItem"]
		except KeyError:
			ERROR_MSG( "Can't find tm_activatItem config by grade(%s)" % grade )
			return 0

	def getActivatItemAmount( self, grade ):
		"""
		��ȡ����Ʒ����������������Ʒ����
		@type	grade	:	INT8
		@param	grade	:	����Ʒ��
		@return			:	INT
		"""
		try:
			return self._aDatas[grade]["tm_activatItemAmount"]
		except KeyError:
			ERROR_MSG( "Can't find tm_activatItemAmount config by grade(%s)" % grade )
			return 0

	def getRebuildItem( self, grade ):
		"""
		���ݷ���Ʒ����ȡ������������ԭ��
		@type	grade	:	INT8
		@param	grade	:	����Ʒ��
		@return			:	INT
		"""
		try:
			return self._aDatas[grade]["tm_rebuildItem"]
		except KeyError:
			ERROR_MSG( "Can't find tm_rebuildItem config by grade(%s)" % grade )
			return 0

	def getRebuildItemAmount( self, grade ):
		"""
		���ݷ���Ʒ����ȡ������������ԭ������
		@type	grade	:	INT8
		@param	grade	:	����Ʒ��
		@return			:	INT
		"""
		try:
			return self._aDatas[grade]["tm_rebuildItemAmount"]
		except KeyError:
			ERROR_MSG( "Can't find tm_rebuildItemAmount config by grade(%s)" % grade )
			return 0

	def getAcGradeByItemID( self, itemID ):
		"""
		������ƷID��ȡ�����Ʒ��
		"""
		for grade, data in self._aDatas.iteritems():
			tmItemIDs = data.get( "tm_activatItem", [] )
			if itemID in tmItemIDs: return grade
		return None

	def getFlawEffect( self ):
		"""
		��ȡ��������
		"""
		effects = {}
		n = 0
		while n < csconst.EQUIP_EFFECT_FLAW_LIMIT:
			n += 1
			r = random.random()
			for effectID, odds, minValue, maxValue in self._fDatas:
				if r <= odds:
					if effectID in effects:
						n -= 1
					else:
						effects[effectID] = random.uniform( minValue, maxValue )
					break

		return effects

	def reset( self ):
		"""
		���¼��ط�����������
		@return None
		"""
		self._gDatas = {}
		self._tDatas = {}
		self._sDatas = {}
		self._pDatas = {}
		self._eDatas = {}
		self._iDatas = {}
		self.load( )
		reload( TalismanGrade )
		reload( TalismanExtraParam )
		reload( TalismanSkill )
		reload( TalismanPotential )
		self._aDatas = TalismanGrade.Datas		# like as { grade : { "tm_upItem" : itemID, ... }, ... }
		self._gDatas = TalismanExtraParam.server_gDatas		# like as { id : { "tm_odds" : odds, "tm_effectID" : effectID, ... }
		self._tDatas = TalismanExtraParam.server_tDatas		# like as { grade : [tm_id,....] , ... }
		self._sDatas = TalismanSkill.sDatas		# like as { level : odds, ... }
		self._pDatas = TalismanPotential.Datas		# like as { skill_level, potential, ... }
		self._eDatas = TalismanSkill.Datas

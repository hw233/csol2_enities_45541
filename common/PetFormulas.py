# -*- coding: gb18030 -*-
#
# $Id: PetFormulas.py,v 1.34 2008-08-21 09:12:25 huangyongwei Exp $

"""
pet property radix value reader

2007/10/24: writen by huangyongwei
"""

import time
import math
import random
import Math
import Language
import csdefine
import csconst
import csarithmetic
import ShareTexts

from bwdebug import *
from cscollections import MapList
from LevelEXP import RoleLevelEXP
from LevelEXP import PetLevelEXP
from config.pet import armor_radix
from config.pet import magic_armor_radix
from config.pet import PetLevelProperties
from config.pet import PetNimbusExp
from config.pet import PetAbility
from config.pet import PetJoyancyEffectConfig

class PetDatas :
	__hierarchiesMaps = {}
	__hierarchiesMaps[csdefine.PET_HIERARCHY_GROWNUP]	= "grownup"			# ����
	__hierarchiesMaps[csdefine.PET_HIERARCHY_INFANCY1]	= "infancy1"		# һ��
	__hierarchiesMaps[csdefine.PET_HIERARCHY_INFANCY2]	= "infancy2"		# ����

	__typesMaps = {}
	__typesMaps[csdefine.PET_TYPE_STRENGTH]				= "strength"		# ������
	__typesMaps[csdefine.PET_TYPE_SMART]				= "smart"			# ������
	__typesMaps[csdefine.PET_TYPE_INTELLECT]			= "intellect"		# ������
	__typesMaps[csdefine.PET_TYPE_BALANCED]				= "balanced"		# ������

	__stringMapType = {}
	__stringMapType["strength"	]			= csdefine.PET_TYPE_STRENGTH		# ������
	__stringMapType["smart"]				= csdefine.PET_TYPE_SMART			# ������
	__stringMapType["intellect"]				= csdefine.PET_TYPE_INTELLECT	# ������
	__stringMapType["balanced"]				= csdefine.PET_TYPE_BALANCED		# ������

	__sndAttrNames = ["corporeity", 										# ��������
					  "strength", 											# ��������
					  "intellect", 											# ��������
					  "dexterity" ] 										# ��������

	__petGettingMap = {}
	__petGettingMap[csdefine.PET_GET_CATCH]						= "normalCatch"			# һ�㲶������׽
	__petGettingMap[csdefine.PET_GET_SUPER_CATCH]				= "suCatch"				# ���ܲ�������׽
	__petGettingMap[csdefine.PET_GET_CATHOLICON]				= "catholicon"			# ��ͯ��
	__petGettingMap[csdefine.PET_GET_PROPAGATE]					= "propagate"			# ��ֳ
	__petGettingMap[csdefine.PET_GET_SUPER_CATHOLICON]			= "suCatholicon"		# ������ͯ��
	__petGettingMap[csdefine.PET_GET_RARE_CATHOLICON]			= "rearCatholicon"		# ��ϡ��ͯ��
	__petGettingMap[csdefine.PET_GET_SUPER_RARE_CATHOLICON]		= "suRearCatholicon"	# ������ϡ��ͯ��


	def __init__( self ) :
		self.__fixedECounts = {}								# { ������� : { "corporeity" : ����ֵ, "strength" : ����ֵ, "intellect" : ����ֵ, "dexterity" : ����ֵ } }
		self.__armorRadies = armor_radix.Datas					# �����������ֵ��{ ������� : { ����ȼ� : ������ } }
		self.__magicArmorRadies = magic_armor_radix.Datas		# ���﷨����������ֵ��{ ������� : { ����ȼ� : ������ } }

		self.__levelProperties = PetLevelProperties.Datas		# { ( ���Ｖ��, ������� ) : { ����1:����ֵ1, ... }, ... }������Ĳ�ͬ���ͺͼ����Ӧ��ͬ������ֵ
		self.__nimbusLevelProperties = {}						# { ( ������ֵ����, ������� ) : { ����1:����ֵ1, ... }, ... }�����ﲻͬ����ֵ�����Ӧ��ͬ������ֵ
		self.__nimbusLevelExp = PetNimbusExp.Datas				# { ������ֵ����:�������ֵ, ... }�����ﲻͬ��ֵ�����Ӧ�ĸ���ֵ

		# { key1:{ �ɳ���:����}, key2:{ �ɳ���:����}, ... }��keyΪ����Ϊ7���ַ������ɴ˳ɳ��ȶ�Ӧ�ĳ������͡����ݡ���÷�ʽ��Я���ȼ���϶���
		# ��һλΪӡ�ǣ��ڶ�λΪ���ݣ���������λΪ
		self.__abilityData = PetAbility.Datas

		self.__joyancyData = PetJoyancyEffectConfig.Datas

		self.__loadFixedEnhanceCounts( )
		self.__loadNimbusLevelProperties( )
	# ----------------------------------------------------------------
	def getLevelProperties( self, level, petType ):
		"""
		��ü�������Ͷ�Ӧ������ֵ
		"""
		try:
			return self.__levelProperties[ ( level, petType ) ]
		except KeyError:
			ERROR_MSG( "level( %i ),petType( %i ) is not exist." % ( level, petType ) )
			return None

	def getNimbusLevelProperties( self, nimbusLevel, petType ):
		"""
		�����ֵ��������Ͷ�Ӧ������ֵ
		"""
		try:
			return self.__nimbusLevelProperties[ ( nimbusLevel, petType ) ]
		except KeyError:
			ERROR_MSG( "level( %i ),petType( %i ) is not exist." % ( nimbusLevel, petType ) )
			return None

	def getCalcaneusMax( self, nimbus ):
		"""
		������Լ����Ӧ��������ֵ
		"""
		try:
			return self.__nimbusLevelExp[ nimbus ]
		except KeyError:
			ERROR_MSG( "û�ж�Ӧ���Լ���( %i )�ĸ���ֵ��" % nimbus )
			return 0

	def getAbility( self, key ):
		"""
		���ݳ����Я���ȼ������ݡ���ȡ���͡�ӡ�� ��ó���ĳɳ���
		"""
		try:
			abilityList = self.__abilityData[key]
		except KeyError:
			ERROR_MSG( "��Ӧ�ɳ��Ȳ����ڣ�Key:%s." % key )
			return 0

		rate = random.random()
		for ability, abilityRate in abilityList:
			if rate > abilityRate:
				continue
			return ability

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __loadFixedEnhanceCounts( self ) :
		"""
		���ظ������ǿ��ʱ���������Եļ�ֵ
		"""
		sect = Language.openConfigSection( "config/pet/fixed_enhance_count.xml" )
		for hierachy, strHierachy in self.__hierarchiesMaps.iteritems() :
			for ptype, strType in self.__typesMaps.iteritems() :
				species = hierachy | ptype
				tag = "%s_%s" % ( strHierachy, strType )
				subSect = sect[tag]
				props = {}
				for propName in self.__sndAttrNames :
					props[propName] = subSect.readFloat( propName )
				self.__fixedECounts[species] = props

	def __loadNimbusLevelProperties( self ):
		"""
		���ز�ͬ������ֵ��������Ͷ�Ӧ������ֵ����
		"""
		section = Language.openConfigSection( "config/pet/PetNimbusLevelProperties.xml" )
		for subSection in section.values():
			nimbuslevel = subSection.readInt( "nimbusLevel" )
			petType = self.__stringMapType[ subSection.readString( "petType" ) ]
			corporeity = subSection.readFloat( "corporeity" )
			intellect = subSection.readFloat( "intellect" )
			strength = subSection.readFloat( "strength" )
			dexterity = subSection.readFloat( "dexterity" )
			if not self.__levelProperties.has_key( ( nimbuslevel, petType ) ):
				self.__nimbusLevelProperties[ ( nimbuslevel, petType ) ] = {}
			self.__nimbusLevelProperties[ ( nimbuslevel, petType ) ] = { "corporeity":corporeity, "intellect":intellect, "strength":strength, "dexterity":dexterity }

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getSndAttrRadix( self, petType, level, nimbus, attrName ) :
		"""
		��ȡ��������ֵ
		"""
		levelProperties = self.getLevelProperties( level, petType )
		nimbusProperties = self.getNimbusLevelProperties( nimbus, petType )
		try:
			return levelProperties[attrName] + nimbusProperties[attrName]
		except:
			return 0

	def getFixedEnhanceCount( self, species, propName, level ) :
		"""
		��ȡ���ȼ���ǿ���������ֵ
		@type				species	 : MACRO DEFINATION
		@param				species	 : defined in csdefine.py
		@type				propName : str
		@param				propName : property's name
		@type				level	 : int
		@param				level	 : the pet's level
		@rtype						 : int
		@return						 : the number of enhance time
		"""
		radix = self.__fixedECounts[species][propName]
		return int( round( radix * level ) )

	def getPhysicsArmorRadies( self, petType, level, ability ):
		"""
		���ݳ������ͺͼ����������������ֵ
		"""
		return self.__armorRadies[ self.__typesMaps[ petType ] ][ level ] * ability * 0.01

	def getMagicArmorRadies( self, petType, level, ability ):
		"""
		���ݳ������ͺͼ����÷�����������ֵ
		"""
		return self.__magicArmorRadies[ self.__typesMaps[ petType ] ][ level ] * ability * 0.01

	def getJoyancyEffect( self, joyancy ):
		"""
		���ݳ�����ֶȻ�ȡӰ���������ֵ
		"""
		return self.__joyancyData.get( joyancy, 0.0 )

# --------------------------------------------------------------------
# implement formula class
# --------------------------------------------------------------------
class Formulas :
	__inst = None

	def __init__( self ) :
		assert Formulas.__inst is None
		self.__petDatas = PetDatas()

		self.__trainRadix = {}				# ����ʱ����õľ���ֵ��ȼ���ϵ�Ļ���

		self.__hitSpecRadix = {}			# �����������������������㹥����ʱ�õ���
		self.__hitSpeeds = {}				# ��ͬ���ͳ���Ĺ����ٶ�
		self.__flipDPS = {}					# ��ͬ������� dps ����ֵ

		self.__magicHitRadix = {}			# ������������������

		# ----------------------------------
		self.__doubleRadies = {}			# �����ʻ���������
		self.__doubleMaters = {}			# �����ʵ���

		self.__magicDoubleRadies = {}		# ����������
		self.__magicDoubleMaters = {}		# ���������ʵ���

		self.__dodgeRadies = {}				# �����ʻ�������
		self.__dodgeMaters = {}				# �����ʵ���

		self.__resistRadies = {}			# �м��ʻ�����
		self.__resistMaters = {}			# �м��ʵ���

		self.__aboutDexterityParam = {}
		self.__aboutIntellectParam = {}
		self.__aboutStrengthParam = {}

		self.__enhanceValue_Free = None
		self.__enhanceValue_Commmon = {}
		self.initialize( )


	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = Formulas()
		return SELF.__inst


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def initialize( self ) :
		"""
		��ʼ�����﹫ʽ����ֵ
		"""
		# -----------------------------------
		# ��ʼ�����������õľ���ֵ�ȼ�����
		# -----------------------------------
		tmpRadix = [ 3.1, 7.4, 11.5, 15.2, 18.2, 20.8, 22.9, 24.6, 25.8, 27, 28, 28.8, 29.4, 29.9, 30.3 ]
		for level in xrange( RoleLevelEXP.getMaxLevel() + 1 ):
			self.__trainRadix[ level ] = tmpRadix[ int( ( level - 1 ) / 10 ) ]

		# -----------------------------------
		# ��ʼ�����������
		# -----------------------------------
		self.__hitSpecRadix[csdefine.PET_HIERARCHY_GROWNUP]		= 1.0
		self.__hitSpecRadix[csdefine.PET_HIERARCHY_INFANCY1]	= 1.0
		self.__hitSpecRadix[csdefine.PET_HIERARCHY_INFANCY2]	= 1.0

		# -----------------------------------
		# ��ʼ�����﹥���ٶ�
		# -----------------------------------
		self.__hitSpeeds[csdefine.PET_TYPE_STRENGTH]	= 1.0
		self.__hitSpeeds[csdefine.PET_TYPE_BALANCED]	= 1.0
		self.__hitSpeeds[csdefine.PET_TYPE_SMART]		= 1.0
		self.__hitSpeeds[csdefine.PET_TYPE_INTELLECT]	= 1.0

		# -----------------------------------
		# ��ʼ���������� DPS ����
		# -----------------------------------
		self.__flipDPS[csdefine.PET_TYPE_STRENGTH]	= 0.15
		self.__flipDPS[csdefine.PET_TYPE_BALANCED]	= 0.15
		self.__flipDPS[csdefine.PET_TYPE_SMART]		= 0.15
		self.__flipDPS[csdefine.PET_TYPE_INTELLECT]	= 0.15

		# -----------------------------------
		# ��ʼ�����﷨����������
		# -----------------------------------
		self.__magicHitRadix[csdefine.PET_TYPE_STRENGTH]	= 0.02
		self.__magicHitRadix[csdefine.PET_TYPE_BALANCED]	= 0.02
		self.__magicHitRadix[csdefine.PET_TYPE_SMART]		= 0.02
		self.__magicHitRadix[csdefine.PET_TYPE_INTELLECT]	= 0.0213

		# -----------------------------------
		# ��ʼ�������������ʡ����������ʡ������ʡ��м��ʼ��㹫ʽ������9:14 2009-3-5,wsf
		# -----------------------------------
		# �й�����
		self.__aboutDexterityParam[ csdefine.PET_TYPE_STRENGTH ] = ( 0.01, 15, [ 2.2, 3, 4, 4.8, 8.2 ] )
		self.__aboutDexterityParam[ csdefine.PET_TYPE_BALANCED ] = ( 0.01, 22.5, [ 3.2, 4.5, 6, 7.3, 12.3 ] )
		self.__aboutDexterityParam[ csdefine.PET_TYPE_INTELLECT ] = ( 0.01, 15, [ 2.1, 3, 4, 4.8, 8.2 ] )
		self.__aboutDexterityParam[ csdefine.PET_TYPE_SMART ] = ( 0.01, 37.5, [ 5.4, 7.5, 10, 12, 20.3 ] )
		# �й�����
		self.__aboutIntellectParam[ csdefine.PET_TYPE_STRENGTH ] = ( 0.01, 7.5, [ 1.1, 1.5, 2, 2.4, 4.1 ] )
		self.__aboutIntellectParam[ csdefine.PET_TYPE_BALANCED ] = ( 0.01, 22.5, [ 3.3, 4.5, 6, 7.2, 12.2 ] )
		self.__aboutIntellectParam[ csdefine.PET_TYPE_INTELLECT ] = ( 0.01, 52.5, [ 7.6, 10.5, 14, 16.9, 28.6 ] )
		self.__aboutIntellectParam[ csdefine.PET_TYPE_SMART ] = ( 0.01, 7.5, [ 1.1, 1.5, 2, 2.4, 4.1 ] )
		# �й�����
		self.__aboutStrengthParam[ csdefine.PET_TYPE_STRENGTH ] = ( 0.01, 30, [ 4.3, 6, 8, 9.7, 16.3 ] )
		self.__aboutStrengthParam[ csdefine.PET_TYPE_BALANCED ] = ( 0.01, 22.5, [ 3.25, 4.5, 6, 7.3, 12.3 ] )
		self.__aboutStrengthParam[ csdefine.PET_TYPE_INTELLECT ] = ( 0.01, 7.5, [ 1.1, 1.5, 2, 2.4, 4.1 ] )
		self.__aboutStrengthParam[ csdefine.PET_TYPE_SMART ] = ( 0.01, 22.5, [ 3.2, 4.5, 6, 7.3, 12.3 ] )

		#ǿ������/�һ�����
		self.__enhanceValue_Commmon = {
		csdefine.PET_TYPE_STRENGTH:{"strength":(9.354,0.338),"corporeity":(10.458,0.378),"dexterity":(4.667,0.169),"intellect":(4.667,0.169)},
		csdefine.PET_TYPE_BALANCED:{"strength":(7.308,0.264),"corporeity":(7.308,0.264),"dexterity":(7.308,0.264),"intellect":(7.308,0.264)},
		csdefine.PET_TYPE_SMART:{"strength":(6.948,0.251),"corporeity":(6.078,0.220),"dexterity":(11.580,0.418),"intellect":(4.632,0.167)},
		csdefine.PET_TYPE_INTELLECT:{"strength":(5.032,0.182),"corporeity":(4.113,0.149),"dexterity":(5.032,0.182),"intellect":(15.096,0.545)}}
		self.__enhanceValue_Free = ( 16.251, 0.587 )
	# -------------------------------------------------
	@staticmethod
	def secondToStrTime( seconds ) :
		"""
		����ת��Ϊ��XX Сʱ XX ����
		@type				seconds : INT64
		@param				seconds : time specifies in second
		@rtype						: str
		@return						: time in hour and minute
		"""
		seconds = int( seconds )
		hours = seconds / 3600
		minutes = ( seconds % 3600 ) / 60
		strHours = strMinutes = ""
		if hours > 0 :
			return "%d %s" % ( hours, ShareTexts.CHTIME_HOUR )
		if minutes > 0 :
			return "%d %s" % ( minutes, ShareTexts.CHTIME_MINUTE )
		return strHours + strMinutes


	# -------------------------------------------------
	# ֱ�Ӵ� PetDatas �л�ȡ���ݵķ�������ʵ petData Ӧ�ø� formula �ϲ���һ��ģ���Ƶ�ʱ��û�п����ܵ��������������֮�٣�
	# -------------------------------------------------
	def getSndProperties( self, species, level, nimbusLevel ):
		"""
		��ȡ��������Ͷ�Ӧ������ֵ
		"""
		petType = self.getType( species )
		propDict = {}
		propDict1 = self.__petDatas.getLevelProperties( level, petType )
		propDict2 = self.__petDatas.getNimbusLevelProperties( nimbusLevel, petType )
		propDict["corporeity"] = propDict1["corporeity"] + propDict2["corporeity"]
		propDict["strength"] = propDict1["strength"] + propDict2["strength"]
		propDict["intellect"] = propDict1["intellect"] + propDict2["intellect"]
		propDict["dexterity"] = propDict1["dexterity"] + propDict2["dexterity"]
		return propDict

	def getAbility( self, takeLevel, hierarchy, catchType, stamp ):
		"""
		���ݳ����Я���ȼ������ݡ���ȡ���͡�ӡ�� ��ó���ĳɳ���
		"""
		return self.__petDatas.getAbility( self.getAbilityKey( takeLevel, hierarchy, catchType, stamp ) )

	def getStamp( self, catchType ):
		"""
		���ݳ���Ļ�÷�ʽ�õ������ӡ��
		ϵͳ��csdefine.PET_STAMP_SYSTEM����д��csdefine.PET_STAMP_MANUSCRIPT
		Ŀǰֻ�е������������д���ҳ���ӡ�ǵ�һ�����ɺ�Ͳ��ٱ仯��
		"""
		if catchType in [ csdefine.PET_GET_EGG1, csdefine.PET_GET_EGG2, csdefine.PET_GET_EGG3 ]:
			return csdefine.PET_STAMP_MANUSCRIPT
		else:
			return csdefine.PET_STAMP_SYSTEM

	def getAbilityKey( self, takeLevel, hierarchy, catchType, stamp ):
		"""
		���ݳ����Я���ȼ������ݡ���ȡ���͡�ӡ�� ������Ӧ�ĳɳ��ȹؼ����ַ���

		����ַ����������ǣ�
			��һ���ַ���ʾ��������ͣ���д����ϵͳ����
			�ڶ����ַ���ʾ����ı��ݣ���������λ��ʾ������������ͣ�
			�����λ��ʾ�����Я���ȼ���
		"""
		sCatchType = str( catchType )
		while len( sCatchType ) < 2:	# ����2λ��ǰ�ò�0
			sCatchType = "0" + sCatchType
		sTakeLevel = str( takeLevel )
		while len( sTakeLevel ) < 3:	# ����3λ��ǰ�ò�0
			sTakeLevel = "0" + sTakeLevel

		return str( stamp ) + str( hierarchy ) + sCatchType + sTakeLevel

	def getSndAttrRadix( self, species, level, nimbus, attrName ) :
		"""
		��ȡ�������Ի�ֵ
		@ptype				species  : MACRO DEFINATION
		@param				species  : defined in csdefined
		@ptype				ptype    : MACRO DEFINATION
		@param				ptype	 : defined in csdefined
		@ptype				level	 : INT8
		@param				level	 : level of the pet
		@ptype				attrName : str
		@param				attrName : property name: ( corporeity, catholicon, rareCatholicon, propagate )
		@rtype						 : int
		@return						 : property values
		"""
		petType = self.getType( species )
		return self.__petDatas.getSndAttrRadix( petType, level, nimbus, attrName )

	def getFixedEnhanceCount( self, species, propName, level ) :
		"""
		��ȡǿ��ʱ����ֵ
		@type				species	 : MACRO DEFINATION
		@param				species	 : defined in csdefine.py
		@type				propName : str
		@param				propName : property's name
		@type				level	 : int
		@param				level	 : the pet's level
		@rtype						 : int
		@return						 : the number of enhance time
		"""
		return self.__petDatas.getFixedEnhanceCount( species, propName, level )

	def getPhysicsArmorRadies( self, species, level, ability ):
		"""
		���ݳ������ͺͼ����������������ֵ
		"""
		ptype = self.getType( species )
		return self.__petDatas.getPhysicsArmorRadies( ptype, level, ability )

	def getMagicArmorRadies( self, species, level, ability ):
		"""
		���ݳ������ͺͼ����÷�����������ֵ
		"""
		ptype = self.getType( species )
		return self.__petDatas.getMagicArmorRadies( ptype, level, ability )


	# -------------------------------------------------
	# �����ʼ���Ļ�������ֵ�Ļ�ȡ
	# -------------------------------------------------
	@staticmethod
	def getKeepingCount( reinBibleCount ) :
		"""
		��ȡ��Я�������������
		@type		reinBibleCount : int
		@param		reinBibleCount : the number of rein bible
		@rtype					   : int
		@return					   : the number of pet can be keep
		"""
		return 3 + reinBibleCount

	def getSndAttrValue( self, attrName, species, level, nimbus ) :
		"""
		��ȡ��������ֵ
		@type				attrName : str
		@param				attrName : secondary attribute name
		@type				species	 : hierarchy combine with type of the pet
		@param				species	 : UINT8
		@type				level	 : int
		@param				level	 : level of the pet
		@rtype						 : int
		@return						 : second attribute value
		"""
		return self.getSndAttrRadix( species, level, nimbus, attrName )

	@staticmethod
	def getCharacter() :
		"""
		���ȡ�ó�����Ը�
		@rtype					: MACRO DEFINATION
		@rettun					: csdeine.PET_CHARACTER_SUREFOOTED
										  PET_CHARACTER_CLOVER
										  PET_CHARACTER_CANNILY
										  PET_CHARACTER_BRAVE
										  PET_CHARACTER_LIVELY
		"""
		charas = [csdefine.PET_CHARACTER_SUREFOOTED,
				  csdefine.PET_CHARACTER_CLOVER,
				  csdefine.PET_CHARACTER_CANNILY,
				  csdefine.PET_CHARACTER_BRAVE,
				  csdefine.PET_CHARACTER_LIVELY]
		count = len( charas )
		return csarithmetic.getRandomElement( charas, count * [1] )


	# -------------------------------------------------
	# ����������ĵļ���
	# -------------------------------------------------
	@staticmethod
	def getTickLifeDecreasement( hierarchy ) :
		"""
		��ȡ������ʱ����ۼ�ֵ
		@type			hierarchy : MACRO DEFINATION
		@param			hierarchy : defined in csdefine.py
		@rtype					  : int
		@return					  : wastage
		"""
		if hierarchy == csdefine.PET_HIERARCHY_GROWNUP :
			return 20
		elif hierarchy == csdefine.PET_HIERARCHY_INFANCY1 :
			return 25
		return 30

	@staticmethod
	def getLostBellLifeDecreasement() :
		"""
		��ȡ����ս��ʱ���������ۼ�ֵ
		@rtype					: int
		@return					: value
		"""
		return 300

	# ---------------------------------------
	@staticmethod
	def getConjureJoyancyLimit() :
		"""
		��ȡ�����������С���ֶ�
		@rtype					: int
		return					: joyancy value
		"""
		return 50

	@staticmethod
	def getTickJoyancyDecreasement() :
		"""
		get joyancy wastage in each time segment
		@rtype					  : int
		@return					  : wastage
		"""
		return 2

	@staticmethod
	def getLostBellJoyancyDecreasement() :
		"""
		��ȡ����ս��ʱ�����ֶȵ��ۼ�ֵ
		@rtype					: int
		@return					: value
		"""
		return 10

	@staticmethod
	def getTradeJoyancyDecreasement() :
		"""
		��ȡ����ʱ�������ۼ�
		@rtype					: int
		@return					: value
		"""
		return 60


	# ---------------------------------------
	# ��׽�����õ��Ĺ�ʽ
	# ---------------------------------------
	@staticmethod
	def getCatchedPetHierarchy( catchType ) :
		"""
		��׽����ʱ�����ȡ����ı���
		"""
		if catchType == csdefine.PET_GET_EGG3:
			return csdefine.PET_HIERARCHY_INFANCY2
		elif catchType == csdefine.PET_GET_EGG2:
			return csdefine.PET_HIERARCHY_INFANCY1
		elif catchType == csdefine.PET_GET_EGG1:
			return csdefine.PET_HIERARCHY_GROWNUP

		hierarchies = [csdefine.PET_HIERARCHY_GROWNUP, csdefine.PET_HIERARCHY_INFANCY1]
		return csarithmetic.getRandomElement( hierarchies, [97, 3] )


	# ---------------------------------------
	# �ϳɳ����õ��Ĺ�ʽ
	# ---------------------------------------
	@staticmethod
	def getCombinePetCost() :
		"""
		��ȡ�ܳɳ���ʱ����Ҫ�Ľ�Ǯ����
		@rtype					: int
		@return					: cost
		"""
		return 2000

	# ---------------------------------------
	# ��ֳ�����õ��Ĺ�ʽ
	# ---------------------------------------
	@staticmethod
	def getProcreatePetCost() :
		"""
		��ȡ��ֳ����ʱ��Ҫ�Ļ���
		@rtype					: int
		@return					: cost
		"""
		return 100000

	@staticmethod
	def getProcreateTime() :
		"""
		��ȡ��ֳʱ�䣬�̶�Ϊcsconst.PET_PROCREATE_NEED_TIME
		"""
		return csconst.PET_PROCREATE_NEED_TIME

	@staticmethod
	def getProcreateLifeDecreasement() :
		"""
		��ȡ��ֳʱ������������ۼ�
		@rtype					: int
		@return					: life descreasement
		"""
		return csconst.PET_PROCREATE_LIFT_NEED


	# ---------------------------------------
	# �����õ��Ĺ�ʽ
	# ---------------------------------------
	@staticmethod
	def getCommonGemActicateCost() :
		"""
		��ȡ������ͨ��ʯ��Ҫ�Ļ���
		@rtype						: int
		@return						: cost
		"""
		return csconst.GEM_HIRE_PAY

	@staticmethod
	def getTrainGemActivateCost() :
		"""
		��ȡ���������ʯ��Ҫ�Ļ���
		@rtype						: int
		@return						: cost
		"""
		return 1000

	@staticmethod
	def getTrainTime( points ) :
		"""
		��ȡ����ʱ��
		@type				points : int
		@param				points : point in game
		@rtype					   : int
		@return					   : time specifies with second
		"""
		return points * 180							# 1 hour equals to 20 points

	@staticmethod
	def getTrainPoints( ttime ) :
		"""
		ͨ������ʱ���ȡ������
		@type				ttime : INT64
		@pararm				ttime : train time
		@rtype					  : int
		@return					  : count of the points
		"""
		return int( ttime * 20 / 3600.0 )

	def getTrainEXP( self, ownerLevel, trainType, duration ) :
		"""
		��ȡ������õ��ľ���ֵ
		@type			ownerLevel : UINT8
		@param			ownerLevel : level of the pet's owner
		@type			trainType  : MACRO DEFINATION
		@param			trainType  : the pet's train type defined in csdefine.py
		@type			duration   : int
		@param			duration   : how long the training persisting( specified by seconds )
		@rytpe					   : int
		@return					   : gained exp value
		"""
		minutes = duration / 60.0
		radix = self.__trainRadix[ ownerLevel ]
		expMin = int( round( radix * minutes * ( 1 - 0.1 ) ) )
		expMax = int( round( radix * minutes * ( 1 + 0.1 ) ) )
		exp = random.randint( expMin, expMax )

		if trainType == csdefine.PET_TRAIN_TYPE_HARD:
			exp *= 1.7

		return int( round( exp ) )

	@staticmethod
	def getAbsorbExpUpper( level ) :	# wsf add,11:14 2008-7-31
		"""
		�ɳ���ȼ���ó��ﵱ���ܹ�ι���ľ���ֵ����
		@type				level : UINT16
		@pararm				level : ���Ｖ��
		@rtype					  : int
		@return					  : count of the points
		"""
		return int( PetLevelEXP.getEXPMax( level ) * 1.3 )


	# ---------------------------------------
	# ����ֿ��õ��Ĺ�ʽ
	# ---------------------------------------
	@staticmethod
	def getStorageCost( stype, times ) :
		"""
		��ȡ�Ĵ��������Ҫ�Ļ���
		@type				stype : MACRO DEFINATION
		@param				stype : storage type defined in csdefine.py
		@rtype					  : UINT32
		@return					  : gold cost
		"""
		costs = {}
		costs[csdefine.PET_STORE_TYPE_LARGE] = 200
		costs[csdefine.PET_STORE_TYPE_SMALL] = 100
		return costs[stype]*times


	# ---------------------------------------
	# ����ǿ���õ��Ĺ�ʽ
	# ---------------------------------------
	@staticmethod
	def getFreeEnhanceCount( level ) :
		"""
		��ȡָ���ȼ�������ǿ�����ܴ�������ǰ�ȼ��£�����ǿ�����������˴�����������ʹ������ǿ����
		@type				level : UINT8
		@param				level : the pet's level
		@rtyle					  : int
		@return					  : enahnce times
		"""
		return int( round( level * 0.587 ) )

	@staticmethod
	def getEnhanceEffect( isCurse ) :
		"""
		��ȡǿ��Ч��
		@type				isCurse		 : bool
		@param				isCurse		 : whether use curse item
		"""
		if isCurse == True : return 5
		return csarithmetic.getRandomElement( [3, 4, 5], [4, 4, 2] )


	def getEnhanceValue( self, species, etype, attrName, count ):
		ptype = self.getType( species )
		if etype == csdefine.PET_ENHANCE_FREE:												# ���������ǿ��
			attrParam  = self.__enhanceValue_Free[0]
			transParam = self.__enhanceValue_Free[1]
		else:
			attrParam  = self.__enhanceValue_Commmon[ptype][attrName][0]
			transParam = self.__enhanceValue_Commmon[ptype][attrName][1]
		maxValue = max( int( attrParam * 1.5 ** ( 0.1 * count / transParam - 1.0 ) - attrParam * 1.5 ** ( 0.1 * ( count - 1 ) / transParam - 1.0 ) ), 5 )
		minValue = int( maxValue * 0.8 )
		return ( minValue , maxValue )

	# -------------------------------------------------
	# ���ڳ��������жϵĹ�ʽ�ͷ���
	# -------------------------------------------------
	@staticmethod
	def getHierarchy( species ) :
		"""
		��ȡ���ﱲ��
		@type			species : MACRO DEFINATION
		@param			species : defined in csdefine.py
		@rtype					: MACRO DEFINATION
		@return					: hierarchy
		"""
		return species & csdefine.PET_HIERARCHY_MASK

	@staticmethod
	def getRejuvenesceHierarchy( hierarchy ):
		"""
		��ȡ���ﻹͯ��ı���

		@type hierarchy :	INT16
		@param hierarchy :	��ͯǰ�ı���
		@rtype:	INT16
		@return:	��ͯ��ı���
		"""
		if hierarchy == csdefine.PET_HIERARCHY_GROWNUP:
			hierarchy = csdefine.PET_HIERARCHY_INFANCY1
		return hierarchy

	@staticmethod
	def getType( species ) :
		"""
		��ȡ�������
		@type			species : MACRO DEFINATION
		@param			species : defined in csdefine.py
		@rtype					: MACRO DEFINATION
		@return					: type
		"""
		return species & csdefine.PET_TYPE_MASK

	@staticmethod
	def isHierarchy( species, hierarchy ) :
		"""
		�ж�ĳ�����Ƿ�ʱָ���ı���
		@type			species : MACRO DEFINATION
		@param			species : defined in csdefine.py
		@param					: hierarchy
		@rtype					: bool
		@return					: if it is hierarchy return true
		"""
		return Formulas.getHierarchy( species ) == hierarchy

	@staticmethod
	def isType( species, ptype ) :
		"""
		�ж������Ƿ���ָ��������
		@type			species : MACRO DEFINATION
		@param			species : defined in csdefine.py
		@type					: MACRO DEFINATION
		@param					: type
		@rtype					: bool
		@return					: if it is ptype return true
		"""
		return Formulas.getType( species ) == ptype


	# -------------------------------------------------
	# ���ڳ�����ֵ�Ĺ�ʽ
	# -------------------------------------------------
	@staticmethod
	def getMaxNimbus( level ) :
		"""
		��ȡ���ﵱǰ�ȼ��µ�������󼶱�
		@ptype			hierarchy	: MACRO DEFINATION
		@param			hierarchy	: defined in csdefined
		@type			level		: UINT8
		@param			level		: the pet's level
		@rtype						: nimbus upper limit
		"""
		return level / 3

	def abilityToCalcaneus( self, ability ):
		"""
		�ɳ���ת��Ϊ����ֵ

		@param ability : �ɳ���
		@type ability : INT32
		"""
		return ability * 100

	def calcaneusToNimbus( self, maxNimbus, currNimbus, calcaneus ) :
		"""
		������ת��Ϊ��ֵ�ȼ�
		@type			maxNimbus	: UINT8
		@param			maxNimbus	: nimbus's upper limit
		@type			currNimbus	: UINT8
		@param			currNimbus	: cureent nimbus
		@type			calcaneus	: INT32
		@param			calcaneus	: calcaneus
		@rtype						: tuple
		@return						: ( nimbus, remainder calcaneus )
		"""
		while calcaneus > 0 :
			if currNimbus >= maxNimbus :
				return ( currNimbus, 0 )
			nextCalcaneus = formulas.getCalcaneusMax( currNimbus )
			leaveCalcaneus = calcaneus - nextCalcaneus
			if leaveCalcaneus >= 0 :
				calcaneus = leaveCalcaneus
				currNimbus += 1
			if leaveCalcaneus <= 0 :
				break
		return ( currNimbus, calcaneus )

	def getCalcaneusMax( self, nimbus ) :
		"""
		��ȡ��ǰ����ֵ�ȼ��µĸ������ֵ�������ǳ�����ֵ����ֵ�ȼ���һ����
		@type			nimbus : UINT8
		@param			nimbus : nimbus
		@rtype				   : INT32
		@return				   : calcaneus value
		"""
		return self.__petDatas.getCalcaneusMax( nimbus )

	# -------------------------------------------------
	# ������ֶȹ�ʽ
	# -------------------------------------------------
	def getJoyancyEffect( self, joyancy ) :
		"""
		��ȡ���ֶȶԳ�������ͷ�����������Ӱ��
		@type				joyancy : UINT8
		@param				joyancy : current joyancy value
		@rtype						: float
		@return						: effect
		"""
		return self.__petDatas.getJoyancyEffect( joyancy )

	# -------------------------------------------------
	# ����ս�����Լ��㹫ʽ
	# -------------------------------------------------
	@staticmethod
	def getBaseHPMax( corporeity, ability, level ):
		"""
		��ȡHP���ֵ����ֵ

		@type				corporeity  : int
		@param				corporeity  : ��������
		@type				ability : int
		@param				ability : ����ɳ���

		����*10 + �ɳ���* 8.4 * 1.5 ** ( 0.1 * level - 1 )
		"""
		return corporeity * 10 + ability * 8.4 * 1.5 ** ( 0.1 * level - 1 )

	@staticmethod
	def getBaseMPMax( intellect, ability, level ):
		"""
		��ȡMP���ֵ����ֵ

		@type				corporeity  : int
		@param				corporeity  : ��������
		@type				ability : int
		@param				ability : ����ɳ���

		����*10 + �ɳ���* 8.4 * 1.5 ** ( 0.1 * level - 1 )
		"""
		return intellect * 10 + ability * 8.4 * 1.5 ** ( 0.1 * level - 1 )

	@staticmethod
	def getBasePhysicsDPS( species, ability, strength, dexterity, level ) :
		"""
		��ȡ�������� DPS
		@type				species	  : MSCRO DEFINATION
		@param				species	  : ��������
		@type				strength  : int
		@param				strength  : ��������
		@type				dexterity : int
		@param				dexterity : ��������

		�����ͣ�սʿ��
		��������DPS������ֵ��=�ɳ���*����*0.025 + 20*1.5^(0.1*lv - 1)
		ƽ���ͣ����ͣ�
		��������dps������ֵ��=�ɳ���*������*0.02+����*0.02�� + 25*1.5^(0.1*lv - 1)
		�����ͣ����֣�
		��������dps������ֵ��=�ɳ���* (���� * 0.01 + ���� * 0.02) + 25.75 * 1.5 ^ (0.1 * Lv - 1)
							  �ɳ���*������*0.0024+����*0.02��+ 21.25*1.5^(0.1*lv - 1)
		�����ͣ���ʦ��
		��������dps������ֵ��=�ɳ��� *����*0.02 +  20*1.5^(0.1*lv - 1)
		"""
		ptype = Formulas.getType( species )
		if ptype == csdefine.PET_TYPE_STRENGTH:
			return ability * strength * 0.025 + 20 * 1.5 ** ( 0.1 * level - 1 )
		elif ptype == csdefine.PET_TYPE_BALANCED:
			return ability *  0.02 * ( strength  + dexterity  ) + 25 * 1.5 ** ( 0.1 * level - 1 )
		elif ptype == csdefine.PET_TYPE_SMART:
			return ability * ( strength * 0.01 + dexterity * 0.02 ) + 25.75 * 1.5 ** ( 0.1 * level - 1 )
		elif ptype == csdefine.PET_TYPE_INTELLECT:
			return ability * strength * 0.02 + 20 * 1.5 ** ( 0.1 * level - 1 )
		raise "pet type %i is not exist!" % ptype

	# ---------------------------------------
	def getHitSpeed( self, species ) :
		"""
		��ȡ���������ٶ�
		@type				species : MSCRO DEFINATION
		@param				species : ��������
		"""
		return self.__hitSpeeds[self.getType( species )]

	def getMinDamage( self, species, dps ) :
		"""
		��ȡ������С��������
		@type				species : MSCRO DEFINATION
		@param				species : ��������
		@type				dps		: int
		@param				dps		: ���� dps

		������������������ֵ��= dps*�����ٶ�
		�ó�������������ֵ��֮���ڹ���Ŀ���ʱ��
		��С������=������*��1-dps������
		��󹥻���=������*��1+dps������
		"""
		ptype = self.getType( species )
		baseDamage = dps * self.__hitSpeeds[ptype]	# ��������
		return baseDamage * ( 1 - self.__flipDPS[ptype] )

	def getMaxDamage( self, species, dps ) :
		"""
		��ȡ���������������
		@type				species : MSCRO DEFINATION
		@param				species : ��������
		@type				dps		: int
		@param				dps		: ���� dps
		"""
		ptype = self.getType( species )
		baseDamage = dps * self.__hitSpeeds[ptype]	# ��������
		return baseDamage * ( 1 + self.__flipDPS[ptype] )

	def getMagicDamage( self, ability, species, intellect, level ) :
		"""
		��ȡ��������������

		������
		���﷨��������������ֵ��=�ɳ���*����*0.0213 + 27.5 * 1.5 ** ( 0.1 * level - 1 )
		�����͡������͡�������
		���﷨��������������ֵ��=�ɳ���*����*0.02 + 20 * 1.5 ** ( 0.1 * level - 1 )
		"""
		ptype = self.getType( species )
		if ptype == csdefine.PET_TYPE_INTELLECT:
			return ability * intellect  * self.__magicHitRadix[ptype] +  27.5 * 1.5 ** ( 0.1 * level - 1 )
		else:
			return ability * intellect  * self.__magicHitRadix[ptype] +  20 * 1.5 ** ( 0.1 * level - 1 )

	# ---------------------------------------
	@staticmethod
	def __getLevelSeg( lv ) :
		"""
		��ȡ�ȼ��ֶ�( �� 0 ��ʼ )
		@type					lv : int
		@param					lv : ����ȼ�
		@rtype					   : int
		@return					   : �ȼ������ĵȼ���
		"""
		return ( lv - 1 ) / 30

	@staticmethod
	def __getlevelBaseValue( lv ) :
		"""
		��ȡ�ȼ��ֶ�ֵ( 1��30 : lv - 1 )��( 31 �� 60 : lv - 30 ) ����
		@type					lv : int
		@param					lv : ����ȼ�
		@rtype					   : int
		@return					   : �ȼ������ĵȼ�����ֵ
		"""
		if lv <= 30 :
			return lv - 1
		return lv - ( Formulas.__getLevelSeg( lv ) * 30 )

	def getDoubleHitProbability( self, species, level, dexterity, ability ) :
		"""
		��ȡ�������������
		@type				species	  : MACRO DEFINATION
		@param				species	  : ��������
		@type				level	  : int
		@param				level	  : ����ȼ�
		@type				dexterity : MACRO DEFINATION
		@param				dexterity : ����ֵ
		"""
		if level < 1 or level > PetLevelEXP.getMaxLevel() :
			ERROR_MSG( "the pet's level is less than 1 or large than max level!" )
			return 0

		ptype = self.getType( species )
		if ptype == csdefine.PET_TYPE_STRENGTH:
			return 0.03 + 0.12 * ability * dexterity /( 7600 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_BALANCED:
			return 0.05 + 0.2 * ability * dexterity /( 11875 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_SMART:
			return 0.06 + 0.24 * ability * dexterity /( 18817 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_INTELLECT:
			return 0.02 + 0.08 * ability * dexterity /( 8133 * 1.5 ** ( 0.1 * level - 1 ) )
		else:
			return 0


	def getMagicDoubleHitProbability( self, species, level, intellect, ability ) :
		"""
		��ȡ��������������
		@type				species	  : MACRO DEFINATION
		@param				species	  : ��������
		@type				level	  : int
		@param				level	  : ����ȼ�
		@type				intellect : MACRO DEFINATION
		@param				intellect : ����
		"""
		if level < 1 or level > PetLevelEXP.getMaxLevel() :
			ERROR_MSG( "the pet's level is less than 1 or large than max level!" )
			return 0

		ptype = self.getType( species )
		if ptype == csdefine.PET_TYPE_STRENGTH:
			return 0.02 + 0.08 * ability * intellect /( 7600 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_BALANCED:
			return 0.05 + 0.2 * ability * intellect /( 11875 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_SMART:
			return 0.03 + 0.12 * ability * intellect /( 7527 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_INTELLECT:
			return 0.056 + 0.224 * ability * intellect /( 24531 * 1.5 ** ( 0.1 * level - 1 ) )
		else:
			return 0

	def getDodgeProbability( self, species, level, dexterity, ability ) :
		"""
		��ȡ�������������
		@type				species	  : MACRO DEFINATION
		@param				species	  : ��������
		@type				level	  : int
		@param				level	  : ����ȼ�
		@type				dexterity : MACRO DEFINATION
		@param				dexterity : ����ֵ

		0.03 + 0.12 * �ɳ��� * ���� / (7600*1.5^(0.1*Lv - 1))
		0.03 + 0.12 * �ɳ��� * ���� / (11875*1.5^(0.1*Lv - 1))
		0.03 + 0.12 * �ɳ��� * ���� / (18817*1.5^(0.1*Lv - 1))
		0.03 + 0.12 * �ɳ��� * ���� / (8177*1.5^(0.1*Lv - 1))
		"""
		if level < 1 or level > PetLevelEXP.getMaxLevel() :
			ERROR_MSG( "the pet's level is less than 1 or large than max level!" )
			return 0

		ptype = self.getType( species )
		if ptype == csdefine.PET_TYPE_STRENGTH:
			return 0.03 + 0.12 * ability * dexterity /( 7600 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_BALANCED:
			return 0.03 + 0.12 * ability * dexterity /( 11875 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_SMART:
			return 0.03 + 0.12 * ability * dexterity /( 18817 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_INTELLECT:
			return 0.03 + 0.12 * ability * dexterity /( 8177 * 1.5 ** ( 0.1 * level - 1 ) )
		else:
			return 0

	def getResistProbability( self, species, level, strength, ability ) :
		"""
		��ȡ�м���
		@type				species	  : MACRO DEFINATION
		@param				species	  : ��������
		@type				level	  : int
		@param				level	  : ����ȼ�
		@type				strength : MACRO DEFINATION
		@param				strength : ����

		0.07 + 0.28 * �ɳ��� * ���� / (15200*1.5^(0.1*Lv - 1))
		0.04 + 0.16 * �ɳ��� * ���� / (11875*1.5^(0.1*Lv - 1))
		0.026 + 0.104 * �ɳ��� * ���� / (11290*1.5^(0.1*Lv - 1))
		0.032 + 0.128 * �ɳ��� * ���� / (8177*1.5^(0.1*Lv - 1))
		"""
		if level < 1 or level > PetLevelEXP.getMaxLevel() :
			ERROR_MSG( "the pet's level is less than 1 or large than max level!" )
			return 0
		ptype = self.getType( species )
		if ptype == csdefine.PET_TYPE_STRENGTH:
			return 0.07 + 0.28 * ability * strength /( 15200 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_BALANCED:
			return 0.04 + 0.16 * ability * strength /( 11875 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_SMART:
			return 0.026 + 0.104 * ability * strength /( 11290 * 1.5 ** ( 0.1 * level - 1 ) )
		elif ptype == csdefine.PET_TYPE_INTELLECT:
			return 0.032 + 0.128 * ability * strength /( 8177 * 1.5 ** ( 0.1 * level - 1 ) )
		else:
			return 0


	def __getProbability( self, paramData, property, denominator, level, ability ):
		"""
		�������ԺͲ����ֵ����������������������������ʡ��м��ʣ�9:14 2009-3-5��wsf

		������ʽΪ���������� = 1%+[���ﵱǰ����-15-2.2*29-3*30-4*30-4.8*30-8.2*��lv-120��] *�ɳ���*3/1000000
		"""
		commonParam1 = paramData[ 0 ]
		commonParam2 = paramData[ 1 ]
		propertyParamList = paramData[ 2 ]

		count = level / 30		# ������Ҫ��������
		restLevel = level % 30	# �������ĵȼ���

		if count == 0:			# ����ȼ�����1-29�������ݹ�ʽ���⴦��
			restLevel -= 1
		if level == 30:			# ����պ���30�������ݹ�ʽ���⴦��
			count = 0
			restLevel -= 1

		result1 = property - commonParam2

		# 30 - ( index ==0 and 1 or 0 )�����������ڵ���30����propertyParamList��һ��������29
		for index in xrange( count ):
			result1 -= propertyParamList[ index ] * ( 30 - ( index == 0 and 1 or 0 ) )
		# restLevel * propertyParamList[ count - 1 ]�����Ｖ���30��������propertyParamList���һ������
		if count >= 5:
			result2 = 0
		else:
			result2 = restLevel * propertyParamList[ count ]
		return commonParam1 + ( result1 - result2 ) * ability * 3 / denominator

	# -------------------------------------------------
	# ������ʽ
	# -------------------------------------------------
	@staticmethod
	def getDisplayName( species, uname, name ) :
		"""
		��ȡ������ʾ������
		@type			species : MACRO DEFINATION
		@param			species : defined.py
		@type			uname	: str
		@param			uname	: uname
		@type			name	: str
		@param			name	: custom name
		@rtype					: str
		@return					: display name
		"""
		if name.strip() != "" : return name
		hierarchies = {}
		hierarchies[csdefine.PET_HIERARCHY_GROWNUP] = ShareTexts.PET_GROWNUP_DSP_NAME
		hierarchies[csdefine.PET_HIERARCHY_INFANCY1] = ShareTexts.PET_INFANCY1_DSP_NAME
		hierarchies[csdefine.PET_HIERARCHY_INFANCY2] = ShareTexts.PET_INFANCY2_DSP_NAME
		hierarchy = Formulas.getHierarchy( species )
#		return hierarchies[hierarchy] % uname
		return uname		# CSOL-11994 ����uname�����뱲�ֵȻ�����һ��

	@staticmethod
	def getAddedEXP( currLevel, currEXP, value ) :
		"""
		��� EXP ����ת��Ϊ�ȼ���ʣ�� EXP ֵ
		@type			currLevel : UINT8
		@param			currLevel : current level
		@type			currEXP	  : INT32
		@param			currEXP	  : current exp
		@type			value	  : INT32
		@param			value	  : the added exp value
		@rtype					  : tuple
		@return					  : ( new level, new exp )
		"""
		exp = currEXP + value
		expMax = PetLevelEXP.getEXPMax( currLevel )
		while exp >= expMax :
			exp -= expMax
			currLevel += 1
			expMax = PetLevelEXP.getEXPMax( currLevel )
			if expMax <= 0 :
				ERROR_MSG( "error exp max: %d" % expMax )
				break
		if currLevel > csconst.PET_LEVEL_UPPER_LIMIT :
			currLevel = csconst.PET_LEVEL_UPPER_LIMIT
			exp = PetLevelEXP.getEXPMax( currLevel )
		return currLevel, exp

	@staticmethod
	def getPosition( rolePos, roleYaw ) :
		"""
		��ȡ���������ҵ�λ��
		@type				rolePos : Vector3
		@param				rolePos : the owner's position
		@type				roleYaw : float
		@param				roleYaw : the own's yaw
		@rtype						: Vector3
		@param						: the pet's postion apart from its owner
		"""
		return rolePos	# ֱ�ӷ�����ҵ�����
		rx, ry, rz = rolePos
		keepDistance = csconst.PET_ROLE_KEEP_DISTANCE - 1.0
		x = rx + keepDistance * math.sin( roleYaw + math.pi/2 )
		z = rz + keepDistance * math.cos( roleYaw + math.pi/2 )
		return Math.Vector3( x, ry, z )



# --------------------------------------------------------------------
# global instances
# --------------------------------------------------------------------
formulas  = Formulas.instance()

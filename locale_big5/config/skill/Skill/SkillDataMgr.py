# -*- coding: cp950 -*-

#SkillDatas���޲z��

from SkillConfigs import skillConfig
import SkillConfigs
import cPickle
import binascii
import os
import Language
import Function


SKILL_CONFIG_HEAD = "Datas"

class SkillDataMgr:
	_instance = None
	def __init__( self ):
		assert SkillDataMgr._instance is None, "instance already exist in"
		self.__data = {}
		self._skillScript = {}
		self._skillcfgs= None
		self.initSkillCfgs()
		self.hasInitSkillScript = False

	def __loadData( self, ID ):
		"""
		�ھ�ID�ȡA�ʺA�[���t�m�ƾڡA�ê�^�ƾڪ��ޥ�
		@type		ID: int
		@param		ID: ���ˬd��ID��
		"""
		if not self.hasInitSkillScript:
			try:
				self.initSkillScript()
			except:
				pass
			self.hasInitSkillScript = True
		return cPickle.loads( binascii.a2b_hex( getattr( self._skillcfgs, "Datas_%d"%ID ) ))

	def __getitem__( self, ID ):
		"""
		��^�������ͪ���H[ ID ]��
		@type		ID: int
		@param		ID: ���ˬd��ID��
		"""
		try:
			return self.__data[ID]
		except KeyError, err:
			try:
				data = self.__loadData( ID )
				self.__data[ID] = data
				return data
			except:
				raise "KeyError %s" % ID
		except:
			raise "Unknown Error!"

	def __getConfigModuleFullName( self, moduleName ):
		"""
		"""
		return "config.skill.Skill.SkillConfigs.%s" % moduleName
	
	def __getScriptModuleFullName( self, moduleName ):
		"""
		"""
		return "Resource.Skills.%s" % moduleName
	
	def __getScriptModuleFullNameInSpellBase(  self, moduleName ):
		"""
		"""
		return "Resource.Skills.SpellBase.%s" % moduleName
	
	#�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X
	#                          public
	#�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X�X
	def has_key( self, ID ):
		"""
		�P�_ID�O�_�s�b
		@type		ID: int
		@param		ID: ���ˬd��ID��
		"""
		if self.__data.has_key( ID ):
			return True
		#try to find and load it
		try:
			self.__data[ID] = self.__loadData( ID )
			return True
		except:
			return False

	def initSkillCfgs( self ):
		"""
		"""
		self._skillcfgs = skillConfig

		#update some skillcfgs
		moduleNames = Language.searchConfigModuleName( "config/skill/Skill/SkillConfigs" )
		for moduleName in moduleNames:
			if not SKILL_CONFIG_HEAD in moduleName:
				continue
			moduleFullName = self.__getConfigModuleFullName( moduleName )
			compons = moduleFullName.split( "." )
			mod = __import__( moduleFullName )
			for com in compons[1:]:
				mod = getattr( mod, com )
			attrs = dir( mod )
			for attr in attrs:
				if SKILL_CONFIG_HEAD in attr:
					setattr( self._skillcfgs, attr, getattr( mod, attr ) )

	def initSkillScript( self ):
		"""
		"""
		#skill script
		moduleNames = Function.searchModuleName( "entities/cell/Resource/Skills" )
		for moduleName in moduleNames:
			moduleFullName = self.__getScriptModuleFullName( moduleName )
			compons = moduleFullName.split( "." )
			mod = __import__( moduleFullName )
			for com in compons[1:]:
				mod = getattr( mod, com )
			self._skillScript[moduleName] = mod

		moduleNames = Function.searchModuleName( "entities/cell/Resource/Skills/SpellBase" )
		for moduleName in moduleNames:
			moduleFullName = self.__getScriptModuleFullNameInSpellBase( moduleName )
			compons = moduleFullName.split( "." )
			mod = __import__( moduleFullName )
			for com in compons[1:]:
				mod = getattr( mod, com )
			self._skillScript["SpellBase."+moduleName] = mod

	def getScript( self, scriptName ):
		"""
		"""
		return self._skillScript[scriptName]
	
	@staticmethod
	def instance():
		"""
		��^SkillDataMgr��󪺹��
		"""
		if SkillDataMgr._instance is None:
			SkillDataMgr._instance = SkillDataMgr( )
		return SkillDataMgr._instance

Datas = SkillDataMgr.instance( )


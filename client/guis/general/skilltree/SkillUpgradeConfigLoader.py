# -*- coding: gb18030 -*-

# $Id: SkillTrainerLoader.py,v 1.1 2008-01-31 07:30:27 yangkai Exp $

import Language
from bwdebug import *
import BigWorld
import skills as Skill
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from GUIFacade.LearnSkillFacade import LearningSkill
from config.client.labels.ItemsFactory import POSTURE_STR
from config.client.colors import Datas as cscolors
from LabelGather import labelGather
import config.client.labels.GUIFacade as lbDatas
import config.client.labels.ItemsFactory as lbs_ItemsFactory
from config.skill.SkillTeachData import Datas as skTeachDatas
from config.skill.Skill.SkillDataMgr import Datas as skDatas
from ItemsFactory import SkillItem

import csdefine
import math
from Time import Time
import re

class SkillUpgradeLoader:
	"""
	���������ܸ����ü���
	"""
	__sk_config_path = "config/client/SkillUpgradeConfig.xml"
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert SkillUpgradeLoader._instance is None
		self._datas = {}
		SkillUpgradeLoader._instance = self
		self.load( self.__sk_config_path )
		
	def load( self, configPath ):
		section = Language.openConfigSection( configPath )
		if section is None:return
		for node in section.values():
			classID = node.readInt( "class" )
			if classID == 0:continue
			type = node.readInt( "type" )
			skillID = node.readInt64( "skillID" )
			isSpecial = node.readBool( "special" )
			rowIndex = node.readInt( "rowIndex" )
			colIndex = node.readInt( "colIndex" )
			skInfo = SkillInfo( skillID, type, isSpecial, rowIndex, colIndex )
			if self._datas.has_key( classID ):
				data = self._datas[classID]
				if data.has_key( type ):
					data[type].add( skInfo )
				else:
					data[type] = set( [skInfo] )
			else:
				self._datas[classID] = {}
				self._datas[classID][type] = set( [skInfo] )
		# �������
		Language.purgeConfig( self.__sk_config_path )

	def getSkInfos( self, classID, type ):
		"""
		����npc���ȡ�ö�Ӧ�ļ���ID��
		"""
		try:
			skInfos = list( self._datas[classID][type] )
			skInfos.sort( key = lambda skInfo: skInfo.sortIndex )
			return skInfos
		except KeyError:
			return []
	
	@staticmethod
	def instance():
		"""
		"""
		if SkillUpgradeLoader._instance is None:
			SkillUpgradeLoader._instance = SkillUpgradeLoader()
		return SkillUpgradeLoader._instance

# ------------------------------------------------------------------

class SkillInfo:
	
	def __init__( self, skillID, type, isSpecial, rowIndex, colIndex ):
		"""
		��ʼ��
		"""
		self.skillID = skillID
		self.type = type
		self.isSpecial = isSpecial
		self.curRow = rowIndex - 1
		self.curCol = colIndex - 1
		self.sortIndex = self.curRow*4 + self.curCol
	
	def getPreState( self, skType ):
		"""
		�Ƿ�Ϊǰ�ü���
		"""
		teachSkill = Skill.getSkill( self.skillID )
		nextSortIndex = self.sortIndex + 4
		nextSkillInfo = self.getNextSkill( skType,nextSortIndex )
		state = -1
		if nextSkillInfo is None :
			return state
		nextSkid = nextSkillInfo.skillID
		if nextSkid == 0:
			state = 0
		else:
			nextSkill = Skill.getSkill( nextSkid )
			if hasattr( nextSkill, "getReqSkills" ):
				reqSkills = nextSkill.getReqSkills()		#��ȡǰ�ü���
				skillsMap = set()
				if hasattr( teachSkill, "_SkillsMap" ):
					skillsMap = teachSkill._SkillsMap
				for reqSkill in reqSkills:
						if reqSkill in skillsMap:
							state = reqSkill
		return state
		
	def getNextSkill( self, skType, nextSortIndex ) :
		"""
		��ȡ���ü���
		"""
		player = BigWorld.player()
		pclass = player.getClass()
		skInfos = skUpgradeLoader.getSkInfos( pclass, skType )
		nextSkillInfo = None		
		for skillInfo in skInfos :
			if skillInfo.sortIndex == nextSortIndex :
				nextSkillInfo = skillInfo
		return nextSkillInfo
	
	def __getCurSkLevel( self, skill ):
		"""
		��ȡ��ɫ�ü��ܵĵȼ�
		"""
		tSkillID = skill.getMapSkillID( skill._SkillsMap )
		return tSkillID
	
	def __getRequireManaDes( self, skill ):
		requireManaDes = ""
		requireManaList = []
		if hasattr( skill , "getRequire" ):
			manaSkill = skill
			requireManaList = manaSkill.getRequire().getRequireManaList(  BigWorld.player(), manaSkill )		# �������ĵķ�������
		for requireMana in requireManaList:
			des = requireMana[0]
			number = re.findall( r"\d+", des )#����ȡ���� 1-N �����������ִ浽 number ��,�� ���ķ���:120 ��ô����� ['120']
			if number:
				if requireMana[1]:
					desNumber = PL_Font.getSource( number[0] , fc = "c6" )
				else:
					desNumber = PL_Font.getSource( number[0] , fc = "c3" )
			des = des.replace( number[0] ,desNumber )		#�����滻������ɫ��
			if requireManaDes == "" :
				requireManaDes += des
			else:
				requireManaDes = requireManaDes + PL_NewLine.getSource() + des
		return requireManaDes
	
	def getDescription( self, skillID, learned = True ):
		"""
		��ȡ����ѧϰ����
		"""
		skill = Skill.getSkill( skillID )
		skInfo = SkillItem( skill )
		return skInfo.description	# ������д��ֱ��ʹ��ͨ�õ�

	def getReqPotential( self, skill,learned = True ):
		skillID = skill.getID()
		skillData = skTeachDatas.get( skillID, None )
		if skillData is None: return 0
		if not learned:
			return skillData["ReqPotential"]
		nextSkID = skillData["nextLevelID"]
		if nextSkID > 0:
			nextSkData = skTeachDatas.get( nextSkID, None )
			if nextSkData is None: return 0
			return nextSkData["ReqPotential"]
		else:
			return 0
		
	def checkPotential( self, skill ):
		"""
		Ǳ�ܼ��
		"""
		reqPotential = self.getReqPotential( skill )
		return BigWorld.player().potential >= reqPotential
	
	def checkRemainPotential( self, skill ):
		"""
		Ǳ�ܼ��
		"""
		player = BigWorld.player()
		reqPotential = self.getReqPotential( skill )
		remainPotential = player.potential - player.getTotalPotential()
		return remainPotential >= reqPotential
	
	def getReqPlayerLevel( self, skill, learned = True ):
		skillID = skill.getID()
		skillData = skTeachDatas.get( skillID, None )
		if skillData is None: return 0
		if not learned: #δѧϰ
			return skillData["ReqLevel"]
		nextSkID = skillData["nextLevelID"]
		if nextSkID > 0:
			nextSkData = skTeachDatas.get( nextSkID, None )
			if nextSkData is None: return 0
			return nextSkData["ReqLevel"]
		else:
			return 0
	
	def checkPlayerLevel( self, skill ):
		"""
		�ȼ����
		"""
		reqPlayerLevel = self.getReqPlayerLevel( skill )
		return BigWorld.player().getLevel() >= reqPlayerLevel
	
	def checkMetier( self ):
		"""
		ְҵ���
		"""
		teachSkill = Skill.getSkill( self.skillID )
		return teachSkill.checkMetier()
	
	def checkPremissSkill( self ):
		"""
		ǰ�ü��ܼ��
		"""
		teachSkill = Skill.getSkill( self.skillID )
		return teachSkill.checkPremissSkill()
	
	def checkUpgrade( self, skillID ):
		if skillID == self.skillID:	#ûѧϰ��
			return False
		else:
			skill = Skill.getSkill( skillID )
			if not self.checkPlayerLevel( skill ):
				return False
			if not self.checkMetier():
				return False
			if not self.checkPremissSkill():
				return False
			if not self.checkRemainPotential( skill ):
				return False
		return True


	def getReqSkills( self, skDict ):
		"""
		��ȡǰ�ü���
		"""
		reqSkills = []
		reqSkDict = {}
		if len( ( skDict["param3"] if len( skDict["param3"] ) > 0 else "" )  ) > 0:
			reqSkStrs = set([e for e in ( skDict["param3"] if len( skDict["param3"] ) > 0 else "" ) .split(";")])
			for rSkill in reqSkStrs:
				if rSkill == "":continue
				rs = rSkill.split(":")
				if len( rs ) > 1:
					reqSkDict[int(rs[0])] = int(rs[1])
				else:
					reqSkills.append( int( rs[0] ) )
		return reqSkills, reqSkDict

	def __isHasDictSkill( self, skillID, reqSkDict ):
		"""
		��ȡǰ�ü���,�ṹ�� learnID0:reqID0;learnID1:reqID1
		"""
		player = BigWorld.player()
		dsp = ""
		colorFunc = lambda v : v and "c6" or "c3"
		if skillID:
			reSkillIDs = []
			reqSkIDs = reqSkDict.keys()
			reqTypes = {}
			for reqSkID in reqSkIDs:									#������ǰ�ü��ܷ���
				reqType = reqSkID/1000
				if reqType in reqTypes:
					reqTypes[reqType].append( reqSkID )
				else:
					reqTypes[reqType] = [reqSkID]
			for reqType, typList in reqTypes.items():
				typList.sort()
				for reqSkID in typList:
					leanSkID = reqSkDict[reqSkID]
					if skillID <= leanSkID:
						reSkillIDs.append( reqSkID )
						break
			for reSkillID in reSkillIDs:
				_reSkillsMap = self.getSkillsMap( reSkillID )
				reSkID = self.hasMapSkill( player.skillList_, _reSkillsMap )
				strColor = colorFunc(  reSkID > 0 )
				skill = Skill.getSkill( reSkillID )
				skill_level = skill.getLevel()
				skill_name = skill.getName()
				dsp += PL_Font.getSource( " %s"%skill_name+ str( skill_level ) + lbDatas.LEVEL, fc = strColor )
		return dsp

	def learnMapSkill( self, skills, skillsMap, skDict  ):
		"""
		�ж��Ƿ���skillIDs����hsMap�д��ڵļ���ID
		@type skillIDs: array receiver.getSkills()
		@type    hsMap: set skillLevelMap
		"""
		reqSks = skDict.keys()
		reqSks.sort()
		for skillID in skills:
			if skillID in skillsMap:
				for rs in reversed( reqSks ):
					if skillID >= rs:
						return ( skillID, skDict[rs] )

	def getSkillsMap( self, skillID ):
		"""
		��ȡ�ü���ӳ��
		"""
		skillsMap = set( [skillID] )
		teachID = self.getTeachSkID( skillID )
		teachSk = Skill.getSkill( teachID )
		if teachSk is None:return
		endLevel = teachSk._skillLevelMax
		startLevel = Skill.getSkill( skillID ).getLevel()
		while startLevel < endLevel:
			teachDatas = skTeachDatas[skillID]
			nextSkID = teachDatas["nextLevelID"]
			if nextSkID == 0: break
			skillsMap.add( nextSkID )
			skillID = nextSkID
			startLevel += 1
		return skillsMap

	def getTeachSkID( self, skillID ):
		"""
		��ȡѧϰ����
		"""
		skDict = skDatas[skillID]
		teachSkID = "9" +"%d"%((skillID/1000)*1000)
		return long( teachSkID )
		
	def __isHasMapSkill( self, skillID, reqSkills ):
		"""
		�Ƿ���Ҫ��������
		"""
		player = BigWorld.player()
		dsp = ""
		colorFunc = lambda v : v and "c6" or "c3"
		if skillID > 0:
			for reSkillID in reqSkills:
				if reSkillID:
					reSkill = Skill.getSkill( reSkillID )
					_reSkillsMap = self.getSkillsMap( reSkillID )
					reSkID = self.hasMapSkill( player.skillList_, _reSkillsMap )
					strColor = colorFunc(  reSkID > 0 )
					skill = Skill.getSkill( reSkID )
					if skill:
						skill_level = skill.getLevel()
						skill_name = skill.getName()
						dsp += PL_Font.getSource( " %s"%skill_name+ str( skill_level ) + lbDatas.LEVEL, fc = strColor )
		return dsp

	def hasMapSkill( self, skillIDs, hsMap ):
		"""
		�ж��Ƿ���skillIDs����hsMap�д��ڵļ���ID
		@type skillIDs: array
		@type    hsMap: set
		"""
		for skillID in skillIDs:
			if skillID in hsMap:
				return skillID
		return 0
		
	def __getRepSkills( self, skill ):
		"""
		ǰ�ü���˵��
		"""
		dsp = ""
		colorFunc = lambda v : v and "c6" or "c3"
		if hasattr( skill, "getReqSkills" ):
			player = BigWorld.player()
			reqSkills = skill.getReqSkills()
			for skilID in reqSkills:
				strColor = colorFunc( player.hasSkill( skilID ) )
				skill = Skill.getSkill( skilID )
				skill_level = skill.getLevel()
				skill_name = skill.getName()
				dsp += PL_Font.getSource( " %s"%skill_name+ str( skill_level ) + lbDatas.LEVEL, fc = strColor )
		return dsp

class ChallengeSkillLoader:
	"""
	��ս�������ܼ���
	"""
	__sk_config_path = "config/client/ChallengeSkills.xml"
	_instance = None

	def __init__( self ):
		# ��������2����2������ʵ��
		assert ChallengeSkillLoader._instance is None
		self._datas = {}
		ChallengeSkillLoader._instance = self
		self.load( self.__sk_config_path )
		
	def load( self, configPath ):
		section = Language.openConfigSection( configPath )
		if section is None:return
		for node in section.values():
			classID = node.readInt( "class" )
			if classID == 0:continue
			type = node.readInt( "type" )
			skillID = node.readInt64( "skillID" )
			isSpecial = node.readBool( "special" )
			rowIndex = node.readInt( "rowIndex" )
			colIndex = node.readInt( "colIndex" )
			cskInfo = SkillInfo( skillID, type, isSpecial, rowIndex, colIndex )
			if self._datas.has_key( classID ):
				data = self._datas[classID]
				data.add( cskInfo )
			else:
				self._datas[classID] = set( [cskInfo] )
		# �������
		Language.purgeConfig( self.__sk_config_path )

	def getChSkInfos( self, classID ):
		"""
		����npc���ȡ�ö�Ӧ�ļ���ID��
		"""
		try:
			cskInfos = list( self._datas[classID] )
			cskInfos.sort( key = lambda cskInfo: cskInfo.sortIndex )
			return cskInfos
		except KeyError:
			return []
	
	def getChSkDesp( self, classID, skillID ):
		cskInfos = self.getChSkInfos( classID )
		for cskInfo in cskInfos:
			if cskInfo.skillID == skillID:
				return cskInfo.getDescription( skillID )
		return ""
	
	@staticmethod
	def instance():
		"""
		"""
		if ChallengeSkillLoader._instance is None:
			ChallengeSkillLoader._instance = ChallengeSkillLoader()
		return ChallengeSkillLoader._instance

skUpgradeLoader = SkillUpgradeLoader.instance()
chSkillLoader = ChallengeSkillLoader.instance()
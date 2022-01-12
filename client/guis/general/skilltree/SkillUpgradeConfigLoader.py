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
	技能树技能格配置加载
	"""
	__sk_config_path = "config/client/SkillUpgradeConfig.xml"
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
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
		# 清除缓冲
		Language.purgeConfig( self.__sk_config_path )

	def getSkInfos( self, classID, type ):
		"""
		根据npc编号取得对应的技能ID表
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
		初始化
		"""
		self.skillID = skillID
		self.type = type
		self.isSpecial = isSpecial
		self.curRow = rowIndex - 1
		self.curCol = colIndex - 1
		self.sortIndex = self.curRow*4 + self.curCol
	
	def getPreState( self, skType ):
		"""
		是否为前置技能
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
				reqSkills = nextSkill.getReqSkills()		#获取前置技能
				skillsMap = set()
				if hasattr( teachSkill, "_SkillsMap" ):
					skillsMap = teachSkill._SkillsMap
				for reqSkill in reqSkills:
						if reqSkill in skillsMap:
							state = reqSkill
		return state
		
	def getNextSkill( self, skType, nextSortIndex ) :
		"""
		获取后置技能
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
		获取角色该技能的等级
		"""
		tSkillID = skill.getMapSkillID( skill._SkillsMap )
		return tSkillID
	
	def __getRequireManaDes( self, skill ):
		requireManaDes = ""
		requireManaList = []
		if hasattr( skill , "getRequire" ):
			manaSkill = skill
			requireManaList = manaSkill.getRequire().getRequireManaList(  BigWorld.player(), manaSkill )		# 技能消耗的法力描述
		for requireMana in requireManaList:
			des = requireMana[0]
			number = re.findall( r"\d+", des )#这里取任意 1-N 个连续的数字存到 number 中,如 消耗法力:120 那么结果是 ['120']
			if number:
				if requireMana[1]:
					desNumber = PL_Font.getSource( number[0] , fc = "c6" )
				else:
					desNumber = PL_Font.getSource( number[0] , fc = "c3" )
			des = des.replace( number[0] ,desNumber )		#数字替换成有颜色的
			if requireManaDes == "" :
				requireManaDes += des
			else:
				requireManaDes = requireManaDes + PL_NewLine.getSource() + des
		return requireManaDes
	
	def getDescription( self, skillID, learned = True ):
		"""
		获取技能学习描述
		"""
		skill = Skill.getSkill( skillID )
		skInfo = SkillItem( skill )
		return skInfo.description	# 不再重写，直接使用通用的

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
		潜能检测
		"""
		reqPotential = self.getReqPotential( skill )
		return BigWorld.player().potential >= reqPotential
	
	def checkRemainPotential( self, skill ):
		"""
		潜能检测
		"""
		player = BigWorld.player()
		reqPotential = self.getReqPotential( skill )
		remainPotential = player.potential - player.getTotalPotential()
		return remainPotential >= reqPotential
	
	def getReqPlayerLevel( self, skill, learned = True ):
		skillID = skill.getID()
		skillData = skTeachDatas.get( skillID, None )
		if skillData is None: return 0
		if not learned: #未学习
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
		等级检测
		"""
		reqPlayerLevel = self.getReqPlayerLevel( skill )
		return BigWorld.player().getLevel() >= reqPlayerLevel
	
	def checkMetier( self ):
		"""
		职业检测
		"""
		teachSkill = Skill.getSkill( self.skillID )
		return teachSkill.checkMetier()
	
	def checkPremissSkill( self ):
		"""
		前置技能检测
		"""
		teachSkill = Skill.getSkill( self.skillID )
		return teachSkill.checkPremissSkill()
	
	def checkUpgrade( self, skillID ):
		if skillID == self.skillID:	#没学习过
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
		获取前置技能
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
		获取前置技能,结构如 learnID0:reqID0;learnID1:reqID1
		"""
		player = BigWorld.player()
		dsp = ""
		colorFunc = lambda v : v and "c6" or "c3"
		if skillID:
			reSkillIDs = []
			reqSkIDs = reqSkDict.keys()
			reqTypes = {}
			for reqSkID in reqSkIDs:									#将需求前置技能分类
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
		判断是否在skillIDs中有hsMap中存在的技能ID
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
		获取该技能映射
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
		获取学习技能
		"""
		skDict = skDatas[skillID]
		teachSkID = "9" +"%d"%((skillID/1000)*1000)
		return long( teachSkID )
		
	def __isHasMapSkill( self, skillID, reqSkills ):
		"""
		是否需要其他技能
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
		判断是否在skillIDs中有hsMap中存在的技能ID
		@type skillIDs: array
		@type    hsMap: set
		"""
		for skillID in skillIDs:
			if skillID in hsMap:
				return skillID
		return 0
		
	def __getRepSkills( self, skill ):
		"""
		前置技能说明
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
	挑战副本技能加载
	"""
	__sk_config_path = "config/client/ChallengeSkills.xml"
	_instance = None

	def __init__( self ):
		# 不允许有2个或2个以上实例
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
		# 清除缓冲
		Language.purgeConfig( self.__sk_config_path )

	def getChSkInfos( self, classID ):
		"""
		根据npc编号取得对应的技能ID表
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
# -*- coding: gb18030 -*-
#

"""
"""
import Math
import random

import BigWorld
from bwdebug import *
from MsgLogger import g_logger
import csdefine
import csstatus
import csconst
import ItemTypeEnum
import ChatObjParser
import Function
from Love3 import g_skills as Skill
from Love3 import g_skillTeachDatas			# ����ѧϰ���ݹ���
g_skillDatas = g_skillTeachDatas._datas
from Love3 import g_skillTrainerList
from config.skill.Skill.SkillDataMgr import Datas as skDatas
import cschannel_msgs
import wizCommand

class RoleUpgradeSkillInterface:
	"""
	��ɫ���������ӿ�
	"""
	def __init__( self ):
		"""
		��ʼ��״̬��
		"""
		pass
		
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
	
	def getTeachSkID( self, skillID ):
		"""
		��ȡѧϰ����
		"""
		skDict = skDatas[skillID]
		teachSkID = "9" +"%d"%((skillID/1000)*1000)
		return long( teachSkID )
	
	def getSkillsMap( self, skillID ):
		"""
		��ȡ�ü���ӳ��
		"""
		skillsMap = set( [skillID] )
		teachID = self.getTeachSkID( skillID )
		teachSk = Skill[teachID]
		if teachSk is None:return
		endLevel = teachSk._skillLevelMax
		startLevel = Skill[skillID].getLevel()
		travSkills = [skillID]
		while startLevel < endLevel:
			teachDatas = g_skillDatas.get( skillID, None )
			if teachDatas is None:break
			nextSkID = teachDatas["nextLevelID"]
			if nextSkID == 0: break
			if nextSkID in travSkills:break
			travSkills.append( nextSkID )
			skillsMap.add( nextSkID )
			skillID = nextSkID
			startLevel += 1
		return skillsMap
	
	def isHasMapSkill( self, skillID, reqSkills ):
		"""
		�Ƿ���Ҫ��������
		"""
		if skillID < 0:return False
		for reSkillID in reqSkills:
			if reSkillID:
				reSkill = Skill[reSkillID]
				_reSkillsMap = self.getSkillsMap( reSkillID )
				if not self.hasMapSkill( self.getSkills(), _reSkillsMap ):
					return False
		return True
		
	def getNextSkillID( self, skillID ):
		"""
		��ȡ��һ�ȼ��ļ���id
		"""
		if g_skillDatas.has_key( skillID ):
			skTeachData = g_skillDatas[skillID]
			return skTeachData["nextLevelID"]
		return 0
	
	def getFinalSkillID( self, skillID, upgrades ):
		"""
		��ȡ������ѧ�ļ���id
		"""
		if upgrades <= 0:
			upgrades = 1
		level = Skill[skillID].getLevel()
		finalSkID = 0
		endLevel = level + upgrades
		travSkills = [skillID]
		while level < endLevel:
			teachDatas = g_skillDatas.get( skillID, None )
			if teachDatas is None:break
			nextSkillID = teachDatas["nextLevelID"]
			if nextSkillID == 0: break
			if nextSkillID in travSkills:break
			travSkills.append( nextSkillID )
			skillID = nextSkillID
			finalSkID = skillID
			level += 1
		return finalSkID

	def upgradeSkills( self, srcEntityID, learnSkills ):
		"""
		/Exposed method
		��ʼ��������
		@type skillIDs: array
		@type difLevels: array
		@param skillIDs: ��ѧ�����б�
		@param difLevels: ��ѧ��Ҫѧ���ܵȼ���
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		for skillID, upgrades in learnSkills.items():
			teachSkID = self.getTeachSkID( skillID )
			teachSkill = Skill[teachSkID]
			skDict = skDatas[teachSkID]
			reqMetier = ( skDict[ "param2" ] if len( skDict[ "param2" ] ) > 0 else "" )
			maxLevel = int( skDict["param4"] if len( skDict["param4"] ) > 0 else 0 )
			if reqMetier != "" and not self.isRaceclass( csconst.g_map_class[reqMetier], csdefine.RCMASK_CLASS ):
				INFO_MSG( "%s(%i): learn skill %i, metier differ." % (receiver.playerName, receiver.id, self._spellTeach) )
				self.statusMessage( csstatus.LEARN_SKILL_METIER_DIFFER )
				return
			totalPotential = self.getSkillTotalPotential( skillID, upgrades )
			if not self.hasPotential( totalPotential ): 		#Ǳ�ܵ㲻��
				INFO_MSG( "%s(%i): learn skill %i, potential %i need." % (self.playerName, self.id, teachSkID, totalPotential) )
				self.statusMessage( csstatus.LEARN_SKILL_NEED_POTENTIAL )
				return
			totalmoney = self.getSkillTotalMoney( skillID, upgrades )
			if not self.payMoney( totalmoney, csdefine.CHANGE_MONEY_LEARN_SKILL ):
				INFO_MSG( "%s(%i): learn skill %i, money %i need." % (self.playerName, self.id, teachSkID, g_skillTeachDatas[ skillID ]['ReqMoney']) )
				self.statusMessage( csstatus.LEARN_SKILL_NEED_MONEY )
				return
			finalSkillID =self.getFinalSkillID( skillID, upgrades )
			if finalSkillID <= 0:return
			finalSkLevel = Skill[finalSkillID].getLevel() 
			if finalSkillID in teachSkill._spellTeachs:				#��Ҫ�����ܵ�ʦ��ѧϰ��һ������
				if upgrades > 1:									#����ѧϰ
					self.statusMessage( csstatus.LEARN_SKILL_MORE_FROM_TRAINER, finalSkLevel - 1 )
					return
				else:
					self.statusMessage( csstatus.LEARN_SKILL_NEED_FROM_TRAINER )
					return
			reqLevel = g_skillTeachDatas[finalSkillID]['ReqLevel']
			if skillID != 0 and self.level < reqLevel:
				INFO_MSG( "%s(%i): learn skill %i, level %i need." % (self.playerName, self.id, teachSkID, reqLevel) )
				self.statusMessage( csstatus.LEARN_SKILL_NEED_LEVEL )
				return
			if finalSkLevel > maxLevel:
				INFO_MSG( "%s(%i): learn skill %i, skill is max level." % (self.playerName, self.id, teachSkID) )
				self.statusMessage( csstatus.LEARN_SKILL_MAX_LEVEL, teachSkill.getName() )
				return
			reqSkills, reqSkDict = self.getReqSkills( skDict )
			if len( reqSkDict ):
				if not self.isHasDictSkill( finalSkillID, reqSkDict ):
					self.statusMessage( csstatus.LEARN_SKILL_NEED_OTHER_SKILL )
					return
			if len( reqSkills ):
				if not self.isHasMapSkill( finalSkillID, reqSkills ):		#�Ƿ���Ҫ��������
					self.statusMessage( csstatus.LEARN_SKILL_NEED_OTHER_SKILL )
					return

			# ��Ǳ�ܵ㣬����ǰ��
			self.payPotential( totalPotential )

			if self.updateSkill( skillID, finalSkillID ):
				self.questSkillLearned( finalSkillID )
			try:
				g_logger.skillUpgradeLog( self.databaseID, self.getName(), finalSkillID, skillID, totalPotential,totalmoney )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
	
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
	
	def isHasDictSkill( self, skillID, reqSkDict ):
		"""
		��ȡǰ�ü���,�ṹ�� learnID0:reqID0;learnID1:reqID1
		"""
		canLearnSkillID = 0
		if skillID:
			reqSks = reqSkDict.keys()
			reqSks.sort()
			for reSkillID in reqSks:
				if reSkillID:
					reSkill = Skill[reSkillID]
					_reSkillsMap = self.getSkillsMap( reSkillID )
					canLearnSkillID = self.learnMapSkill( self.getSkills(), _reSkillsMap, reqSkDict )		# ��ǰ��ѧ�������ȼ�
					if canLearnSkillID and canLearnSkillID + 1 > skillID:		# Ҫѧ�ļ��ܵȼ����ɸ��ڵ�ǰ��ѧ�������ȼ�
						break
					else:
						canLearnSkillID = 0
		return canLearnSkillID != 0
	
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
						return skDict[rs]
		return 0
	
	def getSkillTotalPotential( self, skillID, upgrades ):
		totalSkillPotent = 0
		level = Skill[skillID].getLevel()
		endLevel = level + upgrades
		travSkills = [skillID]
		while level < endLevel:
			teachDatas = g_skillDatas.get( skillID, None )
			if teachDatas is None:break
			nextSkillId = teachDatas["nextLevelID"]
			if nextSkillId == 0: break
			if nextSkillId in travSkills:break
			travSkills.append( nextSkillId )
			reqPotential = g_skillDatas[nextSkillId]["ReqPotential"]
			totalSkillPotent += reqPotential
			skillID = nextSkillId
			level += 1
		return totalSkillPotent
	
	def getSkillTotalMoney( self, skillID, upgrades ):
		level = Skill[skillID].getLevel()
		totalSkillMoney = 0
		endLevel = level + upgrades
		travSkills = [skillID]
		while level < endLevel:
			teachDatas = g_skillDatas.get( skillID, None )
			if teachDatas is None:break
			nextSkillId = teachDatas["nextLevelID"]
			if nextSkillId == 0: break
			if nextSkillId in travSkills:break
			travSkills.append( nextSkillId )
			reqMoney = g_skillDatas[nextSkillId]["ReqMoney"]
			totalSkillMoney += reqMoney
			skillID = nextSkillId
			level += 1
		return totalSkillMoney
	
	def gm_upGradeSkLitToMax( self, srcEntityID, skillID ):
		"""
		/Exposed method
		����������ѧϰ�ȼ�,�ȼ�����
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		if skillID in self.getSkills():
			canUpGradeSkID = self.getCanUpGradeSkId( skillID )
			if canUpGradeSkID:
				wizCommand.wizCommand( self, self.id, "upgradeSkill", "%d %d"%(skillID, canUpGradeSkID) )
		else:
			if g_skillTrainerList.has( skillID ):
				teachSk = Skill[skillID]
				skillID = teachSk._spellTeach
				canUpGradeSkID = self.getCanUpGradeSkId( skillID )
				if canUpGradeSkID:
					wizCommand.wizCommand( self, self.id, "add_skill", "%d"%canUpGradeSkID )
	
	def gm_upGradeSkToMax( self, srcEntityID, skillID ):
		"""
		/Exposed method
		���������ȼ�
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		if skillID in self.getSkills():
			skills = list(self.getSkillsMap( skillID ))
			skills.sort()
			maxLvId = skills[-1]
			wizCommand.wizCommand( self, self.id, "upgradeSkill", "%d %d"%(skillID, maxLvId) )
		else:
			if g_skillTrainerList.has( skillID ):
				teachSk = Skill[skillID]
				skillID = teachSk._spellTeach
				skills = list(self.getSkillsMap( skillID ))
				skills.sort()
				maxLvId = skills[-1]
				wizCommand.wizCommand( self, self.id, "add_skill", "%d"%maxLvId )

	def gm_removeSkill( self, srcEntityID, skillID ):
		"""
		/Exposed method
		ɾ������
		"""
		if not self.hackVerify_( srcEntityID ):
			return
		if not skillID in self.getSkills():
			return
		wizCommand.wizCommand( self, self.id, "remove_skill", "%d"%skillID )
	
	def getCanUpGradeSkId( self, skillID ):
		"""
		��ȡ�ȼ����ƿ����������ȼ�����id
		"""
		canUpGradeId = None
		reqLevel = g_skillTeachDatas[skillID]['ReqLevel']
		if reqLevel > self.level: #�Ѿ��ﵽ��ɫ�ȼ����Ƶ���ߵȼ�
			self.statusMessage( csstatus.LEARN_SKILL_NEED_LEVEL )
			return
		else:
			skills = list(self.getSkillsMap( skillID ))
			skills.sort()
			for skId in skills:
				reqLevel = g_skillTeachDatas[skId]['ReqLevel']
				if reqLevel >= self.level:
					canUpGradeId = skId
					break
			if canUpGradeId is None:
				canUpGradeId = skills[-1]
	 	return canUpGradeId
# -*- coding: gb18030 -*-
import BigWorld

import csdefine
import csconst
import csstatus
import Define
import event.EventCenter as ECenter
from MessageBox import *
from config.client.msgboxtexts import Datas as mbmsgs
from config.skill.SkillTeachData import Datas as skTeachDatas
from config.skill.Skill.SkillDataMgr import Datas as skDatas
import Language
import skills

class RoleUpgradeSkillInterface:

	__sk_config_path = "config/client/ChallengeSkills.xml"
	
	def __init__( self ):
		"""
		初始化
		"""
		self.learnSkills = {}
		self.chalSkills = {}
		self._chDatas = {}
		self.load( self.__sk_config_path )
		
	def load( self, configPath ):
		sect = Language.openConfigSection( configPath )
		if sect is None:return
		for skId, subSect in sect.items():
			self._chDatas[int(skId)] = subSect
		# 清除缓冲
		Language.purgeConfig( configPath )

	def checkUpgradeSkill( self, skillID ):
		"""
		升级技能，调用1次升1级
		"""
		if not skillID in self.skillList_:	#没有学习过该技能
			return
		teachSkID = self.getTeachSkID( skillID )
		skDict = skDatas[teachSkID]
		teachSk = skills.getSkill( teachSkID )
		if teachSk is None:return
		isChalSkill = teachSkID in self._chDatas
		reqMetier = ( skDict[ "param2" ] if len( skDict[ "param2" ] ) > 0 else "" )
		if reqMetier != "" and not self.isRaceclass( csconst.g_map_class[reqMetier], csdefine.RCMASK_CLASS ):
			self.statusMessage( csstatus.LEARN_SKILL_METIER_DIFFER )
			return
		totalPotential = self.getTotalPotential( isChalSkill )
		if self.potential < totalPotential: 		#潜能点不够
			self.statusMessage( csstatus.LEARN_SKILL_NEED_POTENTIAL )
			return
		totalmoney = self.getTotalMoney( isChalSkill )
		if self.money < totalmoney:
			self.statusMessage( csstatus.LEARN_SKILL_NEED_MONEY )
			return
		newSkillID = self.getFinalSkillID( skillID, isChalSkill )
		if newSkillID <= 0:
			return
		newSkill = skills.getSkill( newSkillID )
		newSkLevel = newSkill.getLevel()
		if newSkillID in teachSk._spellTeachs:
			upgrades = self.learnSkills.get( skillID, 0 )
			if isChalSkill:
				upgrades = self.chalSkills.get( skillID, 0 )
			if upgrades > 0:
				self.statusMessage( csstatus.LEARN_SKILL_MORE_FROM_TRAINER, newSkLevel - 1 )
				return
			else:
				self.statusMessage( csstatus.LEARN_SKILL_NEED_FROM_TRAINER )
				return
		teachData = skTeachDatas.get( newSkillID, None )
		if teachData is None:return
		reqLevel = teachData['ReqLevel']
		if self.level < reqLevel:
			self.statusMessage( csstatus.LEARN_SKILL_NEED_LEVEL )
			return
		maxLevel = int( skDict["param4"] if len( skDict["param4"] ) > 0 else 0 )
		if newSkLevel > maxLevel:
			self.statusMessage( csstatus.LEARN_SKILL_MAX_LEVEL, newSkill.getName() )
			return
		reqSkills, reqSkDict = self.getReqSkills( skDict )
		if len( reqSkDict ):
			if not self.isHasDictSkill( newSkillID, reqSkDict ):
				self.statusMessage( csstatus.LEARN_SKILL_NEED_OTHER_SKILL )
				return
		if len( reqSkills ):
			if not self.isHasMapSkill( newSkillID, reqSkills ):		#是否需要其他技能
				self.statusMessage( csstatus.LEARN_SKILL_NEED_OTHER_SKILL )
				return
		if isChalSkill:
			if skillID in self.chalSkills:
				self.chalSkills[skillID] += 1
			else:
				self.chalSkills[skillID] = 1
			ECenter.fireEvent( "EVT_ON_ROLE_CHECK_CHASKILL_SUCC", skillID )
		else:
			if skillID in self.learnSkills:
				self.learnSkills[skillID] += 1
			else:
				self.learnSkills[skillID] = 1
			ECenter.fireEvent( "EVT_ON_ROLE_CHECK_SKILL_SUCC", skillID )	
	
	def downgradeSkill( self, skillID ):
		"""
		降级检测的技能
		"""
		if not skillID in self.skillList_:	#是否已学过该技能
			return
		if self.chalSkills.has_key( skillID ):
			self.chalSkills[skillID] -= 1
			ECenter.fireEvent( "EVT_ON_ROLE_CHECK_CHASKILL_SUCC", skillID )
			if self.chalSkills[skillID] <= 0:
				self.chalSkills.pop( skillID )
		if self.learnSkills.has_key( skillID ):
			self.learnSkills[skillID] -= 1
			level = self.learnSkills[skillID]
			ECenter.fireEvent( "EVT_ON_ROLE_CHECK_SKILL_SUCC", skillID )
			if self.learnSkills[skillID] <= 0:
				self.learnSkills.pop( skillID )
			
	def upgradeSkills( self, isChSkill = False ):
		"""
		升级多个技能
		"""
		if isChSkill:
			self.cell.upgradeSkills( self.chalSkills )
		else:
			self.cell.upgradeSkills( self.learnSkills )

	def onUpdateSkill( self, oldSkillID, newSkillID ):
		"""
		Define Method
		技能升级成功回调
		"""
		if oldSkillID in self.learnSkills:
			self.learnSkills.pop( oldSkillID )
		if oldSkillID in self.chalSkills:
			self.chalSkills.pop( oldSkillID )
	
	def cancelUpgradeSkill( self, isChSkill = False ):
		"""
		取消技能升级
		"""
		if isChSkill:
			for skillID in self.chalSkills:
				self.chalSkills[skillID] = 0
				ECenter.fireEvent( "EVT_ON_ROLE_CHECK_CHASKILL_SUCC", skillID )
			self.chalSkills = {}
		else:
			for skillID in self.learnSkills:
				self.learnSkills[skillID] = 0
				ECenter.fireEvent( "EVT_ON_ROLE_CHECK_SKILL_SUCC", skillID )
			self.learnSkills = {}

	def getFinalSkillID( self, skillID, isChalSkill ):
		"""
		获取最终能学的技能id
		"""
		upgrades = self.learnSkills.get( skillID, 0 )
		if isChalSkill:
			upgrades = self.chalSkills.get( skillID, 0 )
		skill = skills.getSkill( skillID )
		level = skill.getLevel()
		endLevel = level + upgrades
		finalSkID = 0
		travSkills = [skillID]								#遍历的技能
		while level <= endLevel:
			teachDatas = skTeachDatas.get( skillID, None )
			if teachDatas is None:break
			nextSkillID = teachDatas["nextLevelID"]
			if nextSkillID in travSkills:break				#死循环
			travSkills.append( nextSkillID )
			if nextSkillID == 0: break
			skillID = nextSkillID
			finalSkID = skillID
			level += 1
		return finalSkID

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
	
	def isHasDictSkill( self, skillID, reqSkDict ):
		"""
		获取前置技能,结构如 learnID0:reqID0;learnID1:reqID1
		"""
		canLearnSkillID = 0
		if skillID:
			reqSks = reqSkDict.keys()
			reqSks.sort()
			for reSkillID in reqSks:
				if reSkillID:
					reSkill = skills.getSkill( reSkillID )
					_reSkillsMap = self.getSkillsMap( reSkillID )
					canLearnSkillID = self.learnMapSkill( self.skillList_, _reSkillsMap, reqSkDict )		# 当前能学到的最大等级
					if canLearnSkillID and canLearnSkillID + 1 > skillID:		# 要学的技能等级不可高于当前能学到的最大等级
						break
					else:
						canLearnSkillID = 0
		return canLearnSkillID != 0
	
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
						return skDict[rs]
		return 0

	def getSkillsMap( self, skillID ):
		"""
		获取该技能映射
		"""
		skillsMap = set( [skillID] )
		teachID = self.getTeachSkID( skillID )
		teachSk = skills.getSkill( teachID )
		if teachSk is None:return
		endLevel = teachSk._skillLevelMax
		startLevel = skills.getSkill( skillID ).getLevel()
		travSkills = [skillID]
		while startLevel < endLevel:
			teachDatas = skTeachDatas.get( skillID, None )
			if teachDatas is None:break
			nextSkID = teachDatas["nextLevelID"]
			if nextSkID in travSkills:break
			travSkills.append( nextSkID )
			if nextSkID == 0: break
			skillsMap.add( nextSkID )
			skillID = nextSkID
			startLevel += 1
		return skillsMap

	def isHasMapSkill( self, skillID, reqSkills ):
		"""
		是否需要其他技能
		"""
		if skillID < 0:return False
		for reSkillID in reqSkills:
			if reSkillID:
				reSkill = skills.getSkill( reSkillID )
				_reSkillsMap = self.getSkillsMap( reSkillID )
				if not self.hasMapSkill( self.skillList_, _reSkillsMap ):
					return False
		return True

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

	def getTotalPotential( self, isChaSkill = False ):
		"""
		获取所需潜能点之和
		"""
		totalPote = 0
		learnSkills = self.learnSkills
		if isChaSkill:
			learnSkills = self.chalSkills
		for skillID in learnSkills:
			totalPote += self.getSkillTotalPotential( skillID, learnSkills )
		return totalPote
	
	def getTotalMoney( self, isChaSkill = False ):
		"""
		获取所需金钱之和
		"""
		totalMoney = 0
		learnSkills = self.learnSkills
		if isChaSkill:
			learnSkills = self.chalSkills
		for skillID in learnSkills:
			totalMoney += self.getSkillTotalMoney( skillID, learnSkills )
		return totalMoney

	def getNextSkillID( self, skillID ):
		"""
		获取下一等级的技能id
		"""
		if skTeachDatas.has_key( skillID ):
			skTeachData = skTeachDatas[skillID]
			return skTeachData["nextLevelID"]
		return 0
	
	def getSkillTotalPotential( self, skillID, learnSkills ):
		"""
		获取升级一个技能所需潜能
		"""
		upgrades = learnSkills.get( skillID, 1 )
		totalSkillPotent = 0
		skill = skills.getSkill( skillID )
		level = skill.getLevel()
		endLevel = level + upgrades
		travSkills = [skillID]
		while level < endLevel:
			teachDatas = skTeachDatas.get( skillID, None )
			if teachDatas is None:break
			nextSkillId = teachDatas["nextLevelID"]
			if nextSkillId == 0: break
			if nextSkillId in travSkills: break
			travSkills.append( nextSkillId )
			nextDatas = skTeachDatas.get( nextSkillId, None )
			if nextDatas is None:break
			reqPotential = nextDatas["ReqPotential"]
			totalSkillPotent += reqPotential
			skillID = nextSkillId
			level += 1
		return totalSkillPotent
	
	def getCurSkillPotential( self, skillID ):
		"""
		获取升级下一个技能所需潜能
		"""
		upgrades = self.learnSkills.get( skillID, None )
		reqPotential = 0
		skill = skills.getSkill( skillID )
		level = skill.getLevel()
		if upgrades == None:
			endLevel = level + 1
		else:
			endLevel = level + upgrades + 1
		travSkills = [skillID]
		while level < endLevel:
			teachDatas = skTeachDatas.get( skillID, None )
			if teachDatas is None:break
			nextSkillId = teachDatas["nextLevelID"]
			if nextSkillId == 0: break
			if nextSkillId in travSkills: break
			travSkills.append( nextSkillId )
			nextDatas = skTeachDatas.get( nextSkillId, None )
			if nextDatas is None:break
			reqPotential = nextDatas["ReqPotential"]
			skillID = nextSkillId
			level += 1
		return reqPotential
		
	def getSkillTotalMoney( self, skillID, learnSkills ):
		"""
		获取升级一个技能所需金钱
		"""
		upgrades = self.learnSkills.get( skillID, 1 )
		totalSkillMoney = 0
		skill = skills.getSkill( skillID )
		level = skill.getLevel()
		endLevel = level + upgrades
		travSkills = [skillID]
		while level < endLevel:
			teachDatas = skTeachDatas.get( skillID, None )
			if teachDatas is None:break
			nextSkillId = teachDatas["nextLevelID"]
			if nextSkillId == 0: break
			if nextSkillId in travSkills: break
			travSkills.append( nextSkillId )
			nextDatas = skTeachDatas.get( nextSkillId, None )
			if nextDatas is None:break
			reqMoney = nextDatas["ReqMoney"]
			totalSkillMoney += reqMoney
			skillID = nextSkillId
			level += 1
		return totalSkillMoney
	
	def getCurSkillMoney( self, skillID ):
		"""
		获取升级一个技能所需金钱
		"""
		upgrades = self.learnSkills.get( skillID, None )
		reqMoney = 0
		skill = skills.getSkill( skillID )
		level = skill.getLevel()
		if upgrades == None:
			endLevel = level + 1
		else:
			endLevel = level + upgrades + 1
		travSkills = [skillID]
		while level < endLevel:
			teachDatas = skTeachDatas.get( skillID, None )
			if teachDatas is None:break
			nextSkillId = teachDatas["nextLevelID"]
			if nextSkillId == 0: break
			if nextSkillId in travSkills: break
			travSkills.append( nextSkillId )
			nextDatas = skTeachDatas.get( nextSkillId, None )
			if nextDatas is None:break
			reqMoney = nextDatas["ReqMoney"]
			skillID = nextSkillId
			level += 1
		return reqMoney	
	
	def getUpgradeSkillID( self, skillID ):
		"""
		获取升级成功后id
		"""
		upgrades = 0
		if skillID in self.learnSkills:
			upgrades = self.learnSkills[skillID]
		if skillID in self.chalSkills:
			upgrades = self.chalSkills[skillID]
		skill = skills.getSkill( skillID )
		level = skill.getLevel()
		upLevel = level + upgrades
		for upSkid, teachData in skTeachDatas.iteritems():
			if upSkid/1000 == skillID/1000 and upLevel == teachData["Level"]:
				return upSkid
		return skillID + upgrades

	def getTeachSkID( self, skillID ):
		"""
		获取学习技能
		"""
		skDict = skDatas[skillID]
		teachSkID = "9" +"%d"%((skillID/1000)*1000)
		return long( teachSkID )
	
	def gm_upGradeSkLitToMax( self, skillID ):
		"""
		升级到当前可升级的最大等级，只有等级限制
		"""
		self.cell.gm_upGradeSkLitToMax( skillID )
	
	def gm_upGradeSkToMax( self, skillID ):
		"""
		升级到技能的最大等级，无限制
		"""
		self.cell.gm_upGradeSkToMax( skillID )
	
	def gm_removeSkill( self, skillID ):
		"""
		删除该技能
		"""
		self.cell.gm_removeSkill( skillID )
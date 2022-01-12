# -*- coding: gb18030 -*-
#
# $Id: Spell_Teach.py,v 1.40 2008-08-26 06:26:15 qilan Exp $

"""
"""

from SpellBase import *
from bwdebug import *
from interface.State import State
import csdefine
import csconst
from bwdebug import *
import csstatus
from Spell_Item import Spell_Item
from Love3 import g_skills as Skill
from Resource.SkillTeachLoader import g_skillTeachDatas		# 技能学习数据管理
g_skillDatas = g_skillTeachDatas._datas
from MsgLogger import g_logger
import Const
import random
from ObjectScripts.GameObjectFactory import g_objFactory
from VehicleHelper import getCurrVehicleID, getCurrVehicleSkillIDs

class Spell_Teach( Spell ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		self._reqSkills = set([])			# 所需技能，如果没有则置()
		self._spellTeachs = set([])

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )

		####################################
		#学习需求
		#技能的1级学习条件
		#self._reqLevel = dict.readInt( "ReqLevel" )				# 所需等级，如果没有则置0
		self._reqMetier = ( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else "" ) 				# 所需职业，如果没有则置""
		if len( ( dict["param3"] if len( dict["param3"] ) > 0 else "" )  ) > 0:
			self._reqSkills = set([int(e) for e in ( dict["param3"] if len( dict["param3"] ) > 0 else "" ) .split(";")])
		# 教授的1级技能ID
		self._skillLevelMax = int( dict["param4"] if len( dict["param4"] ) > 0 else 0 ) 			# 技能的最大等级
		if len( ( dict["param1"] if len( dict["param1"] ) > 0 else "" )  ) > 0:
			self._spellTeachs = set([int(e) for e in ( dict["param1"] if len( dict["param1"] ) > 0 else "" ) .split(";")])
		self._spellTeach = sorted( self._spellTeachs )[0]
		# 做映射
		self._SkillsMap = self.getSkillsMap( self._spellTeach )

	def getSkillsMap( self, skillID ):
		"""
		获取学习技能对应的所有技能
		"""
		skillsMap = set( [skillID] )
		endLevel = self._skillLevelMax
		startLevel = Skill[skillID].getLevel()
		while startLevel <= endLevel:
			teachDatas = g_skillDatas.get( skillID, None )
			if teachDatas is None:break
			nextSkID = teachDatas["nextLevelID"]
			if nextSkID == 0: break
			skillsMap.add( nextSkID )
			skillID = nextSkID
			startLevel += 1
		return skillsMap

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
	
	def getNextSkillID( self, tSkillID ):
		"""
		获取下一级技能id
		"""
		if g_skillDatas.has_key( tSkillID ):
			skTeachData = g_skillDatas[tSkillID]
			nextSkId = skTeachData["nextLevelID"]
			if nextSkId == 0:						#最大等级的 nextLevelID 为0
				nextSkId = tSkillID
			return nextSkId
		return self._spellTeach

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# 职业不一样
		if self._reqMetier != "" and not receiver.isRaceclass( csconst.g_map_class[self._reqMetier], csdefine.RCMASK_CLASS ):
			INFO_MSG( "%s(%i): learn skill %i, metier differ." % (receiver.playerName, receiver.id, self._spellTeach) )
			receiver.statusMessage( csstatus.LEARN_SKILL_METIER_DIFFER )
			return

		# 是否有该类型的技能
		skillID = self.hasMapSkill( receiver.getSkills(), self._SkillsMap )
		ifUpdate = skillID != 0
		# 等级最大级
		nextSkillID = 0
		if ifUpdate:
			if Skill[skillID].getLevel() >= self._skillLevelMax:
				INFO_MSG( "%s(%i): learn skill %i, skill is max level." % (receiver.playerName, receiver.id, self._spellTeach) )
				receiver.statusMessage( csstatus.LEARN_SKILL_MAX_LEVEL, self.getName() )
				return
			nextSkillID = self.getNextSkillID( skillID )
		else:
			nextSkillID = self._spellTeach

		# 要求等级
		if nextSkillID != 0 and receiver.level < g_skillTeachDatas[ nextSkillID ]['ReqLevel']:
			INFO_MSG( "%s(%i): learn skill %i, level %i need." % (receiver.playerName, receiver.id, self._spellTeach, g_skillTeachDatas[ nextSkillID ]['ReqLevel']) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_LEVEL )
			return

		# 是否有要求技能
		if nextSkillID:
			for reSkillID in self._reqSkills:
				if reSkillID:
					reSkill = Skill[reSkillID]
					_reSkillsMap = self.getSkillsMap( reSkillID )
					if not self.hasMapSkill( receiver.getSkills(), _reSkillsMap ):
						INFO_MSG( "%s(%i): learn skill %i, skill %i need." % (receiver.playerName, receiver.id, self._spellTeach, reSkillID) )
						receiver.statusMessage( csstatus.LEARN_SKILL_NEED_OTHER_SKILL )
						return

		potential = g_skillTeachDatas[ nextSkillID ]['ReqPotential']
		if not receiver.hasPotential( potential ):
			INFO_MSG( "%s(%i): learn skill %i, potential %i need." % (receiver.playerName, receiver.id, self._spellTeach, potential) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_POTENTIAL )
			return

		# 扣钱
		money = g_skillTeachDatas[ nextSkillID ]['ReqMoney']
		if not receiver.payMoney( money, csdefine.CHANGE_MONEY_LEARN_SKILL ):
			INFO_MSG( "%s(%i): learn skill %i, money %i need." % (receiver.playerName, receiver.id, self._spellTeach, g_skillTeachDatas[ skillID ]['ReqMoney']) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_MONEY )
			return

		# 扣潜能点
		receiver.payPotential( potential )

		if ifUpdate:		# 如果是升级，则删除原等级技能
			receiver.setTemp( "roleUpdateSkill", True )
			if receiver.updateSkill( skillID, nextSkillID ):
				receiver.questSkillLearned( nextSkillID )
			try:
				g_logger.skillUpgradeLog( receiver.databaseID, receiver.getName(), nextSkillID, skillID, potential,money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
				
			receiver.removeTemp( "roleUpdateSkill" )
		else:			# 添加技能
			if receiver.addSkill( self._spellTeach ):
				receiver.questSkillLearned( nextSkillID )
			try:
				g_logger.skillLearnLog( receiver.databaseID, receiver.getName(), nextSkillID, potential, money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

class Spell_Teach_MutLevel_Limit( Spell, Spell_Teach ):
	"""
	有多层等级限制的技能学习方式 by 姜毅
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self._reqSkills = {}			# 所需技能，如果没有则置()
		self._reqSk = []
		
	def init( self, dict ):
		"""
		"""
		Spell.init( self, dict )
		####################################
		#学习需求
		#技能的1级学习条件
		#self._reqLevel = dict.readInt( "ReqLevel" )				# 所需等级，如果没有则置0
		self._reqMetier = ( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else "" ) 				# 所需职业，如果没有则置""
		if len( ( dict["param3"] if len( dict["param3"] ) > 0 else "" )  ) > 0:
			_reqSkills = set([e for e in ( dict["param3"] if len( dict["param3"] ) > 0 else "" ) .split(";")])
			self.__paramCheck( _reqSkills )
			for rSkill in _reqSkills:
				if rSkill == "":continue
				rs = rSkill.split(":")
				self._reqSkills[int(rs[0])] = int(rs[1])		# 0 所需前置技能 1 对应学得的最大等级的技能
		self._reqSk = self._reqSkills.keys()
		self._reqSk.sort()

		self._skillLevelMax = int( dict["param4"] if len( dict["param4"] ) > 0 else 0 ) 			# 技能的最大等级
		if len( ( dict["param1"] if len( dict["param1"] ) > 0 else "" )  ) > 0:
			self._spellTeachs = set([int(e) for e in ( dict["param1"] if len( dict["param1"] ) > 0 else "" ) .split(";")])
		self._spellTeach = sorted( self._spellTeachs )[0]
		# 做映射
		self._SkillsMap = self.getSkillsMap( self._spellTeach )

	def __paramCheck( self, param ):
		"""
		参数检测
		"""
		skillIDs = []
		for rSkill in param:
			if rSkill == "":continue
			rs = rSkill.split(":")
			skID1 = int(rs[0])
			skID2 = int(rs[1])
			if skID1 in skillIDs:
				ERROR_MSG( "skillID( %i ) configuration is wrong: %i." % ( self.getID(), skID1 ) )   # 前置技能配置错误
			else:
				skillIDs.append( skID1 )
			if skID2 in skillIDs:
				ERROR_MSG( "skillID( %i ) configuration is wrong: %i." % ( self.getID(), skID2 ) )   # 前置技能配置错误
			else:
				skillIDs.append( skID2)

	def learnMapSkill( self, skillIDs, hsMap ):
		"""
		判断是否在skillIDs中有hsMap中存在的技能ID
		@type skillIDs: array receiver.getSkills()
		@type    hsMap: set skillLevelMap
		"""
		for skillID in skillIDs:
			if skillID in hsMap:
				for s in reversed( self._reqSk ):
					if skillID >= s:
						return self._reqSkills[s]
		return 0

	def getNextSkillID( self, tSkillID ):
		"""
		获取下一级技能id
		"""
		if g_skillDatas.has_key( tSkillID ):
			skTeachData = g_skillDatas[tSkillID]
			nextSkId = skTeachData["nextLevelID"]
			if nextSkId == 0:						#最大等级的 nextLevelID 为0
				nextSkId = tSkillID
			return nextSkId
		return self._spellTeach

	def getSkillsMap( self, skillID ):
		"""
		获取学习技能对应的所有技能
		"""
		skillsMap = set( [skillID] )
		endLevel = self._skillLevelMax
		startLevel = Skill[skillID].getLevel()
		while startLevel <= endLevel:
			teachDatas = g_skillDatas.get( skillID, None )
			if teachDatas is None:break
			nextSkID = teachDatas["nextLevelID"]
			if nextSkID == 0: break
			skillsMap.add( nextSkID )
			skillID = nextSkID
			startLevel += 1
		return skillsMap
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		# 职业不一样
		if self._reqMetier != "" and not receiver.isRaceclass( csconst.g_map_class[self._reqMetier], csdefine.RCMASK_CLASS ):
			INFO_MSG( "%s(%i): learn skill %i, metier differ." % (receiver.playerName, receiver.id, self._spellTeach) )
			receiver.statusMessage( csstatus.LEARN_SKILL_METIER_DIFFER )
			return

		# 是否有该类型的技能
		skillID = self.hasMapSkill( receiver.getSkills(), self._SkillsMap )
		ifUpdate = skillID != 0
		nextSkillID = 0
		# 等级最大级
		if ifUpdate:
			if Skill[skillID].getLevel() >= self._skillLevelMax:
				INFO_MSG( "%s(%i): learn skill %i, skill is max level." % (receiver.playerName, receiver.id, self._spellTeach) )
				receiver.statusMessage( csstatus.LEARN_SKILL_MAX_LEVEL, self.getName() )
				return
			nextSkillID = self.getNextSkillID( skillID ) # 如果是更新技能那么将技能ID设到下级技能ID
		else:
			nextSkillID = self._spellTeach
		# 要求等级
		if nextSkillID != 0 and receiver.level < g_skillTeachDatas[ nextSkillID ]['ReqLevel']:
			INFO_MSG( "%s(%i): learn skill %i, level %i need." % (receiver.playerName, receiver.id, self._spellTeach, g_skillTeachDatas[ nextSkillID ]['ReqLevel']) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_LEVEL )
			return
			
		# 是否有要求技能
		canLearnSkillID = 0
		if nextSkillID:
			for reSkillID in self._reqSk:
				if reSkillID:
					reSkill = Skill[reSkillID]
					_reSkillsMap = self.getSkillsMap( reSkillID )
					canLearnSkillID = self.learnMapSkill( receiver.getSkills(), _reSkillsMap )		# 当前能学到的最大等级
					if canLearnSkillID and canLearnSkillID + 1 > nextSkillID:		# 要学的技能等级不可高于当前能学到的最大等级
						break
					else:
						canLearnSkillID = 0
		if canLearnSkillID == 0:
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_OTHER_SKILL )
			return

		potential = g_skillTeachDatas[ nextSkillID ]['ReqPotential']
		if not receiver.hasPotential( potential ):
			INFO_MSG( "%s(%i): learn skill %i, potential %i need." % (receiver.playerName, receiver.id, self._spellTeach, potential) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_POTENTIAL )
			return

		# 扣钱
		money = g_skillTeachDatas[ nextSkillID ]['ReqMoney']
		if not receiver.payMoney( money, csdefine.CHANGE_MONEY_LEARN_SKILL ):
			INFO_MSG( "%s(%i): learn skill %i, money %i need." % (receiver.playerName, receiver.id, self._spellTeach, g_skillTeachDatas[ nextSkillID ]['ReqMoney']) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_MONEY )
			return

		# 扣潜能点
		receiver.payPotential( potential )

		if ifUpdate:		# 如果是升级，则删除原等级技能
			receiver.setTemp( "roleUpdateSkill", True )
			if receiver.updateSkill( skillID , nextSkillID ):
				receiver.questSkillLearned( nextSkillID )
			try:
				g_logger.skillUpgradeLog( receiver.databaseID, receiver.getName(), nextSkillID, skillID, potential,money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			receiver.removeTemp( "roleUpdateSkill" )
		else:			# 添加技能
			if receiver.addSkill( self._spellTeach ):
				receiver.questSkillLearned( nextSkillID )
			try:
				g_logger.skillLearnLog( receiver.databaseID, receiver.getName(), nextSkillID, potential, money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

class Spell_Pet_TeachBook( Spell_Item, Spell ):
	"""
	宠物技能学习书
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		Spell.init( self, dict )

		self._reqMetier = ( dict[ "param2" ] if dict[ "param2" ] > 0 else "" ) 				# 所需职业，如果没有则置""
		self._spellTeach = long( dict["param1"] if dict["param1"] else 0 ) 				# 教授的1级技能ID
		self._replaceSkillID = int( dict["param3"] if dict["param3"] else 0 )				# 前置技能ID
		self._skillLevelMax = int( dict["param4"] if dict["param4"] else 0 ) 			# 技能的最大等级
		# 做映射
		self._SkillsMap = set( [ self._spellTeach + e for e in xrange(self._skillLevelMax)])

		param5 = [int(e) for e in ( dict["param5"] if dict["param5"] else "" ) .split("|")]
		teachSkillID = self._spellTeach / 1000
		if teachSkillID in param5:
			index = param5.index( teachSkillID )
			self._preSkillList = param5[ 0:index ]
			if index == len( param5 ):
				self._postSkillList = []
			else:
				self._postSkillList = param5[ index+1:len( param5 ) ]
		else:
			DEBUG_MSG("宠物技能书配置有误！！！！！！！！！！！")

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

	def hasPostSkill( self, skillIDs, hsMap ):
		"""
		判断是否在skillIDs中有hsMap中存在的技能ID
		@type skillIDs: list
		@type    hsMap: list
		"""
		if not hsMap: return 0
		for skillID in skillIDs:
			if skillID/ 1000 in hsMap:
				return skillID
		return 0

	def useableCheck( self, caster, target ) :
		petOwner = target.getObject()
		actPet = petOwner.pcg_getActPet()
		if not actPet :
			return csstatus.PET_EVOLVE_FAIL_NOT_CONJURED
		if actPet.etype != "REAL" :
			return csstatus.SKILL_PET_TOO_FAR

		receiver = actPet.entity
		# 职业不一样
		if self._reqMetier != "":
			if not receiver.isRaceclass( csconst.g_map_class[self._reqMetier], csdefine.PET_TYPE_MASK ):
				return csstatus.PET_LEARN_SKILL_METIER_DIFFER

		# 是否有该类型的技能。宠物技能书的作用只是让宠物学会这一类型的技能，
		# 如果已经有了该技能，那么不能再学习了。
		if self.hasMapSkill( receiver.getSkills(), self._SkillsMap ):
			return csstatus.PET_LEARN_SKILL_ALREADY_HAVE

		skillID = self._spellTeach

		# 要求等级
		if skillID and receiver.level < g_skillTeachDatas[ skillID ]['ReqLevel']:
			return csstatus.PET_LEARN_SKILL_NEED_LEVEL

		# 是否有高阶技能
		if self.hasPostSkill( receiver.getSkills(), self._postSkillList ):
			return csstatus.PET_LEARN_SKILL_HAS_POST_SKILL

		# 是否有前置技能
		if skillID and self._replaceSkillID:
			if not self._replaceSkillID in receiver.getSkills():	# 如果玩家身上没有这个前置技能
				return csstatus.PET_LEARN_SKILL_NEED_OTHER_SKILL

		# 如果没有可以替换的技能，则要判断宠物身上的技能个数是否已满
		if not self._replaceSkillID:
			#算出宠物的主动技能总数：天赋技能不算。
			mapMonsterScript = g_objFactory.getObject( petOwner.pcg_petDict.get( receiver.databaseID ).mapMonster )
			inbornSkillCount = 0
			noLevelSkillIDList = [ skillID/1000 for skillID in mapMonsterScript.getInbornSkills() ]
			petSkillList = receiver.getSkills()
			skillCount = len( petSkillList )
			for skillID in petSkillList:
				if skillID / 1000 in noLevelSkillIDList:
					skillCount -= 1

			vpet = g_objFactory.getObject( mapMonsterScript.mapPetID )
			skillLimit = vpet.getSkillCountLimit( receiver.getHierarchy(), receiver.getStamp() )
			if skillCount >= skillLimit:
				return csstatus.PET_LEARN_SKILL_MAX

		return Spell.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# 是否有该类型的技能
		skillID = self.hasMapSkill( receiver.getSkills(), self._SkillsMap )

		if skillID != 0:		# 如果已经有了该技能，那么不能再学习了。
			receiver.statusMessage( csstatus.PET_LEARN_SKILL_ALREADY_HAVE, self.getName() )
			return

		skillID = self._spellTeach
		cskill = Skill[self._spellTeach]
		if cskill.getLevel() < cskill.getMaxLevel():
			lv = cskill.getMaxLevel() - cskill.getLevel()
			if g_skillTeachDatas[ self._spellTeach + lv ]['ReqLevel'] <= receiver.level:
				skillID = self._spellTeach + lv
			else:
				for v in xrange( lv ):
					if receiver.level < g_skillTeachDatas[ self._spellTeach + v + 1 ]['ReqLevel']:
						skillID = self._spellTeach + v
						break

		if self._replaceSkillID:
			receiver.updateSkill( self._replaceSkillID, skillID )
			try:
				g_logger.skillPetUpgradeLog( caster.databaseID, caster.getName(), receiver.databaseID, skillID,self._replaceSkillID )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		else:
			receiver.addSkill( skillID )
			try:
				g_logger.skillPetLearnLog( caster.databaseID, caster.getName(), receiver.databaseID, skillID )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		receiver.statusMessage( csstatus.SKILL_PET_LEARN, self.getName() )


class Spell_TeachTongSkill( Spell_Teach ):
	"""
	帮会技能学习
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Teach.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Teach.init( self, dict )
		#学习需求
		# 注释掉这行是因为玩家可以看到这个技能学习的时候帮会建筑等级必须已经达到
		#self.buildingLv = dict.readString( "buildingLv" )				# 帮会建筑 研究院等级

	def getCurrentLearnSkillID( self, receiver ):
		"""
		获取当前学习技能ID
		"""
		# 是否有该类型的技能
		skillID = self.hasMapSkill( receiver.getSkills(), self._SkillsMap )
		ifUpdate = skillID != 0

		# 等级最大级
		if ifUpdate:
			if Skill[skillID].getLevel() >= self._skillLevelMax:
				#receiver.statusMessage( csstatus.LEARN_SKILL_MAX_LEVEL, self.getName() )
				return 0
			skillID += 1 # 如果是更新技能那么将技能ID设到下级技能ID
		else:
			skillID = self._spellTeach
		return skillID

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# 职业不一样
		if self._reqMetier != "" and not receiver.isRaceclass( csconst.g_map_class[self._reqMetier], csdefine.RCMASK_CLASS ):
			INFO_MSG( "%s(%i): learn skill %i, metier differ." % (receiver.playerName, receiver.id, self._spellTeach) )
			receiver.statusMessage( csstatus.LEARN_SKILL_METIER_DIFFER )
			return

		# 是否有该类型的技能
		skillID = self.hasMapSkill( receiver.getSkills(), self._SkillsMap )
		ifUpdate = skillID != 0

		# 等级最大级
		if ifUpdate:
			if Skill[skillID].getLevel() >= self._skillLevelMax:
				INFO_MSG( "%s(%i): learn skill %i, skill is max level." % (receiver.playerName, receiver.id, self._spellTeach) )
				receiver.statusMessage( csstatus.LEARN_SKILL_MAX_LEVEL, self.getName() )
				return
			skillID += 1 # 如果是更新技能那么将技能ID设到下级技能ID
		else:
			skillID = self._spellTeach

		# 要求等级
		if skillID != 0 and receiver.level < g_skillTeachDatas[ skillID ]['ReqLevel']:
			INFO_MSG( "%s(%i): learn skill %i, level %i need." % (receiver.playerName, receiver.id, self._spellTeach, g_skillTeachDatas[ skillID ]['ReqLevel']) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_LEVEL )
			return

		# 是否有要求技能
		skillCount = len( self._reqSkills )
		if not skillID and skillCount > 0:
			for num in xrange(skillCount):
				reSkillID = list(self._reqSkills)[num]
				if reSkillID:
					reSkill = Skill[reSkillID]
					reCurrLevel = reSkill.getLevel()
					_reSkillsMap = set( [ reSkillID + e for e in xrange(reCurrLevel, reSkill.getMaxLevel() + 1)])
					if not self.hasMapSkill( receiver.getSkills(), _reSkillsMap ):
						INFO_MSG( "%s(%i): learn skill %i, skill %i need." % (receiver.playerName, receiver.id, self._spellTeach, self._reqSkills[num]) )
						receiver.statusMessage( csstatus.LEARN_SKILL_NEED_OTHER_SKILL )
						return

		tongContribute = g_skillTeachDatas[ skillID ]['tongContribute']
		if receiver.tong_holdCity:
			tongContribute *= Const.TONG_HOLD_CITY_CONTRIBUT_DISCOUNT
			receiver.statusMessage( csstatus.TONG_HOLD_CITY_DISCOUNT1, csconst.TONG_CITYWAR_CITY_MAPS.get( receiver.tong_holdCity, receiver.tong_holdCity ) )
		if not receiver.tong_payContribute( tongContribute ):
			receiver.statusMessage( csstatus.TONG_LEARN_SKILL_REP_CONTRIBUTE, tongContribute )
			return

		potential = g_skillTeachDatas[ skillID ]['ReqPotential']
		if not receiver.hasPotential( potential ):
			INFO_MSG( "%s(%i): learn skill %i, potential %i need." % (receiver.playerName, receiver.id, self._spellTeach, potential) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_POTENTIAL )
			return

		# 扣钱
		money = g_skillTeachDatas[ skillID ]['ReqMoney']
		if not receiver.payMoney( money, csdefine.CHANGE_MONEY_LEARN_SKILL  ):
			INFO_MSG( "%s(%i): learn skill %i, money %i need." % (receiver.playerName, receiver.id, self._spellTeach, g_skillTeachDatas[ skillID ]['ReqMoney']) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_MONEY )
			return

		# 扣潜能点
		receiver.payPotential( potential )

		if ifUpdate:		# 如果是升级，则删除原等级技能
			receiver.setTemp( "roleUpdateSkill", True )
			receiver.updateSkill( skillID - 1, skillID )
			try:
				g_logger.skillTongUpgradeLog( receiver.databaseID, receiver.getName(), skillID, skillID - 1, potential, money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			receiver.removeTemp( "roleUpdateSkill" )
		else:			# 添加技能
			receiver.addSkill( self._spellTeach )
			try:
				g_logger.skillTongLearnLog( receiver.databaseID, receiver.getName(), skillID, potential, money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )


class Spell_VehicleTeach( Spell_Teach ):
	"""
	骑宠的技能学习
	"""
	def __init__( self ):
		"""
		"""
		Spell_Teach.__init__( self )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情。
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return False

		currVehicleID = getCurrVehicleID( receiver )
		if currVehicleID == 0:
			receiver.statusMessage( csstatus.LEARN_SKILL_MUST_CALL_VEHICLE )
			return False

		# 因为骑宠技能学习的途径变化 添加映射表1级技能 by姜毅
		vehicleSkills = getCurrVehicleSkillIDs( receiver )
		levels = []
		for vs in vehicleSkills:
			if Skill[vs].getLevel() == 1:
				self._SkillsMap.add( self._spellTeach - 1 )
		# 是否有该类型的技能
		skillID = self.hasMapSkill( vehicleSkills, self._SkillsMap )
		ifUpdate = skillID != 0

		# 等级最大级
		if ifUpdate:
			if Skill[skillID].getLevel() >= self._skillLevelMax:
				INFO_MSG( "%s(%i)'s vehicle: learn skill %i, skill is max level." % (receiver.playerName, receiver.id, self._spellTeach) )
				receiver.statusMessage( csstatus.VEHICLE_LEARN_SKILL_MAX_LEVEL, self.getName() )
				receiver.removeTemp( "item_using" )
				return False
			skillID += 1 # 如果是更新技能那么将技能ID设到下级技能ID
		else:
			skillID = self._spellTeach

		if not ifUpdate:
			if len( vehicleSkills ) >= csconst.VEHICLE_SKILLS_TOTAL:
				receiver.statusMessage( csstatus.LEARN_SKILL_COUNT_LIMIT )
				receiver.removeTemp( "item_using" )
				return False

		# 要求等级
		vehicleLevel = receiver.currAttrVehicleData["level"]
		reqLevel = g_skillTeachDatas[ skillID ]['ReqLevel']
		if skillID != 0 and vehicleLevel < reqLevel:
			INFO_MSG( "%s(%i)'s vehicle: learn skill %i, level %i need." % (receiver.playerName, receiver.id, self._spellTeach, reqLevel) )
			receiver.statusMessage( csstatus.VEHICLE_LEARN_SKILL_NEED_LEVEL )
			receiver.removeTemp( "item_using" )
			return False

		# 是否有要求技能
		skillCount = len( self._reqSkills )
		if skillID and skillCount > 0:
			for num in xrange(skillCount):
				reSkillID = list(self._reqSkills)[num]
				if reSkillID:
					reSkill = Skill[reSkillID]
					reCurrLevel = reSkill.getLevel()
					_reSkillsMap = set( [ reSkillID + e for e in xrange( reSkill.getMaxLevel() - reCurrLevel + 1 )])
					if not self.hasMapSkill( vehicleSkills, _reSkillsMap ):
						INFO_MSG( "%s(%i)'s vehicle: learn skill %i, skill %i need." % (receiver.playerName, receiver.id, self._spellTeach, list( self._reqSkills )[num]) )
						receiver.statusMessage( csstatus.LEARN_SKILL_NEED_OTHER_SKILL )
						receiver.removeTemp( "item_using" )
						return False

		skillPoint = g_skillTeachDatas[ skillID ]['ReqPotential']
		vehicleSkPoint = receiver.currVehicleData["skPoint"]
		if vehicleSkPoint < skillPoint:
			INFO_MSG( "%s(%i)'s vehicle: learn skill %i, skillPoint %i need." % (receiver.playerName, receiver.id, self._spellTeach, skillPoint) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_SKPOINT )
			receiver.removeTemp( "item_using" )
			return False

		# 扣钱
		money = g_skillTeachDatas[ skillID ]['ReqMoney']
		if not receiver.payMoney( money, csdefine.CHANGE_MONEY_LEARN_SKILL ):
			INFO_MSG( "%s(%i)'s vehicle: learn skill %i, money %i need." % (receiver.playerName, receiver.id, self._spellTeach, g_skillTeachDatas[ skillID ]['ReqMoney']) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_MONEY )
			receiver.removeTemp( "item_using" )
			return False

		receiver.addVehicleSkPoint( currVehicleID, -skillPoint )

		if ifUpdate:		# 如果是升级，则删除原等级技能
			receiver.setTemp( "roleUpdateSkill", True )
			receiver.updateVehicleSkill( currVehicleID, skillID - 1, skillID )
			try:
				g_logger.skillVehicleUpgradeLog( receiver.databaseID, receiver.getName(), currVehicleID,skillID,skillID - 1, skillPoint,money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			receiver.removeTemp( "roleUpdateSkill" )
		else:			# 添加技能
			receiver.addVehicleSkill( currVehicleID, self._spellTeach )
			try:
				g_logger.skillVehicleLearnLog( receiver.databaseID, receiver.getName(), currVehicleID, skillID, skillPoint,money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		
		return True

class Spell_VehicleTeachBook( Spell_Item, Spell_VehicleTeach ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Spell_VehicleTeach.__init__( self )
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_VehicleTeach.init( self, dict )
		Spell_Item.init( self, dict )

	def useableCheck( self, caster, receiver ) :
		"""
		"""
		return Spell_Item.useableCheck( self, caster, receiver )
		
	def cast( self, caster, target ):
		Spell_VehicleTeach.cast( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情。
		"""
		if Spell_VehicleTeach.receive( self, caster, receiver ):
			Spell_Item.updateItem(self, caster )

class Spell_TeachTongPetSkill( Spell_TeachTongSkill ):
	"""
	宠物帮会技能学习
	"""
	def getCurrentLearnSkillID( self, receiver ):
		"""
		获取当前学习技能ID
		"""
		actPet = receiver.pcg_getActPet()
		if not actPet :
			return 0
		if actPet.etype != "REAL" :
			return 0
			
		# 是否有该类型的技能
		skillID = self.hasMapSkill( actPet.entity.getSkills(), self._SkillsMap )
		ifUpdate = ( skillID != 0 )

		# 等级最大级
		if ifUpdate:
			if Skill[skillID].getLevel() >= self._skillLevelMax:
				#receiver.statusMessage( csstatus.LEARN_SKILL_MAX_LEVEL, self.getName() )
				return 0
			skillID += 1 # 如果是更新技能那么将技能ID设到下级技能ID
		else:
			skillID = self._spellTeach
		return skillID
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情。
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		actPet = receiver.pcg_getActPet()
		if not actPet :
			receiver.statusMessage( csstatus.PET_EVOLVE_FAIL_NOT_CONJURED )
			return
		if actPet.etype != "REAL" :
			receiver.statusMessage( csstatus.SKILL_PET_TOO_FAR )
			return
			
		petEntity = actPet.entity
		# 职业不一样
		if self._reqMetier != "" and not petEntity.isRaceclass( csconst.g_map_class[self._reqMetier], csdefine.RCMASK_CLASS ):
			INFO_MSG( "%s(%i): learn skill %i, metier differ." % (petEntity.playerName, petEntity.id, self._spellTeach) )
			receiver.statusMessage( csstatus.PET_LEARN_SKILL_METIER_DIFFER )
			return
		# 是否有该类型的技能
		skillID = self.hasMapSkill( petEntity.getSkills(), self._SkillsMap )
		if skillID == 0:
			receiver.statusMessage( csstatus.PET_LEARN_SKILL_NOT_LEARN )
			return
			
		if Skill[skillID].getLevel() >= self._skillLevelMax:
			INFO_MSG( "%s(%i): learn skill %i, skill is max level." % (petEntity.playerName, petEntity.id, self._spellTeach) )
			receiver.statusMessage( csstatus.PET_LEARN_SKILL_LEVEL_MAX, self.getName() )
			return
		skillID += 1 # 将技能ID设到下级技能ID
		learnSkillData = g_skillTeachDatas[ skillID ]
		# 要求等级
		if petEntity.level < learnSkillData['ReqLevel']:
			INFO_MSG( "%s(%i): learn skill %i, level %i need." % (petEntity.getName(), petEntity.id, self._spellTeach, g_skillTeachDatas[ skillID ]['ReqLevel']) )
			receiver.statusMessage( csstatus.PET_LEARN_SKILL_NEED_LEVEL )
			return
			
		# 是否有要求技能
		skillCount = len( self._reqSkills )
		if not skillID and skillCount > 0:
			for num in xrange(skillCount):
				reSkillID = list(self._reqSkills)[num]
				if reSkillID:
					reSkill = Skill[reSkillID]
					reCurrLevel = reSkill.getLevel()
					_reSkillsMap = set( [ reSkillID + e for e in xrange(reCurrLevel, reSkill.getMaxLevel() + 1)])
					if not self.hasMapSkill( petEntity.getSkills(), _reSkillsMap ):
						INFO_MSG( "%s(%i): learn skill %i, skill %i need." % (petEntity.getName(), petEntity.id, self._spellTeach, self._reqSkills[num]) )
						receiver.statusMessage( csstatus.PET_LEARN_SKILL_NEED_OTHER_SKILL )
						return
		tongContribute = learnSkillData['tongContribute']
		if receiver.tong_holdCity:
			tongContribute *= Const.TONG_HOLD_CITY_CONTRIBUT_DISCOUNT
			receiver.statusMessage( csstatus.TONG_HOLD_CITY_DISCOUNT1, csconst.TONG_CITYWAR_CITY_MAPS.get( receiver.tong_holdCity, receiver.tong_holdCity ) )

		if not receiver.tong_payContribute( tongContribute ):
			receiver.statusMessage( csstatus.TONG_LEARN_SKILL_REP_CONTRIBUTE, tongContribute )
			return
			
		petEntity.updateSkill( skillID - 1, skillID )
		try:
			g_logger.skillPetUpgradeLog( receiver.databaseID, receiver.getName(), petEntity.databaseID, skillID, skillID - 1  )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

class Spell_TeachPGSkill( Spell_Item, Spell_Teach ):
	"""
	盘古守护技能学习
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Teach.__init__( self )
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		Spell_Teach.init( self, dict )
		
		self._spellTeach = long( dict["param1"] if dict["param1"] else 0 ) 					# 教授技能ID
		self._skillLevelMax = int( dict["param2"] if dict["param2"] else 0 ) 				# 技能的最大等级
		# 做映射
		self._SkillsMap = self.getSkillsMap( self._spellTeach )

	def useableCheck( self, caster, target ) :
		"""
		校验技能是否可以使用。
		"""
		if caster.level < g_skillTeachDatas[ self._spellTeach ]['ReqLevel']:			# 要求等级
			INFO_MSG( "%s(%i): learn skill %i, level %i need." % (caster.playerName, caster.id, self._spellTeach, g_skillTeachDatas[ self._spellTeach ]['ReqLevel']) )
			return csstatus.LEARN_SKILL_NEED_LEVEL 
			
		if Skill[self._spellTeach].getLevel() > self._skillLevelMax:							# 是否为最大等级
				INFO_MSG( "%s(%i): learn skill %i, skill is max level." % ( caster.playerName, caster.id, self._spellTeach) )
				return csstatus.SKILL_SPELL_LEARN_SKILL_MAX_LEVEL
				
		if self._spellTeach in caster.getSkills():										# 是否已经学习了该技能
				return csstatus.SKILL_SPELL_LEARN_SKILL_ALREADY
				
		if Skill[self._spellTeach].getLevel() > 1:										# 是否已经学习了低等级的技能
			lowSkillID = self._spellTeach -1
			if lowSkillID not in caster.getSkills():
				return csstatus.NATURE_JADE_LEVEL_INVALID

		return Spell_Item.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# 技能若非1级则需要升级（该技能要求是必须从1级开始学）
		ifUpdate = Skill[self._spellTeach].getLevel() > 1

		if ifUpdate:		# 如果是升级，则删除原等级技能
			receiver.setTemp( "roleUpdateSkill", True )
			receiver.updateSkill( self._spellTeach - 1, self._spellTeach )
			try:
				g_logger.skillPGUpgradeLog( receiver.databaseID, receiver.getName(), self._spellTeach, self._spellTeach - 1 )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			receiver.removeTemp( "roleUpdateSkill" )
		else:			# 添加技能
			receiver.addSkill( self._spellTeach )
			try:
				g_logger.skillPGLearnLog( receiver.databaseID, receiver.getName(), self._spellTeach )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
				

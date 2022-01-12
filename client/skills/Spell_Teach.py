# -*- coding: gb18030 -*-
#
# $Id: Spell_Teach.py,v 1.6 2008-07-15 04:08:27 kebiao Exp $

"""
SpellTeach技能类。
"""
import math
from bwdebug import *
from SpellBase import *
from Function import Functor
import BigWorld
import skills as Skill
import csdefine
import csstatus
import csconst
import csstatus_msgs as StatusMsgs
from SkillTeachLoader import g_skillTeachDatas		# 技能学习数据管理
g_skillDatas = g_skillTeachDatas._datas
from config.skill.Skill.SkillDataMgr import Datas as skDatas

class Spell_Teach( Spell ):
	"""
	训练法术基础，仅仅用于技能训练窗口显示所有参数。
	"""
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Spell.__init__( self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def filterReqSkills_( self, skillId ) :
		"""
		获取要学习ID是skillId的技能，所需要的所有前置技能。
		skillId是用来指明技能等级的，因为当前不同等级的技
		能，其所需要的前置技能可能不相同。例如：
		5级狂暴心法支持1-9级双重打击；
		6级狂暴心法支持1-24级双重打击；
		7级狂暴心法支持1-39级双重打击；
		因此不同等级的双重打击技能就需要不同等级的狂暴心法
		"""
		try :
			candidates = [ skId for skId in self._reqSkills \
				if self._reqSkillsMap[skId] > skillId ]						# 注意，_reqSkills必须是升序排列
		except :
			EXCEHOOK_MSG( "-------->>> error: skId:%i map id:%i" % ( skId, skillId ) )
			return set()
		results = set()
		skTypes = []
		for skId in candidates :
			if skId / 1000 not in skTypes :
				results.add( skId )
				skTypes.append( skId / 1000 )
		return results


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置字典数据
		@type dict:				Python dict
		"""
		Spell.init( self, dict )
		#学习需求
		tmpReqSkills = set()						# 所需技能，如果没有则置()
		self._reqSkillsMap = {}
		#技能的1级学习条件
		self._reqMetier = dict[ "param2" ]			# 所需职业，如果没有则置""
		for skillID in dict["param3"].split( ";" ) :	# 多个前置技能以分号分隔
			if not skillID.strip() : continue
			if ":" in skillID :
				reqSkillID, upperLimit = skillID.split( ":" )
				self._reqSkillsMap[ int( reqSkillID ) ] = int( upperLimit )
				tmpReqSkills.add( int( reqSkillID ) )
			else :
				tmpReqSkills.add( int( skillID ) )
		self._reqSkills = sorted( tmpReqSkills )
		self._spellTeachs = set()
		for skillID in dict["param1"].split( ";" ) :
			if not skillID.strip() : continue
			self._spellTeachs.add( int( skillID ) )
		self._spellTeach = sorted( self._spellTeachs )[0]# 教授的1级技能ID
		self._skillLevelMax = int( dict["param4"] )		# 技能的最大等级
		# 做映射
		self._SkillsMap = self.getSkillsMap( self._spellTeach )
		self._maxSkillID = sorted( self._SkillsMap )[-1]
		
	def getMapSkillID( self, hasMap ):
		"""
		是否有技能映射表里的技能
		@param  hsMap: 技能映射表
		@type   hsMap: set
		"""
		player = BigWorld.player()
		for skillID in player.getSkillList():
			if skillID in hasMap:
				return skillID
		return 0
	
	def getSkillsMap( self, skillID ):
		"""
		获取学习技能对应的所有技能
		"""
		skillsMap = set( [skillID] )
		endLevel = self._skillLevelMax
		skill = Skill.getSkill( skillID )
		if skill is None:
			return skillsMap
		startLevel = skill.getLevel()
		count = 0
		while startLevel <= endLevel:
			teachDatas = g_skillDatas.get( skillID, None )
			if teachDatas is None:break
			nextSkID = teachDatas["nextLevelID"]
			if nextSkID == 0: break
			skillsMap.add( nextSkID )
			skillID = nextSkID
			startLevel += 1
		return skillsMap

	def getPotential( self, player ):
		"""
		花费潜能点
		@param player:	玩家实体
		@type player:	entity
		"""
		if g_skillDatas.has_key( self.getNextSkillID() ):
			return g_skillDatas[ self.getNextSkillID() ]['ReqPotential']
		return 0

	def getTeachSkillMap( self ):
		"""
		要学习技能的列表
		"""
		return self._SkillsMap

	def getNeedPlayerLevel( self ):
		"""
		获取当前技能等级对应的需求玩家等级
		"""
		if g_skillDatas.has_key( self.getNextSkillID() ):
			return g_skillDatas[ self.getNextSkillID() ]['ReqLevel']
		return 0

	def getTeachNextLevel( self, player ):
		"""
		获要学习的技能的等级
		"""
		tSkillID = self.getNextSkillID()
		level = Skill.getSkill( tSkillID ).getLevel()
		if self.getTeachMaxLevel() < level:
			return self.getTeachMaxLevel()
		return level
	
	def getNextSkillID( self ):
		"""
		获取下一级技能id
		"""
		tSkillID = self.getMapSkillID( self._SkillsMap )					# 获取玩家身上存在的该技能
		if tSkillID:
			if g_skillDatas.has_key( tSkillID ):
				skTeachData = g_skillDatas[tSkillID]
				nextSkId = skTeachData["nextLevelID"]
				if nextSkId == 0:						#最大等级的 nextLevelID 为0
					nextSkId = tSkillID
				return nextSkId
		return self._spellTeach

	def getTeachMaxLevel( self ):
		"""
		取学习技能最大等级
		"""
		return self._skillLevelMax

	def getSkillDsp( self ):
		"""
		获取当前玩家学习技能对应的技能描述
		"""
		try:
			player = BigWorld.player()
			teach_skill_level = self.getTeachNextLevel( player )					#获取当前学习技能的等级
			teach_skill_id = self.getNextSkillID()#通过等级得取技能对应的技能ID
			skill = Skill.getSkill( teach_skill_id )								#通过ID得到技能，并得到描述
			skill_dsp = skill.getDescription()
			return skill_dsp
		except:
			return ""

	def getTeach( self ):
		return self._spellTeach

	def getReqSkills( self ):
		"""
		获取学习技能所需要的前置技能
		"""
		if not self._reqSkillsMap :
			return set( self._reqSkills )
		skillHeld = self.getMapSkillID( self._SkillsMap )
		if skillHeld is 0 : skillHeld = self._spellTeach
		return self.filterReqSkills_( skillHeld )

	def getReqMetier( self ):
		"""
		获取学习当前技能所需职业#define  in  csconst.py--->g_map_class
		"""
		return self._reqMetier

	def getFirstReqLevel( self ):
		if g_skillDatas.has_key( self._spellTeach ):
			return g_skillDatas[ self._spellTeach ]['ReqLevel']
		return 0

	def getReqLevel( self ):
		if g_skillDatas.has_key( self.getNextSkillID() ):
			return g_skillDatas[ self.getNextSkillID() ]['ReqLevel']
		return 0

	def getCost( self ):
		if g_skillDatas.has_key( self.getNextSkillID() ):
			return g_skillDatas[ self.getNextSkillID() ]['ReqMoney']
		return 0

	def getIcon( self ):
		sk = Skill.getSkill( self._spellTeach )
		if sk is None:
			return ""
		return sk.getIcon()

	def checkMetier( self ):
		"""
		检查职业
		@return BOOL
		"""
		player = BigWorld.player()
		if self._reqMetier != "":
			return player.isRaceclass( csconst.g_map_class[self._reqMetier], csdefine.RCMASK_CLASS )
		else:		#没职业限制
			return True

	def checkLevel( self ):
		"""
		检查等级
		@return BOOL
		"""
		player = BigWorld.player()
		return player.level >= self.getNeedPlayerLevel()

	def checkMoney( self ):
		"""
		检查金钱
		@return BOOL
		"""
		player = BigWorld.player()
		return player.money >= self.getCost()

	def checkPotential( self ):
		"""
		检查潜能点
		@return BOOL
		"""
		player = BigWorld.player()
		needPotential = self.getPotential( player )
		return player.potential >= needPotential

	def checkPremissSkill( self ):
		"""
		检查前置技能
		@return BOOL
		"""
		for reSkillID in self.getReqSkills() :
			_reSkillsMap = self.getSkillsMap( reSkillID )
			if not self.getMapSkillID( _reSkillsMap ):
				return False
		return True

	def checkHasLearnt( self, trainer = None ):
		"""
		检测是否在NPC学过该技能
		"""
		tSkillID = self.getNextSkillID()
		return not tSkillID in self._spellTeachs
		
	def islearnMax( self, trainer = None ):
		"""
		是否学会最高级了，普通技能在NPC学到1级
		"""
		
		return BigWorld.player().hasSkill( self._maxSkillID )
	
	def learnable( self ):
		"""
		判断指定玩家是否符合学习此技能的条件(金钱要求除外)

		@return: BOOL
		"""
		player = BigWorld.player()
		# 职业不一样
		if not self.checkMetier():
			return StatusMsgs.getStatusInfo( csstatus.LEARN_SKILL_METIER_DIFFER ).msg

		# 等级需求
		if not self.checkLevel():
			return StatusMsgs.getStatusInfo( csstatus.LEARN_SKILL_NEED_LEVEL ).msg

		# 是否已在技能导师处学过该技能
		if self.checkHasLearnt():
			return StatusMsgs.getStatusInfo( csstatus.LEARN_SKILL_LEVEL_FULL ).msg
		# 是否有要求技能
		if not self.checkPremissSkill():
			return StatusMsgs.getStatusInfo( csstatus.LEARN_SKILL_NEED_OTHER_SKILL ).msg
		return None

class Spell_Pet_TeachBook( Spell ):
	"""
	宠物技能学习书
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		初始化技能实例。
		@param dict:			技能配置字典数据
		@type dict:				Python dict
		"""
		Spell.init( self, dict )

	def getLearnSkill( self ):
		"""
		获得该学习技能学习的技能的ID
		"""
		return self._datas[ "param1" ]			# 吟唱时间

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
		初始化技能实例。
		@param section:	技能配置
		@type  section:	Python dict
		"""
		Spell_Teach.init( self, dict )
		#学习需求
		# 注释掉这行是因为玩家可以看到这个技能学习的时候帮会建筑等级必须已经达到
		#self.buildingLv = dict[ "buildingLv" ]				# 帮会建筑 研究院等级
		#self.tongContribute = dict[ "tongContribute" ]			# 帮会建筑 研究院等级

	def getReqTongContribute( self ):
		"""
		获要学习的技能的帮会贡献度
		"""
		skillID = self._spellTeach - Skill.getSkill( self._spellTeach ).getLevel() + self.getTeachNextLevel( BigWorld.player())
		if g_skillDatas.has_key( skillID ):
			return g_skillDatas[skillID]['tongContribute']
		return 0

	def checkMetier( self ):
		"""
		检查职业
		@return BOOL
		"""
		if self._reqMetier == "":
			return True
		return Spell_Teach.checkMetier( self )

	def checkContribute( self ):
		"""
		检查帮会贡献度
		@return BOOL
		"""
		player = BigWorld.player()
		playerMember = player.tong_memberInfos.get( player.databaseID, None )
		if playerMember is None:return
		contribute = playerMember.getContribute()
		return contribute >= self.getReqTongContribute()

	def learnable( self ):
		"""
		学习帮会技能判断
		"""
		if not self.checkContribute():
			contribute = self.getReqTongContribute()
			return StatusMsgs.getStatusInfo( csstatus.TONG_LEARN_SKILL_REP_CONTRIBUTE, contribute ).msg
		return None

	def islearnMax( self, trainer ):
		if trainer is None: return False
		curID = self.getID()
		curLevel = self.getCurLevel( curID ) #角色身上该技能等级
		if curLevel <= 0:return False
		for skillInfo in trainer.skillInfos:
			skillID = skillInfo["id"]
			skillLevel = skillInfo["level"]
			if skillID == curID and curLevel >= skillLevel:
				return True
		return False

	def getCurLevel( self, skillID ):
		skillList = BigWorld.player().skillList_
		for skill in skillList:
			if str( skillID )[1:-1] == str( skill )[:-1]:
				return int( str( skill )[-1] )
		return -1
	
	def checkHasLearnt( self, trainer ):
		if trainer is None:return True
		curID = self.getID()
		curLevel = self.getCurLevel( curID )	#角色身上该技能等级
		for skillInfo in trainer.skillInfos:
			skillID = skillInfo["id"]
			skillLevel = skillInfo["level"]
			if skillID == curID and skillLevel >= curLevel:
				return False
		return True

class Spell_VehicleTeach( Spell_Teach ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Spell_Teach.__init__( self )

	def init( self, dict ):
		"""
		"""
		Spell_Teach.init( self, dict )

	def checkMetier( self ):
		"""
		检查职业
		@return BOOL
		"""
		if self._reqMetier == "":
			return True
		return Spell_Teach.checkMetier( self )

	def checkLevel( self ):
		"""
		检查等级
		@return BOOL
		"""
		player = BigWorld.player()
		vLevel = player.getVehicleLevel()
		return vLevel >= self.getNeedVehicleLevel()

	def islearnMax( self, trainer = None ) :
		"""
		检查是否已到顶级
		"""
		player = BigWorld.player()
		vehicleSkills = player.getVehicleSkills( player.vehicleDBID )
		return ( self.getTeach() + self.getTeachMaxLevel() - Skill.getSkill( self._spellTeach ).getLevel() ) in vehicleSkills

	def learnable( self ) :
		"""
		学习技能条件判断
		"""
		player = BigWorld.player()
		if player.vehicleDBID == 0:
			return StatusMsgs.getStatusInfo( csstatus.LEARN_SKILL_MUST_CALL_VEHICLE ).msg
		if not self.checkMetier():
			return StatusMsgs.getStatusInfo( csstatus.VEHICLE_LEARN_SKILL_METIER_WRONG ).msg

		# 等级需求
		if not self.checkLevel():
			return StatusMsgs.getStatusInfo( csstatus.VEHICLE_LEARN_SKILL_NEED_LEVEL ).msg

		# 是否已学会技能最高级
		if self.islearnMax():
			return StatusMsgs.getStatusInfo( csstatus.VEHICLE_LEARN_SKILL_MAX_LEVEL, self.getName() ).msg

		# 是否有要求技能
		if not self.checkPremissSkill():
			return StatusMsgs.getStatusInfo( csstatus.VEHICLE_NEED_OTHER_SKILL ).msg
		return None

	def getMapSkillID( self, hasMap ):
		"""
		是否有技能映射表里的技能
		@param  hsMap: 技能映射表
		@type   hsMap: set
		"""
		player = BigWorld.player()
		vehicleSkills = player.getVehicleSkills( player.vehicleDBID )
		for skillID in vehicleSkills :
			if skillID in hasMap :
				return skillID
		return 0

	def getNeedPlayerLevel( self ):
		"""
		当前骑宠技能对玩家等级没有要求
		"""
		return 0

	def getNeedVehicleLevel( self ) :
		"""
		获取需要的骑宠等级
		"""
		skillID = self._spellTeach - Skill.getSkill( self._spellTeach ).getLevel() + self.getTeachNextLevel( None )
		if g_skillDatas.has_key( skillID ):
			return g_skillDatas[skillID]['ReqLevel']
		return 0

	def checkPotential( self ) :
		"""
		需要的骑宠技能点
		"""
		player = BigWorld.player()
		if player.vehicleDBID == 0: return False

		data = player.vehicleDatas.get( player.vehicleDBID )
		if data is None: return

		skPoint = data["skPoint"]
		needSKPoint = self.getPotential( None )
		return skPoint >= needSKPoint

class Spell_VehicleTeachBook( Spell_VehicleTeach ):
	"""
	通过书本学习骑宠技能 by姜毅
	"""
	def __init__( self ):
		"""
		"""
		Spell_VehicleTeach.__init__( self )

	def init( self, dict ):
		"""
		"""
		Spell_VehicleTeach.init( self, dict )

class Spell_TeachTongPetSkill( Spell_TeachTongSkill ):
	"""
	帮会宠物技能学习
	"""
	def getReqTongContribute( self ):
		"""
		获要学习的技能的帮会贡献度
		"""
		skillID = self._spellTeach - Skill.getSkill( self._spellTeach ).getLevel() + self.getTeachNextLevel( BigWorld.player() )
		if g_skillDatas.has_key( skillID ):
			return g_skillDatas[skillID]['tongContribute']
		return 0

	def checkMetier( self ):
		"""
		检查职业
		@return BOOL
		"""
		if self._reqMetier == "":
			return True

		petEntity = BigWorld.player().pcg_getActPet()
		return petEntity and petEntity.isRaceclass( csconst.g_map_class[self._reqMetier], csdefine.RCMASK_CLASS )

	def checkContribute( self ):
		"""
		检查帮会贡献度
		@return BOOL
		"""
		player = BigWorld.player()
		playerMember = player.tong_memberInfos.get( player.databaseID, None )
		if playerMember is None:return
		contribute = playerMember.getContribute()
		return contribute >= self.getReqTongContribute()

	def islearnMax( self, trainer ):
		if trainer is None: return False
		curID = self.getID()
		curLevel = self.getCurLevel( curID ) #角色身上该技能等级
		if curLevel <= 0:return False
		for skillInfo in trainer.skillInfos:
			skillID = skillInfo["id"]
			skillLevel = skillInfo["level"]
			if skillID == curID and curLevel >= skillLevel:
				return True
		return False

	def getCurLevel( self, skillID ):
		skillList = BigWorld.player().pcg_getPetSkillList()
		for skill in skillList:
			if str( skillID )[1:-1] == str( skill )[:-1]:
				return int( str( skill )[-1] )
		return -1

	def getMapSkillID( self, hasMap ):
		"""
		是否有技能映射表里的技能
		@param  hsMap: 技能映射表
		@type   hsMap: set
		"""
		for skillID in BigWorld.player().pcg_getPetSkillList():
			if skillID in hasMap:
				return skillID
		return 0

	def getTeachNextLevel( self, player ):
		"""
		获要学习的技能的等级
		"""
		tSkillID = self.getMapSkillID( self._SkillsMap )					# 获取宠物身上存在的该技能
		if tSkillID:														# 说明该技能宠物已经学过
			currSkill = Skill.getSkill( tSkillID )
			level = currSkill.getLevel() + 1
			if self.getTeachMaxLevel() < level:
				return self.getTeachMaxLevel()
			return level
		return Skill.getSkill( self._spellTeach ).getLevel() + 1			# 说明该技能玩家还没学过，宠物天赋技能在帮会中只能升级，从2级开始

	def learnable( self ):
		"""
		"""
		if BigWorld.player().pcg_getActPet() is None :						# 没有出战宠物
			return StatusMsgs.getStatusInfo( csstatus.PET_EVOLVE_FAIL_NOT_CONJURED ).msg
		if not self.checkMetier() :											# 职业不符
			return StatusMsgs.getStatusInfo( csstatus.PET_LEARN_SKILL_METIER_DIFFER ).msg
		# 至少有要一级技能
		if self.getMapSkillID( self._SkillsMap ) == 0:
			return StatusMsgs.getStatusInfo( csstatus.PET_LEARN_SKILL_NOT_LEARN ).msg

		if not self.checkContribute():
			contribute = self.getReqTongContribute()
			return StatusMsgs.getStatusInfo( csstatus.TONG_LEARN_SKILL_REP_CONTRIBUTE, contribute ).msg
		return None
#
# $Log: not supported by cvs2svn $
# Revision 1.5  2008/01/31 07:50:08  kebiao
# 修改打开界面弹出信息BUG
#
# Revision 1.4  2008/01/29 05:56:11  kebiao
# 修改了技能学习相关BUG 修改了配置
#
# Revision 1.3  2008/01/15 06:54:41  kebiao
# add:getFirstReqLevel 提供外部查询第一级等级需求
#
# Revision 1.2  2008/01/12 07:48:40  kebiao
# 修改学习条件
#
# Revision 1.1  2008/01/05 03:48:19  kebiao
# no message
#
#
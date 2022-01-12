# -*- coding: gb18030 -*-
#
# $Id: Spell_Teach.py,v 1.6 2008-07-15 04:08:27 kebiao Exp $

"""
SpellTeach�����ࡣ
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
from SkillTeachLoader import g_skillTeachDatas		# ����ѧϰ���ݹ���
g_skillDatas = g_skillTeachDatas._datas
from config.skill.Skill.SkillDataMgr import Datas as skDatas

class Spell_Teach( Spell ):
	"""
	ѵ�������������������ڼ���ѵ��������ʾ���в�����
	"""
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Spell.__init__( self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def filterReqSkills_( self, skillId ) :
		"""
		��ȡҪѧϰID��skillId�ļ��ܣ�����Ҫ������ǰ�ü��ܡ�
		skillId������ָ�����ܵȼ��ģ���Ϊ��ǰ��ͬ�ȼ��ļ�
		�ܣ�������Ҫ��ǰ�ü��ܿ��ܲ���ͬ�����磺
		5�����ķ�֧��1-9��˫�ش����
		6�����ķ�֧��1-24��˫�ش����
		7�����ķ�֧��1-39��˫�ش����
		��˲�ͬ�ȼ���˫�ش�����ܾ���Ҫ��ͬ�ȼ��Ŀ��ķ�
		"""
		try :
			candidates = [ skId for skId in self._reqSkills \
				if self._reqSkillsMap[skId] > skillId ]						# ע�⣬_reqSkills��������������
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
		��ȡ��������
		@param dict:			���������ֵ�����
		@type dict:				Python dict
		"""
		Spell.init( self, dict )
		#ѧϰ����
		tmpReqSkills = set()						# ���輼�ܣ����û������()
		self._reqSkillsMap = {}
		#���ܵ�1��ѧϰ����
		self._reqMetier = dict[ "param2" ]			# ����ְҵ�����û������""
		for skillID in dict["param3"].split( ";" ) :	# ���ǰ�ü����Էֺŷָ�
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
		self._spellTeach = sorted( self._spellTeachs )[0]# ���ڵ�1������ID
		self._skillLevelMax = int( dict["param4"] )		# ���ܵ����ȼ�
		# ��ӳ��
		self._SkillsMap = self.getSkillsMap( self._spellTeach )
		self._maxSkillID = sorted( self._SkillsMap )[-1]
		
	def getMapSkillID( self, hasMap ):
		"""
		�Ƿ��м���ӳ�����ļ���
		@param  hsMap: ����ӳ���
		@type   hsMap: set
		"""
		player = BigWorld.player()
		for skillID in player.getSkillList():
			if skillID in hasMap:
				return skillID
		return 0
	
	def getSkillsMap( self, skillID ):
		"""
		��ȡѧϰ���ܶ�Ӧ�����м���
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
		����Ǳ�ܵ�
		@param player:	���ʵ��
		@type player:	entity
		"""
		if g_skillDatas.has_key( self.getNextSkillID() ):
			return g_skillDatas[ self.getNextSkillID() ]['ReqPotential']
		return 0

	def getTeachSkillMap( self ):
		"""
		Ҫѧϰ���ܵ��б�
		"""
		return self._SkillsMap

	def getNeedPlayerLevel( self ):
		"""
		��ȡ��ǰ���ܵȼ���Ӧ��������ҵȼ�
		"""
		if g_skillDatas.has_key( self.getNextSkillID() ):
			return g_skillDatas[ self.getNextSkillID() ]['ReqLevel']
		return 0

	def getTeachNextLevel( self, player ):
		"""
		��Ҫѧϰ�ļ��ܵĵȼ�
		"""
		tSkillID = self.getNextSkillID()
		level = Skill.getSkill( tSkillID ).getLevel()
		if self.getTeachMaxLevel() < level:
			return self.getTeachMaxLevel()
		return level
	
	def getNextSkillID( self ):
		"""
		��ȡ��һ������id
		"""
		tSkillID = self.getMapSkillID( self._SkillsMap )					# ��ȡ������ϴ��ڵĸü���
		if tSkillID:
			if g_skillDatas.has_key( tSkillID ):
				skTeachData = g_skillDatas[tSkillID]
				nextSkId = skTeachData["nextLevelID"]
				if nextSkId == 0:						#���ȼ��� nextLevelID Ϊ0
					nextSkId = tSkillID
				return nextSkId
		return self._spellTeach

	def getTeachMaxLevel( self ):
		"""
		ȡѧϰ�������ȼ�
		"""
		return self._skillLevelMax

	def getSkillDsp( self ):
		"""
		��ȡ��ǰ���ѧϰ���ܶ�Ӧ�ļ�������
		"""
		try:
			player = BigWorld.player()
			teach_skill_level = self.getTeachNextLevel( player )					#��ȡ��ǰѧϰ���ܵĵȼ�
			teach_skill_id = self.getNextSkillID()#ͨ���ȼ���ȡ���ܶ�Ӧ�ļ���ID
			skill = Skill.getSkill( teach_skill_id )								#ͨ��ID�õ����ܣ����õ�����
			skill_dsp = skill.getDescription()
			return skill_dsp
		except:
			return ""

	def getTeach( self ):
		return self._spellTeach

	def getReqSkills( self ):
		"""
		��ȡѧϰ��������Ҫ��ǰ�ü���
		"""
		if not self._reqSkillsMap :
			return set( self._reqSkills )
		skillHeld = self.getMapSkillID( self._SkillsMap )
		if skillHeld is 0 : skillHeld = self._spellTeach
		return self.filterReqSkills_( skillHeld )

	def getReqMetier( self ):
		"""
		��ȡѧϰ��ǰ��������ְҵ#define  in  csconst.py--->g_map_class
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
		���ְҵ
		@return BOOL
		"""
		player = BigWorld.player()
		if self._reqMetier != "":
			return player.isRaceclass( csconst.g_map_class[self._reqMetier], csdefine.RCMASK_CLASS )
		else:		#ûְҵ����
			return True

	def checkLevel( self ):
		"""
		���ȼ�
		@return BOOL
		"""
		player = BigWorld.player()
		return player.level >= self.getNeedPlayerLevel()

	def checkMoney( self ):
		"""
		����Ǯ
		@return BOOL
		"""
		player = BigWorld.player()
		return player.money >= self.getCost()

	def checkPotential( self ):
		"""
		���Ǳ�ܵ�
		@return BOOL
		"""
		player = BigWorld.player()
		needPotential = self.getPotential( player )
		return player.potential >= needPotential

	def checkPremissSkill( self ):
		"""
		���ǰ�ü���
		@return BOOL
		"""
		for reSkillID in self.getReqSkills() :
			_reSkillsMap = self.getSkillsMap( reSkillID )
			if not self.getMapSkillID( _reSkillsMap ):
				return False
		return True

	def checkHasLearnt( self, trainer = None ):
		"""
		����Ƿ���NPCѧ���ü���
		"""
		tSkillID = self.getNextSkillID()
		return not tSkillID in self._spellTeachs
		
	def islearnMax( self, trainer = None ):
		"""
		�Ƿ�ѧ����߼��ˣ���ͨ������NPCѧ��1��
		"""
		
		return BigWorld.player().hasSkill( self._maxSkillID )
	
	def learnable( self ):
		"""
		�ж�ָ������Ƿ����ѧϰ�˼��ܵ�����(��ǮҪ�����)

		@return: BOOL
		"""
		player = BigWorld.player()
		# ְҵ��һ��
		if not self.checkMetier():
			return StatusMsgs.getStatusInfo( csstatus.LEARN_SKILL_METIER_DIFFER ).msg

		# �ȼ�����
		if not self.checkLevel():
			return StatusMsgs.getStatusInfo( csstatus.LEARN_SKILL_NEED_LEVEL ).msg

		# �Ƿ����ڼ��ܵ�ʦ��ѧ���ü���
		if self.checkHasLearnt():
			return StatusMsgs.getStatusInfo( csstatus.LEARN_SKILL_LEVEL_FULL ).msg
		# �Ƿ���Ҫ����
		if not self.checkPremissSkill():
			return StatusMsgs.getStatusInfo( csstatus.LEARN_SKILL_NEED_OTHER_SKILL ).msg
		return None

class Spell_Pet_TeachBook( Spell ):
	"""
	���＼��ѧϰ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ʼ������ʵ����
		@param dict:			���������ֵ�����
		@type dict:				Python dict
		"""
		Spell.init( self, dict )

	def getLearnSkill( self ):
		"""
		��ø�ѧϰ����ѧϰ�ļ��ܵ�ID
		"""
		return self._datas[ "param1" ]			# ����ʱ��

class Spell_TeachTongSkill( Spell_Teach ):
	"""
	��Ἴ��ѧϰ
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Teach.__init__( self )

	def init( self, dict ):
		"""
		��ʼ������ʵ����
		@param section:	��������
		@type  section:	Python dict
		"""
		Spell_Teach.init( self, dict )
		#ѧϰ����
		# ע�͵���������Ϊ��ҿ��Կ����������ѧϰ��ʱ���Ὠ���ȼ������Ѿ��ﵽ
		#self.buildingLv = dict[ "buildingLv" ]				# ��Ὠ�� �о�Ժ�ȼ�
		#self.tongContribute = dict[ "tongContribute" ]			# ��Ὠ�� �о�Ժ�ȼ�

	def getReqTongContribute( self ):
		"""
		��Ҫѧϰ�ļ��ܵİ�ṱ�׶�
		"""
		skillID = self._spellTeach - Skill.getSkill( self._spellTeach ).getLevel() + self.getTeachNextLevel( BigWorld.player())
		if g_skillDatas.has_key( skillID ):
			return g_skillDatas[skillID]['tongContribute']
		return 0

	def checkMetier( self ):
		"""
		���ְҵ
		@return BOOL
		"""
		if self._reqMetier == "":
			return True
		return Spell_Teach.checkMetier( self )

	def checkContribute( self ):
		"""
		����ṱ�׶�
		@return BOOL
		"""
		player = BigWorld.player()
		playerMember = player.tong_memberInfos.get( player.databaseID, None )
		if playerMember is None:return
		contribute = playerMember.getContribute()
		return contribute >= self.getReqTongContribute()

	def learnable( self ):
		"""
		ѧϰ��Ἴ���ж�
		"""
		if not self.checkContribute():
			contribute = self.getReqTongContribute()
			return StatusMsgs.getStatusInfo( csstatus.TONG_LEARN_SKILL_REP_CONTRIBUTE, contribute ).msg
		return None

	def islearnMax( self, trainer ):
		if trainer is None: return False
		curID = self.getID()
		curLevel = self.getCurLevel( curID ) #��ɫ���ϸü��ܵȼ�
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
		curLevel = self.getCurLevel( curID )	#��ɫ���ϸü��ܵȼ�
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
		���ְҵ
		@return BOOL
		"""
		if self._reqMetier == "":
			return True
		return Spell_Teach.checkMetier( self )

	def checkLevel( self ):
		"""
		���ȼ�
		@return BOOL
		"""
		player = BigWorld.player()
		vLevel = player.getVehicleLevel()
		return vLevel >= self.getNeedVehicleLevel()

	def islearnMax( self, trainer = None ) :
		"""
		����Ƿ��ѵ�����
		"""
		player = BigWorld.player()
		vehicleSkills = player.getVehicleSkills( player.vehicleDBID )
		return ( self.getTeach() + self.getTeachMaxLevel() - Skill.getSkill( self._spellTeach ).getLevel() ) in vehicleSkills

	def learnable( self ) :
		"""
		ѧϰ���������ж�
		"""
		player = BigWorld.player()
		if player.vehicleDBID == 0:
			return StatusMsgs.getStatusInfo( csstatus.LEARN_SKILL_MUST_CALL_VEHICLE ).msg
		if not self.checkMetier():
			return StatusMsgs.getStatusInfo( csstatus.VEHICLE_LEARN_SKILL_METIER_WRONG ).msg

		# �ȼ�����
		if not self.checkLevel():
			return StatusMsgs.getStatusInfo( csstatus.VEHICLE_LEARN_SKILL_NEED_LEVEL ).msg

		# �Ƿ���ѧ�Ἴ����߼�
		if self.islearnMax():
			return StatusMsgs.getStatusInfo( csstatus.VEHICLE_LEARN_SKILL_MAX_LEVEL, self.getName() ).msg

		# �Ƿ���Ҫ����
		if not self.checkPremissSkill():
			return StatusMsgs.getStatusInfo( csstatus.VEHICLE_NEED_OTHER_SKILL ).msg
		return None

	def getMapSkillID( self, hasMap ):
		"""
		�Ƿ��м���ӳ�����ļ���
		@param  hsMap: ����ӳ���
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
		��ǰ��輼�ܶ���ҵȼ�û��Ҫ��
		"""
		return 0

	def getNeedVehicleLevel( self ) :
		"""
		��ȡ��Ҫ�����ȼ�
		"""
		skillID = self._spellTeach - Skill.getSkill( self._spellTeach ).getLevel() + self.getTeachNextLevel( None )
		if g_skillDatas.has_key( skillID ):
			return g_skillDatas[skillID]['ReqLevel']
		return 0

	def checkPotential( self ) :
		"""
		��Ҫ����輼�ܵ�
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
	ͨ���鱾ѧϰ��輼�� by����
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
	�����＼��ѧϰ
	"""
	def getReqTongContribute( self ):
		"""
		��Ҫѧϰ�ļ��ܵİ�ṱ�׶�
		"""
		skillID = self._spellTeach - Skill.getSkill( self._spellTeach ).getLevel() + self.getTeachNextLevel( BigWorld.player() )
		if g_skillDatas.has_key( skillID ):
			return g_skillDatas[skillID]['tongContribute']
		return 0

	def checkMetier( self ):
		"""
		���ְҵ
		@return BOOL
		"""
		if self._reqMetier == "":
			return True

		petEntity = BigWorld.player().pcg_getActPet()
		return petEntity and petEntity.isRaceclass( csconst.g_map_class[self._reqMetier], csdefine.RCMASK_CLASS )

	def checkContribute( self ):
		"""
		����ṱ�׶�
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
		curLevel = self.getCurLevel( curID ) #��ɫ���ϸü��ܵȼ�
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
		�Ƿ��м���ӳ�����ļ���
		@param  hsMap: ����ӳ���
		@type   hsMap: set
		"""
		for skillID in BigWorld.player().pcg_getPetSkillList():
			if skillID in hasMap:
				return skillID
		return 0

	def getTeachNextLevel( self, player ):
		"""
		��Ҫѧϰ�ļ��ܵĵȼ�
		"""
		tSkillID = self.getMapSkillID( self._SkillsMap )					# ��ȡ�������ϴ��ڵĸü���
		if tSkillID:														# ˵���ü��ܳ����Ѿ�ѧ��
			currSkill = Skill.getSkill( tSkillID )
			level = currSkill.getLevel() + 1
			if self.getTeachMaxLevel() < level:
				return self.getTeachMaxLevel()
			return level
		return Skill.getSkill( self._spellTeach ).getLevel() + 1			# ˵���ü�����һ�ûѧ���������츳�����ڰ����ֻ����������2����ʼ

	def learnable( self ):
		"""
		"""
		if BigWorld.player().pcg_getActPet() is None :						# û�г�ս����
			return StatusMsgs.getStatusInfo( csstatus.PET_EVOLVE_FAIL_NOT_CONJURED ).msg
		if not self.checkMetier() :											# ְҵ����
			return StatusMsgs.getStatusInfo( csstatus.PET_LEARN_SKILL_METIER_DIFFER ).msg
		# ������Ҫһ������
		if self.getMapSkillID( self._SkillsMap ) == 0:
			return StatusMsgs.getStatusInfo( csstatus.PET_LEARN_SKILL_NOT_LEARN ).msg

		if not self.checkContribute():
			contribute = self.getReqTongContribute()
			return StatusMsgs.getStatusInfo( csstatus.TONG_LEARN_SKILL_REP_CONTRIBUTE, contribute ).msg
		return None
#
# $Log: not supported by cvs2svn $
# Revision 1.5  2008/01/31 07:50:08  kebiao
# �޸Ĵ򿪽��浯����ϢBUG
#
# Revision 1.4  2008/01/29 05:56:11  kebiao
# �޸��˼���ѧϰ���BUG �޸�������
#
# Revision 1.3  2008/01/15 06:54:41  kebiao
# add:getFirstReqLevel �ṩ�ⲿ��ѯ��һ���ȼ�����
#
# Revision 1.2  2008/01/12 07:48:40  kebiao
# �޸�ѧϰ����
#
# Revision 1.1  2008/01/05 03:48:19  kebiao
# no message
#
#
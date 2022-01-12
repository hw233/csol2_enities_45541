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
from Resource.SkillTeachLoader import g_skillTeachDatas		# ����ѧϰ���ݹ���
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
		���캯����
		"""
		Spell.__init__( self )
		self._reqSkills = set([])			# ���輼�ܣ����û������()
		self._spellTeachs = set([])

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )

		####################################
		#ѧϰ����
		#���ܵ�1��ѧϰ����
		#self._reqLevel = dict.readInt( "ReqLevel" )				# ����ȼ������û������0
		self._reqMetier = ( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else "" ) 				# ����ְҵ�����û������""
		if len( ( dict["param3"] if len( dict["param3"] ) > 0 else "" )  ) > 0:
			self._reqSkills = set([int(e) for e in ( dict["param3"] if len( dict["param3"] ) > 0 else "" ) .split(";")])
		# ���ڵ�1������ID
		self._skillLevelMax = int( dict["param4"] if len( dict["param4"] ) > 0 else 0 ) 			# ���ܵ����ȼ�
		if len( ( dict["param1"] if len( dict["param1"] ) > 0 else "" )  ) > 0:
			self._spellTeachs = set([int(e) for e in ( dict["param1"] if len( dict["param1"] ) > 0 else "" ) .split(";")])
		self._spellTeach = sorted( self._spellTeachs )[0]
		# ��ӳ��
		self._SkillsMap = self.getSkillsMap( self._spellTeach )

	def getSkillsMap( self, skillID ):
		"""
		��ȡѧϰ���ܶ�Ӧ�����м���
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
		�ж��Ƿ���skillIDs����hsMap�д��ڵļ���ID
		@type skillIDs: array
		@type    hsMap: set
		"""
		for skillID in skillIDs:
			if skillID in hsMap:
				return skillID
		return 0
	
	def getNextSkillID( self, tSkillID ):
		"""
		��ȡ��һ������id
		"""
		if g_skillDatas.has_key( tSkillID ):
			skTeachData = g_skillDatas[tSkillID]
			nextSkId = skTeachData["nextLevelID"]
			if nextSkId == 0:						#���ȼ��� nextLevelID Ϊ0
				nextSkId = tSkillID
			return nextSkId
		return self._spellTeach

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# ְҵ��һ��
		if self._reqMetier != "" and not receiver.isRaceclass( csconst.g_map_class[self._reqMetier], csdefine.RCMASK_CLASS ):
			INFO_MSG( "%s(%i): learn skill %i, metier differ." % (receiver.playerName, receiver.id, self._spellTeach) )
			receiver.statusMessage( csstatus.LEARN_SKILL_METIER_DIFFER )
			return

		# �Ƿ��и����͵ļ���
		skillID = self.hasMapSkill( receiver.getSkills(), self._SkillsMap )
		ifUpdate = skillID != 0
		# �ȼ����
		nextSkillID = 0
		if ifUpdate:
			if Skill[skillID].getLevel() >= self._skillLevelMax:
				INFO_MSG( "%s(%i): learn skill %i, skill is max level." % (receiver.playerName, receiver.id, self._spellTeach) )
				receiver.statusMessage( csstatus.LEARN_SKILL_MAX_LEVEL, self.getName() )
				return
			nextSkillID = self.getNextSkillID( skillID )
		else:
			nextSkillID = self._spellTeach

		# Ҫ��ȼ�
		if nextSkillID != 0 and receiver.level < g_skillTeachDatas[ nextSkillID ]['ReqLevel']:
			INFO_MSG( "%s(%i): learn skill %i, level %i need." % (receiver.playerName, receiver.id, self._spellTeach, g_skillTeachDatas[ nextSkillID ]['ReqLevel']) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_LEVEL )
			return

		# �Ƿ���Ҫ����
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

		# ��Ǯ
		money = g_skillTeachDatas[ nextSkillID ]['ReqMoney']
		if not receiver.payMoney( money, csdefine.CHANGE_MONEY_LEARN_SKILL ):
			INFO_MSG( "%s(%i): learn skill %i, money %i need." % (receiver.playerName, receiver.id, self._spellTeach, g_skillTeachDatas[ skillID ]['ReqMoney']) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_MONEY )
			return

		# ��Ǳ�ܵ�
		receiver.payPotential( potential )

		if ifUpdate:		# �������������ɾ��ԭ�ȼ�����
			receiver.setTemp( "roleUpdateSkill", True )
			if receiver.updateSkill( skillID, nextSkillID ):
				receiver.questSkillLearned( nextSkillID )
			try:
				g_logger.skillUpgradeLog( receiver.databaseID, receiver.getName(), nextSkillID, skillID, potential,money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
				
			receiver.removeTemp( "roleUpdateSkill" )
		else:			# ��Ӽ���
			if receiver.addSkill( self._spellTeach ):
				receiver.questSkillLearned( nextSkillID )
			try:
				g_logger.skillLearnLog( receiver.databaseID, receiver.getName(), nextSkillID, potential, money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

class Spell_Teach_MutLevel_Limit( Spell, Spell_Teach ):
	"""
	�ж��ȼ����Ƶļ���ѧϰ��ʽ by ����
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self._reqSkills = {}			# ���輼�ܣ����û������()
		self._reqSk = []
		
	def init( self, dict ):
		"""
		"""
		Spell.init( self, dict )
		####################################
		#ѧϰ����
		#���ܵ�1��ѧϰ����
		#self._reqLevel = dict.readInt( "ReqLevel" )				# ����ȼ������û������0
		self._reqMetier = ( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else "" ) 				# ����ְҵ�����û������""
		if len( ( dict["param3"] if len( dict["param3"] ) > 0 else "" )  ) > 0:
			_reqSkills = set([e for e in ( dict["param3"] if len( dict["param3"] ) > 0 else "" ) .split(";")])
			self.__paramCheck( _reqSkills )
			for rSkill in _reqSkills:
				if rSkill == "":continue
				rs = rSkill.split(":")
				self._reqSkills[int(rs[0])] = int(rs[1])		# 0 ����ǰ�ü��� 1 ��Ӧѧ�õ����ȼ��ļ���
		self._reqSk = self._reqSkills.keys()
		self._reqSk.sort()

		self._skillLevelMax = int( dict["param4"] if len( dict["param4"] ) > 0 else 0 ) 			# ���ܵ����ȼ�
		if len( ( dict["param1"] if len( dict["param1"] ) > 0 else "" )  ) > 0:
			self._spellTeachs = set([int(e) for e in ( dict["param1"] if len( dict["param1"] ) > 0 else "" ) .split(";")])
		self._spellTeach = sorted( self._spellTeachs )[0]
		# ��ӳ��
		self._SkillsMap = self.getSkillsMap( self._spellTeach )

	def __paramCheck( self, param ):
		"""
		�������
		"""
		skillIDs = []
		for rSkill in param:
			if rSkill == "":continue
			rs = rSkill.split(":")
			skID1 = int(rs[0])
			skID2 = int(rs[1])
			if skID1 in skillIDs:
				ERROR_MSG( "skillID( %i ) configuration is wrong: %i." % ( self.getID(), skID1 ) )   # ǰ�ü������ô���
			else:
				skillIDs.append( skID1 )
			if skID2 in skillIDs:
				ERROR_MSG( "skillID( %i ) configuration is wrong: %i." % ( self.getID(), skID2 ) )   # ǰ�ü������ô���
			else:
				skillIDs.append( skID2)

	def learnMapSkill( self, skillIDs, hsMap ):
		"""
		�ж��Ƿ���skillIDs����hsMap�д��ڵļ���ID
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
		��ȡ��һ������id
		"""
		if g_skillDatas.has_key( tSkillID ):
			skTeachData = g_skillDatas[tSkillID]
			nextSkId = skTeachData["nextLevelID"]
			if nextSkId == 0:						#���ȼ��� nextLevelID Ϊ0
				nextSkId = tSkillID
			return nextSkId
		return self._spellTeach

	def getSkillsMap( self, skillID ):
		"""
		��ȡѧϰ���ܶ�Ӧ�����м���
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
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		# ְҵ��һ��
		if self._reqMetier != "" and not receiver.isRaceclass( csconst.g_map_class[self._reqMetier], csdefine.RCMASK_CLASS ):
			INFO_MSG( "%s(%i): learn skill %i, metier differ." % (receiver.playerName, receiver.id, self._spellTeach) )
			receiver.statusMessage( csstatus.LEARN_SKILL_METIER_DIFFER )
			return

		# �Ƿ��и����͵ļ���
		skillID = self.hasMapSkill( receiver.getSkills(), self._SkillsMap )
		ifUpdate = skillID != 0
		nextSkillID = 0
		# �ȼ����
		if ifUpdate:
			if Skill[skillID].getLevel() >= self._skillLevelMax:
				INFO_MSG( "%s(%i): learn skill %i, skill is max level." % (receiver.playerName, receiver.id, self._spellTeach) )
				receiver.statusMessage( csstatus.LEARN_SKILL_MAX_LEVEL, self.getName() )
				return
			nextSkillID = self.getNextSkillID( skillID ) # ����Ǹ��¼�����ô������ID�赽�¼�����ID
		else:
			nextSkillID = self._spellTeach
		# Ҫ��ȼ�
		if nextSkillID != 0 and receiver.level < g_skillTeachDatas[ nextSkillID ]['ReqLevel']:
			INFO_MSG( "%s(%i): learn skill %i, level %i need." % (receiver.playerName, receiver.id, self._spellTeach, g_skillTeachDatas[ nextSkillID ]['ReqLevel']) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_LEVEL )
			return
			
		# �Ƿ���Ҫ����
		canLearnSkillID = 0
		if nextSkillID:
			for reSkillID in self._reqSk:
				if reSkillID:
					reSkill = Skill[reSkillID]
					_reSkillsMap = self.getSkillsMap( reSkillID )
					canLearnSkillID = self.learnMapSkill( receiver.getSkills(), _reSkillsMap )		# ��ǰ��ѧ�������ȼ�
					if canLearnSkillID and canLearnSkillID + 1 > nextSkillID:		# Ҫѧ�ļ��ܵȼ����ɸ��ڵ�ǰ��ѧ�������ȼ�
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

		# ��Ǯ
		money = g_skillTeachDatas[ nextSkillID ]['ReqMoney']
		if not receiver.payMoney( money, csdefine.CHANGE_MONEY_LEARN_SKILL ):
			INFO_MSG( "%s(%i): learn skill %i, money %i need." % (receiver.playerName, receiver.id, self._spellTeach, g_skillTeachDatas[ nextSkillID ]['ReqMoney']) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_MONEY )
			return

		# ��Ǳ�ܵ�
		receiver.payPotential( potential )

		if ifUpdate:		# �������������ɾ��ԭ�ȼ�����
			receiver.setTemp( "roleUpdateSkill", True )
			if receiver.updateSkill( skillID , nextSkillID ):
				receiver.questSkillLearned( nextSkillID )
			try:
				g_logger.skillUpgradeLog( receiver.databaseID, receiver.getName(), nextSkillID, skillID, potential,money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			receiver.removeTemp( "roleUpdateSkill" )
		else:			# ��Ӽ���
			if receiver.addSkill( self._spellTeach ):
				receiver.questSkillLearned( nextSkillID )
			try:
				g_logger.skillLearnLog( receiver.databaseID, receiver.getName(), nextSkillID, potential, money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

class Spell_Pet_TeachBook( Spell_Item, Spell ):
	"""
	���＼��ѧϰ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		Spell.init( self, dict )

		self._reqMetier = ( dict[ "param2" ] if dict[ "param2" ] > 0 else "" ) 				# ����ְҵ�����û������""
		self._spellTeach = long( dict["param1"] if dict["param1"] else 0 ) 				# ���ڵ�1������ID
		self._replaceSkillID = int( dict["param3"] if dict["param3"] else 0 )				# ǰ�ü���ID
		self._skillLevelMax = int( dict["param4"] if dict["param4"] else 0 ) 			# ���ܵ����ȼ�
		# ��ӳ��
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
			DEBUG_MSG("���＼�����������󣡣�������������������")

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

	def hasPostSkill( self, skillIDs, hsMap ):
		"""
		�ж��Ƿ���skillIDs����hsMap�д��ڵļ���ID
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
		# ְҵ��һ��
		if self._reqMetier != "":
			if not receiver.isRaceclass( csconst.g_map_class[self._reqMetier], csdefine.PET_TYPE_MASK ):
				return csstatus.PET_LEARN_SKILL_METIER_DIFFER

		# �Ƿ��и����͵ļ��ܡ����＼���������ֻ���ó���ѧ����һ���͵ļ��ܣ�
		# ����Ѿ����˸ü��ܣ���ô������ѧϰ�ˡ�
		if self.hasMapSkill( receiver.getSkills(), self._SkillsMap ):
			return csstatus.PET_LEARN_SKILL_ALREADY_HAVE

		skillID = self._spellTeach

		# Ҫ��ȼ�
		if skillID and receiver.level < g_skillTeachDatas[ skillID ]['ReqLevel']:
			return csstatus.PET_LEARN_SKILL_NEED_LEVEL

		# �Ƿ��и߽׼���
		if self.hasPostSkill( receiver.getSkills(), self._postSkillList ):
			return csstatus.PET_LEARN_SKILL_HAS_POST_SKILL

		# �Ƿ���ǰ�ü���
		if skillID and self._replaceSkillID:
			if not self._replaceSkillID in receiver.getSkills():	# ����������û�����ǰ�ü���
				return csstatus.PET_LEARN_SKILL_NEED_OTHER_SKILL

		# ���û�п����滻�ļ��ܣ���Ҫ�жϳ������ϵļ��ܸ����Ƿ�����
		if not self._replaceSkillID:
			#�����������������������츳���ܲ��㡣
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
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# �Ƿ��и����͵ļ���
		skillID = self.hasMapSkill( receiver.getSkills(), self._SkillsMap )

		if skillID != 0:		# ����Ѿ����˸ü��ܣ���ô������ѧϰ�ˡ�
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
	��Ἴ��ѧϰ
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Teach.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Teach.init( self, dict )
		#ѧϰ����
		# ע�͵���������Ϊ��ҿ��Կ����������ѧϰ��ʱ���Ὠ���ȼ������Ѿ��ﵽ
		#self.buildingLv = dict.readString( "buildingLv" )				# ��Ὠ�� �о�Ժ�ȼ�

	def getCurrentLearnSkillID( self, receiver ):
		"""
		��ȡ��ǰѧϰ����ID
		"""
		# �Ƿ��и����͵ļ���
		skillID = self.hasMapSkill( receiver.getSkills(), self._SkillsMap )
		ifUpdate = skillID != 0

		# �ȼ����
		if ifUpdate:
			if Skill[skillID].getLevel() >= self._skillLevelMax:
				#receiver.statusMessage( csstatus.LEARN_SKILL_MAX_LEVEL, self.getName() )
				return 0
			skillID += 1 # ����Ǹ��¼�����ô������ID�赽�¼�����ID
		else:
			skillID = self._spellTeach
		return skillID

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# ְҵ��һ��
		if self._reqMetier != "" and not receiver.isRaceclass( csconst.g_map_class[self._reqMetier], csdefine.RCMASK_CLASS ):
			INFO_MSG( "%s(%i): learn skill %i, metier differ." % (receiver.playerName, receiver.id, self._spellTeach) )
			receiver.statusMessage( csstatus.LEARN_SKILL_METIER_DIFFER )
			return

		# �Ƿ��и����͵ļ���
		skillID = self.hasMapSkill( receiver.getSkills(), self._SkillsMap )
		ifUpdate = skillID != 0

		# �ȼ����
		if ifUpdate:
			if Skill[skillID].getLevel() >= self._skillLevelMax:
				INFO_MSG( "%s(%i): learn skill %i, skill is max level." % (receiver.playerName, receiver.id, self._spellTeach) )
				receiver.statusMessage( csstatus.LEARN_SKILL_MAX_LEVEL, self.getName() )
				return
			skillID += 1 # ����Ǹ��¼�����ô������ID�赽�¼�����ID
		else:
			skillID = self._spellTeach

		# Ҫ��ȼ�
		if skillID != 0 and receiver.level < g_skillTeachDatas[ skillID ]['ReqLevel']:
			INFO_MSG( "%s(%i): learn skill %i, level %i need." % (receiver.playerName, receiver.id, self._spellTeach, g_skillTeachDatas[ skillID ]['ReqLevel']) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_LEVEL )
			return

		# �Ƿ���Ҫ����
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

		# ��Ǯ
		money = g_skillTeachDatas[ skillID ]['ReqMoney']
		if not receiver.payMoney( money, csdefine.CHANGE_MONEY_LEARN_SKILL  ):
			INFO_MSG( "%s(%i): learn skill %i, money %i need." % (receiver.playerName, receiver.id, self._spellTeach, g_skillTeachDatas[ skillID ]['ReqMoney']) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_MONEY )
			return

		# ��Ǳ�ܵ�
		receiver.payPotential( potential )

		if ifUpdate:		# �������������ɾ��ԭ�ȼ�����
			receiver.setTemp( "roleUpdateSkill", True )
			receiver.updateSkill( skillID - 1, skillID )
			try:
				g_logger.skillTongUpgradeLog( receiver.databaseID, receiver.getName(), skillID, skillID - 1, potential, money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			receiver.removeTemp( "roleUpdateSkill" )
		else:			# ��Ӽ���
			receiver.addSkill( self._spellTeach )
			try:
				g_logger.skillTongLearnLog( receiver.databaseID, receiver.getName(), skillID, potential, money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )


class Spell_VehicleTeach( Spell_Teach ):
	"""
	���ļ���ѧϰ
	"""
	def __init__( self ):
		"""
		"""
		Spell_Teach.__init__( self )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ�������顣
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return False

		currVehicleID = getCurrVehicleID( receiver )
		if currVehicleID == 0:
			receiver.statusMessage( csstatus.LEARN_SKILL_MUST_CALL_VEHICLE )
			return False

		# ��Ϊ��輼��ѧϰ��;���仯 ���ӳ���1������ by����
		vehicleSkills = getCurrVehicleSkillIDs( receiver )
		levels = []
		for vs in vehicleSkills:
			if Skill[vs].getLevel() == 1:
				self._SkillsMap.add( self._spellTeach - 1 )
		# �Ƿ��и����͵ļ���
		skillID = self.hasMapSkill( vehicleSkills, self._SkillsMap )
		ifUpdate = skillID != 0

		# �ȼ����
		if ifUpdate:
			if Skill[skillID].getLevel() >= self._skillLevelMax:
				INFO_MSG( "%s(%i)'s vehicle: learn skill %i, skill is max level." % (receiver.playerName, receiver.id, self._spellTeach) )
				receiver.statusMessage( csstatus.VEHICLE_LEARN_SKILL_MAX_LEVEL, self.getName() )
				receiver.removeTemp( "item_using" )
				return False
			skillID += 1 # ����Ǹ��¼�����ô������ID�赽�¼�����ID
		else:
			skillID = self._spellTeach

		if not ifUpdate:
			if len( vehicleSkills ) >= csconst.VEHICLE_SKILLS_TOTAL:
				receiver.statusMessage( csstatus.LEARN_SKILL_COUNT_LIMIT )
				receiver.removeTemp( "item_using" )
				return False

		# Ҫ��ȼ�
		vehicleLevel = receiver.currAttrVehicleData["level"]
		reqLevel = g_skillTeachDatas[ skillID ]['ReqLevel']
		if skillID != 0 and vehicleLevel < reqLevel:
			INFO_MSG( "%s(%i)'s vehicle: learn skill %i, level %i need." % (receiver.playerName, receiver.id, self._spellTeach, reqLevel) )
			receiver.statusMessage( csstatus.VEHICLE_LEARN_SKILL_NEED_LEVEL )
			receiver.removeTemp( "item_using" )
			return False

		# �Ƿ���Ҫ����
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

		# ��Ǯ
		money = g_skillTeachDatas[ skillID ]['ReqMoney']
		if not receiver.payMoney( money, csdefine.CHANGE_MONEY_LEARN_SKILL ):
			INFO_MSG( "%s(%i)'s vehicle: learn skill %i, money %i need." % (receiver.playerName, receiver.id, self._spellTeach, g_skillTeachDatas[ skillID ]['ReqMoney']) )
			receiver.statusMessage( csstatus.LEARN_SKILL_NEED_MONEY )
			receiver.removeTemp( "item_using" )
			return False

		receiver.addVehicleSkPoint( currVehicleID, -skillPoint )

		if ifUpdate:		# �������������ɾ��ԭ�ȼ�����
			receiver.setTemp( "roleUpdateSkill", True )
			receiver.updateVehicleSkill( currVehicleID, skillID - 1, skillID )
			try:
				g_logger.skillVehicleUpgradeLog( receiver.databaseID, receiver.getName(), currVehicleID,skillID,skillID - 1, skillPoint,money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			receiver.removeTemp( "roleUpdateSkill" )
		else:			# ��Ӽ���
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
		��ȡ��������
		@param dict: ��������
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
		����������Ҫ�������顣
		"""
		if Spell_VehicleTeach.receive( self, caster, receiver ):
			Spell_Item.updateItem(self, caster )

class Spell_TeachTongPetSkill( Spell_TeachTongSkill ):
	"""
	�����Ἴ��ѧϰ
	"""
	def getCurrentLearnSkillID( self, receiver ):
		"""
		��ȡ��ǰѧϰ����ID
		"""
		actPet = receiver.pcg_getActPet()
		if not actPet :
			return 0
		if actPet.etype != "REAL" :
			return 0
			
		# �Ƿ��и����͵ļ���
		skillID = self.hasMapSkill( actPet.entity.getSkills(), self._SkillsMap )
		ifUpdate = ( skillID != 0 )

		# �ȼ����
		if ifUpdate:
			if Skill[skillID].getLevel() >= self._skillLevelMax:
				#receiver.statusMessage( csstatus.LEARN_SKILL_MAX_LEVEL, self.getName() )
				return 0
			skillID += 1 # ����Ǹ��¼�����ô������ID�赽�¼�����ID
		else:
			skillID = self._spellTeach
		return skillID
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ�������顣
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
		# ְҵ��һ��
		if self._reqMetier != "" and not petEntity.isRaceclass( csconst.g_map_class[self._reqMetier], csdefine.RCMASK_CLASS ):
			INFO_MSG( "%s(%i): learn skill %i, metier differ." % (petEntity.playerName, petEntity.id, self._spellTeach) )
			receiver.statusMessage( csstatus.PET_LEARN_SKILL_METIER_DIFFER )
			return
		# �Ƿ��и����͵ļ���
		skillID = self.hasMapSkill( petEntity.getSkills(), self._SkillsMap )
		if skillID == 0:
			receiver.statusMessage( csstatus.PET_LEARN_SKILL_NOT_LEARN )
			return
			
		if Skill[skillID].getLevel() >= self._skillLevelMax:
			INFO_MSG( "%s(%i): learn skill %i, skill is max level." % (petEntity.playerName, petEntity.id, self._spellTeach) )
			receiver.statusMessage( csstatus.PET_LEARN_SKILL_LEVEL_MAX, self.getName() )
			return
		skillID += 1 # ������ID�赽�¼�����ID
		learnSkillData = g_skillTeachDatas[ skillID ]
		# Ҫ��ȼ�
		if petEntity.level < learnSkillData['ReqLevel']:
			INFO_MSG( "%s(%i): learn skill %i, level %i need." % (petEntity.getName(), petEntity.id, self._spellTeach, g_skillTeachDatas[ skillID ]['ReqLevel']) )
			receiver.statusMessage( csstatus.PET_LEARN_SKILL_NEED_LEVEL )
			return
			
		# �Ƿ���Ҫ����
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
	�̹��ػ�����ѧϰ
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Teach.__init__( self )
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		Spell_Teach.init( self, dict )
		
		self._spellTeach = long( dict["param1"] if dict["param1"] else 0 ) 					# ���ڼ���ID
		self._skillLevelMax = int( dict["param2"] if dict["param2"] else 0 ) 				# ���ܵ����ȼ�
		# ��ӳ��
		self._SkillsMap = self.getSkillsMap( self._spellTeach )

	def useableCheck( self, caster, target ) :
		"""
		У�鼼���Ƿ����ʹ�á�
		"""
		if caster.level < g_skillTeachDatas[ self._spellTeach ]['ReqLevel']:			# Ҫ��ȼ�
			INFO_MSG( "%s(%i): learn skill %i, level %i need." % (caster.playerName, caster.id, self._spellTeach, g_skillTeachDatas[ self._spellTeach ]['ReqLevel']) )
			return csstatus.LEARN_SKILL_NEED_LEVEL 
			
		if Skill[self._spellTeach].getLevel() > self._skillLevelMax:							# �Ƿ�Ϊ���ȼ�
				INFO_MSG( "%s(%i): learn skill %i, skill is max level." % ( caster.playerName, caster.id, self._spellTeach) )
				return csstatus.SKILL_SPELL_LEARN_SKILL_MAX_LEVEL
				
		if self._spellTeach in caster.getSkills():										# �Ƿ��Ѿ�ѧϰ�˸ü���
				return csstatus.SKILL_SPELL_LEARN_SKILL_ALREADY
				
		if Skill[self._spellTeach].getLevel() > 1:										# �Ƿ��Ѿ�ѧϰ�˵͵ȼ��ļ���
			lowSkillID = self._spellTeach -1
			if lowSkillID not in caster.getSkills():
				return csstatus.NATURE_JADE_LEVEL_INVALID

		return Spell_Item.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# ��������1������Ҫ�������ü���Ҫ���Ǳ����1����ʼѧ��
		ifUpdate = Skill[self._spellTeach].getLevel() > 1

		if ifUpdate:		# �������������ɾ��ԭ�ȼ�����
			receiver.setTemp( "roleUpdateSkill", True )
			receiver.updateSkill( self._spellTeach - 1, self._spellTeach )
			try:
				g_logger.skillPGUpgradeLog( receiver.databaseID, receiver.getName(), self._spellTeach, self._spellTeach - 1 )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
			receiver.removeTemp( "roleUpdateSkill" )
		else:			# ��Ӽ���
			receiver.addSkill( self._spellTeach )
			try:
				g_logger.skillPGLearnLog( receiver.databaseID, receiver.getName(), self._spellTeach )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
				

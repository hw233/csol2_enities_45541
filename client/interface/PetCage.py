# -*- coding: gb18030 -*-
#
# $Id: PetCage.py,v 1.29 2008-08-11 07:20:11 huangyongwei Exp $

"""
This module implements the pet entity.

2007/07/17 : writen by huangyongwei
2007/10/24 : according to new version document, it is rewriten by huangyongwei
"""

import BigWorld
import csdefine
import csconst
import csstatus
import Const
import skills as Skill
import event.EventCenter as ECenter
from bwdebug import *
from PetFormulas import formulas
from gbref import rds
from ItemsFactory import PetSkillItem
from QuickBar import QBPetSkillItem
from PetTrainer import PetTrainer
from PetStorage import PetStorage
from PetFoster import PetFoster
from Helper import courseHelper
from ItemsFactory import BuffItem
from Function import Functor
from Time import Time

class PetCage( PetTrainer, PetStorage, PetFoster ) :
	def __init__( self ) :
		PetTrainer.__init__( self )
		PetStorage.__init__( self )
		PetFoster.__init__( self )
		self.__petEpitomes = {}								# �������г���� epitome��{ databaseID : instance of PetEpitome }
		self.__skillList = []								# ����ļ����б�
		self.__buffList = []								# ���� buff �б�
		self.__cooldownInfos = {}							# ����� cooldown ��Ϣ
		self.__qbItems = []									# ���＼����


	def leaveWorld( self ):
		PetFoster.leaveWorld( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getCombineMaterialPets( self ) :
		"""
		��ȡ����ϳ�ʱ�Ĳ��ϳ���
		"""
		petEpitomes = []
		outEpitome = self.pcg_getActPetEpitome()
		if outEpitome is None : return []
		for epitome in self.__petEpitomes.itervalues() :
			if outEpitome.databaseID == epitome.databaseID : continue
			if formulas.isHierarchy( epitome.species, csdefine.PET_HIERARCHY_GROWNUP ) :
				if epitome.level >= outEpitome.level - 5 :
					petEpitomes.append( epitome )
		return petEpitomes

	def __flyPassiveSkillName( self, skillID ):
		"""
		������ڱ������ܣ�ͷ��ð���������ܵ����֡�
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_SKILL_NAME", self.pcg_getActPet().id, skillID )


	# ----------------------------------------------------------------
	# attribute update methods
	# ----------------------------------------------------------------
	def set_pcg_reinBible( self, oldValue ) :
		"""
		����Ԧ�����ʱ������
		"""
		self.statusMessage( csstatus.REIN_BOOK_USE_SUCCESS, self.pcg_reinBible - oldValue )
		ECenter.fireEvent( "EVT_ON_PCG_KEEPING_COUNT_CHANGED" )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		PetTrainer.onCacheCompleted( self )
		PetStorage.onCacheCompleted( self )
		PetFoster.onCacheCompleted( self )

	def pcg_onActPetEnterWorld( self, actPet ):
		pass

	# -------------------------------------------------
	def pcg_getKeepingCount( self ) :
		"""
		��ȡ����Я�����������
		"""
		return formulas.getKeepingCount( self.pcg_reinBible )

	def pcg_getPetEpitomes( self ) :
		"""
		��ȡ���г���� epitome
		"""
		return self.__petEpitomes

	def pcg_getPetEpitome( self, petDBID ):
		"""
		��ȡ��Ӧdbid�ĳ���epitome
		"""
		return self.__petEpitomes[petDBID]

	def pcg_getActPetEpitome( self ) :
		"""
		��ȡ��ǰ��������� epitome
		"""
		for epitome in self.__petEpitomes.itervalues() :
			petEntity = epitome.getEntity()
			if petEntity is not None :
				return epitome
		return None

	def pcg_getActPet( self ) :
		"""
		��ȡ��ǰ�����ĳ��� entity
		"""
		epitome = self.pcg_getActPetEpitome()
		if epitome is not None :
			return epitome.getEntity()
		return None

	def pcg_isActPet( self, dbid ):
		"""
		�Ƿ��������
		"""
		epitome = self.pcg_getActPetEpitome()
		return epitome and epitome.databaseID == dbid

	def pcg_isPetBinded( self, dbid ):
		"""
		�����Ƿ񱻰�
		"""
		return self.__petEpitomes[dbid].isBinded

	def pcg_getActPetBuffList( self ):
		return self.__buffList

	# -------------------------------------------------
	def pcg_getPetSkillList( self ) :
		"""
		��ȡ���＼���б�
		"""
		return self.__skillList[:]

	def pcg_getPetCooldown( self, typeID ) :
		"""
		��ȡ����� cooldown
		"""
		epitome = self.pcg_getActPetEpitome()
		if epitome:
			if self.__cooldownInfos.get( epitome.databaseID, {}):
				return self.__cooldownInfos[epitome.databaseID].get( typeID, ( 0, 0, 0, 0 ) )
			else:
				return ( 0, 0, 0, 0 )
		else:
			return ( 0, 0, 0, 0 )
		#return self.__cooldownInfos.get( typeID, ( 0, 0, 0, 0 ) )

	# -------------------------------------------------
	def pcg_combinePet( self, srcDbid ) :
		"""
		�ϳɳ���
		"""
		self.cell.pcg_combinePets( srcDbid )

	# -------------------------------------------------
	def pcg_setActionMode( self, mode ) :
		"""
		���ó������Ϊģʽ
		"""
		pet = self.pcg_getActPet()
		if pet is None : return False
		pet.setActionMode( mode )
		return True

	def pcg_setTussleMode( self, mode ) :
		"""
		���ó����ս��ģʽ
		"""
		pet = self.pcg_getActPet()
		if pet is None : return False
		if pet.tussleMode == mode : return False
		pet.setTussleMode( mode )
		return True

	# -------------------------------------------------
	def pcg_updatePetQBItem( self, index, spell ) :
		"""
		���³�������
		"""
		pet = self.pcg_getActPet()
		if pet is None :
			DEBUG_MSG( "pet is not in AOI, update pet's quickbar fail!" )
			return
		item = { "skillID" : 0, "autoUse" : 0 }
		if spell :
			item["skillID"] = spell.getID()
			item["autoUse"] = False
		pet.cell.updateQBItem( index, item )

	def pcg_exchangePetQBItem( self, srcIdx, dstIdx ) :
		"""
		�������������ݸ�
		"""
		pet = self.pcg_getActPet()
		if pet is None :
			DEBUG_MSG( "pet is not in AOI, update pet's quickbar fail!" )
		else :
			pet.cell.updateQBItem( srcIdx, self.__qbItems[dstIdx] )
			pet.cell.updateQBItem( dstIdx, self.__qbItems[srcIdx] )

	def pcg_toggleAutoUsePetQBItem( self, index, autoUse = None ) :
		"""
		����/���������ݸ���Զ�ʹ�ù���
		"""
		pet = self.pcg_getActPet()
		if pet is None :
			DEBUG_MSG( "pet is not in AOI, update pet's quickbar fail!" )
		elif autoUse != self.__qbItems[index]["autoUse"] :
			qbItem = self.__qbItems[index]
			item = {}
			item["index"] = index
			item["skillID"] = qbItem["skillID"]
			if autoUse is None : autoUse = not qbItem["autoUse"]
			item["autoUse"] = autoUse
			pet.cell.updateQBItem( index, item )

	# -------------------------------------------------
	def pcg_attackTarget( self, skillID = None ) :
		"""
		�ó��﹥��Ŀ�꣬����ָ�����ܣ�����ָ�����ܹ����������������ܹ���
		"""
		target = self.targetEntity
		if target is None :
			self.statusMessage( csstatus.SKILL_NO_TARGET )
			return False
		pet = self.pcg_getActPet()
		if not pet : return False
		if skillID and skillID not in self.__skillList : return False
		if skillID is None or skillID == 0:
			skillID = csconst.PET_SKILL_ID_PHYSICS_MAPS.get( pet.getPType(), 0 )
		pet.attackTarget( target, skillID )
		return True


	# ----------------------------------------------------------------
	# defined methods
	# ----------------------------------------------------------------
	def pcg_onInitPetSkillBox( self, skillIDs ):
		"""
		defined method.
		��ʼ�������б�
		@type					skills : list
		@param 					skills : [ skillID, ... ]
		"""
		ECenter.fireEvent( "EVT_ON_BEFORE_PET_ADD_SKILL" )	# ����ճ��＼�����
		self.__skillList = skillIDs
		interval = 0.0
		for skillID in skillIDs:
			skillInstance = Skill.getSkill( skillID )
			if skillInstance.getType() == csdefine.BASE_SKILL_TYPE_PASSIVE:
				interval += Const.PET_PASSTIVE_SKILL_FLY_TIME
				BigWorld.callback( interval, Functor( self.__flyPassiveSkillName, skillID ) )
		ECenter.fireEvent( "EVT_ON_PET_PANEL_REFRESH" )

	def pcg_onInitPetQBItems( self, qbItems ) :
		"""
		<defined method>
		��ʼ����������
		"""
		ECenter.fireEvent( "EVT_ON_PET_CLEAR_SKILLS" )	# ����ճ�������
		self.__qbItems = list( qbItems )
		for index, qbItem in enumerate( self.__qbItems ) :
			item = None
			skillID = qbItem["skillID"]
			if skillID:
				skillInstance = Skill.getSkill( skillID )
				if skillInstance.getType() in csconst.BASE_SKILL_TYPE_PASSIVE_SPELL_LIST:
					continue
				else:
					item = QBPetSkillItem( qbItem )
					ECenter.fireEvent( "EVT_ON_PET_UPDATE_QUICKITEM", index, item )

	def pcg_onUpdatePetQBItem( self, index, qbItem ) :
		"""
		<defined method>
		���³�������
		"""
		self.__qbItems[index] = qbItem
		item = None
		skillID = qbItem["skillID"]
		if skillID:
			skillInstance = Skill.getSkill( skillID )
			if skillInstance.getType() not in csconst.BASE_SKILL_TYPE_PASSIVE_SPELL_LIST:
				item = QBPetSkillItem( qbItem )
		# �յ�ҲҪ����
		ECenter.fireEvent( "EVT_ON_PET_UPDATE_QUICKITEM", index, item )

	def pcg_getQBItems( self ):
		"""
		��ȡ����Ŀ��������
		"""
		return self.__qbItems[:]

	# -------------------------------------------------
	def pcg_onAddPet( self, petEpitome ) :
		"""
		defined method.
		�����һ������ʱ������
		"""
		self.__petEpitomes[petEpitome.databaseID] = petEpitome
		self.__cooldownInfos[petEpitome.databaseID] = {}
		ECenter.fireEvent( "EVT_ON_PCG_ADD_PET", petEpitome )
		rds.helper.courseHelper.petAction( "huode" )			# ������ó������

	def pcg_onRemovePet( self, dbid ) :
		"""
		defined method.
		��ɾ��һ������ʱ������
		"""
		if dbid in self.__petEpitomes :
			self.__petEpitomes.pop( dbid )
			self.__cooldownInfos.pop( dbid )
		else :
			ERROR_MSG( "pet is not exist which id is %i" % dbid )
		ECenter.fireEvent( "EVT_ON_PCG_REMOVE_PET", dbid )

	# -------------------------------------------------
	def pcg_onPetConjured( self, dbid ) :
		"""
		�������ʱ������
		"""
		pass

	def pcg_onPetWithdrawed( self ) :
		"""
		�������ʱ������
		"""
		self.__skillList = []
		self.__buffList = []
		#self.__cooldownInfos.clear()
		ECenter.fireEvent( "EVT_ON_PET_PCG_WITHDRAW" )

	# -------------------------------------------------
	def pcg_onShowCombineDialog( self ) :
		"""
		defined method.
		��ʾ����ϳɴ���
		"""
		outPet = self.pcg_getActPetEpitome()
		petEpitomes = self.__getCombineMaterialPets()
		ECenter.fireEvent( "EVT_ON_PCG_SHOW_COMBINE", outPet, petEpitomes )

	def pcg_onHideCombineDialog( self ) :
		"""
		defined method.
		��˳���ϳɴ���
		"""
		ECenter.fireEvent( "EVT_ON_PCG_HIDE_COMBINE" )

	# -------------------------------------------------
	def pcg_onPetAddSkill( self, skillID ) :
		"""
		defined method.
		���һ����ս���＼��
		@type		skillID	: INT
		@param		skillID : ��ӵļ��ܵ�ID��
		@return				: None
		"""
		if skillID not in self.__skillList:
			self.__skillList.append( skillID )
		ECenter.fireEvent( "EVT_ON_PET_PANEL_REFRESH" )

	def pcg_onPetRemoveSkill( self, skillID ) :
		"""
		defined method.
		�Ƴ���ս�����һ������
		@type		skillID	: INT
		@param		skillID : Ҫ�Ƴ��ļ���ID��
		@return				: None
		"""
		if skillID in self.__skillList:
			self.__skillList.remove( skillID )
			ECenter.fireEvent( "EVT_ON_PET_REMOVE_SKILL", skillID )

	def pcg_onPetUpdateSkill( self, oldSkillID, newSkillID ) :
		"""
		defined method.
		���³�ս�����һ������
		@type		oldSkillID : INT
		@param		oldSkillID : �ɵļ��� ID
		@type		newSkillID : INT
		@param		newSkillID : �µļ��� ID
		@return				   : None
		"""
		for index, skillID in enumerate( self.__skillList ) :
			if skillID == oldSkillID :
				self.__skillList[index] = newSkillID
				break
		skill = Skill.getSkill( newSkillID )
		skillItem = PetSkillItem( skill )
		ECenter.fireEvent( "EVT_ON_PET_UPDATE_SKILL", oldSkillID, skillItem )

	# -------------------------------------------------
	def pcg_onPetAddBuff( self, buff ) :
		"""
		defined method.
		��ӳ��� buff
		"""
		buffItem = BuffItem( buff )
		self.__buffList.append( buffItem )
		ECenter.fireEvent( "EVT_ON_PET_ADD_BUFF", buffItem )

	def pcg_onPetRemoveBuff( self, index ) :
		"""
		defined method.
		ɾ������ buff
		"""
		DEBUG_MSG( "-------->>>1111" )
		if len( self.__buffList ) <= 0:
			return
		for buffItem in self.__buffList:
			if buffItem.buffIndex == index:
				ECenter.fireEvent( "EVT_ON_PET_REMOVE_BUFF", buffItem )
				self.__buffList.remove( buffItem )
				return

		WARNING_MSG( "onPetRemoveBuff->not found buff[ index:%i ]" % index )

	def pcg_onPetUpdateBuff( self, index, buff ) :
		"""
		defined method
		���³��� buff
		"""
		buffItem = BuffItem( buff )
		self.__buffList[index] = buffItem
		ECenter.fireEvent( "EVT_ON_PET_UPDATE_BUFF", buffItem )

	# -------------------------------------------------
	def pcg_onPetCooldownChanged( self, typeID, lastTime, totalTime ):
		"""
		defined method.
		������ cooldown �ı�ʱ������
		@type 			typeID	: STRING
		@param			typeID	: cooldown type
		@type 			timeVal	: DOUBLE
		@param			timeVal	: unfreezed time
		"""
		startTime = Time.time()
		endTime = startTime + lastTime
		epitome = self.pcg_getActPetEpitome()
		self.__cooldownInfos[epitome.databaseID][typeID] = ( lastTime, totalTime, startTime, endTime )
		ECenter.fireEvent( "EVT_ON_PET_BEGIN_COOLDOWN", typeID, lastTime )


	# -------------------------------------------------
	# bridge methods
	# -------------------------------------------------
	def pcg_onUpdatePetEpitomeAttr( self, dbid, attrName, value ) :
		"""
		���·ǳ�ս���������
		"""
		epitome = self.__petEpitomes.get( dbid, None )
		if epitome is None :
			ERROR_MSG( "pet which database id is %i is not exist!" )
		else :
			epitome.onUpdateAttr( attrName, value )

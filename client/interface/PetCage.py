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
		self.__petEpitomes = {}								# 保存所有宠物的 epitome：{ databaseID : instance of PetEpitome }
		self.__skillList = []								# 宠物的技能列表
		self.__buffList = []								# 宠物 buff 列表
		self.__cooldownInfos = {}							# 宠物的 cooldown 信息
		self.__qbItems = []									# 宠物技能栏


	def leaveWorld( self ):
		PetFoster.leaveWorld( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getCombineMaterialPets( self ) :
		"""
		获取宠物合成时的材料宠物
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
		如果存在被动技能，头顶冒出被动技能的名字。
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_SKILL_NAME", self.pcg_getActPet().id, skillID )


	# ----------------------------------------------------------------
	# attribute update methods
	# ----------------------------------------------------------------
	def set_pcg_reinBible( self, oldValue ) :
		"""
		当驾驭典更新时被调用
		"""
		self.statusMessage( csstatus.REIN_BOOK_USE_SUCCESS, self.pcg_reinBible - oldValue )
		ECenter.fireEvent( "EVT_ON_PCG_KEEPING_COUNT_CHANGED" )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		PetTrainer.onCacheCompleted( self )
		PetStorage.onCacheCompleted( self )
		PetFoster.onCacheCompleted( self )

	def pcg_onActPetEnterWorld( self, actPet ):
		pass

	# -------------------------------------------------
	def pcg_getKeepingCount( self ) :
		"""
		获取可以携带宠物的数量
		"""
		return formulas.getKeepingCount( self.pcg_reinBible )

	def pcg_getPetEpitomes( self ) :
		"""
		获取所有宠物的 epitome
		"""
		return self.__petEpitomes

	def pcg_getPetEpitome( self, petDBID ):
		"""
		获取相应dbid的宠物epitome
		"""
		return self.__petEpitomes[petDBID]

	def pcg_getActPetEpitome( self ) :
		"""
		获取当前出征宠物的 epitome
		"""
		for epitome in self.__petEpitomes.itervalues() :
			petEntity = epitome.getEntity()
			if petEntity is not None :
				return epitome
		return None

	def pcg_getActPet( self ) :
		"""
		获取当前出征的宠物 entity
		"""
		epitome = self.pcg_getActPetEpitome()
		if epitome is not None :
			return epitome.getEntity()
		return None

	def pcg_isActPet( self, dbid ):
		"""
		是否出征宠物
		"""
		epitome = self.pcg_getActPetEpitome()
		return epitome and epitome.databaseID == dbid

	def pcg_isPetBinded( self, dbid ):
		"""
		宠物是否被绑定
		"""
		return self.__petEpitomes[dbid].isBinded

	def pcg_getActPetBuffList( self ):
		return self.__buffList

	# -------------------------------------------------
	def pcg_getPetSkillList( self ) :
		"""
		获取宠物技能列表
		"""
		return self.__skillList[:]

	def pcg_getPetCooldown( self, typeID ) :
		"""
		获取宠物的 cooldown
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
		合成宠物
		"""
		self.cell.pcg_combinePets( srcDbid )

	# -------------------------------------------------
	def pcg_setActionMode( self, mode ) :
		"""
		设置宠物的行为模式
		"""
		pet = self.pcg_getActPet()
		if pet is None : return False
		pet.setActionMode( mode )
		return True

	def pcg_setTussleMode( self, mode ) :
		"""
		设置宠物的战斗模式
		"""
		pet = self.pcg_getActPet()
		if pet is None : return False
		if pet.tussleMode == mode : return False
		pet.setTussleMode( mode )
		return True

	# -------------------------------------------------
	def pcg_updatePetQBItem( self, index, spell ) :
		"""
		更新宠物快捷栏
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
		交换两个宠物快捷格
		"""
		pet = self.pcg_getActPet()
		if pet is None :
			DEBUG_MSG( "pet is not in AOI, update pet's quickbar fail!" )
		else :
			pet.cell.updateQBItem( srcIdx, self.__qbItems[dstIdx] )
			pet.cell.updateQBItem( dstIdx, self.__qbItems[srcIdx] )

	def pcg_toggleAutoUsePetQBItem( self, index, autoUse = None ) :
		"""
		设置/撤销宠物快捷格的自动使用功能
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
		让宠物攻击目标，给出指定技能，则用指定技能攻击，否则用物理技能攻击
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
		初始化技能列表
		@type					skills : list
		@param 					skills : [ skillID, ... ]
		"""
		ECenter.fireEvent( "EVT_ON_BEFORE_PET_ADD_SKILL" )	# 先清空宠物技能面板
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
		初始化宠物快捷栏
		"""
		ECenter.fireEvent( "EVT_ON_PET_CLEAR_SKILLS" )	# 先清空宠物快捷栏
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
		更新宠物快捷栏
		"""
		self.__qbItems[index] = qbItem
		item = None
		skillID = qbItem["skillID"]
		if skillID:
			skillInstance = Skill.getSkill( skillID )
			if skillInstance.getType() not in csconst.BASE_SKILL_TYPE_PASSIVE_SPELL_LIST:
				item = QBPetSkillItem( qbItem )
		# 空的也要更新
		ECenter.fireEvent( "EVT_ON_PET_UPDATE_QUICKITEM", index, item )

	def pcg_getQBItems( self ):
		"""
		获取宠物的快捷栏技能
		"""
		return self.__qbItems[:]

	# -------------------------------------------------
	def pcg_onAddPet( self, petEpitome ) :
		"""
		defined method.
		当添加一个宠物时被调用
		"""
		self.__petEpitomes[petEpitome.databaseID] = petEpitome
		self.__cooldownInfos[petEpitome.databaseID] = {}
		ECenter.fireEvent( "EVT_ON_PCG_ADD_PET", petEpitome )
		rds.helper.courseHelper.petAction( "huode" )			# 触发获得宠物帮助

	def pcg_onRemovePet( self, dbid ) :
		"""
		defined method.
		当删除一个宠物时被调用
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
		宠物出征时被调用
		"""
		pass

	def pcg_onPetWithdrawed( self ) :
		"""
		宠物回收时被调用
		"""
		self.__skillList = []
		self.__buffList = []
		#self.__cooldownInfos.clear()
		ECenter.fireEvent( "EVT_ON_PET_PCG_WITHDRAW" )

	# -------------------------------------------------
	def pcg_onShowCombineDialog( self ) :
		"""
		defined method.
		显示宠物合成窗口
		"""
		outPet = self.pcg_getActPetEpitome()
		petEpitomes = self.__getCombineMaterialPets()
		ECenter.fireEvent( "EVT_ON_PCG_SHOW_COMBINE", outPet, petEpitomes )

	def pcg_onHideCombineDialog( self ) :
		"""
		defined method.
		因此宠物合成窗口
		"""
		ECenter.fireEvent( "EVT_ON_PCG_HIDE_COMBINE" )

	# -------------------------------------------------
	def pcg_onPetAddSkill( self, skillID ) :
		"""
		defined method.
		添加一个出战宠物技能
		@type		skillID	: INT
		@param		skillID : 添加的技能的ID号
		@return				: None
		"""
		if skillID not in self.__skillList:
			self.__skillList.append( skillID )
		ECenter.fireEvent( "EVT_ON_PET_PANEL_REFRESH" )

	def pcg_onPetRemoveSkill( self, skillID ) :
		"""
		defined method.
		移除出战宠物的一个技能
		@type		skillID	: INT
		@param		skillID : 要移除的技能ID号
		@return				: None
		"""
		if skillID in self.__skillList:
			self.__skillList.remove( skillID )
			ECenter.fireEvent( "EVT_ON_PET_REMOVE_SKILL", skillID )

	def pcg_onPetUpdateSkill( self, oldSkillID, newSkillID ) :
		"""
		defined method.
		更新出战宠物的一个技能
		@type		oldSkillID : INT
		@param		oldSkillID : 旧的技能 ID
		@type		newSkillID : INT
		@param		newSkillID : 新的技能 ID
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
		添加宠物 buff
		"""
		buffItem = BuffItem( buff )
		self.__buffList.append( buffItem )
		ECenter.fireEvent( "EVT_ON_PET_ADD_BUFF", buffItem )

	def pcg_onPetRemoveBuff( self, index ) :
		"""
		defined method.
		删除宠物 buff
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
		更新宠物 buff
		"""
		buffItem = BuffItem( buff )
		self.__buffList[index] = buffItem
		ECenter.fireEvent( "EVT_ON_PET_UPDATE_BUFF", buffItem )

	# -------------------------------------------------
	def pcg_onPetCooldownChanged( self, typeID, lastTime, totalTime ):
		"""
		defined method.
		当宠物 cooldown 改变时被调用
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
		更新非出战宠物的属性
		"""
		epitome = self.__petEpitomes.get( dbid, None )
		if epitome is None :
			ERROR_MSG( "pet which database id is %i is not exist!" )
		else :
			epitome.onUpdateAttr( attrName, value )

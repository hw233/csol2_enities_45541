# -*- coding: gb18030 -*-
#
# $Id: PetCage.py,v 1.46 2008-08-05 03:09:56 yangkai Exp $

"""
this module implements pet cage interface.

2007/07/01: writen by huangyongwei
2007/10/24: according to the new version, it is rewriten by huangyongwei
"""

import time
import BigWorld
import csdefine
import csconst
import csstatus
import Const
import csstatus_msgs
import ECBExtend
from bwdebug import *
from MsgLogger import g_logger
from cscollections import MapList
from Function import Functor
from PetFormulas import formulas
from ObjectScripts.GameObjectFactory import g_objFactory
from PetTrainer import PetTrainer
from PetStorage import PetStorage
from PetFoster import PetFoster
from PetEpitome import queryPets
import sys

# --------------------------------------------------------------------
# implement pet cage class
# --------------------------------------------------------------------
class PetCage( PetTrainer, PetStorage, PetFoster ) :
	def __init__( self ) :
		PetTrainer.__init__( self )
		PetStorage.__init__( self )
		PetFoster.__init__( self )

		self.conjurePosition = formulas.getPosition( self.cellData["position"], self.cellData["direction"][2] )
		self.conjureDirection = self.cellData["direction"]

		self.__petEpitomes = MapList()
		self.__tmpInitEpitomes = []


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initPets( self ) :
		"""
		initialize all pets when login
		"""
		def onInitPets( success, epitomes ) :
			if not success :
				ERROR_MSG( "init pets fail!" )
			else :
				self.__tmpInitEpitomes = epitomes.values()
				for epitome in self.__tmpInitEpitomes:
					if hasattr( self, "cell" ) :
						self.cell.pcg_onAddPet( epitome.getCellPetEpitome() )
					else :
						INFO_MSG( "role '%i' has been destroyed, when enterworld, so pet's initializing fail!" % self.databaseID )

		if len( self.__petDBIDs ) > 0 :
			queryPets( self.databaseID, self.__petDBIDs, onInitPets )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def pcg_addPet_( self, epitome, addReason = 0 ) :
		dbid = epitome.databaseID
		if dbid in self.__petDBIDs :
			if dbid in self.__petEpitomes :
				ERROR_MSG( "pet %i is exists!" % dbid )
				return False
			else :
				if epitome.getAttr( "ownerDBID" ) != self.databaseID :
					epitome.updateAttr( "ownerDBID", self.databaseID, self, lambda res : res )
				self.__petEpitomes[dbid] = epitome
				self.client.pcg_onAddPet( epitome )
		else :
			if epitome.getAttr( "ownerDBID" ) != self.databaseID :
				epitome.updateAttr( "ownerDBID", self.databaseID, self, lambda res : res )
			self.__petDBIDs.append( dbid )
			self.writeToDB()	# ��ó������������������ݵ����ݿ��ֹ�ص���ɳ����ò��ɹ���12:57 2009-10-29��wsf
			self.__petEpitomes[dbid] = epitome
			self.cell.pcg_onAddPet( epitome.getCellPetEpitome() )
			self.client.pcg_onAddPet( epitome )
			if addReason != csdefine.ADDPET_INIT:		# ��ʼ��ʱ��д��־
				try:
					g_logger.petAddLog( self.databaseID, self.getName(), dbid, epitome.getAttr("uname"), addReason )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
		return True

	def pcg_removePet_( self, dbid, deleteReason = 0 ) :
		if dbid in self.__petDBIDs :
			self.__petDBIDs.remove( dbid )
			epitome = self.__petEpitomes.pop( dbid )
			
			if hasattr( self, "client" ):	# ��ʱ�п���client�Ѿ����٣���cell���Ի����ڣ���Ϊ������cell���ù����ġ�
				self.client.pcg_onRemovePet( dbid )
			self.cell.pcg_onRemovePet( dbid )
			
			try:
				g_logger.petDelLog( self.databaseID, self.getName(), dbid, epitome.getAttr("uname"), deleteReason )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

			return epitome
		else :
			ERROR_MSG( "pet %i is not exist, you can't remove!" % dbid )
		return None


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def pcg_updateClient( self ) :
		"""
		������¿ͻ���
		"""
		if len( self.__tmpInitEpitomes ) :
			self.addTimer( 0.0, csconst.ROLE_INIT_INTERVAL, ECBExtend.UPDATE_CLIENT_PET_CBID )
		else :
			self.client.onInitialized( csdefine.ROLE_INIT_PETS )

	def onTimer_pet_updateClient( self, timerID, cbid ) :
		"""
		�ְ����ͳ������ݵ��ͻ���
		"""
		epitome = self.__tmpInitEpitomes.pop( 0 )
		self.pcg_addPet_( epitome, csdefine.ADDPET_INIT )
		if len( self.__tmpInitEpitomes ) == 0 :						# �������
			del self.__tmpInitEpitomes
			self.delTimer( timerID )
			self.client.onInitialized( csdefine.ROLE_INIT_PETS )

	# -------------------------------------------------
	def pcg_getPetCount( self ) :
		return len( self.__petDBIDs )

	def pcg_getPetEpitome( self, dbid ) :
		return self.__petEpitomes.get( dbid, None )

	def pcg_isActivePet( self, dbid ) :
		return dbid == self.__actPetDBID

	def pcg_getActPetDBID( self ):
		return self.__actPetDBID

	def pcg_requestPet( self ):
		"""
		Exposed method.
		�����ٻ���ս����
		"""
		def onConjurePet( pet, dbid, wasActive ) :
			if pet is None :
				self.__actPetDBID = 0
				DEBUG_MSG( "conjure pet fail in initialization!" )
			elif wasActive :
				ERROR_MSG( "pet which id is %i has conjured!" % dbid )
			else :
				pet = BigWorld.entities[pet.id]		# pet is a MAILBOX since the "shouldResolveMailBoxes" parame set to false on bw.xml::<baseapp>.
				pet.initialize( self )
				pet.createCellEntity( self.cell )
				self.__petEpitomes[dbid].updateAttr( "mapPetID", pet.id, self )
				self.__actPet = pet
				self.cell.pcg_onConjureResult( dbid, pet )

		if self.__actPetDBID in self.__petEpitomes :
			BigWorld.createBaseLocallyFromDBID( "Pet", self.__actPetDBID, onConjurePet )


	# ----------------------------------------------------------------
	# called by base entity
	# ----------------------------------------------------------------
	def pcg_onWithdrawPet( self, pet, withdrawMode ) :
		"""
		when a pet is withdrawed, it will be called by the pet entity
		@type				pet			 : MAILBOX
		@param				pet			 : the withdrawing pet's base mailbox
		@type				withdrawMode : bool
		@param				withdrawMode : defined in common/csdefine.py:
										   PET_WITHDRAW_COMMON
										   PET_WITHDRAW_HP_DEATH
										   PET_WITHDRAW_OFFLINE
										   PET_WITHDRAW_CONJURE
		@return							 : None
		"""
		dbid = pet.databaseID
		epitome = self.__petEpitomes.get( dbid, None )
		if not epitome :
			if self.__actPetDBID > 0 :
				ERROR_MSG( "withdraw pet fail, model: %i" % withdrawMode )
			else :
				WARNING_MSG( "pet is rewithdrawed! model: %i" % withdrawMode )
			return

		if withdrawMode != csdefine.PET_WITHDRAW_OFFLINE :						# �������Ϊ���߻��յĻ����������ﲻ�ᱻ����
			self.__actPetDBID = 0
		withdrawStatuses = {}
		withdrawStatuses[csdefine.PET_WITHDRAW_COMMON]		= csstatus.PET_WITHDRAW_SUCCESS_COMMON
		withdrawStatuses[csdefine.PET_WITHDRAW_HP_DEATH]	= csstatus.PET_WITHDRAW_SUCCESS_HP_DEATH
		withdrawStatuses[csdefine.PET_WITHDRAW_LIFE_DEATH]	= csstatus.PET_WITHDRAW_SUCCESS_LIFE_DEATH
		withdrawStatuses[csdefine.PET_WITHDRAW_CONJURE]		= csstatus.PET_WITHDRAW_SUCCESS_CONJURE
		withdrawStatuses[csdefine.PET_WITHDRAW_FREE]		= csstatus.PET_WITHDRAW_SUCCESS_FREE
		withdrawStatuses[csdefine.PET_WITHDRAW_OWNER_DEATH]	= csstatus.PET_WITHDRAW_SUCCESS_OWNER_DEATH
		withdrawStatuses[csdefine.PET_WITHDRAW_OFFLINE]		= csstatus.PET_WITHDRAW_SUCCESS_OFFLINE
		withdrawStatuses[csdefine.PET_WITHDRAW_GMWATCHER]	= csstatus.PET_WITHDRAW_SUCCESS_GMWATCHER
		withdrawStatuses[csdefine.PET_WITHDRAW_BUFF]		= csstatus.PET_WITHDRAW_SUCCESS_FORCE
		withdrawStatus = withdrawStatuses[withdrawMode]
		petEntity = BigWorld.entities[pet.id]
		petEntity.initialize()
		epitome.updateByPet( petEntity, self )
		epitome.updateAttr( "mapPetID", 0, self )
		self.__actPet = None
		if withdrawMode == csdefine.PET_WITHDRAW_FREE :							# ����Ƿ�������
			self.pcg_removePet_( pet.databaseID, csdefine.DELETEPET_FREEPET )								# ���б���ɾ��Ҫ�����ĳ���
			petEntity.destroy( deleteFromDB = True )							# ��ͬʱɾ�����ݿ��¼
			self.cell.pcg_onFreeResult( csstatus.PET_FREE_SUCCESS )
			return
		else :
			petEntity.destroy()
		if withdrawMode == csdefine.PET_WITHDRAW_CONJURE :						# �������Ϊ����һ���µĳ�������յ�ǰ����
			self.pcg_conjurePet( *self.__tmpConjureArgs )						# ���ڻ��պ��ٳ��������µĳ������
			del self.__tmpConjureArgs											# ɾ������ʱ�������ʱ����
		if hasattr( self, "cell" ) :
			self.cell.pcg_onWithdrawResult( epitome.getCellPetEpitome(), withdrawStatus )


	# ----------------------------------------------------------------
	# define methods
	# ----------------------------------------------------------------
	def pcg_renamePet( self, dbid, newName ) :
		"""
		defined method
		����������
		"""
		def respond( status, *arg ) :
			self.cell.pcg_onRenameResult( status )
			self.statusMessage( status, *arg )

		epitome = self.__petEpitomes.get( dbid, None )
		if epitome is None :											# ���ﲻ����
			respond( csstatus.PET_RENAME_FAIL_NOT_EXIST )
			return

		oldName = epitome.getDisplayName()

		def onRename( oldName, res ) :
			if res < 0 :
				respond( csstatus.PET_RENAME_FAIL_UNKNOW )
			else :
				respond( csstatus.PET_RENAME_SUCCESS, oldName, newName )
		epitome.updateAttr( "name", newName, self, Functor( onRename, oldName ) )	# ����û�����Ļ���ֱ���޸� epitome��������

	def pcg_catchPet( self, monsterClassName, level, modelNumber, defSkillIDs, catchType, isBinded, needResetLevel = False, isCatch = True ) :
		"""
		��׽����
		"""
		className = g_objFactory.getObject( monsterClassName ).mapPetID
		vpet = g_objFactory.getObject( className )
		if vpet is None :
			self.statusMessage( csstatus.PET_CATCH_FAIL_INFO_LOST )
			return

		def onCatchPet( epitome ) :
			if epitome is None :
				ERROR_MSG( "save pet fail, after catched!" )
				self.statusMessage( csstatus.PET_CATCH_FAIL_NUKNOW )
			else :
				self.pcg_addPet_( epitome, csdefine.ADDPET_CATCHPET )
				if isCatch:		#ͨ����׽���
					self.statusMessage( csstatus.PET_CATCH_SUCCESS, epitome.getDisplayName() )
				else:
					self.statusMessage( csstatus.PET_HATCH_SUCCESS, epitome.getDisplayName() )
				# LOG ��Ϣ 17:55 2008-7-21 yk
				species = epitome.getAttr("species")
				LOG_MSG( "databaseID(%i), playerName(%s), playerClass(%i), playerLevel(%i), mapMonster(%s), petLevel(%i), petName(%s), hierarchy(%i), ptype(%i), ability(%i)"
					%( self.databaseID, self.getName(), self.getClass(), self.level, epitome.getAttr("mapMonster"), epitome.getAttr("level"), epitome.getAttr("uname"),\
						species & csdefine.PET_HIERARCHY_MASK, species & csdefine.PET_TYPE_MASK, epitome.getAttr("ability") ) )
		vpet.catchPet( self.databaseID, monsterClassName, level, modelNumber, onCatchPet, defSkillIDs, catchType, isBinded, needResetLevel )

	# -------------------------------------------------
	def pcg_conjurePet( self, dbid, position, direction ) :
		"""
		defined method
		�������
		"""
		if self.__actPet :																# ����г�������
			self.__tmpConjureArgs = ( dbid, position, direction )						# ������ʱ�õ��Ĳ�����ʱ��������
			self.__actPet.withdraw( csdefine.PET_WITHDRAW_CONJURE )						# ���Ȼ��յ�ǰ�����ĳ���
			return

		epitome = self.__petEpitomes[dbid]												# Ҫ������ epitome
		if epitome.getAttr( "life" ) <= 0 :												# �����ľ�
			self.cell.pcg_onConjureResult( 0, None )									# �򣬳���ʧ��
			self.statusMessage( csstatus.PET_CONJURE_FAIL_LESS_LIFE )
			return
		joyancyLimit = formulas.getConjureJoyancyLimit()								# ���ٳ������ֶ�
		if epitome.getAttr( "joyancy" ) < joyancyLimit :								# ��������ֶȲ���
			self.cell.pcg_onConjureResult( 0, None )									# �򣬳���ʧ��
			self.statusMessage( csstatus.PET_CONJURE_FAIL_LESS_JOYANCY, joyancyLimit )
			return

		def onConjurePet( pet, dbid, wasActive ) :
			status = csstatus.PET_CONJURE_SUCCESS
			if pet is None :
				self.__actPetDBID = 0
				self.cell.pcg_onConjureResult( 0, None )
				ERROR_MSG( "the pet has conjured!" )
				self.statusMessage( csstatus.PET_CONJURE_FAIL_UNKNOW )
			elif wasActive :
				ERROR_MSG( "the pet which id is %d has conjured" % dbid )
			else :
				petEntity = BigWorld.entities[pet.id]
				self.conjurePosition = position
				self.conjureDirection = direction
				petEntity.initialize( self )
				self.__petEpitomes[dbid].updateAttr( "mapPetID", pet.id, self )
				petEntity.createCellEntity( self.cell )
				self.__actPetDBID = dbid
				self.__actPet = petEntity
				self.statusMessage( csstatus.PET_CONJURE_SUCCESS )
				self.cell.pcg_onConjureResult( dbid, petEntity )

		BigWorld.createBaseLocallyFromDBID( "Pet", dbid, onConjurePet )

	def pcg_freePet( self, dbid ) :
		"""
		��������
		"""
		if dbid not in self.__petEpitomes :									# Ҫ�����ĳ��ﲻ����
			self.cell.pcg_onFreeResult( csstatus.PET_FREE_FAIL_NOT_EXIST )
			return

		def onFreePet( res ) :
			if res :														# ɾ������ɹ�
				self.pcg_removePet_( dbid, csdefine.DELETEPET_FREEPET  )									# ɾ���б��еĳ���
				self.cell.pcg_onFreeResult( csstatus.PET_FREE_SUCCESS )
			else :															# ɾ�����ݿ��¼ʧ��
				self.cell.pcg_onFreeResult( csstatus.PET_FREE_FAIL_UNKNOW )
		BigWorld.deleteBaseByDBID( "Pet", dbid, onFreePet )

	# -------------------------------------------------
	def pcg_combinePets( self, level, dbid ) :
		"""
		�ϳɳ���
		"""
		if self.__actPet is None :														# ���������������������������ݴ� cell �� base ����Ĺ�����
			self.cell.pcg_onCombineResult( csstatus.PET_COMBINE_FAIL_NOT_OUT, "" )		# ��������պ���ʧ��
			return

		epitome = self.__petEpitomes.get( dbid, None )
		if epitome is None :
			self.cell.pcg_onCombineResult( csstatus.PET_COMBINE_FAIL_NOT_EXIST, "" )
			return
		hierarchy = formulas.getHierarchy( epitome.getAttr( "species" ) )
		if hierarchy != csdefine.PET_HIERARCHY_GROWNUP :
			self.cell.pcg_onCombineResult( csstatus.PET_COMBINE_FAIL_GROWNUP_NEED, "" )
			return
		if epitome.getAttr( "level" ) < level and level-epitome.getAttr( "level" ) > 5 : # ���¹��򣺲��ϳ���ĵȼ���ͱ�Ŀ������5��
			self.cell.pcg_onCombineResult( csstatus.PET_COMBINE_FAIL_LEVEL_SHORT, "" )
			return
		ability = epitome.getAttr( "ability" )
		if ability <= 0 :
			self.cell.pcg_onCombineResult( csstatus.PET_COMBINE_FAIL_LACK_ABILITY, "" )
			return
		self.pcg_removePet_( dbid, csdefine.DELETEPET_COMBINEPETS )
		calcaneus = formulas.abilityToCalcaneus( ability )
		upFlag = self.__actPet.addCalcaneus( calcaneus )
		args = ( calcaneus, )
		dialogID = csstatus.PET_COMBINE_SUCCESS
		if upFlag :
			args += ( calcaneus, )
			dialogID = csstatus.PET_COMBINE_SUCCESS_UP
		args = str( args )
		self.cell.pcg_onCombineResult( dialogID, args )

		def onCombinePets( success ) :
			if not success:
				ERROR_MSG( "player( %s ) delete pet( dbid:%i ) from tbl_Pet." )
		BigWorld.deleteBaseByDBID( "Pet", dbid, onCombinePets )

	def pcg_addLife( self, dbid, value ) :
		"""
		��������
		"""
		epitome = self.__petEpitomes.get( dbid, None )
		if epitome is None :
			self.cell.pcg_onAddLifeResult( csstatus.PET_ADD_LIFE_FAIL_NOT_EXIST )
			return
		oldLife = epitome.getAttr( "life" )
		if oldLife >= csconst.PET_LIFE_UPPER_LIMIT :
			self.cell.pcg_onAddLifeResult( csstatus.PET_ADD_LIFE_FAIL_FULL )
			return

		def onAddLife( epitome, oldLife, success ) :
			if not success :
				self.cell.pcg_onAddLifeResult( csstatus.PET_ADD_LIFE_FAIL_UNKNOW )
			elif oldLife == 0 :
				self.cell.pcg_onAddLifeResult( csstatus.PET_ADD_LIFE_SUCCESS )
				self.statusMessage( csstatus.PET_ADD_LIFE_SUCCESS_RELIVE, epitome.getDisplayName() )
			else :
				self.cell.pcg_onAddLifeResult( csstatus.PET_ADD_LIFE_SUCCESS )
				self.statusMessage( csstatus.PET_ADD_LIFE_SUCCESS, epitome.getDisplayName(), value )
		life = min( oldLife + value, csconst.PET_LIFE_UPPER_LIMIT )
		life = max( 0, life )
		epitome.updateAttr( "life", life, self, Functor( onAddLife, epitome, oldLife ) )

	def pcg_addJoyancy( self, dbid, value ) :
		"""
		����ѱ��
		"""
		epitome = self.__petEpitomes.get( dbid, None )
		if epitome is None :
			self.cell.pcg_onAddJoyancyResult( csstatus.PET_ADD_JOYANCY_FAIL_NOT_EXIST )
			return
		oldJoyancy = epitome.getAttr( "joyancy" )
		if oldJoyancy >= csconst.PET_JOYANCY_UPPER_LIMIT :
			return
		def onAddJoyancy( epitome, oldJoyancy, success ) :
			if success == 0 :
				self.cell.pcg_onAddJoyancyResult( csstatus.PET_ADD_JOYANCY_FAIL_UNKNOW )
			else :
				self.cell.pcg_onAddJoyancyResult( csstatus.PET_ADD_JOYANCY_SUCCESS )
				self.statusMessage( csstatus.PET_ADD_JOYANCY_SUCCESS, epitome.getDisplayName(), value )
		joyancy = min( oldJoyancy + value, csconst.PET_JOYANCY_UPPER_LIMIT )
		joyancy = max( 0, joyancy )
		epitome.updateAttr( "joyancy", joyancy, self, Functor( onAddJoyancy, epitome, oldJoyancy ) )


	# ----------------------------------------------------------------
	# callbacks of engine
	# ----------------------------------------------------------------
	def onWriteToDB( self, cellData ) :
		"""
		when writeToDB is called, it will be called
		"""
		pass

	def onGetCell( self ) :
		"""
		"""
		PetFoster.onGetCell( self )
		self.__initPets()

	def onClientGetCell( self ):
		pass


	def onLoseCell( self ) :
		"""
		when my cell entity has lost, it will be called by engine
		"""
		if self.__actPet is not None :
			self.__actPet.withdraw( csdefine.PET_WITHDRAW_OFFLINE )

	def onClientDeath( self ) :
		"""
		when my client is death, it will be called by engine
		"""
		if self.__actPet is not None :
			self.__actPet.withdraw( csdefine.PET_WITHDRAW_OFFLINE )

	def pcg_addActPetExp( self, value ):
		"""
		Define Method.
		����ҳ�ս�ĳ���Ӿ���
		"""
		if self.__actPet is not None and hasattr( self.__actPet, "cell" ):
			self.__actPet.cell.addEXP( value )
	
	def pcg_setActionMode( self, mode ):
		"""
		define method
		�����˳�����Ϊģʽ
		"""
		self.petModeRecord["lastActPet_aMode"] = mode
	
	def pcg_setTussleMode( self, mode ):
		"""
		define method
		�����˳���ս��ģʽ
		"""
		self.petModeRecord["lastActPet_tMode"] = mode

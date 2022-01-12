# -*- coding: gb18030 -*-
#
# $Id: Pet.py,v 1.33 2008-08-11 02:43:55 huangyongwei Exp $

"""
This module implements the pet entity.

2007/07/01: writen by huangyongwei
2007/10/24 : base on new version documents, it is rewirten by huangyongwei
"""

import BigWorld
import csarithmetic
import csdefine
import csstatus
import csconst
from bwdebug import *
from PetFormulas import formulas
from PetEpitome import PetEpitome
from interface.GameObject import GameObject
from ObjectScripts.GameObjectFactory import g_objFactory
import Love3
g_skills = Love3.g_skills
g_cooldowns = Love3.g_cooldowns

# --------------------------------------------------------------------
# implement pet class
# --------------------------------------------------------------------
class Pet( BigWorld.Base, GameObject ) :
	"""
	@type				ownerDBID : INT64
	@ivar				ownerDBID : my owner database id
	@type				owner	  : my owner's mailbox
	@ivar				owner	  : MAILBOX
	"""
	def __init__( self ) :
		BigWorld.Base.__init__( self )
		GameObject.__init__( self )
		self.__withdrawMode = csdefine.PET_WITHDRAW_OFFLINE
		self.__destroyCell = False									# ����Ƿ���Ҫ�� onGetCell ��ʱ��ɾ�� cell
		self.onRestoreCooldown( self.cellData["attrCooldowns"] )	# ����entityMailbox�Ƿ���ڣ����Ƕ�����ָ�cooldown
		self.onRestoreBuffs( self.cellData["attrBuffs"] )

	# ----------------------------------------------------------------
	# public called by owner
	# ----------------------------------------------------------------
	def getEpitome( self ) :
		petEpitome = PetEpitome()
		petEpitome.updateByPet( self )
		return petEpitome

	# -------------------------------------------------
	def initialize( self, owner = None ) :
		"""
		when my owner enter world and init me, it will be called to initialize my attributes which is not store in database
		@return						 : None
		"""
		if owner is not None :
			self.baseOwnerID = owner.id
			self.cellData["baseOwner"] = owner
			self.cellData["ownerID"] = owner.id
			self.cellData["position"] = owner.conjurePosition
			self.cellData["direction"] = owner.conjureDirection
			mapMonster = g_objFactory.getObject( self.mapMonster )
			if mapMonster is None :
				ERROR_MSG( "can't find mapping monster!" )
			else :
				models = mapMonster.getEntityProperty( "modelNumber" )
				if self.cellData["modelNumber"] not in models and len( models ) :
					self.cellData["modelNumber"] = models[0]
				if mapMonster.getEntityProperty( "petModelScale" ) > 0.0001:		# ��������˳�������ű���ֵ���Դ�ֵ���г�������� 2008-12-5 add by gjx
					self.cellData["modelScale"] = mapMonster.getEntityProperty( "petModelScale" )
				else:
					self.cellData["modelScale"] = mapMonster.getEntityProperty( "modelScale" )
			
			# ������������ϴεĳ���ָ�ս��ģʽ����Ϊģʽ CSOL-2398
			if owner.petModeRecord["lastActPet_dbid"] == self.databaseID:
				self.cellData["actionMode"] = owner.petModeRecord["lastActPet_aMode"]
				self.cellData["tussleMode"] = owner.petModeRecord["lastActPet_tMode"]
			else:
				owner.petModeRecord["lastActPet_dbid"] = self.databaseID
				owner.petModeRecord["lastActPet_aMode"] = csdefine.PET_ACTION_MODE_FOLLOW
				owner.petModeRecord["lastActPet_tMode"] = csdefine.PET_TUSSLE_MODE_GUARD
				self.cellData["actionMode"] = csdefine.PET_ACTION_MODE_FOLLOW
				self.cellData["tussleMode"] = csdefine.PET_TUSSLE_MODE_GUARD

		self.cellData["databaseID"] = self.databaseID
		self.cellData["takeLevel"] = self.getTakeLevel()
		species = self.cellData["species"]
		level = self.cellData["level"]
		nimbus =  self.cellData["nimbus"]
		sndAttrRadies = formulas.getSndProperties( species, level, nimbus )
		self.cellData["corporeity"] = sndAttrRadies["corporeity"] + self.cellData["e_corporeity"]
		self.cellData["strength"] = sndAttrRadies["strength"] + self.cellData["e_strength"]
		self.cellData["intellect"] = sndAttrRadies["intellect"] + self.cellData["e_intellect"]
		self.cellData["dexterity"] = sndAttrRadies["dexterity"] + self.cellData["e_dexterity"]

	def withdraw( self, withdrawMode ) :
		"""
		withdraw my self, notify by my owner
		@type				withdrawMode : bool
		@param				withdrawMode : defined in common/csdefine.py: PET_WITHDRAW_OFFLINE/PET_WITHDRAW_DEAD/PET_WITHDRAW_COMMON
		@return							 : None
		"""
		self.__withdrawMode = withdrawMode
		if hasattr( self, "cell" ) :									# ����� cell entity
			try :
				self.destroyCellEntity()								# ��ɾ�� cell entity
			except :
				self.__destroyCell = True								# �����ڳ�ʼ�� cell������û��ʼ����ϵ�ʱ������쳣
		else :
			owner = BigWorld.entities.get( self.baseOwnerID, None )
			if owner :
				owner.pcg_onWithdrawPet( self, withdrawMode )
			else :
				self.destroy()


	# ----------------------------------------------------------------
	# callbacks of engine
	# ----------------------------------------------------------------
	def onGetCell( self ) :
		"""
		when my cell is created it will be called
		"""
		if self.__destroyCell :
			self.destroyCellEntity()
			self.__destroyCell = False

	def onLoseCell( self ) :
		"""
		when my cell is lost, it will be called
		"""
		owner = BigWorld.entities.get( self.baseOwnerID, None )
		if owner :
			owner.pcg_onWithdrawPet( self, self.__withdrawMode )
		else :
			self.destroy()

	def onWriteToDB( self, cellData ):
		"""
		see also api_python/python_base.chm
		"""
		# check cooldown
		self.onSaveCooldown( cellData["attrCooldowns"] )
		self.onSaveBuffs( cellData["attrBuffs"] )

	def onSaveCooldown( self, cooldownsInstance ):
		"""
		cooldownд�����ݿ�ʱ�Ĵ���
		"""
		dels = []
		for cd in cooldownsInstance:
			try:
				cooldown = g_cooldowns[ cd ]
			except KeyError:
				dels.append( cd ) 	# cooldown ���Ͳ�������ɾ����������Ŀ������ֶ��޸������ݿ��������Ѵ��ڵľɵ�cooldown
				continue

			cdData = cooldownsInstance[ cd ]
			endTime = cdData[ 2 ]
			if cooldown.isTimeout( endTime ):
				dels.append( cd )	# ɾ���ѹ�ʱ��cooldown
				continue

			if cooldown.isSave():
				cooldownsInstance[ cd ] = cooldown.calculateOnSave( cdData )
			else:
				dels.append( cd )	# �������cooldownȫ��ɾ��

		for cd in dels:
			cooldownsInstance.pop( cd )

	def onRestoreCooldown( self, cooldownsInstance ):
		"""
		�ָ�cooldown���������㣬���ô˷�����Ч�����ڵ���createCellEntity()֮ǰ����
		"""
		dels = []
		for cd in cooldownsInstance:
			try:
				cooldown = g_cooldowns[ cd ]
			except KeyError:
				dels.append( cd ) 	# cooldown ���Ͳ�������ɾ����������Ŀ������ֶ��޸������ݿ��������Ѵ��ڵľɵ�cooldown
				continue

			cdData = cooldownsInstance[ cd ]
			cooldownsInstance[ cd ] = cooldown.calculateOnLoad( cdData )
			endTime = cooldownsInstance[ cd ][2]
			# ��coolDown���ݻָ�֮������жϣ�ɾ���ѹ�ʱ��coolDown
			if cooldown.isTimeout( endTime ):
				dels.append( cd )

		for cd in dels:
			cooldownsInstance.pop( cd )

	def onSaveBuffs( self, buffsInstance ):
		"""
		buff�����ݿ���д��ʱ�Ĵ���
		"""
		rmb = []
		for idx, buff in enumerate( buffsInstance ):
			try:
				spell = g_skills[buff["skill"]["id"]]
			except KeyError:
				rmb.append( idx )
				continue

			if spell.isSave():
				buff["persistent"] = spell.calculateOnSave( buff["persistent"] )
			else:
				rmb.append( idx )

		rmb.reverse()	# �Ӻ�����ǰɾ��
		for r in rmb:
			buffsInstance.pop( r )

	def onRestoreBuffs( self, buffsInstance ):
		"""
		�ָ�buff���������㣬���ô˷�����Ч�����ڵ���createCellEntity()֮ǰ����
		"""
		buffIndex = 0
		rmb = []
		bt = time.time()
		for idx, buff in enumerate( buffsInstance ):
			try:
				spell = g_skills[buff["skill"]["id"]]
			except KeyError:
				rmb.append( idx )
				continue

			buff[ "index" ]	= buffIndex
			buffIndex += 1
			t = spell.calculateOnLoad( buff["persistent"] )	# �����Ȼָ�������ж�buff�Ƿ����
			buff[ "persistent" ] = t

		rmb.reverse()	# �Ӻ�����ǰɾ��
		for r in rmb:
			buffsInstance.pop( r )

	# ----------------------------------------------------------------
	# bridge methods
	# ----------------------------------------------------------------
	def addCalcaneus( self, calcaneus ) :
		if hasattr( self, "cell" ) :
			self.cell.remoteCall( "addCalcaneus", ( calcaneus, ) )
		else :
			calcaneus += self.cellData["calcaneus"]
			hierarchy = self.cellData["species"] & csdefine.PET_HIERARCHY_MASK
			maxNimbus = formulas.getMaxNimbus( self.cellData["level"] )
			up = self.cellData["nimbus"] # ���Գ�ʼֵ
			newNimbus, newCalcaneus = formulas.calcaneusToNimbus( maxNimbus, up, calcaneus )
			up = newNimbus - up # �����Ƿ�������
			self.cellData["nimbus"] = newNimbus
			self.cellData["calcaneus"] = newCalcaneus
			return up

	def getTakeLevel( self ):
		"""
		��ȡ�����Я���ȼ�
		"""
		return g_objFactory.getObject( self.mapMonster ).takeLevel
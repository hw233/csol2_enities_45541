# -*- coding: gb18030 -*-
#
# $Id: PetCage.py,v 1.59 2008-09-05 01:39:19 zhangyuxing Exp $

"""
This module implements the pet entity.

2007/07/01: writen by huangyongwei
2007/10/24: according to new version documents, it is rewriten by huangyongwei
"""

import time
import random
import BigWorld
import csdefine
import csconst
import csstatus
import ECBExtend
import items
from bwdebug import *
from PetFormulas import formulas
from ChatProfanity import chatProfanity
from PetTrainer import PetTrainer
from PetStorage import PetStorage
from PetFoster import PetFoster
from SkillTargetObjImpl import createTargetObjEntity
from ObjectScripts.GameObjectFactory import g_objFactory
from Love3 import g_skills
from VehicleHelper import  getCurrVehicleSkillIDs, isFlying
from Domain_Fight import g_fightMgr
import Language
import utils

# --------------------------------------------------------------------
# implement active pet
# --------------------------------------------------------------------
class _ActivePet( object ) :
	__slots__ = ( "dbid", "etype", "entity" )

	def __init__( self, dbid, mbBase ) :
		self.dbid = dbid
		entity = BigWorld.entities.get( mbBase.id )
		if entity is None :
			self.etype = "MAILBOX"
			self.entity = mbBase.cell
		elif entity.isReal() :
			self.etype = "REAL"
			self.entity = entity
		else :
			self.etype = "GHOST"
			self.entity = entity


# --------------------------------------------------------------------
# implement pet cage class
# --------------------------------------------------------------------
class PetCage( PetTrainer, PetStorage, PetFoster ) :
	def __init__( self ) :
		PetTrainer.__init__( self )						# ����
		PetStorage.__init__( self )						# �ֿ�
		PetFoster.__init__( self )						# ��ֳ
		self.pcg_releaseOperating_()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def pcg_lockOperation_( self ) :
		"""
		����������������������Ϊ�˷�ֹĳ��������û�� base ���� cell ����ʱ����һ�������ֳ���
		�����������ĳЩ��Ʒ���Ǯ����������ֻ�������һ�εģ������β�����ͨ����
		"""
		if self.__operateTime + 5.0 > time.time() :
			self.statusMessage( csstatus.GB_OPERATE_FREQUENTLY )
			return False
		self.__operateTime = time.time()
		return True

	def pcg_releaseOperating_( self ) :
		"""
		ȡ����ǰ�ķ�æ״̬
		"""
		self.__operateTime = 0.0

	def pcg_isTradingPet_( self, dbid ) :
		"""
		�ж�ĳ�����ﵱǰ�Ƿ��ڽ���״̬
		"""
		if self.isPetInSwap( dbid ):
			self.statusMessage( csstatus.PET_OPERATE_REFUSE_IN_TRADING )
			return True
		return False


	# ----------------------------------------------------------------
	# �� base ���صĵ���
	# ----------------------------------------------------------------
	def pcg_onAddPet( self, epitome ) :
		"""
		defined method
		��������һ�������ʱ�򱻵���
		@type				epitome : common.CellPetEpitome
		@param				epitome : ������ cell ���ֵ�����Ӱ��
		"""
		self.pcg_petDict.add( epitome.databaseID, epitome, self )
		self.questPetAmountChange( 1 )
		self.questPetAmountAdd( epitome.mapMonster, epitome.databaseID )

	def pcg_onRemovePet( self, dbid ) :
		"""
		defined method
		��һ�����ﱻɾ����ʱ�򱻵���
		@type				dbid : INT64
		@param				dbid : ��ɾ���ĳ�������ݿ� ID
		"""
		if self.pcg_petDict.has_key( dbid ) :
			petData = self.pcg_petDict.get( dbid )
			self.questPetAmountSub( petData.mapMonster, petData.databaseID )
			self.pcg_petDict.remove( dbid, self )
			self.questPetAmountChange( -1 )
			if self.pcg_actPetDBID == dbid:
				self.pcg_actPetDBID = 0

	# -------------------------------------------------
	def pcg_onConjureResult( self, petDBID, basePet ) :
		"""
		defined method
		�����������ķ���
		@type					petDBID : INT64
		@param					petDBID : ������������ݿ� ID
		@type					basePet : MAILBOX
		@param					basePet : ��������� base mailbox
		"""
		if petDBID > 0 :
			self.pcg_actPetDBID = petDBID
			self.pcg_mbBaseActPet = basePet
			self.client.pcg_onPetConjured( petDBID )
			actPet = self.pcg_getActPet()
			pet = actPet.entity
			pet.planesID = self.planesID
			self.onPetConjureNotifyTeam( pet.id, pet.uname, pet.name, pet.modelNumber, pet.species )

			self.questPetActChanged()								# �������ٻ��������񡱱�Ǹ�������� 2009-07-15	15:00 SPF
			for i, v in self.enemyList.iteritems():
				enemy = BigWorld.entities.get( i )
				if enemy:
					g_fightMgr.buildEnemyRelation( pet, enemy )
		self.removeTemp( "pcg_conjuring_dbid" )						# ����������� DBID ����ʱ����
		self.pcg_releaseOperating_()								# ���� base ���������ʱ�򣬲������������������������

	def pcg_onWithdrawResult( self, epitome, result ) :
		"""
		defined method
		�������ʱ������
		@type					result : MACRO DEFINATION
		@param					result : ���ս������ common.csstatus �ж���
		"""
		if result == csstatus.PET_WITHDRAW_SUCCESS_FREE :			# �����������Ϊ���������յĻ�
			self.questPetActChanged()								# �������ｫ���ٻ�������������Ϊδ��� 2009-07-15	15:00 SPF
		elif result != csstatus.PET_WITHDRAW_SUCCESS_CONJURE :		# ������Ƿ������գ�Ҳ���ǳ�ս����
			self.statusMessage( result )							# ����ͻ���������ս����Ϣ�����򣬲����ͻ��ս����Ϣ��
			self.pcg_releaseOperating_()							# ����������
		if result != csstatus.PET_WITHDRAW_FAIL_NOT_OUT :			# ������ճɹ�
			self.pcg_petDict.update( epitome.databaseID, epitome, self )# ���·ǳ�ս���������
			self.client.pcg_onPetWithdrawed()
			self.pcg_actPetDBID = 0									# �򣬽�����������Ϣ���
			self.questPetActChanged()								# ���ճ��ｫ���ٻ�������������Ϊδ��� 2009-07-15	15:00 SPF
			self.onPetWithdrawNotifyTeam()					# �ջس���֪ͨ����

	def pcg_onFreeResult( self, result ) :
		"""
		defined method
		���������ʱ������
		@type					result : MACRO DEFINATION
		@param					result : ����������� scstatus �ж���
		"""
		self.statusMessage( result )
		self.pcg_releaseOperating_()
		self.onPetWithdrawNotifyTeam()

	# -------------------------------------------------
	def pcg_onRenameResult( self, result ) :
		"""
		defined method
		��������� base ����
		@type					result : MACRO DEFINATION
		@param					result : ���������ؽ������ csstatus �ж���
		"""
		self.pcg_releaseOperating_()								# �ͷŲ�������

	# -------------------------------------------------
	def pcg_onCombineResult( self, result, args ) :
		"""
		defined method
		����ϳ�ʱ��base �ķ��ؽ��
		@type					result : MACRO DEFINATION
		@param					result : �ϳɷ��ؽ������ csstatus �ж���
		"""
		self.client.onStatusMessage( result, args )
		self.unfreezeMoney()										# ������Ǯ����Ϊ�ϳ�ʱ��Ҫ�õ���Ǯ��
		self.pcg_releaseOperating_()								# ��������
		if result in [csstatus.PET_COMBINE_SUCCESS,csstatus.PET_COMBINE_SUCCESS_UP] :
			self.questPetEvent( "combine" )

	def pcg_onAddLifeResult( self, result ) :
		"""
		defined method
		��������ֵʱ�ķ��ؽ��
		@type					result : MACRO DEFINATION
		@param					result : ���������ķ��ؽ������ csstatus �ж���
		"""
		if result == csstatus.PET_ADD_LIFE_SUCCESS :
			itemSeat0 = self.queryTemp( "pcg_add_life_item_seat", None )	# ɾ�����ٵ�
			if itemSeat0:
				self.removeItem_( itemSeat0, 1 , csdefine.DELETE_ITEM_PET_ADDLIFE )			# ɾ�����ٵ�
		else :
			self.statusMessage( result )
		self.removeTemp( "pcg_add_life_item_seat" )
		self.pcg_releaseOperating_()										# �����������

	def pcg_onAddJoyancyResult( self, result ) :
		"""
		defined method
		���ӿ��ֶ�ʱ�ķ��ؽ��
		@type					result : MACRO DEFINATION
		@param					result : ���ӿ��ֶȵķ��ؽ������ csstatus �ж���
		"""
		if result == csstatus.PET_ADD_JOYANCY_SUCCESS :
			itemSeat0 = self.queryTemp( "pcg_add_joyancy_item_seat", None )	# ������ �� ������
			self.questPetEvent( "joyancy" )
			if itemSeat0:
				self.removeItem_( itemSeat0, 1, csdefine.DELETE_ITEM_PET_ADDJOYANCY )				# ɾ��һ�������������
		else :
			self.statusMessage( result )
		self.removeTemp( "pcg_add_joyancy_item_seat" )
		self.pcg_releaseOperating_()										# �����������

	def pcg_onUpdatePetEpitomeAttr( self, databaseID, attrName, value ):
		"""
		Define method.
		petδ��ս��������Ըı䣬���µ�cell

		@param databaseID : ���Ըı��petDBID
		@type databaseID : DATABASE_ID
		@param attrName : ��������
		@type attrName : STRING
		@param value : ����ֵ
		@type value : PYTHON
		"""
		self.pcg_petDict.get( databaseID ).update( attrName, value, self )

	# ----------------------------------------------------------------
	# methods called by active pet
	# ----------------------------------------------------------------
	def pcg_teleportPet( self ) :
		"""
		<Define method>
		��������ת�����
		ע�⣺�����Խ����ص� ActivePet ���������Թ�����ʹ�á�
		@type			mbBasePet : MAILBOX
		@param			mbBasePet : ����� base mailbox
		"""
		actPet = self.pcg_getActPet()												# ���ﲻ��Ҫ�ж��Ƿ��г��������ˣ������ȷ���Ƿ��г������
																					# �ڵ��ø÷���֮ǰ�����ж��Ƿ��г�������
		pos = formulas.getPosition( self.position, self.yaw )						# �������λ�û�ȡ�������ʱ��λ��
		pos = utils.navpolyToGround(self.spaceID, pos, 5.0, 5.0)					# ȡ�����ϵĵ�
		actPet.entity.teleportToEntity( self.spaceID, self, pos, self.direction )


	# ----------------------------------------------------------------
	# public methods ���� NPC �Ի�ʱ����
	# ----------------------------------------------------------------
	def pcg_dlgCanCombinePet( self ) :
		"""
		�ж��ͷſ��Ժϳ�
		"""
		return self.pcg_hasActPet()

	def pcg_dlgCombinePet( self, npcEntity ) :
		"""
		��ʾ�� NPC �Ի�Ҫ�ϳɳ���Ի���
		"""
		if self.pcg_hasActPet() :
			self.client.pcg_onShowCombineDialog()
		else :
			self.statusMessage( csstatus.PET_COMBINE_FAIL_NOT_OUT )


	# ----------------------------------------------------------------
	# public methods
	# ----------------------------------------------------------------
	def pcg_onCellPetChange( self ):
		"""
		for real & ghost
		�������ݸı䣬����bw��ͨ�Ż��ƣ����봥��"="�����Ż��pcg_petDict���ݹ㲥��ȥ
		�÷����� common/CellPetDict:CellPetEpitome �е���
		"""
		self.pcg_petDict = self.pcg_petDict

	# -------------------------------------------------
	def pcg_getPetCount( self ) :
		"""
		for real & ghost
		��ȡ��ǰЯ�����������
		"""
		return self.pcg_petDict.count()

	def pcg_getKeepingCount( self ) :
		"""
		for real & ghost
		��ȡ��ǰ����Я��������������
		"""
		return formulas.getKeepingCount( self.pcg_reinBible )

	def pcg_isFull( self ) :
		"""
		for real & ghost
		�жϵ�ǰЯ���ĳ����Ƿ��Ѿ��ﵽ����
		"""
		return self.pcg_getPetCount() >= self.pcg_getKeepingCount()

	def pcg_isOverbrim( self, count ) :
		"""
		for real & ghost
		�ж����� count ��������Ƿ��ﵽЯ������
		@type				count : int
		@param				count : Ҫ���ӵ�Я����������
		"""
		return self.pcg_getPetCount() + count > self.pcg_getKeepingCount()

	# ---------------------------------------
	def pcg_hasActPet( self ) :
		"""
		for real & ghost
		�Ƿ��г�������
		"""
		return self.pcg_actPetDBID > 0

	def pcg_isActPet( self, dbid ) :
		"""
		for real & ghost
		�ж�ָ���ĳ����Ƿ��ǳ�������
		"""
		if dbid == 0 : return False
		return self.pcg_actPetDBID == dbid

	def pcg_isPetBinded( self, dbid ):
		"""
		�����Ƿ񱻰�
		"""
		return self.pcg_petDict.get( dbid ).isBinded

	def pcg_getActPet( self ) :
		"""
		for real & ghost
		��ȡ�������� ActivePet( ��ģ�鶥������ )
		@rtype					: _ActivePet
		@return					: ��������ģ������û�г�������򷵻� None
		"""
		if self.pcg_actPetDBID == 0 : return None
		return _ActivePet( self.pcg_actPetDBID, self.pcg_mbBaseActPet )

	def pcg_isConjuring( self, dbid ):
		"""
		for real
		�����Ƿ����ڱ��ٻ���
		"""
		return self.queryTemp( "pcg_conjuring_dbid", 0 ) == dbid

	# -------------------------------------------------
	def pcg_catchPet( self, monsterClassName, level, modelNumber, catchType, isCatch, needResetLevel = False ) :
		"""
		for real
		��׽һ��������Ϊ����
		@type			monsterClassName : str
		@param			monsterClassName : ����� ID
		@type			level			 : UINT8
		@param			level			 : ����ȼ�
		@type			modelNumber		 : str
		@param			modelNumber		 : ����ģ�ͺ�
		@type			needResetLevel	:BOOL
		@param			needResetLevel	:�Ƿ�ǿ�����õȼ�Ϊ1
		@return							 : None
		"""
		className = g_objFactory.getObject( monsterClassName ).mapPetID
		vpet = g_objFactory.getObject( className )
		if self.pcg_isFull() :
			self.statusMessage( csstatus.PET_CATCH_FAIL_OVERRUN )
		else :
			defSkillIDs = vpet.getDefSkillIDs( level  )				# ����ǰ׺
			self.base.pcg_catchPet( monsterClassName, level, modelNumber, defSkillIDs, catchType, False, needResetLevel,isCatch )

	def pcg_onEnhanceResult( self, *args ) :
		"""
		for real
		����ǿ��ʱ��base �ķ��ؽ��
		@type					result : MACRO DEFINATION
		@param					result : ǿ�����ؽ������ csstatus �ж���
		"""
		result = args[0]
		if result == csstatus.PET_ENHANCE_SUCCESS :							# ǿ���ɹ�ʱ
			itemSeat0 = self.queryTemp( "pcg_enhance_item_seat", None )		# ���ǿ����Ҫ����Ʒ
			itemSeat1 = self.queryTemp( "pcg_enhance_item_seat1", None )	# ���������㻯��
			itemSeat2 = self.queryTemp( "pcg_enhance_item_seat2", None )
			for order in [itemSeat0, itemSeat1, itemSeat2]:
				if order:
					self.removeItem_( order, 1, reason = csdefine.DELETE_ITEM_PET_ENHANCE )
			# remove item
			self.questPetEvent( "enhance" )
		self.statusMessage( *args )
		self.removeTemp( "pcg_enhance_item_seat" )
		self.removeTemp( "pcg_enhance_item_seat1" )
		self.removeTemp( "pcg_enhance_item_seat2" )
		self.pcg_releaseOperating_()										# ��������


	# ----------------------------------------------------------------
	# exposed methods
	# ----------------------------------------------------------------
	def pcg_renamePet( self, srcEntityID, dbid, newName ) :
		"""
		<Exposed/>
		����������
		@type				dbid		: INT64
		@param				dbid		: �������ݿ� ID
		@type				newName		: STRING
		@param				newName		: ������
		"""
		if not self.hackVerify_( srcEntityID ) : return									# ��֤�Ƿ�����ƭ�Ŀͻ���
		if self.pcg_isTradingPet_( dbid ) : return										# �ж�Ҫ�����ĳ����Ƿ��ڽ���״̬
		if self.pcg_isActPet( dbid ): return											# ��ս״̬���������

		illegalWord = chatProfanity.searchNameProfanity( newName )						# ��֤�����Ƿ�Ϸ�
		if illegalWord is not None :
			self.statusMessage( csstatus.PET_RENAME_FAIL_ILLEGAL_WORD, illegalWord )
		elif len( newName.decode( Language.DECODE_NAME ) ) > csconst.PET_NAME_MAX_LENGTH :			# �����Ƿ񳬳��޶�����
			self.statusMessage( csstatus.PET_RENAME_FAIL_OVERLONG )
		elif self.pcg_lockOperation_() :												# ����������ע������ý����ĵط�����ص���pcg_onRenameResult��
			self.base.pcg_renamePet( dbid, newName )

	def pcg_conjurePet( self, srcEntityID, dbid ) :
		"""
		<Exposed/>
		�ó������
		@type				dbid : INT64
		@param				dbid : Ҫ������������ݿ� ID
		"""
		if not self.hackVerify_( srcEntityID ) : return									# ��֤�Ƿ�����ƭ�Ŀͻ���
		if self.actionSign( csdefine.ACTION_FORBID_CALL_PET ) or isFlying( self ) or self.onFengQi:
			# ���ڲ��������״̬
			self.statusMessage( csstatus.PET_CAN_NOT_CONJURED )
			return

		if self.pcg_isTradingPet_( dbid ) : return										# �ж�Ҫ�����ĳ����Ƿ��ڽ���״̬
		if self.pft_procreating( dbid ) :												# �Ƿ�ѡ�����ڷ�ֳ
			self.statusMessage( csstatus.PET_PROCREATING_CANT_CONJURED )
			return
		if self.isSunBathing(): return													# �ж��Ƿ������չ�ԡ�У��������ٻ�
		if self.actionSign( csdefine.ACTION_ALLOW_DANCE ):								# �жϽ�ɫ�Ƿ���������
			self.statusMessage( csstatus.JING_WU_SHI_KE_RESTRICT_CONJURE_PET )
			return
		if self.effect_state & csdefine.EFFECT_STATE_WATCHER:							# �۲���״̬�²������ٻ�����
			self.statusMessage( csstatus.PET_CONJURE_FAIL_WATCHER )
			return
		if self.effect_state & csdefine.EFFECT_STATE_PROWL:								# Ǳ��״̬�²������ٻ�����
			self.statusMessage( csstatus.PET_CONJURE_FAIL_SNAKE )
			return

		spaceKey = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		spaceScript = g_objFactory.getObject( spaceKey )
		if not spaceScript.canConjurePet:
			self.statusMessage( csstatus.PET_CONJURE_FAIL_NOT_SPECIAL_MAP)				# canConjurePet����Ϊ0�ĸ�����ֹ�ٻ�����
			return

		if not self.pcg_lockOperation_() : return										# ����������ע������ý����ĵط�����ص���pcg_onConjureResult��
		self.setTemp( "pcg_conjuring_dbid", dbid )										# ��¼��Ҫ������������ݿ� ID
		state = self.spellTarget( csdefine.SKILL_ID_CONJURE_PET, self.id )				# ʹ�ó�������
		if state != csstatus.SKILL_GO_ON :												# ʹ�ó�������ʧ��
			self.statusMessage( state )

	def pcg_withdrawPet( self, srcEntityID ) :
		"""
		<Exposed/>
		���ճ���
		"""
		if not self.hackVerify_( srcEntityID ) : return									# ��֤�Ƿ�����ƭ�Ŀͻ���
		actPet = self.pcg_getActPet()													# ��ȡ��������
		if actPet is None :																# ���û�г�������
			self.statusMessage( csstatus.PET_WITHDRAW_FAIL_NOT_OUT )
		elif self.pcg_lockOperation_() :												# ����������ע������ý����ĵط�����ص���pcg_onWithdrawResult��
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON ) 						# ���û�г����ս

	def pcg_freePet( self, srcEntityID, dbid ) :
		"""
		<Exposed/>
		��������
		@type					dbid : INT64
		@param					dbid : Ҫ�����ĳ������ݿ� ID
		"""
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return

		if self.vend_isVendedPet( dbid ) : return										# �жϳ����Ƿ����ڰ�̯��
		if self.pcg_isTradingPet_( dbid ) : return										# �ж�Ҫ�����ĳ����Ƿ��ڽ���״̬
		if not self.hackVerify_( srcEntityID ) : return									# ��֤�Ƿ�����ƭ�Ŀͻ���
		if not self.pcg_lockOperation_() : return										# ����������ע������ý����ĵط�����ص���pcg_onFreeResult��
		actPet = self.pcg_getActPet()
		if actPet and actPet.dbid == dbid :												# ��������ĳ��ﴦ�ڳ���״̬
			actPet.entity.free()
		else :
			self.base.pcg_freePet( dbid )												# ֪ͨ base ����

	# -------------------------------------------------
	def pcg_combinePets( self, srcEntityID, dbid ) :
		"""
		<Exposed/>
		�ϳɳ���
		@type					dbid : INT64
		@param					dbid : Ҫ�ϳɳ���Ĳ��ϳ�����ݿ� ID
		"""
		if not self.hackVerify_( srcEntityID ) : return									# ��֤�Ƿ�����ƭ�Ŀͻ���
		if self.pcg_isTradingPet_( dbid ) : return										# �ж�Ҫ�����ĳ����Ƿ��ڽ���״̬
		actPet = self.pcg_getActPet()
		if actPet is None :																# ��ǰû�г�������
			self.statusMessage( csstatus.PET_COMBINE_FAIL_NOT_OUT )						# ������ϳ�
		elif actPet.dbid == dbid :														# ������ϳ��ǳ�����
			self.statusMessage( csstatus.PET_COMBINE_FAIL_SELF_MATERIAL )				# ������ϳ�
		elif self.pcg_lockOperation_() :												# ����������ע������ý����ĵط�����ص���pcg_onCombineResult��
			actPet.entity.combine( dbid )

	# -------------------------------------------------
	def pcg_enhancePet( self, srcEntityID, etype, attrName, isCurse, stoneItemUid, symbolItemUid ) :
		"""
		ǿ������
		@type					etype			 : MACRO DEFINATION
		@param					etype			 : ǿ������
		@type					attrName 		 : str
		@param					attrName 		 : Ҫǿ������������
		@type					isCurse			 : bool
		@param					isCurse			 : �Ƿ�ʹ�õ㻯��
		@param					stoneItemUid	 : ����ʯuid
		@type					stoneItemUid 	 : uid
		@param					symbolItemUid    : �㻯��uid
		@type					symbolItemUid 	 : uid
		"""
		if not self.hackVerify_( srcEntityID ) : return										# ��֤�Ƿ�����ƭ�Ŀͻ���
		actPet = self.pcg_getActPet()
		if actPet is None :																	# û�г�ս�������ǿ��
			self.statusMessage( csstatus.PET_ENHANCE_FAIL_NOT_OUT )
			return

		if not self.pcg_lockOperation_() : return											# ����������ע������ý����ĵط�����ص���pcg_onEnhanceResult��

		#�Ӷ�������ֵ
		if etype == csdefine.PET_ENHANCE_COMMON:
			count = getattr( actPet.entity, "ec_" + attrName )
		else:
			count =  actPet.entity.ec_free
		minValue,maxValue = formulas.getEnhanceValue( actPet.entity.species, etype, attrName, count + 1  )
		value = random.randint( minValue, maxValue )
		if isCurse:
			for itemID in csconst.PET_SMELT_ITEMS:
				itemInfo = self.findItemFromNKCK_( itemID )									# ������
				if itemInfo and not itemInfo.isFrozen():
					self.setTemp( "pcg_enhance_item_seat", itemInfo.order )
					value = maxValue
					break

		if etype == csdefine.PET_ENHANCE_FREE:												# ���������ǿ��
			findItem = None
#			for itemID in csconst.PET_DIRECT_ITEMS:
#				itemInfo = self.findItemFromNKCK_( itemID )									# ��Ѱ�ҵ㻯��
#				if itemInfo and not itemInfo.isFrozen():
#					findItem = itemInfo
#					break
			itemInfo = self.getItemByUid_( symbolItemUid )									# ��Ѱ�ҵ㻯��
			if itemInfo and not itemInfo.isFrozen():
				findItem = itemInfo
			if findItem:
				self.setTemp( "pcg_enhance_item_seat1", findItem.order )
			else:
				self.pcg_onEnhanceResult( csstatus.PET_ENHANCE_CURSE_NOT_FOUND )
				return

		def getStoneInfo( attrName ):
			"""
			���ǿ�����Զ�Ӧ����ʯ��Ϣ
			"""
			hasItem = False
			stoneItem = None
			maxQuality = -1
			itemlist = csconst.pet_enhance_stones.get( attrName, () )
			for itemID in itemlist :
				items = self.findItemsByIDFromNKCK( itemID )
				for item in items :
					hasItem = True
					if not item.isFull() :
						continue
					if item.isFrozen():
						continue
					quality = item.getQuality()
					if quality > maxQuality :										# �������Ʒ�ʵ�
						stoneItem = item
						maxQuality = quality
			return hasItem, stoneItem

		stoneItem = self.getItemByUid_( stoneItemUid )
		if stoneItem :
			self.setTemp( "pcg_enhance_item_seat2", stoneItem.order )				# �ҵ�����ػ���ʯ
			actPet.entity.enhance( etype, attrName, value )							# ǿ���ɹ�
		else :
			self.pcg_onEnhanceResult( csstatus.PET_ENHANCE_KA_STONE_NOT_FOUND )		# û�ҵ���Ӧ�Ļ���ʯ

	def pcg_addLife( self, srcEntityID, dbid ) :
		"""
		���ӳ�������
		@type					dbid : INT64
		@param					dbid : Ҫ�������������ݿ� ID
		"""
		if not self.hackVerify_( srcEntityID ) : return								# ��֤�Ƿ�����ƭ�Ŀͻ���
		if self.pcg_isTradingPet_( dbid ) : return									# ��֤�Ƿ��ڽ���״̬

		item = None
		for itemID in csconst.PET_ADD_LIFE_ITEMS:
			findItem = self.findItemFromNKCK_( itemID )								# Ѱ�����ٵ�
			if findItem:
				item = findItem
				break
		if item is None:															# ���û�����ٵ��򷵻�
			self.statusMessage( csstatus.PET_ADD_LIFE_FAIL_NO_STUFF )
			return

		if not self.pcg_lockOperation_() : return									# ����������ע������ý����ĵط�����ص���pcg_onAddLifeResult��
		self.setTemp( "pcg_add_life_item_seat", item.order )						# ��¼���ٵ���λ��
		value = item.query( "pet_life", 0 )
		actPet = self.pcg_getActPet()
		if actPet and actPet.dbid == dbid :											# �Գ�����������
			actPet.entity.lifeup( value )
		else :
			self.base.pcg_addLife( dbid, value )									# ��ת�� base ���������

	def pcg_addJoyancy( self, srcEntityID, dbid ) :
		"""
		���ӿ��ֶ�
		@type					dbid : INT64
		@param					dbid : Ҫ���ӿ��ֶȵĳ������ݿ� ID
		"""
		if not self.hackVerify_( srcEntityID ) : return								# ��֤�Ƿ�����ƭ�Ŀͻ���
		if self.pcg_isTradingPet_( dbid ) : return									# ��֤�Ƿ��ڽ���״̬
		if not self.pcg_petDict.has_key( dbid ) : return							# �����Ѿ������ڣ�����Ҫ�����ʾ������
		if not self.pcg_lockOperation_() : return									# ����������ע������ý����ĵط�����ص���pcg_onAddJoyancyResult��

		def getItemValue( level ) :
			"""
			��ȡ�ʺϵȼ�ѱ����Ʒ�Ŀ���ֵ
			"""
			index = level / 30															# �������Ӧ��ʹ�����಼���� ��Ϊ5��,ÿ30��Ϊһ�� �� 60�� ����2��(����Ϊ1)
			if level % 30 == 0:															# �������Ϊ 60/30 = 2 ����60�ܱ�30���� ������û�г���2�� ���� 2-1 �ó� 60Ϊ 1��
				index -= 1
			item = self.findItemFromNKCK_( csconst.pet_joyancy_items[index] )				# �����޻�������
			if item is None : return -1, -1
			if item.isFrozen(): return -1, -1
			return item.order, item.query( "joyancy", 0 )

		actPet = self.pcg_getActPet()
		if actPet and actPet.dbid == dbid :												# Ҫѱ���ĳ����Ƿ��ڳ���״̬
			if actPet.etype == "MAILBOX" :												# ��ʱ�Ҳ��������ĳ���
				self.pcg_onAddJoyancyResult( csstatus.PET_ADD_JOYANCY_FAIL_NOT_EXIST )
			else :
				order, value = getItemValue( actPet.entity.level )
				if value < 0 :															# ѱ����Ʒ������
					self.pcg_onAddJoyancyResult( csstatus.PET_ADD_JOYANCY_FAIL_NO_STUFF )
				else :
					self.setTemp( "pcg_add_joyancy_item_seat", order )					# ������ϵ�λ��
					actPet.entity.domesticate( value )									# ע���������ص���pcg_onAddJoyancyResult
		else :
			order, value = getItemValue( self.pcg_petDict.get( dbid ).level )
			if value < 0 :																# ѱ����Ʒ������
				self.pcg_onAddJoyancyResult( csstatus.PET_ADD_JOYANCY_FAIL_NO_STUFF )
			else :
				self.setTemp( "pcg_add_joyancy_item_seat", order )						# ������ϵ�λ��
				self.base.pcg_addJoyancy( dbid, value )									# ע���������ص���pcg_onAddJoyancyResult


	# ----------------------------------------------------------------
	# callback methods
	# ----------------------------------------------------------------
	def onGetPetCell( self, petMailbox ):
		"""
		Define method.
		����cell���ִ�����ϵ�֪ͨ

		@param petMailbox : �����cell mailbox
		@type petMailbox : MAILBOX
		"""
		pass

	def onDie( self ) :
		"""
		���������ʱ������
		"""
		actPet = self.pcg_getActPet()
		if actPet :
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_OWNER_DEATH )			# �����Ȼ��ճ���

	def onDestroy( self ) :
		"""
		��ɫ����ʱ������
		"""
		# ���������ڳ�������
		actPet = self.pcg_getActPet()
		if actPet:
			actPet.entity.baseOwner = None
		
		self.pcg_actPetDBID = 0													# �����ս����
		self.pcg_mbBaseActPet = None


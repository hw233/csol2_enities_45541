# -*- coding: gb18030 -*-
#
# $Id: PetFoster.py,v 1.9 2008-07-21 02:45:20 huangyongwei Exp $

"""
This module implements the pet entity.

2007/11/26: writen by huangyongwei
2009-09-01: rewrite by wangshufeng
"""

import csdefine
import csstatus
import csconst
from PetFormulas import formulas
import BigWorld
from bwdebug import *

FIND_TEAMMATE_RANGE = 20

class PetFoster :
	def __init__( self ) :
		pass

	# ----------------------------------------------------------------
	# public methods for npc dialog
	# ----------------------------------------------------------------
	def pft_dlgShowProcreateDialog( self, npcEntity ):
		if not self.isInTeam():
			self.statusMessage( csstatus.PET_PROCREATE_MUST_TEAM )
			return
		if not self.isTeamCaptain():
			self.statusMessage( csstatus.PET_PROCREATE_MUST_CAPTAIN )
			return
		teammateList = npcEntity.searchTeamMember( self.teamMailbox.id, csconst.COMMUNICATE_DISTANCE )
		if len( teammateList ) > 2:
			self.statusMessage( csstatus.PET_PROCREATE_MORE_PLAYER_IN_TEAM )
			return
		if len( teammateList ) < 2:
			self.statusMessage( csstatus.PET_PROCREATE_NOT_ONE_PLAYER )
			return
		targetEntity = teammateList[0].id == self.id and teammateList[1] or teammateList[0]
		if self.isPetProcreating():
			self.statusMessage( csstatus.PET_PROCREATE_ALREADY_HAS )
			targetEntity.client.onStatusMessage( csstatus.PET_PROCREATE_ALREADY_HAS, "" )
			return
		self.pft_changeState( csdefine.PET_PROCREATION_WAITING, targetEntity )

	def pft_dlgTakeProcreatePet( self, npcEntity ):
		if not self.isInTeam():
			self.statusMessage( csstatus.PET_PROCREATE_MUST_TEAM )
			return
		if not self.isTeamCaptain():
			self.statusMessage( csstatus.PET_PROCREATE_MUST_CAPTAIN )
			return
		teammateList = npcEntity.searchTeamMember( self.teamMailbox.id, csconst.COMMUNICATE_DISTANCE )
		if len( teammateList ) > 2:
			self.statusMessage( csstatus.PET_PROCREATE_MORE_PLAYER_IN_TEAM )
			return
		if len( teammateList ) < 2:
			self.statusMessage( csstatus.PET_PROCREATE_NOT_ONE_PLAYER )
			return
		targetEntity = teammateList[0].id == self.id and teammateList[1] or teammateList[0]
		if not self.isPetProcreating():
			self.statusMessage( csstatus.PET_PROCREATE_GET_NOT_EXIST )
			targetEntity.client.onStatusMessage( csstatus.PET_PROCREATE_GET_NOT_EXIST, "" )
			return
		if targetEntity.isReal() and not targetEntity.isPetProcreating():
			self.statusMessage( csstatus.PET_PROCREATE_GET_NOT_EXIST )
			targetEntity.statusMessage( csstatus.PET_PROCREATE_GET_NOT_EXIST )
			return
		if self.pcg_isOverbrim( 2 ):
			self.statusMessage( csstatus.PET_PROCREATE_GET_NO_SEAT )
			targetEntity.client.onStatusMessage( csstatus.PET_PROCREATE_GET_NO_SEAT, "" )
			return
		if targetEntity.pcg_isOverbrim( 2 ):
			self.statusMessage( csstatus.PET_PROCREATE_GET_NO_SEAT )
			targetEntity.client.onStatusMessage( csstatus.PET_PROCREATE_GET_NO_SEAT, "" )
			return
		self.setTemp( "pft_takePetTargetID", targetEntity.id )
		BigWorld.globalData["PetProcreationMgr"].requestProcreatedPet( self.databaseID, targetEntity.databaseID, self.base, targetEntity.base )

	def ptf_procreating( self, dbid ):
		"""
		�Ƿ����ڷ�ֳ
		"""
		return self.setTemp( "myProcreationPetDBID", 0 ) == dbid

	def pft_obtainProcreatedPet( self, targetDBID, petDBID1, petDBID2 ):
		"""
		Define method.
		ȥ��ֳ������ȡ��ֳ�������Ϣ����

		@param targetDBID : ��ͬ��ֳ�Ķ���dbid
		@param petDBID1 : �������ڷ�ֳ�ĳ���dbid
		@param petDBID2 : �������ڷ�ֳ�ĳ���dbid
		@type petDBID : DATABASE_ID
		"""
		try:
			targetEntity = BigWorld.entities[self.queryTemp( "pft_takePetTargetID", 0 )]
		except KeyError:
			DEBUG_MSG( "cannot find procreate together player( %i )." % self.queryTemp( "pft_takePetTargetID", 0 ) )
			return
		# �������û�����٣���ô��ʱ֪ͨ��base����������ݣ���ʱ�Է���base���ᱻ����
		if targetEntity.isDestroyed:
			DEBUG_MSG( "procreate together player( %i ) has been destroyed." % ( targetEntity.id ) )
			return
		self.removeProcreatingFlag()
		targetEntity.removeProcreatingFlag()
		targetEntity.base.pft_takePet( petDBID2, petDBID1 )
		self.base.pft_takePet( petDBID1, petDBID2 )
		BigWorld.globalData["PetProcreationMgr"].obtainPetSuccess( self.databaseID, targetDBID )

	def pft_procreatePetFailed( self, targetDBID, petDBID1, petDBID2 ):
		"""
		Define method.
		ȥ��ֳ������ȡ��ֳ�������Ϣ����

		@param targetDBID : ��ͬ��ֳ�Ķ���dbid
		@param petDBID1 : �������ڷ�ֳ�ĳ���dbid
		@param petDBID2 : �������ڷ�ֳ�ĳ���dbid
		@type petDBID : DATABASE_ID
		"""
		self.removeTemp( "pft_takePetTargetID" )

	def pft_changeState( self, state, dstEntity ):
		"""
		��ֳ����״̬�ı�

		@param dstEntity : ���뷱ֳ��Ŀ��entity
		"""
		if PET_PROCREATION_STATE[self.procreateState].changeState( self, dstEntity, state ):
			self.procreateState = state
			PET_PROCREATION_STATE[self.procreateState].enter( self, dstEntity )
			if dstEntity:
				dstEntity.pft_dstChangeState( state, self.id )

	def pft_dstChangeState( self, state, targetID ):
		"""
		Define method.
		�Է�״̬�ı�

		@param state : �Է��ĵ�ǰ��ֳ����״̬
		@param targetID : �Է��� entity id
		"""
		if state != csdefine.PET_PROCREATION_WAITING and self.queryTemp( "petProcreationTargetID", 0 ) != targetID:
			return
		try:
			dstEntity = BigWorld.entities[targetID]
		except KeyError:
			dstEntity = None
			self.pft_changeState( csdefine.PET_PROCREATION_DEFAULT, dstEntity )
			return
		PET_PROCREATION_STATE[self.procreateState].onDstStateChanged( self, dstEntity, state )
		self.client.pft_dstChangeState( state )

	def pft_selectPet( self, srcEntityID, petDBID ):
		"""
		Exposed method.
		ѡ�����

		@param petDBID : �����databaseID
		@type petDBID : DATABASE_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % ( srcEntityID, self.id ) )
			return
		try:
			dstEntity = BigWorld.entities[self.queryTemp( "petProcreationTargetID", 0 )]
		except KeyError:
			dstEntity = None
			self.pft_changeState( csdefine.PET_PROCREATION_DEFAULT, dstEntity )	# ע�⣬dstEntity�п�����None
			return
		if not self.pcg_petDict.has_key( petDBID ):
			HACK_MSG( "pet( %i )�����ڡ�" % petDBID )
			return
		if self.pcg_isActPet( petDBID ):
			self.statusMessage( csstatus.PET_PROCREATE_FAIL_CONJURED )
			return
		if self.pcg_isConjuring( petDBID ):
			self.pft_changeState( csdefine.PET_PROCREATION_DEFAULT, dstEntity )
			return
		if self.isPetInSwap( petDBID ):
			self.pft_changeState( csdefine.PET_PROCREATION_DEFAULT, dstEntity )
			return
		PET_PROCREATION_STATE[self.procreateState].changePet( self, dstEntity, petDBID )

	def pft_playerChangeState( self, srcEntityID, state ):
		"""
		Exposed method.
		��Ҹı䷱ֳ����״̬

		@param state : ��ֳ����״̬
		@type state : INT8
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src( %i ) calling dst( %i ) method" % ( srcEntityID, self.id ) )
			return

		dstEntityID = self.queryTemp( "petProcreationTargetID", 0 )
		try:
			dstEntity = BigWorld.entities[dstEntityID]
		except KeyError:
			dstEntity = None
			self.pft_changeState( csdefine.PET_PROCREATION_DEFAULT, dstEntity )	# ע�⣬dstEntity�п�����None
			return
		self.pft_changeState( state, dstEntity )
		#PET_PROCREATION_STATE[self.procreateState].changeState( self, dstEntity, state )

	def pft_changeMyPet( self, petDBID ):
		"""
		�ı��Լ��ĳ���
		"""
		self.setTemp( "myProcreationPetDBID", petDBID )

	def pft_dstChangePet( self, petDBID ):
		"""
		Define method.
		�Է��ı䷱ֳ����
		"""
		self.setTemp( "dstProcreationPetDBID", petDBID )

	def pft_canProcreate( self, dstEntity ):
		"""
		�Ƿ��ܹ��ͶԷ���ֳ����
		"""
		try:
			myPetData = self.pcg_petDict.get( self.queryTemp( "myProcreationPetDBID", 0 ) )
			dstPetData = dstEntity.pcg_petDict.get( self.queryTemp( "dstProcreationPetDBID", 0 ) )
		except:
			DEBUG_MSG( "--->>>there's no pet data" )
			return csstatus.PET_PROCREATE_FAIL_NOT_EXIST
		if myPetData.procreated or dstPetData.procreated:
			return csstatus.PET_PROCREATE_FAIL_PROCREATED
		if not formulas.isHierarchy( myPetData.species, csdefine.PET_HIERARCHY_INFANCY1 ) or \
			not formulas.isHierarchy( dstPetData.species, csdefine.PET_HIERARCHY_INFANCY1 ):
				return csstatus.PET_PROCREATE_FAIL_NEED_INFANCY
		if formulas.getType( myPetData.species ) != formulas.getType( dstPetData.species ):
			return csstatus.PET_PROCREATE_FAIL_DIFFER_TYPE
		if myPetData.mapMonster != dstPetData.mapMonster:
			return csstatus.PET_PROCREATE_FAIL_DIFFER_TYPE
		if myPetData.level < csconst.PET_PROCREATE_MIN_LEVEL or \
			dstPetData.level < csconst.PET_PROCREATE_MIN_LEVEL:
				return csstatus.PET_PROCREATE_FAIL_LEVEL_SHORT
		if myPetData.gender == dstPetData.gender:
			return csstatus.PET_PROCREATE_FAIL_SAME_SEX
		if myPetData.life < csconst.PET_PROCREATE_LIFT_NEED or dstPetData.life < csconst.PET_PROCREATE_LIFT_NEED:
			return csstatus.PET_PROCREATE_FAIL_LIFE_LACK
		if myPetData.joyancy < csconst.PET_PROCREATE_JOY_NEED or dstPetData.joyancy < csconst.PET_PROCREATE_JOY_NEED:
			return csstatus.PET_PROCREATE_FAIL_JOY_LACK
		return csstatus.PET_PROCREATE_START

	def pft_endProcreate( self ):
		"""
		Define method.
		��ֳ��Ϊ����������ֳ����
		"""
		self.removeTemp( "myProcreationPetDBID" )
		self.removeTemp( "dstProcreationPetDBID" )
		self.removeTemp( "petProcreationTargetID" )
		self.procreateState = csdefine.PET_PROCREATION_DEFAULT

	def pft_procreating( self, petDBID ):
		"""
		�Ƿ��ڷ�ֳ������
		"""
		if self.queryTemp( "myProcreationPetDBID", 0 ) == petDBID:
			return True
		return False

	def pft_onLeaveTeam( self ):
		"""
		�뿪����Գ��ﷱֳ��Ӱ��
		"""
		try:
			dstEntity = BigWorld.entities[self.queryTemp( "petProcreationTargetID", 0 )]
		except KeyError:
			dstEntity = None
		PET_PROCREATION_STATE[self.procreateState].changeState( self, dstEntity, csdefine.PET_PROCREATION_DEFAULT )

	def pft_setProcreating( self ):
		"""
		Define method.
		������ߣ���ѯ�������з�ֳ����Ļص�
		��ʱcell����Ҫ��ֳ��������ݣ���������ֳ���
		"""
		self.setTemp( "petProcreating", True )

	def isPetProcreating( self ):
		"""
		����Ƿ��ڳ��ﷱֳ��
		"""
		return self.queryTemp( "petProcreating", False )

	def removeProcreatingFlag( self ):
		"""
		������ﷱֳ���
		"""
		self.removeTemp( "petProcreating" )

class PetProcreationState:
	"""
	���ѡ����ﷱֳ��״̬������

	PET_PROCREATION_DEFAULT : Ĭ��״̬�����û���г��ﷱֳ����
	PET_PROCREATION_SELECTING : ѡ��ֳ����״̬
	PET_PROCREATION_LOCK : ��������״̬
	PET_PROCREATION_SURE : ȷ���ύ��ֳ����״̬
	PET_PROCREATION_COMMIT : �ύ��ֳ����״̬
	"""
	def __init__( self ):
		pass

	def enter( self, srcEntity, dstEntity ):
		"""
		�����״̬����
		"""
		pass

	def leave( self, srcEntity, dstEntity ):
		"""
		�뿪��״̬����
		"""
		pass

	def onDstStateChanged( self, srcEntity, dstEntity, state ):
		"""
		dstEntity״̬�ı��srcEntity��Ӱ��
		"""
		pass

	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		srcEntity�������ݸı�
		"""
		pass

	def changeState( self, srcEntity, dstEntity, state ):
		"""
		�ı�״̬
		"""
		pass

class PetProcreationStateDefault( PetProcreationState ):
	"""
	PET_PROCREATION_DEFAULT : Ĭ��״̬�����û���г��ﷱֳ����
	"""
	_instance = None
	def __init__( self ):
		assert PetProcreationStateDefault._instance is None,"instance has already exist!"
		PetProcreationState.__init__( self )

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance  = PetProcreationStateDefault()
		return self._instance

	def enter( self, srcEntity, dstEntity ):
		"""
		�����״̬����
		"""
		srcEntity.removeTemp( "myProcreationPetDBID" )
		srcEntity.removeTemp( "dstProcreationPetDBID" )
		srcEntity.removeTemp( "petProcreationTargetID" )

	def leave( self, srcEntity, dstEntity ):
		"""
		�뿪��״̬����
		"""
		pass

	def onDstStateChanged( self, srcEntity, dstEntity, state ):
		"""
		dstEntity״̬�ı��srcEntity��Ӱ��
		"""
		if state == csdefine.PET_PROCREATION_WAITING:
			srcEntity.pft_changeState( csdefine.PET_PROCREATION_SELECTING, dstEntity )

	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		srcEntity�������ݸı�
		"""
		pass

	def changeState( self, srcEntity, dstEntity, state ):
		"""
		�ı�״̬
		"""
		if state == csdefine.PET_PROCREATION_WAITING:
			return True
		elif state == csdefine.PET_PROCREATION_SELECTING:
			if srcEntity.isPetProcreating():
				srcEntity.statusMessage( csstatus.PET_PROCREATE_ALREADY_HAS )
				dstEntity.client.onStatusMessage( csstatus.PET_PROCREATE_ALREADY_HAS, "" )
				dstEntity.pft_endProcreate()
				return False
			srcEntity.setTemp( "petProcreationTargetID", dstEntity.id )
			return True
		return False


class PetProcreationStateWaiting( PetProcreationState ):
	"""
	PET_PROCREATION_DEFAULT : Ĭ��״̬�����û���г��ﷱֳ����
	"""
	_instance = None
	def __init__( self ):
		assert PetProcreationStateWaiting._instance is None,"instance has already exist!"
		PetProcreationState.__init__( self )

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance  = PetProcreationStateWaiting()
		return self._instance

	def enter( self, srcEntity, dstEntity ):
		"""
		�����״̬����
		"""
		srcEntity.setTemp( "petProcreationTargetID", dstEntity.id )

	def leave( self, srcEntity, dstEntity ):
		"""
		�뿪��״̬����
		"""
		pass

	def onDstStateChanged( self, srcEntity, dstEntity, state ):
		"""
		dstEntity״̬�ı��srcEntity��Ӱ��
		"""
		if state == csdefine.PET_PROCREATION_SELECTING:
			srcEntity.pft_changeState( state, dstEntity )

	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		srcEntity�������ݸı�
		"""
		pass

	def changeState( self, srcEntity, dstEntity, state ):
		"""
		�ı�״̬
		"""
		if state != csdefine.PET_PROCREATION_SELECTING:
			return False
		return True


class PetProcreationStateSelecting( PetProcreationState ):
	"""
	PET_PROCREATION_SELECTING : ѡ��ֳ����״̬
	"""
	_instance = None
	def __init__( self ):
		assert PetProcreationStateSelecting._instance is None,"instance has already exist!"
		PetProcreationState.__init__( self )

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance  = PetProcreationStateSelecting()
		return self._instance

	def enter( self, srcEntity, dstEntity ):
		"""
		�����״̬����
		"""
		pass

	def leave( self, srcEntity, dstEntity ):
		"""
		�뿪��״̬����
		"""
		pass

	def onDstStateChanged( self, srcEntity, dstEntity, state ):
		"""
		dstEntity״̬�ı��srcEntity��Ӱ��
		"""
		if state == csdefine.PET_PROCREATION_DEFAULT:
			srcEntity.pft_changeState( dstEntity, state )

	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		srcEntity�������ݸı�
		"""
		srcEntity.pft_changeMyPet( petDBID )
		dstEntity.pft_dstChangePet( petDBID )
		srcEntity.base.pft_changePet( dstEntity.base, petDBID )
		srcEntity.pft_changeState( csdefine.PET_PROCREATION_SELECTING, dstEntity )

	def changeState( self, srcEntity, dstEntity, state ):
		"""
		�ı�״̬
		"""
		if state == csdefine.PET_PROCREATION_DEFAULT:
			return True
		elif state == csdefine.PET_PROCREATION_SELECTING:
			return True
		elif state == csdefine.PET_PROCREATION_LOCK:
			return True
		else:
			return False


class PetProcreationStateLock( PetProcreationState ):
	"""
	PET_PROCREATION_LOCK : ��������״̬
	"""
	_instance = None
	def __init__( self ):
		assert PetProcreationStateLock._instance is None,"instance has already exist!"
		PetProcreationState.__init__( self )

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance  = PetProcreationStateLock()
		return self._instance

	def enter( self, srcEntity, dstEntity ):
		"""
		�����״̬����
		"""
		pass

	def leave( self, srcEntity, dstEntity ):
		"""
		�뿪��״̬����
		"""
		pass

	def onDstStateChanged( self, srcEntity, dstEntity, state ):
		"""
		dstEntity״̬�ı��srcEntity��Ӱ��
		"""
		if state == csdefine.PET_PROCREATION_DEFAULT:
			srcEntity.pft_changeState( state, dstEntity )
		elif state == csdefine.PET_PROCREATION_SELECTING:
			srcEntity.pft_changeState( state, dstEntity )

	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		srcEntity�������ݸı�
		"""
		srcEntity.pft_changeMyPet( petDBID )
		dstEntity.pft_dstChangePet( petDBID )
		srcEntity.base.pft_changePet( dstEntity.base, petDBID )
		srcEntity.pft_changeState( csdefine.PET_PROCREATION_SELECTING, dstEntity )

	def changeState( self, srcEntity, dstEntity, state ):
		"""
		�ı�״̬
		"""
		if state == csdefine.PET_PROCREATION_SELECTING:
			return True
		elif state == csdefine.PET_PROCREATION_SURE:
			dstEntityState = dstEntity.procreateState
			if dstEntityState != csdefine.PET_PROCREATION_LOCK and dstEntityState != csdefine.PET_PROCREATION_SURE:
				return False
			if srcEntity.isTeamCaptain() and srcEntity.money < formulas.getProcreatePetCost():
				dstEntity.client.onStatusMessage( csstatus.PET_PROCREATE_FAIL_LACK_MONEY, "" )
				srcEntity.statusMessage( csstatus.PET_PROCREATE_FAIL_LACK_MONEY )
				return False
			status = srcEntity.pft_canProcreate( dstEntity )
			if status != csstatus.PET_PROCREATE_START:
				dstEntity.client.onStatusMessage( status, "" )
				srcEntity.statusMessage( status )
				return False
			return True
		elif state == csdefine.PET_PROCREATION_DEFAULT:
			return True
		else:
			return False

class PetProcreationStateSure( PetProcreationState ):
	"""
	PET_PROCREATION_SURE : ȷ���ύ��ֳ����״̬
	"""
	_instance = None
	def __init__( self ):
		assert PetProcreationStateSure._instance is None,"instance has already exist!"
		PetProcreationState.__init__( self )

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance  = PetProcreationStateSure()
		return self._instance

	def enter( self, srcEntity, dstEntity ):
		"""
		�����״̬����
		"""
		if dstEntity.procreateState == csdefine.PET_PROCREATION_SURE:
			srcEntity.pft_changeState( csdefine.PET_PROCREATION_COMMIT, dstEntity )

	def leave( self, srcEntity, dstEntity ):
		"""
		�뿪��״̬����
		"""
		pass

	def onDstStateChanged( self, srcEntity, dstEntity, state ):
		"""
		dstEntity״̬�ı��srcEntity��Ӱ��
		"""
		if state == csdefine.PET_PROCREATION_DEFAULT:
			srcEntity.pft_changeState( state, dstEntity )
		elif state == csdefine.PET_PROCREATION_SELECTING:
			srcEntity.pft_changeState( state, dstEntity )
		elif state == csdefine.PET_PROCREATION_SURE:
			if srcEntity.isTeamCaptain() and srcEntity.money < formulas.getProcreatePetCost():
				dstEntity.client.onStatusMessage( csstatus.PET_PROCREATE_FAIL_LACK_MONEY, "" )
				srcEntity.statusMessage( csstatus.PET_PROCREATE_FAIL_LACK_MONEY )
				srcEntity.pft_changeState( csdefine.PET_PROCREATION_DEFAULT, dstEntity )
				return
			srcEntity.pft_changeState( csdefine.PET_PROCREATION_COMMIT, dstEntity )
		elif state == csdefine.PET_PROCREATION_COMMIT:
			if srcEntity.isTeamCaptain() and srcEntity.money < formulas.getProcreatePetCost():
				dstEntity.client.onStatusMessage( csstatus.PET_PROCREATE_FAIL_LACK_MONEY, "" )
				srcEntity.statusMessage( csstatus.PET_PROCREATE_FAIL_LACK_MONEY )
				srcEntity.pft_endProcreate()
				dstEntity.pft_endProcreate()
				return
			srcEntity.pft_changeState( state, dstEntity )

	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		srcEntity�������ݸı�
		"""
		ERROR( "--->>>" )

	def changeState( self, srcEntity, dstEntity, state ):
		"""
		�ı�״̬
		"""
		if state == csdefine.PET_PROCREATION_SELECTING:
			return True
		elif state == csdefine.PET_PROCREATION_COMMIT:
			return True
		elif state == csdefine.PET_PROCREATION_DEFAULT:
			return True
		else:
			return False


class PetProcreationStateCommit( PetProcreationState ):
	"""
	PET_PROCREATION_COMMIT : �ύ��ֳ����״̬
	"""
	_instance = None

	def __init__( self ):
		assert PetProcreationStateCommit._instance is None,"instance has already exist!"
		PetProcreationState.__init__( self )

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance  = PetProcreationStateCommit()
		return self._instance

	def enter( self, srcEntity, dstEntity ):
		"""
		�����״̬����
		"""
		pass

	def leave( self, srcEntity, dstEntity ):
		"""
		�뿪��״̬����
		"""
		pass

	def onDstStateChanged( self, srcEntity, dstEntity, state ):
		"""
		dstEntity״̬�ı��srcEntity��Ӱ��
		"""
		if state == csdefine.PET_PROCREATION_COMMIT:
			try:
				myPetData = srcEntity.pcg_petDict.get( srcEntity.queryTemp( "myProcreationPetDBID", 0 ) )
				dstPetData = dstEntity.pcg_petDict.get( srcEntity.queryTemp( "dstProcreationPetDBID", 0 ) )
			except:
				DEBUG_MSG( "--->>>there's no pet data" )
				dstEntity.pft_endProcreate()
				srcEntity.pft_endProcreate()
				return

			endTime = time.time() + csconst.PET_PROCREATE_NEED_TIME
			srcEntity.base.pft_procreatePet( dstEntity.databaseID, myPetData.databaseID, endTime )
			dstEntity.base.pft_procreatePet( srcEntity.databaseID, dstPetData.databaseID, endTime )
			srcEntity.client.pft_receivePetProcreationInfo( dstEntity.databaseID, endTime )
			dstEntity.client.pft_receivePetProcreationInfo( srcEntity.databaseID, endTime )
			srcEntity.statusMessage( csstatus.PET_PROCREATE_START )
			dstEntity.client.onStatusMessage( csstatus.PET_PROCREATE_START, "" )
			if srcEntity.isTeamCaptain():
				srcEntity.payMoney( formulas.getProcreatePetCost(), csdefine.CHANGE_MONEY_PROCREATE )
			else:
				dstEntity.payMoney( formulas.getProcreatePetCost(), csdefine.CHANGE_MONEY_PROCREATE )
			srcEntity.pft_setProcreating()
			dstEntity.pft_setProcreating()
			srcEntity.pft_endProcreate()
			dstEntity.pft_endProcreate()

	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		srcEntity�������ݸı�
		"""
		ERROR_MSG( "--->>>" )

	def changeState( self, srcEntity, dstEntity, state ):
		"""
		�ı�״̬
		"""
		return False


PET_PROCREATION_STATE = { csdefine.PET_PROCREATION_DEFAULT : PetProcreationStateDefault.instance(),
								csdefine.PET_PROCREATION_WAITING : PetProcreationStateWaiting.instance(),
								csdefine.PET_PROCREATION_SELECTING : PetProcreationStateSelecting.instance(),
								csdefine.PET_PROCREATION_LOCK : PetProcreationStateLock.instance(),
								csdefine.PET_PROCREATION_SURE : PetProcreationStateSure.instance(),
								csdefine.PET_PROCREATION_COMMIT : PetProcreationStateCommit.instance(),
								}


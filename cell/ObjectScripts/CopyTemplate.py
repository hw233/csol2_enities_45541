# -*- coding: gb18030 -*-

# ------------------------------------------------
# from python
import copy
# ------------------------------------------------
# from common
from bwdebug import *
import Language
import csdefine
# ------------------------------------------------
# from cell
import Const
import Resource.CopyStage.CopyStageBase as CopyStageBase
from interface.CopyStageInterface import CopyStageInterface
# ------------------------------------------------
# from current directory
from SpaceCopy import SpaceCopy
# ------------------------------------------------

class CopyTemplate( SpaceCopy, CopyStageInterface ) :
	"""
	����ģ��
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		CopyStageInterface.__init__( self )
		self._stageFile = ""					# �����Ĺؿ������ļ�
		self._stageSection = None

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		SpaceCopy.load( self, section )

		self._spaceConfigInfo["extended_shown"] =\
			[int(i) for i in section.readString("extended_shown").split()]

		if section.has_key( "CopyStageFile" ) :
			self.loadStages(section.readString("CopyStageFile"))

	def loadStages(self, stage_file_path):
		"""
		���ؽ׶���������
		@type	stage_file_path:	string
		@param	stage_file_path:	file path
		"""
		self._stageFile = stage_file_path
		assert self._stageFile != "", "the CopyStageFile is NULL."

		self._stageSection = Language.openConfigSection( self._stageFile )
		assert self._stageSection is not None, "open %s false." % self._stageFile

		for childSect in self._stageSection.values() :
			copyStage = CopyStageBase.CopyStageBase()
			copyStage.init( childSect )
			self.addStage( copyStage )
			copyStage.setIndexInCopy( len( self._stages ) - 1 )

		# �������
		Language.purgeConfig( self._stageFile )

	def getCopyStageFile( self ) :
		"""
		��ȡ�ؿ������ļ�
		"""
		return self._stageFile

	def getCopyStageSection( self ) :
		"""
		"""
		return self._stageSection

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )

		params["baseMailbox"] = baseMailbox
		currentStage = self.getCurrentStage( selfEntity )
		if not selfEntity.queryTemp("firstPlayer", False ) :
			selfEntity.setTemp('firstPlayer', True )
			currentStage.doAllEvent( selfEntity, csdefine.COPY_EVENT_ON_FIRST_ENTER_COPY, params )

		currentStage.doAllEvent( selfEntity, csdefine.COPY_EVENT_ON_ENTER_COPY, params )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		params["baseMailbox"] = baseMailbox
		currentStage = self.getCurrentStage( selfEntity )
		currentStage.doAllEvent( selfEntity, csdefine.COPY_EVENT_ON_LEAVE_COPY, params )
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )

	def onConditionChange( self, selfEntity, params ) :
		"""
		�����¼��仯֪ͨ
		"""
		pass

	def onTeleportReady( self, selfEntity, baseMailbox ):
		"""
		"""
		SpaceCopy.onTeleportReady( self, selfEntity, baseMailbox )
		baseMailbox.client.onOpenCopySpaceInterface( self.shownDetails() )

		params = {}
		params["baseMailbox"] = baseMailbox
		self.getCurrentStage( selfEntity ).doAllEvent( selfEntity, csdefine.COPY_EVENT_ON_TELEPORT_READY, params )

	def copyTemplate_onMonsterDie( self, spaceBase, monsterID, monsterClassName, killerID ):
		"""
		����֪ͨ�����ڸ����Լ����ˣ����ݹ����className����ͬ����������
		�˴���û������������¼�������ͳһ����˹���������֪ͨ��ԭ�����£�
		# 1.����������֪ͨ����������϶�
		# 2.����������������Ƚ�ͳһ���������﷽������̳�ʹ�á�
		ȱ�����һЩ�����Ĺ�����������֪ͨ��������������̳��ڴ˵ĸ�����ϣ������Щ����֪ͨ�Ļ��������ش˽ӿڡ�
		"""
		spaceEntity = BigWorld.entities.get( spaceBase.id )
		if spaceEntity and spaceEntity.isReal() :
			spaceEntity.getScript().copyTemplate_onMonsterDieRemote( spaceEntity, monsterID, monsterClassName, killerID )
		else :
			spaceBase.cell.remoteScriptCall( "copyTemplate_onMonsterDieRemote", ( monsterID, monsterClassName, killerID ) )

	def copyTemplate_onMonsterDieRemote( self, selfEntity, monsterID, monsterClassName, killerID ):
		"""
		����֪ͨ�����ڸ����Լ����ˣ����ݹ����className����ͬ��������
		"""
		params = {}
		params["monsterID"] = monsterID
		params["monsterClassName"] = monsterClassName
		params["killerID"] = killerID
		self.getCurrentStage( selfEntity ).doAllEvent( selfEntity, csdefine.COPY_EVENT_ON_MONSTER_DIE, params )

	def onRoleDie( self, role, killer ):
		"""
		<virtual method>

		#ĳrole�ڸø���������

		"""
		SpaceCopy.onRoleDie( self, role, killer )

		"""
		params = {}

		if not killer :
			params[ "killer" ] = None
		else :
			killerType = killer.getEntityType()
			if killer.isEntityType( csdefine.ENTITY_TYPE_PET ) :
				killer = killer.getOwner().entity

			params[ "killerType" ]	= killer.getEntityType()
			if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
				params[ "killerBase" ]			= killer.base
				params[ "playerName" ]			= killer.playerName
				params[ "killerCamp" ]			= killer.getCamp()
				params[ "killer_dbID" ]			= killer.databaseID
				params[ "killer_tong_dbID" ]	= killer.tong_dbID
			else :
				if hasattr( killer, "uname" ) :
					params[ "uname" ]			= killer.uname

		params[ "roleBase" ]		= role.base
		params[ "roleCamp" ]		= role.getCamp()
		params[ "rolePos" ]			= role.position
		params[ "role_dbID" ]		= role.databaseID
		params[ "role_tong_dbID" ]	= role.tong_dbID
		params[ "role_teamID" ]		= 0
		if role.getTeamMailbox() :
			params[ "role_teamID" ]	= role.getTeamMailbox().id

		spaceBase = role.getCurrentSpaceBase()
		if spaceBase :
			spaceEntity = BigWorld.entities.get( spaceBase.id )
			if spaceEntity and spaceEntity.isReal() :
				spaceEntity.getScript().onRoleDieRemote( spaceEntity, params )
			else :
				spaceBase.cell.remoteScriptCall( "onRoleDieRemote", ( params, ) )

		# �����ڴ˴�ͳһ�����������¼�֪ͨ�����Ĵ���ԭ�� ��
		# 1.������������Ҫ�������֪ͨ
		# 2.��ͬ������֪ͨ����������ϴ󣬿��ܻ����������������ͳһҲ�����ں�����չ��
		# ��������ṩһ�������������¼��Ĵ���ʽ���������̳��ڴ˵ĸ����ο���
		def onRoleDieRemote( selfEntity, params ) :
			self.getCurrentStage( selfEntity ).doAllEvent( selfEntity, csdefine.COPY_EVENT_ON_ROLE_DIE, params )
		"""

	def shownDetails( self ):
		"""
		shownDetails ����������ʾ����
		[
			0: ʣ��ʱ��
			1: ʣ��С��
			2: ʣ��С������
			3: ʣ��BOSS
			4: ��������
			5: ʣ��ħ�ƻ�����
			6: ʣ�����Ӱʨ����
			7: ��һ��ʣ��ʱ��(���Ȫm؅)
		]
		"""
		# Ĭ����ʾ�������������ʾ����Ҫ����Ҫ�����ⶨ��shownDetails
		details = [ 0, 1, 3 ]
		# �������ö����������ʾ��
		details.extend(self.extendedShownDetails())
		return details

	#-------------------------------------------------------------
	# ����ķ��������µ� addUserTimer ��ӵĻص�������
	# ����֧����Ϊ��֧�� action ���ӳٵ��ÿ����á�
	#-------------------------------------------------------------

	def onTimer( self, selfEntity, timerID, userArg, params ) :
		"""
		"""
		if userArg == Const.SPACE_TIMER_ARG_CLOSE_SPACE :		# ֵΪ -1���˴���timer��������������Ա���ã������ȥConst.py��ȥ��˵����
			self.closeCopy( selfEntity )
		elif userArg > Const.SPACE_TIMER_USER_ARG_MAX :
			self.doCopyStageAction( selfEntity, params )
		else :
			self.getCurrentStage( selfEntity ).doAllEvent( selfEntity, csdefine.COPY_EVENT_ON_TIMER, params )

	def doCopyStageAction( self, selfEntity, params ) :
		"""
		����һ��������Ϊ
		"""
		eventType		= params.get( "eventType" )
		eventInStage	= params.get( "eventInStage" )
		actionInEvent	= params.get( "actionInEvent" )
		stageInCopy		= params.get( "stageInCopy" )

		copyStage	= self._stages[ stageInCopy ]
		copyEvent	= copyStage.getEvent( eventType, eventInStage )
		copyAction	= copyEvent.getAction( actionInEvent )
		copyAction.do( selfEntity, params )

	def closeCopy( self, selfEntity, params = {} ) :
		"""
		# �����ر�,�ù��������߳��������֮����ܵ��ã��������������߳���Һ��һ�� 10 ���timer
		# �����ڲ�����������Ա֪����timer��userArg ������Const.py�У�Ϊ��ֵ��
		# �ù�����ʵ�ڵײ� SpaceCopy ���У���������ʹ����selfEntity.addTimer( 10.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE )����,���������ظ��ǡ�
		"""
		if BigWorld.cellAppData.has_key( selfEntity.getSpaceGlobalKey() ):
			del BigWorld.cellAppData[ selfEntity.getSpaceGlobalKey() ]
		selfEntity.base.closeSpace( True )

	def extendedShownDetails(self):
		"""��ȡ������ʾ��Ϣ����"""
		return self._spaceConfigInfo["extended_shown"]

	def getNonRepeatedPatrolGraphID( self, selfEntity, patrolGraphIdList, monsterClassName, monsterCell ) :
		"""
		��Ѳ��·�� patrolGraphIdList �в��ظ���ȡһ�������ڹ��� AIAction300
		"""
		if selfEntity.queryCopyShareTemp( SHARE_MAPPING_KEY_AIACTION300_GRAPH_IDS ) == None :
			selfEntity.setCopyShareTemp( SHARE_MAPPING_KEY_AIACTION300_GRAPH_IDS, patrolGraphIdList )
		
		originalGraphIDs = selfEntity.queryCopyShareTemp( SHARE_MAPPING_KEY_AIACTION300_GRAPH_IDS )
		key = SHARE_MAPPING_KEY_AIACTION300_GRAPH_IDS + monsterClassName
		if not selfEntity.queryCopyShareTemp( key ) :
			selfEntity.setCopyShareTemp( key, copy.deepcopy( originalGraphIDs ) )
		
		graphID = selfEntity.queryCopyShareTemp( key ).pop()
		monsterCell.remoteScriptCall( "onGetNonRepeatedPatrolGraphID", ( graphID, ) )


# ------------------------------------------------
# ������������ copyShareTempMapping key �Ķ���
# ------------------------------------------------

SHARE_MAPPING_KEY_AIACTION300_GRAPH_IDS							= "AIAction300_graphIDs_"				# ����ģ����� AIAction300 ���ڴ洢���ﹲ���Ѳ��·����Ϣ��Ϊ����ͬ�����ʵ key Ϊ "AIAction300_graphIDs_XXX"��XXXΪ����className



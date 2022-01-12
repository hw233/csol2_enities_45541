# -*-coding:gb18030 -*-

from bwdebug import *
from SpaceCopyTeam import SpaceCopyTeam
import BigWorld
import csconst
import time
import csdefine
import Const

PREPARE_CLOSE_SPACE_USERAGE = 1
BOSSCOUNT					= 1

class SpaceCopyTeachKillMonster( SpaceCopyTeam ):
	"""
	"""
	def __init__( self ):
		SpaceCopyTeam.__init__( self )
		self.masterSkillList = []			# ʦ���ĸ���ר������
		self.prenticeSkillList = []			# ͽ�ܵĸ���ר������
		self.warTotalTime = 0			# ��������ʱ��
		self.doorData = {}

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		#DEBUG_MSG( "--->>>self.params",selfEntity.params.items() )
		SpaceCopyTeam.initEntity( self, selfEntity )
		selfEntity.addTimer( self.warTotalTime, 0, PREPARE_CLOSE_SPACE_USERAGE )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_TEACH_MONSTER_LEVEL, selfEntity.params["monsterLevel"] )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, csconst.TEACH_SPACE_MONSTER_COUNT )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, time.time() )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, self.warTotalTime )
		selfEntity.setTemp( "bossCount", BOSSCOUNT )	# ������ˢboss�ĸ���ΪBOSSCOUNT

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		if params["isMaster"]:
			baseMailbox.client.initSpaceSkills( self.masterSkillList, csdefine.SPACE_TYPE_TEACH_KILL_MONSTER )
		else:
			baseMailbox.client.initSpaceSkills( self.prenticeSkillList, csdefine.SPACE_TYPE_TEACH_KILL_MONSTER )
		baseMailbox.cell.teach_enterKillMonsterSpaceSuccess()

	def packedSpaceDataOnEnter( self, playerEntity ):
		"""
		�����ҽ���ռ�ʱ������
		"""
		# ��������ʦͽ���������ߣ���ʱ��ϵ�����п��ܻ�û��ʼ����ϣ���������iAmMaster�ж��Ƿ�ʦ���ǲ�׼ȷ��
		# Ŀǰ��ʱͨ����ҵļ������ж��Ƿ�ʦ�����Ժ���޸Ŀռ������ƣ�����ҵ����ݼ�����Ϻ�Ż����ռ䡣
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, playerEntity )
		packDict[ "dbID" ] = playerEntity.databaseID
		packDict[ "isMaster" ] = playerEntity.iAmMaster() or playerEntity.level >= csconst.TEACH_MASTER_MIN_LEVEL
		return packDict

	def packedDomainData( self, entity ):
		"""
		�����domain�������ռ�ʱ������
		"""
		members = entity.getAllMemberInRange( csconst.TEACH_SPACE_ENTER_TEAMMATE_DISTANCE )
		totalLevel = 0
		for player in members:
			totalLevel += player.level
		playerCount = len( members )
		monsterLevel = totalLevel / playerCount

		d = { 'dbID' : entity.databaseID }
		if entity.teamMailbox:
			# �Ѽ�����飬ȡ��������
			d["teamID"] = entity.teamMailbox.id
			d["captainDBID"] = entity.getTeamCaptainDBID()
			d["membersDBID"] = entity.getTeamMemberDBIDs()
			d["monsterLevel"] = monsterLevel
			d["playerCount"] = playerCount
			d["spaceKey"]	 = entity.teamMailbox.id
		return d

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�

		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		SpaceCopyTeam.onLoadEntityProperties_( self, section )
		self.masterSkillList = [ int( skillID ) for skillID in section.readString( "masterSkills" ).split( ";" ) ]
		self.prenticeSkillList = [ int( skillID ) for skillID in section.readString( "prenticeSkills" ).split( ";" ) ]
		self.warTotalTime = section.readFloat( "warTotalTime" )
		doorSection = section["Door"]
		self.doorData["name"] = doorSection.readString( "name" )
		self.doorData["position"] = doorSection.readVector3( "Pos" )
		self.doorData["radius"] = doorSection.readFloat("radius")
		self.doorData["destSpace"] = doorSection.readString("DestSpace")
		self.doorData["destPosition"] = doorSection.readVector3("DestPos")
		self.doorData["modelNumber"] = doorSection.readString("modelNumber")
		self.doorData["modelScale"] = doorSection.readFloat("modelScale")

	def canUseSkill( self, playerEntity, skillID ):
		"""
		"""
		if playerEntity.iAmMaster():
			return skillID in self.masterSkillList
		else:
			return skillID in self.prenticeSkillList

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == PREPARE_CLOSE_SPACE_USERAGE:	# �Ȱ���Ҵ��ͳ�������10���رտռ�
			for playerBase in selfEntity._players:
				playerBase.cell.gotoForetime()
			#selfEntity.base.closeSpace( True )
			selfEntity.addTimer( 10, 0, Const.SPACE_TIMER_ARG_CLOSE )
		else:
			SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )

	def createDoor( self, selfEntity ):
		"""
		�����뿪�����Ĵ�����
		"""
		BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, self.doorData["position"], (0, 0, 0), self.doorData )
		#if otherDict.has_key( 'modelScale' ) and otherDict[ 'modelScale' ] != 0.0:
		#	door.modelScale = otherDict[ 'modelScale' ]

	def onLeaveTeam( self, playerEntity ):
		"""
		����뿪����Ĵ���
		"""
		playerEntity.gotoForetime()

	def requestInitSpaceSkill( self, playerEntity ):
		"""
		��ʼ����������
		"""
		if playerEntity.iAmMaster():
			playerEntity.client.initSpaceSkills( self.masterSkillList, csdefine.SPACE_TYPE_TEACH_KILL_MONSTER )
		else:
			playerEntity.client.initSpaceSkills( self.prenticeSkillList, csdefine.SPACE_TYPE_TEACH_KILL_MONSTER )

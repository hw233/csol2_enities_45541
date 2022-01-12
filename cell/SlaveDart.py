# -*- coding: gb18030 -*-


from SlaveMonster import SlaveMonster
import Monster
import cschannel_msgs
import ShareTexts as ST
from FactionMgr import factionMgr
import ECBExtend
import BigWorld
import csdefine
import csconst
import csstatus
import Const
import Define
import random
from bwdebug import *
from VehicleHelper import getCurrVehicleID
from Domain_Fight import g_fightMgr


FIND_OWNER_SPEED = 5.0				#���������ٶ�

STATES =   csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_WIELD | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_TRADE | csdefine.ACTION_FORBID_JUMP | csdefine.ACTION_FORBID_FIGHT \
			  | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_CALL_PET | csdefine.ACTION_FORBID_VEHICLE | csdefine.ACTION_FORBID_TALK

class SlaveDart( SlaveMonster ):
	"""
	"""
	def __init__(self):
		"""
		"""
		INFO_MSG( "SlaveDart(%i) create! ownerName:%s!"%(self.id, self.ownerName ) )

		self.isRideOwner = False
		SlaveMonster.__init__( self )
		self.utype = csdefine.ENTITY_TYPE_VEHICLE_DART
		self.topSpeedY = csconst.ROLE_TOP_SPEED_Y			#Y���ϵ��˶�������������

		# �ڳ��ᱻ�������ȥ�����ƣ�����˱���һ�������ܹ㲥������Ϣ��
		self.volatileInfo = (BigWorld.VOLATILE_ALWAYS, BigWorld.VOLATILE_ALWAYS, None, None)
		self.addTimer( 5000, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )						# �ڳ�5000����
		spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
		BigWorld.globalData['DartManager'].buildDartRelation( self.ownerName, spaceLabel, self.base, self.getFaction() )

		if BigWorld.entities.has_key( self.ownerID ):
			INFO_MSG( "SlaveDart(%i) find owner just create!. ownerName:%s!"%(self.id, self.ownerName ) )
			player = BigWorld.entities[self.ownerID]
			player.queryDartInfo( self )
			self.setOwner( player )
		else:
			INFO_MSG( "SlaveDart(%i) can't find owner just create!. ownerName:%s!"%(self.id, self.ownerName ) )
			self.addTimer( FIND_OWNER_SPEED, 0, ECBExtend.INIT_DART_OWNER_CBID )									# ���������ҵ����ˣ��ڳ�5.0���Ѱ������
		self.enemyForTongDart = []			# ������¼˭�������ڳ�
		self.addFlag( csdefine.ENTITY_FLAG_CANT_ROTATE_IN_FIGHT_STATE )


	def onInitOwner( self, controllerID, userData ):
		"""
		�ص��ķ�ʽ��ʼ���ڳ�
		"""
		if BigWorld.entities.has_key( self.ownerID ):
			INFO_MSG( "SlaveDart(%i) spend few second to find owner success!. ownerName:%s!"%(self.id, self.ownerName ) )
			player = BigWorld.entities[self.ownerID]
			player.queryDartInfo( self )
			self.setOwner( player )

		else:
			self.addTimer( FIND_OWNER_SPEED, 0, ECBExtend.INIT_DART_OWNER_CBID )									#�����ڳ���ͣ��Ѱ������
			INFO_MSG( "SlaveDart(%i) spend little second to find owner, but missed!. ownerName:%s!"%(self.id, self.ownerName ) )
			BigWorld.globalData['DartManager'].findOwnerByName( self.ownerName )

	def onReceiveDartInfo( self, dart_destNpcClassName, dart_questID, dart_eventIndex, dart_factionID, dart_level, dart_type  ):
		"""
		define method
		"""
		self.uname = factionMgr.getName( dart_factionID ) + cschannel_msgs.DART_INFO_4
		self.setTemp( "destNpcClassName", dart_destNpcClassName )			# �ڳ��洢�����NPC ClassName
		self.setTemp( 'questID', dart_questID )								# �ڳ��洢��������ID
		self.setTemp( 'eventIndex', dart_eventIndex )						# �ڳ��洢��������ID
		self.setTemp( "factionID", dart_factionID  )						# �ڳ���������id
		self.setTemp('start_time',BigWorld.time() )							# �ڳ�����ʱ��
		self.setTemp('level', dart_level )
		self.setTemp('callMonstersTotal', 3 )								# �йָ���
		self.setTemp('callMonstersTimeTotal', 5 )							# �йִ���
		self.factionID = dart_factionID
		
		owner = BigWorld.entities.get( self.getOwnerID() )
		if owner is None:
			return
			
		self.position = owner.position
			
		if dart_type == 7:
			self.setTemp( "ownerTongDBID", owner.tong_dbID )
			self.addCombatRelationIns( csdefine.RELATION_DYNAMIC_TONG_FRIEND, owner.tong_dbID )
		# owner.sendTongMemberQuest( dart_questID, self.id )	# CSOL-2118 ���ٷ�����������

	def mountEntity( self, srcEntityID, entityID, order ):
		"""
		Exposed Method
		"""
		return
		if BigWorld.entities.has_key( entityID ) and not self.isRideOwner and BigWorld.entities[entityID].isReal():
			player = BigWorld.entities[entityID]
			if player.vehicle or getCurrVehicleID( player ):
				player.client.onStatusMessage( csstatus.DART_FORBID_VEHICLE, "" )
				return
			if player.position.flatDistTo( self.position ) > 5.0:
				player.client.onStatusMessage( csstatus.DART_FORBID_TOO_FAR, "" )
				return
			if player.getState() != csdefine.ENTITY_STATE_FREE or self.getState() != csdefine.ENTITY_STATE_FREE:
				if self.getState() == csdefine.ENTITY_STATE_FIGHT:
					if len( self.enemyList ) == 0:
						self.state = 0
					needRemoveEnemyIDs = []
					for i in self.enemyList:
						entity = BigWorld.entities.get( i )
						if entity is None or entity.getState() != csdefine.ENTITY_STATE_FIGHT:
							needRemoveEnemyIDs.append( i )
					
					g_fightMgr.breakGroupEnemyRelationByIDs( self, needRemoveEnemyIDs )
					
				player.client.onStatusMessage( csstatus.DART_FORBID_CUR_THING, "" )
				return
			self.direction = player.direction
			player.position = self.position
			if not self.isMoving():
				self.planesAllClients( "setFilterYaw", ( player.direction[2], ) )
			self.controlledBy = player.base
			#���ڳ�ʱȡ����Ӹ���
			if player.isTeamFollowing():
				player.cancelTeamFollow()
				
			player.boardVehicle( self.id )
			player.actCounterInc( STATES )					# �������ڳ�ʱ���ܽ��е���Ϊ
			#player.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )
			# ֪ͨentity����
			self.planesAllClients( "onMountEntity", ( player.id, 0 ) )
			self.isRideOwner = True
			self.topSpeed = self.move_speed + csconst.ROLE_MOVE_SPEED_BIAS


	def disMountEntity( self, srcEntityID, playerID = 0 ):
		"""
		Exposed Method
		ж��entity
		@param entity		:	entity
		@type entity		:	mailBox
		@return None
		"""
		return
		if BigWorld.entities.has_key( srcEntityID ) and self.isRideOwner and srcEntityID == self.ownerID:
			self._disMountEntity()


	def _disMountEntity( self ):
		self.isRideOwner = False
		player = BigWorld.entities[self.ownerID]
		player.leaveDart( STATES, self.id )
		self.stopMoving()
		if player.isReal():
			player.stopMoving()
		self.controlledBy = None


	def beforeDie( self, killerID ):
		"""
		virtual method.
		"""
		if self.isRideOwner:
			self._disMountEntity()
		return True
		
	def dartMissionBrocad( self, killer, factionID ):
		"""
		���ڻ���ڳɹ��Ĺ㲥 by����14:10 2009-7-31
		@param missionType : ��������
		@param missonnType : UINT8
		"""
		#self.family_grade
		killer.brocastMessageSlaveDart( factionID )

	def destoryDartEntity( self ):
		"""
		define method
		"""
		self.setTemp( 'dartQuestAbandoned', True )
		owner = self.getOwner()
		if owner:
			self.removeCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID, self.getOwnerID() )
		self.addTimer( csconst.MONSTER_CORPSE_DURATION, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )
		if self.controlledBy is not None:
			self._disMountEntity()

	def closeVolatileInfo( self ):
		"""
		virtual method.
		�ر�������Ϣ���͹��ܡ�
		�������ģ��ᱻ��ͬ��entity���ã���ĳЩentity���ܻ���Ҫ�Բ�ͬ
		�ķ�ʽ��ʱ���ر������Ϊ���������ӿ�����������ء�
		"""
		# �������ش˽ӿڣ��������κ����飬���ڲ�ִ�йر�������Ϣ֪ͨ����Ϊ
		# ����ر��ˣ���ң��ڳ�����Ư�ƣ���Ϊ��ң��������ڳ����ƶ�ʱ��û�б�֪ͨҪ��������Ϣ֪ͨ���ܡ�
		pass

	def openVolatileInfo( self ):
		"""
		virtual method.
		��������Ϣ���͹���
		�������ģ��ᱻ��ͬ��entity���ã���ĳЩentity���ܻ���Ҫ�Բ�ͬ
		�ķ�ʽ��ʱ���ر������Ϊ���������ӿ�����������ء�
		"""
		# ���ز����Ǵ˷����Ĺ��ܣ�ʹ�ڳ����������֡�
		pass

	def onDestroy( self ):
		"""
		"""
		# ����ڳ��������Ҫ����������ڳ�
		if self.isRideOwner:
			self._disMountEntity()
		# ����б���Ҫ���ٱ���
		baoBiaoList = self.queryTemp( "DartMonsterIdList", [] )
		if len( baoBiaoList ) > 0:
			for i in baoBiaoList:
				if BigWorld.entities.has_key( i ):
					BigWorld.entities[i].destroy()
		SlaveMonster.onDestroy( self )

	def onRoleDestroy( self, entityID ):
		"""
		��ɫ����ǰ�ص�
		"""
		self.ownerID = 0
		self.setTemp( "ownerBaseMailBox", None )
		self.controlledBy = None
		if self.isRideOwner:
			self._disMountEntity()

	def isSlaveDart( self ):
		"""
		������Ƿ����ڳ�
		"""
		return True

	def sendOwnerToSelf( self, baseMailbox ):
		"""
		�����ڳ����˵��ڳ�
		"""
		spaceName = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		baseMailbox.gotoSpace( spaceName, self.position, self.direction )

	def onCorpseDelayTimer( self, controllerID, userData ):
		"""
		MONSTER_CORPSE_DELAY_TIMER_CBID��callback������
		"""
		if not self.isDestroyed:
			playerName = self.ownerName
			if self.queryTemp( 'questFinish', False ) == False:
				INFO_MSG( "SlaveDart(%i) destroy on quest not finish! ownerName:%s!"%(self.id, self.ownerName ) )
				ownerID = self.getOwnerID()
				if BigWorld.entities.has_key( ownerID ):
					if not self.queryTemp('beKilled',False):
						BigWorld.entities[ownerID].statusMessage( csstatus.ROLE_QUEST_DART_TIME_OUT )
					if not self.queryTemp( 'dartQuestAbandoned', False ):
						BigWorld.entities[ownerID].handleDartFailed()
					BigWorld.entities[ownerID].selectTitle( ownerID, 0 )
				elif playerName != '':
					if not self.queryTemp('beKilled',False):
						BigWorld.globalData['DartManager'].addDartMessage( playerName, csstatus.ROLE_QUEST_DART_TIME_OUT, True )
			else:
				INFO_MSG( "SlaveDart(%i) destroy on quest finish! ownerName:%s!"%(self.id, self.ownerName ) )
			if not self.queryTemp( 'dartQuestAbandoned', False ):
				BigWorld.globalData['DartManager'].onReceiveDestoryCommand( playerName )
			self.destroy()


	def queryRelation( self, entity ):
		"""
		virtual method.
		ȡ���Լ���Ŀ��Ĺ�ϵ

		@param entity: ����Ŀ��entity
		@return : RELATION_*
		"""
		#if self.isDestroyed or entity.isDestroyed:
		#	return csdefine.RELATION_NOFIGHT
		
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.Monster.queryRelation( self, entity )
			
		slaveOwner = BigWorld.entities.get( self.ownerID )

		if entity.effect_state  & csdefine.EFFECT_STATE_NO_FIGHT:
			return csdefine.RELATION_NOFIGHT
			
		if entity.utype == csdefine.ENTITY_TYPE_ROLE:				# ���ð���Ա�����ڳ�Ϊ�Ѻù�ϵ
			if self.queryTemp( "ownerTongDBID",0 ) != 0 and self.queryTemp( "ownerTongDBID" ) == entity.tong_dbID:
				return csdefine.RELATION_FRIEND

		if slaveOwner == None or not slaveOwner.isReal():
			return csdefine.RELATION_ANTAGONIZE

		return slaveOwner.queryRelation( entity )

	def updateTopSpeed( self ):
		"""
		virtual method = 0.

		�����ƶ��ٶ�����(topSpeed)
		"""
		slaveOwner = BigWorld.entities.get( self.ownerID )
		if slaveOwner != None:
			if self.actionSign( csdefine.ACTION_FORBID_MOVE ) or slaveOwner.actionSign( csdefine.ACTION_FORBID_MOVE ):
				self.topSpeed = 0.001
			else:
				self.topSpeed = self.move_speed + csconst.ROLE_MOVE_SPEED_BIAS
	
	
	def updateOwnerID( self, ownerID ):
		"""
		define method
		"""
		self.ownerID = ownerID
	
	
	def updateOwnerBaseMailbox( self, ownerBaseMB ):
		"""
		define method
		��ɫ�������ߣ������ڳ�������baseMailBox������
		"""
		self.setTemp( "ownerBaseMailBox", ownerBaseMB )
		self.updateOwnerID( ownerBaseMB.id )

	def setDartMember( self, entityID ):
		"""
		define method
		�������ڳ�Ա
		"""
		dm = self.queryTemp( "dartMembers" )
		if dm is None:
			dm = {}
		dm[entityID] = 0
		self.setTemp( "dartMembers", dm )
		
	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.
		�����˺���
		@param   casterID: ʩ����ID
		@type    casterID: OBJECT_ID
		@param    skillID: ����ID
		@type     skillID: INT
		@param damageType: �˺����ͣ�see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: INT
		@param     damage: �˺���ֵ
		@type      damage: INT
		"""
		if casterID not in self.enemyForTongDart:
			attacker = BigWorld.entities.get( casterID )
			if attacker and attacker.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				self.enemyForTongDart.append( casterID )
		Monster.Monster.receiveDamage( self, casterID, skillID, damageType, damage )
		
	def getRelationEntity( self ):
		"""
		��ȡ��ϵ�ж�����ʵentity
		"""
		owner = BigWorld.entities.get( self.getOwnerID() )
		if not owner:
			return None
		else:
			return owner
		
	def queryCombatRelation( self, entity ):
		owner = BigWorld.entities.get( self.getOwnerID() )
		if owner:
			return owner.queryCombatRelation( entity )
		else:
			return csdefine.RELATION_ANTAGONIZE
		
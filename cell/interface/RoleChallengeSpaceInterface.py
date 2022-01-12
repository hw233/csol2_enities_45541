# -*- coding: gb18030 -*-

from bwdebug import *
import BigWorld
import Const
import ECBExtend
import csdefine
import csstatus

import csconst

# ��ʱ�˳�������λ��
TEMP_FORET_POSITION = (77.927963, 14.858975, 0.499060)
TEMP_FORET_DIRECTION = (1, 0, 0)
TEMP_FORET_SPACE = "fengming"
# ����BUFF
CHALLENGE_SKILL_ID = 122297001
CHALLENGE_SKILL_BUFF_ID = 9003

# ��Ƶ�ļ�
CHALLENGE_PI_SHAN_VIDEO = "compose-all.avi"

class RoleChallengeSpaceInterface:
	# ��ս�����Ľӿ�
	def __init__( self ):
		self.addTimer( Const.CALL_MONSTER_INIT_TIME, 0, ECBExtend.CALL_MONSTER_INIT )
	
	def isInSpaceChallenge( self ):
		return "fu_ben_hua_shan" in BigWorld.getSpaceDataFirstForKey( self.spaceID,  csconst.SPACE_SPACEDATA_KEY )
	
	def challengeSpaceEnter( self, exposed ):
		# ��������ս����
		# exposed method
		if exposed != self.id:
			return 
			
		reqLevel = self.level
		if self.isInTeam():
			if BigWorld.globalData.has_key( "spaceChallengeTeam_%d"%self.teamMailbox.id ):
				spaceChallengeKey = BigWorld.globalData[ "spaceChallengeTeam_%d"%self.teamMailbox.id ]
				self.spaceChallengeKey = spaceChallengeKey
				BigWorld.globalData[ "SpaceChallengeMgr" ].newJoin( spaceChallengeKey, self.base, self.databaseID )
				return
				
			entities = []
			dbidList = []
			if not self.isTeamCaptain() :
				self.statusMessage( csstatus.CHALLENGE_OPEN_MUST_CAPTAIN )
				return
			
			teamMemberList = self.getAllMemberInRange( 30 )
			for m in teamMemberList:
				# ������Ҫ�Ƿ�addTeamMember��ָ����Լ���Ӷ�ν��б���
				if m.id not in [ e.id for e in entities ]:
					entities.append( m.base )
					dbidList.append( m.databaseID )
					m.set( "challengeSpaceType", csconst.SPACE_CHALLENGE_TYPE_MANY )
					
			BigWorld.globalData[ "SpaceChallengeMgr" ].onRequestChallengeTeam( entities, dbidList, reqLevel, self.teamMailbox )
		else:
			self.set( "challengeSpaceType", csconst.SPACE_CHALLENGE_TYPE_SINGLE )
			BigWorld.globalData[ "SpaceChallengeMgr" ].onRequestChallenge( self.base, self.databaseID, reqLevel )
	
	def challengeSpaceOnStart( self, spaceChallengeKey, spaceChallengeGate, spaceKey, position, direction ):
		# define method
		# ��ս������ʼ
		if self.isInTeam():
			self.addActivityCount( csdefine.ACTIVITY_CHALLENGE_FUBEN_MANY )
		else:
			self.addActivityCount( csdefine.ACTIVITY_CHALLENGE_FUBEN )
			
		self.spaceChallengeKey = spaceChallengeKey
		self.challengeSpaceGotoGate( spaceChallengeGate, spaceKey, position, direction )
	
	def challengeSpaceGotoGate( self, spaceChallengeGate, spaceKey, position, direction ):
		# define method
		# ��ս��������ָ����
		if self.query( "spaceChallengeGate" ):
			self.setTemp( "isChallengeGotoGate", True )
			
		self.set( "spaceChallengeGate", spaceChallengeGate )
		actPet = self.pcg_getActPet()
		if actPet:
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )
			
		self.gotoSpace( spaceKey, position, direction )
	
	def challengeSpaceOnEnd( self ):
		# define method
		# ��ս��������
		self.remove( "spaceChallengeGate" )
		self.spaceChallengeKey = ""
		self.remove( "challengeSpaceAvatar" )
		self.remove( "challengeSpaceType" )
		#self.stopMagicChangeChallenge()
		#self.removeAllBuffByBuffID( CHALLENGE_SKILL_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE ] )
		self.gotoSpace( TEMP_FORET_SPACE, TEMP_FORET_POSITION, TEMP_FORET_DIRECTION )
		params = {}
		self.client.challengeSpaceOnEnd( params )
		
	def challengeSpaceIsTimeOut( self ):
		# define method.
		# ��ҵ�½
		self.remove( "spaceChallengeGate" )
		self.spaceChallengeKey = ""
		self.remove( "challengeSpaceAvatar" )
		
	def challengeSpaceSetAvatar( self, exposed, avatarType ):
		# ������ս�����Ӣ��
		# exposed method
		if exposed != self.id:
			return
			
		self.set( "challengeSpaceAvatar",  avatarType )
		# �㲥������������Ӣ�۵�ְҵ
		teamMemberList = self.getAllMemberInRange( 30 )
		for m in teamMemberList:
			m.client.challengeSpaceReceivesSetAvatar( self.id, avatarType )
	
	def challengeSpaceOnLeaveSpecial( self ):
		# �Ѿ��뿪��ս����������ָ�س�/ʹ����·��ȵ�������ʽ�����˳�����
		# ֪ͨ�ͻ���
		dict = {}
		self.client.challengeSpaceOnEnd( dict )
	
	def challengeSpacePassDoor( self ):
		# define method
		if self.isInTeam() and not self.isTeamCaptain():
			self.statusMessage( csstatus.CHALLENGE_SPACE_DOOR_NOT_CAPTIAN )
			return

		if self.spaceChallengeKey:
			BigWorld.globalData["SpaceChallengeMgr"].passGateDoor( self.spaceChallengeKey )
		else:
			ERROR_MSG( "challengeGate is %d, spaceChallengeKey is %s"%( currentGate, self.spaceChallengeKey ) )
	
	def challengeSpaceReEnter( self ):
		# ���½�����ս����
		if self.spaceChallengeKey:
			BigWorld.globalData[ "SpaceChallengeMgr" ].reEnter( self.spaceChallengeKey, self.base )
	
	def challengeSpaceEnterBaoXiang( self ):
		# define method
		# ���뱦�ظ���
		pass
	
	def challengeSpaceEnterPiShan( self ):
		# define method
		# ������ɽ����
		#self.client.playVideo( CHALLENGE_PI_SHAN_VIDEO )
		pass
		
	# ------------------------------
	# �����ٻ��Ľӿ�
	# ------------------------------
	def callEntity( self, entityID, entityDict, entityPosition, entityDirection ):
		# �ٻ�entity
		entityDict[ "owner" ] = self.base
		entityDict[ "ownerID" ] = self.id
		# �����Ѿ��ٻ���Monster�������Ҫ���¹���
		callMonsterList = self.query( "callMonsterList", [] )
		for m in callMonsterList:
			m.cell.onOwnerCallMonster( entityID )
		self.base.createNPCObject( self, entityID, entityPosition, entityDirection, entityDict )
	
	def registerCallMonster( self, BaseMailBox ):
		# define method
		# ���ﴴ���󣬰��Լ�ע�ᵽ��������
		callMonsterList = self.query( "callMonsterList", [] )
		if BaseMailBox:
			callMonsterList.append( BaseMailBox )
			self.set( "callMonsterList", callMonsterList )
	
	def removeCallMonster( self, BaseMailBox ):
		# define method
		# ���б�ɾ����Ч��entity
		callMonsterList = self.query( "callMonsterList", [] )
		cmIDList = [ m.id for m in callMonsterList ]
		if BaseMailBox.id in cmIDList:
			i = cmIDList.index( BaseMailBox.id )
			del callMonsterList[ i ]
			self.set( "callMonsterList", callMonsterList )
	
	def onTimer_initCallMonster( self,  timerID, cbID ):
		# �һ��ٻ�entity
		callMonsterList = self.query( "callMonsterList", [] )
		for m in callMonsterList:
			if m:
				m.cell.setOwner( self.base )
		
		self.remove( "callMonsterList" )
	
	def onRemoteFollowCallMonster( self, baseMailBox ):
		# defined method.
		# �����л������Զ�̸���Ļص�
		baseMailBox.cell.followMaster( int( self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY ) ), self, self.position )
	
	
	# ------------------------------
	# ����/���ߴ���
	# ------------------------------
	def onDestroy( self ):
		# ����
		callMonsterList = self.query( "callMonsterList", [] )
		for m in callMonsterList:
			m.cell.onOwnerDestroy()
			
		if self.spaceChallengeKey:
			BigWorld.globalData["SpaceChallengeMgr"].playerDisconnected( self.spaceChallengeKey, self.base )
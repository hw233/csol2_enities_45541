# -*- coding:gb18030 -*-

from Function import Function
import csstatus
import csdefine
from bwdebug import *
import Const
import BigWorld

class FuncTanabataQuiz( Function ):
	"""
	��Ϧ����ʴ����Ի�
	"""
	def valid( self, playerEntity, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��
		
		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True
		
	def do( self, playerEntity, talkEntity = None ):
		"""
		ִ��һ������

		@param playerEntity: ���
		@type  playerEntity: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		playerEntity.endGossip( talkEntity )
		if talkEntity is None:
			ERROR_MSG( "player( %s ) talk entity is None." % player.getName() )
			return
		if not BigWorld.globalData.has_key( "TanabataQuizStart" ):
			playerEntity.statusMessage( csstatus.ROLE_TANABATA_QUIZ_NOT_START )
			return
		if not playerEntity.isTeamCaptain():
			playerEntity.statusMessage( csstatus.ROLE_TANABATA_QUIZ_CAPTAIN_TALK )
			return
		teammateNum = playerEntity.getTeamCount()
		if teammateNum < 2:
			playerEntity.statusMessage( csstatus.ROLE_TANABATA_QUIZ_NO_PARTNER )
			return
		if teammateNum > 2:
			playerEntity.statusMessage( csstatus.ROLE_TANABATA_QUIZ_MORE_TEAMMATE )
			return

		teammateList = playerEntity.getAllMemberInRange( Const.TANABATA_QUIZ_TEAMMATE_DISTANCE )
		if len( teammateList ) < 2:
			playerEntity.statusMessage( csstatus.ROLE_TANABATA_QUIZ_NEAR_NO_PARTNER )
			return
		teammateEntity = teammateList[0] if teammateList[1].id == playerEntity.id else teammateList[1]
		if teammateEntity.state == csdefine.ENTITY_STATE_DEAD:
			return
		if not teammateEntity.isReal():	# Ҫ��֤teammate��real entity����Ҫ����teammate�Ļ���
			playerEntity.statusMessage( csstatus.ROLE_TANABATA_QUIZ_NEAR_NO_PARTNER )
			return
		if teammateEntity.getGender() == playerEntity.getGender():
			playerEntity.statusMessage( csstatus.ROLE_TANABATA_QUIZ_NO_PARTNER )
			return
		if playerEntity.level < Const.TANABATA_QUIZ_LEVEL_LIMIT or teammateEntity.level < Const.TANABATA_QUIZ_LEVEL_LIMIT:
			playerEntity.statusMessage( csstatus.ROLE_TANABATA_QUIZ_TEAMMATE_LEVEL_LACK, Const.TANABATA_QUIZ_LEVEL_LIMIT )
			return

		if player.isActivityCanNotJoin( csdefine.ACTIVITY_TANABATA_QUIZ )  or teammateEntity.isActivityCanNotJoin( csdefine.ACTIVITY_TANABATA_QUIZ ) :
			playerEntity.statusMessage( csstatus.ROLE_TANABATA_QUIZ_ALREDY_ANSWERED )
			return
			
		# { "talkNPCID":npc id, "targetID":����id, "tanabata_question_id":��ǰ���ڻش����Ŀ }
		playerEntity.setTemp( "tanabata_quiz_data", { "talkNPCID":talkEntity.id, "targetID":teammateEntity.id, "tanabata_question_id":0 } )
		teammateEntity.setTemp( "tanabata_quiz_data", { "talkNPCID":talkEntity.id, "targetID":playerEntity.id, "tanabata_question_id":0 } )
		
		playerEntity.spellTarget( 780043001, playerEntity.id )
		teammateEntity.spellTarget( 780043001, teammateEntity.id )
		
		playerEntity.addActivityCount( csdefine.ACTIVITY_TANABATA_QUIZ )
		teammateEntity.remoteAddActivityCount( csdefine.ACTIVITY_TANABATA_QUIZ )
		
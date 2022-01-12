# -*- coding:gb18030 -*-

from SpellBase import Buff
from bwdebug import *
import csstatus
import Const
import items
import csdefine
import ECBExtend
import BigWorld
import csdefine
import cschannel_msgs
import csconst

g_items = items.instance()

class Buff_99023( Buff ):
	"""
	七夕情感问答buff
	
	每一次loop检查玩家是否还符合答题条件，检查玩家答题结果，给玩家出题
	"""
	def __init__( self ):
		Buff.__init__( self )
		
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。
		
		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff.doBegin( self, receiver, buffData )
		receiver.statusMessage( csstatus.ROLE_TANABATA_QUIZ_PLEASE_READY )
		
	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		用于buff，表示buff在每一次心跳时应该做什么。
		
		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL；如果允许继续则返回True，否则返回False
		@rtype:  BOOL
		"""
		receiver.endGossip( None )	# 玩家的对话窗口可能还没关闭
		tanabataQuizData = receiver.queryTemp( "tanabata_quiz_data", None )
		if tanabataQuizData is None:
			ERROR_MSG( "player( %s ) cannot find tanabata_quiz_data." % ( receiver.getName() ) )
			return False
		talkNPC = BigWorld.entities.get( tanabataQuizData["talkNPCID"] )
		if talkNPC is None or receiver.position.distTo( talkNPC.position ) > csconst.COMMUNICATE_DISTANCE:
			receiver.statusMessage( csstatus.ROLE_TANABATA_QUIZ_NPC_TOO_FAR )
			return False
		teammateList = receiver.getAllMemberInRange( Const.TANABATA_QUIZ_TEAMMATE_DISTANCE )
		if len( teammateList ) < 2:
			receiver.statusMessage( csstatus.ROLE_TANABATA_QUIZ_NO_PARTNER )
			return False
		if receiver.getTeamCount() > 2:
			receiver.statusMessage( csstatus.ROLE_TANABATA_QUIZ_MORE_TEAMMATE )
			return False
		teammateEntity = teammateList[0] if teammateList[1].id == receiver.id else teammateList[1]
		if teammateEntity.spaceID != receiver.spaceID or teammateEntity.spaceID != talkNPC.spaceID:
			return False
		if teammateEntity.position.distTo( talkNPC.position ) > csconst.COMMUNICATE_DISTANCE:	# 队友和npc距离也需要判断
			receiver.statusMessage( csstatus.ROLE_TANABATA_QUIZ_TEAMMATE_NPC_TOO_FAR )
			return False
		if teammateEntity.id != tanabataQuizData["targetID"]:
			receiver.statusMessage( csstatus.ROLE_TANABATA_QUIZ_NO_PARTNER )
			return False
		if teammateEntity.state == csdefine.ENTITY_STATE_DEAD or receiver.state == csdefine.ENTITY_STATE_DEAD:
			return False
		# 检查双方答案是否一致，默认答案不一致
		next_tanabata_question_id = tanabataQuizData["tanabata_question_id"] + 1
		if next_tanabata_question_id > 1:
			if receiver.queryTemp( "tanabata_quiz_target_answer", "" ) == receiver.queryTemp( "tanabata_quiz_self_answer", None ):
				itemInstance = g_items.createDynamicItem( Const.TANABATA_QUIZ_REWARD_ITEM )
				if not receiver.addItemAndNotify_( itemInstance, csdefine.ADD_ITEM_TANABATA_QUIZ ):
					receiver.mail_send_on_air_withItems( receiver.getName(), csdefine.MAIL_TYPE_QUICK, cschannel_msgs.TANABATA_QUIZ_MAIL_TITLE, "", [itemInstance] )
					receiver.statusMessage( csstatus.ROLE_TANABATA_QUIZ_MAIL_NOTIFY )
				receiver.statusMessage( csstatus.ROLE_TANABATA_QUIZ_ANSWER_RIGHT )
			else:
				receiver.statusMessage( csstatus.ROLE_TANABATA_QUIZ_ANSWER_WRONG )
				
		if next_tanabata_question_id > Const.TANABATA_QUIZ_DAY_QUESTIONS_COUNT:	# 已经是最后一道题目
			receiver.statusMessage( csstatus.ROLE_TANABATA_QUIZ_FINISH )
			return False
		receiver.removeTemp( "tanabata_quiz_self_answer" )
		receiver.removeTemp( "tanabata_quiz_target_answer" )
		receiver.removeTemp( "tanabataOptionsData" )
		receiver.setTemp( "talkID", "TANABATA_QUIZ" )
		receiver.setTemp( "talkNPCID", talkNPC.id )
		tanabataQuizData["tanabata_question_id"] = next_tanabata_question_id
		receiver.addTimer( 0, 0, ECBExtend.AUTO_TALK_CBID )	# 下一个tick触发新对话
		
		return Buff.doLoop( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。
		
		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		receiver.removeTemp( "tanabata_quiz_data" )
		receiver.removeTemp( "tanabata_quiz_self_answer" )
		receiver.removeTemp( "tanabata_quiz_target_answer" )
		receiver.removeTemp( "tanabataOptionsData" )
		Buff.doEnd( self, receiver, buffData )
		
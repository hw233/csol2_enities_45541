# -*- coding: gb18030 -*-

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import random
from Question import Question
import Love3
import csdefine
from Resource.SkillLoader import g_skills

class Buff_299023( Buff_Normal ):
	"""
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self.param1 = 0


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.param1 = int(dict["Param1"])			#�ش𲻳����⣬�����������



	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		self.newQuestion( receiver )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		if not receiver.queryTemp( "Buff_question_result", False ):
			g_skills[self.param1].getBuffLink(0).getBuff().receive( None, receiver )
			#receiver.spellTarget( self.param1, receiver.id )
		else:
			receiver.removeTemp( "Buff_question_result" )
		receiver.client.onBuffQuestionEnd()

	def newQuestion( self, player ):
		"""
		"""
		key = random.choice( Love3.g_ieQuestionSection.keys() )
		questionItem = Question()
		questionItem.questDes = Love3.g_ieQuestionSection[key]["questionDes"].asString
		sec = Love3.g_ieQuestionSection[key]
		questionItem.answers = {
			"a" : sec["a"].asString,
			"b" : sec["b"].asString,
			"c" : sec["c"].asString,
			"d" : sec["d"].asString,
			"e" : sec["e"].asString,
			}
		questionItem.buffID = self.getBuffID()
		player.client.onBuffQuestionStart( questionItem )
		player.setTemp( "Buff_questionID", key )
	
	def answerQuestion( self, player, answer ):
		"""
		"""
		player.client.onBuffQuestionEnd()
		key = player.queryTemp( "Buff_questionID", "" )
		if Love3.g_ieQuestionSection[key]["answer"].asString == answer:
			player.setTemp( "Buff_question_result", True )
			return
		player.removeBuffByID( self.getID(), [csdefine.BUFF_INTERRUPT_NONE] )

	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		����buff����ʾbuff��ÿһ������ʱӦ����ʲô��

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL�������������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		spaceType = receiver.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if not spaceType in self.spaceNames:
			receiver.client.onBuffQuestionEnd()
			return False
		return Buff_Normal.doLoop( self, receiver, buffData )
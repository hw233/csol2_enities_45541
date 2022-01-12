# -*- coding: gb18030 -*-

from NPCObject import NPCObject
from bwdebug import *
import Love3
import csstatus
import random

class SpringRiddleNPC( NPCObject ):
	def __init__( self ):
		NPCObject.__init__( self )
		
	def questQuestionHandle( self, selfEntity, playerEntity, dlgKey ):
		"""
		NPC�Ի�����
		
		��������ɸѡ����ȡ�Ը���NPCObject��Ч�ʲ��ߣ���������ʱ���ܣ��պ�����
		"""
		if dlgKey == "START_SPRING_RIDDLE":
			typeQuestionKeys = []															#���ϵ�ǰ�������͵� ��ĿID�б�
			question_id_list = playerEntity.queryTemp( "spring_riddle_question_id_list", [] )
			question_type = playerEntity.queryTemp("question_type")
			for i in Love3.g_questQuestionSection.keys():
				if Love3.g_questQuestionSection[i]["type"].asInt == question_type and i not in question_id_list:
					typeQuestionKeys.append( i )
					
			if len( typeQuestionKeys ) == 0:
				for i in Love3.g_questQuestionSection.keys():
					if Love3.g_questQuestionSection[i]["type"].asInt == question_type:
						typeQuestionKeys.append( i )
						
			questionID = random.sample( typeQuestionKeys, 1 )[0]
			playerEntity.setTemp( "current_question_id", questionID )
			question_id_list = playerEntity.queryTemp( "spring_riddle_question_id_list", [] )
			question_id_list.append( questionID )
			playerEntity.setTemp( "spring_riddle_question_id_list", question_id_list )
			
			playerEntity.setGossipText( Love3.g_questQuestionSection[questionID]["questionDes"].asString )
			playerEntity.addGossipOption( "a", "a." + Love3.g_questQuestionSection[questionID]["a"].asString )
			playerEntity.addGossipOption( "b", "b." + Love3.g_questQuestionSection[questionID]["b"].asString )
			playerEntity.addGossipOption( "c", "c." + Love3.g_questQuestionSection[questionID]["c"].asString )
			if Love3.g_questQuestionSection[questionID]["d"].asString != "":
				playerEntity.addGossipOption( "d", "d." + Love3.g_questQuestionSection[questionID]["d"].asString )
			if Love3.g_questQuestionSection[questionID]["e"].asString != "":
				playerEntity.addGossipOption( "e", "e." + Love3.g_questQuestionSection[questionID]["e"].asString )
			playerEntity.sendGossipComplete( selfEntity.id )
		elif dlgKey == "a":
			self.answerProcess( selfEntity, playerEntity, "a" )
			playerEntity.endGossip( selfEntity )
		elif dlgKey == "b":
			self.answerProcess( selfEntity, playerEntity, "b" )
			playerEntity.endGossip( selfEntity )
		elif dlgKey == "c":
			self.answerProcess( selfEntity, playerEntity, "c" )
			playerEntity.endGossip( selfEntity )
		elif dlgKey == "d":
			self.answerProcess( selfEntity, playerEntity, "d" )
			playerEntity.endGossip( selfEntity )
		elif dlgKey == "e":
			self.answerProcess( selfEntity, playerEntity, "e" )
			playerEntity.endGossip( selfEntity )
		else:
			return False
		return True
		
	def answerProcess(  self, selfEntity, playerEntity, answerID  ):
		"""
		�Ի��ʴ���
		"""
		if playerEntity.queryTemp( "current_question_id" ) == None:
			return
		if Love3.g_questQuestionSection[playerEntity.queryTemp( "current_question_id" )]['answer'].asString == answerID:
			playerEntity.springRiddleReward()
			playerEntity.statusMessage( csstatus.IE_ANSWER_TRUE )
			playerEntity.clientEntity( selfEntity.id ).onAnswerSuceed( True )
		else:
			playerEntity.statusMessage( csstatus.IE_ANSWER_FALSE )
			playerEntity.clientEntity( selfEntity.id ).onAnswerSuceed( False )
		playerEntity.removeTemp( "current_question_id" )
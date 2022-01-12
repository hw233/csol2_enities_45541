# -*- coding:gb18030 -*-

from Chapman import Chapman
from bwdebug import *
from Love3 import g_tanabataQuizLoader
import random
import BigWorld

class NPCTanabata( Chapman ):
	"""
	��Ϧ� ��д��� npc
	"""
	def questQuestionHandle( self, selfEntity, playerEntity, dlgKey ):
		"""
		"""
		tanabata_quiz_data = playerEntity.queryTemp( "tanabata_quiz_data", None )
		if tanabata_quiz_data is None:
			return False
		if dlgKey == "TANABATA_QUIZ":
			questionData = g_tanabataQuizLoader.getQuestion( tanabata_quiz_data["tanabata_question_id"] )
			playerEntity.setGossipText( questionData["questionDes"] )
			optionsList = questionData["options"][:]
			random.shuffle( optionsList )
			tanabataOptionsData = {}	# ��¼��Ӧѡ��Ĵ��ַ������Ա�����֪�����ѡ����ʲô��
			
			# ������3��ѡ����5��
			aAnswer = optionsList.pop()
			tanabataOptionsData["a"] = aAnswer
			playerEntity.addGossipOption( "a", "a." + aAnswer )
			bAnswer = optionsList.pop()
			tanabataOptionsData["b"] = bAnswer
			playerEntity.addGossipOption( "b", "b." + bAnswer )
			cAnswer = optionsList.pop()
			tanabataOptionsData["c"] = cAnswer
			playerEntity.addGossipOption( "c", "c." + cAnswer )
			if len( optionsList ) > 0:
				dAnswer = optionsList.pop()
				tanabataOptionsData["d"] = dAnswer
				playerEntity.addGossipOption( "d", "d." + dAnswer )
			if len( optionsList ) > 0:
				eAnswer = optionsList.pop()
				tanabataOptionsData["e"] = eAnswer
				playerEntity.addGossipOption( "e", "e." + eAnswer )
			playerEntity.setTemp( "tanabataOptionsData", tanabataOptionsData )
			playerEntity.sendGossipComplete( selfEntity.id )
		elif dlgKey in [ "a", "b", "c", "d", "e" ]:
			playerEntity.endGossip( selfEntity )
			tanabataOptionsData = playerEntity.queryTemp( "tanabataOptionsData", None )
			if tanabataOptionsData is None:
				return False
			targetEntity = BigWorld.entities.get( tanabata_quiz_data["targetID"] )
			if targetEntity is None:
				return False
			answer = tanabataOptionsData[dlgKey]
			playerEntity.setTemp( "tanabata_quiz_self_answer", answer )
			targetEntity.setTemp( "tanabata_quiz_target_answer", answer )
		else:
			return False
		return True
		
		
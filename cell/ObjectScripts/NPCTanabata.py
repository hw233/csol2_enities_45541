# -*- coding:gb18030 -*-

from Chapman import Chapman
from bwdebug import *
from Love3 import g_tanabataQuizLoader
import random
import BigWorld

class NPCTanabata( Chapman ):
	"""
	七夕活动 情感大考验 npc
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
			tanabataOptionsData = {}	# 记录对应选项的答案字符串，以便答题后知道玩家选择了什么答案
			
			# 至少有3个选项，最多5个
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
		
		
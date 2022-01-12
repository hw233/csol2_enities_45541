# -*- coding: gb18030 -*-

import time
import random
from bwdebug import *

#**
# ս��״̬�µ�AIִ�����
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def onFightAIHeartbeat( self ):
	"""
	ս��״̬��AI �� ������

	ע�⣺Ϊ���Ч�ʣ��˽ű������߼���ʹ��c++��ʵ��ΪonFightAIHeartbeat_AIInterface_cpp���˷�����ʧЧ�������Ҫ�޸Ĵ˷���������ϵwangshufeng��15:01 2012-12-7 by wsf��
	"""
	if self.fightStateAICount <= 0:
		return
	elif self.intonating() or self.inHomingSpell():
		return

	if self.fightStartTime == 0.0:
		self.fightStartTime = time.time()

	# ƥ��AI���еȼ�
	if self.attrAINowLevelTemp != self.attrAINowLevel:
		self.attrAINowLevel = self.attrAINowLevelTemp
	nTitle = getattr(self,"title")
	aiDebug = self.queryTemp("debug",0)
	if nTitle == "debug" or aiDebug == 1:
		DEBUG_MSG_FOR_AI( self, "++++++++++++++++++++++++++++++++++++++", "" )

	if nTitle == "debug" or aiDebug == 1:
		DEBUG_MSG_FOR_AI( self, "��ʼս��AI", "" )
	# ִ��ͨ��AI��ѭ��
	for ai in self.attrAttackStateGenericAIs.get( self.attrAINowLevel, [] ):
		if self.isDestroyed or not self.isReal(): return
		if self.aiCommonCheck( ai ):
			if nTitle == "debug" or aiDebug == 1:
				DEBUG_MSG_FOR_AI( self, "  ��ʼAI: %i"%ai.getID(), "AI_DEBUG_LOG:begin ( NPCID %i className %s) ) AttackStateGenericAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID) )
			ai.do( self )
			if nTitle == "debug" or aiDebug == 1:
				DEBUG_MSG_FOR_AI( self, "  ����AI: %i"%ai.getID(), "AI_DEBUG_LOG:end ( NPCID %i className %s) ) AttackStateGenericAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID ) )
	if nTitle == "debug" or aiDebug == 1:
		DEBUG_MSG_FOR_AI( self, "����ս��AI", "" )

	if self.isDestroyed:
		return

	# ������AI������ִ������AI
	if len( self.comboAIArray ):
		self.doComboAI()

	if not self.comboAIState:		# ����Ϊִ��ʧ�ܻ�ûִ�ж���Ϊ
		if nTitle == "debug" or aiDebug == 1:
			DEBUG_MSG_FOR_AI( self, "��ʼ����AI", "" )
		# ִ������AI��ѭ��
		if self.insert_ai and self.aiCommonCheck( self.insert_ai ):
			self.insert_ai.do( self )
		else:
			for ai in self.attrSchemeAIs.get( self.attrAINowLevel, [] ):
				if self.isDestroyed or not self.isReal(): return
				if self.aiCommonCheck( ai ):
					if nTitle == "debug" or aiDebug == 1:
						DEBUG_MSG_FOR_AI( self, "  ��ʼAI: %i"%ai.getID(), "AI_DEBUG_LOG:begin ( NPCID %i className %s) ) SchemeAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID ) )
					ai.do( self )
					if nTitle == "debug" or aiDebug == 1:
						DEBUG_MSG_FOR_AI( self, "  ����AI: %i"%ai.getID(), "AI_DEBUG_LOG:end ( NPCID %i className %s) ) SchemeAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID ) )
					break
		if nTitle == "debug" or aiDebug == 1:
			DEBUG_MSG_FOR_AI( self, "��������AI", "" )
		if self.isDestroyed:
			return

		comboID = self.comboAICheck()
		if comboID:			# �ܷ�ִ������AI
			self.doComboAI( comboID )
		if not self.comboAIState:		# ����Ϊִ��ʧ��
			if nTitle == "debug" or aiDebug == 1:
				DEBUG_MSG_FOR_AI( self, "��ʼ����AI", "" )
			# ִ��SAI ÿ��ִ���б�ĵ�һ��AI�����ִ��ʧ�ܣ�����������б�
			isSAIDo = False
			if len( self.saiArray ):
				ai = self.saiArray.pop( 0 )
				if self.aiCommonCheck( ai ):
					ai.do( self )
					isSAIDo = True
				else:
					self.saiArray = []
			if not isSAIDo:
				# ִ������AI��ѭ��
				doSuccess = False
				for ai in self.attrSpecialAIs.get( self.attrAINowLevel, [] ):
					if self.isDestroyed or not self.isReal(): return
					if self.aiCommonCheck( ai ):
						if nTitle == "debug" or aiDebug == 1:
							DEBUG_MSG_FOR_AI( self, "  ��ʼAI: %i"%ai.getID(), "AI_DEBUG_LOG:begin ( NPCID %i className %s) ) SpecialAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID) )
						ai.do( self )
						if nTitle == "debug" or aiDebug == 1:
							DEBUG_MSG_FOR_AI( self, "  ����AI: %i"%ai.getID(), "AI_DEBUG_LOG:end ( NPCID %i className %s) ) SpecialAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID ) )
						doSuccess = True
						break

				if not doSuccess:
					self.onSpecialAINotDo()

		if nTitle == "debug" or aiDebug == 1:
			DEBUG_MSG_FOR_AI( self, "��������AI", "" )
		if self.isDestroyed:
			return

	self.setAITargetID( 0 ) 	# ��ձ���AI����, ��һ������һ��ȥ����
	self.comboAIState = False	# ���comboAIִ��״̬

	if nTitle == "debug" or aiDebug == 1:
		DEBUG_MSG_FOR_AI( self, "----------------------------------------", "" )

#**
# AI �Ĺ����ж�����
#
# >>> ��Ҫ�޸Ĵ˷������ˣ����޸���ɺ�֪ͨ�����Ա�޸���Ӧ��c++������<<<
#**
def aiCommonCheck( self, ai ):
	"""
	AI �Ĺ����ж�����
	"""
	# ��ai�Ƿ���һ��e��ai �ǵĻ�������
	if self.isEAI( ai.getID() ):
		return False

	# ִ��ai�Ļ����
	activeRate = ai.getActiveRate()
	if activeRate < 100:
		if activeRate <= 0 or random.randint( 0, 100 ) > activeRate:
			nTitle=getattr( self,"title")
			if nTitle == "debug" or self.queryTemp("debug",0) == 1:
				DEBUG_MSG_FOR_AI( self, "    ai:%i ִ��ʧ�ܣ�ԭ��: ���� %i��"%( ai.getID(), activeRate ), "AI_DEBUG_LOG:( NPCID %i className %s )'s AIData %i whose activeRate is %i , will not be implemented" % ( self.id, self.className, ai.getID(), activeRate ))

			return False

	# ��� ai��������
	if not ai.check( self ):
		nTitle=getattr( self,"title")
		if nTitle == "debug" or self.queryTemp("debug",0) == 1:
			DEBUG_MSG_FOR_AI( self, "    ����ai:%i ִ��ʧ�ܡ�"%ai.getID(), "AI_DEBUG_LOG:( NPCID %i className %s ) AICondtion result False in AIData %i" % ( self.id, self.className, ai.getID() ))

		return False
	return  True
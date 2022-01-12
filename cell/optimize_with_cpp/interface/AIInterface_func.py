# -*- coding: gb18030 -*-

import time
import random
from bwdebug import *

#**
# 战斗状态下的AI执行入口
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def onFightAIHeartbeat( self ):
	"""
	战斗状态下AI 的 心跳。

	注意：为提高效率，此脚本方法逻辑已使用c++来实现为onFightAIHeartbeat_AIInterface_cpp，此方法已失效，如果需要修改此方法，请联系wangshufeng。15:01 2012-12-7 by wsf。
	"""
	if self.fightStateAICount <= 0:
		return
	elif self.intonating() or self.inHomingSpell():
		return

	if self.fightStartTime == 0.0:
		self.fightStartTime = time.time()

	# 匹配AI运行等级
	if self.attrAINowLevelTemp != self.attrAINowLevel:
		self.attrAINowLevel = self.attrAINowLevelTemp
	nTitle = getattr(self,"title")
	aiDebug = self.queryTemp("debug",0)
	if nTitle == "debug" or aiDebug == 1:
		DEBUG_MSG_FOR_AI( self, "++++++++++++++++++++++++++++++++++++++", "" )

	if nTitle == "debug" or aiDebug == 1:
		DEBUG_MSG_FOR_AI( self, "开始战斗AI", "" )
	# 执行通用AI的循环
	for ai in self.attrAttackStateGenericAIs.get( self.attrAINowLevel, [] ):
		if self.isDestroyed or not self.isReal(): return
		if self.aiCommonCheck( ai ):
			if nTitle == "debug" or aiDebug == 1:
				DEBUG_MSG_FOR_AI( self, "  开始AI: %i"%ai.getID(), "AI_DEBUG_LOG:begin ( NPCID %i className %s) ) AttackStateGenericAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID) )
			ai.do( self )
			if nTitle == "debug" or aiDebug == 1:
				DEBUG_MSG_FOR_AI( self, "  结束AI: %i"%ai.getID(), "AI_DEBUG_LOG:end ( NPCID %i className %s) ) AttackStateGenericAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID ) )
	if nTitle == "debug" or aiDebug == 1:
		DEBUG_MSG_FOR_AI( self, "结束战斗AI", "" )

	if self.isDestroyed:
		return

	# 有连续AI，优先执行连续AI
	if len( self.comboAIArray ):
		self.doComboAI()

	if not self.comboAIState:		# 多行为执行失败或没执行多行为
		if nTitle == "debug" or aiDebug == 1:
			DEBUG_MSG_FOR_AI( self, "开始配置AI", "" )
		# 执行配置AI的循环
		if self.insert_ai and self.aiCommonCheck( self.insert_ai ):
			self.insert_ai.do( self )
		else:
			for ai in self.attrSchemeAIs.get( self.attrAINowLevel, [] ):
				if self.isDestroyed or not self.isReal(): return
				if self.aiCommonCheck( ai ):
					if nTitle == "debug" or aiDebug == 1:
						DEBUG_MSG_FOR_AI( self, "  开始AI: %i"%ai.getID(), "AI_DEBUG_LOG:begin ( NPCID %i className %s) ) SchemeAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID ) )
					ai.do( self )
					if nTitle == "debug" or aiDebug == 1:
						DEBUG_MSG_FOR_AI( self, "  结束AI: %i"%ai.getID(), "AI_DEBUG_LOG:end ( NPCID %i className %s) ) SchemeAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID ) )
					break
		if nTitle == "debug" or aiDebug == 1:
			DEBUG_MSG_FOR_AI( self, "结束配置AI", "" )
		if self.isDestroyed:
			return

		comboID = self.comboAICheck()
		if comboID:			# 能否执行连续AI
			self.doComboAI( comboID )
		if not self.comboAIState:		# 多行为执行失败
			if nTitle == "debug" or aiDebug == 1:
				DEBUG_MSG_FOR_AI( self, "开始特殊AI", "" )
			# 执行SAI 每次执行列表的第一条AI，如果执行失败，则清空整个列表
			isSAIDo = False
			if len( self.saiArray ):
				ai = self.saiArray.pop( 0 )
				if self.aiCommonCheck( ai ):
					ai.do( self )
					isSAIDo = True
				else:
					self.saiArray = []
			if not isSAIDo:
				# 执行特殊AI的循环
				doSuccess = False
				for ai in self.attrSpecialAIs.get( self.attrAINowLevel, [] ):
					if self.isDestroyed or not self.isReal(): return
					if self.aiCommonCheck( ai ):
						if nTitle == "debug" or aiDebug == 1:
							DEBUG_MSG_FOR_AI( self, "  开始AI: %i"%ai.getID(), "AI_DEBUG_LOG:begin ( NPCID %i className %s) ) SpecialAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID) )
						ai.do( self )
						if nTitle == "debug" or aiDebug == 1:
							DEBUG_MSG_FOR_AI( self, "  结束AI: %i"%ai.getID(), "AI_DEBUG_LOG:end ( NPCID %i className %s) ) SpecialAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID ) )
						doSuccess = True
						break

				if not doSuccess:
					self.onSpecialAINotDo()

		if nTitle == "debug" or aiDebug == 1:
			DEBUG_MSG_FOR_AI( self, "结束特殊AI", "" )
		if self.isDestroyed:
			return

	self.setAITargetID( 0 ) 	# 清空本轮AI对象, 下一轮由下一轮去设置
	self.comboAIState = False	# 清空comboAI执行状态

	if nTitle == "debug" or aiDebug == 1:
		DEBUG_MSG_FOR_AI( self, "----------------------------------------", "" )

#**
# AI 的公共判断条件
#
# >>> 需要修改此方法的人，请修改完成后通知相关人员修改相应的c++方法。<<<
#**
def aiCommonCheck( self, ai ):
	"""
	AI 的公共判断条件
	"""
	# 该ai是否是一个e级ai 是的话不运行
	if self.isEAI( ai.getID() ):
		return False

	# 执行ai的活动概率
	activeRate = ai.getActiveRate()
	if activeRate < 100:
		if activeRate <= 0 or random.randint( 0, 100 ) > activeRate:
			nTitle=getattr( self,"title")
			if nTitle == "debug" or self.queryTemp("debug",0) == 1:
				DEBUG_MSG_FOR_AI( self, "    ai:%i 执行失败，原因: 几率 %i。"%( ai.getID(), activeRate ), "AI_DEBUG_LOG:( NPCID %i className %s )'s AIData %i whose activeRate is %i , will not be implemented" % ( self.id, self.className, ai.getID(), activeRate ))

			return False

	# 检查 ai基本条件
	if not ai.check( self ):
		nTitle=getattr( self,"title")
		if nTitle == "debug" or self.queryTemp("debug",0) == 1:
			DEBUG_MSG_FOR_AI( self, "    导致ai:%i 执行失败。"%ai.getID(), "AI_DEBUG_LOG:( NPCID %i className %s ) AICondtion result False in AIData %i" % ( self.id, self.className, ai.getID() ))

		return False
	return  True
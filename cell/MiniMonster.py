# -*- coding: gb18030 -*-


from Monster import Monster
import BigWorld
import csdefine
from bwdebug import *
import time

class MiniMonster( Monster ):
	"""
	精简战斗AI流程怪物
	"""
	def onFightAIHeartbeat( self ):
		"""
		战斗状态下AI 的 心跳，覆盖底层战斗心跳行为
		"""
		if not BigWorld.globalData["optimizeWithAI_ShortProcess"] :				# 根据配置进行切换
			Monster.onFightAIHeartbeat( self )	
			return 
			
		if self.fightStartTime == 0.0:
			self.fightStartTime = time.time()
			
		self.getScript().onFightAIHeartbeat( self )	# 为了减少怪物的类型，这里转由怪物的Script去做处理
		self.setAITargetID( 0 ) # 清空本轮AI对象, 下一轮由下一轮去设置
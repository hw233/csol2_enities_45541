# -*- coding: gb18030 -*-
#

import BigWorld
import csdefine
import csconst
import items
import ECBExtend
from QuestBox import QuestBox

class QuestBoxCampActivity( QuestBox ):
	"""
	阵营活动箱子：只有阵营活动在箱子所在地图开启箱子才可选中
	"""
	def taskStatus( self, selfEntity, playerEntity ):
		"""
		判断玩家和箱子的任务状态
		
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus（ state )
		state == True :  表示有这样的状态，告诉任务箱子可以被选中
		否则: 没有这样的状态，不能被选中
		""" 
		# 必须判断该entity是否为real，否则后面的queryTemp()一类的代码将不能正确执行。
		if not selfEntity.isReal():
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return
			
		if len( self.questData ) <= 0:
			if self.spellID <= 0:
				playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			else:
				playerEntity.clientEntity( selfEntity.id ).onTaskStatus( selfEntity.queryTemp( "quest_box_destroyed", 0 ) == 0 )
			return
			
		findQuest = False
		for id in self.questData.keys():
			quest = self.getQuest( id )
			if quest != None:
				findQuest = True
				break
		if not findQuest:
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False )
			return

		if selfEntity.queryTemp( "quest_box_destroyed", 0 ) != 0:	# 不等于0表示已经被触发过了，等待删除中
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False )
			return
			
		# 只有阵营活动在箱子所在地图开启才可以选取箱子
		if not BigWorld.globalData.has_key( "CampActivityCondition" ):
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False )
			return
		if playerEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) not in BigWorld.globalData["CampActivityCondition"][0]:
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( False )
			return

		indexTaskState = False
		for questID, taskIndex in self.questData.iteritems():
			if not playerEntity.taskIsCompleted( questID, taskIndex ):
				indexTaskState = True
				break
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus( indexTaskState )
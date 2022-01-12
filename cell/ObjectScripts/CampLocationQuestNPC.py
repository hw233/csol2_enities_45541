# -*- coding: gb18030 -*-

import random
import BigWorld
import csdefine
import csconst
from bwdebug import *

from NPC import NPC

RANDOM_AMOUNT = 5

class CampLocationQuestNPC( NPC ):
	"""
	阵营日常任务发布NPC
	阵营日常任务开启机制：根据当前阵营活动确定N个必要日常任务，另外从其他日常任务中随机M个，这两部分组成玩家可接的日常任务。CSOL-1774
	"""
	def __init__( self ):
		NPC.__init__( self )
		self.hasFiltrated = False			# 是否随机了阵营日常任务
		self._questStartList_record = set()

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		NPC.initEntity( self, selfEntity )
		BigWorld.globalData["CampMgr"].addDailyQuestNpcBases( selfEntity.base )
		
	def addStartQuest( self, questID ):
		"""
		virtual method.
		增加一个任务到开始列表中
		"""
		self._questStartList.add( questID )
		self._questStartList_record.add( questID )
	
	def embedQuests( self, selfEntity, player ):
		"""
		嵌入指定玩家所有可以显示的任务。
		"""
		if not self.hasFiltrated:
			self.hasFiltrated = True
			self.filtrateDailyQuest( selfEntity )
		NPC.embedQuests( self, selfEntity, player )

	def questStatus( self, selfEntity, playerEntity ):
		"""
		查询一个游戏对象所有任务相对于玩家的状态，状态将通过回调返回给client相对应的GameObject。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 玩家
		@type  playerEntity: Entity
		@return: 无
		"""
		if not self.hasFiltrated:
			self.hasFiltrated = True
			self.filtrateDailyQuest( selfEntity )
		NPC.questStatus( self, selfEntity, playerEntity )
		
		
	def filtrateDailyQuest( self, selfEntity ):
		"""
		阵营日常任务刷新：必要日常任务一定在开始任务列表中，其他非必要日常任务会随机几个添加到开始任务列表中，其他未随机到的移除；
		如何确定为必要日常任务：判断配置的脚本为QTRCampActivityCondition的requirement，如果通过说明此任务与当前阵营活动类型相匹配,为必要任务。
		因此阵营日常任务必须都配一个这种类型的requirement。
		"""
		self._questStartList = self._questStartList_record.copy()			# 先恢复原始数据
		removeQuests = []
		tempQuestList = []
		
		# 如果没开阵营活动，把所有阵营日常任务从NPC的开始任务列表中移除
		if not BigWorld.globalData.has_key( "CampActivityCondition" ):
			for id in self._questStartList:
				quest = self.getQuest( id )
				if quest.getType() == csdefine.QUEST_TYPE_CAMP_DAILY:
					removeQuests.append( id )
			for i in removeQuests:
				self._questStartList.remove( i )
		
		# 否则，刷新日常任务
		else:
			activitySpace = BigWorld.globalData["CampActivityCondition"][0]
			for id in self._questStartList:
				quest = self.getQuest( id )
				if quest.getType() == csdefine.QUEST_TYPE_CAMP_DAILY:		# 只有日常任务要做如下繁琐的判断
					passed = False
					for requirement in quest.requirements_:
						if requirement.__class__.__name__ == "QTRCampActivityCondition" and requirement.query( None ) and requirement._activityType != "":		# 必要日常任务，不动
							passed = True
							break
						
						elif requirement.__class__.__name__ == "QTRCampActivityCondition" and requirement._spaceName in activitySpace: # 非必要日常任务，但是是可随机的日常（地图匹配，只是活动类型不匹配），待定
							tempQuestList.append( id )
							break
					
					if not passed:
						removeQuests.append( id )
			
			# 先移除所有非必要日常任务
			for i in removeQuests:
				self._questStartList.remove( i )
				
			# 对待定日常任务进行随机
			if len( tempQuestList ) >= RANDOM_AMOUNT:
				for i in random.sample( tempQuestList, RANDOM_AMOUNT ):
					self._questStartList.add( i )
			else:
				for i in tempQuestList:
					self._questStartList.add( i )
			
		for role in selfEntity.entitiesInRangeExt( csconst.ROLE_AOI_RADIUS, "Role", selfEntity.position ):
			self.questStatus( selfEntity, role )
		
		DEBUG_MSG( "Camp NPC refresh daily quest. className: %s" % selfEntity.className )
				
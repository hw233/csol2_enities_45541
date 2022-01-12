# -*- coding: gb18030 -*-

import csdefine
from MonsterResume import MonsterResume
from QuestBoxResume import QuestBoxResume

class CityWarBaseResume( MonsterResume, QuestBoxResume ):
	"""
	帮会夺城战决赛据点，根据配置的不同据点有不同的表现形式
	资源点类似任务箱子的表现
	其余的据点则是怪物的表现
	"""
	def __init__( self ) :
		MonsterResume.__init__( self )
		QuestBoxResume.__init__( self )

	def doMsg_( self, entity, window ):
		"""
		"""
		if entity.hasFlag( csdefine.ENTITY_FLAG_QUEST_BOX ):
			return QuestBoxResume.doMsg_( self, entity, window )
		else:
			return MonsterResume.doMsg_( self, entity, window )

instance = CityWarBaseResume()
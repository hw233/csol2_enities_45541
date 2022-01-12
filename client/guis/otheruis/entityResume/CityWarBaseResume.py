# -*- coding: gb18030 -*-

import csdefine
from MonsterResume import MonsterResume
from QuestBoxResume import QuestBoxResume

class CityWarBaseResume( MonsterResume, QuestBoxResume ):
	"""
	�����ս�����ݵ㣬�������õĲ�ͬ�ݵ��в�ͬ�ı�����ʽ
	��Դ�������������ӵı���
	����ľݵ����ǹ���ı���
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
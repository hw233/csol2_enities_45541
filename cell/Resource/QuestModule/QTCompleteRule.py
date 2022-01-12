# -*- coding: gb18030 -*-

import csdefine
from bwdebug import *


# ������ɹ���ʵ��
# ��ͬ�������ָ����ͬ����ɹ���
# CSOL-1803 add by cwl

def createRule( type ):
	try:
		return quest_complete_rule_maps[ type ]()
	except KeyError:
		ERROR_MSG( "can't create complete rule instance by %s type." % type )
		return None
	
#-------------------------------------------
# QTCompleteRuleDefault
#-------------------------------------------
class QTCompleteRuleDefault:
	"""
	ȫ������Ŀ����ɲ����������
	"""
	def __init__( self ):
		pass
	
	def checkComplete( self, player, questID ):
		if player.questTaskIsCompleted( questID ):
			return True
		else:
			return False

#-------------------------------------------
# QTCompleteRulePartTaskCom
#-------------------------------------------
class QTCompleteRulePartTaskCom:
	"""
	ֻҪ���һ������Ŀ������������
	"""
	def __init__( self ):
		pass
		
	def checkComplete( self, player, questID ):
		tasks = player.getQuestTasks( questID ).getTasks()
		for task in tasks.itervalues() :
			if task.isCompleted( player ) :
				return True
		return False

quest_complete_rule_maps = {}
quest_complete_rule_maps[ csdefine.QUEST_COMPLETE_RULE_DEFAULT ] = QTCompleteRuleDefault
quest_complete_rule_maps[ csdefine.QUEST_COMPLETE_RULE_PART_TASK_COM ] = QTCompleteRulePartTaskCom
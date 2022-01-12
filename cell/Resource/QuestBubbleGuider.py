# -*- coding: gb18030 -*-
#
# $Id: QuestBubbleGuider.py

"""
任务NPC头顶冒泡指示
"""
import BigWorld
import Language
import csconst
from bwdebug import *
import Function
import time
from config.QuestBubbleGuide import Datas as guideDatas

class QuestBubbleGuider:
	# 任务npc头顶冒泡
	_instance = None
	def __init__( self ):
		assert QuestBubbleGuider._instance is None,"instance already exist in"
		self._datas = {}
		self.__initCnfData()

	@classmethod
	def instance( self ):
		"""
		"""
		if self._instance is None:
			self._instance = QuestBubbleGuider()
		return self._instance

	def __getitem__( self, key ):
		"""
		"""
		if self._datas.has_key( key ):
			return self._datas[key]
		else:
			return None
	
	def __initCnfData( self ):
		"""
		初始化数据
		"""
		for data in guideDatas:
			questID = int( data["questID"] )
			targetData = data["targetIndex"]
			npcData = data["npcIDs"]
			isComShow = data["isCompleteShow"]				#True为完成时显示，否则未完成时显示
			targets = npcIDs=[]
			if len( targetData ):
				contents = {}
				targets = [int(target) for target in targetData.split("|")]
				for index, target in enumerate( targets ):
					if len( npcData ):
						npcIDs = npcData.split("|")[index].split(";")
					contents[target] = ( npcIDs, isComShow )
				self._datas[questID] = contents
	
	def getQuestTaskByCls( self, className, questID ):
		"""
		通过任务id和npc的className获得目标状态
		"""
		if questID in self._datas:
			for tskIndex, targetData in self._datas[questID].items():
				npcCls = targetData[0]
				isComShow = targetData[1]
				if className in npcCls:
					return ( tskIndex, isComShow )
		return None
	
	def getDatas( self ):
		return self._datas
	
def instance():
	return QuestBubbleGuider.instance()
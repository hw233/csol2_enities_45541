# -*- coding: gb18030 -*-
#
# $Id: QuestBubbleGuider.py

"""
����NPCͷ��ð��ָʾ
"""
import BigWorld
import Language
import csconst
from bwdebug import *
import Function
import time
from config.QuestBubbleGuide import Datas as guideDatas

class QuestBubbleGuider:
	# ����npcͷ��ð��
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
		��ʼ������
		"""
		for data in guideDatas:
			questID = int( data["questID"] )
			targetData = data["targetIndex"]
			npcData = data["npcIDs"]
			isComShow = data["isCompleteShow"]				#TrueΪ���ʱ��ʾ������δ���ʱ��ʾ
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
		ͨ������id��npc��className���Ŀ��״̬
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
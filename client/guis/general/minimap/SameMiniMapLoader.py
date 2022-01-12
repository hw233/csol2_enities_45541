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
from config.client.SpaceSameMiniMap import Datas as mapDatas

class SameMiniMapLoader:
	# ��ͬ��ͼ��ͬС��ͼ��Դ·��
	_instance = None
	def __init__( self ):
		assert SameMiniMapLoader._instance is None,"instance already exist in"
		self._datas = {}
		self.__initCnfData()

	@classmethod
	def instance( self ):
		"""
		"""
		if self._instance is None:
			self._instance = SameMiniMapLoader()
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
		for data in mapDatas:
			spaceLabel = data["sapceLabel"]
			mapPath = data["mapPath"]
			if not self._datas.has_key( spaceLabel ):
				self._datas[spaceLabel] = mapPath

	def getDatas( self ):
		return self._datas
	
	def isHasSameMap( self, spaceLabel ):
		"""
		�Ƿ��ڸ�������
		"""
		return spaceLabel in self._datas
	
	def getMapPath( self, spaceLabel ):
		if self.isHasSameMap( spaceLabel ):
			return self._datas[spaceLabel]
	
def instance():
	return SameMiniMapLoader.instance()
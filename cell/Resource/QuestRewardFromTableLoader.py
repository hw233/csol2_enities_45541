# -*- coding: gb18030 -*-

import Language
from bwdebug import *

class QuestRewardFromTableLoader:
	"""
	����������������Ϊ�������
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert QuestRewardFromTableLoader._instance is None
		self._datas = {}
		QuestRewardFromTableLoader._instance = self

	def load( self, configPath ):
		"""
		�������������
		"""
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s false." % configPath
		
		for node in section.values():
			questID = node.readString( "questID" )
			level = node.readInt( "level" )
			exp = node.readInt( "exp" )
			money = node.readInt( "money" )
			potential = node.readInt( "potential" )
			items = node.readString( "items" )		# ��Ʒ1ID:����1;��Ʒ2ID:����2......
			
			if questID not in self._datas:
				self._datas[questID] = {}
			if level not in self._datas[questID]:
				self._datas[questID][level] = {}
			if 'exp' not in self._datas[questID][level]:
				self._datas[questID][level]['exp'] = exp
			if 'money' not in self._datas[questID][level]:
				self._datas[questID][level]['money'] = money
			if 'potential' not in self._datas[questID][level]:
				self._datas[questID][level]['potential'] = potential
			
			# ��ȡ�����Ʒ��������	
			tempSum = 0
			itemsDict = {}
			for e in items.split( ";" ):
				d = e.split(":")
				if len(d) < 2:
					continue
				try:
					tempSum += int( d[1] )
				except KeyError:
					ERROR_MSG( "QuestRewardFromTableLoader.xml���ô���" )
				
				itemsDict[tempSum] = int( d[0] )
				
			if 'items' not in self._datas[questID][level]:
				self._datas[questID][level]['items'] = itemsDict

		# �������
		Language.purgeConfig( configPath )

	def get( self, questID ):
		"""
		����������,��ȡ������Ϣ

		@param questID: NPC���
		@return: { level : { 'exp' : exp, 'money' : money } }
		"""
		try:
			return self._datas[questID]
		except KeyError:
			DEBUG_MSG( "questID %s has no reward from table." % ( questID ) )
			return {}


	@staticmethod
	def instance():
		"""
		"""
		if QuestRewardFromTableLoader._instance is None:
			QuestRewardFromTableLoader._instance = QuestRewardFromTableLoader()
		return QuestRewardFromTableLoader._instance

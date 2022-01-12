# -*- coding: gb18030 -*-

# $Id: SkillTrainerLoader.py,v 1.1 2008-01-31 07:30:27 yangkai Exp $

import Language
from bwdebug import *

class SkillTrainerLoader:
	"""
	����ѵ��ʦ���ڵļ��ܼ���
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert SkillTrainerLoader._instance is None
		self._datas = {}
		self._skillIDs = set([])
		SkillTrainerLoader._instance = self

	def load( self, configPath ):
		"""
		"""
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s false." % configPath
		for node in section.values():
			npcID = node.readString( "npcID" )
			skillID = node.readInt64( "skillID" )
			self._skillIDs.add( skillID )
			if self._datas.has_key( npcID ):
				self._datas[ npcID ].add( skillID )
			else:
				self._datas[ npcID ] = set( [skillID] )
		# �������
		Language.purgeConfig( configPath )

	def get( self, npcID ):
		"""
		����npc���ȡ�ö�Ӧ�ļ���ID��
		"""
		try:
			return list( self._datas[npcID] )
		except KeyError:
			DEBUG_MSG( "npc %s has not config" % npcID)
			return  []
	
	def has( self, skillID ):
		"""
		�Ƿ���ѧϰ�����б�
		"""
		return skillID in self._skillIDs

	@staticmethod
	def instance():
		"""
		"""
		if SkillTrainerLoader._instance is None:
			SkillTrainerLoader._instance = SkillTrainerLoader()
		return SkillTrainerLoader._instance


#
# $Log: not supported by cvs2svn $
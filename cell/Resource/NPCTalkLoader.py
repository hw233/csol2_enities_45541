# -*- coding: gb18030 -*-

# $Id: NPCTalkLoader.py,v 1.1 2008-01-15 06:05:46 phw Exp $

import Language
from bwdebug import *
from Resource.DialogManager import DialogManager

class NPCTalkLoader:
	"""
	NPC�Ի����ݼ�����
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert NPCTalkLoader._instance is None
		# key == npcID
		# value == DialogManager()
		self._datas = {}
		NPCTalkLoader._instance = self

	def load( self, configPath ):
		"""
		���ؾ������ñ�
		"""
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s false." % configPath
		for node in section.values():
			self._datas[node.readString( "npcID" )] = DialogManager ( node["talks"] )
		# �������
		Language.purgeConfig( configPath )

	def get( self, npcID ):
		"""
		����npcIDȡ�öԻ��ű�
		
		@return: instance of DialogManager
		"""
		try:
			return self._datas[npcID]
		except KeyError:
			#WARNING_MSG( "npcID %s has not in table." % npcID )	����Ҳ����NPC��������̫�࣬����ʾ����Ҳ����
			return None

	@staticmethod
	def instance():
		"""
		"""
		if NPCTalkLoader._instance is None:
			NPCTalkLoader._instance = NPCTalkLoader()
		return NPCTalkLoader._instance


#
# $Log: not supported by cvs2svn $
#
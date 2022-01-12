# -*- coding: gb18030 -*-
"""
����MiniMonster�ļ�������
"""

from bwdebug import *
import Language

class MiniMonsterSkillLoader:
	"""
	�����͹��＼�����ü���
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert MiniMonsterSkillLoader._instance is None
		self.miniMonsterSkill = {} 	# ������＼�����ñ�
		self.load( "config/server/gameObject/MiniMonsterSkill.xml" )
		MiniMonsterSkillLoader._instance = self

	@staticmethod
	def instance():
		"""
		"""
		if MiniMonsterSkillLoader._instance is None:
			MiniMonsterSkillLoader._instance = MiniMonsterSkillLoader()
		return MiniMonsterSkillLoader._instance

	def load( self, configFile ):
		"""
		��ȡ������＼�����ñ�
		"""
		if len( configFile ) <= 0:
			return
		sect = Language.openConfigSection( configFile )
		assert sect is not None, "Open %s false." % configFile
		for node in sect.values():
			className = node["className"].asString
			if not self.miniMonsterSkill.has_key( className ):
				self.miniMonsterSkill[className] = []
			self.miniMonsterSkill[ className ] = node["skillID"].asInt

		# ��ȡ�����رմ򿪵��ļ�
		Language.purgeConfig( configFile )

	def getSkillIDByClassName( self, className ):
		"""
		����className���skillID
		"""
		skillID = 1
		try:
			skillID = self.miniMonsterSkill[className ]
		except:
			ERROR_MSG( "ClassName %s has not in config MiniMonsterSkill.xml " % className )
		return skillID

g_MiniMonsterSkill = MiniMonsterSkillLoader.instance()
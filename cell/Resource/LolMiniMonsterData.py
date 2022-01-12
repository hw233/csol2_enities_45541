# -*- coding: gb18030 -*-
"""
����MiniMonster_Lol��Ѳ�߼��жԹ�������
"""

from bwdebug import *
import Language

class LolMiniMonsterData:
	"""
	Ӣ�����˸���С������
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert LolMiniMonsterData._instance is None
		self.lolMiniMonsterData = {} 	# ������＼�����ñ�
		self.load( "config/server/LolMiniMonsterData.xml" )
		LolMiniMonsterData._instance = self

	@staticmethod
	def instance():
		"""
		"""
		if LolMiniMonsterData._instance is None:
			LolMiniMonsterData._instance = LolMiniMonsterData()
		return LolMiniMonsterData._instance

	def load( self, configFile ):
		"""
		Ӣ�����˸����������ݼ���
		"""
		if len( configFile ) <= 0:
			return
		sect = Language.openConfigSection( configFile )
		assert sect is not None, "Open %s false." % configFile
		for node in sect.values():
			className = node["className"].asString
			if not self.lolMiniMonsterData.has_key( className ):
				self.lolMiniMonsterData[className] = {}
			self.lolMiniMonsterData[ className ]["patrolList"]= node["patrolList"].asString
			self.lolMiniMonsterData[ className ]["enemyIDs"] = node["enemyIDs"].asString

		# ��ȡ�����رմ򿪵��ļ�
		Language.purgeConfig( configFile )

	def getLolMiniMonsterData( self, className ):
		"""
		����className���skillID
		"""
		data = {}
		try:
			data = self.lolMiniMonsterData[className ]
		except:
			ERROR_MSG( "ClassName %s has not in config LolMiniMonsterData.xml " % className )
		return data

g_MiniMonsterSkill = LolMiniMonsterData.instance()
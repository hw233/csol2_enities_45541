# -*- coding: gb18030 -*-

import Language
from bwdebug import *
from config.server import NPCExcData

class NPCExcDataLoader:
	"""
	NPC���������ñ����
	DPS��DPS�����������ٶȡ��������롢���������������������������
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert NPCExcDataLoader._instance is None
		# key == ��Ӧ�Ĺ���ְҵ
		# value == �ڸ�ְҵ�µ������ֵ�
		#		key == ��Ӧ�Ĺ���ȼ�
		# 		value == �ڸõȼ��µ�����ֵ
		# like as { սʿ : { �ȼ� : { DPS : xxx, DPS���� : xxx, �����ٶ� : xxx, �������� : xxx, �������� : xxx, ������� : xxx, �������� : xxx }, ... }, ...}
		self._datas = NPCExcData.Datas
		NPCExcDataLoader._instance = self

	def get( self, raceclass, level  ):
		"""
		������������
		"""
		try:
			# ��Ҫִ��(raceclass >> 4) & 0xf��ԭ������Ϊ��ǰentity.getClass()���ص���һ��������4λ��ֵ���꿴csdefine.CLASS_*
			return self._datas[(raceclass >> 4) & 0xf][level]
		except:
			if level != 0:
				ERROR_MSG( "( Raceclass %i, Level %i ) can not find in table NPCExcDataConfig" % ( raceclass, level ) )
			return {
					"data_dps" : 5.0,
					"data_dpsWave": -0.28,
					"data_speed": 0.0,
					"data_range": 0.0,
					"data_magicDamage": 10,
					"data_physicsArmor": 100,
					"data_magicArmor": 100,
					}

	@staticmethod
	def instance():
		"""
		"""
		if NPCExcDataLoader._instance is None:
			NPCExcDataLoader._instance = NPCExcDataLoader()
		return NPCExcDataLoader._instance
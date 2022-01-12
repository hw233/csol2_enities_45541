# -*- coding: gb18030 -*-

# $Id: NPCBaseAttrLoader.py,v 1.8 2008-09-04 07:45:21 kebiao Exp $

import Language
from bwdebug import *
import csconst
from config.server import NPCBaseAttr

class NPCBaseAttrLoader:
	"""
	������������������ü�����
	���ʡ�����������������
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert NPCBaseAttrLoader._instance is None
		# key == ��Ӧ�Ĺ���ְҵ
		# value == �ڸ�ְҵ�µ������ֵ�
		#		key == ��Ӧ�Ĺ���ȼ�
		# 		value == �ڸõȼ��µ����������ֵ�
		# like as { ��ʦ : { �ȼ� : { ���� : xxx, ���� : xxx, ���� : xxx, ���� : xxx }, ... }, ...}
		self._datas = NPCBaseAttr.Datas
		NPCBaseAttrLoader._instance = self

	def get( self, raceclass, level ):
		"""
		���ݵ�ȡ�ö�Ӧ�ľ���ֵ
		@param type: ����������
		@param raceclass: ����ְҵ��ţ���սʿ(0x00)��
		@return: { ���� : xxx, ���� : xxx, ���� : xxx, ���� : xxx }
		"""
		try:
			# ��Ҫִ��(raceclass >> 4) & 0xf��ԭ������Ϊ��ǰentity.getClass()���ص���һ��������4λ��ֵ���꿴csdefine.CLASS_*
			return self._datas[(raceclass >> 4) & 0xf][level]
		except KeyError:
			if level != 0:
				ERROR_MSG( "level %i or class %i has not in table." % ( level, raceclass ) )
			return {	"strength_base" : 10000.0,
						"dexterity_base" : 10000.0,
						"intellect_base" : 10000.0,
						"corporeity_base" : 10000.0, }
			

	@staticmethod
	def instance():
		"""
		"""
		if NPCBaseAttrLoader._instance is None:
			NPCBaseAttrLoader._instance = NPCBaseAttrLoader()
		return NPCBaseAttrLoader._instance

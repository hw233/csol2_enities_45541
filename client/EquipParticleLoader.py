# -*- coding: gb18030 -*-

from bwdebug import *
import Language
import csdefine
import Math
from config.client import IntensifyEffect
from config.client import StuddedEffect
from config.client import WeaponGlow


class EquipParticleLoader:
	"""
	װ��ǿ������ǶЧ������
	@ivar _data: ȫ�������ֵ�; key is id, value is dict like as {key��{...}}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert EquipParticleLoader._instance is None, "instance already exist in"
		self._datas = IntensifyEffect.Datas
		self._sdatas = StuddedEffect.Datas
		self._wdatas = WeaponGlow.Datas

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = EquipParticleLoader()
		return self._instance

	def getFsHp( self, intensify ):
		"""
		����ǿ���ȼ���ȡ����Ч���󶨵�
		return string
		"""
		try:
			return self._datas[intensify]["fs_hp"]
		except:
			return ""

	def getFsGx( self, intensify, profession, gender ):
		"""
		����ְҵ���Ա��ǿ���ȼ���ȡ��������
		return list of string
		"""
		try:
			return self._datas[intensify]["fs_gx"][profession | gender]
		except:
			return []

	def getSsHp( self, intensify ):
		"""
		����ǿ���ȼ���ȡ����Ч���󶨵�
		return string
		"""
		try:
			return self._datas[intensify]["ss_hp"]
		except:
			return ""

	def getSsGx( self, intensify, profession ):
		"""
		����ְҵ��ȡ����Ч������
		return list of string
		"""
		try:
			return self._datas[intensify]["ss_gx"][profession]
		except:
			return []

	def getPxHp( self, intensify ):
		"""
		����ǿ���ȼ���ȡ�����������Ч���󶨵�
		return string
		"""
		try:
			return self._datas[intensify]["px_hp"]
		except:
			return ""

	def getPxGx( self, intensify ):
		"""
		����ְҵ��ȡ�����������Ч������
		return list of string
		"""
		try:
			return self._datas[intensify]["px_gx"]
		except:
			return []

	def getLongHp( self, intensify ):
		"""
		����ǿ���ȼ���ȡ������ת�⻷Ч���󶨵�
		return string
		"""
		try:
			return self._datas[intensify]["long_hp"]
		except:
			return ""

	def getLongGx( self, intensify ):
		"""
		����ְҵ��ȡ������ת�⻷Ч������
		return list of string
		"""
		try:
			return self._datas[intensify]["long_gx"]
		except:
			return []

	def getDianHp( self, intensify ):
		"""
		����ǿ���ȼ���ȡ������ת�⻷Ч���󶨵�
		return string
		"""
		try:
			return self._datas[intensify]["dian_hp"]
		except:
			return ""

	def getDianGx( self, intensify ):
		"""
		����ְҵ��ȡ������ת�⻷Ч������
		return list of string
		"""
		try:
			return self._datas[intensify]["dian_gx"]
		except:
			return []

	def getXqHp( self, studdedAmount ):
		"""
		������Ƕ������ȡ��Ƕ�󶨵�
		"""
		try:
			return self._sdatas[studdedAmount]["hp"]
		except:
			return []

	def getXqGx( self, studdedAmount ):
		"""
		������Ƕ������ȡ��Ƕ����
		return list of string
		"""
		try:
			return self._sdatas[studdedAmount]["particle"]
		except:
			return []

	def getWTexture( self, weaponKey ):
		"""
		���ݹؼ��ֻ�ȡ������ͼ·��
		return string
		"""
		try:
			return self._wdatas[weaponKey]["texture"]
		except:
			WARNING_MSG( "Can't find textureConfig by (%s)" % weaponKey )
			return ""

	def getWType( self, weaponKey ):
		"""
		���ݹؼ��ֻ�ȡ������Ⱦ����
		return Int
		"""
		try:
			return self._wdatas[weaponKey]["type"]
		except:
			WARNING_MSG( "Can't find typeConfig by (%s)" % weaponKey )
			return 0

	def getWScale( self, weaponKey, intensifyLevel ):
		"""
		���ݹؼ��ֺ�ǿ���ȼ���ȡ��������ֵ
		return Vector4
		"""
		key = ""
		if intensifyLevel in [4,5]:
			key = "scale1"
		elif intensifyLevel in [6,7]:
			key = "scale2"
		elif intensifyLevel in [8,9]:
			key = "scale3"

		try:
			return self._wdatas[weaponKey][key]
		except:
			WARNING_MSG( "Can't find scaleConfig by (%s)" % weaponKey )
			return Math.Vector4()

	def getWColour( self, weaponKey ):
		"""
		���ݹؼ��ֻ�ȡ������ɫVector4
		return Vector4
		"""
		try:
			return self._wdatas[weaponKey]["colour"]
		except:
			WARNING_MSG( "Can't find colourConfig by (%s)" % weaponKey )
			return Math.Vector4()

	def getWOffset( self, weaponKey ):
		"""
		���ݹؼ��ֻ�ȡ������ͼƫ����Vector3
		return Vector3
		"""
		try:
			return self._wdatas[weaponKey]["offset"]
		except:
			WARNING_MSG( "Can't find offsetConfig by (%s)" % weaponKey )
			return Math.Vector3()

	def reset( self ):
		"""
		���¼�������
		"""
		reload( IntensifyEffect )
		reload( StuddedEffect )
		reload( WeaponGlow )
		self._datas = IntensifyEffect.Datas
		self._sdatas = StuddedEffect.Datas
		self._wdatas = WeaponGlow.Datas
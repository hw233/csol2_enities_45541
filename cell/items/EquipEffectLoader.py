# -*- coding: gb18030 -*-

#$Id: EquipEffectLoader.py,v 1.12 2008-08-09 09:31:24 wangshufeng Exp $

from bwdebug import *
import Language
from SmartImport import smartImport
import Function
import random
import copy
from config.item.EquipEffects import serverDatas as g_serverDatas
import ItemTypeEnum


# ----------------------------------------------------------------------------------------------------
# װ�����Լ���
# ----------------------------------------------------------------------------------------------------

class EquipEffectLoader:
	"""
	װ�����Լ���
	@ivar _data: ȫ�������ֵ�; key is id, value is dict like as {key��[...], ...}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert EquipEffectLoader._instance is None, "instance already exist in"
		self._datas = g_serverDatas
		for key, value in self._datas.iteritems():
			self._datas[key]["dynClass"] = smartImport( value["dynClass"] )

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = EquipEffectLoader()
		return self._instance

	def getEffect( self, effectID ):
		"""
		����Ч��ID��ȡЧ����Ӧ�ű���
		"""
		try:
			return self._datas[effectID]["dynClass"]
		except:
			ERROR_MSG( "Can't find equipEffect config by %s" % effectID )
			return None

	def getEffectIDsByQuality( self, quality ):
		"""
		ͨ��װ��Ʒ��ȷ���ɳ��ֵ�Ч��ID�б�
		"""
		EffectIDs = set([])
		for key, value in self._datas.iteritems():
			if value["needEquipQuality"] <= quality:
				EffectIDs.add( key )
		return list( EffectIDs )

	def getEffectIDsByLevel( self, level, canSystemCreate = False ):
		"""
		ͨ��װ���ȼ�ȷ���ɳ��ֵ�Ч��ID�б�

		canSystemCreateΪFalseʱ���˵�ϵͳ������ԣ����򷵻������������id�б�
		"""
		EffectIDs = set([])
		for key, value in self._datas.iteritems():
			if value["needEquipLevel"] <= level:
				if not canSystemCreate and value[ "canSystemCreate" ] == 0:
					continue
				EffectIDs.add( key )
		return list( EffectIDs )

	def getLevel( self, effectID ):
		"""
		����Ч��ID��ȡ��Ч�������ֵ�װ����͵ȼ�
		"""
		try:
			return self._datas[effectID]["needEquipLevel"]
		except:
			return 0

	def getReqClass( self, effectID ):
		"""
		����Ч��ID��ȡ��Ч�������ֵ�װ��ְҵ����
		"""
		try:
			return self._datas[effectID]["needEquipClass"]
		except:
			return 0

	def getPerGene( self, effectID ):
		"""
		����Ч��ID��ȡÿ��λ��Ч�������ֵ������
		"""
		try:
			gene =  self._datas[effectID]["needPerProceGene"]
		except:
			gene = 0
		return gene

	def getType( self, effectID ):
		"""
		����Ч��ID��ȡ��������
		"""
		data = self._datas.get( effectID, None )
		if data is None: return ItemTypeEnum.EQUIP_EFFECT_TYPE_ADD
		return data.get( "type", ItemTypeEnum.EQUIP_EFFECT_TYPE_ADD )

	def canSystemCreate( self, effectID ):
		"""
		�жϸ��������Ƿ�����ϵͳ�������
		@param effectID: Ч�����
		@type  effectID: Int
		@return 1 or 0
		"""
		try:
			return self._datas[effectID]["canSystemCreate"]
		except KeyError:
			ERROR_MSG( "Can't find CanSystemCreate config by %s" % effectID )
			return 0

	def getNoCoexist( self, effectID ):
		"""
		��ȡЧ��ID�����
		"""
		try:
			return list( self._datas[effectID]["noCoexist"] )
		except KeyError:
			ERROR_MSG( "Can't find noCoexist config by %s" % effectID )
			return []

	def canSmelt( self, effectID ):
		"""
		�жϸ��������Ƿ���������
		@param effectID: Ч�����
		@type  effectID: Int
		@return 1 or 0
		"""
		try:
			return self._datas[effectID]["canSmelt"]
		except KeyError:
			ERROR_MSG( "Can't find canSmelt config by %s" % effectID )
			return 0
			
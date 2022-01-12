# -*- coding: gb18030 -*-

from bwdebug import *
import BigWorld
import Define
import Const
from Function import Functor
from gbref import rds
import csdefine
import csol
from config.client.SpaceEffectConfig import Datas as SpaceEffectDatas

# ------------------------------------------------------------------------------
# Class AreaEffectMgr:
# ����Ч��������
# ����ʵ�ָ��ֵ�ͼ����Ч��
# ------------------------------------------------------------------------------
class AreaEffectBase:
	"""
	����Ч��������
	"""
	@staticmethod
	def start( entity ):
		"""
		Ч������
		"""
		pass

	@staticmethod
	def stop( entity ):
		"""
		Ч��ֹͣ
		"""
		pass

	@staticmethod
	def enter( entity ):
		"""
		�ض���entityЧ������(����Ч����Ч)
		"""
		pass

class AreaEffectBubbles( AreaEffectBase ):
	"""
	����ˮ��Ч��
	"""
	@staticmethod
	def start( player ):
		"""
		Ч������
		"""
		toggleTypes = [csdefine.ENTITY_TYPE_ROLE, csdefine.ENTITY_TYPE_PET, csdefine.ENTITY_TYPE_MONSTER]
		for entity in BigWorld.entities.values():
			if entity.getEntityType() not in toggleTypes : continue
			entity.attachBubblesEffect()

	@staticmethod
	def stop( player ):
		"""
		Ч��ֹͣ
		"""
		toggleTypes = [csdefine.ENTITY_TYPE_ROLE, csdefine.ENTITY_TYPE_PET, csdefine.ENTITY_TYPE_MONSTER]
		for entity in BigWorld.entities.values():
			if entity.getEntityType() not in toggleTypes : continue
			entity.detachBubblesEffect()

	@staticmethod
	def enter( entity ):
		"""
		�ض���entityЧ������(����Ч����Ч)
		"""
		entity.attachBubblesEffect()

class AreaEffectUnderWater( AreaEffectBase ):
	"""
	ˮŤ����ˮ�׿�ʴ������Ч��
	"""
	@staticmethod
	def start( entity ):
		"""
		Ч������
		"""
		csol.alwaysUnderWater( True )
		BigWorld.enableShimmer( True )

	@staticmethod
	def stop( entity ):
		"""
		Ч��ֹͣ
		"""
		csol.alwaysUnderWater( False )
		BigWorld.enableShimmer( False )

	@staticmethod
	def enter( entity ):
		"""
		�ض���entityЧ������(����Ч����Ч)
		"""
		pass

class AreaEffectMgr:
	__instance = None

	def __init__( self ):
		assert AreaEffectMgr.__instance is None
		self.spaceEffectDatas = {}
		self.AREA_EFFECT_MAPS = {	Define.MAP_AREA_EFFECT_SHUIPAO	:	AreaEffectBubbles,
									Define.MAP_AREA_EFFECT_UNWATER	:	AreaEffectUnderWater,
									}

	@classmethod
	def instance( SELF ):
		if SELF.__instance is None:
			SELF.__instance = AreaEffectMgr()
		return SELF.__instance

	def onAreaChange( self, entity, oldArea, newArea ):
		"""
		��ͼ�������֪ͨ
		"""
		if newArea is None: return

		# �Ƴ��ɵ�Ч��
		if oldArea:
			oldEffectFlag = oldArea.getEffectFlag()
			for flag in Define.MAP_AREA_EFFECTS_CHANGEAREA:
				if ( flag & oldEffectFlag ) == flag:
					effectClass = self.AREA_EFFECT_MAPS.get( flag )
					if effectClass is None: continue
					effectClass.stop( entity )


		# ����µ�Ч��
		newEffectFlag = newArea.getEffectFlag()
		for flag in Define.MAP_AREA_EFFECTS_CHANGEAREA:
			if ( flag & newEffectFlag ) == flag:
				effectClass = self.AREA_EFFECT_MAPS.get( flag )
				if effectClass is None: continue
				effectClass.start( entity )

	def onModelChange( self, entity ):
		"""
		entity ����ģ��֪ͨ
		"""
		player = BigWorld.player()
		if player is None: return

		currArea = player.getCurrArea()
		if currArea is None: return

		effectFlag = currArea.getEffectFlag()
		for flag in Define.MAP_AREA_EFFECTS_MODELCHANGE:
			if ( flag & effectFlag ) == flag:
				effectClass = self.AREA_EFFECT_MAPS.get( flag )
				if effectClass is None: continue
				effectClass.enter( entity )

	def onStopAreaEffect( self, entity ):
		"""
		ֹͣ����ˮЧ��
		"""	
		for flag in Define.MAP_AREA_EFFECTS_CHANGEAREA:
			effectClass = self.AREA_EFFECT_MAPS.get( flag )
			if effectClass is None: continue
			effectClass.stop( entity )

	def startSpaceEffect( self, entity ):
		"""
		����������Ч
		"""
		self.stopSpaceEffect()  # ֹͣ�ɵĹ�Ч

		# ��ʼ�µĹ�Ч
		for key, value in SpaceEffectDatas.items():
			resultList = []
			conditionIDList = key.split( ";" )
			for conditionID in conditionIDList:
				result = rds.spaceEffectMgr.check( entity, int( conditionID ) )
				resultList.append( result )
			if not False in resultList:
				rds.spaceEffectMgr.trigger( value )
				event = rds.spaceEffectMgr.getEvent()
				self.spaceEffectDatas[key] = event

	def stopSpaceEffect( self ):
		"""
		ֹͣ������Ч
		"""
		for event in self.spaceEffectDatas.values():
			event.cancel()
		self.spaceEffectDatas = {}
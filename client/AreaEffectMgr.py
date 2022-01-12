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
# 区域效果管理器
# 用于实现各种地图区域效果
# ------------------------------------------------------------------------------
class AreaEffectBase:
	"""
	区域效果抽象类
	"""
	@staticmethod
	def start( entity ):
		"""
		效果启动
		"""
		pass

	@staticmethod
	def stop( entity ):
		"""
		效果停止
		"""
		pass

	@staticmethod
	def enter( entity ):
		"""
		特定的entity效果启动(区域效果有效)
		"""
		pass

class AreaEffectBubbles( AreaEffectBase ):
	"""
	区域水泡效果
	"""
	@staticmethod
	def start( player ):
		"""
		效果启动
		"""
		toggleTypes = [csdefine.ENTITY_TYPE_ROLE, csdefine.ENTITY_TYPE_PET, csdefine.ENTITY_TYPE_MONSTER]
		for entity in BigWorld.entities.values():
			if entity.getEntityType() not in toggleTypes : continue
			entity.attachBubblesEffect()

	@staticmethod
	def stop( player ):
		"""
		效果停止
		"""
		toggleTypes = [csdefine.ENTITY_TYPE_ROLE, csdefine.ENTITY_TYPE_PET, csdefine.ENTITY_TYPE_MONSTER]
		for entity in BigWorld.entities.values():
			if entity.getEntityType() not in toggleTypes : continue
			entity.detachBubblesEffect()

	@staticmethod
	def enter( entity ):
		"""
		特定的entity效果启动(区域效果有效)
		"""
		entity.attachBubblesEffect()

class AreaEffectUnderWater( AreaEffectBase ):
	"""
	水扭曲、水底刻蚀纹理动画效果
	"""
	@staticmethod
	def start( entity ):
		"""
		效果启动
		"""
		csol.alwaysUnderWater( True )
		BigWorld.enableShimmer( True )

	@staticmethod
	def stop( entity ):
		"""
		效果停止
		"""
		csol.alwaysUnderWater( False )
		BigWorld.enableShimmer( False )

	@staticmethod
	def enter( entity ):
		"""
		特定的entity效果启动(区域效果有效)
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
		地图区域更改通知
		"""
		if newArea is None: return

		# 移除旧的效果
		if oldArea:
			oldEffectFlag = oldArea.getEffectFlag()
			for flag in Define.MAP_AREA_EFFECTS_CHANGEAREA:
				if ( flag & oldEffectFlag ) == flag:
					effectClass = self.AREA_EFFECT_MAPS.get( flag )
					if effectClass is None: continue
					effectClass.stop( entity )


		# 添加新的效果
		newEffectFlag = newArea.getEffectFlag()
		for flag in Define.MAP_AREA_EFFECTS_CHANGEAREA:
			if ( flag & newEffectFlag ) == flag:
				effectClass = self.AREA_EFFECT_MAPS.get( flag )
				if effectClass is None: continue
				effectClass.start( entity )

	def onModelChange( self, entity ):
		"""
		entity 更换模型通知
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
		停止各种水效果
		"""	
		for flag in Define.MAP_AREA_EFFECTS_CHANGEAREA:
			effectClass = self.AREA_EFFECT_MAPS.get( flag )
			if effectClass is None: continue
			effectClass.stop( entity )

	def startSpaceEffect( self, entity ):
		"""
		开启场景光效
		"""
		self.stopSpaceEffect()  # 停止旧的光效

		# 开始新的光效
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
		停止场景光效
		"""
		for event in self.spaceEffectDatas.values():
			event.cancel()
		self.spaceEffectDatas = {}
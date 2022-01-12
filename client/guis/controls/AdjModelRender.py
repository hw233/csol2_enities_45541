# -*- coding: gb18030 -*-
#
# $Id: ModelRender.py,v 1.6 2008-08-28 03:53:55 huangyongwei Exp $

"""
implement adjustable model render gui

2009/06/12: writen by huangyongwei
"""

import os
from AbstractTemplates import AbstractClass
from gbref import PyConfiger
from guis import *
from ModelRender import ModelRender

class AdjModelRender( AbstractClass, ModelRender ) :
	__abstract_methods = set()
	"""
	该类实现带配置、可调整的模型观察器的抽象基类
	"""
	def __init__( self, uiRender, cfgKey, config ) :
		"""
		@type				uiRender : GUI.Simple
		@param				uiRender : 模型放置 UI 版面
		@type				cfgKey   : alltype
		@param				cfgKey   : 位置配置键的默认值（每个观察器可能都不一样）
		@type				config	 : str
		@param				config	 : 模型位置配置文件
		"""
		ModelRender.__init__( self, uiRender )
		self.cfgName = os.path.split( config )[1]					# 配置文件名称（只有调整工具用）

		self.cfgKey_ = cfgKey										# 当前模型的位置标记（在配置中的键）
		self.configDatas_ = PyConfiger().read( config, {} )			# 读取配置

		self.__defCfgKey = cfgKey									# 默认配置键


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	@staticmethod
	def creatModelInfo_( modelNumber, name, pos, pitch, yaw ) :
		"""
		创建一个调整工具可识别的模型位置信息: ModelInfo
		"""
		return ModelInfo( modelNumber, name, pos, pitch, yaw )

	# -------------------------------------------------
	def onModelChanged_( self, oldModel ) :
		viewInfo = self.getViewInfo( self.cfgKey_ )
		if viewInfo :
			self.modelPos = viewInfo["position"]
			self.pitch = viewInfo["pitch"]
			if viewInfo.has_key( "yaw" ):
				self.yaw = viewInfo["yaw"]
		ModelRender.onModelChanged_( self, oldModel )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def clearModel( self ) :
		"""
		清除当前显示的模型
		"""
		self.cfgKey_ = self.__defCfgKey								# 回复为默认键
		self.setModel( None )

	# -------------------------------------------------
	def getConfigKey( self ) :
		"""
		获取当前的模型标记
		"""
		return self.cfgKey_

	# -------------------------------------------------
	def getViewInfo( self, cfgKey ) :
		"""
		获取位置信息
		"""
		return self.configDatas_.get( cfgKey, None )

	def saveViewInfo( self, modelInfo ) :
		"""
		保存指定的模型位置信息
		@type				modelInfo : ModelInfo
		@param				modelInfo : 要保存的位置信息
		"""
		viewInfo = self.configDatas_.get( modelInfo.mark, None )
		if viewInfo is None :
			viewInfo = {}
			self.configDatas_[modelInfo.mark] = viewInfo
		viewInfo['position'] = modelInfo.position
		viewInfo['pitch'] = modelInfo.pitch
		viewInfo['yaw'] = self.yaw

	# -------------------------------------------------
	def resetModel( self, mark = None, bgCreate = True ) :
		"""
		重新设置观察模型
		注意：子类必须实现该方法
		"""
		pass

	def getViewInfos( self ) :
		"""
		获取所有可调整模型的位置信息
		@rtype				modelInfo : ModelInfo
		@param				modelInfo : 模型位置信息
		注意：子类必须实现该方法
		"""
		return []


	# ----------------------------------------------------------------
	# set abstract class
	# ----------------------------------------------------------------
	__abstract_methods.add( resetModel )
	__abstract_methods.add( getViewInfos )


# --------------------------------------------------------------------
# implement model info for adjuster
# --------------------------------------------------------------------
class ModelInfo( object ) :
	def __init__( self, mark, name, pos, pitch, yaw ) :
		self.__mark = mark
		self.__name = name
		self.position = pos
		self.pitch = pitch
		self.yaw = yaw
	mark = property( lambda self : self.__mark )							# str: 模型标记 mark 为只读
	name = property( lambda self : self.__name )							# str: 模型名称为只读

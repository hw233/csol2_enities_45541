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
	����ʵ�ִ����á��ɵ�����ģ�͹۲����ĳ������
	"""
	def __init__( self, uiRender, cfgKey, config ) :
		"""
		@type				uiRender : GUI.Simple
		@param				uiRender : ģ�ͷ��� UI ����
		@type				cfgKey   : alltype
		@param				cfgKey   : λ�����ü���Ĭ��ֵ��ÿ���۲������ܶ���һ����
		@type				config	 : str
		@param				config	 : ģ��λ�������ļ�
		"""
		ModelRender.__init__( self, uiRender )
		self.cfgName = os.path.split( config )[1]					# �����ļ����ƣ�ֻ�е��������ã�

		self.cfgKey_ = cfgKey										# ��ǰģ�͵�λ�ñ�ǣ��������еļ���
		self.configDatas_ = PyConfiger().read( config, {} )			# ��ȡ����

		self.__defCfgKey = cfgKey									# Ĭ�����ü�


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	@staticmethod
	def creatModelInfo_( modelNumber, name, pos, pitch, yaw ) :
		"""
		����һ���������߿�ʶ���ģ��λ����Ϣ: ModelInfo
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
		�����ǰ��ʾ��ģ��
		"""
		self.cfgKey_ = self.__defCfgKey								# �ظ�ΪĬ�ϼ�
		self.setModel( None )

	# -------------------------------------------------
	def getConfigKey( self ) :
		"""
		��ȡ��ǰ��ģ�ͱ��
		"""
		return self.cfgKey_

	# -------------------------------------------------
	def getViewInfo( self, cfgKey ) :
		"""
		��ȡλ����Ϣ
		"""
		return self.configDatas_.get( cfgKey, None )

	def saveViewInfo( self, modelInfo ) :
		"""
		����ָ����ģ��λ����Ϣ
		@type				modelInfo : ModelInfo
		@param				modelInfo : Ҫ�����λ����Ϣ
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
		�������ù۲�ģ��
		ע�⣺�������ʵ�ָ÷���
		"""
		pass

	def getViewInfos( self ) :
		"""
		��ȡ���пɵ���ģ�͵�λ����Ϣ
		@rtype				modelInfo : ModelInfo
		@param				modelInfo : ģ��λ����Ϣ
		ע�⣺�������ʵ�ָ÷���
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
	mark = property( lambda self : self.__mark )							# str: ģ�ͱ�� mark Ϊֻ��
	name = property( lambda self : self.__name )							# str: ģ������Ϊֻ��

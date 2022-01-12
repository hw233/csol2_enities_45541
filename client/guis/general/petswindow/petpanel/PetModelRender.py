# -*- coding: gb18030 -*-
#
# $Id: PetModelRender.py,v 1.5 2008-08-28 03:56:26 huangyongwei Exp $

"""
implement model's ui render

2008.07.31 -- by huangyongwei
"""

from gbref import rds
from guis import *
from config.client import NPCModelConfig
from guis.controls.AdjModelRender import AdjModelRender

class PetModelRender( AdjModelRender ) :
	__cc_config = "config/client/uimodel_configs/pet.py"

	def __init__( self, mirror ) :
		AdjModelRender.__init__( self, mirror, 0, self.__cc_config )
		self.bgTexture = "guis/general/petswindow/renderbg.tga"		# ������ͼ


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onModelCreated( self, modelNumber, model ) :
		"""
		����ģ�ͻص�
		"""
		if self.cfgKey_ != modelNumber :
			return
		if model is None :
			self.cfgKey_ = 0
			# "����ģ��ʧ�ܣ�"
			showMessage( 0x04e1, "", MB_OK, pyOwner = self )
		self.setModel( model )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resetModel( self, modelNumber, bgCreate = True ) :
		"""
		��������ģ��
		@type			modelNumber : INT32
		@param			modelNumber : ģ�� ID
		@type			bgCreate	: bool
		@param			bgCreate	: �Ƿ��ں�̨����ģ��
		@return					 	: None
		"""
		if self.cfgKey_ == modelNumber :
			return
		else:
			self.cfgKey_ = modelNumber
		if bgCreate :
			rds.npcModel.createDynamicModelBG( modelNumber, Functor( self.__onModelCreated, modelNumber ) )
		else :
			try :
				model = rds.npcModel.createDynamicModel( modelNumber )
			except :
				model = None
			self.__onModelCreated ( modelNumber, model )

	# -------------------------------------------------
	def getViewInfos( self ) :
		"""
		��ȡ����ģ����Ϣ
		"""
		keys = self.configDatas_.keys()
		infos = []
		npcModelCfgData = NPCModelConfig.Datas
		for modelNumber, val in npcModelCfgData.iteritems( ):
			if not val["forPet"] : continue
			name = val.get( "name", "" )
			if name == "" :
				name = modelNumber
			else :
				name = "%s(%s)" % ( modelNumber, name )
			pos = Math.Vector3( 0, 0, 0 )
			pitch = 0.0
			yaw = 0.0
			viewInfo = self.getViewInfo( modelNumber )
			if viewInfo :
				pos = viewInfo["position"]
				pitch = viewInfo["pitch"]
				if viewInfo.has_key( "yaw" ):
					yaw = viewInfo["yaw"]
			modelInfo = self.creatModelInfo_( modelNumber, name, pos, pitch, yaw )
			if modelNumber == self.cfgKey_ :
				infos.insert( 0, modelInfo )
			else :
				infos.append( modelInfo )
			if modelNumber in keys :										# �Ƴ�ģ���Ѿ������ڵ�����
				keys.remove( modelNumber )
		assert infos[0].mark == self.cfgKey_, "current model number is not in model list!"
		infos[0].position = self.modelPos
		infos[0].pitch = self.pitch
		for key in keys :
			self.configDatas_.pop( key )
		return infos

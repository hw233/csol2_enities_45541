# -*- coding: gb18030 -*-
#
# $Id: PetModelRender.py,v 1.5 2008-08-28 03:56:26 huangyongwei Exp $

"""
implement model's ui render
"""

from NPCModelLoader import NPCModelLoader
from guis import *
from guis.controls.AdjModelRender import AdjModelRender
from TongBeastData import TongBeastData
tongBeastData = TongBeastData.instance()

class GodRender( AdjModelRender ) :
	__cc_config = "config/client/uimodel_configs/shenshou.py"

	def __init__( self, mirror ) :
		AdjModelRender.__init__( self, mirror, "", self.__cc_config )
		self.bgTexture = "guis/general/tongabout/shenshoubeckon/modelbg.dds"						# 背景贴图
#		self.mapping = util.getGuiMapping((512,512),93,419,87,445)
#		self.cfgKey_ = "" #模型id

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onModelCreated( self, modelNumber, model ) :
		"""
		创建模型回调
		"""
		if model is None :
			self.cfgKey_ = ""
			# "创建模型失败！"
			showMessage( 0x08e1, "", MB_OK, pyOwner = self )
		self.setModel( model )
		self.enableDrawModel()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resetModel( self, beaClassName, bgCreate = True ) :
		"""
		重新设置模型
		@type			modelNumber : INT32
		@param			modelNumber : 模型 ID
		@type			bgCreate	: bool
		@param			bgCreate	: 是否在后台创建模型
		@return					 	: None
		"""
		if self.cfgKey_ == beaClassName :
			return
		else:
			self.cfgKey_ = beaClassName
		beastData = tongBeastData.getDatas()
		modelNumber = beastData[beaClassName][1]["modelNums"][0]
		if bgCreate :
			rds.npcModel.createDynamicModelBG( modelNumber, Functor( self.__onModelCreated, modelNumber ) )
		else :
			try :
				model = rds.npcModel.createDynamicModel( modelNumber )
			except :
				model = None
#			if self.cfgKey_ != modelNumber :
#				return
			self.__onModelCreated ( modelNumber, model )

	# -------------------------------------------------
	def getViewInfos( self ) :
		"""
		获取所有模型信息
		"""
		beastData = tongBeastData.getDatas()
		beastName = beastData[self.cfgKey_][1]["uname"]
		pos = self.modelPos
		pitch = self.pitch
		yaw = self.yaw
		modelInfo = self.creatModelInfo_( self.cfgKey_, beastName, pos, pitch, yaw )
		return [modelInfo]											# 只调整当前职业



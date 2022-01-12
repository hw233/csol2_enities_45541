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
		self.bgTexture = "guis/general/tongabout/shenshoubeckon/modelbg.dds"						# ������ͼ
#		self.mapping = util.getGuiMapping((512,512),93,419,87,445)
#		self.cfgKey_ = "" #ģ��id

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onModelCreated( self, modelNumber, model ) :
		"""
		����ģ�ͻص�
		"""
		if model is None :
			self.cfgKey_ = ""
			# "����ģ��ʧ�ܣ�"
			showMessage( 0x08e1, "", MB_OK, pyOwner = self )
		self.setModel( model )
		self.enableDrawModel()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resetModel( self, beaClassName, bgCreate = True ) :
		"""
		��������ģ��
		@type			modelNumber : INT32
		@param			modelNumber : ģ�� ID
		@type			bgCreate	: bool
		@param			bgCreate	: �Ƿ��ں�̨����ģ��
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
		��ȡ����ģ����Ϣ
		"""
		beastData = tongBeastData.getDatas()
		beastName = beastData[self.cfgKey_][1]["uname"]
		pos = self.modelPos
		pitch = self.pitch
		yaw = self.yaw
		modelInfo = self.creatModelInfo_( self.cfgKey_, beastName, pos, pitch, yaw )
		return [modelInfo]											# ֻ������ǰְҵ



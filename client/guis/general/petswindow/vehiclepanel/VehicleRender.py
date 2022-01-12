# -*- coding: gb18030 -*-
#
# $Id: PetModelRender.py,v 1.5 2008-08-28 03:56:26 huangyongwei Exp $

"""
implement model's ui render

2008.07.31 -- by huangyongwei
"""

from guis import *
from guis.controls.AdjModelRender import AdjModelRender
from config.client import ItemModel
from config.client.msgboxtexts import Datas as mbmsgs
from gbref import rds
import Define

class VehicleRender( AdjModelRender ) :
	__cc_config = "config/client/uimodel_configs/vehicle.py"

	def __init__( self, mirror ) :
		AdjModelRender.__init__( self, mirror, 0, self.__cc_config )
		self.bgTexture = "guis/general/petswindow/renderbg.tga"
		self.cfgKey_ = 0


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onModelCreated( self, itemModelID, model ) :
		"""
		创建模型回调
		"""
		if self.cfgKey_ != itemModelID :
			return
		if model is None :
			self.update( 0, None )
			# 创建模型失败！
			showMessage( 0x0521, "", MB_OK, pyOwner = self )
		else :
			effectIDs = rds.itemModel.getMEffects( itemModelID )
			for effectID in effectIDs:
				dictData = rds.spellEffect.getEffectConfigDict( effectID )
				if len( dictData ) == 0: continue
				effect = rds.skillEffect.createEffect( dictData, model, model, Define.TYPE_PARTICLE_PLAYER,  Define.TYPE_PARTICLE_PLAYER )
				effect.start()
			self.update( itemModelID, model )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resetModel( self, itemModelID, bgCreate = True ) :
		"""
		重新设置模型
		@type			itemModelID : INT32
		@param			itemModelID : 模型对应的物品 ID
		@type			bgCreate	: bool
		@param			bgCreate	: 是否在后台创建模型
		@return					 	: None
		"""
		if itemModelID == self.cfgKey_ : return
		else:
			self.cfgKey_ = itemModelID
		if itemModelID is None :
			self.update( 0, None )
			return
			# "骑宠模型'%i'不存在！"
			showMessage( mbmsgs[0x0522] % itemModelID, "", MB_OK, pyOwner = self )
		else :
			if bgCreate :
				rds.itemModel.createModelBG( itemModelID, Functor( self.__onModelCreated, itemModelID ) )
			else :
				model = rds.itemModel.createModel( itemModelID )
				self.__onModelCreated( itemModelID, model )

	def update( self, cfgKey, model ):
		"""
		设置关键字信息和模型
		"""
		self.cfgKey_ = cfgKey
		AdjModelRender.setModel( self, model )

	# -------------------------------------------------
	def getViewInfos( self ) :
		"""
		获取所有模型信息
		"""
		keys = self.configDatas_.keys()
		infos = []
		pathPrifx = "mount/"														# 法宝模型前缀
		for itemModelID, val in ItemModel.Datas.iteritems() :
			sources = val.get( "model_source1", None )								# 获取模型资源
			if sources is None : continue											# 资源不存在
			if not len( sources ) : continue
			source = sources[0]
			if not source.startswith( pathPrifx ) : continue						# 非法宝资源
			viewInfo = self.getViewInfo( itemModelID )
			pos = Math.Vector3( 0, 0, 0 )
			pitch = 0.0
			yaw = 0.0
			if viewInfo :
				pos = viewInfo["position"]
				pitch = viewInfo["pitch"]
				if viewInfo.has_key( "yaw" ):
					yaw = viewInfo["yaw"]
			modelInfo = self.creatModelInfo_( itemModelID, itemModelID, pos, pitch, yaw )
			if itemModelID == self.cfgKey_ :										# 把当前模型放到第一位
				infos.insert( 0, modelInfo )
			else :
				infos.append( modelInfo )
			if itemModelID in keys :
				keys.remove( itemModelID )
		assert infos[0].mark == self.cfgKey_, "current model number is not in model list!"
		infos[0].position = self.modelPos
		infos[0].pitch = self.pitch
		for key in keys :															# 删除被废弃的模型配置
			self.configDatas_.pop( key )
		return infos

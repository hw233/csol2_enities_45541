# -*- coding: gb18030 -*-
#
# $Id: PetModelRender.py,v 1.5 2008-08-28 03:56:26 huangyongwei Exp $

"""
implement model's ui render

2008.07.31 -- by huangyongwei
"""

from guis import *
from gbref import rds
from guis.controls.AdjModelRender import AdjModelRender
from config.client import ItemModel
from config.client.msgboxtexts import Datas as mbmsgs
from RobotInfosLoader import robotInfosLoader
from config.skill.Skill.SkillDataMgr import Datas as skDatas
import skills
import Define

class RobotRender( AdjModelRender ) :
	__cc_config = "config/client/uimodel_configs/robot.py"

	def __init__( self, mirror ) :
		AdjModelRender.__init__( self, mirror, 0, self.__cc_config )
		self.bgTexture = "guis/general/petswindow/renderbg.tga"
		self.cfgKey_ = ""


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onModelCreated( self, className, model ) :
		"""
		创建模型回调
		"""
		if self.cfgKey_ != className :
			return
		if model is None :
			self.update( 0, None )
			# 创建模型失败！
			showMessage( 0x0521, "", MB_OK, pyOwner = self )
		else :
			effectIDs = rds.itemModel.getMEffects( className )
			for effectID in effectIDs:
				dictData = rds.spellEffect.getEffectConfigDict( effectID )
				if len( dictData ) == 0: continue
				effect = rds.skillEffect.createEffect( dictData, model, model, Define.TYPE_PARTICLE_PLAYER,  Define.TYPE_PARTICLE_PLAYER )
				effect.start()
			self.update( className, model )
	
	def __getSkillID( self, className ):
		player = BigWorld.player()
		for skillID in player.skillList_:
			skData = skDatas[skillID]
			if skData["param1"] == className:
				return skillID
		return 0


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resetModel( self, className, bgCreate = True ) :
		"""
		重新设置模型
		@type			itemModelID : INT32
		@param			itemModelID : 模型对应的物品 ID
		@type			bgCreate	: bool
		@param			bgCreate	: 是否在后台创建模型
		@return					 	: None
		"""
		if className == self.cfgKey_ : return
		else:
			self.cfgKey_ = className
		if className is None :
			self.update( 0, None )
			return
			# "骑宠模型'%i'不存在！"
			showMessage( mbmsgs[0x0522] % itemModelID, "", MB_OK, pyOwner = self )
		else :
			robotInfo = robotInfosLoader.getRobotInfo( className )
			modelNum = robotInfo.modelNum
			if bgCreate :
				rds.itemModel.createModelBG( modelNum, Functor( self.__onModelCreated, modelNum ) )
			else :
				model = rds.npcModel.createDynamicModel( modelNum )
				self.__onModelCreated( className, model )

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
		robotInfo = robotInfosLoader.getRobotInfo( self.cfgKey_ )
		name = robotInfo.name
		pos = self.modelPos
		pitch = self.pitch
		yaw = self.yaw
		modelInfo = self.creatModelInfo_( self.cfgKey_, name, pos, pitch, yaw )
		return [modelInfo]											# 只调整当前职业
		for key in keys :															# 删除被废弃的模型配置
			self.configDatas_.pop( key )
		return infos

# -*- coding: gb18030 -*-
#
# $Id: RoleModelRender.py,v 1.5 2008/08/28 03:56:30 huangyongwei Exp $

"""
implement role model's render

2008.08.01 -- writen by huangyongwei
"""

from gbref import PyConfiger
from guis import *
from guis.controls.ModelRender import ModelRender
from gbref import rds
import csdefine
import Const
import Define
import event.EventCenter as ECenter

class TargetModelRender( ModelRender ) :
	__cc_config = "config/client/uimodel_configs/role.py"

	def __init__( self, mirror ) :
		ModelRender.__init__( self, mirror )
		self.bgTexture = "guis/general/playerprowindow/equippanel/renderBg.tga"		# 背景贴图
		self.mapping = util.getGuiMapping( ( 256, 512 ), 8, 248, 104, 429 )

		self.__cfgDatas = PyConfiger().read( self.__cc_config, {} )					# 角色模型位置配置
		self.__profession = -1														# 角色职业

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onModelChanged_( self, oldModel ) :
		"""
		模型改变时被调用
		"""
		if self.__profession >= 0 :
			viewInfo = self.__cfgDatas.get( self.__profession, None )
			if viewInfo :
				self.modelPos = viewInfo["position"]
				self.pitch = viewInfo["pitch"]
			self.playAction()
		ModelRender.onModelChanged_( self, oldModel )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def clearModel( self ) :
		"""
		清除当前显示的模型
		"""
		self.__profession = -1
		self.setModel( None )

	def resetModel( self, role, fashionNum ) :
		"""
		重新设置模型
		"""
		def callback( model ):
			if not role.inWorld: return
			# 发型
			self.setModel( model )
			onHairChanged()
			# 左手
			onLeftHandChanged()
			# 右手
			onRightHandChanged()
			# 显示身上的装备粒子效果
			if not fashionNum:
				role.createBodyEffectBG( model )
				role.createFeetEffectBG( model )

		def onHairChanged():
			"""
			发型改变通知
			"""
			def callback( model ):
				if not role.inWorld: return
				rds.effectMgr.linkObject( self.model, "HP_head", model )
			hairNumber = role.hairNumber
			rds.roleMaker.createHairModelBG( hairNumber, fashionNum, profession, gender, callback )

		def onLeftHandChanged():
			"""
			角色更换左手武器通知
			"""
			def callback( model ):
				if not role.inWorld: return
				role.weaponAttachEffect( model, role.lefthandFDict )
				key = "HP_left_shield"
				if profession in [csdefine.CLASS_SWORDMAN, csdefine.CLASS_ARCHER]:
					key = "HP_left_hand"
				rds.effectMgr.linkObject( self.model, key, model )

			lefthandFDict = role.lefthandFDict
			rds.roleMaker.createMWeaponModelBG( lefthandFDict, callback )

		def onRightHandChanged():
			"""
			角色更换右手武器通知
			"""
			def callback( model ):
				if not role.inWorld: return
				role.weaponAttachEffect( model, role.righthandFDict )
				key = "HP_right_hand"
				rds.effectMgr.linkObject( self.model, key, model )

			righthandFDict = role.righthandFDict
			rds.roleMaker.createMWeaponModelBG( righthandFDict, callback )

		profession = role.getClass()
		gender = role.getGender()
		self.__profession = profession
		roleInfo = role.getModelInfo()
		roleInfo.update( {"fashionNum" : fashionNum } )
		showModels = rds.roleMaker.getShowModelPath( roleInfo )
		partModels = rds.roleMaker.getPartModelPath( roleInfo )
		rds.roleMaker.createPartModelBG( role.id, roleInfo, callback )
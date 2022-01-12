# -*- coding: gb18030 -*-
#
# $Id: RoleModelRender.py,v 1.5 2008-08-28 03:56:30 huangyongwei Exp $

"""
implement role model's render

2008.08.01 -- writen by huangyongwei
"""

import csdefine
import csconst
import Const
import event.EventCenter as ECenter
from gbref import rds
from guis import *
from guis.controls.AdjModelRender import AdjModelRender
import Define
import random
import BigWorld

class RoleModelRender( AdjModelRender ) :
	__cc_config = "config/client/uimodel_configs/role.py"

	def __init__( self, mirror ) :
		AdjModelRender.__init__( self, mirror, -1, self.__cc_config )
		self.bgTexture = "guis/general/playerprowindow/equippanel/renderBg.tga"		# 背景贴图
		self.mapping = util.getGuiMapping( ( 256, 512 ), 8, 248, 104, 429 )

		self.__triggers = {}
		self.__reigisterTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __reigisterTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_MODEL_CHANGED"] = self.__onBodyChanged
		self.__triggers["EVT_ON_ROLE_HAIR_CHANGED"] = self.__onHairChanged
		self.__triggers["EVT_ON_ROLE_LEFTHAND_CHANGED"] = self.__onLeftHandChanged
		self.__triggers["EVT_ON_ROLE_RIGHTHAND_CHANGED"] = self.__onRightHandChanged
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	# -------------------------------------------------
	def __onBodyChanged( self ):
		"""
		角色换装通知
		"""
		player = BigWorld.player()
		if player is None: return

		def callback( newModel ):
			"""
			角色换装模型创建回调
			"""
			if newModel is None: return
			oldModel = self.model
			# 发型很重要
			hairModel = oldModel.head
			# 武器盾牌替换
			lefthand = oldModel.left_hand
			righthand = oldModel.right_hand
			leftshield = oldModel.left_shield
			oldModel.head = None
			oldModel.left_hand = None
			oldModel.right_hand = None
			oldModel.left_shield = None
			newModel.head = hairModel
			newModel.left_hand = lefthand
			newModel.right_hand = righthand
			newModel.left_shield = leftshield
			# 光效效果
			if not player.fashionNum:
				player.createBodyEffectBG( newModel )
				player.createFeetEffectBG( newModel )
			if hasattr( newModel, "shangshen1") and newModel.shangshen1.tint[-2] == "_":
				if hasattr( newModel, "lian1" ):
					tint = newModel.lian1.tint + "_2"
					newModel.lian1 = tint
			self.setModel( newModel )

		roleInfo = player.getModelInfo()
		rds.roleMaker.createPartModelBG( player.id, roleInfo, callback )

	def __onHairChanged( self ):
		"""
		发型改变通知
		"""
		player = BigWorld.player()
		if player is None: return

		def callback( model ):
			key = "HP_head"
			rds.effectMgr.linkObject( self.model, key, model )

		hairNumber = player.hairNumber
		fashionNum = player.fashionNum
		rds.roleMaker.createHairModelBG( hairNumber, fashionNum, player.getClass(), player.getGender(), callback )

	def __onLeftHandChanged( self ):
		"""
		角色更换左手武器通知
		"""
		player = BigWorld.player()
		if player is None: return

		def callback( model ):
			player.weaponAttachEffect( model, player.lefthandFDict )
			profession = player.getClass()
			key = "HP_left_shield"
			if profession in [csdefine.CLASS_SWORDMAN, csdefine.CLASS_ARCHER]:
				key = "HP_left_hand"
			rds.effectMgr.linkObject( self.model, key, model )

		lefthandFDict = player.lefthandFDict
		rds.roleMaker.createMWeaponModelBG( lefthandFDict, callback )

	def __onRightHandChanged( self ):
		"""
		角色更换右手武器通知
		"""
		player = BigWorld.player()
		if player is None: return

		def callback( model ):
			"""
			右手武器模型创建回调
			"""
			player.weaponAttachEffect( model, player.righthandFDict )
			key = "HP_right_hand"
			rds.effectMgr.linkObject( self.model, key, model )
			
			weaponNum = player.righthandFDict["modelNum"]
			if weaponNum:
				actionName = rds.itemModel.getActionsName( weaponNum )
				if actionName:
					timetick = rds.itemModel.getTimetick( weaponNum )
					def callback():
						if not model: return
						if not model.inWorld:return 
						if model.hasAction( actionName ):
							rds.actionMgr.playAction( model, actionName )
						BigWorld.callback(random.randint( timetick[0], timetick[1] ),callback )
					callback()

		righthandFDict = player.righthandFDict
		rds.roleMaker.createMWeaponModelBG( righthandFDict, callback )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onEnterWorld( self ) :
		"""
		角色进入世界后，重新设置模型
		"""
		self.resetModel()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def resetModel( self, profession = None ):
		"""
		EnterWorld 创建角色模型
		"""
		player = BigWorld.player()
		if player is None: return

		def callback( model ):
			self.setModel( model )
			self.__onHairChanged()
			self.__onLeftHandChanged()
			self.__onRightHandChanged()
			if not player.fashionNum:
				player.createBodyEffectBG( model )
				player.createFeetEffectBG( model )
			# 法师特有光效的说
			if player.getClass() == csdefine.CLASS_MAGE:
				rds.effectMgr.createParticleBG( model, "HP_root", Const.CLASS_MAGE_USE_PARTICLE, type = Define.TYPE_PARTICLE_PLAYER )
			if hasattr( model, "shangshen1") and model.shangshen1.tint[-2] == "_":
				if hasattr( model, "lian1" ):
					tint = model.lian1.tint + "_2"
					model.lian1 = tint

		self.cfgKey_ = profession
		if profession is None : self.cfgKey_ = player.getClass()
		roleInfo = player.getModelInfo()
		rds.roleMaker.createPartModelBG( player.id, roleInfo, callback )

	# -------------------------------------------------
	def getViewInfos( self ) :
		"""
		获取所有模型信息
		"""
		proName = csconst.g_chs_class[self.cfgKey_]					# 模型对应的职业名称
		pos = self.modelPos
		pitch = self.pitch
		yaw = self.yaw
		modelInfo = self.creatModelInfo_( self.cfgKey_, proName, pos, pitch, yaw )
		return [modelInfo]											# 只调整当前职业

# -*- coding: gb18030 -*-

"""
实现地表是的光圈

2010.05.05: rewriten by huangyongwei
"""

import BigWorld
from bwdebug import *
import Const
from gbref import rds
from AbstractTemplates import Singleton
import csdefine

class UnitSelect( Singleton ) :
	def __init__( self ) :
		self.__moveGuideModel = None				# 鼠标点击地面，指示角色移动的光圈

		self.textureName_g = "gzawu/unitselect/unitselectcircle_g.dds"
		self.textureName_r = "gzawu/unitselect/unitselectcircle_r.dds"

		self.__targetModel = None
		self.targetSelect = BigWorld.UnitSelect()	# 选择圈
		self.__focusModel = None
		self.focusSelect = BigWorld.UnitSelect()	# 焦点圈
		self.__spellModel = None
		self.spellSelect = BigWorld.UnitSelect()	# 技能圈
		self.targetSelect.setTexture( self.textureName_g )
		self.focusSelect.setTexture( self.textureName_g )
		self.spellSelect.setTexture( self.textureName_g )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onRoleLeaveWorld( self ) :
		"""
		角色离开世界时被调用
		"""
		self.hideMoveGuider()
		self.__moveGuideModel = None

		self.hideTarget()
		self.hideFocus()
		self.hideSpellSite()

	# -------------------------------------------------
	# 实现角色移动到目标的光圈
	# -------------------------------------------------
	def showMoveGuider( self, pos ) :
		"""
		显示角色移动到目的地的光圈
		@type			pos : tuple/Vector3
		@param			pos : 光圈显示位置（角色意欲移动到的目的地）
		"""
		player = BigWorld.player()
		model = self.__moveGuideModel
		if model is None :
			model = BigWorld.Model( "gzawu/unitselect/arrow_new.model" )
			player.addModel( model )
			self.__moveGuideModel = model
		model.position = pos
		model.visible = True
		rds.actionMgr.playAction( model, Const.MODEL_ACTION_MOVE )

	def hideMoveGuider( self ) :
		"""
		隐藏移动到目的地的光圈
		"""
		if self.__moveGuideModel :
			rds.actionMgr.stopAction( self.__moveGuideModel, Const.MODEL_ACTION_MOVE )
			self.__moveGuideModel.visible = False

	# -------------------------------------------------
	# 技能光圈
	# -------------------------------------------------
	def setSpellSite( self, pos ):
		"""
		显示施法目标位置光圈
		@type			pos	   : tuple/Vector3
		@param			pos	   : 施法位置
		"""
		self.hideFocus()	# 有技能光圈不显示焦点光圈
		player = BigWorld.player()
		model = self.__spellModel
		if model is None :
			model = BigWorld.Model("")
			player.addModel( model )
			self.__spellModel = model
			self.spellSelect.setModel( model )
		model.position = pos
		self.showSpellSite()

	def showSpellSite( self ):
		"""
		显示技能光圈
		"""
		self.spellSelect.visible = True

	def hideSpellSite( self ):
		"""
		隐藏技能光圈
		"""
		self.spellSelect.visible = False
		model = self.__spellModel
		if model is None: return
		player = BigWorld.player()
		if player and model in list( player.models ):
			player.delModel( model )
		self.__spellModel = None

	def setSpellSize( self, size ):
		"""
		设置技能光圈大小
		param size: 技能光圈大小
		type size: float
		"""
		self.spellSelect.curUnitSize = size

	def setSpellTexture( self, textureName ):
		"""
		设置技能光圈贴图
		param textureName: 技能光圈贴图路径
		type textureName: string
		return None
		"""
		self.spellSelect.setTexture( textureName )

	def setInRangeTexture( self ):
		"""
		技能施法范围之内（绿色贴图）
		"""
		self.setSpellTexture( self.textureName_g )

	def setOutOfRangeTexture( self ):
		"""
		超出技能施法范围（红色贴图）
		"""
		self.setSpellTexture( self.textureName_r )

	# -------------------------------------------------
	# 脚底光圈
	# -------------------------------------------------

	def getTexture( self, entity ):
		"""
		返回该entity使用的texture
		param entity: 目标
		type entity: entity
		return string
		"""
		if BigWorld.player().queryRelation( entity ) == csdefine.RELATION_ANTAGONIZE:
			texture = self.textureName_r
		else:
			texture = self.textureName_g

		return texture

	def getTargetID( self ):
		"""
		返回选择圈的ID
		return entityID
		"""
		return self.targetSelect.entityID

	def getTargetModel( self ):
		"""
		返回选择光圈的模型
		return pyModel
		"""
		return self.__targetModel

	def setTarget( self, target ):
		"""
		设置选择光圈目标
		param target: 脚底光圈目标
		type target: entity/pyModel/none
		return	None
		"""
		if isinstance( target, BigWorld.Model ):
			if self.getFocusModel() == target:
				self.detachFocus()
			self.__targetModel = target
			self.targetSelect.setModel( target )
		elif isinstance( target, BigWorld.Entity ):
			self.__targetModel = None
			if self.getFocusID() == target.id:
				self.detachFocus()

			self.setTargetTexture( self.getTexture( target ) )
			self.targetSelect.setEntity( target )
			self.targetSelect.curUnitSize = target.getUSelectSize()
		else:
			return

		self.showTarget()

	def showTarget( self ):
		"""
		显示选择光圈
		return None
		"""
		self.targetSelect.visible = True

	def hideTarget( self ):
		"""
		隐藏选择光圈
		return None
		"""
		self.targetSelect.visible = False

	def detachTarget( self ):
		"""
		删除选择光圈
		return None
		"""
		self.hideFocus()
		self.__targetModel = None
		self.targetSelect.setEntity( None )
		self.targetSelect.setModel( None )

	def refreshTarget( self, target ):
		"""
		刷新选择光圈
		param target: 脚底光圈目标
		type target: entity
		return None
		"""
		if isinstance( target, BigWorld.Entity ) and self.getTargetID() == target.id:
			self.detachTarget()
			self.setTarget( target )

	def setTargetTexture( self, textureName ):
		"""
		设置选择光圈贴图
		param textureName: 脚底光圈贴图路径
		type textureName: string
		return None
		"""
		self.targetSelect.setTexture( textureName )

	# -------------------------------------------------
	# 焦点光圈
	# -------------------------------------------------
	def getFocusID( self ):
		"""
		返回焦点光圈ID
		return entityID
		"""
		return self.focusSelect.entityID

	def getFocusModel( self ):
		"""
		返回焦点光圈模型
		return pyModel
		"""
		return self.__focusModel

	def setFocus( self, target ):
		"""
		显示焦点光圈
		param target: 焦点光圈目标
		type target: entity/pyModel/none
		return	None
		"""
		if isinstance( target, BigWorld.Model ):
			if self.getTargetModel() == target:
				return
			self.__focusModel = target
			self.focusSelect.setModel( target )
		elif isinstance( target, BigWorld.Entity ):
			if self.getTargetID() == target.id:
				return
			self.setFocusTexture( self.getTexture( target ) )
			self.focusSelect.setEntity( target )
			self.focusSelect.curUnitSize = target.getUSelectSize()
		else:
			return

		if self.__spellModel: return	# 有技能光圈不显示焦点光圈
		self.showFocus()

	def showFocus( self ):
		"""
		显示焦点光圈
		"""
		self.focusSelect.visible = True

	def hideFocus( self ):
		"""
		隐藏焦点光圈
		"""
		self.focusSelect.visible = False

	def detachFocus( self ):
		"""
		删除焦点光圈
		"""
		self.hideFocus()
		self.__focusModel = None
		self.focusSelect.setEntity( None )
		self.focusSelect.setModel( None )

	def refreshFocus( self, target ):
		"""
		刷新焦点光圈
		param target: 焦点光圈目标
		type target: entity
		return None
		"""
		if isinstance( target, BigWorld.Entity ) and self.getFocusID() == target.id:
			self.detachFocus()
			self.setFocus( target )

	def setFocusTexture( self, textureName ):
		"""
		设置焦点光圈贴图
		param textureName: 脚底焦点贴图路径
		type textureName: string
		return None
		"""
		self.focusSelect.setTexture( textureName )

# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
unitSelect = UnitSelect()

# -*- coding: gb18030 -*-

from bwdebug import *
import BigWorld
import Math
from gbref import rds

# ------------------------------------------------------------------------------
# Class ModelColorMgr:
# 模型变色管理器
# ------------------------------------------------------------------------------
class ModelColorMgr:

	def __init__( self, pyModel ):
		self.model = pyModel
		self.colorBGs = []
		self.defaultColor = Math.Vector4( 1, 1, 1, 1 )
		self.currColor = Math.Vector4( 1, 1, 1, 1 )
		self.currBgColor = Math.Vector4( 1, 1, 1, 1 )

	def onModelChange( self, oldModel, newModel ):
		"""
		模型更换通知
		@type oldModel		PyModel
		@param oldModel		旧模型
		@type newModel		PyModel
		@param newModel		新模型
		@return None
		"""
		self.model = newModel
		self.updateModelColor()

	def addModelColorBG( self, id, color, lastTime ):
		"""
		添加模型的背景颜色
		@type id			Uint64
		@param id			唯一标识符,通常是buffID
		@type color			Vector4
		@param color		颜色
		@type lastTime		Float
		@param lastTime		淡入淡出时间
		@return None
		"""
		self.colorBGs.append( ( id, color, lastTime ) )
		self.updateModelColor()

	def removeModelColorBG( self, id ):
		"""
		移除模型的背景颜色
		@type id			Uint64
		@param id			唯一标识符,通常是buffID
		@return None
		"""
		for k in xrange( len( self.colorBGs ) - 1, -1, -1 ):
			data = self.colorBGs[k]
			if data[0] == id:
				self.colorBGs.remove( data )
				break
		self.updateModelColor()

	def updateModelColor( self ):
		"""
		刷新模型当前颜色
		"""
		if self.model is None: return
		if not self.model.inWorld: return
		if len( self.colorBGs ) == 0:
			color = Math.Vector4( 1, 1, 1, 1 )
			rds.effectMgr.setModelColor( self.model, self.currColor, color, 0.5 )
			return

		id, color, lastTime = self.colorBGs[-1]
		self.currBgColor = color
		rds.effectMgr.setModelColor( self.model, self.currColor, color, lastTime )

	def setModelColor( self, dstColor, lastTime ):
		"""
		@type dstColor		Vector4
		@param dstColor		最终颜色
		@type lastTime		Float
		@param lastTime		淡入淡出时间
		@return None
		"""
		rds.effectMgr.setModelColor( self.model, self.currBgColor, dstColor, lastTime )
		self.currColor = dstColor
		BigWorld.callback( lastTime, self.updateModelColor )
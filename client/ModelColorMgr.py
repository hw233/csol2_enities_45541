# -*- coding: gb18030 -*-

from bwdebug import *
import BigWorld
import Math
from gbref import rds

# ------------------------------------------------------------------------------
# Class ModelColorMgr:
# ģ�ͱ�ɫ������
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
		ģ�͸���֪ͨ
		@type oldModel		PyModel
		@param oldModel		��ģ��
		@type newModel		PyModel
		@param newModel		��ģ��
		@return None
		"""
		self.model = newModel
		self.updateModelColor()

	def addModelColorBG( self, id, color, lastTime ):
		"""
		���ģ�͵ı�����ɫ
		@type id			Uint64
		@param id			Ψһ��ʶ��,ͨ����buffID
		@type color			Vector4
		@param color		��ɫ
		@type lastTime		Float
		@param lastTime		���뵭��ʱ��
		@return None
		"""
		self.colorBGs.append( ( id, color, lastTime ) )
		self.updateModelColor()

	def removeModelColorBG( self, id ):
		"""
		�Ƴ�ģ�͵ı�����ɫ
		@type id			Uint64
		@param id			Ψһ��ʶ��,ͨ����buffID
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
		ˢ��ģ�͵�ǰ��ɫ
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
		@param dstColor		������ɫ
		@type lastTime		Float
		@param lastTime		���뵭��ʱ��
		@return None
		"""
		rds.effectMgr.setModelColor( self.model, self.currBgColor, dstColor, lastTime )
		self.currColor = dstColor
		BigWorld.callback( lastTime, self.updateModelColor )
# -*- coding: gb18030 -*-
#
# $Id: FloatName.py,v 1.28 2008-08-16 03:30:41 phw Exp $

"""
implement float name of the character
2009.02.13：tidy up by huangyongwei
"""

from guis import *
from guis.common.GUIBaseObject import GUIBaseObject
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText

class DoubleName( GUIBaseObject ) :
	def __init__( self, lrName ) :
		GUIBaseObject.__init__( self, lrName )
		self.pyLeftName_ = StaticText( lrName.stLeft )
		self.pyRightName_ = StaticText( lrName.stRight )
		self.pyLeftName_.setFloatNameFont()
		self.pyRightName_.setFloatNameFont()

		self.__leftName = ""				# 左边的名字
		self.__rightName = ""				# 右边的名字
		self.__color = 255,255,255,255		# 整体颜色
		self.__leftColor = 255,255,255,255	# 左边颜色
		self.__rightColor = 255,255,255,255	# 右边颜色
		self.__fontSize = 14.0				#字体大小

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def layout_( self ) :
		if self.pyLeftName_.visible and self.pyLeftName_.text != "" :
			self.pyLeftName_.left = 0.0
			if self.pyRightName_.visible :
				self.pyRightName_.left = self.pyLeftName_.right + 2.0
				self.width = self.pyRightName_.right + 1.0
			else :
				self.width = self.pyLeftName_.right + 1.0
			self.visible = True
		else :
			if self.pyRightName_.visible :
				self.pyRightName_.left = 0.0
				self.width = self.pyRightName_.right + 1.0
				self.visible = True
			else :
				self.visible = False

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def toggleLeftName( self, visible ) :
		"""
		显示/隐藏左边名字
		"""
		self.pyLeftName_.visible = visible
		self.layout_()

	def toggleRightName( self, visible ) :
		"""
		显示/隐藏右边名字
		"""
		self.pyRightName_.visible = visible
		self.layout_()

	def toggleDoubleName( self,visible ) :
		"""
		显示/隐藏两边的名字
		"""
		self.pyLeftName_.visible = visible
		self.pyRightName_.visible = visible
		self.layout_()

	def leftDispose( self ) :
		self.pyLeftName_.dispose()

	def rightDispose( self ) :
		self.pyRightName_.dispose()


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getLeftName( self ) :
		return self.__leftName

	def _setLeftName( self, leftName ) :
		self.__leftName = leftName
		self.pyLeftName_.text = leftName
		self.layout_()

	def _getRightName( self ) :
		return self.__rightName

	def _setRightName( self, rightName ) :
		self.__rightName = rightName
		self.pyRightName_.text = rightName
		self.layout_()

	def _getColor( self ) :
		return self.__color

	def _setColor( self,value ) :
		self.__color = value
		self._setLeftColor( value )
		self._setRightColor( value )

	def _getLeftColor( self ) :
		return self.__leftColor

	def _setLeftColor( self,value ) :
		self.__leftColor = value
		self.pyLeftName_.color = value

	def _setRightColor( self,value ) :
		self.__rightColor = value
		self.pyRightName_.color = value

	def _getRightColor( self ) :
		return self.pyRightName_.color
	
	def _setRightFontSize( self, fontSize ) :
		self.pyRightName_.fontSize = fontSize

	def _getRightFontSize( self ) :
		return self.pyRightName_.fontSize
	
	def _getFontSize( self ):
		return self.__fontSize
	
	def _setFontSize( self, fontSize ):
		self.__fontSize = fontSize
		self.pyLeftName_.fontSize = fontSize
		self.pyRightName_.fontSize = fontSize

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	leftName = property( _getLeftName, _setLeftName )
	rightName = property( _getRightName, _setRightName )
	color = property( _getColor, _setColor )
	leftColor = property( _getLeftColor, _setLeftColor )
	rightColor = property( _getRightColor, _setRightColor )
	rightFontSize = property( _getRightFontSize, _setRightFontSize )
	fontSize = property( _getFontSize, _setFontSize )

# --------------------------------------------------------------------------
#角色头顶帮会信息
class TongName( GUIBaseObject ):
	def __init__( self, tongName ):
		GUIBaseObject.__init__( self, tongName )
		self.__pyDoubleName = DoubleName( tongName.doubleName )
		self.__pyDoubleName.leftName = ""
		self.__pyDoubleName.rightName = ""
		
		self.__pyTongIcon = PyGUI( tongName.tongIcon )
		self.__pyTongIcon.texture = ""
		self.__dbNameSitScale = 0.0
		self.__color = 255, 255, 255, 255
		
	def layout_( self ):
		if self.__pyTongIcon.visible and self.__pyTongIcon.texture != "":
			self.__pyTongIcon.left = 0.0
			if self.__pyDoubleName.visible and self.__pyDoubleName.leftName != "" :
				self.__pyDoubleName.left = self.__pyTongIcon.right + 1.0
				self.width = self.__pyDoubleName.right + 1.0
				self.visible = True
		else:
			if self.__pyDoubleName.visible and self.__pyDoubleName.leftName != "":
				self.__pyDoubleName.left = 0.0
				self.width = self.__pyDoubleName.right + 1.0
				self.visible = True
			else:
				self.visible = False
		self.__dbNameSitScale = float( self.__pyDoubleName.left + self.__pyDoubleName.width/2.0)/self.width
	
	def toggleDoubleName( self, visible ):
		self.__pyDoubleName.toggleDoubleName( visible )
		self.iconVisible = visible
	
	def _getTongIcon( self ):
		return self.__pyTongIcon.texture
	
	def _setTongIcon( self, path ):
		self.__pyTongIcon.texture = path
		self.layout_()
	
	def _getIconVisible( self ):
		return self.__pyTongIcon.visible
	
	def _setIconVisible( self, visible ):
		self.__pyTongIcon.visible = visible
		self.layout_()
	
	def _getLeftName( self ):
		return self.__pyDoubleName.leftName
	
	def _setLeftName( self, leftName ):
		self.__pyDoubleName.leftName = leftName
	
	def _getRightName( self ):
		return self.__pyDoubleName.rightName
	
	def _setRightName( self, rightName ):
		self.__pyDoubleName.rightName = rightName

	def _getCenter( self ):
		offset = self.width*( 0.5 - self.__dbNameSitScale )
		center = GUIBaseObject._getCenter( self )
		return center - offset

	def _setCenter( self, center ):
		offset = self.width*( 0.5 - self.__dbNameSitScale )
		GUIBaseObject._setCenter( self, center + offset )

	def _getColor( self ) :
		return self.__pyDoubleName.color	

	def _setColor( self,value ) :
		self.__pyDoubleName.color = value

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	tongIcon = property( _getTongIcon, _setTongIcon )
	iconVisible = property( _getIconVisible, _setIconVisible )
	leftName = property( _getLeftName, _setLeftName )
	rightName = property( _getRightName, _setRightName )
	center = property( _getCenter, _setCenter )
	color = property( _getColor, _setColor )
	
# ----------------------------------------------------------------------------------
# 角色头顶名称、称号信息,上下2层
# ----------------------------------------------------------------------------------
class RoleDoubleName( DoubleName ):
	
	def __init__( self, roleName ):
		DoubleName.__init__( self, roleName )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def layout_( self ) :
		if self.pyLeftName_.visible and self.pyLeftName_.text != "" :
			self.pyLeftName_.left = 0.0
			if self.pyRightName_.visible :
				self.pyRightName_.top = 1.0
				self.width = max( self.pyLeftName_.width, self.pyRightName_.width )
				self.pyLeftName_.center = self.width/2.0
				self.pyRightName_.center = self.width/2.0
				self.pyLeftName_.top = self.pyRightName_.bottom + 5.0
			else :
				self.pyLeftName_.top = 1.0
				self.width = self.pyLeftName_.right + 1.0
			self.height = self.pyLeftName_.bottom
			self.visible = True
		else :
			if self.pyRightName_.visible :
				self.pyRightName_.left = 0.0
				self.width = self.pyRightName_.right + 1.0
				self.height = self.pyRightName_.bottom
				self.visible = True
			else :
				self.visible = False
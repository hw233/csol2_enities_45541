# -*- coding: gb18030 -*-
#
# $Id: SelectableButton.py,v 1.4 2008-08-01 09:47:33 huangyongwei Exp $

"""
implement button class。
-- 2008/06/18 : writen by huangyongwei
"""
"""
composing :
	GUI.XXX

or
	GUI.Window
		-- lbText：GUI.Text( 可以没有 )
"""


from guis import *
from Button import Button
from guis.common.UIStatesTab import HStatesTabEx
class SelectableButton( Button ) :
	"""
	鼠标左键按下时处于选中状态的按钮
	"""
	def __init__( self, button = None, pyBinder = None ) :
		Button.__init__( self, button, pyBinder )
		self.__initialize( button )						# 初始化
		self.__selected = False
		self.__autoSelect = True						# 是否自动选中（按下鼠标左键时选中）

	def subclass( self, button, pyBinder = None ) :
		Button.subclass( self, button, pyBinder )
		self.__initialize( button )
		return self

	def __del__( self ) :
		Button.__del__( self )
		if Debug.output_del_Button :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, button ) :
		self.mappings_[UIState.SELECTED] = self.mapping								# 选中状态 mapping
		if self.pyText_ :
			self.foreColors_[UIState.SELECTED] = self.foreColors_[UIState.COMMON]	# 选中状态前景色
		self.backColors_[UIState.SELECTED] = self.color


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生事件
		"""
		Button.generateEvents_( self )
		self.__onSelectChanged = self.createEvent_( "onSelectChanged" )			# 当选中状态改变时触发

	@property
	def onSelectChanged( self ) :
		"""
		当被选中时触发
		"""
		return self.__onSelectChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __select( self ) :
		"""
		设置为选中状态
		"""
		if self.selected : return
		self.__selected = True
		self.setState( UIState.SELECTED )
		self.onSelectChanged( True )

	def __deselect( self ) :
		"""
		取消选中
		"""
		if not self.selected : return
		self.__selected = False
		self.setState( UIState.COMMON )
		self.onSelectChanged( False )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		Button.onLMouseDown_( self, mods )
		if self.__autoSelect :
			self.selected = True
			if self.enable :
				self.setState( UIState.SELECTED )
		return True

	def onLMouseUp_( self, mods ) :
		Button.onLMouseUp_( self, mods )
		if self.enable and self.selected :
			self.setState( UIState.SELECTED )
		return True

	# ---------------------------------------
	def onMouseEnter_( self ) :
		Button.onMouseEnter_( self )
		if self.selected :
			self.setState( UIState.SELECTED )
		else :
			self.setState( UIState.HIGHLIGHT )
		return True

	def onMouseLeave_( self ) :
		Button.onMouseLeave_( self )
		if self.selected :
			self.setState( UIState.SELECTED )
		else :
			self.setState( UIState.COMMON )
		return True

	# ---------------------------------------
	def onEnable_( self ) :
		Button.onEnable_( self )
		if self.selected :
			self.setState( UIState.SELECTED )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setStatesMapping( self, stMode ) :
		"""
		设置状态 mapping
		@type					stMode : MACRO DEFINATION / tuple
		@param					stMode : 标示几行几列（将各个状态贴图放到同一张图片上）: ( 行数，列数)
									   : 也可以在 guis.uidefine.py 的 UIState 中选择：MODE_XXX
		"""
		Button.setStatesMapping( self, stMode )
		self.mappings_[UIState.SELECTED] = self.mappings_[UIState.PRESSED]


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setCommonMapping( self, mapping ) :
		if self.state == UIState.COMMON :
			self.mapping = mapping
		self.mappings_[UIState.COMMON] = mapping

	def _setCommonForeColor( self, color ) :
		if self.pyText_ and self.state == UIState.COMMON :
			self.pyText_.color = color
		self.foreColors_[UIState.COMMON] = color

	def _setCommonBackColor( self, color ) :
		if self.state == UIState.COMMON :
			self.color = color
		self.backColors_[UIState.COMMON] = color

	# ---------------------------------------
	def _getSelectedMapping( self ) :
		return self.mappings_[UIState.SELECTED]

	def _setSelectedMapping( self, mapping ) :
		self.mappings_[UIState.SELECTED] = mapping
		self.mappings_[UIState.PRESSED] = mapping
		if self.selected and self.enable :
			self.setStateView_( UIState.SELECTED )

	# ---------------------------------------
	def _getSelectedForeColor( self ) :
		return self.foreColors_[UIState.PRESSED]

	def _setSelectedForeColor( self, color ) :
		self.foreColors_[UIState.SELECTED] = color
		self.foreColors_[UIState.PRESSED] = color
		if self.selected and self.enable :
			self.setStateView_( UIState.SELECTED )

	def _getSelectedBackColor( self ) :
		return self.backColors_[UIState.PRESSED]

	def _setSelectedBackColor( self, color ) :
		self.backColors_[UIState.SELECTED] = color
		self.backColors_[UIState.PRESSED] = color
		if self.selected and self.enable :
			self.setStateView_( UIState.SELECTED )

	# ---------------------------------------
	def _getSelected( self ) :
		return self.__selected

	def _setSelected( self, selected ) :
		if selected == self.__selected :
			return
		if selected : self.__select()
		else : self.__deselect()

	def _getAutoSelect( self ) :
		return self.__autoSelect

	def _setAutoSelect( self, auto ) :
		self.__autoSelect = auto


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	commonMapping = property( Button._getCommonMapping, _setCommonMapping )			# 获取/设置普通状态下的贴图 mapping
	commonForeColor = property( Button._getCommonForeColor, _setCommonForeColor )	# 获取/设置普通状态下的前景色
	commonBackColor = property( Button._getCommonBackColor, _setCommonBackColor )	# 获取/设置普通状态下的背景色
	selectedMapping = property( _getSelectedMapping, _setSelectedMapping )			# 获取/设置选中状态下的贴图 mapping
	selectedForeColor = property( _getSelectedForeColor, _setSelectedForeColor )	# 获取/设置选中状态下的前景色
	selectedBackColor = property( _getSelectedBackColor, _setSelectedBackColor )	# 获取/设置选中状态下的背景色
	selected = property( _getSelected, _setSelected )								# 设置选中状态
	autoSelect = property( _getAutoSelect, _setAutoSelect )							# 获取/设置，是否自动选中（为 True 时，鼠标左键按下选中）
	

class HSelectableButtonEx( SelectableButton, HStatesTabEx ):
	
	def __init__( self, button, pyBinder = None ) :
		SelectableButton.__init__( self, button, pyBinder )
		HStatesTabEx.__init__( self, button )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setStateView_( self, state ) :
		"""
		设置指定状态下的外观表现
		"""
		if state == UIState.DISABLE :
			self.setDisableView_()
			return
		SelectableButton.setStateView_( self, state )
		self.exMappings = self.exMappingsMap_[state]

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setExStatesMapping( self, stMode ) :
		HStatesTabEx.setExStatesMapping( self, stMode )
		self.exMappingsMap_[UIState.SELECTED] = self.exMappingsMap_[UIState.PRESSED]
		if self.enable :
			self.setState( UIState.COMMON )
		
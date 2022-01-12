# -*- coding: gb18030 -*-

from guis import util
from guis.uidefine import UIState
from guis.common.GUIBaseObject import GUIBaseObject


class HStatesTabEx( GUIBaseObject ) :
	"""
	水平方向伸缩的UI Mapping切换器
	GUI.TextureFrame :
	children :
		lbText
	elements :
		frm_l, frm_bg, fem_r
	"""
	def __init__( self, gui ) :
		GUIBaseObject.__init__( self, gui )
		self.exMappingsMap_ = {}									# key : ( e1, e2, e3 )
		self.__initialize( gui )

	def __initialize( self, gui ) :
		exMappings = self.exMappings
		self.exMappingsMap_ = {}									# 状态 mapping
		self.exMappingsMap_[UIState.COMMON] = exMappings			# 普通状态
		self.exMappingsMap_[UIState.HIGHLIGHT] = exMappings			# 高亮状态
		self.exMappingsMap_[UIState.PRESSED] = exMappings			# 鼠标按下状态
		self.exMappingsMap_[UIState.DISABLE] = exMappings			# 无效状态


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setStateView_( self, state ) :
		"""
		设置指定状态下的外观表现
		"""
		self.exMappings = self.exMappingsMap_[state]


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setExStatesMapping( self, stMode ) :
		"""
		设置状态 mapping
		@type					stMode : MACRO DEFINATION / tuple
		@param					stMode : 标示几行几列（将各个状态贴图放到同一张图片上，
									   : 各个部分有自己独立的贴图）: ( 行数，列数)
									   : 也可以在 guis.uidefine.py 的 UIState 中选择：MODE_XXX
		"""
		row, col = stMode
		count = row * col
		if count <= 0 : return
		lSize = self.gui.elements["frm_l"].size
		rSize = self.gui.elements["frm_r"].size
		bgSize = self.gui.elements["frm_bg"].size
		lMapping = util.getStateMapping( lSize, stMode, UIState.ST_R1C1 )
		rMapping = util.getStateMapping( rSize, stMode, UIState.ST_R1C1 )
		bgMapping = util.getStateMapping( bgSize, stMode, UIState.ST_R1C1 )
		self.exMappingsMap_[UIState.COMMON] = lMapping, rMapping, bgMapping
		self.exMappingsMap_[UIState.HIGHLIGHT] = lMapping, rMapping, bgMapping
		self.exMappingsMap_[UIState.PRESSED] = lMapping, rMapping, bgMapping
		self.exMappingsMap_[UIState.DISABLE] = lMapping, rMapping, bgMapping
		if count > 1 :
			state = ( 1 / col + 1, 1 % col + 1 )
			lMapping = util.getStateMapping( lSize, stMode, state )
			rMapping = util.getStateMapping( rSize, stMode, state )
			bgMapping = util.getStateMapping( bgSize, stMode, state )
			self.exMappingsMap_[UIState.HIGHLIGHT] = lMapping, rMapping, bgMapping
		if count > 2 :
			state = ( 2 / col + 1, 2 % col + 1 )
			lMapping = util.getStateMapping( lSize, stMode, state )
			rMapping = util.getStateMapping( rSize, stMode, state )
			bgMapping = util.getStateMapping( bgSize, stMode, state )
			self.exMappingsMap_[UIState.PRESSED] = lMapping, rMapping, bgMapping
		if count > 3 :
			state = ( 3 / col + 1, 3 % col + 1 )
			lMapping = util.getStateMapping( lSize, stMode, state )
			rMapping = util.getStateMapping( rSize, stMode, state )
			bgMapping = util.getStateMapping( bgSize, stMode, state )
			self.exMappingsMap_[UIState.DISABLE] = lMapping, rMapping, bgMapping


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getExMappings( self ) :
		elems = self.gui.elements
		return ( elems["frm_l"].mapping,\
				elems["frm_r"].mapping,\
				elems["frm_bg"].mapping )

	def _setExMappings( self, mappings ) :
		elems = self.gui.elements
		elems["frm_l"].mapping = mappings[0]
		elems["frm_r"].mapping = mappings[1]
		elems["frm_bg"].mapping = mappings[2]

	exMappings = property( _getExMappings, _setExMappings )

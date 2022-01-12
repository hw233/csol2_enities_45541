# -*- coding: gb18030 -*-
#
# $Id: ListItem.py,v 1.33 2008-08-25 07:06:18 huangyongwei Exp $

"""
implement listitem class

-- 2006/06/10: writen by huangyongwei
-- 2008/01/09: add single column item and multi columns item
"""
"""
composing :
	GUI.Window
		-- lbText ( GUI.Text )
"""

import copy
from guis import *
from Control import Control
from StaticText import StaticText
from StaticLabel import StaticLabel
from Label import Label
from guis.tooluis.fulltext.FullText import FullText

# --------------------------------------------------------------------
# implement list item class
# --------------------------------------------------------------------
"""
composing :
	-- GUI.Window

"""

class ListItem( Control ) :
	def __init__( self, item = None, pyBinder = None ) :
		Control.__init__( self, item, pyBinder )
		self.__initialize( item )
		self.__selectable = True							# �Ƿ���Ա�ѡ��
		self.__selected = False								# �Ƿ���ѡ��״̬
		self.__mouseUpSelect = False						# �Ƿ���굯��ʱѡ��
		self.__rMouseSelect = False							# �Ҽ�����ʱ���Ƿ�ѡ�������е�ѡ��
		self.__viewState = UIState.COMMON						# ѡ��ĵ�ǰ״̬

	def subclass( self, item, pyBinder = None ) :
		Control.subclass( self, item, pyBinder )
		self.__initialize( item )
		return self

	def __del__( self ) :
		Control.__del__( self )
		if Debug.output_del_ListItem :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, item ) :
		if item is None : return
		self.focus = True
		self.crossFocus = True

		self.__stateMappings = {}
		self.__stateMappings[UIState.COMMON] = self.mapping
		self.__stateMappings[UIState.HIGHLIGHT] = self.mapping
		self.__stateMappings[UIState.SELECTED] = self.mapping
		self.__stateMappings[UIState.DISABLE] = self.mapping

		defCommonColor = 255, 255, 255, 0
		self.color = defCommonColor
		self.backColors_ = {}
		self.backColors_[UIState.COMMON] = defCommonColor
		self.backColors_[UIState.HIGHLIGHT] = 10, 36, 106, 255
		self.backColors_[UIState.SELECTED] = 34, 61, 69, 255
		self.backColors_[UIState.DISABLE] = 255, 255, 255, 0


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		Control.generateEvents_( self )
		self.__onSelectChanged = self.createEvent_( "onSelectChanged" )
		self.__onHighlight = self.createEvent_( "onHighlight" )

	@property
	def onSelectChanged( self ) :
		return self.__onSelectChanged

	@property
	def onHighlight( self ) :
		return self.__onHighlight


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __select( self ) :
		self.__selected = True
		self.onSelectChanged( True )
		self.setState( UIState.SELECTED )

	def __deselect( self ) :
		self.__selected = False
		self.setState( UIState.COMMON )
		self.onSelectChanged( False )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onStateChanged_( self, state ) :
		pass

	# -------------------------------------------------
	def onMouseEnter_( self ) :
		"""
		after mouse entered, will be called
		"""
		Control.onMouseEnter_( self )
		self.setState( UIState.HIGHLIGHT )
		return True

	def onMouseLeave_( self ) :
		"""
		after mouse left, will be called
		"""
		Control.onMouseLeave_( self )
		if self.__selected :
			self.setState( UIState.SELECTED )
		else :
			self.setState( UIState.COMMON )
		FullText.hide()
		return True

	# ---------------------------------------
	def onLMouseDown_( self, mods ) :
		"""
		when mouse down, it will be called
		"""
		Control.onLMouseDown_( self, mods )
		if not self.__mouseUpSelect and self.selectable :
			self.selected = True
		return True

	def onLMouseUp_( self, mods ) :
		Control.onLMouseUp_( self, mods )
		if self.__mouseUpSelect and self.selectable :
			self.selected = True
		return True

	def onRMouseDown_( self, mods ) :
		Control.onRMouseDown_( self, mods )
		if not self.__rMouseSelect : return True
		if not self.__mouseUpSelect and self.selectable :
			self.selected = True
		return True

	def onRMouseUp_( self, mods ) :
		Control.onRMouseUp_( self, mods )
		if not self.__rMouseSelect : return True
		if self.__mouseUpSelect and self.selectable :
			self.selected = True
		return True

	# ---------------------------------------
	def onEnable_( self ) :
		Control.onEnable_( self )
		self.setState( UIState.COMMON )

	def onDisable_( self ) :
		Control.onDisable_( self )
		self.setState( UIState.DISABLE )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self ) :
		"""
		resume common state
		"""
		self.setState( UIState.COMMON )

	def setState( self, state ) :
		"""
		set view styles under the state
		"""
		if self.enable and self.isMouseHit() :
			state = UIState.HIGHLIGHT
			self.onHighlight()
		elif self.enable and self.selected :
			state = UIState.SELECTED
		self.__viewState = state
		self.color = self.backColors_[state]
		self.mapping = self.__stateMappings[state]
		self.onStateChanged_( state )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getCommonBackColor( self ) :
		return self.backColors_[UIState.COMMON]

	def _setCommonBackColor( self, color ) :
		self.backColors_[UIState.COMMON] = color
		self.color = color

	def _getCommonMapping( self ) :
		return self.__stateMappings[UIState.COMMON]

	def _setCommonMapping( self, mapping ) :
		self.__stateMappings[UIState.COMMON] = mapping

	# ---------------------------------------
	def _getHighlightBackColor( self ) :
		return self.backColors_[UIState.HIGHLIGHT]

	def _setHighlightBackColor( self, color ) :
		self.backColors_[UIState.HIGHLIGHT] = color

	def _getHighlightMapping( self ) :
		return self.__stateMappings[UIState.HIGHLIGHT]

	def _setHighlightMapping( self, mapping ) :
		self.__stateMappings[UIState.HIGHLIGHT] = mapping

	# ---------------------------------------
	def _getSelectedBackColor( self ) :
		return self.backColors_[UIState.SELECTED]

	def _setSelectedBackColor( self, color ) :
		self.backColors_[UIState.SELECTED] = color

	def _getSelectedMapping( self ) :
		return self.__stateMappings[UIState.SELECTED]

	def _setSelectedMapping( self, mapping ) :
		self.__stateMappings[UIState.SELECTED] = mapping

	# ---------------------------------------
	def _getDisableBackColor( self ) :
		return self.backColors_[UIState.DISABLE]

	def _setDisableBackColor( self, color ) :
		self.backColors_[UIState.DISABLE] = color

	def _getDisableMapping( self ) :
		return self.__stateMappings[UIState.DISABLE]

	def _setDisableMapping( self, mapping ) :
		self.__stateMappings[UIState.DISABLE] = mapping

	# -------------------------------------------------
	def _getSelectable( self ) :
		return self.__selectable

	def _setSelectable( self, value ) :
		self.__selectable = value
		if not value and self.__selected :
			self.__deselect()

	# ---------------------------------------
	def _getSelected( self ) :
		return self.__selected

	def _setSelected( self, isSelected ) :
		if not self.enable : return
		if not self.__selectable : return
		if self.__selected == isSelected : return
		if isSelected :
			self.__select()
		else :
			self.__deselect()

	# -------------------------------------------------
	def _getMouseUpSelect( self ) :
		return self.__mouseUpSelect

	def _setMouseUpSelect( self, value ) :
		self.__mouseUpSelect = value

	# ---------------------------------------
	def _getRMouseSelect( self ) :
		return self.__rMouseSelect

	def _setRMouseSelect( self, value ) :
		self.__rMouseSelect = value


	# ----------------------------------------------------------------
	# prperties
	# ----------------------------------------------------------------
	commonBackColor = property( _getCommonBackColor, _setCommonBackColor )			# ��ȡ/������ͨ״̬�µı���ɫ
	commonMapping = property( _getCommonMapping, _setCommonMapping )				# ��ȡ/������ͨ״̬�µ� mapping
	highlightBackColor = property( _getHighlightBackColor, _setHighlightBackColor ) # ��ȡ/���ø���״̬�µı���ɫ
	highlightMapping = property( _getHighlightMapping, _setHighlightMapping )		# ��ȡ/���ø���״̬�µ� mapping
	selectedBackColor = property( _getSelectedBackColor, _setSelectedBackColor )    # ��ȡ/����ѡ��״̬�µı���ɫ
	selectedMapping = property( _getSelectedMapping, _setSelectedMapping )			# ��ȡ/����ѡ��״̬�µ� mapping
	disableBackColor = property( _getDisableBackColor, _setDisableBackColor )		# ��ȡ/������Ч״̬�µı���ɫ
	disableMapping = property( _getDisableMapping, _setDisableMapping )				# ��ȡ/������Ч״̬�µ� mapping

	viewState = property( lambda self : self.__viewState )							# ��ȡѡ�ǰ״̬
	selectable = property( _getSelectable, _setSelectable )							# ��ȡ/����ѡ���Ƿ�ɱ�ѡ��
	selected = property( _getSelected, _setSelected )								# ��ȡ/����ѡ���Ƿ���ѡ��״̬
	mouseUpSelect = property( _getMouseUpSelect, _setMouseUpSelect )				# ��ȡ/�����Ƿ����������ʱѡ��ѡ�Ĭ��Ϊ False��
	rMouseSelect = property( _getRMouseSelect, _setRMouseSelect )					# ��ȡ/�����Ҽ�����Ƿ�ѡ��ѡ�Ĭ��Ϊ False��


# --------------------------------------------------------------------
# implement single text column list item
# --------------------------------------------------------------------
"""
composing :
	-- GUI.Window
		-- lbText: GUI.Text
"""

class SingleColListItem( StaticLabel, ListItem ) :
	def __init__( self, item = None, pyBinder = None ) :
		StaticLabel.__init__( self, item, pyBinder )
		item = StaticLabel.getGui( self )
		ListItem.__init__( self, item, pyBinder )
		self.__initialize( item )

	def subclass( self, item, pyBinder = None ) :
		ListItem.subclass( self, item, pyBinder )
		StaticLabel.subclass( self, item, pyBinder )
		self.__initialize()

	def __del__( self ) :
		ListItem.__del__( self )
		StaticLabel.__del__( self )
		if Debug.output_del_ListItem :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, item ) :
		if item is None : return
		self.foreColors_ = {}
		self.foreColors_[UIState.COMMON] = self.foreColor
		self.foreColors_[UIState.HIGHLIGHT] = 255, 255, 255, 255
		self.foreColors_[UIState.SELECTED] = 10, 255, 10, 255
		self.foreColors_[UIState.DISABLE] = 128, 128, 128, 255


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onStateChanged_( self, state ) :
		ListItem.onStateChanged_( self, state )
		self.foreColor = self.foreColors_[state]

	# -------------------------------------------------
	def onMouseEnter_( self ) :
		"""
		after mouse entered, will be called
		"""
		ListItem.onMouseEnter_( self )
		if self.pyText_.width > self.width :
			FullText.show( self, self.pyText_ )
		return True

	# -------------------------------------------------
	def onMouseLeave_( self ) :
		"""
		after mouse left, will be called
		"""
		ListItem.onMouseLeave_( self )
		FullText.hide()
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setState( self, state ) :
		ListItem.setState( self, state )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getCommonForeColor( self ) :
		return self.foreColors_[UIState.COMMON]

	def _setCommonForeColor( self, color ) :
		self.foreColors_[UIState.COMMON] = color
		self.foreColor = color

	# ---------------------------------------
	def _getHighlightForeColor( self ) :
		return self.foreColors_[UIState.HIGHLIGHT]

	def _setHighlightForeColor( self, color ) :
		self.foreColors_[UIState.HIGHLIGHT] = color

	# ---------------------------------------
	def _getSelectedForeColor( self ) :
		return self.foreColors_[UIState.SELECTED]

	def _setSelectedForeColor( self, color ) :
		self.foreColors_[UIState.SELECTED] = color

	# ---------------------------------------
	def _getDisableForeColor( self ) :
		return self.foreColors_[UIState.DISABLE]

	def _setDisableForeColor( self, color ) :
		self.foreColors_[UIState.DISABLE] = color


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	commonForeColor = property( _getCommonForeColor, _setCommonForeColor )				# ��ȡ/������ͨ״̬�µ�ǰ��ɫ
	highlightForeColor = property( _getHighlightForeColor, _setHighlightForeColor )		# ��ȡ/���ø���״̬�µ�ǰ��ɫ
	selectedForeColor = property( _getSelectedForeColor, _setSelectedForeColor )		# ��ȡ/����ѡ��״̬�µ�ǰ��ɫ
	disableForeColor = property( _getDisableForeColor, _setDisableForeColor )			# ��ȡ/������Ч״̬�µ�ǰ��ɫ


# --------------------------------------------------------------------
# implement multible text column list item
# --------------------------------------------------------------------
"""
composing :
	-- GUI.Window
		-- col_0 : GUI.Window
			-- lbText: GUI.Text
		-- col_1 : GUI.Window
			-- lbText: GUI.Text
		-- col_2 : GUI.Window
			-- lbText: GUI.Text
		����
		����
"""

class MultiColListItem( ListItem ) :
	class __SubItem( Label ) :
		def __init__( self, item, pyBinder ) :
			Label.__init__( self, item, pyBinder )
			self.focus = False
			self.crossFocus = True
			self.align = "C"
			self.realText = ""
			self.showTips = False

			del self.backColors_			# �����õ�����ɫ
			del self.mappings_				# �����õ� mapping

		# ----------------------------------------------------------------
		# protected
		# ----------------------------------------------------------------
		def onMouseEnter_( self ) :
			"""
			������ʱ������
			ע�⣺���ﲻҪ�ص� Lavel �� onMouseEnter_
			"""
			self.pyBinder.onMouseEnter_()
			if self.showTips:
				toolbox.infoTip.showToolTips( self, self.realText )
			return True

		def onMouseLeave_( self ) :
			"""
			����뿪ʱ������
			ע�⣺���ﲻҪ�ص� Lavel �� onMouseLeave_
			"""
			self.pyBinder.onMouseLeave_()
			toolbox.infoTip.hide( self )
			return True

		# -------------------------------------------------
		def onStateChanged_( self, state ) :
			"""
			״̬�ı�ʱ������
			"""
			self.foreColor = self.foreColors_[state]


	# ----------------------------------------------------------------
	# main body
	# ----------------------------------------------------------------
	def __init__( self, item = None, pyBinder = None ) :
		ListItem.__init__( self, item, pyBinder )
		self.pyCols_ = []
		self.__initialize( item )

	def subclass( self, item, pyBinder = None ) :
		ListItem.subclass( self, item, pyBinder )
		self.__initialize( item )

	def __del__( self ) :
		ListItem.__del__( self )
		if Debug.output_del_ListItem :
			INFO_MSG( str( self ) )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, item ) :
		if item is None : return
		self.__initCells( item )
		self.foreColors_ = {}
		self.foreColors_[UIState.COMMON] = self.foreColor
		self.foreColors_[UIState.HIGHLIGHT] = 255, 255, 255, 255
		self.foreColors_[UIState.SELECTED] = 10, 255, 10, 255
		self.foreColors_[UIState.DISABLE] = 128, 128, 128, 255
		for pyCol in self.pyCols_ :
			pyCol.foreColors_ = copy.copy( self.foreColors_ )

	def __initCells( self, panel ) :
		for name, ch in panel.children :
			if "col_" not in name : continue
			pyCol = MultiColListItem.__SubItem( ch, self )
			self.pyCols_.append( pyCol )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onStateChanged_( self, state ) :
		for pyCol in self.pyCols_ :
			pyCol.onStateChanged_( state )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setTextes( self, *textes ) :
		if isDebuged :
			assert len( textes ) == len( self.pyCols_ )
		for index, pyCol in enumerate( self.pyCols_ ) :
			cellText = str( textes[index] )
			pyCol.realText = cellText
			pyCol.text = cellText
			pyCol.showTips = False
			if pyCol.pyText_.width > pyCol.width:	# �����򸡶�����ʾ
				pyCol.showTips = True
				cellText = cellText[:6]
				pyCol.text = cellText + "..."

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getCols( self ) :
		return self.pyCols_[:]

	# ---------------------------------------
	def _getForeColor( self ) :
		"""
		get color of the label
		"""
		return self.pyCols_[0].foreColor

	def _setForeColor( self, color ) :
		"""
		set forecolor
		"""
		for pyCol in self.pyCols_ :
			pyCol.foreColor = color

	# -------------------------------------------------
	def _getCommonForeColor( self ) :
		return self.foreColors_[UIState.COMMON]

	def _setCommonForeColor( self, color ) :
		self.foreColors_[UIState.COMMON] = color
		if self.viewState == UIState.COMMON :
			self.foreColor = color
			for pyCol in self.pyCols_ :
				pyCol.foreColors_[UIState.COMMON] = color
				pyCol.foreColor = color
		else :
			for pyCol in self.pyCols_ :
				pyCol.foreColors_[UIState.COMMON] = color

	# ---------------------------------------
	def _getHighlightForeColor( self ) :
		return self.foreColors_[UIState.HIGHLIGHT]

	def _setHighlightForeColor( self, color ) :
		self.foreColors_[UIState.HIGHLIGHT] = color
		for pyCol in self.pyCols_ :
			pyCol.foreColors_[UIState.HIGHLIGHT] = color

	# ---------------------------------------
	def _getSelectedForeColor( self ) :
		return self.foreColors_[UIState.SELECTED]

	def _setSelectedForeColor( self, color ) :
		self.foreColors_[UIState.SELECTED] = color
		for pyCol in self.pyCols_ :
			pyCol.foreColors_[UIState.SELECTED] = color

	# ---------------------------------------
	def _getDisableForeColor( self ) :
		return self.foreColors_[UIState.DISABLE]

	def _setDisableForeColor( self, color ) :
		self.foreColors_[UIState.DISABLE] = color
		for pyCol in self.pyCols_ :
			pyCol.foreColors_[UIState.DISABLE] = color
			
	def _setFontSize( self, fontSize ):
		for pyCol in self.pyCols_:
			pyCol.fontSize = fontSize
			
	def _getFontSize( self ):
		for pyCol in self.pyCols_:
			return pyCol.fontSize


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyCols = property( _getCols )													# ��ȡ��������
	foreColor = property( _getForeColor, _setForeColor )							# ��ȡ/���õ�ǰǰ��ɫ

	commonForeColor = property( _getCommonForeColor, _setCommonForeColor )			# ��ȡ/������ͨ״̬�µ�ǰ��ɫ
	highlightForeColor = property( _getHighlightForeColor, _setHighlightForeColor ) # ��ȡ/���ø���״̬�µ�ǰ��ɫ
	selectedForeColor = property( _getSelectedForeColor, _setSelectedForeColor )	# ��ȡ/����ѡ��״̬�µ�ǰ��ɫ
	disableForeColor = property( _getDisableForeColor, _setDisableForeColor )		# ��ȡ/������Ч״̬�µ�ǰ��ɫ
	
	fontSize = property( _getFontSize, _setFontSize )								# ��ȡ/����������Ĵ�С


# --------------------------------------------------------------------
# implement text column
# --------------------------------------------------------------------
class ODTextColumn( StaticText ) :
	def __init__( self, pyViewItem, text = "" ) :
		StaticText.__init__( self, None, pyViewItem )
		pyViewItem.onMouseMove.bind( self.__onBinderMouseMove, True )
		pyViewItem.moveFocus = True
		self.__text = ""
		self.__maxWidth = self.textWidth()
		self.__isMouseIn = False


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onBinderMouseMove( self, dx, dy ) :
		if self.isMouseHit() :
			if not self.__isMouseIn :
				self.__isMouseIn = True
				self.__onMouseEnter()
		else :
			if self.__isMouseIn :
				self.__isMouseIn = False
				self.__onMouseLeave()

	def __onMouseEnter( self ) :
		if self.__text != StaticText._getText( self ) :
			toolbox.infoTip.showToolTips( self, self.__text )

	def __onMouseLeave( self ) :
		toolbox.infoTip.hide( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getText( self ) :
		return self.__text

	def _setText( self, text ) :
		self.__text = text
		text, wtext = self.elideText( self.__maxWidth, "CUT", text )
		StaticText._setText( self, text )

	# -------------------------------------------------
	def _getMaxWidth( self ) :
		return self.__maxWidth

	def _setMaxWidth( self, width ) :
		self.__maxWidth = width


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )
	maxWidth = property( _getMaxWidth, _setMaxWidth )

# -*- coding: gb18030 -*-
#
# $Id: TipWindow.py,v 1.3 2008-08-26 02:21:39 huangyongwei Exp $

"""
implement information tips window

-- 2008/08/12 : writen by huangyongwei
			    named TipWindow
			    支持多列

-- 2008/09/28 : modified by huangyongwei
			    named ItemTip
			    改为仅支持两列（仅适应物品提示）
"""

from guis import *
from guis.common.PyGUI import PyGUI
from guis.tooluis.CSRichText import CSRichText
from TipWindow import TipWindow

class Grid :
	"""
	格子模板
	"""
	def __init__( self, text, tpl = None ) :
		self.text = text
		self.align = None						# 文本的水平对齐方式
		self.lineFlat = None					# 文本的垂直对其方式
		self.newline = None						# 文本是否强制换行（如果为 False，则在 maxWidth 内是不会换行的，当然如果超出了 maxWidth 还是会自动换行）
		if tpl : self.__dict__.update( tpl )


# --------------------------------------------------------------------
# implement ItemTip class
# --------------------------------------------------------------------
class ItemTip( TipWindow ) :
	__cg_splitter = GUI.load( "guis/tooluis/infotip/splitter.gui" )

	__cc_col_spacing		= 16.0						# 列间距
	__cc_minWidth = 195.0

	__cg_pyRichPool = []								# CSRichText 对象池
	__cg_pySPPool = []									# 分隔条对象池


	def __init__( self ) :
		TipWindow.__init__( self )
		self.__grids = []								# 保存每个格子的文本[( 第一列文本，第二列文本 ), ( 第一列文本，第二列文本 ), ...]
		self.__pySplitters = {}							# 分隔条{ 行号 : 对应行号后面的分隔条, ...}
		self.__typeseted = False						# 是否已经排版

		self.__minWidth = self.__cc_minWidth			# 窗口的最小宽度（-1 表示没有最小宽度）
		self.__lMaxWidth = -1							# 左边列的最大宽度（-1 表示没有最大宽度限制）
		self.__rMaxWidth = -1							# 有边列的最大宽度（-1 表示没有最大宽度限制）

		self.__tmpWidth = -1							# 窗口宽度


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getSplitter( self ) :
		"""
		从对象池中获取一个分隔条，如果对象池中不存在，则创建一个
		"""
		if len( self.__cg_pySPPool ) :
			pySplitter = self.__cg_pySPPool.pop()
		else :
			splitter = util.copyGuiTree( ItemTip.__cg_splitter )
			pySplitter = PyGUI( splitter )
		self.addPyChild( pySplitter )
		pySplitter.left = self.cc_edge_width_
		return pySplitter

	def __getGrid( self, ginfo ) :
		"""
		获取一个格子
		"""
		if ginfo == "" : return None
		grid = ginfo
		if not isinstance( ginfo, Grid ) :
			grid = Grid( ginfo )
		if grid.text == "" : return None
		if hasattr( grid, "pyRich" ) :
			del grid.pyRich
		if len( self.__cg_pyRichPool ) :
			pyRich = self.__cg_pyRichPool.pop()
		else :
			pyRich = CSRichText()
		self.addPyChild( pyRich )
		grid.pyRich = pyRich
		return grid

	# -------------------------------------------------
	def __calcMaxWidth( self ) :
		"""
		计算最大宽度
		"""
		if not len( self.__grids ) : return -1									# 全空文本
		dblcols = 0																# 是否是双列
		for lgrid, rgrid in self.__grids :
			if lgrid is None : continue											# 正行都为空文本
			# 单列文本
			if rgrid is None :													# 只有一列文本时
				if lgrid.newline == False :										# 不允许该列文本则窗口的最大范围内自动换行
					pyRich = lgrid.pyRich
					if self.__lMaxWidth > 0 and self.__rMaxWidth > 0 :			# 如果设置了窗口的最大宽度
						mwidth = self.__lMaxWidth + self.__rMaxWidth			# 窗口的最大宽度
						pyRich.autoNewline = True
						pyRich.maxWidth = mwidth								# 设置 CSRichText 的最大宽度为窗口的最大宽度
					else :														# 如果没有设置窗口的最大宽度
						pyRich.autoNewline = False								# 将 CSRichText 设置为不自动换行
					pyRich.text = lgrid.text
					self.__tmpWidth = max( self.__tmpWidth, pyRich.width )		# 窗口的宽度
				continue

			# 双列文本
			dblcols = 1
			if self.__lMaxWidth > 0 :											# 已经设置了左列最大宽度
				lgrid.pyRich.autoNewline = True
				lgrid.pyRich.maxWidth = self.__lMaxWidth						# 则，左列的 CSRichText 有最大宽度
			else :
				lgrid.pyRich.autoNewline = False								# 否则，左列不自动换行
			lgrid.pyRich.text = lgrid.text										# 设置左列文本
			if self.__rMaxWidth > 0 :											# 已经设置了右列最大宽度
				rgrid.pyRich.autoNewline = True
				rgrid.pyRich.maxWidth = self.__rMaxWidth						# 则，右列的 CSRichText 有最大宽度
			else :
				rgrid.pyRich.autoNewline = False								# 否则，右列不自动换行
			rgrid.pyRich.text = rgrid.text										# 设置右列文本

			lwidth = lgrid.pyRich.width											# 左边列宽度
			rwidth = rgrid.pyRich.width											# 右边列宽度
			width = lwidth + rwidth + self.__cc_col_spacing						# 整行宽度
			self.__tmpWidth = max( self.__tmpWidth, width )						# 保存整个窗口的宽度

		if self.__tmpWidth < 0 :												# 如果最终发现窗口宽度没有被设置（则肯定只有一列）
			count = 0
			for lgrid, rgrid in self.__grids :									# 则意味着只有一列文本
				if lgrid is None :
					count += 1
				else :
					lgrid.newline = False										# 将所有行设置为不自动换行
			if count < len( self.__grids ) :
				self.__calcMaxWidth()											# 重新计算一遍

		if dblcols == 1 and self.__tmpWidth < self.__minWidth :					# 如果设置了窗口最小宽度
			self.__tmpWidth = self.__minWidth									# 则最终宽度等于最小宽度
		return dblcols

	def __layoutSingleCol( self ) :
		"""
		对单列提示文本排版
		"""
		top = self.cc_edge_width_												# 当前行的顶部距离
		for row in xrange( len( self.__grids ) ) :
			lgrid, rgrid = self.__grids[row]
			if lgrid is None : continue
			pyRich = lgrid.pyRich
			if lgrid.align == "R" :												# 文本靠左
				pyRich.right = self.cc_edge_width_ + self.__tmpWidth
			elif lgrid.align == "C" :											# 文本局中
				pyRich.center = self.cc_edge_width_ + self.__tmpWidth / 2
			else :																# 文本靠右
				pyRich.left = self.cc_edge_width_
			pyRich.top = top
			top = pyRich.bottom
			pySP = self.__pySplitters.get( row + 1, None )
			if pySP :															# 有分割条
				pySP.top = top
				top = pySP.bottom
				pySP.width = self.__tmpWidth
		self.width = self.cc_edge_width_ * 2 + self.__tmpWidth
		self.height = top + self.cc_edge_width_

	def __layoutDoubleCol( self ) :
		"""
		对双列提示文本排版
		"""
		top = self.cc_edge_width_												# 当前行的顶部距离
		for row in xrange( len( self.__grids ) ) :
			lgrid, rgrid = self.__grids[row]
			if lgrid is None : continue											# 空列
			if rgrid is None :													# 只有一列
				pyRich = lgrid.pyRich
				if lgrid.newline != False :										# 自动换行
					pyRich.autoNewline = True
					pyRich.maxWidth = self.__tmpWidth
					pyRich.text = lgrid.text
				if lgrid.align == "R" :											# 文本靠左
					pyRich.right = self.cc_edge_width_ + self.__tmpWidth
				elif lgrid.align == "C" :										# 文本居中
					pyRich.center = self.cc_edge_width_ + self.__tmpWidth / 2
				else :
					pyRich.left = self.cc_edge_width_
				pyRich.top = top
				top = pyRich.bottom
			else :																# 两列都有文本
				pyLRich, pyRRich = lgrid.pyRich, rgrid.pyRich
				# 设置列的水平位置
				pyLRich.left = self.cc_edge_width_								# 如果两列都有文本，则左边列固定靠左
				pyRRich.right = self.cc_edge_width_ + self.__tmpWidth			# 右边列固定靠右

				# 设置列的垂直方向位置
				if pyLRich.height == pyRRich.height :							# 该行的两列的高度一样
					pyLRich.top = pyRRich.top = top
					top = pyLRich.bottom
				elif pyLRich.height > pyRRich.height :							# 该行的第一列高于第二列
					pyLRich.top = top
					top = pyLRich.bottom
					if pyRRich.lineFlat == "T" :								# 设置为顶部对齐
						pyRRich.top = pyLRich.top
					elif pyRRich.lineFlat == "M" :								# 设置为中间对齐
						pyRRich.middle = pyLRich.middle
					else :														# 默认是底部对齐
						pyRRich.bottom = top
				else :															# 该行的第二列高于第一列
					pyRRich.top = top
					top = pyRRich.bottom
					if pyLRich.lineFlat == "T" :								# 设置为顶部对齐
						pyLRich.top = pyRRich.top
					elif pyLRich.lineFlat == "M" :								# 设置为中间对齐
						pyLRich.middle = pyRRich.middle
					else :														# 默认是底部对齐
						pyLRich.bottom = top
			pySP = self.__pySplitters.get( row + 1, None )
			if pySP :															# 有分割条
				pySP.top = top
				top = pySP.bottom
				pySP.width = self.__tmpWidth
		self.width = self.cc_edge_width_ * 2 + self.__tmpWidth
		self.height = top + self.cc_edge_width_


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setTemplate( self, tpl ) :
		"""
		设置模板
		"""
		self.__minWidth = tpl.get( "minWidth", self.__cc_minWidth )
		self.__lMaxWidth = tpl.get( "lMaxWidth", -1 )
		self.__rMaxWidth = tpl.get( "rMaxWidth", -1 )

	# -------------------------------------------------
	def appendRow( self, rowGrids, typeset = False ) :
		"""
		追加一行文本
		@type				rowGrids : Grid
		@param				rowGrids : 文本行信息: ( 第一列文本，第二列文本 )
		@type				typeset : bool
		@param				typeset : 是否排版
		"""
		row = len( self.__grids )								# 新添加行行号
		gtype = type( rowGrids )								# 传入的行内容
		lgrid, rgrid = None, None								# 第一第二列
		if gtype is str or gtype is unicode :					# 如果只有一列字符串文本
			lgrid = self.__getGrid( rowGrids )					# 创建一个格子
			if lgrid is not None :
				self.__grids.append( ( lgrid, rgrid ) )
		elif isinstance( rowGrids, Grid ) :						# 只有一列，并且传入的是 grid
			lgrid = self.__getGrid( rowGrids )
			if lgrid is not None :
				self.__grids.append( ( rowGrids, rgrid ) )
		elif len( rowGrids ) > 0 :								# 如果传入的只有一列文本，但以单元素链表表示
			lgrid = self.__getGrid( rowGrids[0] )
			if len( rowGrids ) > 1 :							# 如果有两列文本
				rgrid = self.__getGrid( rowGrids[1] )
			if lgrid is None :									# 如果左边列为空
				lgrid = rgrid									# 则将右边列挪到左边
				rgrid = None									# 并清除右边列
			if lgrid is not None :
				self.__grids.append( ( lgrid, rgrid ) )			# 追加一行文本
		else :													# 其他情况，当其意图为插入一个分割条
			self.__pySplitters[row] = self.__getSplitter()		# 则表示增加一个分隔条

		if typeset : self.typeset()
		else : self.__typeseted = False

	def setItemInfo( self, grids, typeset = False ) :
		"""
		设置一组物品信息
		@type				grids	: list
		@param				grids	: 信息文本：[( 第一列，第二列 ), ( 第一列，第二列 ), ...]
		@type				typeset : bool
		@param				typeset : 是否马上排版
		"""
		if type( grids ) is str or \
			type( grids ) is unicode :
				self.appendRow( grids )
		else :
			for rowGrids in grids :
				self.appendRow( rowGrids )
		if typeset : self.typeset()
		else : self.__typeseted = False

	def setGridText( self, row, col, text, typeset = True ) :
		"""
		设置指定格子的文本
		@type				row		: int
		@param				row		: 行号
		@type				col		: int
		@param				col		: 列号（最多两列）
		@type				text	: Grid / Text
		@param				text	: 格子或文本
		@type				typeset : bool
		@param				typeset : 是否排版
		"""
		if row < 0 or col < 0 :
			raise IndexError( "Error row or column index!" )
		if row >= len( self.__grids ) :
			raise IndexError( "row index out of range! it must be less then %i." % len( self.__grids ) - 1 )
		if col > 1 :
			raise IndexError( "column index out of range! it must be less then 2." )
		grid = self.__grids[row][col]
		if grid is None :
			grid = self.__getGrid( text )
			self.__grids[row][col] = grid
		elif text != "" :
			grid.text = text
		else :
			if hasattr( grid, "pyRich" ) :
				self.delPyChild( grid.pyRich )
				grid.pyRich.clear()
				self.__cg_pyRichPool.append( grid.pyRich )
			self.__grids[row][col] = None

		lgrid, rgrid = self.__grids[row]
		if lgrid is None :
			self.__grids[row] = [rgrid, None]

		self.__typeseted = False
		if typeset : self.typeset()

	# -------------------------------------------------
	def typeset( self ) :
		"""
		排版
		"""
		res = self.__calcMaxWidth()									# 计算窗口宽度
		if res < 0 : return											# 没有任何文本信息
		elif res == 0 : self.__layoutSingleCol()					# 只有一列文本的排版
		else : self.__layoutDoubleCol()								# 有两列文本的排版
		self.__typeseted = True										# 设置为已经排版

	def clear( self ) :
		"""
		清除所有文本
		"""
		for rowGrids in self.__grids :
			for rgrid in rowGrids :
				pyRich = getattr( rgrid, "pyRich", None )			# 挂在 rgrid 上的 richtext
				if pyRich is None : continue
				self.delPyChild( pyRich )							# 释放一个格子
				pyRich.clear()
				self.__cg_pyRichPool.append( pyRich )				# 回收所有 CSRichText 控件
		self.__grids = []											# 清空缓存中的文本
		self.__cg_pySPPool += self.__pySplitters.values()			# 回收所有分隔条
		self.__pySplitters.clear()									# 清除分隔条
		self.__minWidth = self.__cc_minWidth						# 恢复为没有最小宽度限制
		self.__lMaxWidth = -1										# 恢复为没有最大宽度
		self.__rMaxWidth = -1										# 恢复为没有最大宽度
		self.__tmpWidth = -1										# 恢复窗口宽度为 0
		self.__typeseted = False									# 清除排版标记

	# -------------------------------------------------
	def show( self, pyBinder ) :
		if len( self.__grids ) == 0 :
			return
		if not self.__typeseted :
			self.typeset()
		TipWindow.show( self, pyBinder )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getMinWidth( self ) :
		return self.__minWidth

	def _setMinWidth( self, width ) :
		self.__minWidth = width

	def _getLMaxWidth( self ) :
		return self.__lMaxWidth

	def _setLMaxWidth( self, width ) :
		self.__rMaxWidth = width

	def _getRMaxWidth( self ) :
		return self.__rMaxWidth

	def _setRMaxWidth( self, width ) :
		self.__rMaxWidth = width

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	minWidth = property( _getMinWidth, _setMinWidth )
	lMaxWidth = property( _getLMaxWidth, _setLMaxWidth )
	rMaxWidth = property( _getRMaxWidth, _setRMaxWidth )


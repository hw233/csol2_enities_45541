# -*- coding: gb18030 -*-
#
# $Id: TipWindow.py,v 1.3 2008-08-26 02:21:39 huangyongwei Exp $

"""
implement information tips window

-- 2008/08/12 : writen by huangyongwei
			    named TipWindow
			    ֧�ֶ���

-- 2008/09/28 : modified by huangyongwei
			    named ItemTip
			    ��Ϊ��֧�����У�����Ӧ��Ʒ��ʾ��
"""

from guis import *
from guis.common.PyGUI import PyGUI
from guis.tooluis.CSRichText import CSRichText
from TipWindow import TipWindow

class Grid :
	"""
	����ģ��
	"""
	def __init__( self, text, tpl = None ) :
		self.text = text
		self.align = None						# �ı���ˮƽ���뷽ʽ
		self.lineFlat = None					# �ı��Ĵ�ֱ���䷽ʽ
		self.newline = None						# �ı��Ƿ�ǿ�ƻ��У����Ϊ False������ maxWidth ���ǲ��ỻ�еģ���Ȼ��������� maxWidth ���ǻ��Զ����У�
		if tpl : self.__dict__.update( tpl )


# --------------------------------------------------------------------
# implement ItemTip class
# --------------------------------------------------------------------
class ItemTip( TipWindow ) :
	__cg_splitter = GUI.load( "guis/tooluis/infotip/splitter.gui" )

	__cc_col_spacing		= 16.0						# �м��
	__cc_minWidth = 195.0

	__cg_pyRichPool = []								# CSRichText �����
	__cg_pySPPool = []									# �ָ��������


	def __init__( self ) :
		TipWindow.__init__( self )
		self.__grids = []								# ����ÿ�����ӵ��ı�[( ��һ���ı����ڶ����ı� ), ( ��һ���ı����ڶ����ı� ), ...]
		self.__pySplitters = {}							# �ָ���{ �к� : ��Ӧ�кź���ķָ���, ...}
		self.__typeseted = False						# �Ƿ��Ѿ��Ű�

		self.__minWidth = self.__cc_minWidth			# ���ڵ���С��ȣ�-1 ��ʾû����С��ȣ�
		self.__lMaxWidth = -1							# ����е�����ȣ�-1 ��ʾû����������ƣ�
		self.__rMaxWidth = -1							# �б��е�����ȣ�-1 ��ʾû����������ƣ�

		self.__tmpWidth = -1							# ���ڿ��


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getSplitter( self ) :
		"""
		�Ӷ�����л�ȡһ���ָ��������������в����ڣ��򴴽�һ��
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
		��ȡһ������
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
		���������
		"""
		if not len( self.__grids ) : return -1									# ȫ���ı�
		dblcols = 0																# �Ƿ���˫��
		for lgrid, rgrid in self.__grids :
			if lgrid is None : continue											# ���ж�Ϊ���ı�
			# �����ı�
			if rgrid is None :													# ֻ��һ���ı�ʱ
				if lgrid.newline == False :										# ����������ı��򴰿ڵ����Χ���Զ�����
					pyRich = lgrid.pyRich
					if self.__lMaxWidth > 0 and self.__rMaxWidth > 0 :			# ��������˴��ڵ������
						mwidth = self.__lMaxWidth + self.__rMaxWidth			# ���ڵ������
						pyRich.autoNewline = True
						pyRich.maxWidth = mwidth								# ���� CSRichText �������Ϊ���ڵ������
					else :														# ���û�����ô��ڵ������
						pyRich.autoNewline = False								# �� CSRichText ����Ϊ���Զ�����
					pyRich.text = lgrid.text
					self.__tmpWidth = max( self.__tmpWidth, pyRich.width )		# ���ڵĿ��
				continue

			# ˫���ı�
			dblcols = 1
			if self.__lMaxWidth > 0 :											# �Ѿ����������������
				lgrid.pyRich.autoNewline = True
				lgrid.pyRich.maxWidth = self.__lMaxWidth						# �����е� CSRichText �������
			else :
				lgrid.pyRich.autoNewline = False								# �������в��Զ�����
			lgrid.pyRich.text = lgrid.text										# ���������ı�
			if self.__rMaxWidth > 0 :											# �Ѿ����������������
				rgrid.pyRich.autoNewline = True
				rgrid.pyRich.maxWidth = self.__rMaxWidth						# �����е� CSRichText �������
			else :
				rgrid.pyRich.autoNewline = False								# �������в��Զ�����
			rgrid.pyRich.text = rgrid.text										# ���������ı�

			lwidth = lgrid.pyRich.width											# ����п��
			rwidth = rgrid.pyRich.width											# �ұ��п��
			width = lwidth + rwidth + self.__cc_col_spacing						# ���п��
			self.__tmpWidth = max( self.__tmpWidth, width )						# �����������ڵĿ��

		if self.__tmpWidth < 0 :												# ������շ��ִ��ڿ��û�б����ã���϶�ֻ��һ�У�
			count = 0
			for lgrid, rgrid in self.__grids :									# ����ζ��ֻ��һ���ı�
				if lgrid is None :
					count += 1
				else :
					lgrid.newline = False										# ������������Ϊ���Զ�����
			if count < len( self.__grids ) :
				self.__calcMaxWidth()											# ���¼���һ��

		if dblcols == 1 and self.__tmpWidth < self.__minWidth :					# ��������˴�����С���
			self.__tmpWidth = self.__minWidth									# �����տ�ȵ�����С���
		return dblcols

	def __layoutSingleCol( self ) :
		"""
		�Ե�����ʾ�ı��Ű�
		"""
		top = self.cc_edge_width_												# ��ǰ�еĶ�������
		for row in xrange( len( self.__grids ) ) :
			lgrid, rgrid = self.__grids[row]
			if lgrid is None : continue
			pyRich = lgrid.pyRich
			if lgrid.align == "R" :												# �ı�����
				pyRich.right = self.cc_edge_width_ + self.__tmpWidth
			elif lgrid.align == "C" :											# �ı�����
				pyRich.center = self.cc_edge_width_ + self.__tmpWidth / 2
			else :																# �ı�����
				pyRich.left = self.cc_edge_width_
			pyRich.top = top
			top = pyRich.bottom
			pySP = self.__pySplitters.get( row + 1, None )
			if pySP :															# �зָ���
				pySP.top = top
				top = pySP.bottom
				pySP.width = self.__tmpWidth
		self.width = self.cc_edge_width_ * 2 + self.__tmpWidth
		self.height = top + self.cc_edge_width_

	def __layoutDoubleCol( self ) :
		"""
		��˫����ʾ�ı��Ű�
		"""
		top = self.cc_edge_width_												# ��ǰ�еĶ�������
		for row in xrange( len( self.__grids ) ) :
			lgrid, rgrid = self.__grids[row]
			if lgrid is None : continue											# ����
			if rgrid is None :													# ֻ��һ��
				pyRich = lgrid.pyRich
				if lgrid.newline != False :										# �Զ�����
					pyRich.autoNewline = True
					pyRich.maxWidth = self.__tmpWidth
					pyRich.text = lgrid.text
				if lgrid.align == "R" :											# �ı�����
					pyRich.right = self.cc_edge_width_ + self.__tmpWidth
				elif lgrid.align == "C" :										# �ı�����
					pyRich.center = self.cc_edge_width_ + self.__tmpWidth / 2
				else :
					pyRich.left = self.cc_edge_width_
				pyRich.top = top
				top = pyRich.bottom
			else :																# ���ж����ı�
				pyLRich, pyRRich = lgrid.pyRich, rgrid.pyRich
				# �����е�ˮƽλ��
				pyLRich.left = self.cc_edge_width_								# ������ж����ı���������й̶�����
				pyRRich.right = self.cc_edge_width_ + self.__tmpWidth			# �ұ��й̶�����

				# �����еĴ�ֱ����λ��
				if pyLRich.height == pyRRich.height :							# ���е����еĸ߶�һ��
					pyLRich.top = pyRRich.top = top
					top = pyLRich.bottom
				elif pyLRich.height > pyRRich.height :							# ���еĵ�һ�и��ڵڶ���
					pyLRich.top = top
					top = pyLRich.bottom
					if pyRRich.lineFlat == "T" :								# ����Ϊ��������
						pyRRich.top = pyLRich.top
					elif pyRRich.lineFlat == "M" :								# ����Ϊ�м����
						pyRRich.middle = pyLRich.middle
					else :														# Ĭ���ǵײ�����
						pyRRich.bottom = top
				else :															# ���еĵڶ��и��ڵ�һ��
					pyRRich.top = top
					top = pyRRich.bottom
					if pyLRich.lineFlat == "T" :								# ����Ϊ��������
						pyLRich.top = pyRRich.top
					elif pyLRich.lineFlat == "M" :								# ����Ϊ�м����
						pyLRich.middle = pyRRich.middle
					else :														# Ĭ���ǵײ�����
						pyLRich.bottom = top
			pySP = self.__pySplitters.get( row + 1, None )
			if pySP :															# �зָ���
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
		����ģ��
		"""
		self.__minWidth = tpl.get( "minWidth", self.__cc_minWidth )
		self.__lMaxWidth = tpl.get( "lMaxWidth", -1 )
		self.__rMaxWidth = tpl.get( "rMaxWidth", -1 )

	# -------------------------------------------------
	def appendRow( self, rowGrids, typeset = False ) :
		"""
		׷��һ���ı�
		@type				rowGrids : Grid
		@param				rowGrids : �ı�����Ϣ: ( ��һ���ı����ڶ����ı� )
		@type				typeset : bool
		@param				typeset : �Ƿ��Ű�
		"""
		row = len( self.__grids )								# ��������к�
		gtype = type( rowGrids )								# �����������
		lgrid, rgrid = None, None								# ��һ�ڶ���
		if gtype is str or gtype is unicode :					# ���ֻ��һ���ַ����ı�
			lgrid = self.__getGrid( rowGrids )					# ����һ������
			if lgrid is not None :
				self.__grids.append( ( lgrid, rgrid ) )
		elif isinstance( rowGrids, Grid ) :						# ֻ��һ�У����Ҵ������ grid
			lgrid = self.__getGrid( rowGrids )
			if lgrid is not None :
				self.__grids.append( ( rowGrids, rgrid ) )
		elif len( rowGrids ) > 0 :								# ��������ֻ��һ���ı������Ե�Ԫ�������ʾ
			lgrid = self.__getGrid( rowGrids[0] )
			if len( rowGrids ) > 1 :							# ����������ı�
				rgrid = self.__getGrid( rowGrids[1] )
			if lgrid is None :									# ��������Ϊ��
				lgrid = rgrid									# ���ұ���Ų�����
				rgrid = None									# ������ұ���
			if lgrid is not None :
				self.__grids.append( ( lgrid, rgrid ) )			# ׷��һ���ı�
		else :													# ���������������ͼΪ����һ���ָ���
			self.__pySplitters[row] = self.__getSplitter()		# ���ʾ����һ���ָ���

		if typeset : self.typeset()
		else : self.__typeseted = False

	def setItemInfo( self, grids, typeset = False ) :
		"""
		����һ����Ʒ��Ϣ
		@type				grids	: list
		@param				grids	: ��Ϣ�ı���[( ��һ�У��ڶ��� ), ( ��һ�У��ڶ��� ), ...]
		@type				typeset : bool
		@param				typeset : �Ƿ������Ű�
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
		����ָ�����ӵ��ı�
		@type				row		: int
		@param				row		: �к�
		@type				col		: int
		@param				col		: �кţ�������У�
		@type				text	: Grid / Text
		@param				text	: ���ӻ��ı�
		@type				typeset : bool
		@param				typeset : �Ƿ��Ű�
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
		�Ű�
		"""
		res = self.__calcMaxWidth()									# ���㴰�ڿ��
		if res < 0 : return											# û���κ��ı���Ϣ
		elif res == 0 : self.__layoutSingleCol()					# ֻ��һ���ı����Ű�
		else : self.__layoutDoubleCol()								# �������ı����Ű�
		self.__typeseted = True										# ����Ϊ�Ѿ��Ű�

	def clear( self ) :
		"""
		��������ı�
		"""
		for rowGrids in self.__grids :
			for rgrid in rowGrids :
				pyRich = getattr( rgrid, "pyRich", None )			# ���� rgrid �ϵ� richtext
				if pyRich is None : continue
				self.delPyChild( pyRich )							# �ͷ�һ������
				pyRich.clear()
				self.__cg_pyRichPool.append( pyRich )				# �������� CSRichText �ؼ�
		self.__grids = []											# ��ջ����е��ı�
		self.__cg_pySPPool += self.__pySplitters.values()			# �������зָ���
		self.__pySplitters.clear()									# ����ָ���
		self.__minWidth = self.__cc_minWidth						# �ָ�Ϊû����С�������
		self.__lMaxWidth = -1										# �ָ�Ϊû�������
		self.__rMaxWidth = -1										# �ָ�Ϊû�������
		self.__tmpWidth = -1										# �ָ����ڿ��Ϊ 0
		self.__typeseted = False									# ����Ű���

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


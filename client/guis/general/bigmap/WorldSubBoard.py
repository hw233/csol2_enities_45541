# -*- coding: gb18030 -*-
#
# $Id: WorldArea.py,v 1.28 2008-08-27 09:04:26 huangyongwei Exp $

"""
implement sub area of the world map

2009.09.27 : wirten by huangyongwei
"""

from cscustom import Polygon
from guis import *
from guis.common.ScriptObject import ScriptObject

class WorldSubBoard( ScriptObject ) :
	__cg_pyBoards = []							# �������а��
	__cg_pySelBoard = None						# ��ǰ���ѡ�еİ��
	__cg_lastHitCount = 0						# �����а�������

	def __init__( self, board ) :
		if len( WorldSubBoard.__cg_pyBoards ) == 0 :					# ��ֻ֤���һ��
			LastMouseEvent.attach( WorldSubBoard.__onLastMouseEvent )	# �������ƶ��¼������������λ��
		WorldSubBoard.__cg_pyBoards.append( self )						# ���浹����б���
		gui = GUI.Simple( "" )
		ScriptObject.__init__( self, gui )
		self.setToDefault()
		gui.size = board.size
		util.setGuiState( gui )
		self.focus = True
		self.__board = board											# MapMgr.WorldArea.SubBoard
		self.__polygon = Polygon( board.polygon.points )				# ���򶥵�

	def __del__( self ) :
		ScriptObject.__del__( self )
		if Debug.output_del_BigMapWorldSubBoard :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		if len( WorldSubBoard.__cg_pyBoards ) :						# ��ֻ֤ɾ��һ��
			LastMouseEvent.detach( self.__onLastMouseEvent )		# ȡ������ƶ��¼�
		WorldSubBoard.__cg_pyBoards = []							# ������а��
		WorldSubBoard.__cg_pySelBoard = None						# ȥ��ѡ�а�������
		ScriptObject.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __onLastMouseEvent( dx, dy, dz ) :
		"""
		����ڰ�ť�ϲ��ƶ�ʱ����
		"""
		pySelBoard = WorldSubBoard.__cg_pySelBoard
		pyHitedBoards = []
		for pyBoard in WorldSubBoard.__cg_pyBoards :
			if pyBoard.isMouseHit() :
				pyHitedBoards.append( pyBoard )
		oldCount = WorldSubBoard.__cg_lastHitCount
		count = len( pyHitedBoards )							# �����а������
		WorldSubBoard.__cg_lastHitCount = count
		if count == 0 :											# ���û�л����κΰ��
			if pySelBoard :
				pySelBoard.onMouseLeave_()
		elif count == 1 :
			pyBoard = pyHitedBoards[0]
			if pyBoard == pySelBoard :							# ���ֻ�ڵ�ǰѡ�а����
				return
			if pySelBoard :
				pySelBoard.onMouseLeave_()
			pyBoard.onMouseEnter_()
		else :													# �����ж�����
			if oldCount < count and \
				pySelBoard in pyHitedBoards :					# ����һ�������������ı߽�
					pyHitedBoards.remove( pySelBoard )			# �����°����Ϊѡ�а��(��ֹ���ص����ʱ������ڱ߽�ʱ�����ǻ��й̶���һ�����)
			if pySelBoard in pyHitedBoards :
				return
			if pySelBoard :
				pySelBoard.onMouseLeave_()
			pyHitedBoards[0].onMouseEnter_()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		ScriptObject.onMouseEnter_( self )
		self.texture = self.__board.texture
		WorldSubBoard.__cg_pySelBoard = self

	def onMouseLeave_( self ) :
		ScriptObject.onMouseLeave_( self )
		self.texture = ""
		WorldSubBoard.__cg_pySelBoard = None

	def onLClick_( self, mods ) :
		pySelBoard = WorldSubBoard.__cg_pySelBoard
		if pySelBoard :											# �����ϣ��ܲ����� None
			ScriptObject.onLClick_( pySelBoard, mods )
		return True


	# -------------------------------------------------
	# rewrite method
	# -------------------------------------------------
	def isMouseHit( self ) :
		"""
		��дisMouseHit�������ж�����Ƿ����ڶ������
		"""
		return ScriptObject.isMouseHit( self ) and \
			self.__polygon.isPointIn( self.mousePos )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getScale( self ) :
		return self.__scale

	def _setScale( self, scale ) :
		self.__scale = scale
		self.size = scale * self.__board.size
		self.pos = scale * self.__board.pos
		points = self.__board.polygon.points
		self.__polygon.update( [p * scale for p in points] )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	scale = property( _getScale, _setScale )
	area = property( lambda self : self.__board.area )

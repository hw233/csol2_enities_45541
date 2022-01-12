# -*- coding: gb18030 -*-
#
# $Id: DragObject.py,v 1.6 2008-08-26 02:12:34 huangyongwei Exp $

"""
implement dragitem class
2005/08/10: wirten by huangyongwei( DragItem )
2008/01/24: renamed by huangyongwei( DragObject )
"""
"""
composing :
	the same as the source dragged
"""

import weakref
from guis import *
from AbstractTemplates import Singleton
from RootGUI import RootGUI

class DragObject( Singleton, RootGUI ) :
	def __init__( self ) :
		item = GUI.Simple( "" )							# ����һ��Ĭ�ϵ� UI
		RootGUI.__init__( self, item )					# �ص����๹�캯��
		self.posZSegment = ZSegs.L2						# ����Ϊ�������еڶ���
		self.activable_ = False							# �����Ա�����
		self.hitable_ = False							# ����ס���
		self.escHide_ = False							# �����԰� ESC ������

		self.__attach = None							# �ϷŸ��Ӷ��󣬿��������ϵ�ʱ������һ�����Ӷ���Ȼ���ڷ��µ�ʱ���ȡ�ö���
		self.__mouseInPos = ( 0, 0 )					# ��ʱ������������갴��ʱ������


	def dispose( self ) :
		self.release()
		RootGUI.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onLastKeyUp( self, key, mods ) :
		"""
		���������ʱ������
		"""
		if key == KEY_LEFTMOUSE :
			LastKeyUpEvent.detach( self.__onLastKeyUp )			# �ͷ���������¼�
			LastMouseEvent.detach( self.__onLastMouseEvent )	# ���������ƶ��¼�
			self.release()										# �ͷ��Ϸ� UI �ĸ���Ʒ

	def __onLastMouseEvent( self, dx, dy, dz ) :
		"""
		�������ƶ��¼�
		"""
		self.left += dx
		self.top += dy


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, pyDragged, dragMark ) :
		"""
		��ʾ�ϷŶ���
		"""
		def handle( newGui ) :									# �����ϷŶ�����Ʒ������
			newGui.focus = False								# �����Խ��հ����¼�
			newGui.dragFocus = False							# �����Խ����Ϸ��¼�
			newGui.dropFocus = False							# �����Խ����Ϸ��¼�
			newGui.moveFocus = False							# �����Խ�������ƶ��¼�
			newGui.crossFocus = False							# �����Խ����������¼�

		cpy = util.copyGuiTree( pyDragged.getGui(), handle )	# �����ϷŶ���
		self.resetBindingUI_( cpy )								# ���°� UI ����
		self.r_pos = pyDragged.r_posToScreen					# ���ø���Ʒ��λ��
		self.dragMark = dragMark								# �����Ϸű��
		LastKeyUpEvent.attach( self.__onLastKeyUp )				# ����������¼�
		LastMouseEvent.attach( self.__onLastMouseEvent )		# ���������ƶ��¼�
		RootGUI.show( self )									# ��ʾ�ϷŶ���ĸ���Ʒ

	def release( self ) :
		"""
		ȡ���Ϸ�
		"""
		self.attach = None										# ��ո��Ӷ���
		self.dragMark = DragMark.NONE							# ����Ϸű��
		self.hide()												# �����Ϸ� UI ����


	# ----------------------------------------------------------------
	# property methonds
	# ----------------------------------------------------------------
	def _setVisible( self, isVisible ) :
		if not isVisible : self.release()

	# -------------------------------------------------
	def _getMouseInPos( self ) :
		return self.__mouseInPos

	def _setMouseInPos( self, pos ) :
		self.__mouseInPos = pos

	# -------------------------------------------------
	def _getAttach( self ) :
		if self.__attach is None :
			return None
		if type( self.__attach ) is weakref.ReferenceType :	# �������ö���
			return self.__attach()
		return self.__attach								# ��ǿ���ö���

	def _setAttach( self, attach ) :
		try :
			self.__attach = RefEx( attach )					# ���Բ�ȡ�����õ���ʹ��������
		except TypeError :
			self.__attach = attach							# ����ʹ��ǿ����


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	visible = property( RootGUI._getVisible, _setVisible )			# ��ȡ/�����ϷŸ���Ʒ�Ŀɼ���
	dragging = property( RootGUI._getVisible )						# ��ȡ�Ƿ����Ϸ�״̬
	mouseInPos = property( _getMouseInPos, _setMouseInPos )			# ��ȡ/��������Ϸ�ʱ�����ϷŶ����ϵ�����
	attach = property( _getAttach, _setAttach )						# �ϷŸ��Ӷ��󣬿��������ϵ�ʱ������һ�����Ӷ���Ȼ���ڷ��µ�ʱ���ȡ�ö���

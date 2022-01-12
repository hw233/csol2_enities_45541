# -*- coding: gb18030 -*-
# $Id: CursorMgr.py,v 1.8 2008-02-22 06:57:00 huangyongwei Exp $
#
"""
implement cursor manager

2008.09.12: writen by huangyongwei
"""

import GUI
import ResMgr
import csol
from bwdebug import *
from AbstractTemplates import Singleton

class CustomCursor( Singleton ) :
	def __init__( self ) :
		self.__mcursor = GUI.mcursor()
		self.__sect = ResMgr.openSection( "guis/otheruis/cursor/cursors.xml" )
		self.__locked = False						# �Ƿ�������꣬���������꣬����û����֮ǰ���������ö�����Ч��

		self.set( "normal" )						# Ĭ��Ϊ��ͨ���


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def hotSpot( self ) :
		"""
		���ָ���������ͼ�е�λ��
		"""
		return self.__sect[self.shape].readVector2( "hotSpot" )

	@property
	def downSpot( self ) :
		"""
		���������ʾ����С
		"""
		return self.__sect[self.shape].readVector2( "downSpot" )

	# ---------------------------------------
	@property
	def pos( self ) :
		"""
		�������Ļ�ϵ�λ�ã��������꣩
		"""
		return csol.pcursorPosition()

	@property
	def rpos( self ) :
		"""
		�������Ļ�ϵ�λ��(�������)
		"""
		return csol.rcursorPosition()

	@property
	def dpos( self ) :
		"""
		������½�λ��( �������� )
		"""
		x, y = self.pos
		dx, dy = self.downSpot
		hx, hy = self.hotSpot
		left = x + dx - hx
		bottom = y + dy - hy
		return left, bottom

	@property
	def rdpos( self ) :
		"""
		������½�λ��( ������� )
		"""
		dx, dy = self.dpos
		rright = 2 * ( dx / BigWorld.screenWidth() ) - 1
		rbottom = 1 - 2 * ( dy / BigWorld.screenHeight() )

	# -------------------------------------------------
	@property
	def shape( self ) :
		"""
		��ǰ�������
		"""
		name = self.__mcursor.shape
		if self.grayed : 						# ����ǻ�ɫ״̬
			return name[2:]						# ��ȥ����ɫ״̬ǰ׺
		return name

	@property
	def grayed( self ) :
		"""
		�Ƿ��ڻ�ɫ״̬
		"""
		return self.__mcursor.shape.startswith( "g_" )

	@property
	def locked( self ) :
		"""
		�Ƿ�������״̬
		"""
		return self.__locked


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def set( self, name, isGray = False ) :
		"""
		�������
		@type			name   : str
		@param			name   : �������
		@type			isGray : bool
		@param			isGray : �Ƿ�ʹ�û�ɫ״̬
		@rype				   : str
		@return				   : �����괦������״̬���򷵻� None�����򷵻ؾɵ��������
		"""
		assert self.__sect.has_key( name ), "error cursor name"
		if self.__locked : return None			# ��걻�������򷵻� None ��ʾ����ʧ��
		oleName = self.shape					# ��¼�¾ɵ��������
		self.__mcursor.shape = name				# ���������
		if isGray : self.gray()					# ����Ϊ��ɫ״̬
		else : self.degray()					# ����Ϊ�ǻ�ɫ״̬
		return oleName							# ���ؾ����

	# -------------------------------------------------
	def lock( self, shape, isGray = False ) :
		"""
		�������Ϊĳ����״
		ע�⣺���������һ����״��ס����꣬���������ʧ�ܣ�����⿪ǰ��һ����״����������������
		@type		shape : str
		@param		shape : Ҫ��������״
		@rtype			  : bool
		@return			  : ��������ǰ������״̬
		"""
		locked = self.__locked
		if locked : return locked
		self.set( shape, isGray )
		self.__locked = True
		return locked

	def unlock( self, shape, newShape = None ) :
		"""
		�������
		@type		shape	 : str
		@param		shape	 : Ҫ��������״�������ǰ������������״��������ʧ��
		@type		newShape : str
		@param		newShape : �����󣬻ظ�������״
		@rtype				 : bool
		@return				 : ��������ǰ������״̬
		"""
		locked = self.__locked
		if locked and shape != self.shape :
			return True
		self.__locked = False
		if newShape :
			self.set( newShape )
		return locked

	# -------------------------------------------------
	def gray( self ) :
		"""
		ʹ�����
		@rtype				 : bool
		@param				 : �ı�ɹ��Ļ����� True�����򷵻� False
		"""
		if self.__locked : return False			# ��걻�������򷵻�
		if self.grayed : return True			# ����Ѿ��ǻ�ɫ��꣬�����޸�
		name = "g_%s" % self.shape				# ��ȡ��ɫ�������
		if self.__sect.has_key( name ) :		# ������ڻ�ɫ��ͼ
			self.__mcursor.shape = name			# ������Ϊ��ɫ���
			return True							# ���������óɹ�
		return False

	def degray( self ) :
		"""
		������ɫ״̬
		"""
		if self.__locked : return False			# ��걻�������򷵻�
		if not self.grayed : return True		# �Ѿ����ڷǻ�ɫ״̬
		self.set( self.shape )					# �������ü���
		return True

	# -------------------------------------------------
	def normal( self, isGray = False ) :
		"""
		�������Ϊ��ͨģʽ
		@type			isGray : bool
		@param			isGray : �Ƿ�ʹ�û�ɫ״̬
		"""
		if self.__mcursor.shape == "normal" :
			return
		if self.__locked : return False			# ��걻�������򷵻�
		self.__mcursor.shape = "normal"
		if isGray : self.gray()
		return True

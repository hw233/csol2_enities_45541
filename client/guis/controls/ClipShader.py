# -*- coding: gb18030 -*-
#
# $Id: ClipShader.py,v 1.8 2008-06-21 01:46:57 huangyongwei Exp $

"""
implement alpha shader class

2007/3/18 : writen by huangyongwei
"""
"""
composing :
	GUI.Window
		-- clipper ( GUI.ClipShader )
"""

from guis import *
from guis.common.PyGUI import PyGUI

class ClipShader( object ) :
	"""
	�ü� Shader
	"""
	def __init__( self, gui ) :
		object.__init__( self )
		self.__initialize( gui )
		self.__clipMode = "RIGHT"								# �ü�ģʽ��"LEFT"��"RIGHT"��"TOP"��"BOTTOM"
		self.__value = 1										# �ü�Ĭ��ֵ
		self.__speed = 1										# �ü��ٶ�

		self.__perClipValue = 1.0								# ��ʱ����������ÿһ tick Ӧ�ò��е� value ֵ
		self.__clipCBID = 0										# ���е� callback ID

	def subclass( self, gui ) :
		self.__initialize( gui )
		return self

	def __del__( self ) :
		self.__stopClipping()
		self.__gui = None
		if Debug.output_del_ClipShader :
			INFO_MSG( str( self ) )

	# ---------------------------------------
	def __initialize( self, gui ) :
		if isDebuged :
			assert gui.size[0] > 0 and gui.size[1] > 0, "the ui's size clip shader attach to must large than 0!"
		self.__gui = gui
		self.__defMapping = gui.mapping											# UI ��ԭʼ mapping
		self.__defMapBound = util.getGuiMappingBound( gui.size, gui.mapping ) 	# UI ��ԭʼ mapping Bound
		self.__defSize = tuple( gui.size )										# UI ��ԭʼ��С
		self.__defPos = s_util.getGuiPos( gui )									# UI ��ԭʼλ��
		self.__defRight = s_util.getGuiRight( gui )								# UI ��ԭʼ�Ҿ�
		self.__defBottom = s_util.getGuiBottom( gui )							# UI ��ԭʼ�׾�

		self.__clipFuncs = {}											# ���к���
		self.__clipFuncs["LEFT"]	= RefEx( self.__leftClip )			# �������
		self.__clipFuncs["RIGHT"]	= RefEx( self.__rightClip )			# �����ұ�
		self.__clipFuncs["TOP"]		= RefEx( self.__topClip )			# �����ϱ�
		self.__clipFuncs["BOTTOM"]	= RefEx( self.__bottomClip )		# �����±�


	# --------------------------------------------------------------------
	# private
	# --------------------------------------------------------------------
	def __stopClipping( self ) :
		"""
		ֹͣ��ǰ�Ĳ���
		"""
		BigWorld.cancelCallback( self.__clipCBID )				# �ֶ�ֹͣ����
		self.__value = self.currValue							# �� value ��Ϊʵ��ֵ

	# -------------------------------------------------
	def __leftClip( self, currValue ) :
		"""
		ģʽΪ��ߵĲ���
		"""
		value = currValue + self.__perClipValue					# ��ǰ tick �� value
		if self.__perClipValue > 0 :							# ���ֵ��������
			value = min( self.__value, value )					# ��cuur ֵ���ܴ��������õ�ֵ
		else :													# ����
			value = max( self.__value, value )					# cuur ֵ����С�������õ�ֵ

		defWidth = self.__defSize[0]							# ԭʼ���
		width = defWidth * value								# ��ǰ tick Ӧ�����õĿ��
		self.__gui.width = width								# ����Ϊ�µĴ�С

		left, right, top, bottom = self.__defMapBound			# ԭʼ Mapping Bound
		defMWidth = right - left								# ԭʼ mapping width
		left += defMWidth * ( 1 - value )						# �µ� mapping ���
		self.__gui.mapping = util.getGuiMapping( self.__defSize, left, right, top, bottom )

		s_util.setGuiRight( self.__gui, self.__defRight )		# ���� UI ��λ�ã��̶����ұߣ�

		if value != self.__value :
			self.__clipCBID = BigWorld.callback( 0.01, Functor( self.__leftClip, value ) )

	def __rightClip( self, currValue ) :
		"""
		ģʽΪ�ұߵĲ���
		"""
		value = currValue + self.__perClipValue					# ��ǰ tick �� value
		if self.__perClipValue > 0 :							# ���ֵ��������
			value = min( self.__value, value )					# ��cuur ֵ���ܴ��������õ�ֵ
		else :													# ����
			value = max( self.__value, value )					# cuur ֵ����С�������õ�ֵ

		defWidth = self.__defSize[0]							# ԭʼ���
		width = defWidth * value								# ��ǰ tick Ӧ�����õĿ��
		self.__gui.width = width								# ����Ϊ�µĴ�С

		left, right, top, bottom = self.__defMapBound			# ԭʼ Mapping Bound
		defMWidth = right - left								# ԭʼ mapping width
		right = left + defMWidth * value						# �µ� mapping ���
		self.__gui.mapping = util.getGuiMapping( self.__defSize, left, right, top, bottom )

		if value != self.__value :
			self.__clipCBID = BigWorld.callback( 0.01, Functor( self.__rightClip, value ) )

	def __topClip( self, currValue ) :
		"""
		ģʽΪ�ϲ��Ĳ���
		"""
		value = currValue + self.__perClipValue					# ��ǰ tick �� value
		if self.__perClipValue > 0 :							# ���ֵ��������
			value = min( self.__value, value )					# ��cuur ֵ���ܴ��������õ�ֵ
		else :													# ����
			value = max( self.__value, value )					# cuur ֵ����С�������õ�ֵ

		defHeight = self.__defSize[1]							# ԭʼ�߶�
		height = defHeight * value								# ��ǰ tick Ӧ�����õĿ��
		self.__gui.height = height								# ����Ϊ�µĴ�С

		left, right, top, bottom = self.__defMapBound			# ԭʼ Mapping Bound
		defMHeight = bottom - top								# ԭʼ mapping width
		top += defMHeight * ( 1 - value )						# �µ� mapping ���
		self.__gui.mapping = util.getGuiMapping( self.__defSize, left, right, top, bottom )

		s_util.setGuiBottom( self.__gui, self.__defBottom )

		if value != self.__value :
			self.__clipCBID = BigWorld.callback( 0.01, Functor( self.__topClip, value ) )

	def __bottomClip( self, currValue ) :
		"""
		ģʽΪ�ײ��Ĳ���
		"""
		value = currValue + self.__perClipValue					# ��ǰ tick �� value
		if self.__perClipValue > 0 :							# ���ֵ��������
			value = min( self.__value, value )					# ��cuur ֵ���ܴ��������õ�ֵ
		else :													# ����
			value = max( self.__value, value )					# cuur ֵ����С�������õ�ֵ

		defHeight = self.__defSize[1]							# ԭʼ�߶�
		height = defHeight * value								# ��ǰ tick Ӧ�����õĿ��
		self.__gui.height = height								# ����Ϊ�µĴ�С

		left, right, top, bottom = self.__defMapBound			# ԭʼ Mapping Bound
		defMHeight = bottom - top								# ԭʼ mapping width
		bottom = top + defMHeight * value 						# �µ� mapping ���
		self.__gui.mapping = util.getGuiMapping( self.__defSize, left, right, top, bottom )

		if value != self.__value :
			self.__clipCBID = BigWorld.callback( 0.01, Functor( self.__bottomClip, value ) )


	# --------------------------------------------------------------------
	# property methods
	# --------------------------------------------------------------------
	def _getGui( self ) :
		return self.__gui

	# -------------------------------------------------
	def _getClipMode( self ) :
		return self.__clipMode

	def _setClipMode( self, clipMode ) :
		if isDebuged :
			assert clipMode in self.__clipFuncs, "clip mode must be 'LEFT' or 'RIGHT' or 'TOP' or 'BOTTOM'"
		self.__gui.size = self.__defSize 						# �ָ�ԭʼ��С
		self.__gui.mapping = self.__defMapping					# �ָ�ԭʼ�� mapping
		s_util.setGuiPos( self.__gui, self.__defPos )			# �ָ�ԭʼλ��
		self.__stopClipping()									# ������ڲ��У���ֹͣ
		self.__clipMode = clipMode

	# -------------------------------------------------
	def _getValue( self ) :
		return self.__value

	def _setValue( self, value ) :
		value = min( 1.0, value )
		value = max( 0.0, value )
		if self.__value == value : return								# ������õ�ֵ�뵱ǰֵһ�£��򷵻�
		self.__stopClipping()											# �������ִ����һ�εĲ��У���ֹͣ����
		self.__perClipValue = ( value - self.__value ) * self.__speed	# ����ÿһ tick Ӧ�ò��е� value ֵ
		oldValue = self.__value
		self.__value = value											# ������ֵ
		self.__clipFuncs[self.__clipMode]()( oldValue )					# ���ò��к��������𲽲���

	# ---------------------------------------
	def _getSpeed( self ) :
		return self.__speed

	def _setSpeed( self, speed ) :
		speed = max( 0.0, speed )
		if speed == 0.0 : speed = 1.0
		self.__speed = min( speed, 1.0 )

	# -------------------------------------------------
	def _getCurrValue( self ) :
		size = self.__gui.size
		if self.__clipMode == "LEFT" or self.__clipMode == "RIGHT" :
			return size[0] / self.__defSize[0]
		return size[1] / self.__defSize[1]


	# --------------------------------------------------------------------
	# properties
	# --------------------------------------------------------------------
	gui = property( _getGui )								# ��ȡ�����е� UI
	clipMode = property( _getClipMode, _setClipMode )		# ����ģʽ: "LEFT", "RIGHT", "TOP", "BOTTOM"
	value = property( _getValue, _setValue )				# ���б�ֵ��0��1.0
	speed = property( _getSpeed, _setSpeed )				# �����ٶȣ�0��1.0 ( 0 �� 1.0 ��Ч����һ��������˲ʱ�������ֵ )
	currValue = property( _getCurrValue )					# ��ȡ��ǰ��ʵ����ֵ

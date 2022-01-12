# -*- coding: gb18030 -*-
#
# $Id: ProgressBar.py,v 1.18 2008-08-06 03:09:01 huangyongwei Exp $

"""
implement progressbar class
2005/05/18 : writen by huangyongwei
"""


import sys
import weakref
from guis import *
from guis.common.Frame import HFrame
from Control import Control

# --------------------------------------------------------------------
# implement horizontal progress bar
# --------------------------------------------------------------------
"""
composing :
	GUI.Simple
		-- clipper ( GUI.ClipShader )
"""

class HProgressBar( Control ) :
	def __init__( self, pbar = None, pyBinder = None ) :
		Control.__init__( self, pbar, pyBinder )
		self.__initialize( pbar )

		self.__value = self.currValue					# ��ǰ���õĽ���ֵ
		self.__clipInterval = 0.001						# �ݽ���ʱ���ٶȣ����೤ʱ���ȡһ�Σ�
		self.__speed = 0.0								# �ݽ���λ���ٶ�
		self.__clipCBID = 0								# callback ID

	def subclass( self, pbar, pyBinder = None ) :
		Control.subclass( self, pbar, pyBinder )
		self.__initialize( pbar )
		return self

	def __initialize( self, pbar ) :
		if pbar is None : return
		self.__clipper = pbar.clipper


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		Control.generateEvents_( self )
		self.__onProgressChanged = self.createEvent_( "onProgressChanged" )
		self.__onCurrentValueChanged = self.createEvent_( "onCurrentValueChanged" )

	@property
	def onProgressChanged( self ) :
		return self.__onProgressChanged

	@property
	def onCurrentValueChanged( self ) :
		return self.__onCurrentValueChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __cycleClip( self, currValue ) :
		if self.__speed <= 0 :												# ��������ٶ�С�ڻ���� 0
			currValue = self.__value										# �����˲�����
		elif self.__value > currValue :										# ����
			currValue += self.__speed										# ��ǰʵ��ֵ�����ٶ�ֵ
			currValue = min( self.__value, currValue )						# ���Ƶ�ǰʵ��ֵС����ֵ
		else :																# ����
			currValue -= self.__speed										# ��ǰʵ��֮��ȥ�ٶ�ֵ
			currValue = max( self.__value, currValue )						# ���Ƶ�ǰʵ��ֵ������ֵ
		self.__clipper.value = currValue									# ���� shader ��ֵ
		self.onCurrProgressChanged_( currValue )							# ����ʵ�ʽ��ȸı��¼�
		if currValue != self.__value :										# �����ǰʵ��ֵ�������������õ�ֵ
			func = Functor( self.__cycleClip, currValue )					# ���������
			self.__clipCBID = BigWorld.callback( self.__clipInterval, func )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onPorgressChanged_( self, value ) :
		"""
		����ֵ�ı�ʱ������
		"""
		self.onProgressChanged( value )

	def onCurrProgressChanged_( self, value ) :
		"""
		ʵʱ����ֵ�ı�ʱ������
		"""
		self.onCurrentValueChanged( value )

	def onDisable( self ) :
		"""
		��Чʱ������
		"""
		self.materialFX = "BLEND"


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self, value = 0 ) :
		"""
		�������ý���ֵ
		@type			value : float
		@param			value : new value
		@return				  : None
		"""
		value = min( 1, value )
		value = max( 0, value )
		BigWorld.cancelCallback( self.__clipCBID )
		changed = self.__value != value
		self.__value = value
		self.__clipper.value = value
		self.__clipper.reset()
		if changed :
			self.onCurrProgressChanged_( value )
			self.onPorgressChanged_( value )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getClipMode( self ) :
		return self.__clipper.mode

	def _setClipMode( self, mode ) :
		self.__clipper.mode = mode

	# -------------------------------------------------
	def _getValue( self ) :
		return self.__value

	def _setValue( self, value ) :
		value = min( value, 1.0 )						# ����ֵ���ܴ��� 1.0
		value = max( 0, value )							# ����ֵ����С�� 0.0
		oldValue = self.__value							# �����ֵ
		if oldValue == value : return					# ���Ҫ���õ�ֵ���ڵ�ǰֵ���򷵻�
		BigWorld.cancelCallback( self.__clipCBID )		# �����ǰ���ڲ��У���ֹͣ��ǰ�Ĳ��ж���
		self.__value = value							# ������ֵ
		self.__cycleClip( oldValue )					# ��ʼ����
		self.onPorgressChanged_( value )				# �������ȸı��¼�

	# ---------------------------------------
	def _getCurrValue( self ) :
		return self.__clipper.value

	# ---------------------------------------
	def _getSpeed( self ) :
		return self.__speed * 100

	def _setSpeed( self, value ) :
		speed = max( 0, value )
		self.__speed = speed / 100.0


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	clipMode = property( _getClipMode, _setClipMode )				# ��ȡ/���ý��ȷ���"LEFT", "RIGHT"
	value = property( _getValue, _setValue )						# ��ȡ/���ý���ֵ����ΧΪ 0��1
	currValue = property( _getCurrValue )							# ��ȡ��ǰ����ʵ����ֵ����Ϊ�����п����ǽ����ģ�
	speed = property( _getSpeed, _setSpeed )						# �����ٶȣ�������� 0����ֵԽ���佥���ٶ�Խ��


# --------------------------------------------------------------------
# implement horizontal frame progress bar
# --------------------------------------------------------------------
"""
composing :
	GUI.Window
		-- l ( GUI.Simple )
		-- r ( GUI.Simple )
		-- bg ( GUI.Simple )
"""

class HFProgressBar( HFrame, Control ) :
	def __init__( self, pb = None, pyBinder = None ) :
		HFrame.__init__( self, pb )
		Control.__init__( self, pb, pyBinder )
		self.__width = HFrame._getWidth( self )				# ���
		self.__value = self.currValue						# ����ֵ
		self.__clipInterval = 0.001							# ����ʱ�����ȵĵ�λʱ����
		self.__speed = 0.0									# �����ٶ�
		self.__clipCBID = 0									# callback ID


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		Control.generateEvents_( self )
		self.__onProgressChanged = self.createEvent_( "onProgressChanged" )
		self.__onCurrentValueChanged = self.createEvent_( "onCurrentValueChanged" )

	@property
	def onProgressChanged( self ) :
		return self.__onProgressChanged

	@property
	def onCurrentValueChanged( self ) :
		return self.__onCurrentValueChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __cycleClip( self, currValue ) :
		if self.__speed <= 0 :												# ��������ٶ�С�ڻ���� 0
			currValue = self.__value										# �����˲�����
		elif self.__value > currValue :										# ����
			currValue += self.__speed										# ��ǰʵ��ֵ�����ٶ�ֵ
			currValue = min( self.__value, currValue )						# ���Ƶ�ǰʵ��ֵС����ֵ
		else :																# ����
			currValue -= self.__speed										# ��ǰʵ��֮��ȥ�ٶ�ֵ
			currValue = max( self.__value, currValue )						# ���Ƶ�ǰʵ��ֵ������ֵ
		HFrame._setWidth( self, self.width * currValue )					# ���ÿ��ֵ��ֵ
		self.onCurrProgressChanged_( currValue )							# ����ʵ�ʽ��ȸı��¼�
		if currValue != self.__value :										# �����ǰʵ��ֵ�������������õ�ֵ
			func = Functor( self.__cycleClip, currValue )					# ���������
			self.__clipCBID = BigWorld.callback( self.__clipInterval, func )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onPorgressChanged_( self, value ) :
		"""
		����ֵ�ı�ʱ������
		"""
		self.onProgressChanged( value )

	def onCurrProgressChanged_( self, value ) :
		"""
		ʵʱ����ֵ�ı�ʱ������
		"""
		self.onCurrentValueChanged( value )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self, value = 0 ) :
		value = min( 1.0, value )
		value = max( value, 0 )
		BigWorld.cancelCallback( self.__clipCBID )
		changed = self.__value != value
		self.__value = value
		HFrame._setWidth( self, self.width * value )
		if changed :
			self.onCurrProgressChanged_( value )
			self.onPorgressChanged_( value )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getValue( self ) :
		return self.__value

	def _setValue( self, value ) :
		value = min( value, 1.0 )						# ����ֵ���ܴ��� 1.0
		value = max( 0, value )							# ����ֵ����С�� 0.0
		oldValue = self.__value							# �����ֵ
		if oldValue == value : return					# ���Ҫ���õ�ֵ���ڵ�ǰֵ���򷵻�
		BigWorld.cancelCallback( self.__clipCBID )		# �����ǰ���ڲ��У���ֹͣ��ǰ�Ĳ��ж���
		self.__value = value							# ������ֵ
		self.__cycleClip( oldValue )					# ��ʼ����
		self.onPorgressChanged_( value )				# �������ȸı��¼�

	def _getCurrValue( self ) :
		if self.width <= 0 : return 0
		return HFrame._getWidth( self ) / self.width

	# ---------------------------------------
	def _getSpeed( self ) :
		return self.__speed * 100

	def _setSpeed( self, value ) :
		speed = max( 0, value )
		self.__speed = speed / 100.0

	# -------------------------------------------------
	def _getWidth( self ) :
		return self.__width

	def _setWidth( self, width ) :
		self.__width = width
		HFrame._setWidth( self, width * self.value )

	# -------------------------------------------------
	def _getRWidth( self ) :
		return s_util.toRXMeasure( self.__width )

	def _setRWidth( self, width ) :
		self.width = s_util.toPXMeasure( width )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	value = property( _getValue, _setValue )							# ��ȡ/���ý���ֵ
	currValue = property( _getCurrValue )								# ��ȡ��ǰ����ֵ����Ϊ�п����ǽ����ģ�
	speed = property( _getSpeed, _setSpeed )							# �����ٶȣ�������� 0����ֵԽ���佥���ٶ�Խ��
	width = property( _getWidth, _setWidth )							# ��ȡ/��������������
	r_width = property( _getRWidth, _setRWidth )						# ��ȡ/�������������

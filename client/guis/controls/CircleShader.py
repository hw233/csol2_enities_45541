# -*- coding: gb18030 -*-

# this module implement CircleShader
# written by gjx 2009-6-16

# CircleShader ���ڼ�����ȴ�Ľ�����֣�Χ��ͼ������˳ʱ��/��ʱ��ݼ�

from guis import *
import math

PI = math.pi

# --------------------------------------------------------------------
# CircleGUIComponent��֧����Բ���ε�Ч��
# (1) ��Ⱦ��ʽ��˳ʱ�뷽�򣬴���ʼ���ȣ�startRadian_������ֹ���ȣ�endRadian_������λ�õ���Բ����
# (2) ��gui�����ļ���������ʼ���ȡ�startRadian������ֹ���ȡ�endRadian���ֶΣ�����Ϊfloat
# (3) �ű��������������Ӧ�ɶ�д���ԣ�Circle.startRadian Ĭ��ֵΪ0.0, Circle.endRadian Ĭ��ֵΪ 2_PI
# --------------------------------------------------------------------
# ����� GUI.Circle ʹ�õĵ�λ�ǻ���,�����ｫ�Դ˵�λ����ת������,ʹ��
# CircleShader�����������ԣ�
# 1����ʼ����ֹλ�ö������Ϸ�����ת��������Լ��趨Ϊ˳ʱ�������ʱ�룬
#	Ĭ����˳ʱ�룻
# 2��CircleShader�����ֵ��1�����reverseֵΪFalse,��ֵΪ1ʱ������ͼ
#	��ȫ���ɼ���Ϊ0��ȫ�����أ����reverseֵΪTrue���෴������ֵ�Ĵ�С
#	���㵱ǰ�����������
# 3��ÿ�θ�����ֵ�����ڣ�0 �� 1.0���ķ�Χ֮�ڣ�����ʱ���������߽�Ϊ����
#	ֵ������ʾ��
# --------------------------------------------------------------------

class CircleShader( object ) :

	def __init__( self, cover ) :
		object.__init__( self )

		self.__deasil = True				# True��˳ʱ�뷽����ת��False����ʱ�뷽����ת
		self.__reverse = False				# �Ƿ�ɫ��ʾ��True����ɫ����������ӣ�
		self.__value = 1.0					# ��ʼʱĬ��ֵ��ȫ����ʾ
		self.__initialize( cover )

	def __del__( self ) :
		self.__gui = None
		if Debug.output_del_CircleShader :
			INFO_MSG( str( self ) )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, cover ) :
		if isDebuged :
			assert type( cover ) == GUI.Circle, "Engine gui must be instance of 'GUI.Circle'!"
		self.__gui = cover					# ����Բ��GUI
		self.__gui.endRadian = 1.5 * PI
		self.__gui.startRadian = -0.5 * PI

	def __updateArea( self ) :
		"""
		���㵱ǰ���������
		"""
		if self.__deasil :														# ˳ʱ����ת
			if self.__reverse :													# ��ɫ
				self.__gui.endRadian = ( 1.5 - self.__value * 2 ) * PI
			else :
				self.__gui.startRadian = ( 1.5 - self.__value * 2 ) * PI
		else :																	# ��ʱ����ת
			if self.__reverse :													# ��ɫ
				self.__gui.startRadian = ( self.__value * 2 - 0.5 ) * PI
			else :
				self.__gui.endRadian = ( self.__value * 2 - 0.5 ) * PI


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self ) :
		"""
		���¼����������
		"""
		self.__gui.endRadian = 1.5 * PI
		self.__gui.startRadian = -0.5 * PI
		self.__updateArea()


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getValue( self ) :
		return self.__value

	def _setValue( self, value ) :
		value = min( 1.0, value )
		value = max( 0.0, value )
		self.__value = value
		self.__updateArea()

	def _getEddyMode( self ) :
		return self.__deasil

	def _setEddyMode( self, mode ) :
		self.__deasil = mode
		self.reset()

	def _getReverse( self ) :
		return self.__reverse

	def _setReverse( self, reverse ) :
		self.__reverse = reverse
		self.reset()

	# -------------------------------------------------
	value = property( _getValue, _setValue )				# ��ȡ/���õ�ǰֵ
	deasil = property( _getEddyMode, _setEddyMode )			# ��ȡ/������ת����˳/��ʱ�룩
	reverse = property( _getReverse, _setReverse )			# �Ƿ�ɫ

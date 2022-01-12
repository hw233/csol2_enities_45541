# -*- coding: gb18030 -*-

# this module implement CircleShader
# written by gjx 2009-6-16

# CircleShader 用于技能冷却的界面表现，围绕图标中心顺时针/逆时针递减

from guis import *
import math

PI = math.pi

# --------------------------------------------------------------------
# CircleGUIComponent，支持椭圆扇形的效果
# (1) 渲染方式：顺时针方向，从起始弧度（startRadian_）到终止弧度（endRadian_）所在位置的椭圆扇形
# (2) 在gui配置文件新增的起始弧度“startRadian”和终止弧度“endRadian”字段，类型为float
# (3) 脚本层次上新增的相应可读写属性：Circle.startRadian 默认值为0.0, Circle.endRadian 默认值为 2_PI
# --------------------------------------------------------------------
# 引擎的 GUI.Circle 使用的单位是弧度,在这里将对此单位进行转换计算,使得
# CircleShader具有以下特性：
# 1、起始和终止位置都在正上方，旋转方向可以自己设定为顺时针或者逆时针，
#	默认是顺时针；
# 2、CircleShader的最大值是1，如果reverse值为False,则当值为1时，整个图
#	形全部可见，为0，全部隐藏；如果reverse值为True则相反；根据值的大小
#	计算当前的扇形面积；
# 3、每次给出的值必须在（0 — 1.0）的范围之内，超出时以这两个边界为极限
#	值进行演示；
# --------------------------------------------------------------------

class CircleShader( object ) :

	def __init__( self, cover ) :
		object.__init__( self )

		self.__deasil = True				# True：顺时针方向旋转，False：逆时针方向旋转
		self.__reverse = False				# 是否反色显示（True：有色面积慢慢增加）
		self.__value = 1.0					# 开始时默认值是全部显示
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
		self.__gui = cover					# 引擎圆形GUI
		self.__gui.endRadian = 1.5 * PI
		self.__gui.startRadian = -0.5 * PI

	def __updateArea( self ) :
		"""
		计算当前的扇形面积
		"""
		if self.__deasil :														# 顺时针旋转
			if self.__reverse :													# 反色
				self.__gui.endRadian = ( 1.5 - self.__value * 2 ) * PI
			else :
				self.__gui.startRadian = ( 1.5 - self.__value * 2 ) * PI
		else :																	# 逆时针旋转
			if self.__reverse :													# 反色
				self.__gui.startRadian = ( self.__value * 2 - 0.5 ) * PI
			else :
				self.__gui.endRadian = ( self.__value * 2 - 0.5 ) * PI


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self ) :
		"""
		重新计算扇形面积
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
	value = property( _getValue, _setValue )				# 获取/设置当前值
	deasil = property( _getEddyMode, _setEddyMode )			# 获取/设置旋转方向（顺/逆时针）
	reverse = property( _getReverse, _setReverse )			# 是否反色

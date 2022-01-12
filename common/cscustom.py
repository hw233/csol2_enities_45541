# -*- coding: gb18030 -*-
#
# $Id: cscustom.py,v 1.4 2008-05-30 09:47:15 huangyongwei Exp $

"""
This module implements custom data type
2007/12/26: writen by huangyongwei
"""

# --------------------------------------------------------------------
# 几何类型
# --------------------------------------------------------------------
import math
import Math

# --------------------------------------------------------------------
# 实现 line 类，该直线由两点确定的，因此也可以将该直线理解为线段或者射线
# --------------------------------------------------------------------
class Line( object ) :
	__slots__ = ["__x1", "__x2", "__y1", "__y2", "__length", "__slope"]

	def __init__( self, point1 = ( 0, 0 ), point2 = ( 0, 0 ) ) :
		self.__x1 = self.__y1 = 0
		self.__x2 = self.__y2 = 0
		self.__length = 0				# 两点间的距离
		self.__slope = 0				# 斜率
		self.update( point1, point2 )


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		return "Line(%s, %s)" % ( self.point1, self.point2 )

	def __str__( self ) :
		return self.__repr__()

	def __cmp__( self, line ) :
		if self.point1 == line.point1 and self.point2 == line.point2 :
			return 0
		if self.point1 == line.point2 and self.point2 == line.point1 :
			return 0
		return -1


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __reset( self ) :
		# 计算两点间距离
		powx = ( self.__x2 - self.__x1 ) ** 2
		powy = ( self.__y2 - self.__y1 ) ** 2
		self.__length = ( powx + powy ) * 0.5

		# 计算斜率
		x_dst = self.__x2 - self.__x1
		if x_dst == 0 :
			self.__slope = None
		else :
			self.__slope = ( self.__y2 - self.__y1 ) / x_dst


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, point1, point2 ) :
		"""
		update line
		@type			point1 : tuple
		@param			point1 : 点1
		@type			point2 : tuple
		@param			point2 : 点2
		@return				   : None
		"""
		x1, y1 = point1
		x2, y2 = point2
		self.__x1 = float( x1 )
		self.__y1 = float( y1 )
		self.__x2 = float( x2 )
		self.__y2 = float( y2 )
		self.__reset()

	def updateByLine( self, line ) :
		"""
		设置为与给定线相等( 重合 )
		@type				line : Line
		@param				line : 源直线
		@return					 : None
		"""
		self.__x1 = line.__x1
		self.__x2 = line.__x2
		self.__y1 = line.__y1
		self.__y2 = line.__y2
		self.__reset()

	def copy( self ) :
		"""
		获得一份拷贝
		@rtype					: Line
		@return					: 直线拷贝
		"""
		return Line( self.point1, self.point2 )

	# -------------------------------------------------
	def isPoint( self ) :
		"""
		判断该直线是否是点
		@rtype				: bool
		@return				: 如果确定直线的两个点重合，则返回 True
		"""
		return self.point1 == self.point2

	def isPointIn( self, point, warp = 0.0 ) :
		"""
		判断某点是否在直线上
		@type			point : tuple
		@param			point : 给出判断的点
		@type			warp  : float
		@param			warp  : 偏差值，即当 point 与直线的偏差值不大于该值，则认为该点在直线上
		@rtype				  : bool
		@return				  : 如果给出的点在直线上，则返回 True
		"""
		x, y = point
		a = ( self.__x1 - x ) * ( self.__y2 - y )
		b = ( self.__y1 - y ) * ( self.__x2 - x )
		return abs( a - b ) <= warp

	def isInnerPoint( self, point, warp = 0.0 ) :
		"""
		判断某点是否在线段內
		@type			point : tuple
		@param			point : 给出的点
		@type			warp  : float
		@param			warp  : 偏差值，即当 point 与直线的偏差值不大于该值，则认为该点在直线上
		@rtype				  : bool
		@return				  : 如果给出的点在线段上，则返回 True
		"""
		if not self.isPointIn( point, warp ) :
			return False
		x, y = point
		minX = min( self.__x1, self.__x2 )
		maxX = max( self.__x1, self.__x2 )
		minY = min( self.__y1, self.__y2 )
		maxY = max( self.__y1, self.__y2 )
		if x < minX - warp : return False
		if x > maxX + warp : return False
		if y < minY - warp : return False
		if y > maxY + warp : return False
		return True

	# -------------------------------------------------
	def isIntersectant( self, line ) :
		"""
		判断是否与另一条直线相交( 如果两条线重合，则不算作相交 )
		@type			line : Line
		@param			line : 要判断的直线
		@rtype				 : bool
		@param				 : 如果两直线相交，则返回 True
		"""
		return self.__slope != line.__slope

	def isSuperposition( self, line ) :
		"""
		判断两条直线是否重合
		@type			line : Line
		@param			line : 要判断的直线
		@rtype				 : bool
		@param				 : 如果两直线重合，则返回 True
		"""
		if self.isIntersectant( line ) :
			return False
		if self.isPointIn( line.point1 ) :
			return True
		return False

	def getIntersectantPoint( self, line ) :
		"""
		获取两直线的交点( 如果两条直线重合，则不算相交 )( 消元法 )
		@type			line : Line
		@param			line : 另一条直线
		@rtype				 : tuple
		@return				 : 两直线的交点，如果量直线没有交点，则返回 None
		"""
		if not self.isIntersectant( line ) :
			return None

		# 假设 x 和 y 为交点，则二元方程组如下：
		# ( x - self.x1 ) * ( self.y2 - self.y1 ) = ( y - self.y1 ) * ( self.x2 - self.x1 )
		# ( x - line.x1 ) * ( line.y2 - line.y1 ) = ( y - line.y1 ) * ( line.x2 - line.x1 )
		oSegX = self.__x2 - self.__x1
		oSegY = self.__y2 - self.__y1
		lSegX = line.x2 - line.x1
		lSegY = line.y2 - line.y1

		# 整理得：
		# lSegY * line.x2 - lSegY * x = lSegX * line.y2 - lSegX * y
		# oSegY * self.x2 - oSegY * x = oSegX * self.y2 - oSegX * y
		# 移项得：
		# lSegX * y - lSegY * x = d1 ( 系数 d1 = lSegX * line.y2 - lSegY * line.x2 )
		# oSegX * y - oSegY * x = d2 ( 系数 d2 = oSegX * self.y2 - oSegY * self.x2 )
		d1 = lSegX * line.y2 - lSegY * line.x2
		d2 = oSegX * self.y2 - oSegY * self.x2

		if oSegX == 0 :							# self 是垂直于 x 轴的直线
			x = self.__x1
			y = ( d1 + lSegY * x ) / lSegX
		elif lSegX == 0 :						# line 是垂直于 x 轴的直线
			x = line.x1
			y = ( d2 + oSegY * x ) / oSegX
		elif oSegY == 0 :						# self 是平行于 x 轴的直线
			y = self.__y1
			x = ( lSegX * y - d1 ) / lSegY
		elif lSegY == 0 :						# line 是平行于 x 轴的直线
			y = line.y1
			x = ( oSegX * y - d2 ) / oSegY
		else :
			# 方程 1 两边同时乘以 oSegX，方程 2 两边同时乘以 lSegX 得：
			# oSegX * lSegX * y - oSegX * lSegY * x = oSegX * d1
			# oSegX * lSegX * y - oSegY * lSegX * x = lSegX * d2
			# 用方程 2 减去方程 1 得：
			# ( oSegX * lSegY - oSegY * lSegX ) * x = lSegX * d2 - oSegX * d1
			# 求得 x：
			x = ( lSegX * d2 - oSegX * d1 ) / ( oSegX * lSegY - oSegY * lSegX )
			y = ( d1 + lSegY * x ) / lSegX
		return x, y

	# -------------------------------------------------
	def isSeamIntersectant( self, line ) :
		"""
		判断两线段是否有交点( 两条线段在同一直线上，则不算有交点 )
		@type				line : Line
		@param				line : 指定的线段
		@rtype					 : bool
		@return					 : 如果有交点则返回 True
		"""
		point = self.getIntersectantPoint()
		if point is not None :
			return self.isInnerPoint( point )
		return False

	def getSeamIntersectantPoint( self, line ) :
		"""
		获取两线段的交点( 如果两条直线重合，则不算相交 )
		@type			line : Line
		@param			line : 另一条直线
		@rtype				 : tuple
		@return				 : 两线段的交点，如果两个线段没有交点，则返回 None
		"""
		point = self.getIntersectantPoint()
		if point is None :
			return None
		if self.isInnerPoint( point ) :
			return point
		return None


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getPoint1( self ) :
		return Math.Vector2( self.__x1, self.__y1 )

	def _setPoint1( self, point ) :
		x, y = point
		self.__x1 = float( x )
		self.__y1 = float( y )
		self.__reset()

	# ---------------------------------------
	def _getPoint2( self ) :
		return Math.Vector2( self.__x2, self.__y2 )

	def _setPoint2( self, point ) :
		x, y = point
		self.__x2 = float( x )
		self.__y2 = float( y )
		self.__reset()


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def x1( self ) :						# 线段的起点 x 坐标
		return self.__x1

	@property
	def y1( self ) :						# 线段的起点 y 坐标
		return self.__y1

	@property
	def x2( self ) :						# 线段的结束点 x 坐标
		return self.__x2

	@property
	def y2( self ) :						# 线段的结束点 y 坐标
		return self.__y2

	# ---------------------------------------
	@property
	def length( self ) :					# 线段的长度
		return self.__length

	@property
	def slope( self ) :						# 线段的斜率
		return self.__slope

	# -------------------------------------------------
	point1 = property( _getPoint1, _setPoint1 )			# 线段的起始坐标
	point2 = property( _getPoint2, _setPoint2 )			# 线段的结束坐标


# --------------------------------------------------------------------
# 实现 rect 类
# --------------------------------------------------------------------
class Rect( object ) :
	__slots__ = ["__x", "__y", "__width", "__height"]

	def __init__( self, location = ( 0, 0 ), size = ( 0, 0 ) ) :
		self.__x = 0				# 低值顶点 x 坐标
		self.__y = 0				# 低值顶点 y 坐标
		self.__width = 0			# 宽度
		self.__height = 0			# 高度
		self.update( location, size )

	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		return "Rect((%s, %s), (%s, %s))" % ( self.__x, self.__y, self.__width, self.__height )

	def __str__( self ) :
		return self.__repr__()

	def __cmp__( self, rect ) :
		if self.__x != rect.__x : return -1
		if self.__y != rect.__x : return -1
		if self.__width != rect.__width : return -1
		if self.__height != rect.__height : return -1
		return 0


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def copy( self ) :
		"""
		获得一份拷贝
		@rtype					: Line
		@return					: 矩形
		"""
		return Rect( self.location, self.size )

	# -------------------------------------------------
	def update( self, location, size ) :
		"""
		更新矩形
		@type				location : float / int
		@param				location : 矩形低值顶点 x 坐标
		@type				size	 : float / int
		@param				size	 : 矩形低值顶点 y 坐标
		@return						 : None
		"""
		self.updateLocation( *location )
		self.updateSize( *size )

	def updateByRect( self, rect ) :
		"""
		用另一个 rect 更新我自己
		@type				rect : Rect
		@param				rect : 源 Rect
		@return					 : None
		"""
		self.__x = rect.__x
		self.__y = rect.__y
		self.__width = rect.__width
		self.__height = rect.__height

	def updateByBound( self, minX, maxX, minY, maxY ) :
		"""
		更新矩形
		@type				minX : float / int
		@param				minX : 矩形低值顶点 x 坐标
		@type				maxX : float / int
		@param				maxX : 矩形高值顶点 x 坐标
		@type				minY : float / int
		@param				minY : 矩形低值顶点 y 坐标
		@type				maxY : float / int
		@param				maxY : 矩形高值顶点 y 坐标
		@return					 : None
		"""
		x = min( minX, maxX )
		y = min( minY, maxY )
		w = abs( maxX - minX )
		h = abs( maxY - minY )
		self.updateLocation( x, y )
		self.updateSize( w, h )

	def updateLocation( self, x, y ) :
		"""
		更新矩形位置
		@type				x : float / int
		@param				x : 矩形低值顶点 x 坐标
		@type				y : float / int
		@param				y : 矩形低值顶点 y 坐标
		@return				  : None
		"""
		self.__x = float( x )
		self.__y = float( y )

	def updateSize( self, w, h ) :
		"""
		更新矩形大小
		@type				w : float / int
		@param				w : 矩形宽度
		@type				h : float / int
		@param				h : 矩形高度
		@return				  : None
		"""
		self.__width = float( w )
		self.__height = float( h )

	# ---------------------------------------
	def move( self, offsetx, offsety ) :
		"""
		偏移矩形位置
		@type				offsetx : float / int
		@param				offsetx : 矩形沿 x 轴向高值移动的偏移
		@type				offsety : float / int
		@param				offsety : 矩形沿 y 轴向高值移动的偏移
		@return						: None
		"""
		self.__x += offsetx
		self.__y += offsety

	def increase( self, deltaw, deltah ) :
		"""
		增大/减小矩形
		@type				deltaw : float / int
		@param				deltaw : 矩形宽度增量
		@type				deltah : float / int
		@param				deltah : 矩形高度增量
		@return					   : None
		"""
		self.__width += deltaw
		self.__height += deltah

	def zoom( self, scalew, scaleh ) :
		"""
		放大/缩小矩形
		@type				deltaw : float / int
		@param				deltaw : 矩形宽度放大倍率
		@type				deltah : float / int
		@param				deltah : 矩形高度放大倍率
		@return					   : None
		"""
		self.__width *= scalew
		self.__height *= scaleh

	# -------------------------------------------------
	def isPointIn( self, location ) :
		"""
		判断给定点是否在矩形內
		@type				location : float / int
		@param				location : 指定的点
		@rtype						 : bool
		@return						 : 如果指定点在矩形內，则返回 True
		"""
		x, y = location
		if x < self.__x : return False
		if y < self.__y : return False
		if x > self.__x + self.__width : return False
		if y > self.__y + self.__height : return False
		return True


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def x( self ) :
		return self.__x

	@property
	def y( self ) :
		return self.__y

	@property
	def width( self ) :
		return self.__width

	@property
	def height( self ) :
		return self.__height

	@property
	def rect( self ) :
		return self.__x, self.__y, self.__width, self.__height

	# ---------------------------------------
	@property
	def minX( self ) :
		return self.__x

	@property
	def maxX( self ) :
		return self.__x + self.__width

	@property
	def minY( self ) :
		return self.__y

	@property
	def maxY( self ) :
		return self.__y + self.__height

	@property
	def bound( self ) :
		return self.minX, self.maxX, self.minY, self.maxY

	# ---------------------------------------
	@property
	def location( self ) :
		return Math.Vector2( self.__x, self.__y )

	@property
	def size( self ) :
		return self.__width, self.__height



# --------------------------------------------------------------------
# 实现 polygon 类，该多边形必须为突多边形，传入的构造多边形的点必须按顺序（顺时针或逆时针都可以）
# 判断点是否在多边形內
# 艾吉松修改后，支持凹多边形
# --------------------------------------------------------------------
class Polygon( object ) :
	__slots__ = ["__points", "__edges", "__bound", "__isConcave"]

	cg_warp = 0.0001

	def __init__( self, points ) :
		self.__points = []						# 多边形的顶点
		self.__edges = []						# 多边形的所有边，为了减轻计算时的负担，在构造多边形时，同时构造完成它的边
		self.__bound = Rect()					# 多边形的外接矩形：( left, right, top, bottom )
		self.update( points )


	# ----------------------------------------------------------------
	# inner mehods
	# ----------------------------------------------------------------
	def __repr__( self ) :
		return "Polygon%s" % str( self.__points )

	def __str__( self ) :
		return self.__repr__()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __calcBound( self, points ) :
		"""
		计算多边形的外接矩形
		"""
		if len( points ) == 0 : return
		minX = maxX = self.__points[0][0]
		minY = maxY = self.__points[0][1]
		for point in points :
			minX = min( minX, point[0] )
			maxX = max( maxX, point[0] )
			minY = min( minY, point[1] )
			maxY = max( maxY, point[1] )
		self.__bound.updateByBound( minX, maxX, minY, maxY )

	def __createBorders( self, points ) :
		"""
		创建多边形的所有边
		"""
		if len( points ) == 0 :
			return
		self.__edges = []
		firstPoint = points[0]
		forePoint = firstPoint
		for point in points[1:] :
			line = Line( forePoint, point )
			self.__edges.append( line )
			forePoint = point
		line = Line( forePoint, firstPoint )
		self.__edges.append( line )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, points ) :
		"""
		用新的点列表更新多边形
		@type				points : list
		@param				points : 多边形的所有顶点
		@return					   : None
		"""
		self.__points = points[:]
		self.__createBorders( points )							# 创建多边形的边
		self.__calcBound( points )								# 计算外接矩形

	def isPointIn( self, point ) :
		"""
		判断指定点是否在多边形内
		算法：aijisong
		"""
		if not self.__bound.isPointIn( point ) :				# 如果点不在外接矩形中，则肯定不在多边形內
			return False
		count = len( self.__points )
		if count == 0 :
			return False
		x, y = point
		flag = False
		for index in xrange( 0, count ) :
			x1, y1 = self.__points[index - 1]
			x2, y2 = self.__points[index]
			if x1 <= x <= x2 or x2 <= x <= x1 :
				deltaX12 = x1 - x2
				deltaY12 = y1 - y2
				deltaX = x - x1
				deltaY = y - y1
				if x == x2 :
					continue
				if deltaX12 > 0 and deltaY * deltaX12 <= deltaX * deltaY12 :
					flag = not flag
				elif deltaX12 < 0 and deltaY * deltaX12 >= deltaX * deltaY12 :
					flag = not flag
		return flag


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def points( self ) :											# 获取多边形的顺序顶点
		return self.__points[:]

	@property
	def bound( self ) :												# 获取多边形的外接矩形
		return self.__bound

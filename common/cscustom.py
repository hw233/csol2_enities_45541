# -*- coding: gb18030 -*-
#
# $Id: cscustom.py,v 1.4 2008-05-30 09:47:15 huangyongwei Exp $

"""
This module implements custom data type
2007/12/26: writen by huangyongwei
"""

# --------------------------------------------------------------------
# ��������
# --------------------------------------------------------------------
import math
import Math

# --------------------------------------------------------------------
# ʵ�� line �࣬��ֱ��������ȷ���ģ����Ҳ���Խ���ֱ�����Ϊ�߶λ�������
# --------------------------------------------------------------------
class Line( object ) :
	__slots__ = ["__x1", "__x2", "__y1", "__y2", "__length", "__slope"]

	def __init__( self, point1 = ( 0, 0 ), point2 = ( 0, 0 ) ) :
		self.__x1 = self.__y1 = 0
		self.__x2 = self.__y2 = 0
		self.__length = 0				# �����ľ���
		self.__slope = 0				# б��
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
		# ������������
		powx = ( self.__x2 - self.__x1 ) ** 2
		powy = ( self.__y2 - self.__y1 ) ** 2
		self.__length = ( powx + powy ) * 0.5

		# ����б��
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
		@param			point1 : ��1
		@type			point2 : tuple
		@param			point2 : ��2
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
		����Ϊ����������( �غ� )
		@type				line : Line
		@param				line : Դֱ��
		@return					 : None
		"""
		self.__x1 = line.__x1
		self.__x2 = line.__x2
		self.__y1 = line.__y1
		self.__y2 = line.__y2
		self.__reset()

	def copy( self ) :
		"""
		���һ�ݿ���
		@rtype					: Line
		@return					: ֱ�߿���
		"""
		return Line( self.point1, self.point2 )

	# -------------------------------------------------
	def isPoint( self ) :
		"""
		�жϸ�ֱ���Ƿ��ǵ�
		@rtype				: bool
		@return				: ���ȷ��ֱ�ߵ��������غϣ��򷵻� True
		"""
		return self.point1 == self.point2

	def isPointIn( self, point, warp = 0.0 ) :
		"""
		�ж�ĳ���Ƿ���ֱ����
		@type			point : tuple
		@param			point : �����жϵĵ�
		@type			warp  : float
		@param			warp  : ƫ��ֵ������ point ��ֱ�ߵ�ƫ��ֵ�����ڸ�ֵ������Ϊ�õ���ֱ����
		@rtype				  : bool
		@return				  : ��������ĵ���ֱ���ϣ��򷵻� True
		"""
		x, y = point
		a = ( self.__x1 - x ) * ( self.__y2 - y )
		b = ( self.__y1 - y ) * ( self.__x2 - x )
		return abs( a - b ) <= warp

	def isInnerPoint( self, point, warp = 0.0 ) :
		"""
		�ж�ĳ���Ƿ����߶΃�
		@type			point : tuple
		@param			point : �����ĵ�
		@type			warp  : float
		@param			warp  : ƫ��ֵ������ point ��ֱ�ߵ�ƫ��ֵ�����ڸ�ֵ������Ϊ�õ���ֱ����
		@rtype				  : bool
		@return				  : ��������ĵ����߶��ϣ��򷵻� True
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
		�ж��Ƿ�����һ��ֱ���ཻ( ����������غϣ��������ཻ )
		@type			line : Line
		@param			line : Ҫ�жϵ�ֱ��
		@rtype				 : bool
		@param				 : �����ֱ���ཻ���򷵻� True
		"""
		return self.__slope != line.__slope

	def isSuperposition( self, line ) :
		"""
		�ж�����ֱ���Ƿ��غ�
		@type			line : Line
		@param			line : Ҫ�жϵ�ֱ��
		@rtype				 : bool
		@param				 : �����ֱ���غϣ��򷵻� True
		"""
		if self.isIntersectant( line ) :
			return False
		if self.isPointIn( line.point1 ) :
			return True
		return False

	def getIntersectantPoint( self, line ) :
		"""
		��ȡ��ֱ�ߵĽ���( �������ֱ���غϣ������ཻ )( ��Ԫ�� )
		@type			line : Line
		@param			line : ��һ��ֱ��
		@rtype				 : tuple
		@return				 : ��ֱ�ߵĽ��㣬�����ֱ��û�н��㣬�򷵻� None
		"""
		if not self.isIntersectant( line ) :
			return None

		# ���� x �� y Ϊ���㣬���Ԫ���������£�
		# ( x - self.x1 ) * ( self.y2 - self.y1 ) = ( y - self.y1 ) * ( self.x2 - self.x1 )
		# ( x - line.x1 ) * ( line.y2 - line.y1 ) = ( y - line.y1 ) * ( line.x2 - line.x1 )
		oSegX = self.__x2 - self.__x1
		oSegY = self.__y2 - self.__y1
		lSegX = line.x2 - line.x1
		lSegY = line.y2 - line.y1

		# ����ã�
		# lSegY * line.x2 - lSegY * x = lSegX * line.y2 - lSegX * y
		# oSegY * self.x2 - oSegY * x = oSegX * self.y2 - oSegX * y
		# ����ã�
		# lSegX * y - lSegY * x = d1 ( ϵ�� d1 = lSegX * line.y2 - lSegY * line.x2 )
		# oSegX * y - oSegY * x = d2 ( ϵ�� d2 = oSegX * self.y2 - oSegY * self.x2 )
		d1 = lSegX * line.y2 - lSegY * line.x2
		d2 = oSegX * self.y2 - oSegY * self.x2

		if oSegX == 0 :							# self �Ǵ�ֱ�� x ���ֱ��
			x = self.__x1
			y = ( d1 + lSegY * x ) / lSegX
		elif lSegX == 0 :						# line �Ǵ�ֱ�� x ���ֱ��
			x = line.x1
			y = ( d2 + oSegY * x ) / oSegX
		elif oSegY == 0 :						# self ��ƽ���� x ���ֱ��
			y = self.__y1
			x = ( lSegX * y - d1 ) / lSegY
		elif lSegY == 0 :						# line ��ƽ���� x ���ֱ��
			y = line.y1
			x = ( oSegX * y - d2 ) / oSegY
		else :
			# ���� 1 ����ͬʱ���� oSegX������ 2 ����ͬʱ���� lSegX �ã�
			# oSegX * lSegX * y - oSegX * lSegY * x = oSegX * d1
			# oSegX * lSegX * y - oSegY * lSegX * x = lSegX * d2
			# �÷��� 2 ��ȥ���� 1 �ã�
			# ( oSegX * lSegY - oSegY * lSegX ) * x = lSegX * d2 - oSegX * d1
			# ��� x��
			x = ( lSegX * d2 - oSegX * d1 ) / ( oSegX * lSegY - oSegY * lSegX )
			y = ( d1 + lSegY * x ) / lSegX
		return x, y

	# -------------------------------------------------
	def isSeamIntersectant( self, line ) :
		"""
		�ж����߶��Ƿ��н���( �����߶���ͬһֱ���ϣ������н��� )
		@type				line : Line
		@param				line : ָ�����߶�
		@rtype					 : bool
		@return					 : ����н����򷵻� True
		"""
		point = self.getIntersectantPoint()
		if point is not None :
			return self.isInnerPoint( point )
		return False

	def getSeamIntersectantPoint( self, line ) :
		"""
		��ȡ���߶εĽ���( �������ֱ���غϣ������ཻ )
		@type			line : Line
		@param			line : ��һ��ֱ��
		@rtype				 : tuple
		@return				 : ���߶εĽ��㣬��������߶�û�н��㣬�򷵻� None
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
	def x1( self ) :						# �߶ε���� x ����
		return self.__x1

	@property
	def y1( self ) :						# �߶ε���� y ����
		return self.__y1

	@property
	def x2( self ) :						# �߶εĽ����� x ����
		return self.__x2

	@property
	def y2( self ) :						# �߶εĽ����� y ����
		return self.__y2

	# ---------------------------------------
	@property
	def length( self ) :					# �߶εĳ���
		return self.__length

	@property
	def slope( self ) :						# �߶ε�б��
		return self.__slope

	# -------------------------------------------------
	point1 = property( _getPoint1, _setPoint1 )			# �߶ε���ʼ����
	point2 = property( _getPoint2, _setPoint2 )			# �߶εĽ�������


# --------------------------------------------------------------------
# ʵ�� rect ��
# --------------------------------------------------------------------
class Rect( object ) :
	__slots__ = ["__x", "__y", "__width", "__height"]

	def __init__( self, location = ( 0, 0 ), size = ( 0, 0 ) ) :
		self.__x = 0				# ��ֵ���� x ����
		self.__y = 0				# ��ֵ���� y ����
		self.__width = 0			# ���
		self.__height = 0			# �߶�
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
		���һ�ݿ���
		@rtype					: Line
		@return					: ����
		"""
		return Rect( self.location, self.size )

	# -------------------------------------------------
	def update( self, location, size ) :
		"""
		���¾���
		@type				location : float / int
		@param				location : ���ε�ֵ���� x ����
		@type				size	 : float / int
		@param				size	 : ���ε�ֵ���� y ����
		@return						 : None
		"""
		self.updateLocation( *location )
		self.updateSize( *size )

	def updateByRect( self, rect ) :
		"""
		����һ�� rect �������Լ�
		@type				rect : Rect
		@param				rect : Դ Rect
		@return					 : None
		"""
		self.__x = rect.__x
		self.__y = rect.__y
		self.__width = rect.__width
		self.__height = rect.__height

	def updateByBound( self, minX, maxX, minY, maxY ) :
		"""
		���¾���
		@type				minX : float / int
		@param				minX : ���ε�ֵ���� x ����
		@type				maxX : float / int
		@param				maxX : ���θ�ֵ���� x ����
		@type				minY : float / int
		@param				minY : ���ε�ֵ���� y ����
		@type				maxY : float / int
		@param				maxY : ���θ�ֵ���� y ����
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
		���¾���λ��
		@type				x : float / int
		@param				x : ���ε�ֵ���� x ����
		@type				y : float / int
		@param				y : ���ε�ֵ���� y ����
		@return				  : None
		"""
		self.__x = float( x )
		self.__y = float( y )

	def updateSize( self, w, h ) :
		"""
		���¾��δ�С
		@type				w : float / int
		@param				w : ���ο��
		@type				h : float / int
		@param				h : ���θ߶�
		@return				  : None
		"""
		self.__width = float( w )
		self.__height = float( h )

	# ---------------------------------------
	def move( self, offsetx, offsety ) :
		"""
		ƫ�ƾ���λ��
		@type				offsetx : float / int
		@param				offsetx : ������ x �����ֵ�ƶ���ƫ��
		@type				offsety : float / int
		@param				offsety : ������ y �����ֵ�ƶ���ƫ��
		@return						: None
		"""
		self.__x += offsetx
		self.__y += offsety

	def increase( self, deltaw, deltah ) :
		"""
		����/��С����
		@type				deltaw : float / int
		@param				deltaw : ���ο������
		@type				deltah : float / int
		@param				deltah : ���θ߶�����
		@return					   : None
		"""
		self.__width += deltaw
		self.__height += deltah

	def zoom( self, scalew, scaleh ) :
		"""
		�Ŵ�/��С����
		@type				deltaw : float / int
		@param				deltaw : ���ο�ȷŴ���
		@type				deltah : float / int
		@param				deltah : ���θ߶ȷŴ���
		@return					   : None
		"""
		self.__width *= scalew
		self.__height *= scaleh

	# -------------------------------------------------
	def isPointIn( self, location ) :
		"""
		�жϸ������Ƿ��ھ��΃�
		@type				location : float / int
		@param				location : ָ���ĵ�
		@rtype						 : bool
		@return						 : ���ָ�����ھ��΃ȣ��򷵻� True
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
# ʵ�� polygon �࣬�ö���α���Ϊͻ����Σ�����Ĺ������εĵ���밴˳��˳ʱ�����ʱ�붼���ԣ�
# �жϵ��Ƿ��ڶ���΃�
# �������޸ĺ�֧�ְ������
# --------------------------------------------------------------------
class Polygon( object ) :
	__slots__ = ["__points", "__edges", "__bound", "__isConcave"]

	cg_warp = 0.0001

	def __init__( self, points ) :
		self.__points = []						# ����εĶ���
		self.__edges = []						# ����ε����бߣ�Ϊ�˼������ʱ�ĸ������ڹ�������ʱ��ͬʱ����������ı�
		self.__bound = Rect()					# ����ε���Ӿ��Σ�( left, right, top, bottom )
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
		�������ε���Ӿ���
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
		��������ε����б�
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
		���µĵ��б���¶����
		@type				points : list
		@param				points : ����ε����ж���
		@return					   : None
		"""
		self.__points = points[:]
		self.__createBorders( points )							# ��������εı�
		self.__calcBound( points )								# ������Ӿ���

	def isPointIn( self, point ) :
		"""
		�ж�ָ�����Ƿ��ڶ������
		�㷨��aijisong
		"""
		if not self.__bound.isPointIn( point ) :				# ����㲻����Ӿ����У���϶����ڶ���΃�
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
	def points( self ) :											# ��ȡ����ε�˳�򶥵�
		return self.__points[:]

	@property
	def bound( self ) :												# ��ȡ����ε���Ӿ���
		return self.__bound

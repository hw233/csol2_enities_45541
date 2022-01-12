# -*- coding: gb18030 -*-
# written by wsf

import BigWorld
import gd
import math
import random
from bwdebug import *
import StringIO
import csconst
import base64
import Function
import zlib
import Language

VERIFY_IMAGE_PAPER_WIDTH = 128
VERIFY_IMAGE_PAPER_HIGH = 64
# 验证图片画布大小
VERIFY_IMAGE_PAPER_SIZE = ( VERIFY_IMAGE_PAPER_WIDTH, VERIFY_IMAGE_PAPER_HIGH )

CHILD_IMAGE_PAPER_WIDTH = 24			# 子图片画布长
CHILD_IMAGE_PAPER_HIGH = 24				# 子图片画布宽
# 子图片大小
CHILD_IMAGE_PAPER_SIZE = ( CHILD_IMAGE_PAPER_WIDTH, CHILD_IMAGE_PAPER_HIGH )

VERYFY_IMAGE_AMOUNT = 2000				# 随机生成的验证图象数量

DISTURB_ARC_COUNT	= 0					# 干扰弧线数量
DISTURB_POINT_COUNT	= 80				# 干扰点数量
DISTURB_LINE_COUNT = 0					# 干扰直线数

VERIFY_PAPER_IMAGE_COLORS = (			# 默认为画布背景色
									( 255, 255, 255 ),
									( 192, 192, 192 ),
									( 176, 192, 206 ),
									( 228, 130, 253 ),
									)

VERIFY_CHILD_IMAGE_COLORS = (			# 验证子图片的颜色集
								( 0, 128, 255 ),
								( 128, 128, 192 ),
								( 0, 0, 0 ),
								( 0, 255, 0 ),
								)
								
def rotatePoint( point, centerPoint, arc ):
	"""
	以centerPoint为中心，把point点旋转arc角度
	"""
	arc = arc * math.pi / 180
	cosValue = math.cos( arc )
	sinValue = math.sin( arc )
	x = int( ( point[0] - centerPoint[0] ) * cosValue - ( point[1] - centerPoint[1] ) * sinValue + centerPoint[0] )
	y = int( ( point[1] - centerPoint[1] ) * cosValue + ( point[0] - centerPoint[0] ) * sinValue + centerPoint[1] )
	return ( x, y )
	
	
class AntiRobotVerify( BigWorld.Base ):
	"""
	反外挂验证管理
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.verifyData = {}		# 验证数据{ entityID:[timerID, callback] }
		
	def triggerVerify( self, entity, callback ):
		"""
		触发验证
		
		@param entity : entity必须是一个可验证entity，即必须有相关属性
		@param callback : 验证完毕后的回调函数，回调函数接受一个参数，True表示通过验证，False则验证失败，根据此结果进行后续处理。
		"""
		try:		# 如果没找到问题和答案，那么不需验证
			answer, questionData = imageVerify.getVerifyImageData()
		except:
			callback( True )
			return
		time = csconst.IMAGE_VERIFY_TIME_MAP[entity.antiRobotCount]
		timerID = self.addTimer( time, 0, entity.id )
		#DEBUG_MSG( "entity(%s) trigger:answer(%s)" % ( entity.getName(), str( answer ) ) )
		self.verifyData[entity.id] = (timerID, callback, answer)
		entity.client.trigerImageVerify( questionData, entity.antiRobotCount )
		
	def onTimer( self, timerID, useArg ):
		try:
			data = self.verifyData[useArg]
		except KeyError:
			INFO_MSG( "keyError : entityID( %i )" % useArg )
			return
		del self.verifyData[useArg]
		data[1]( False )	# 时间到还没回答问题，那么验证不通过
		
	def verify( self, entityID, answer ):
		"""
		验证答案是否正确
		
		@param answer : 问题的答案( x, y )
		"""
		#DEBUG_MSG( "--->>>entityID, answer", entityID, answer )
		try:
			data = self.verifyData[entityID]
		except KeyError:
			ERROR_MSG( "keyError : entityID( %i )" % ( entityID ) )
			return
		del self.verifyData[entityID]
		self.delTimer( data[0] )
		answerData = data[2]
		#DEBUG_MSG( "---->>>>answerData", answerData )
		if answerData[1] < answer[0] < answerData[2] and answerData[3] < answer[1] < answerData[4]:
			data[1]( True )
		else:
			data[1]( False )
	
	def cancelVerify( self, entityID ):
		"""
		选择人物界面的取消按钮执行 add by wuxo 2011-10-25
		"""
		try:
			data = self.verifyData[entityID]
		except KeyError:
			ERROR_MSG( "keyError : entityID( %i )" % ( entityID ) )
			return
		del self.verifyData[entityID]
		self.delTimer( data[0] )
		
	
class ImageVerifyMgr:
	"""
	验证图片管理
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		assert ImageVerifyMgr._instance is None
		self.verifyData = {}	# { (x1, x2, y1, y2):图片数据 }
		self.initVerifyImage()
		
	@classmethod
	def instance( self):
		if self._instance is None:
			self._instance = ImageVerifyMgr()
		return self._instance
		
	def initVerifyImage( self ):
		"""
		初始化验证图形
		"""
		self.initFileVerifyImage()
		INFO_MSG( "verify image count:%i" % len( self.verifyData ) )
		
	def initFileVerifyImage( self ):
		"""
		使用配置好的验证图片初始化
		"""
		jpgFiles = Language.searchConfigFileABS( "config/server/verifyImage", ".DDS" )
		successCount = 0
		failedCount = 0
		for filePath in jpgFiles:
			jpgfile = open( filePath, "rb" )
			try:
				data = zlib.compress( base64.b64encode( jpgfile.read() ) )
			except:
				failedCount += 1
				jpgfile.close()
				return
			jpgfile.close()
			try:
				key = [ int( x ) for x in filePath.split( "." )[0].split( "/" )[-1].split( "_" ) ]
				key = ( key[0], key[1], key[1] + CHILD_IMAGE_PAPER_WIDTH, key[2], key[2] + CHILD_IMAGE_PAPER_HIGH )
			except:
				failedCount += 1
				ERROR_MSG( "fileName:%s" % filePath )
				continue
			self.verifyData[key] = data
			successCount += 1
			
	def initGDVerifyImage( self ):
		"""
		代码使用gd库生成验证图片方式
		"""
		for i in xrange( VERYFY_IMAGE_AMOUNT ):
			verifyImage = VerifyImage()
			verifyImage.initialize( VERIFY_PAPER_IMAGE_COLORS )
			fileName = verifyImage.getFileName()
			key = tuple( [ int( e ) for e in fileName.split( "_" ) ] )		# 使用tuple作为key
			stringIO = StringIO.StringIO()
			verifyImage.writeJpeg2StringIO( stringIO )
			# 使用base64对jpeg图片数据进行编码，否则在传输过程中引擎会丢掉一些控制字符使得客户端接收到数据后不能正确转化成texture
			data = zlib.compress( base64.b64encode( stringIO.getvalue() ) )
			self.verifyData[key] = data
			
	def getVerifyImageData( self ):
		"""
		随机获得一张验证图片的字符串形式和正确答案（图像坐标范围）
		return ( tuple, data )
		tuple为( 图片编号, x1, x2, y1, y2 ), data为图片数据
		"""
		key = random.sample( self.verifyData, 1 )[0]
		return key, self.verifyData[key]
		
		
class VerifyImage:
	"""
	验证图片
	"""
	classInitialCount = 0		# 每生成一张验证图片会加1，验证图片实例化计数器
	def __init__( self ):
		"""
		"""
		self.img = gd.image( VERIFY_IMAGE_PAPER_SIZE )
		self.fileName = ""
		self.color = ( 255, 255, 255 )	# 默认的画布颜色
		VerifyImage.classInitialCount += 1
		
	def getAllowPosition( self, positionList ):
		"""
		获得合法的坐标
		"""
		x = random.randint( 0, VERIFY_IMAGE_PAPER_WIDTH - CHILD_IMAGE_PAPER_WIDTH )
		y = random.randint( 0, VERIFY_IMAGE_PAPER_HIGH - CHILD_IMAGE_PAPER_HIGH )
		for position in positionList:
			xPosition = position[0]
			yPosition = position[1]
			notAllow = max( xPosition - CHILD_IMAGE_PAPER_WIDTH, 0 ) <= x <= xPosition + CHILD_IMAGE_PAPER_WIDTH and \
						max( yPosition - CHILD_IMAGE_PAPER_HIGH, 0 ) <= y <= yPosition + CHILD_IMAGE_PAPER_HIGH
			if notAllow:
				return self.getAllowPosition( positionList )
		return ( x, y )
		
	def initialize( self, colors ):
		"""
		"""
		self.initColor( colors )
		answerPosition = ( random.randint( 0, VERIFY_IMAGE_PAPER_WIDTH - CHILD_IMAGE_PAPER_WIDTH ), random.randint( 0, VERIFY_IMAGE_PAPER_HIGH - CHILD_IMAGE_PAPER_HIGH ) )
		imgClassList = random.sample( IMAGE_LIST, 2 )		# 获得随机的两个子图片类
		self.setFileName( answerPosition )					# 文件名命名规则与答案位置有关
		childPaperColor = self.getColor()
		
		# 生成4张子图片并确定位置复制到画布生成验证图片
		commonImageClass = imgClassList[1]
		# 非答案图片
		commonImageFillColors = random.sample( VERIFY_CHILD_IMAGE_COLORS, 1 )
		positionList = [answerPosition]
		for i in xrange( 3 ):	# 随机复制的位置不能重叠，每一次生成随机位置都要检查位置是否合法
			try:		# 有可能出现maximum recursion depth exceeded in cmp
				allowPosition = self.getAllowPosition( positionList )
			except RuntimeError:
				DEBUG_MSG( "--->>>maximum recursion depth exceeded in cmp." )
				x = random.randint( 0, VERIFY_IMAGE_PAPER_WIDTH - CHILD_IMAGE_PAPER_WIDTH )
				y = random.randint( 0, VERIFY_IMAGE_PAPER_HIGH - CHILD_IMAGE_PAPER_HIGH )
				allowPosition = ( x, y )
			positionList.append( allowPosition )
			commonImageClass( CHILD_IMAGE_PAPER_SIZE, childPaperColor, commonImageFillColors ).copyMergeTo( self.img, allowPosition )
		imgClassList[0]( CHILD_IMAGE_PAPER_SIZE, childPaperColor, VERIFY_CHILD_IMAGE_COLORS ).copyMergeTo( self.img, answerPosition )
		
		self.disturbImage()
		
		
	def disturbImage( self ):
		"""
		图像干扰
		"""
		for i in xrange( DISTURB_ARC_COUNT ):	# 画两条弧线
			centerPoint = ( random.randint( 0, 128 ), random.randint( 0, 64 ) )
			size = ( 48, 48 )
			self.img.arc( centerPoint, size, 0, random.randint( 90, 180 ), self.getRandomColor() )
		color = self.getRandomColor()
		for i in xrange( DISTURB_POINT_COUNT ):		# 生成干扰点
			xpoint = random.randint( 0, 128 )
			ypoint = random.randint( 0, 64 )
			self.img.setPixel( ( xpoint, ypoint ), color )
			self.img.setPixel( (xpoint-1, ypoint+1), color )
			self.img.setPixel( (xpoint+1, ypoint-1), color )
			self.img.setPixel( (xpoint-1, ypoint-1), color )
			self.img.setPixel( (xpoint+1, ypoint+1), color )
		color = self.getRandomColor()
		for i in xrange( DISTURB_LINE_COUNT ):	# 生成干扰直线
			point1 = ( random.randint( 0, 128 ), random.randint( 0, 64 ) )
			point2 = ( random.randint( 0, 128 ), random.randint( 0, 64 ) )
			self.img.line( point1, point2, color )
			
	def initColor( self, colors ):
		"""
		"""
		for color in colors:
			self.img.colorAllocate( color )
		self.color = self.getRandomColor()
		self.img.fill( (0,0), self.color )
		
	def getColor( self ):
		"""
		@rtype : tuple，背景颜色
		"""
		return self.color
		
	def getRandomColor( self ):
		return random.randint( 0, self.img.colorsTotal() - 1 )
		
	def setFileName( self, answerPosition ):
		x = answerPosition[0]
		y = answerPosition[1]
		positionList = [x, x+CHILD_IMAGE_PAPER_WIDTH, y, y+CHILD_IMAGE_PAPER_HIGH]
		self.fileName = str( VerifyImage.classInitialCount ) + "_" + "_".join( [str(e) for e in positionList] )
		
	def getFileName( self ):
		"""
		fileName格式例如："1_x1_x2_y1_y2"
		使用"_"分隔字符串："1"表示图片编号，不同图片对应不同编号；x1、x2、y1、y2为正确的坐标范围。
		"""
		return self.fileName
		
	def writeJpeg2File( self ):
		"""
		测试用
		"""
		fileName = r"test/" + self.getFileName() + ".jpg"
		self.img.writeJpeg( fileName )
		
	def writeJpeg2StringIO( self, stringIO ):
		self.img.writeJpeg( stringIO )
		
		
class ChildImage( gd.image ):
	"""
	"""
	def __init__( self, size, paperColor, colors ):
		gd.image.__init__( self, size )
		self.initColor( paperColor, colors )
		self.init()
		
	def initColor( self, paperColor, colors ):
		self.colorAllocate( VERIFY_PAPER_IMAGE_COLORS[paperColor] )	# 第0位是背景色
		for color in colors:
			self.colorAllocate( color )
		self.fill( ( 0, 0 ), 0 )
		
	def init( self ):
		ERROR_MSG( "cannot instialize ChildImage!" )
		
	def getRandomColor( self ):
		"""
		获得随机颜色
		"""
		return random.randint( 1, self.colorsTotal() - 1 )	# 第一种颜色是背景色
		
	def getCenterPoint( self ):
		"""
		获得中心点
		"""
		size = self.size()
		return ( size[0] / 2, size[1] / 2 )
		
	def getStartPoint( self ):
		"""
		获得开始点
		"""
		size = self.size()
		return ( size[0] / 2, 0 )
		
		
class TriangleImage( ChildImage ):
	"""
	三角形
	"""
	def init( self ):
		startPoint = self.getStartPoint()
		centerPoint = self.getCenterPoint()
		point1 = rotatePoint( startPoint, centerPoint, random.randint( 40, 80 ) )
		point2 = rotatePoint( startPoint, centerPoint, random.randint( 160, 200 ) )
		point3 = rotatePoint( startPoint, centerPoint, random.randint( 280, 320 ) )
		color = self.getRandomColor()
		self.polygon( [ point1, point2, point3 ], color, color )
		
		
class RectangleImage( ChildImage ):
	"""
	矩形
	"""
	def init( self ):
		size = self.size()
		centerPoint = self.getCenterPoint()
		points = ( (-0.5,0.5), (0.5,-0.5) )
		points = [ (int(e[0] * size[0]) + centerPoint[0], int(e[1] * size[1]) + centerPoint[1]) for e in points ]
		color = self.getRandomColor()
		self.rectangle( points[0], points[1], color, color )
		
		
class PentacleImage( ChildImage ):
	"""
	五角星
	"""
	def init( self ):
		startPoint = self.getStartPoint()
		centerPoint = self.getCenterPoint()
		point1 = rotatePoint( startPoint, centerPoint, random.randint( 0, 360 ) )
		point2 = rotatePoint( point1, centerPoint, 72 )
		point3 = rotatePoint( point2, centerPoint, 72 )
		point4 = rotatePoint( point3, centerPoint, 72 )
		point5 = rotatePoint( point4, centerPoint, 72 )
		color = self.getRandomColor()
		self.line( point1, point3, color )
		self.line( point2, point4, color )
		self.line( point3, point5, color )
		self.line( point4, point1, color )
		self.line( point5, point2, color )
		
		
class CircleImage( ChildImage ):
	"""
	圆
	"""
	def init( self ):
		"""
		"""
		size = self.size()
		startPoint = self.getStartPoint()
		centerPoint = self.getCenterPoint()
		color = self.getRandomColor()
		self.arc( centerPoint, size, 0, 360, color )
		self.filledArc( centerPoint, size, 0, 360, color, 0 )
		
class pentagonImage( ChildImage ):
	"""
	五边形
	"""
	def init( self ):
		"""
		"""
		startPoint = self.getStartPoint()
		centerPoint = self.getCenterPoint()
		point1 = rotatePoint( startPoint, centerPoint, random.randint( 0, 360 ) )
		point2 = rotatePoint( point1, centerPoint, 72 )
		point3 = rotatePoint( point2, centerPoint, 72 )
		point4 = rotatePoint( point3, centerPoint, 72 )
		point5 = rotatePoint( point4, centerPoint, 72 )
		color = self.getRandomColor()
		self.polygon( [point1, point2, point3, point4, point5], color, color )
		
IMAGE_LIST = (								# 图片类列表
				TriangleImage, 
				RectangleImage, 
				PentacleImage, 
				CircleImage, 
				pentagonImage,
				)

imageVerify = ImageVerifyMgr.instance()


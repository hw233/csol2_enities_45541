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
# ��֤ͼƬ������С
VERIFY_IMAGE_PAPER_SIZE = ( VERIFY_IMAGE_PAPER_WIDTH, VERIFY_IMAGE_PAPER_HIGH )

CHILD_IMAGE_PAPER_WIDTH = 24			# ��ͼƬ������
CHILD_IMAGE_PAPER_HIGH = 24				# ��ͼƬ������
# ��ͼƬ��С
CHILD_IMAGE_PAPER_SIZE = ( CHILD_IMAGE_PAPER_WIDTH, CHILD_IMAGE_PAPER_HIGH )

VERYFY_IMAGE_AMOUNT = 2000				# ������ɵ���֤ͼ������

DISTURB_ARC_COUNT	= 0					# ���Ż�������
DISTURB_POINT_COUNT	= 80				# ���ŵ�����
DISTURB_LINE_COUNT = 0					# ����ֱ����

VERIFY_PAPER_IMAGE_COLORS = (			# Ĭ��Ϊ��������ɫ
									( 255, 255, 255 ),
									( 192, 192, 192 ),
									( 176, 192, 206 ),
									( 228, 130, 253 ),
									)

VERIFY_CHILD_IMAGE_COLORS = (			# ��֤��ͼƬ����ɫ��
								( 0, 128, 255 ),
								( 128, 128, 192 ),
								( 0, 0, 0 ),
								( 0, 255, 0 ),
								)
								
def rotatePoint( point, centerPoint, arc ):
	"""
	��centerPointΪ���ģ���point����תarc�Ƕ�
	"""
	arc = arc * math.pi / 180
	cosValue = math.cos( arc )
	sinValue = math.sin( arc )
	x = int( ( point[0] - centerPoint[0] ) * cosValue - ( point[1] - centerPoint[1] ) * sinValue + centerPoint[0] )
	y = int( ( point[1] - centerPoint[1] ) * cosValue + ( point[0] - centerPoint[0] ) * sinValue + centerPoint[1] )
	return ( x, y )
	
	
class AntiRobotVerify( BigWorld.Base ):
	"""
	�������֤����
	"""
	def __init__( self ):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.verifyData = {}		# ��֤����{ entityID:[timerID, callback] }
		
	def triggerVerify( self, entity, callback ):
		"""
		������֤
		
		@param entity : entity������һ������֤entity�����������������
		@param callback : ��֤��Ϻ�Ļص��������ص���������һ��������True��ʾͨ����֤��False����֤ʧ�ܣ����ݴ˽�����к�������
		"""
		try:		# ���û�ҵ�����ʹ𰸣���ô������֤
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
		data[1]( False )	# ʱ�䵽��û�ش����⣬��ô��֤��ͨ��
		
	def verify( self, entityID, answer ):
		"""
		��֤���Ƿ���ȷ
		
		@param answer : ����Ĵ�( x, y )
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
		ѡ����������ȡ����ťִ�� add by wuxo 2011-10-25
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
	��֤ͼƬ����
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		assert ImageVerifyMgr._instance is None
		self.verifyData = {}	# { (x1, x2, y1, y2):ͼƬ���� }
		self.initVerifyImage()
		
	@classmethod
	def instance( self):
		if self._instance is None:
			self._instance = ImageVerifyMgr()
		return self._instance
		
	def initVerifyImage( self ):
		"""
		��ʼ����֤ͼ��
		"""
		self.initFileVerifyImage()
		INFO_MSG( "verify image count:%i" % len( self.verifyData ) )
		
	def initFileVerifyImage( self ):
		"""
		ʹ�����úõ���֤ͼƬ��ʼ��
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
		����ʹ��gd��������֤ͼƬ��ʽ
		"""
		for i in xrange( VERYFY_IMAGE_AMOUNT ):
			verifyImage = VerifyImage()
			verifyImage.initialize( VERIFY_PAPER_IMAGE_COLORS )
			fileName = verifyImage.getFileName()
			key = tuple( [ int( e ) for e in fileName.split( "_" ) ] )		# ʹ��tuple��Ϊkey
			stringIO = StringIO.StringIO()
			verifyImage.writeJpeg2StringIO( stringIO )
			# ʹ��base64��jpegͼƬ���ݽ��б��룬�����ڴ������������ᶪ��һЩ�����ַ�ʹ�ÿͻ��˽��յ����ݺ�����ȷת����texture
			data = zlib.compress( base64.b64encode( stringIO.getvalue() ) )
			self.verifyData[key] = data
			
	def getVerifyImageData( self ):
		"""
		������һ����֤ͼƬ���ַ�����ʽ����ȷ�𰸣�ͼ�����귶Χ��
		return ( tuple, data )
		tupleΪ( ͼƬ���, x1, x2, y1, y2 ), dataΪͼƬ����
		"""
		key = random.sample( self.verifyData, 1 )[0]
		return key, self.verifyData[key]
		
		
class VerifyImage:
	"""
	��֤ͼƬ
	"""
	classInitialCount = 0		# ÿ����һ����֤ͼƬ���1����֤ͼƬʵ����������
	def __init__( self ):
		"""
		"""
		self.img = gd.image( VERIFY_IMAGE_PAPER_SIZE )
		self.fileName = ""
		self.color = ( 255, 255, 255 )	# Ĭ�ϵĻ�����ɫ
		VerifyImage.classInitialCount += 1
		
	def getAllowPosition( self, positionList ):
		"""
		��úϷ�������
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
		imgClassList = random.sample( IMAGE_LIST, 2 )		# ��������������ͼƬ��
		self.setFileName( answerPosition )					# �ļ��������������λ���й�
		childPaperColor = self.getColor()
		
		# ����4����ͼƬ��ȷ��λ�ø��Ƶ�����������֤ͼƬ
		commonImageClass = imgClassList[1]
		# �Ǵ�ͼƬ
		commonImageFillColors = random.sample( VERIFY_CHILD_IMAGE_COLORS, 1 )
		positionList = [answerPosition]
		for i in xrange( 3 ):	# ������Ƶ�λ�ò����ص���ÿһ���������λ�ö�Ҫ���λ���Ƿ�Ϸ�
			try:		# �п��ܳ���maximum recursion depth exceeded in cmp
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
		ͼ�����
		"""
		for i in xrange( DISTURB_ARC_COUNT ):	# ����������
			centerPoint = ( random.randint( 0, 128 ), random.randint( 0, 64 ) )
			size = ( 48, 48 )
			self.img.arc( centerPoint, size, 0, random.randint( 90, 180 ), self.getRandomColor() )
		color = self.getRandomColor()
		for i in xrange( DISTURB_POINT_COUNT ):		# ���ɸ��ŵ�
			xpoint = random.randint( 0, 128 )
			ypoint = random.randint( 0, 64 )
			self.img.setPixel( ( xpoint, ypoint ), color )
			self.img.setPixel( (xpoint-1, ypoint+1), color )
			self.img.setPixel( (xpoint+1, ypoint-1), color )
			self.img.setPixel( (xpoint-1, ypoint-1), color )
			self.img.setPixel( (xpoint+1, ypoint+1), color )
		color = self.getRandomColor()
		for i in xrange( DISTURB_LINE_COUNT ):	# ���ɸ���ֱ��
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
		@rtype : tuple��������ɫ
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
		fileName��ʽ���磺"1_x1_x2_y1_y2"
		ʹ��"_"�ָ��ַ�����"1"��ʾͼƬ��ţ���ͬͼƬ��Ӧ��ͬ��ţ�x1��x2��y1��y2Ϊ��ȷ�����귶Χ��
		"""
		return self.fileName
		
	def writeJpeg2File( self ):
		"""
		������
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
		self.colorAllocate( VERIFY_PAPER_IMAGE_COLORS[paperColor] )	# ��0λ�Ǳ���ɫ
		for color in colors:
			self.colorAllocate( color )
		self.fill( ( 0, 0 ), 0 )
		
	def init( self ):
		ERROR_MSG( "cannot instialize ChildImage!" )
		
	def getRandomColor( self ):
		"""
		��������ɫ
		"""
		return random.randint( 1, self.colorsTotal() - 1 )	# ��һ����ɫ�Ǳ���ɫ
		
	def getCenterPoint( self ):
		"""
		������ĵ�
		"""
		size = self.size()
		return ( size[0] / 2, size[1] / 2 )
		
	def getStartPoint( self ):
		"""
		��ÿ�ʼ��
		"""
		size = self.size()
		return ( size[0] / 2, 0 )
		
		
class TriangleImage( ChildImage ):
	"""
	������
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
	����
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
	�����
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
	Բ
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
	�����
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
		
IMAGE_LIST = (								# ͼƬ���б�
				TriangleImage, 
				RectangleImage, 
				PentacleImage, 
				CircleImage, 
				pentagonImage,
				)

imageVerify = ImageVerifyMgr.instance()


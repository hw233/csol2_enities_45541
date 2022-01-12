# -*- coding: gb18030 -*-
#
# $Id: Function.py,v 1.23 2008-08-26 02:29:59 kebiao Exp $

"""
��������ģ��
"""

import re
import cschannel_msgs
import ShareTexts as ST
import os
import types
import inspect
import random
import time
import math
import BigWorld
import Math
import ResMgr
import csarithmetic
import zlib
import base64


def getMethodName( method ) :
	"""
	��ȡ������
	@type				method : method
	@param				mehtod : ������ʵ���������෽��
	@rtype					   : str
	@return					   : ���ط�����
	"""
	assert inspect.ismethod( method ), \
		"%s is not a method" % str( method )				# ������ʵ���������෽��
	funcName = method.im_func.func_name						# ��ȡ������
	imSelf = method.im_self									# ��ȡ����������ʵ��
	if hasattr( imSelf, funcName ) :						# �����ʵ������ֱ���ҵ�����
		return funcName										# ��˵������ private ������ֱ�ӷ��ط�����

	if type( imSelf ) is types.ClassType or \
		type( imSelf ) is types.TypeType :					# ������෽��
			clses = inspect.getmro( method.im_self )		# ��ͨ�� im_self ��ȡ����ʵ�������л���
	else :
		clses = inspect.getmro( method.im_class )			# ��ͨ�� im_class ��ȡ����ʵ�������л���
	for cls in clses :										# ͨ���������������Ѱ��
		methodName = "_%s%s" % ( cls.__name__, funcName )	# Ϊ˽�з��������ǰ׺
		methodName = re.sub( "^_*", "_", methodName )
		tmpMethod = getattr( imSelf, methodName, None )		# ��ȡ˽�з���
		if tmpMethod is None : continue						# ���˽�з��������ڴ��࣬�����
		if tmpMethod != method : continue					# ���������ͬ���Ƶ���һ�������е�˽�з����������
		return methodName									# ���򣬷����ҵ��ķ�����
	raise "%s is not a method" % str( method )				# ���������ﲻ�ᱻִ��


# --------------------------------------------------------------------
def initRand():
	"""
	��ʼ���������
	"""
	random.seed(int((time.time()*100)%256))

def estimate( odds, precision = 100 ):
	"""
	�жϼ���odds������ȱʡ1%
	@param			odds	  : ���ּ���
	@type			odds	  : int16
	@param			precision : ���Ȳ���
	@type			precision : integer
	@return					  : True ���ڼ���,False �����ڼ���
	@rtype					  : boolean
	"""
	if odds <= 0:
		return False
	if odds >= precision:
		return True
	r = int( random.random() * precision + 1 )
	if odds >= r:
		return True
	return False

def getTimestamp():
	"""
	���ʱ�����
	"""
	return int( ( BigWorld.time() * 10 ) % 1024 )

def movePosition( srcPos, desPos, distance ):
	"""
	�����ƶ�λ�ã���Ŀ�ĵ�һ������
	@param	srcPos		: ԭλ��
	@type	srcPos		: Vector3
	@param	desPos		: Ŀ��λ��
	@type	desPos		: Vector3
	@param	distance	: ��Ŀ�ĵ�ľ���
	@type	distance	: float
	@rtype				: Vector3
	@return				: ��Ŀ�ĵ�distance�����λ��
	"""
	vDir = Math.Vector3()
	vDir = desPos - srcPos
	vDir.normalise()
	pos1 = Math.Vector3( srcPos )
	pos2 = Math.Vector3( desPos )
	fDist = pos1.flatDistTo( pos2 )
	if fDist <= distance:
		return srcPos
	fDist = fDist - distance
	vDir.x = vDir.x * fDist
	vDir.y = vDir.y * fDist
	vDir.z = vDir.z * fDist
	vPos = Math.Vector3()
	vPos = srcPos + vDir
	return vPos

def distancePosition( srcPos, desPos, distance ):
	"""
	�����ƶ�λ�ã���Ŀ�ĵ�һ������
	@param	srcPos		: ԭλ��
	@type	srcPos		: Vector3
	@param	desPos		: Ŀ��λ��
	@type	desPos		: Vector3
	@param	distance	: ��Ŀ�ĵ�ľ���
	@type	distance	: float
	@rtype				: Vector3
	@return				: ��Ŀ�ĵ�distance�����λ��
	"""
	vDir = Math.Vector3()
	vDir = desPos - srcPos
	vDir.normalise()
	vDir.x = vDir.x * distance
	vDir.y = vDir.y * distance
	vDir.z = vDir.z * distance
	vPos = Math.Vector3()
	vPos = srcPos + vDir
	return vPos

def randNewPosForPos( srcPos, distance ):
	"""
	��ָ���㸽����һ�������
	@param	srcPos		: ԭλ��
	@type	srcPos		: Vector3
	@param	distance	: ��Ŀ�ĵ�ľ���
	@type	distance	: float
	"""
	range = random.random() * distance
	randAngle = random.random() * 3.1415926 * 2
	vPos = Math.Vector3()
	vPos.x = srcPos.x + math.cos( randAngle ) * range
	vPos.z = srcPos.z + math.sin( randAngle ) * range
	vPos.y = srcPos.y
	return vPos

def collideCaluc( pos, spaceID ):
	"""
	��ײ����
	"""
	src = pos
	#�������Ϸ���ĵ����ײλ��
	dst = pos
	dst.y += 9999
	upPos = BigWorld.collide( spaceID, src, dst )
	#�������·���ĵ����ײλ��
	dst = pos
	dst.y -= 9999
	downPos = BigWorld.collide( spaceID, src, dst )
	if upPos == None and downPos == None:
		return pos
	if upPos == None:
		return downPos
	if downPos == None:
		return upPos
	dist1 = csarithmetic.distancePP3( pos, upPos )
	dist2 = csarithmetic.distancePP3( pos, downPos )
	if dist1 <= dist2:
		return upPos
	return downPos

def calcuDirFromYaw( yaw ):
	"""
	ͨ��yaw���������
	"""
	direction = Math.Vector3()
	direction.x = math.sin( yaw )
	direction.y = 0
	direction.z = math.cos( yaw )
	return direction


# --------------------------------------------------------------------
class Functor:
	"""
	�������������Callback�����ࡣ
		@ivar _fn:			Callback����
		@type _fn:			function
		@ivar _args:		����
		@type _args:		tuple
	"""

	def __init__( self, fn, *args ):
		"""
		���캯����
			@param fn:			Callback����
			@type fn:			function
			@param args:		����
			@type args:			tuple
		"""
		self._fn = fn
		self._args = args

	def __call__( self, *args ):
		"""
		����Callback����fn��
			@param args:		����
			@type args:			tuple
			@return:			Callback�����ķ���ֵ
		"""
		return self._fn( *( self._args + args ) )


def searchFile( searchPath, exts ):
	"""
	����ָ����Ŀ¼(searchPath)���������з���ָ������չ��(exts)���ļ�����Ŀ¼����
	ע�⣺���ǲ����ж�һ���ļ��Ƿ����ļ��У�Ҳ�����еݹ���ң���������չ����ָ��Ŀ¼���в��ң�

	@param searchPath: STRING or tuple of STRING, Ҫ������·�����б�
	@param       exts: STRING or tuple of STRING, Ҫ��������չ�����б���ÿ����չ�����������Ե㿪ͷ�ģ��磺.txt
	@return: array of STRING
	"""
	assert isinstance( exts, (str, tuple, list) )
	assert isinstance( searchPath, (str, tuple, list) )
	if isinstance( exts, str ):
		exts = ( exts, )
	if isinstance( searchPath, str ):
		searchPaths = [ searchPath, ]
	else:
		searchPaths = list( searchPath )

	files = []
	for searchPath in searchPaths:
		section = ResMgr.openSection( searchPath )
		assert section is not None, "can't open section %s." % searchPath

		if searchPath[-1] not in "\\/":
			searchPath += "/"

		for key in section.keys():
			name, ext = os.path.splitext( key )		# ��ȡ��չ��
			if ext in exts:							# ��չ��ƥ��
				files.append( searchPath + key )
		ResMgr.purge( searchPath )
	return files

def searchModuleName( searchPath ):
	"""
	"""
	modulesfiles = searchFile( searchPath, [ ".py", ".pyc", ".pyo" ] )
	moduleNames= set([])
	for i in modulesfiles:
		moduleNames.add( i.split(".")[0].split("/")[-1] )
	return moduleNames

def zipFloat( floatVal, percentage = 10000 ):
	"""
	ѹ��һ�������� by kebiao
	@param floatVal		: ������ֵ
	@param percentage	: ѹ������
	@return type		: int32
	"""
	return int( floatVal * percentage )

def unzipFloat( intVal, percentage = 10000 ):
	"""
	��ѹ��һ��ѹ�����ĸ����� by kebiao
	@param intVal		: ��ֵ
	@param percentage	: ѹ������
	@return type		: float
	"""
	return intVal / float( percentage )

def ipToStr( val ):
	"""
	ת��int32��ip��ַΪ�Ե�(".")�ָ����ַ���ģʽ��
	����ipToStr( 436211884 ) --> '172.16.0.26'
	"""
	return "%i.%i.%i.%i" % ( val & 0xff, ( val >> 8 ) & 0xff, ( val >> 16 ) & 0xff, ( val >> 24 ) & 0xff )


class UIDFactory:
	"""
	64λUID��������
	�˽ӿ�ֻ������cellapp��baseapp�е��á�
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		self._component_flag = -1		# see also: self._init()
		self._last_id = 0

	def __call__( self ):
		"""
		����һ��ȫ���Ե�ΨһID
		@rtype INT64
		"""
		# ע�����ڵ�ǰ�������𶯻��Ƶ�ԭ��������ʱ����һ��ʼ�ͳ�ʼ��cellapp��baseapp��idֵ
		# ����ֻ���Ƴٵ���һ��ȡֵ��ʱ���ʼ��
		if self._component_flag <= 0:
			self._init()

		t = int( time.time() )

		self._last_id += 1
		if self._last_id > 0xffffff:
			self._last_id = 0
		return ( t << 32 ) + ( self._component_flag << 24 ) + self._last_id

	def _init( self ):
		"""
		��ʼ��������ص�UIDǰ׺
		"""
		# init watcher key by bigworld component
		if BigWorld.component == "base":
			_watcher_key = "id"
			# ��ֵ���������ֵ�����baseapp����cellapp������ID��Ҳ��Ϊ�˱���idֵ��ͻ
			# ����ʹ��һ���ֽڵĴ�С����ʾ��baseapp��cellapp��id
			# Ҳ�������������Էֱ��ʾ128��baseapp��cellapp
			_app_flag = 0x80
		elif BigWorld.component == "cell":
			_watcher_key = "cellAppID"
			_app_flag = 0
		else:
			assert False

		appID = int( BigWorld.getWatcher( _watcher_key ) )
		assert appID > 0	# ����ڷ�����������ʱ�ͳ�ʼ�������ֵ���п��ܻ�С��0
		self._component_flag = appID | _app_flag

	@classmethod
	def instance( SELF ):
		if SELF._instance is None:
			SELF._instance = SELF()
		return SELF._instance

def newUID():
	"""
	"""
	return UIDFactory.instance()()

def switchMoney( money ):
	"""
	ת��������ʾ��ʽ ���ڸú������÷�Χ�ȽϹ� ���ݿ´����Ľ��� ���������ӹ����ӿ� by����
	"""
	sign = ""
	if money < 0:
		money = abs( money )
		sign = "-"
	gold = int( money/10000 )
	silver = int( ( money%10000 )/100 )
	coin = int( ( money%10000 )%100 )
	moneyText = ""
	if gold > 0: moneyText += cschannel_msgs.ON_LINE_GIFT_INFO_1%gold
	if silver > 0: moneyText += cschannel_msgs.ON_LINE_GIFT_INFO_2%silver
	if coin > 0: moneyText += cschannel_msgs.ON_LINE_GIFT_INFO_3%coin
	return sign + moneyText
		
		
def getIconStringByPath( path ):
	"""
	��ͼ��ת��Ϊbase64�Ĵ� by ����
	"""
	iconString = ""
	try:
		file = open( path, "rb" )
	except:
		return None
		
	try:
		iconString = zlib.compress( base64.b64encode( file.read() ) )
		file.close()
	except:
		file.close()
		return None
	return iconString
	
def getIconByString( iString ):
	"""
	ͨ�������ַ������ͼ���ַ��� by ����
	���ⲿ��ͨ�� csol.binaryToTexture( imgStr ) ���ͼ��
	"""
	if iString is None:
		return None
	try:
		return base64.b64decode( zlib.decompress( iString ) )	#imgStr
	except:
		return None
		
	 
def makeFile( path, fileName, file ):
	"""
	ͨ��·�������ʹ����ļ� by ����
	���ƣ�ֻ�ܴ���resĿ¼��
	"""
	path_file = path + "/" + fileName
	d = open( path_file, "wb" )
	d.write( file )
	d.close()

def get3DVectorFromStr( str, delim = " " ):
	"""
	����delim�ָ����ַ����л�ȡһ��3d tuple
	���磺delim == ',' str == '1,2,3'
	���أ�( 1.0, 2.0, 3.0 )
	"""
	assert len( delim ) == 1
	
	tmp = str.split( delim )
	assert len( tmp ) == 3
	
	x = float( tmp[0] )
	y = float( tmp[1] )
	z = float( tmp[2] )
	
	return ( x, y, z )
	

# Function.py

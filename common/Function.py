# -*- coding: gb18030 -*-
#
# $Id: Function.py,v 1.23 2008-08-26 02:29:59 kebiao Exp $

"""
公共函数模块
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
	获取方法名
	@type				method : method
	@param				mehtod : 必须是实例方法或类方法
	@rtype					   : str
	@return					   : 返回方法名
	"""
	assert inspect.ismethod( method ), \
		"%s is not a method" % str( method )				# 必须是实例方法或类方法
	funcName = method.im_func.func_name						# 获取方法名
	imSelf = method.im_self									# 获取方法所属的实例
	if hasattr( imSelf, funcName ) :						# 如果在实例中能直接找到方法
		return funcName										# 则说明不是 private 方法，直接返回方法名

	if type( imSelf ) is types.ClassType or \
		type( imSelf ) is types.TypeType :					# 如果是类方法
			clses = inspect.getmro( method.im_self )		# 则，通过 im_self 获取方法实例的所有基类
	else :
		clses = inspect.getmro( method.im_class )			# 则，通过 im_class 获取方法实例的所有基类
	for cls in clses :										# 通过方法名逐个基类寻找
		methodName = "_%s%s" % ( cls.__name__, funcName )	# 为私有方法添加类前缀
		methodName = re.sub( "^_*", "_", methodName )
		tmpMethod = getattr( imSelf, methodName, None )		# 获取私有方法
		if tmpMethod is None : continue						# 如果私有方法不属于此类，则继续
		if tmpMethod != method : continue					# 如果遇到相同名称的另一个基类中的私有方法，则继续
		return methodName									# 否则，返回找到的方法名
	raise "%s is not a method" % str( method )				# 理论上这里不会被执行


# --------------------------------------------------------------------
def initRand():
	"""
	初始化随机函数
	"""
	random.seed(int((time.time()*100)%256))

def estimate( odds, precision = 100 ):
	"""
	判断几率odds，精度缺省1%
	@param			odds	  : 出现几率
	@type			odds	  : int16
	@param			precision : 精度参数
	@type			precision : integer
	@return					  : True 存在几率,False 不存在几率
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
	获得时间戳。
	"""
	return int( ( BigWorld.time() * 10 ) % 1024 )

def movePosition( srcPos, desPos, distance ):
	"""
	计算移动位置，离目的地一定距离
	@param	srcPos		: 原位置
	@type	srcPos		: Vector3
	@param	desPos		: 目标位置
	@type	desPos		: Vector3
	@param	distance	: 离目的点的距离
	@type	distance	: float
	@rtype				: Vector3
	@return				: 离目的点distance距离的位置
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
	计算移动位置，离目的地一定距离
	@param	srcPos		: 原位置
	@type	srcPos		: Vector3
	@param	desPos		: 目标位置
	@type	desPos		: Vector3
	@param	distance	: 离目的点的距离
	@type	distance	: float
	@rtype				: Vector3
	@return				: 离目的点distance距离的位置
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
	在指定点附近找一个随机点
	@param	srcPos		: 原位置
	@type	srcPos		: Vector3
	@param	distance	: 离目的点的距离
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
	碰撞计算
	"""
	src = pos
	#计算向上方向的点的碰撞位置
	dst = pos
	dst.y += 9999
	upPos = BigWorld.collide( spaceID, src, dst )
	#计算向下方向的点的碰撞位置
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
	通过yaw计算出方向
	"""
	direction = Math.Vector3()
	direction.x = math.sin( yaw )
	direction.y = 0
	direction.z = math.cos( yaw )
	return direction


# --------------------------------------------------------------------
class Functor:
	"""
	构造任意参数的Callback函数类。
		@ivar _fn:			Callback函数
		@type _fn:			function
		@ivar _args:		参数
		@type _args:		tuple
	"""

	def __init__( self, fn, *args ):
		"""
		构造函数。
			@param fn:			Callback函数
			@type fn:			function
			@param args:		参数
			@type args:			tuple
		"""
		self._fn = fn
		self._args = args

	def __call__( self, *args ):
		"""
		调用Callback函数fn。
			@param args:		参数
			@type args:			tuple
			@return:			Callback函数的返回值
		"""
		return self._fn( *( self._args + args ) )


def searchFile( searchPath, exts ):
	"""
	搜索指定的目录(searchPath)，查找所有符合指定的扩展名(exts)的文件（或目录）；
	注意：我们并不判断一个文件是否是文件夹，也不进行递归查找，仅仅以扩展名在指定目录进行查找；

	@param searchPath: STRING or tuple of STRING, 要搜索的路径（列表）
	@param       exts: STRING or tuple of STRING, 要搜索的扩展名（列表），每个扩展名都必须是以点开头的，如：.txt
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
			name, ext = os.path.splitext( key )		# 截取扩展名
			if ext in exts:							# 扩展名匹配
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
	压缩一个浮点数 by kebiao
	@param floatVal		: 浮点数值
	@param percentage	: 压缩比率
	@return type		: int32
	"""
	return int( floatVal * percentage )

def unzipFloat( intVal, percentage = 10000 ):
	"""
	解压缩一个压缩过的浮点数 by kebiao
	@param intVal		: 数值
	@param percentage	: 压缩比率
	@return type		: float
	"""
	return intVal / float( percentage )

def ipToStr( val ):
	"""
	转换int32的ip地址为以点(".")分隔的字符串模式。
	例：ipToStr( 436211884 ) --> '172.16.0.26'
	"""
	return "%i.%i.%i.%i" % ( val & 0xff, ( val >> 8 ) & 0xff, ( val >> 16 ) & 0xff, ( val >> 24 ) & 0xff )


class UIDFactory:
	"""
	64位UID生成器。
	此接口只允许在cellapp或baseapp中调用。
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		self._component_flag = -1		# see also: self._init()
		self._last_id = 0

	def __call__( self ):
		"""
		产生一个全局性的唯一ID
		@rtype INT64
		"""
		# 注：由于当前服务器起动机制的原因，我们暂时不能一开始就初始化cellapp或baseapp的id值
		# 所以只能推迟到第一次取值的时候初始化
		if self._component_flag <= 0:
			self._init()

		t = int( time.time() )

		self._last_id += 1
		if self._last_id > 0xffffff:
			self._last_id = 0
		return ( t << 32 ) + ( self._component_flag << 24 ) + self._last_id

	def _init( self ):
		"""
		初始化进程相关的UID前缀
		"""
		# init watcher key by bigworld component
		if BigWorld.component == "base":
			_watcher_key = "id"
			# 此值的用来区分到底是baseapp还是cellapp产生的ID，也是为了避免id值冲突
			# 我们使用一个字节的大小来表示各baseapp和cellapp的id
			# 也就是我们最多可以分别表示128个baseapp或cellapp
			_app_flag = 0x80
		elif BigWorld.component == "cell":
			_watcher_key = "cellAppID"
			_app_flag = 0
		else:
			assert False

		appID = int( BigWorld.getWatcher( _watcher_key ) )
		assert appID > 0	# 如果在服务器刚运行时就初始化，这个值就有可能会小于0
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
	转换货币显示形式 由于该函数适用范围比较广 根据柯大侠的建议 在这里增加公共接口 by姜毅
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
	把图标转换为base64的串 by 姜毅
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
	通过解码字符串获得图标字符串 by 姜毅
	在外部再通过 csol.binaryToTexture( imgStr ) 获得图标
	"""
	if iString is None:
		return None
	try:
		return base64.b64decode( zlib.decompress( iString ) )	#imgStr
	except:
		return None
		
	 
def makeFile( path, fileName, file ):
	"""
	通过路径创建和存入文件 by 姜毅
	限制：只能存入res目录下
	"""
	path_file = path + "/" + fileName
	d = open( path_file, "wb" )
	d.write( file )
	d.close()

def get3DVectorFromStr( str, delim = " " ):
	"""
	从由delim分隔的字符串中获取一个3d tuple
	比如：delim == ',' str == '1,2,3'
	返回：( 1.0, 2.0, 3.0 )
	"""
	assert len( delim ) == 1
	
	tmp = str.split( delim )
	assert len( tmp ) == 3
	
	x = float( tmp[0] )
	y = float( tmp[1] )
	z = float( tmp[2] )
	
	return ( x, y, z )
	

# Function.py

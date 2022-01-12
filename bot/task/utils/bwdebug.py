# -*- coding: gb18030 -*-
#
# $Id: bwdebug.py,v 1.9 2008-07-29 02:34:21 yangkai Exp $

"""
提供Trace系列输出函数。
	@var printPath:		是否打印调用者的程序信息(Source FileName + LineNo)
	@type printPath:	bool
"""

import sys
import time
import traceback

printPath = False

try:
	isPublished = __import__( "csol" ).isPublished()
except ImportError, impe:
	isPublished = False
	print "bwdebug: isPublished", isPublished, "- no csol module, maybe server."
except AttributeError, ae:
	isPublished = False
	print "bwdebug: isPublished", isPublished ,"- no isPublished() method."
isDebuged = not isPublished


def _printErrorInfo():
	print str( sys.exc_info()[1] )

def _getClassName( f, funcName ):
	"""
	取得对应堆栈帧(Frame)的类名字。
	@param 			f : 调用者的堆栈帧(Frame)
	@type 			f : Frame
	@return			  : 对应的类名字
	@rtype			  : string
	"""
	try:
		selfClass = f.f_locals[ 'self' ].__class__					# Note: This only works if self argument is self.
		mro = getattr( selfClass, "__mro__", [] )					# Only new style classes have __mro__ ( inherit object class )
		if mro == []:												# get all grandsire classes
			stack = [selfClass]
			while stack:
				curr = stack.pop( 0 )
				mro.append(curr)									# get all grandsire classes and my self
				stack += curr.__bases__								# base classes
		for bases in mro:
			method = bases.__dict__.get( funcName, None )
			if method is None :										# private method
				prvFunc = "_%s%s" % ( bases.__name__, funcName )	# private method name
				method = bases.__dict__.get( prvFunc, None )		# get private method
			if ( method is not None ) and \
				method.func_code == f.f_code :						# if find out the method, in class
					return bases.__name__ + "."						# return the class name
	except : pass
	return ""

def _printMessage( prefix, args, printPath ):
	"""
	按照Prefix输出信息。
	@param 			prefix		: 输出前缀
	@type 			prefix		: string
	@param 			args		: 输出的信息
	@type 			args		: tuple
	@param 			printPath	: 是否输出程序信息
	@type 			printPath	: bool
	@return						: None
	"""
	debug_str = ""
	f = sys._getframe(2)
	if printPath:
		debug_str += f.f_code.co_filename + "(" + str( f.f_lineno ) + ") :" + "\n"
	funcName = f.f_code.co_name
	className = _getClassName( f, funcName )
	debug_str += "%s: %s%s: " % ( prefix, className, funcName )
	for m in args : debug_str += m
	print debug_str + "\n"

def STREAM_MSG( stream, *args ):
	"""
	输出Hack信息。
	@param 			stream	: 输出的二进制流
	@type 			stream	: String
	@param 			args	: 输出的信息
	@type 			args	: 可变参数列表
	@return					: 无
	@rtype					: None
	"""
	dumpStream = "0x"
	for char in stream:
		hexString = hex( ord( char ) )[2:]
		pad = "0" * ( 2 - len( hexString ) )
		dumpStream = dumpStream + pad + hexString
	sargs = list( args )
	sargs.append( dumpStream )
	_printMessage( "Stream", sargs, printPath )

def TRACE_MSG( *args ):
	"""
	输出Trace信息。
	@param 				args : 输出的信息
	@type 				args : 可变参数列表
	@return					 : None
	"""
	_printMessage( "Trace", args, printPath )

def DEBUG_MSG( *args ):
	"""
	输出Debug信息。
	@param 				args : 输出的信息
	@type 				args : 可变参数列表
	@return					 : None
	"""
	if isPublished:
		return
	_printMessage( "Debug", args, printPath )

def INFO_MSG( *args ):
	"""
	输出Info信息。
	@param 				args : 输出的信息
	@type 				args : 可变参数列表
	@return					 : 无
	@rtype					 : None
	"""
	if isPublished:
		return
	_printMessage( "Info", args, printPath )

def NOTICE_MSG( *args ):
	"""
	输出Notice信息。
	@param 			args : 输出的信息
	@type 			args : 可变参数列表
	@return				 : None
	"""
	if isPublished:
		return
	_printMessage( "Notice", args, printPath )

def WARNING_MSG( *args ):
	"""
	输出Warning信息。
	@param 			args : 输出的信息
	@type 			args : 可变参数列表
	@return				 : None
	"""
	_printMessage( "Warning", args, printPath )

def ERROR_MSG( *args ):
	"""
	输出Error信息。
	@param 			args : 输出的信息
	@type 			args : 可变参数列表
	@return				 : 无
	@rtype				 : None
	"""
	_printMessage( "Error", args, printPath )
	_printErrorInfo()
	printStackTrace()

def GET_ERROR_MSG():
	"""
	获取上一次的错误信息
	该接口只有在except中调用才有意义
	"""
	message = ""
	f = sys.exc_info()[2].tb_frame
	message += f.f_code.co_filename + "(" + str( f.f_lineno ) + ") :"
	funcName = f.f_code.co_name
	className = _getClassName( f, funcName )
	message += "%s: %s: %s" % ( className,sys.exc_info()[0], sys.exc_info()[1] )

	return message

def CRITICAL_MSG( *args ):
	"""
	输出Critical信息。
	@param 			args : 输出的信息
	@type 			args : 可变参数列表
	@return				 : None
	"""
	_printMessage( "Critical", args, printPath )

def HACK_MSG( *args ):
	"""
	输出Hack信息。
	@param 			args : 输出的信息
	@type 			args : 可变参数列表
	@return				 : None
	"""
	_printMessage( "Hack", args, printPath )

def TEMP_MSG( *args ):
	"""
	输出Temp信息。
	@param 			args : 输出的信息
	@type 			args : 可变参数列表
	@return				 : None
	"""
	if isPublished:
		return
	_printMessage( "Temp", args, printPath )

def HOOK_MSG( *args ) :
	"""
	输出Hook信息。
	@param 			args : 输出的信息
	@type 			args : 可变参数列表
	@return				 : None
	"""
	excStr = "Hook: "
	for i in xrange( len( args ) ) :
		excStr += "%s, "
	try :
		raise excStr % args
	except Exception, err :
		sys.excepthook( Exception, err, sys.exc_traceback )

def LOG_MSG( *args ):
	"""
	输出log信息。
	@param 			args : 输出的信息
	@type 			args : 可变参数列表
	@return				 : None
	"""
	_printMessage( "NOTE_LOG(%s)" % time.strftime( "%Y-%m-%d %X" ), args, True )

def EXCEHOOK_MSG( *args ) :
	"""
	输出当前栈帧错误信息，常用于输出异常信息
	writen by hyw--2009.02.26
	@param 			args : 输出的信息
	@type 			args : 可变参数列表
	@return				 : None
	"""
	exceInfo = sys.exc_info()
	if exceInfo is None or exceInfo == ( None, None, None ) :
		INFO_MSG( "no exception in stack!" )
	else :
		_printMessage( "EXCEHOOK_MSG:", args, printPath )
		sys.excepthook( *exceInfo )

def DATABASE_LOG_MSG( table, msg, *args ):
	"""
	输出日志数据到数据库中。
	@param 			msg  : 输出的信息
	@type			msg  : STRING
	@param 			args : 可变参数，用于格式化msg
	@type 			args : 可变参数列表
	@return				 : None
	注:这里只需要打印即可被日志模块message_logger截获，并写入到日志数据库中
	"""
	message = msg % args
	print "mysql$" + str(table) + "$" + getLogTime() + message

def DEBUG_MSG_FOR_AI( entity, clientMsg, serverMsg ):
	"""
	输出Debug信息。
	@param 				args : 输出的信息
	@type 				args : 可变参数列表
	@return					 : None
	"""
	if serverMsg != "":
		DEBUG_MSG( serverMsg )
	entity.say( clientMsg )






def getLogTime( ):
	"""
	获取当前的时间，格式为"2009-06-18 12:00:00"
	"""
	date = time.localtime()
	return time.strftime("%Y-%m-%d %H:%M:%S",date)

import sys

outputTemplate = "%s\t%s:%s"

def __formatFrameObj( frmObj ):
	fileName = ""
	funcName = ""
	lineNum = 0
	codeObj = frmObj.f_code

	fileName = codeObj.co_filename
	funcName = codeObj.co_name
	lineNum = codeObj.co_firstlineno

	return outputTemplate%( funcName, fileName, lineNum )


def printStackTrace():
	"""
	打印当前堆栈，只需要在要打堆栈的代码中调用此函数就可以了，堆栈信息会输出在日志中。
	"""
	#if isPublished: return

	ids = [ threadid for threadid in sys._current_frames().iterkeys() ]
	curframe=sys._current_frames()[threadid].f_back
	print "Strack Trace:"
	print "In %s\t%s:%s"%( curframe.f_code.co_name, curframe.f_code.co_filename, curframe.f_lineno )
	while(curframe.f_back!=None):
		curframe=curframe.f_back
		print "#\t\t" + __formatFrameObj( curframe )

def print_stack():
	"""打印当前堆栈调用信息"""
	frame = sys._getframe().f_back
	print "<Debug> Stack trace:"
	print "(From file %s, line %s, in %s)" % traceback.extract_stack(frame, 1)[0][:3]
	traceback.print_stack( frame )

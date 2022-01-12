# -*- coding: gb18030 -*-
#
# $Id: bwdebug.py,v 1.9 2008-07-29 02:34:21 yangkai Exp $

"""
�ṩTraceϵ�����������
	@var printPath:		�Ƿ��ӡ�����ߵĳ�����Ϣ(Source FileName + LineNo)
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
	ȡ�ö�Ӧ��ջ֡(Frame)�������֡�
	@param 			f : �����ߵĶ�ջ֡(Frame)
	@type 			f : Frame
	@return			  : ��Ӧ��������
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
	����Prefix�����Ϣ��
	@param 			prefix		: ���ǰ׺
	@type 			prefix		: string
	@param 			args		: �������Ϣ
	@type 			args		: tuple
	@param 			printPath	: �Ƿ����������Ϣ
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
	���Hack��Ϣ��
	@param 			stream	: ����Ķ�������
	@type 			stream	: String
	@param 			args	: �������Ϣ
	@type 			args	: �ɱ�����б�
	@return					: ��
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
	���Trace��Ϣ��
	@param 				args : �������Ϣ
	@type 				args : �ɱ�����б�
	@return					 : None
	"""
	_printMessage( "Trace", args, printPath )

def DEBUG_MSG( *args ):
	"""
	���Debug��Ϣ��
	@param 				args : �������Ϣ
	@type 				args : �ɱ�����б�
	@return					 : None
	"""
	if isPublished:
		return
	_printMessage( "Debug", args, printPath )

def INFO_MSG( *args ):
	"""
	���Info��Ϣ��
	@param 				args : �������Ϣ
	@type 				args : �ɱ�����б�
	@return					 : ��
	@rtype					 : None
	"""
	if isPublished:
		return
	_printMessage( "Info", args, printPath )

def NOTICE_MSG( *args ):
	"""
	���Notice��Ϣ��
	@param 			args : �������Ϣ
	@type 			args : �ɱ�����б�
	@return				 : None
	"""
	if isPublished:
		return
	_printMessage( "Notice", args, printPath )

def WARNING_MSG( *args ):
	"""
	���Warning��Ϣ��
	@param 			args : �������Ϣ
	@type 			args : �ɱ�����б�
	@return				 : None
	"""
	_printMessage( "Warning", args, printPath )

def ERROR_MSG( *args ):
	"""
	���Error��Ϣ��
	@param 			args : �������Ϣ
	@type 			args : �ɱ�����б�
	@return				 : ��
	@rtype				 : None
	"""
	_printMessage( "Error", args, printPath )
	_printErrorInfo()
	printStackTrace()

def GET_ERROR_MSG():
	"""
	��ȡ��һ�εĴ�����Ϣ
	�ýӿ�ֻ����except�е��ò�������
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
	���Critical��Ϣ��
	@param 			args : �������Ϣ
	@type 			args : �ɱ�����б�
	@return				 : None
	"""
	_printMessage( "Critical", args, printPath )

def HACK_MSG( *args ):
	"""
	���Hack��Ϣ��
	@param 			args : �������Ϣ
	@type 			args : �ɱ�����б�
	@return				 : None
	"""
	_printMessage( "Hack", args, printPath )

def TEMP_MSG( *args ):
	"""
	���Temp��Ϣ��
	@param 			args : �������Ϣ
	@type 			args : �ɱ�����б�
	@return				 : None
	"""
	if isPublished:
		return
	_printMessage( "Temp", args, printPath )

def HOOK_MSG( *args ) :
	"""
	���Hook��Ϣ��
	@param 			args : �������Ϣ
	@type 			args : �ɱ�����б�
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
	���log��Ϣ��
	@param 			args : �������Ϣ
	@type 			args : �ɱ�����б�
	@return				 : None
	"""
	_printMessage( "NOTE_LOG(%s)" % time.strftime( "%Y-%m-%d %X" ), args, True )

def EXCEHOOK_MSG( *args ) :
	"""
	�����ǰջ֡������Ϣ������������쳣��Ϣ
	writen by hyw--2009.02.26
	@param 			args : �������Ϣ
	@type 			args : �ɱ�����б�
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
	�����־���ݵ����ݿ��С�
	@param 			msg  : �������Ϣ
	@type			msg  : STRING
	@param 			args : �ɱ���������ڸ�ʽ��msg
	@type 			args : �ɱ�����б�
	@return				 : None
	ע:����ֻ��Ҫ��ӡ���ɱ���־ģ��message_logger�ػ񣬲�д�뵽��־���ݿ���
	"""
	message = msg % args
	print "mysql$" + str(table) + "$" + getLogTime() + message

def DEBUG_MSG_FOR_AI( entity, clientMsg, serverMsg ):
	"""
	���Debug��Ϣ��
	@param 				args : �������Ϣ
	@type 				args : �ɱ�����б�
	@return					 : None
	"""
	if serverMsg != "":
		DEBUG_MSG( serverMsg )
	entity.say( clientMsg )






def getLogTime( ):
	"""
	��ȡ��ǰ��ʱ�䣬��ʽΪ"2009-06-18 12:00:00"
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
	��ӡ��ǰ��ջ��ֻ��Ҫ��Ҫ���ջ�Ĵ����е��ô˺����Ϳ����ˣ���ջ��Ϣ���������־�С�
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
	"""��ӡ��ǰ��ջ������Ϣ"""
	frame = sys._getframe().f_back
	print "<Debug> Stack trace:"
	print "(From file %s, line %s, in %s)" % traceback.extract_stack(frame, 1)[0][:3]
	traceback.print_stack( frame )

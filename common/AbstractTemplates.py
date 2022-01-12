# -*- coding: gb18030 -*-
#
# $Id: InputBase.py,v 1.19 2008-06-21 01:48:39 huangyongwei Exp $

"""
��ģ����Ҫ����һЩ���ģʽ��ص�ģʽ�����ģʽ��

2009.01.20 : writen by huangyongwei
2010.05.10 : add 'MultiLngFuncDecorator' class
"""

import re
from bwdebug import *
from Weaker import WeakList

# --------------------------------------------------------------------
# ����������
# �ó���ʵ���˵�������࣬��������п������������ɷ�ʽ��
# �Ӷ������ģʽ�еĵ���ʵ�֣��ɹ�ȥ��Լ����ʽ�޸�Ϊ�����ϵ�֧�֡�
# --------------------------------------------------------------------
class MetaSingletonClass( type ) :
	def __init__( cls, name, bases, dict ) :
		super( MetaSingletonClass, cls ).__init__( name, bases, dict )	# ���û����ʼ������
		cls.__inst = None
		cls.__initer = cls.__init__
		cls.__new__ = staticmethod( MetaSingletonClass.__replace_new )	# ���¶�λ�������ʵ��������

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def insted( cls ) :
		"""
		�Ƿ��Ѿ���ʼ���˵���ʵ��
		"""
		return cls.__inst is not None

	@property
	def inst( cls ) :
		"""
		��ȡ����ʵ��
		"""
		return cls()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __replace_init( inst, *args, **kwds ) :
		"""
		�滻���� init
		"""
		pass

	@staticmethod
	def __replace_new( cls, *args, **kwds ) :
		"""
		�µ��滻 new
		"""
		if cls.__inst is None :
			cls.__inst = object.__new__( cls, *args, **kwds )
			cls.__init__( cls.__inst, *args, **kwds )
			cls.__init__ = MetaSingletonClass.__replace_init
		return cls.__inst

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def releaseInst( cls ) :
		"""
		�ͷŵ���ǰʵ��
		"""
		cls.__inst = None
		cls.__init__ = cls.__initer


# -----------------------------------------------------
# �������࣬���ĳ����̳��� Singleton������ཫ���Զ���Ϊ������
# -----------------------------------------------------
class Singleton( object ) :
	__metaclass__ = MetaSingletonClass										# ǿ�Ƶ��������Ϊ MetaSingletonClass


# --------------------------------------------------------------------
# ����������
# �ó���ʵ���˳�������࣬��������п������������ɷ�ʽ���Ӷ�������ĳ���
# --------------------------------------------------------------------
class MetaAbstractClass( type ) :
	def __init__( cls, name, bases, dict ) :
		super( MetaAbstractClass, cls ).__init__( name, bases, dict )		# ���û����ʼ������
		if cls.isAbstract() :												# ����ǳ�����
			cls.__new__ = staticmethod( MetaAbstractClass.__replace_new )	# ���滻�������ʵ��������
		else :
			for method in cls.__getImplementedMethods() :
				mname = method.func_name
				myfunc = getattr( cls, mname ).im_func
				assert myfunc != method, "class %s must implement method %s" % ( cls.__name__, mname )
			cls.__new__ = object.__new__

	def __getAbstractMethods( cls ) :
		"""
		��ȡ��ǰҪʵ�ֵ���ĳ��󷽷���������಻�ǳ����࣬�򷵻� None
		"""
		methodName = "_%s__abstract_methods" % cls.__name__
		methodName = re.sub( "^_*", "_", methodName )
		return getattr( cls, methodName, None )

	def __getImplementedMethods( cls ) :
		"""
		��ȡ��ǰ����Ҫʵ�ֵĳ��󷽷�
		"""
		methods = set()
		for base in cls.__bases__ :
			if hasattr( base, "_MetaAbstractClass__getAbstractMethods" ) :
				abstractMethods = base.__getAbstractMethods()
				if abstractMethods is None : continue
				methods.update( abstractMethods )
		return methods

	def __replace_new( cls, *args, **kwds ) :
		"""
		�滻�������ʵ��������
		"""
		raise TypeError( "abstract class '%s' is not allow to be instanced!" % cls.__name__ )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isAbstract( cls ) :
		"""
		�Ƿ��ǳ�����
		"""
		return cls.__getAbstractMethods() is not None


# -----------------------------------------------------
# ��������࣬�̳��ڸ�����࣬��Ϊ������
# ����̳��ڸ�����࣬���� __abstract_methods ���Ա��
#	��̳е����࣬��Ȼ��һ�������ࣨ����ʵ������
# ������� __abstract_methods.add() ��һ����Ա������ӵ� __abstract_methods �У�
# 	����ӵ� __abstract_methods �еķ�����Ϊ���󷽷�����Ҫ��������ʵ������
# -----------------------------------------------------
class AbstractClass( object ) :
	__metaclass__ = MetaAbstractClass										# ǿ����ĳ���Ϊ MetaSingletonClass
	__abstract_methods = set()



# --------------------------------------------------------------------
# �¼��������
# ����ʵ����һ���¼�����ͨ���ô������԰󶨶�� callback���Ӷ�ʵ��
#	  �¼���������󣬿��Դ������ callback
# --------------------------------------------------------------------
class EventDelegate( object ) :
	"""
	�¼���( ע�⣺�󶨵ķ���һ����ʵ������ )
	"""
	def __init__( self ) :
		self.__handlers = WeakList()		# ���������¼������ߺ���
		self.__shield = False				# �Ƿ������¼��������κ󣬽����߽��ղ����¼�������


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def isShield( self ) :
		"""
		�Ƿ������¼��������κ󣬽����߽��ղ����¼�������
		"""
		return self.__shield

	@property
	def handlerCount( self ) :
		"""
		��ȡ�¼�������������
		"""
		return len( self.__handlers )


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __call__( self, *args ) :
		"""
		��������
		"""
		if self.__shield : return False
		res = False
		for handler in self.__handlers :
			try :
				res = handler( *args ) or res
			except :
				EXCEHOOK_MSG( str( method ) )
		return res


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def bind( self, handler ) :
		"""
		��һ�������ߺ���
		@type				handler : callable object
		@param				handler : �¼������ߵĿɵ��ö���
		"""
		if handler in self.__handlers :
			ERROR_MSG( "%s has been in delegate list!" % str( handler ) )
		else :
			self.__handlers.append( handler )

	def unbind( self, handler ) :
		"""
		�����һ�������
		@type				handler : callable object
		@param				handler : �¼������ߵĿɵ��ö���
		"""
		if handler in self.__handlers :
			self.__handlers.remove( handler )

	# -------------------------------------------------
	def getHandlers( self ) :
		"""
		��ȡ���е��¼�����
		"""
		return self.__handlers.list()

	def hasHandler( self, handler ) :
		"""
		ָ���������Ƿ���ָ���¼����ն���
		"""
		return handler in self.__handlers

	def clearHandlers( self ) :
		"""
		������а󶨵��¼�����
		"""
		self.__handlers.clear()

	# -------------------------------------------------
	def shield( self ) :
		"""
		���ε��¼��Ĵ���
		"""
		self.__shield = True

	def unshield( self ) :
		"""
		ȡ���¼���������
		"""
		self.__shield = False


# --------------------------------------------------------------------
# �����԰汾�ĺ���װ����
# ����ʵ����һ�������򷽷���װ������ʹ�ñ����ڣ��ϸ���˵�� import �ڣ�
#	  ���ܸ��ݲ�ͬ���԰汾��ʹ�ò�ͬ�ĺ����򷽷�ʵ�ֲ�ͬ�Ĺ���
#
# ʹ�÷�����
#	  ʹ�Զ���ĺ���װ�����̳��� MultiLngFuncDecorator��Ȼ�����Զ����װ������
#	  ʵ�ֲ�ͬ���԰汾��ʵ�ַ�����
# --------------------------------------------------------------------
from Language import LANG_CONFIG_STRING as METHOD_NAME

class MetaMultiLngFuncDecorator( type ) :
	# ---------------------------------------
	# ������װ��
	# ---------------------------------------
	class FWarp( object ) :
		__slots__ = ( "__func" )
		def __init__( self, f ) :
			self.__func = f
		def __call__( self, *args, **darg ) :
			return self.__func( *args, **darg )

	# ---------------------------------------
	# ����ʵ��ǰ��װ��
	# ---------------------------------------
	def __init__( cls, name, bases, dict ) :
		super( MetaMultiLngFuncDecorator, cls ).__init__( name, bases, dict )
		cls.originalFunc = None

	def __call__( cls, func ) :
		assert cls.originalFunc is None, "muti-language function '%r' decorator has decorated!" % cls
		cls.originalFunc = MetaMultiLngFuncDecorator.FWarp( func )
		baseFunc = getattr( MultiLngFuncDecorator, METHOD_NAME, func )
		subFunc = getattr( cls, METHOD_NAME, func )
		if baseFunc is subFunc :
			return func
		return subFunc

# -----------------------------------------------------
# ע�⣺
#	  �� ��Щʵ�ַ��������Ǿ�̬��
#	  �� ��Щʵ�ַ������Ʊ����� Language::LANG_STRING_MARKS ��Ӧ������
#	  �� ���û�б�дĳ�����԰汾��ʵ�ַ�������Ĭ��ʹ��ԭʼ������ʵ��
#	  �� ͨ�� deco.originalFunc() ���Ի��ԭʼ����
#	  �� ���ͬʱ������װ������@staticmethod��@classmethod������Щװ����
#		 �������ڱ�װ������ǰ�档
# -----------------------------------------------------
class MultiLngFuncDecorator( object ) :
	__metaclass__ = MetaMultiLngFuncDecorator

	# ----------------------------------------------------------------
	@staticmethod
	def locale_default( *args, **darg ) :
		"""
		LANG_GBK ��ʵ�ַ������������д�ú��������� LANG_GBK �汾�£�Ĭ��ʹ��ԭʼ�汾
		"""
		return MultiLngFuncDecorator.originalFunc( *args, **darg )			# ԭʼ����

	@staticmethod
	def locale_big5( *args, **darg ) :
		"""
		LANG_BIG5 ��ʵ�ַ������������д�ú��������� LANG_BIG5 �汾�£�Ĭ��ʹ��ԭʼ�汾
		"""
		return MultiLngFuncDecorator.originalFunc( *args, **darg )			# ԭʼ����

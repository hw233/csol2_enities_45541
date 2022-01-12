#
# -*- coding: gb18030 -*-
# $Id: SmartImport.py,v 1.4 2008-05-17 12:08:26 huangyongwei Exp $
#
"""
自已的模块导入函数，在所有的服务器端都有可能被调用；
以后如果整合全局函数的时候要把这个放进去，现在没地方放只好先放了。

2005/05/11 : wirten by wolf( named: myImport )
2007/07/17 : rewriten by huangyongwei
2008/05/10 : add method importAll( by huangyongwei )
"""

import os
import re
import sys
import glob
import BigWorld
import ResMgr
from bwdebug import *

def smartImport( mname ) :
	"""
	导入一个模块。
	@type			mname		: STRING
	@param			mname		: 模块名称。具体格式为"mod1.mod2.modN:className"
								  其中":className"是可选的，表示要导入哪个类，如果存在则只允许有一个，类似于 "from mod import className"
								  也就是说可以直接导入一个模块里指定的类。
	@rtype				 		: object of module or class
	@return				 		: 返回指定的模块
	@raise 			ImportError : 如果指定的模块不存在则产生此异常
	"""
	compons = mname.split( ":" )							# 拆分路径和模块
	assert len( compons ) > 0, "wrong module name!"			# 排除空路径
	mod = __import__( compons[0], fromlist=[""] )			# import 最后一层模块(fromlist只要非空，就会返回最后一层模块)
															# 一个直观的理解是，调用__import__( 'A.B', fromlist=['c'] )
															# 应该是如同 from A.B import c，在调用的局部作用域里会设置c这个变量，或者__import__
															# 会返回c所指向的目标，但实际上并不是如此。根据python帮助文档，__import__( 'A.B', fromlist=['c'] )
															# 不会返回c所指向的目标，而只会得到A.B这个模块，python文档是这样说的：
															# the __import__() function does not set the local variable named eggs; this is done by
															# subsequent code that is generated for the import statement.
															# 也就是说，设置局部变量c不是在__import__里做的，而是在import方法里才做的，因此想要得到
															# c所指向的目标，只能在获取到A.B模块之后，再从模块中获取c，而只要fromlist参数不为空，
															# __import__就会返回A.B模块（否则返回A模块），所以传入一个非空的fromlist参数就不需要再使用迭代
															# 去逐级获取所需的c目标。
															# (注意：使用默认fromlist的话，只会 import 最顶层，但它会对全路径进行检查，路径不存在会 import 失败)

	if len( compons ) > 1 :									# 需要import模块的类
		try :
			mod = getattr( mod, compons[-1] )
		except AttributeError, err :						# 这里将AttrbuteError转变为了ImportError，如果外部捕捉ImportError，当这里出现了AttrbuteError，外部也会捕捉到异常，但是会失去异常的真实信息
			EXCEHOOK_MSG( err )
			raise ImportError( "module '%s' has no class or attribute '%s'!" % ( compons[0], compons[-1] ) )
	return mod

def importAll( modulePath, sfilter = "*" ) :
	"""
	import 指定文件夹下的所有模块
	@type			modulePath : str
	@param			modulePath : 要 import 的路径
	@type			sfilter	   : str
	@param			sfilter	   : 文件过滤器（譬如，要 import 指定文件夹下的所有以 P 开头的模块，则可以传入改参数为：P*）
	@type					   : list
	@return					   : 指定文件夹下的所有模块
	"""
	if modulePath.strip() == "" :
		ERROR_MSG( "importAll: empty path!" )
		return []
	if modulePath[-1] != "/" : modulePath += "/"							# 插入路径分隔符
	path = "entities/%s/%s" % ( BigWorld.component, modulePath )			# 资源全路径
	if ResMgr.openSection( path ) is None :									# 判断路径是否存在
		ERROR_MSG( "importAll: error module path: %s!" % path )
		return []

	modules = []
	if sfilter == "*.*" : sfilter = '*'
	moduleFiles = glob.glob1( path, sfilter + ".po" )						# 检索打包后的 pyc 文件
	if len( moduleFiles ) == 0 :											# 打包后不会执行到下面
		moduleFiles += glob.glob1( path, sfilter + ".py" )					# 检索 py 文件
		moduleFiles += glob.glob1( path, sfilter + ".pyc" )					# 检索 pyc 文件（python目标文件）
	moduleFiles = set( [os.path.splitext( e )[0] for e in moduleFiles] )	# 去除重复的模块

	modulePath = modulePath.replace( "/", "." )								# 格式化为 smartImport 识别的路径方式
	for mname in moduleFiles :
		mpath = modulePath + mname											# 模块全路径
		try :
			module = smartImport( mpath )
			modules.append( module )
		except Exception, e :
			sys.excepthook( Exception, e, sys.exc_traceback )
	return modules

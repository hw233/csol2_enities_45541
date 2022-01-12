#
# -*- coding: gb18030 -*-
# $Id: SmartImport.py,v 1.4 2008-05-17 12:08:26 huangyongwei Exp $
#
"""
���ѵ�ģ�鵼�뺯���������еķ������˶��п��ܱ����ã�
�Ժ��������ȫ�ֺ�����ʱ��Ҫ������Ž�ȥ������û�ط���ֻ���ȷ��ˡ�

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
	����һ��ģ�顣
	@type			mname		: STRING
	@param			mname		: ģ�����ơ������ʽΪ"mod1.mod2.modN:className"
								  ����":className"�ǿ�ѡ�ģ���ʾҪ�����ĸ��࣬���������ֻ������һ���������� "from mod import className"
								  Ҳ����˵����ֱ�ӵ���һ��ģ����ָ�����ࡣ
	@rtype				 		: object of module or class
	@return				 		: ����ָ����ģ��
	@raise 			ImportError : ���ָ����ģ�鲻������������쳣
	"""
	compons = mname.split( ":" )							# ���·����ģ��
	assert len( compons ) > 0, "wrong module name!"			# �ų���·��
	mod = __import__( compons[0], fromlist=[""] )			# import ���һ��ģ��(fromlistֻҪ�ǿգ��ͻ᷵�����һ��ģ��)
															# һ��ֱ�۵�����ǣ�����__import__( 'A.B', fromlist=['c'] )
															# Ӧ������ͬ from A.B import c���ڵ��õľֲ��������������c�������������__import__
															# �᷵��c��ָ���Ŀ�꣬��ʵ���ϲ�������ˡ�����python�����ĵ���__import__( 'A.B', fromlist=['c'] )
															# ���᷵��c��ָ���Ŀ�꣬��ֻ��õ�A.B���ģ�飬python�ĵ�������˵�ģ�
															# the __import__() function does not set the local variable named eggs; this is done by
															# subsequent code that is generated for the import statement.
															# Ҳ����˵�����þֲ�����c������__import__�����ģ�������import����������ģ������Ҫ�õ�
															# c��ָ���Ŀ�ֻ꣬���ڻ�ȡ��A.Bģ��֮���ٴ�ģ���л�ȡc����ֻҪfromlist������Ϊ�գ�
															# __import__�ͻ᷵��A.Bģ�飨���򷵻�Aģ�飩�����Դ���һ���ǿյ�fromlist�����Ͳ���Ҫ��ʹ�õ���
															# ȥ�𼶻�ȡ�����cĿ�ꡣ
															# (ע�⣺ʹ��Ĭ��fromlist�Ļ���ֻ�� import ��㣬�������ȫ·�����м�飬·�������ڻ� import ʧ��)

	if len( compons ) > 1 :									# ��Ҫimportģ�����
		try :
			mod = getattr( mod, compons[-1] )
		except AttributeError, err :						# ���ｫAttrbuteErrorת��Ϊ��ImportError������ⲿ��׽ImportError�������������AttrbuteError���ⲿҲ�Ჶ׽���쳣�����ǻ�ʧȥ�쳣����ʵ��Ϣ
			EXCEHOOK_MSG( err )
			raise ImportError( "module '%s' has no class or attribute '%s'!" % ( compons[0], compons[-1] ) )
	return mod

def importAll( modulePath, sfilter = "*" ) :
	"""
	import ָ���ļ����µ�����ģ��
	@type			modulePath : str
	@param			modulePath : Ҫ import ��·��
	@type			sfilter	   : str
	@param			sfilter	   : �ļ���������Ʃ�磬Ҫ import ָ���ļ����µ������� P ��ͷ��ģ�飬����Դ���Ĳ���Ϊ��P*��
	@type					   : list
	@return					   : ָ���ļ����µ�����ģ��
	"""
	if modulePath.strip() == "" :
		ERROR_MSG( "importAll: empty path!" )
		return []
	if modulePath[-1] != "/" : modulePath += "/"							# ����·���ָ���
	path = "entities/%s/%s" % ( BigWorld.component, modulePath )			# ��Դȫ·��
	if ResMgr.openSection( path ) is None :									# �ж�·���Ƿ����
		ERROR_MSG( "importAll: error module path: %s!" % path )
		return []

	modules = []
	if sfilter == "*.*" : sfilter = '*'
	moduleFiles = glob.glob1( path, sfilter + ".po" )						# ���������� pyc �ļ�
	if len( moduleFiles ) == 0 :											# ����󲻻�ִ�е�����
		moduleFiles += glob.glob1( path, sfilter + ".py" )					# ���� py �ļ�
		moduleFiles += glob.glob1( path, sfilter + ".pyc" )					# ���� pyc �ļ���pythonĿ���ļ���
	moduleFiles = set( [os.path.splitext( e )[0] for e in moduleFiles] )	# ȥ���ظ���ģ��

	modulePath = modulePath.replace( "/", "." )								# ��ʽ��Ϊ smartImport ʶ���·����ʽ
	for mname in moduleFiles :
		mpath = modulePath + mname											# ģ��ȫ·��
		try :
			module = smartImport( mpath )
			modules.append( module )
		except Exception, e :
			sys.excepthook( Exception, e, sys.exc_traceback )
	return modules

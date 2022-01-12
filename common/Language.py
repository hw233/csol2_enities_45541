# -*- coding: gb18030 -*-
"""
���Կ���ģ�顣
�����ϣ����ģ����Love3.py���ʼ��ʱ����á�

ʹ�ã�
1.��Ҫ���������Ե����ã�ʹ�á�LANG_����Ϊǰ׺���꿴�����LANG_GBK�ȶ��壩��
  ����Ҫ�ڡ�_LANG_CONFIG_STRING_MAPPING����������Ӧ����������Ŀ¼������Щ
  Ŀ¼��ͳһ���ڡ�res/entities/�������С�locale_default��ΪĬ����������Ŀ¼(GBK)��
  ÿһ��locale_*Ŀ¼������Ŀ¼���ǻ���ģ����������ö�����������locale_*�д���һ�ݣ�
  ��ʹ������ȫһ��Ҳ��Ҫ��
2.��Ҫ�޸�Ĭ������ֻҪ�޸ġ�LANG�����弴�ɡ�
3.����Ҫ�Ե�ǰ���Խ����жϵĵط����������ã�
  import Language
  if Language.LANG == Language.LANG_GBK:
     ...
  elif ...:
     ...
  else:
     ...
4.����Ӧ��ʹ��openConfigSection()�������򿪣�ʹ��������
  import Language
  # ע�⣬���ò�����ԭ����ȫ·����ʽ
  section = Language.openConfigSection( "config/path/filename.xml" )
  # do some thing ...
  Language.purgeConfig( "config/path/filename.xml" )
"""
import sys
import ResMgr

# ���Զ���
LANG_GBK	= 0
LANG_BIG5	= 1

DECODE_NAMES = {
	LANG_GBK	: "GB18030",
	LANG_BIG5	: "CP950",
	}										# �������ԵĽ�������

_LANG_CONFIG_STRING_MAPPING = {
	LANG_GBK	: "locale_default",
	LANG_BIG5	: "locale_big5",
	}										# �������Ե�����·��


LANG			= LANG_GBK					# Ĭ�����ԣ�������Ҫ�ı����ԣ��޸Ĵ�ֵ����
DECODE_NAME 	= DECODE_NAMES[LANG]		# ��ǰ���ԵĽ�������


# ���ַ�����Ҫ��������ȡ���õĴ���ʹ�ã���ȥ���汾�����
# ���磬���ǿ��ܻ������ã�
# section = ResMgr.openSection( "entities/%s/config/xxx/yyy/zzz.xml" % LANG_CONFIG_STRING )
LANG_CONFIG_STRING = _LANG_CONFIG_STRING_MAPPING[LANG]
LANG_CONFIG_HEAD = "entities/%s" % LANG_CONFIG_STRING
LANG_CONFIG_DIR = LANG_CONFIG_HEAD + "/%s"

# ��ʼ������������ã������˳�����ң�
# ����ǰ���ض����Ե������ܸ���Ĭ������
sys.path.append( LANG_CONFIG_HEAD )


# ��װ������������ö�ȡ
def getFilePathABS( filename ):
	"""

	"""
	f = LANG_CONFIG_DIR % filename
	if ResMgr.root.has_key( f ):
		return f
	return ""


def openConfigSection( filename ):
	"""
	This function opens the specified resource as a DataSection.
	If the resource is not found, then it returns None.
	A new section can optionally be created by specifying true in
	the optional second argument.

	@param filename: ����·�����ļ�����ע�����ļ���·��ֻ�������������Ŀ¼��·����
	@return: the DataSection that was loaded, or None if the id was not found.
	"""
	return ResMgr.openSection( LANG_CONFIG_DIR % filename )

def purgeConfig( filename ):
	"""
	This function purges the previously loaded section with the specified path
	from the cache and census. Optionally, all child sections can also be purged
	(only useful if the resource is a DirSection), by specifying true in the
	optional second argument.

	@param filename: ����·�����ļ�����ע�����ļ���·��ֻ�������������Ŀ¼��·����
	"""
	ResMgr.purge( LANG_CONFIG_DIR % filename )



def searchConfigFile( searchPath, exts ):
	"""
	����ָ����Ŀ¼(searchPath)���������з���ָ������չ��(exts)���ļ�����Ŀ¼����
	��Ϊ������������ص��ļ������汾�������������ļ�����ʹ��openConfigSection()�򿪡�
	ע�⣺���ǲ����ж�һ���ļ��Ƿ����ļ��У�Ҳ�����еݹ���ң���������չ����ָ��Ŀ¼���в��ң�

	@param searchPath: STRING or tuple of STRING, Ҫ������·�����б�
	@param       exts: STRING or tuple of STRING, Ҫ��������չ�����б���ÿ����չ�����������Ե㿪ͷ�ģ��磺.txt
	@return: array of STRING
	"""
	files = searchConfigFileABS( searchPath, exts )
	# ��ȥ������ص�·��ͷ�����ŵ�hash_set��
	filesSet = set()
	lchLen = len( LANG_CONFIG_HEAD ) + 1
	for f in files:
		filesSet.add( f[lchLen:] )
	return filesSet

def searchConfigFileABS( searchPath, exts ):
	"""
	����ָ����Ŀ¼(searchPath)���������з���ָ������չ��(exts)���ļ�����Ŀ¼����
	ע�⣺���ǲ����ж�һ���ļ��Ƿ����ļ��У�Ҳ�����еݹ���ң���������չ����ָ��Ŀ¼���в��ң�

	@param searchPath: STRING or tuple of STRING, Ҫ������·�����б�
	@param       exts: STRING or tuple of STRING, Ҫ��������չ�����б���ÿ����չ�����������Ե㿪ͷ�ģ��磺.txt
	@return: hash_set of STRING
	"""
	assert isinstance( searchPath, (str, tuple, list) )
	if isinstance( searchPath, str ):
		searchPaths = [ searchPath, ]
	else:
		searchPaths = list( searchPath )

	finalPaths = []
	for e in searchPaths:
		if ResMgr.openSection( LANG_CONFIG_DIR % e ) is not None:
			finalPaths.append( LANG_CONFIG_DIR % e )

	return Function.searchFile( finalPaths, exts )

def searchConfigModuleName( searchPath ):
	"""
	"""
	modulesfiles = searchConfigFile( searchPath, [ ".py", ".pyc" ] )
	moduleNames= set([])
	for i in modulesfiles:
		moduleNames.add( i.split(".")[0].split("/")[-1] )
	return moduleNames

# ���importֻ�ܷ�����Ա���Ǳ�ڵĿ��ܴ��ڵĽ�������
import Function

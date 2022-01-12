# -*- coding: gb18030 -*-
"""
语言控制模块。
理论上，这个模块由Love3.py在最开始的时候调用。

使用：
1.需要增加新语言的配置，使用“LANG_”作为前缀（详看下面的LANG_GBK等定义），
  且需要在“_LANG_CONFIG_STRING_MAPPING”中增加相应的语言配置目录名，这些
  目录都统一放在“res/entities/”，其中“locale_default”为默认语言配置目录(GBK)。
  每一个locale_*目录与其它目录都是互斥的，即所有配置都必须在所有locale_*中存在一份，
  即使配置完全一样也需要。
2.需要修改默认语言只要修改“LANG”定义即可。
3.在需要对当前语言进行判断的地方可以这样用：
  import Language
  if Language.LANG == Language.LANG_GBK:
     ...
  elif ...:
     ...
  else:
     ...
4.配置应该使用openConfigSection()方法来打开，使用样例：
  import Language
  # 注意，配置不再是原来的全路径方式
  section = Language.openConfigSection( "config/path/filename.xml" )
  # do some thing ...
  Language.purgeConfig( "config/path/filename.xml" )
"""
import sys
import ResMgr

# 语言定义
LANG_GBK	= 0
LANG_BIG5	= 1

DECODE_NAMES = {
	LANG_GBK	: "GB18030",
	LANG_BIG5	: "CP950",
	}										# 所有语言的解码名称

_LANG_CONFIG_STRING_MAPPING = {
	LANG_GBK	: "locale_default",
	LANG_BIG5	: "locale_big5",
	}										# 所有语言的配置路径


LANG			= LANG_GBK					# 默认语言，将来需要改变语言，修改此值即可
DECODE_NAME 	= DECODE_NAMES[LANG]		# 当前语言的解码名称


# 此字符串主要用来给读取配置的代码使用，以去除版本相关性
# 例如，我们可能会这样用：
# section = ResMgr.openSection( "entities/%s/config/xxx/yyy/zzz.xml" % LANG_CONFIG_STRING )
LANG_CONFIG_STRING = _LANG_CONFIG_STRING_MAPPING[LANG]
LANG_CONFIG_HEAD = "entities/%s" % LANG_CONFIG_STRING
LANG_CONFIG_DIR = LANG_CONFIG_HEAD + "/%s"

# 初始化语言相关配置，且这个顺序不能乱，
# 以让前面特定语言的配置能覆盖默认配置
sys.path.append( LANG_CONFIG_HEAD )


# 封装多语言相关配置读取
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

	@param filename: 配置路径及文件名；注：此文件名路径只能是相对于配置目录的路径。
	@return: the DataSection that was loaded, or None if the id was not found.
	"""
	return ResMgr.openSection( LANG_CONFIG_DIR % filename )

def purgeConfig( filename ):
	"""
	This function purges the previously loaded section with the specified path
	from the cache and census. Optionally, all child sections can also be purged
	(only useful if the resource is a DirSection), by specifying true in the
	optional second argument.

	@param filename: 配置路径及文件名；注：此文件名路径只能是相对于配置目录的路径。
	"""
	ResMgr.purge( LANG_CONFIG_DIR % filename )



def searchConfigFile( searchPath, exts ):
	"""
	搜索指定的目录(searchPath)，查找所有符合指定的扩展名(exts)的文件（或目录）；
	此为多语言配置相关的文件搜索版本，搜索出来的文件可以使用openConfigSection()打开。
	注意：我们并不判断一个文件是否是文件夹，也不进行递归查找，仅仅以扩展名在指定目录进行查找；

	@param searchPath: STRING or tuple of STRING, 要搜索的路径（列表）
	@param       exts: STRING or tuple of STRING, 要搜索的扩展名（列表），每个扩展名都必须是以点开头的，如：.txt
	@return: array of STRING
	"""
	files = searchConfigFileABS( searchPath, exts )
	# 截去语言相关的路径头，并放到hash_set中
	filesSet = set()
	lchLen = len( LANG_CONFIG_HEAD ) + 1
	for f in files:
		filesSet.add( f[lchLen:] )
	return filesSet

def searchConfigFileABS( searchPath, exts ):
	"""
	搜索指定的目录(searchPath)，查找所有符合指定的扩展名(exts)的文件（或目录）；
	注意：我们并不判断一个文件是否是文件夹，也不进行递归查找，仅仅以扩展名在指定目录进行查找；

	@param searchPath: STRING or tuple of STRING, 要搜索的路径（列表）
	@param       exts: STRING or tuple of STRING, 要搜索的扩展名（列表），每个扩展名都必须是以点开头的，如：.txt
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

# 这个import只能放这里，以避免潜在的可能存在的交叉引用
import Function

# -*- coding: gb18030 -*-
# 15:30 2013-5-30 by wangshufeng

from xml.dom import minidom

g_filtter_out_entities = [ "None", "Role", "Account", "Monster" ]	# 需要过滤掉的entityType

def createEntityScript( srcPath = r"entities/entities.xml", dstPath = r"entities/bot/" ):
	"""
	根据entities.xml创建相应的entity脚本文件到指定文件夹，注意：entities.xml中不能有中文字符。
	use case :
	import BotTest
	BotTest.createEntityScript( r"E:\love3\res\entities\entities.xml", r"E:\love3\res\entities\ss" )
	
	@param srcPath: path of entities.xml
	@param dstPath: the output directory.
	"""
	rootDoc = minidom.parse( srcPath )
	if dstPath[-1] not in "\\/":
		dstPath += "/"
	successCount = 0
	for domDoc in rootDoc.firstChild.childNodes:
		entityType = domDoc.localName
		if entityType is None or entityType in g_filtter_out_entities:
			continue
		entityPath = dstPath + "%s.py" % entityType
		fp = open( entityPath,"w" )
		fp.writelines( "import BigWorld\n" )
		fp.writelines( "class %s( BigWorld.Entity ):pass\n" % entityType )
		fp.close()
		successCount += 1
	print "createEntityScript success count:", successCount,
	rootDoc.unlink()

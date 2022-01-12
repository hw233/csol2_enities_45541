# -*- coding: gb18030 -*-
#
"""
读取文件的版本
"""
import os
import ResMgr
import binascii

def getVersion():
	"""
	获取版本
	"""
	file = ResMgr.openSection("entities/version")
	if file == None:
		return ""
	s = file.asBinary
	# 去掉一些杂七杂八的允许的冗余字符，
	# 以避免一些无意识增加的空行影响版本号的正确性。
	s = s.replace( "\n", "" )
	s = s.replace( "\r", "" )
	s = s.replace( " ", "" )
	s = s.replace( "\t", "" )
	return s

def getGameName() :
	"""
	获取游戏名字( 在 bw.xml 中定义的游戏英文名称 )
	2010.06.08: writen by huangyongwei
	"""
	sect = ResMgr.openSection( "server/bw.xml" )
	return sect.readString( "gameName" )

def getServerName():
	"""
	获取服务器名字
	"""
	nameConfig = ResMgr.openSection("../options.xml/scriptsPreferences/login/server/servername")
	if nameConfig is None:
		return ""
	serverName = " - " + binascii.a2b_hex( nameConfig.asString ) # 需要将16进制编码转成字符
	return serverName

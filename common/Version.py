# -*- coding: gb18030 -*-
#
"""
��ȡ�ļ��İ汾
"""
import os
import ResMgr
import binascii

def getVersion():
	"""
	��ȡ�汾
	"""
	file = ResMgr.openSection("entities/version")
	if file == None:
		return ""
	s = file.asBinary
	# ȥ��һЩ�����Ӱ˵�����������ַ���
	# �Ա���һЩ����ʶ���ӵĿ���Ӱ��汾�ŵ���ȷ�ԡ�
	s = s.replace( "\n", "" )
	s = s.replace( "\r", "" )
	s = s.replace( " ", "" )
	s = s.replace( "\t", "" )
	return s

def getGameName() :
	"""
	��ȡ��Ϸ����( �� bw.xml �ж������ϷӢ������ )
	2010.06.08: writen by huangyongwei
	"""
	sect = ResMgr.openSection( "server/bw.xml" )
	return sect.readString( "gameName" )

def getServerName():
	"""
	��ȡ����������
	"""
	nameConfig = ResMgr.openSection("../options.xml/scriptsPreferences/login/server/servername")
	if nameConfig is None:
		return ""
	serverName = " - " + binascii.a2b_hex( nameConfig.asString ) # ��Ҫ��16���Ʊ���ת���ַ�
	return serverName

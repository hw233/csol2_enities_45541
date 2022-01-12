# -*- coding: gb18030 -*-
#
# $Id: SpaceData.py,v 1.9 2008-04-16 05:55:47 phw Exp $

"""
��������
"""

import BigWorld
import Language
from bwdebug import *
import Function
import Language

class SpaceData:
	def __init__( self, configPath = None ):
		"""
		���캯����
			@param configPath:	���������ļ�·��
			@type  configPath:	string
		"""
		if configPath is not None:
			self.load( configPath )

	def __getitem__( self, key ):
		"""
		ȡ��Space���ݲ���
		"""
		return self.data[key]

	def load( self, configPath ):
		"""
		���س������ݡ�
			@param configPath:	���������ļ�·��
			@type configPath:	string
		"""
		self.data = {}
		files = Language.searchConfigFile( configPath, ".xml" )			# ��ȡ�õ�����·���������ļ�

		# ����������
		doormap = {}
		# �������
		tombmap = {}
		print files
		for path in files:
			sect = Language.openConfigSection( path )
			assert sect is not None, "open %s false." % path
			print path
			name = sect["className"].asString
			sect = sect["Space"]
			if sect.has_key("Transport"):
				doorList = {}
				for objName, objSect in sect["Transport"].items():
					sign = objSect.readInt64("Sign")
					doordict = {"name" : objSect.readString("Name")}
					doordict["pos"] = objSect.readVector3("ReturnPos")
					doordict["direction"] = objSect.readVector3("ReturnDirection")
					doorList[sign] = doordict
				doormap[name] = doorList

			v = sect
			if v.has_key("Tomb"):
				tombs = []
				for objName, sect in v["Tomb"].items():
					s = {}
					s["position"] = sect["Position"].asVector3
					s["name"] = sect["SpaceName"].asString
					s["direction"] = sect["Direction"].asVector3
					tombs.append( s )
				tombmap[name] = tombs
			# ��ȡ�����رմ򿪵��ļ�
			Language.purgeConfig( path )
		self.data["Transport"] = doormap
		self.data["tomb"] = tombmap

g_spacedata = SpaceData( "config/server/gameObject/space" )

def getSpaceData( key ):
	"""
	��ȡ�������ݡ�
		@param key:	������
		@type key:	string
	"""
	return g_spacedata[key]

#
# $Log: not supported by cvs2svn $
# Revision 1.8  2008/01/25 10:10:47  yangkai
# �����ļ�·���޸�
#
# Revision 1.7  2007/09/28 02:18:41  yangkai
# �����ļ�·������:
# res/server/config  -->  res/config
#
# Revision 1.6  2007/09/25 07:26:24  kebiao
# �޸ļ���·��
#
# Revision 1.5  2007/09/24 02:41:06  kebiao
# ����·����ȡ��ʽ
#
# Revision 1.4  2006/12/21 08:01:06  panguankong
# ���߻�Ҫ���޸��˴��͵�͸������Ϣ
#
# Revision 1.3  2006/12/09 03:18:19  panguankong
# �����Ĺ�ط���
#
# Revision 1.2  2006/11/03 01:22:37  panguankong
# ��ӿռ������
#
# Revision 1.1  2005/12/01 06:38:22  xuning
# ����
#
#

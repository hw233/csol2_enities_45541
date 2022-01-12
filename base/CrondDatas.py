# -*- coding: gb18030 -*-
#
# $Id: CrondDatas.py,v 1.12 2008-07-15 04:21:55 kebiao Exp $

"""
����ƻ�ʱ������
"""

import BigWorld
import Language
import csconst
from bwdebug import *
import Function
import time

class CrondDatas:
	_instance = None
	def __init__( self, configPath = None ):
		"""
		���캯����
		@param configPath:	���������ļ�·��
		@type  configPath:	string
		"""
		assert CrondDatas._instance is None		# ���������������ϵ�ʵ��
		self._datas = {}	# key is BuffTime::_id and value is instance of BuffTime which derive from it.
		CrondDatas._instance = self

		if configPath is not None:
			self.load( configPath )

	@staticmethod
	def instance():
		"""
		ͨ�� action id ��ȡactionʵ��
		"""
		if CrondDatas._instance is None:
			CrondDatas._instance = CrondDatas()
		return CrondDatas._instance

	def __getitem__( self, key ):
		"""
		ȡ��Skillʵ��
		"""
		return self._datas[ key ]
		
	def load( self, configPath ):
		"""
		���ؼ���ʵ����
		@param configPath:	���������ļ�·��
		@type  configPath:	string
		"""
		sections = Language.openConfigSection( configPath )
		assert sections is not None, "open %s false." % configPath

		for section in sections.values():
			taskName 		= section.readString("key").strip().lower()
			taskCMD 		= section.readString("cmd").strip()
			activityName 	= section.readString("name").strip()
			activityDes 	= section.readString("description").strip()
			showOnClient 	= section.readInt("showOnClient")
			isStart		 	= section.readInt("isStart")
			condition		= section.readString("condition").strip()
			area			= section.readString("area").strip()
			act				= section.readInt("act")
			activityType	= section.readString("activityType").strip()
			line			= section.readString("line").strip()
			star			= section.readInt("star")
			persist		= section.readInt("persist")
			if not self._datas.has_key( taskName ):
				self._datas[ taskName ] = [{'cmd':taskCMD, 'name':activityName, 'description':activityDes, "showOnClient": showOnClient, 'isStart': isStart, 'condition': condition, 'area' : area, 'act' : act, 'activityType' : activityType, 'line' : line, 'star' : star, "persist" : persist }]
			else:
				self._datas[ taskName ].append( {'cmd':taskCMD, 'name':activityName, 'description':activityDes, "showOnClient": showOnClient, 'isStart': isStart, 'condition': condition, 'area' : area, 'act' : act, 'activityType' : activityType, 'line' : line, 'star' : star, "persist" : persist } )
				
		# ��ȡ�����رմ򿪵��ļ�
		Language.purgeConfig( configPath )
		INFO_MSG( "building of crondDatas load the complete!" )

	def getTaskCmds( self, taskName ):
		taskName = taskName.lower()
		if not taskName in self._datas:
			return []
		cmdList = []
		for i in self._datas[taskName]:
			if i["act"]:	# ֻ�б�����Ļ���ӽ��ƻ�����
				cmdList.append( i["cmd"] )
		return cmdList


	def getAllActivityData( self ):
		return self._datas


	def getTaskPersist( self, taskName ):
		"""
		���һ����ĳ���ʱ��
		"""
		if taskName in self._datas:
			for i in self._datas[taskName]:
				if i["isStart"]:
					return i["persist"]
		return 0
		

def instance():
	return CrondDatas.instance()

#
# $Log: not supported by cvs2svn $
#
#

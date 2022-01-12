# -*- coding: gb18030 -*-
#
"""
��Ϸ���������֧��

��Ϸ������ÿ10���������ݿ�����һ�����ݣ���ʽ��ÿ��Сʱ��10��20��...60�֡��統ǰΪ55�֣���ô�´�ȡ���ݵ�ʱ��Ϊ60�֣�
������Ҫ��5�������޸����ݣ�����60�ּ���Ч��������ÿ���趨����ǰ10���ӣ��� 20��ʱ����ĳ���棬��ô��10��֮ǰд�����ݣ�

�뱱���������ģ����ѭ����ԭ��:
1.��ʼʱ�䲻�ܴ��ڽ���ʱ�䡣
2.�Ѿ���ʼ�Ļ���߹��治���޸�.���ǿ���ɾ��������Ϸ��������ȡ���ݺ�������Ӧ�Ĵ������治�ٷ��ͣ������ֹͣ��

"""

import BigWorld
import Const
import time
import csdefine
import Love3
from bwdebug import *
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

class GameBroadcast(BigWorld.Base):
	"""
	��ʱ��־����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		self.registerGlobally( "GameBroadcast", self._onRegisterManager )		#ע���Լ���ȫ����
		self.broadcastDatas = {}
		self.actionDatas    = {}
		self.updateTime		= 0
		self.timer_id		= 0

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register GameBroadcast Fail!" )
			self.registerGlobally( "GameBroadcast", self._onRegisterManager )
		else:
			BigWorld.globalData["GameBroadcast"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("GameBroadcast Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
					  	"GameBroadcast" : "updataBroadcast",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )

	def updataBroadcast( self ):
		"""
		@define method
		���¹�������
		"""
		BigWorld.executeRawDatabaseCommand( "call GAMEBROADCAST()", self.updateDatas )

	def updateDatas( self, results, rows, errstr ):
		"""
		ˢ������
		"""
		if errstr:
			ERROR_MSG( "update gamebroadcast datas  failed, please check the mysql Stored Procedure is correct: %s" % errstr  )
			return

		sql = "select id,operationstart,distance,operationend,actiontype,content from custom_GameBroadcast where mark = 1"
		BigWorld.executeRawDatabaseCommand( sql, self.onGetDatas )


	def onGetDatas( self, results, rows, errstr):
		"""
		��ȡ����������
		"""
		if errstr:
			ERROR_MSG( "get gamebroadcast datas  failed, please check the mysql Stored Procedure is correct: %s" % errstr  )
			return
		self.updateTime = time.time()
		run = False		# ��Ǵ˴������Ƿ������
		for result in results:
			key = int(result[0])
			atype = int(result[4])
			pdict = {}
			if  atype == 0:		# �������͵�����
				pdict = self.broadcastDatas
			elif atype == 1:			# ����͵�����
				pdict = self.actionDatas

			if  pdict.has_key( key ):
				pdict[key]["version"]	=	self.updateTime
			else:
				pdict[key] = { "operationstart"	:	result[1],
								"interval"		:	int(result[2]),
								"operationend"	:	result[3],
								"content"		:	result[5],
								"version"		:	self.updateTime,
								"executeState"	:	0,
								}
				run = True

		if not self.timer_id and run:
			self.timer_id = self.addTimer( 0, 1.0 )

	def date2time( self, date ):
		"""
		����ת��ʱ��
		"""
		tdate =time.strptime(date,"%Y-%m-%d %H:%M:%S")
		return time.mktime(tdate )

	def onTimer( self, id, userArg ):
		"""
		"""
		INFO_MSG( "=======================================================>>>>>>>>>>b" )
		now = time.time()
		run = False
		for key,value in self.broadcastDatas.items():
			startTime = self.date2time(value["operationstart"])
			endTime   = self.date2time(value["operationend"])
			if value["version"] != self.updateTime:
				INFO_MSG( "version ��ƥ�� �����͸ù���" )
				self.broadcastDatas.pop(key)
				continue
			if now >= endTime:
				INFO_MSG( "����ʱ����������ٷ���" )
				self.broadcastDatas.pop(key)
				continue	# �Ѿ�������������
			if now >= startTime:
				interval = now - ( value["executeState"] + value["interval"])
				if interval >=0:
					if interval <= value["interval"]:		# ��ʾ��һ�η���ʱ������ڼ��δ����һ�����ʱ��
						Love3.g_baseApp.anonymityBroadcast( value["content"], [] )
						value["executeState"] = now
						INFO_MSG( "ʱ������,���͹���" )
					else:		# ��������ʱ��
						value["executeState"] = now - ( now - startTime ) % value["interval"]
						INFO_MSG( "��������ʱ��" )
			run = True

		global actions
		for key,value in self.actionDatas.items():
			startTime = self.date2time(value["operationstart"])
			endTime   = self.date2time(value["operationend"])
			if value["version"] != self.updateTime:					# ��ʾ������ֹ
				if value["executeState"] == 1:						# ��ʾ��δ�ر�
					actions[ value["content"] ].onEnd()				# ������
					value["executeState"] = 0
					INFO_MSG( "status = 1, �رջ" )
				self.actionDatas.pop(key)
				continue
			if now >= endTime:										# ����Ѿ�������ʱ��
				if value["executeState"] == 1:						# ��ʾ��δ�ر�
					actions[ value["content"] ].onEnd()					# ������
					value["executeState"] = 0
					INFO_MSG( "ʱ�䵽���رջ" )
				self.actionDatas.pop(key)
				continue
			if now >= startTime:									# ��ִ��ʱ����
				if value["executeState"] == 0:						# ��ʾ��δ��ʼִ��
					actions[ value["content"] ].onBegin()			# ��ʼ�
					value["executeState"] = 1
					INFO_MSG( "�����" )
			run = True
		if not run:
			INFO_MSG( "delteTimer==============>>>>" )
			self.delTimer( self.timer_id )
			self.timer_id = 0



class Action_SysMultExpMgr:
	"""
	�౶����
	"""
	@classmethod
	def onBegin( self ):
		"""
		���ʼ
		"""
		BigWorld.globalData["SysMultExpMgr"].onStart2()

	@classmethod
	def onEnd( self ):
		"""
		�����
		"""
		BigWorld.globalData["SysMultExpMgr"].onEnd2()

class Action_LuckyBoxActivityMgr:
	"""
	�콵����
	"""
	@classmethod
	def onBegin( self ):
		"""
		���ʼ
		"""
		BigWorld.globalData["LuckyBoxActivityMgr"].onStartLuckyBox()

	@classmethod
	def onEnd( self ):
		"""
		�����
		"""
		BigWorld.globalData["LuckyBoxActivityMgr"].onEndLuckyBox()


actions = {
			"Action_SysMultExpMgr" : Action_SysMultExpMgr,
			"Action_LuckyBoxActivityMgr" : Action_LuckyBoxActivityMgr,
			}
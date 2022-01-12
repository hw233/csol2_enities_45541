# -*- coding: gb18030 -*-

# $Id: AIBase.py,v 1.10 2008-05-04 09:05:21 kebiao Exp $

import sys
import csstatus
import Resource.AIData
from bwdebug import *
from AIEAISet import AIEAISet
from AISAISet import AISAISet
from AISetSystemDefLevel import AISetSystemDefLevel
from AISetSystemTempLevel import AISetSystemTempLevel
g_aiActions = Resource.AIData.aiAction_instance()
g_aiConditions = Resource.AIData.aiConditon_instance()
from CPUCal import CPU_CostCal
import csdefine
	
class AIBase:
	def __init__( self ):
		self._id = 0							# AI �� id  int
		self._name = ""							# AI �� ���� string
		self._conditions = []					# AI �� ���� instance of the AICondition of array
		self._actions = []						# AI �� ִ�ж��� instance of the AIAction of array
		self._activeRate = 100					# AI�Ļ���ʣ� Ĭ��100%
		self._duration = -1						# AI�ĳ���ʱ�䣬Ĭ��Ϊ-1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		self._id = section["id"].asInt
		self._name = section.readString( "name" )
		self._activeRate = section.readInt( "activeProb" )
		if section.has_key( "duration" ):
			self._duration = section.readFloat( "duration" )

		if section.has_key( "condition" ):
			for sec in section[ "condition" ].values():
				if sec.has_key( "isActivated" ) and sec[ "isActivated" ].asInt == 0:
					continue
				inst = g_aiConditions[ sec["id"].asInt ]()
				inst.setAIDataID( self._id )
				inst.init( sec )
				self._conditions.append( inst )

		if section.has_key( "action" ):
			for sec in section[ "action" ].values():
				if sec.has_key( "isActivated" ) and sec[ "isActivated" ].asInt == 0:
					continue
				try:
					inst = g_aiActions[ sec["id"].asInt ]()
				except KeyError, errstr:
					ERROR_MSG( "%i: no such ai action. action id = %i." % ( self._id, sec["id"].asInt ) )
					continue
				try:
					inst.setAIDataID( self._id )
					inst.init( sec )
				except Exception, errstr:
					ERROR_MSG( "%i: action(id = %i) init error." % ( self._id, sec["id"].asInt ) )
					sys.excepthook(*sys.exc_info())
					continue

				self._actions.append( inst )

	def getID( self ):
		"""
		ȡ��AI id
		"""
		return self._id

	def getName( self ):
		"""
		ȡ��AI����
		"""
		return self._name

	def getActiveRate( self ):
		"""
		ȡ��AIִ�и���
		"""
		return self._activeRate

	def getDuration( self ):
		"""
		ȡ��AIִ��ʱ��
		"""
		return self._duration

	def reset( self, entity ):
		"""
		vitural method
		���ô�AI
		"""
		pass

	def check( self, entity ):
		"""
		vitural method
		@param	entity	: 	ִ�д�AI��entity
		@type	entity	:	entity
		"""
		# �ж��Ƿ�������������
		for condtion in self._conditions:
			CPU_CostCal( csdefine.CPU_COST_AI_SC, csdefine.AI_CONDITION, condtion.getID() )
			result = condtion.check( self, entity )
			CPU_CostCal( csdefine.CPU_COST_AI_SC, csdefine.AI_CONDITION, condtion.getID() )
			if not result:
				nTitle=getattr(entity,"title")
				if nTitle == "debug" or entity.queryTemp("debug",0) == 1:
					DEBUG_MSG_FOR_AI( entity, "    �����ж�ʧ�ܣ�����ID: %i,��������: %i"%( condtion.getID(), self._conditions.index( condtion )+1 ),"AI_DEBUG_LOG: (NPCID %i className %s ) AICondtion( ID %i, index %i ) result False" % ( entity.id, entity.className, condtion.getID(), self._conditions.index( condtion )+1 ) )
				return False
		return True

	def do( self, entity ):
		"""
		vitural method
		@param	entity	: 	ִ�д�AI��entity
		@type	entity	:	entity
		"""
		if self._duration != -1 and self._duration > 0:
			entity.nextAIInterval.append( self._duration )

		# ִ��������Ϊ
		for action in self._actions:
			CPU_CostCal( csdefine.CPU_COST_AI_SC, csdefine.AI_ACTION, action.getID() )
			action.do( self, entity )
			CPU_CostCal( csdefine.CPU_COST_AI_SC, csdefine.AI_ACTION, action.getID() )

	def attach( self, entity ):
		"""
		vitural method
		@param	entity	: 	ִ�д�AI��entity
		@type	entity	:	entity
		"""
		pass

	def detach( self, entity ):
		"""
		vitural method
		@param	entity	: 	ִ�д�AI��entity
		@type	entity	:	entity
		"""
		pass

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴AIObjImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{ "param": None }������ʾ�޶�̬���ݡ�
		
		@return: ����һ��AI���͵��ֵ䡣AI������ϸ���������defs/alias.xml�ļ�
		"""
		return {  "param" : None }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵ�ai����ϸ�ֵ����ݸ�ʽ�����AIObjImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵ�ai�о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�
		
		@type data: dict
		"""
		return self

#
# $Log: not supported by cvs2svn $
# Revision 1.9  2008/04/22 04:16:34  kebiao
# ����˳�ʼ������
#
# Revision 1.8  2008/04/18 07:17:43  kebiao
# ȥ��SAI EAI������ ��������Ӧ����ȥ����
#
# Revision 1.7  2008/04/02 03:43:42  kebiao
# ȥ��֧������һ������������
#
# Revision 1.5  2008/03/29 07:04:50  kebiao
# configureEAIID ����Ϊlist
#
# Revision 1.4  2008/03/29 03:57:23  kebiao
# �����ӿڼ��������� SAI��EAI�Ĳ�����ʽ
#
# Revision 1.3  2008/03/29 02:10:42  kebiao
# no message
#
# Revision 1.2  2008/03/27 09:11:10  kebiao
# ȥ��isActive���֧��
#
# Revision 1.1  2008/03/25 07:43:09  kebiao
# ���AI���
#
#
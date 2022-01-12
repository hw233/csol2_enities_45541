# -*- coding: gb18030 -*-

# $Id: AIInterface.py,v 1.27 2008-07-30 01:26:44 kebiao Exp $

import csstatus
import csdefine
import Const
import BigWorld
import ECBExtend
import random
import time
from bwdebug import *
from Resource.AI.AIBase import AIBase
from optimize_with_cpp.interface import AIInterface_func as AI_CPP_OPTIMIZE
import Resource.AIData
g_aiDatas = Resource.AIData.aiData_instance()

class AIInterface:
	"""
	entity AI �ӿ�
	"""
	def __init__( self ):
		"""
		��ʼ������
		"""
		aiDefLevel = self.getScript().attrAIDefLevel
		self.attrAINowLevel = aiDefLevel
		self.attrAINowLevelTemp = self.attrAINowLevel
		self.setDefaultAILevel( aiDefLevel )

	def getAIDataMapping( self ):
		"""
		AI��������Ӱ��
		"""
		d = {
				csdefine.AI_TYPE_GENERIC_FREE	: self.attrFreeStateGenericAIs,
				csdefine.AI_TYPE_GENERIC_ATTACK : self.attrAttackStateGenericAIs,
				csdefine.AI_TYPE_SCHEME 		: self.attrSchemeAIs,
				csdefine.AI_TYPE_SPECIAL 		: self.attrSpecialAIs,
			}
		return d

	def addAI( self, level, ai, type ):
		"""
		define method.
		���entity��� ai
		@param ai  : ai of instance
		@param type: csdefine.AI_TYPE_SCHEME ...
		@param level: �趨��AI�����м���, �� AIϵͳ�ڴ˼���ʱ�Ż����и�AI
		"""
		if type == csdefine.AI_TYPE_GENERIC_FREE:
			self.noFightStateAICount += 1
		else:
			self.fightStateAICount += 1

		aimapping = self.getAIDataMapping()
		if isinstance( ai, AIBase ):
			if aimapping[ type ].has_key( level ):
				aimapping[ type ][ level ].append( ai )
			else:
				aimapping[ type ][ level ] = [ ai ]
		else:
			ERROR_MSG( "addAI only receive an AIBase of instance." )

	def removeAI( self, level, aid, type ):
		"""
		define method.
		ɾ��һ��ai��ͨ��ai��id�ͼ����Լ������ɾ����
		@param aid: ai of id
		@param type: csdefine.AI_TYPE_SCHEME ...
		"""
		ais = self.getAIDataMapping()[ type ].get( level )
		if ais:
			for idx, ai in enumerate( ais ):
				if ai.getID() == aid:
					ais.pop( idx )
					if type == csdefine.AI_TYPE_GENERIC_FREE:
						self.noFightStateAICount -= 1
					else:
						self.fightStateAICount -= 1
					return

	def addEventAI( self, event, level, ai ):
		"""
		define method.
		���entity��� ai
		@param ai   : ai of instance
		@param event: �¼�
		@param level: �趨��AI�����м���, �� AIϵͳ�ڴ˼���ʱ�Ż����и�AI
		"""
		if isinstance( ai, AIBase ):
			if self.triggersTable.has_key( event ):
				if self.triggersTable[ event ].has_key( level ):
					self.triggersTable[ event ][ level ].append( ai )
				else:
					self.triggersTable[ event ][ level ] = [ ai ]
			else:
				self.triggersTable[ event ] = { level : [ ai ] }
		else:
			ERROR_MSG( "addEventAI only receive an AIBase of instance." )

	def removeEventAI( self, event, level, aid ):
		"""
		ɾ��һ���¼�ai��ͨ��ai��id�ͼ����Լ��¼���ɾ����
		@param   aid: ai of id
		@param event: �¼�
		"""
		ais = self.triggersTable[ event ].get( level )
		if ais:
			for idx, ai in enumerate( ais ):
				if ai.getID() == aid:
					ais.pop( idx )
					return

	def setDefaultAILevel( self, level ):
		"""
		AI��Ĭ�ϼ���
		@param level: Ҫ���õļ���
		@type  level: int8
		"""
		nTitle=getattr(self,"title")
		if nTitle == "debug" or self.queryTemp("debug",0) == 1:
			DEBUG_MSG_FOR_AI( self, "    ����Ĭ�ϵȼ�AI %i to %i"%(  self.attrAIDefLevel, level ), "AI_DEBUG_LOG:setDefaultAILevel ( NPCID %i className %s) ) from %i to %i" % ( self.id, self.className, self.attrAIDefLevel, level ) )
		self.attrAIDefLevel = level

	def setNextRunAILevel( self, level ):
		"""
		����AI��һ�����еļ���
		@param level: Ҫ���õļ���
		@type  level: int8
		"""
		nTitle=getattr(self,"title")
		if nTitle == "debug" or self.queryTemp("debug",0) == 1:
			DEBUG_MSG_FOR_AI( self, "    ������һ�ȼ�AI %i to %i"%(  self.attrAINowLevelTemp, level ), "AI_DEBUG_LOG:setNextRunAILevel ( NPCID %i className %s) ) from %i to %i" % ( self.id, self.className, self.attrAINowLevelTemp, level ) )
		self.attrAINowLevelTemp = level

	def getDefaultAILevel( self ):
		"""
		��� AI��Ĭ�ϼ���
		"""
		return self.attrAIDefLevel

	def getNextRunAILevel( self ):
		"""
		��� AI��һ�����еļ���
		"""
		return self.attrAINowLevelTemp

	def getNowAILevel( self ):
		"""
		��� AI��ǰ���еļ���
		"""
		return self.attrAINowLevel

	def addSAI( self, aid ):
		"""
		����SAI SAI������������һ��ѭ��ʱ ǿ��ִ�д�AI
		@param type: AI������ ��AI_TYPE_GENERIC_FREE
		@param aid: ai of id.
		"""
		if not g_aiDatas.has( aid ):
			ERROR_MSG( "className %s:sai %i not found! please to check in config the ai of file." % ( self.className, aid ) )
			return
		self.saiArray.append( g_aiDatas[ aid ] )

	def insertSAI( self, aid ):
		"""
		����һ��SAI����ӵ�SAI�б����ǰ��,����ִ��
		"""
		if not g_aiDatas.has( aid ):
			ERROR_MSG( "className %s:sai %i not found! please to check in config the ai of file." % ( self.className, aid ) )
			return
		self.saiArray.insert( 0, g_aiDatas[ aid ] )

	def addEAI( self, aiID ):
		"""
		����EAI EAI��������AI������ǰ ���ò�������
		@param aiID: id
		"""
		if aiID != 0 and not( aiID in self.eaiIDArray ):
			nTitle=getattr(self,"title")
			if nTitle == "debug" or self.queryTemp("debug",0) == 1:
				DEBUG_MSG_FOR_AI( self, "    ����eai: %i"%aiID, "AI_DEBUG_LOG:( NPCID %i className %s) addEAI %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, aiID, self.attrAINowLevel,self.aiTargetID, self.targetID ) )
			self.eaiIDArray.append( aiID )

	def clearAllEAI( self ):
		"""
		�������eai��¼
		"""
		self.eaiIDArray = []

	def isEAI( self, aid ):
		"""
		�жϴ�aid�Ƿ���E��AI
		"""
		return aid in self.eaiIDArray

	def addSAIInst( self, ai, force = False ):
		"""
		ֱ�ӽ�һ��AI����ΪSAI
		@param ai	: ai of instance
		@param force: bool �Ƿ�ǿ������
		"""
		if not force in self.saiArray: # �������ظ�����
			return
		self.saiArray.append( ai )

	def setInsertAI( self, ai ):
		"""
		define method.
		���ò���AIʵ���� ͨ�����ⲿ����
		"""
		self.insert_ai = ai

	def doAllAI( self ):
		"""
		������������AI ��Ҫԭ���� ĳЩ�ط�������Ҫ��ʱ��ӳ������ȴ�AItimer
		"""
		if self.getState() == csdefine.ENTITY_STATE_FIGHT:
			self.onFightAIHeartbeat_AIInterface_cpp()
		else:
			self.onNoFightAIHeartbeat()

	def onFightAIHeartbeat( self ):
		"""
		ս��״̬��AI �� ������

		ע�⣺Ϊ���Ч�ʣ��˽ű������߼���ʹ��c++��ʵ��ΪonFightAIHeartbeat_AIInterface_cpp���˷�����ʧЧ�������Ҫ�޸Ĵ˷���������ϵwangshufeng��15:01 2012-12-7 by wsf��

		��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
		"""
		AI_CPP_OPTIMIZE.onFightAIHeartbeat(self)

	def onNoFightAIHeartbeat( self ):
		"""
		AI �� ����
		"""
		if self.noFightStateAICount <= 0:
			return
		elif self.intonating() or self.inHomingSpell():
			return

		# ƥ��AI���еȼ�
		if self.attrAINowLevelTemp != self.attrAINowLevel:
			self.attrAINowLevel = self.attrAINowLevelTemp
		nTitle=getattr(self,"title")
		aiDebug = self.queryTemp("debug",0)
		if nTitle == "debug" or aiDebug == 1:
			DEBUG_MSG_FOR_AI( self, "��ʼ��ͨAI", "" )
		# ִ��ͨ��AI��ѭ��
		for ai in self.attrFreeStateGenericAIs.get( self.attrAINowLevel, [] ):
			if self.isDestroyed or not self.isReal(): return
			if self.aiCommonCheck( ai ):
				if nTitle == "debug" or aiDebug == 1:
					DEBUG_MSG_FOR_AI( self, "  ��ʼAI: %i"%ai.getID(), "AI_DEBUG_LOG:begin ( NPCID %i className %s) )  FreeStateGenericAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID ) )
				ai.do( self )
				if nTitle == "debug" or aiDebug == 1:
					DEBUG_MSG_FOR_AI( self, "  ����AI: %i"%ai.getID(), "AI_DEBUG_LOG:end ( NPCID %i className %s) ) FreeStateGenericAIs do %i, attrAINowLevel %i, aiTarget %i, FinalTarget %i" % ( self.id, self.className, ai.getID(), self.attrAINowLevel, self.aiTargetID, self.targetID ) )
		if nTitle == "debug" or aiDebug == 1:
			DEBUG_MSG_FOR_AI( self, "������ͨAI", "" )
		if self.isDestroyed:
			return

		self.setAITargetID( 0 )					# ��ձ���AI����, ��һ������һ��ȥ����

	def onSpecialAINotDo( self ):
		"""
		virtual method.
		����AIִ��ʧ��Ҫ���Ĵ���
		"""
		pass

	def aiCommonCheck( self, ai ):
		"""
		AI �Ĺ����ж�����
		��ֱֹ�ӱ༭�÷������뵽�²�ģ�����޸ġ�
		"""
		return AI_CPP_OPTIMIZE.aiCommonCheck(self, ai)

	def resetAI( self ):
		"""
		����AI
		"""
		self.clearAllEAI()
		self.saiArray = []
		self.setInsertAI( None )
		self.fightStartTime = 0.0
		self.aiTargetID = 0
		aimapping = self.getAIDataMapping()
		aiDefLevel = self.getScript().attrAIDefLevel

		# ��ԭĬ��AI�ȼ�Ϊ�������ɵĵȼ�
		self.attrAINowLevel = aiDefLevel
		self.attrAINowLevelTemp = aiDefLevel
		nTitle=getattr(self,"title")
		if nTitle == "debug" or self.queryTemp("debug",0) == 1:
			DEBUG_MSG_FOR_AI( self, "    ai���ûص�0��", "AI_DEBUG_LOG:set ( NPCID %i className %s) )AILevel from %i to %i" % ( self.id, self.className, self.attrAIDefLevel, aiDefLevel ) )
		self.setDefaultAILevel( aiDefLevel )

		# �������AI
		self.comboAIArray = []
		self.comboAIState = False

		for aiItems in aimapping.itervalues():
			for aiList in aiItems.itervalues():
				for ai in aiList:
					ai.reset( self )

		for aiData in self.triggersTable.itervalues():
			for aiList in aiData.itervalues():
				for ai in aiList:
					ai.reset( self )

	def getEventTriTable( self, event ):
		"""
		��ȡĳ�¼�������ai��
		@param event: �¼�ID
		@return type: success to return the table, fail to return the []
		"""
		if not self.triggersTable.has_key( event ):
			return {}
		return self.triggersTable[ event ]

	def doAllEventAI( self, event ):
		"""
		ִ��ĳ�¼�����AI
		@param event: �¼�ID
		"""
		if self.isDestroyed:
			return
		nTitle=getattr(self,"title")
		aiDebug = self.queryTemp("debug",0)
		if nTitle == "debug" or aiDebug == 1:
			DEBUG_MSG_FOR_AI( self, "******��ʼ�¼�AI", "" )
		aidata = self.getEventTriTable( event )
		if aidata.has_key( self.attrAINowLevel ):
			for ai in aidata[ self.attrAINowLevel ]:
				if self.isDestroyed or not self.isReal(): return
				if self.aiCommonCheck( ai ):
					if nTitle == "debug" or aiDebug == 1:
						DEBUG_MSG_FOR_AI( self, "******��ʼAI: %i"%ai.getID(), "AI_DEBUG_LOG:begin ( NPCID %i className %s) ) at event %i, do %i, attrAINowLevel %i" % ( self.id, self.className, event, ai.getID(), self.attrAINowLevel ) )
					ai.do( self )
					if nTitle == "debug" or aiDebug == 1:
						DEBUG_MSG_FOR_AI( self, "******����AI: %i"%ai.getID(), "AI_DEBUG_LOG:end ( NPCID %i className %s) ) at event %i, do %i, attrAINowLevel %i" % ( self.id, self.className, event, ai.getID(), self.attrAINowLevel ) )
		if nTitle == "debug" or aiDebug == 1:
			DEBUG_MSG_FOR_AI( self, "******�����¼�AI", "" )

	def onAICommand( self, entityID, className, cmd ):
		"""
		< Define Method >
		ai ��� ��������λ֪ͨ��entity��һ����������ж�Ӧ��AI�������������򲻻���Ӱ��
		@param entityID : ������ID
		@param cmd		: ���� uint16
		"""
		self.setTemp( "AICommand", ( entityID, className, cmd ) )
		nTitle=getattr(self,"title")
		if nTitle == "debug" or self.queryTemp("debug",0) == 1:
			DEBUG_MSG_FOR_AI( self, "    ���յ�����%s��ָ��%i"%( className, cmd ), "AI_DEBUG_LOG:( NPCID %i className %s) )get a AICommand from ( id:%i, className:%s, cmd:%i ), attrAINowLevel %i" % ( self.id, self.className, entityID, className, cmd, self.attrAINowLevel ) )
		self.doAllEventAI( csdefine.AI_EVENT_COMMAND )

	def sendAICommand( self, entityID, cmd ):
		"""
		ai ��� ��������λ֪ͨ��entity��һ����������ж�Ӧ��AI�������������򲻻���Ӱ��
		@param entityID : ������ID
		@param cmd		: ���� uint16
		"""
		try:
			entity = BigWorld.entities[ entityID ]
		except:
			return
		nTitle=getattr(self,"title")
		if nTitle == "debug" or self.queryTemp("debug",0) == 1:
			DEBUG_MSG_FOR_AI( self, "    ����AIָ��%i"%cmd, "AI_DEBUG_LOG:( NPCID %i className %s) ) sed a AICommand to ( id:%i, className:%s, cmd:%i ), attrAINowLevel %i" % ( self.id, self.className, entityID, entity.className, cmd, self.attrAINowLevel ) )
		entity.onAICommand( self.id, self.className, cmd )

	def setAITargetID( self, entityID ):
		"""
		define method.
		����AI��ǰ��ѡ�����entityID
		"""
		self.aiTargetID = entityID

	def comboAICheck( self ):
		"""
		�ܷ�ִ������AI���,�����ִ�У��򷵻���ִ�е�comboID
		"""
		nTitle=getattr( self, "title" )
		if len( self.getScript().comboAITable ) == 0 or len( self.getScript().comboAITable[ self.attrAINowLevel ] ) == 0:
			return 0

		# ����AIִ�и���
		comboActiveRate = self.getScript().comboActiveRate
		randomRate = random.randint( 0, 100 )
		if comboActiveRate < randomRate:
			if nTitle == "debug" or self.queryTemp( "debug", 0 ) == 1:
				DEBUG_MSG_FOR_AI( self, "�ܹ�ִ��comboAI��⣬����False", "combAI check False, comboActiveRate %f, randomRate %f" % ( comboActiveRate, randomRate ) )
			return 0

		# �����ִ����һ��AI
		for comboID, item in self.getScript().comboAITable[ self.attrAINowLevel ].iteritems():
			activeRate = item["activeRate"]
			if random.randint( 1, 100 ) <= activeRate:
				return comboID

		return 0

	def addComboAI( self, comboID ):
		"""
		ִ������AI
		"""
		for id, item in self.getScript().comboAITable[ self.attrAINowLevel ].iteritems():
			if id == comboID:
				self.comboAIArray = item["aiDatas"]

	def doComboAI( self, comboID = 0 ):
		"""
		ִ������AI, comboID ��Ϊ0��ʾ��Ҫ�������AI
		"""
		nTitle=getattr( self, "title" )

		if comboID:			# ��Ҫ�������AI
			self.addComboAI( comboID )
			array = []
			for ai in self.comboAIArray:
				array.append( ai.getID() )
			if nTitle == "debug" or self.queryTemp( "debug", 0 ) == 1:
				DEBUG_MSG_FOR_AI( self, "���comboAI, comboID %i, array %s" % ( comboID, array ), "%s addcomboAI,comboID %i, array %s" % ( self.className, comboID, array ))

		if len( self.comboAIArray ):
			ai = self.comboAIArray.pop( 0 )
			if self.aiCommonCheck( ai ):
				ai.do( self )
				self.comboAIState = True
				if nTitle == "debug" or self.queryTemp( "debug", 0 ) == 1:
					DEBUG_MSG_FOR_AI( self, "ִ��comboAI,ai%i" % ( ai.getID() ), "%s, %i do comboAI %i " % ( self.className, self.id, ai.getID() ) )
			else:
				if nTitle == "debug" or self.queryTemp( "debug", 0 ) == 1:
					DEBUG_MSG_FOR_AI( self, "����comboAI" , "%s, %i reset comboAI" % ( self.className, self.id ) )
				self.comboAIArray = []
				self.comboAIState = False
			if len( self.comboAIArray ) == 0:
				if nTitle == "debug" or self.queryTemp( "debug", 0 ) == 1:
					DEBUG_MSG_FOR_AI( self, "����comboAI ", " %s, %i finish comboAI " % ( self.className, self.id ) )
		else:
			self.comboAIState = False

# $Log: not supported by cvs2svn $
# Revision 1.26  2008/07/30 01:14:06  kebiao
# fix a bug
#
# Revision 1.25  2008/07/30 01:03:58  kebiao
# ai_timer -> ai_fight_timer
#
# Revision 1.24  2008/07/21 03:51:24  kebiao
# �Ż���AIʱ������
#
# Revision 1.23  2008/07/19 07:44:25  kebiao
# fight_timer --> ai_fight_timer
#
# Revision 1.22  2008/07/09 03:18:05  kebiao
# ����aiTargetID ����ʱΪ0
#
# Revision 1.21  2008/07/02 07:55:11  kebiao
# ��AI������ʱ ��ʱ���еȼ�Ҳ����Ϊ0
#
# Revision 1.20  2008/05/31 03:13:25  kebiao
# ����AI �ڹ���������ִ�д���
#
# Revision 1.19  2008/05/26 04:18:52  kebiao
# ����insert_ai �����ⲿǿ�в��� ǿ��ִ��һ������
#
# Revision 1.18  2008/05/14 01:10:55  kebiao
# ����һ���������������BUG
#
# Revision 1.17  2008/05/05 07:16:00  kebiao
# �������������Ż���
#
# Revision 1.16  2008/05/04 09:02:31  kebiao
# �ı�self.aiTargetID ����λ��
#
# Revision 1.15  2008/04/21 00:59:23  kebiao
# �޸��¼�ѭ��BUG���޸�addAI�ӿڵȲ���
#
# Revision 1.14  2008/04/19 01:31:29  kebiao
# Ĭ��AI�ƶ���monster�������
#
# Revision 1.13  2008/04/18 07:15:39  kebiao
# ADD : setAITargetID
#
# Revision 1.12  2008/04/16 03:41:58  kebiao
# add:onAICommand, sendAICommand
#
# Revision 1.11  2008/04/10 08:51:11  kebiao
# ����AI��һ�η�Ӧ���ٶ�
#
# Revision 1.10  2008/04/07 08:56:17  kebiao
# ��������AI�ӿڹ���
#
# Revision 1.1  2008/03/25 07:42:07  kebiao
# ���AI���
#
#
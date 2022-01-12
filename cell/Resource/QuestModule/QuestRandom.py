# -*- coding: gb18030 -*-
#
# $Id: QuestRandom.py,v 1.12 2008-08-07 08:58:13 zhangyuxing Exp $

"""
�������ģ��
"""

from bwdebug import *
import csstatus
from Quest import *
from QuestDataType import QuestDataType
from ObjectScripts.GameObjectFactory import g_objFactory
import Love3

class QuestRandom( Quest ):
	def __init__( self ):
		Quest.__init__( self )
		self._group_id = 0							#������ID
		self._point = 0								#��������ֵ
		self._minus_interval = 0					#����ĸ���ȼ���������
		self._positive_interval = 0					#���������ȼ���������
		self._patternDict = {}						#ģʽƥ������ֵ�
		self._style = csdefine.QUEST_STYLE_RANDOM	#������ʽ


	def init( self, section ):
		"""
		@param section: ���������ļ�section
		@type  section: pyDataSection
		"""
		Quest.init( self, section )

		self._minus_interval = section.readInt( "minus_interval" )
		self._positive_interval = section.readInt( "positive_interval" )

		self._group_id = section.readInt( "random_group_id" )		# ���������ID(Ҳ���ǵ�ǰ�����parent id)

		self._point = section.readInt("point")						#����������ֵ

		extSection = section["quest_pattern"]						#�������ģʽ
		self._patternType = extSection.readInt( "type" )
		self._patternDict["p1"] = extSection.readString( "param1" )
		self._patternDict["p2"] = extSection.readString( "param2" )
		self._patternDict["p3"] = extSection.readString( "param3" )
		self._patternDict["p4"] = extSection.readString( "param4" )
		self._patternDict["p5"] = extSection.readString( "param5" )
		self._patternDict["p6"] = extSection.readString( "param6" )
		self._patternDict["p7"] = extSection.readString( "param7" )
		self._patternDict["p8"] = extSection.readString( "param8" )
		self._patternDict["p9"] = extSection.readString( "param9" )
		self._patternDict["p10"] = extSection.readString( "param10" )
		self._patternDict["p11"] = extSection.readString( "param11" )
		self._patternDict["p12"] = extSection.readString( "param12" )
		self._patternDict["p13"] = extSection.readString( "param13" )
		self._patternDict["p14"] = extSection.readString( "param14" )

		self.addToQuestBox()

	def getGroupQuest( self ):
		"""
		���������
		"""
		return Love3.g_taskData[self._group_id]

	def getGroupID( self ):
		"""
		���������ID
		"""
		return self._group_id


	def getPatternType( self ):
		"""
		�����������ģʽ����
		"""
		return self._patternType


	def addToQuestBox( self ):
		"""
		������������
		"""
		QuestBoxsDict = self.getQuestBoxsDict()
		for QuestBoxID in QuestBoxsDict:
			QuestBoxNpc = g_objFactory.getObject( QuestBoxID )
			if not QuestBoxNpc:
				ERROR_MSG( self.getID(), "QuestBox not found.", QuestBoxID )
			else:
				index = QuestBoxsDict[ QuestBoxID ]
				QuestBoxNpc.addQuestTask( self._group_id, index ) #�������Ӻ�������ID��

	def complete( self, player, rewardIndex, codeStr = "" ):
		"""
		"""
		#player.setTemp( "questKitTote", kitTote )
		#player.setTemp( "questOrder", order )
		self.setDecodeTemp( player, codeStr )
		player.setTemp( "questTeam", True )

		if not self.query( player ) == csdefine.QUEST_STATE_FINISH:
			#player.removeTemp( "questKitTote" )
			#player.removeTemp( "questOrder" )
			self.removeDecodeTemp( player, codeStr )
			player.removeTemp( "questTeam")
			return False

		player.setTemp( "RewardItemChoose" , rewardIndex )
		if not self.reward_( player, rewardIndex ):
			#player.removeTemp( "questKitTote" )
			#player.removeTemp( "questOrder" )
			self.removeDecodeTemp( player, codeStr )
			player.removeTemp( "questTeam")
			return False

		for e in self.afterComplete_:
			e.do( player )

		player.addSubQuestCount( self._group_id, 1 )
		player.addGroupPoint( self._group_id, self._point )
		questTitle = player.getQuest( self._group_id )._title

		#��ʾ�������
		#player.statusMessage( csstatus.ROLE_QUEST_RANDON_POINT, self._point )
		player.removeTemp( "RewardItemChoose" )
		#player.removeTemp( "questKitTote" )
		#player.removeTemp( "questOrder" )
		#self.removeDecodeTemp( player, codeStr )
		player.removeTemp( "questTeam")
		player.statusMessage( csstatus.ROLE_QUEST_COMPLETE, questTitle )
		return True

	def query( self, player ):
		"""
		��ѯ�����ɸ���������������������Ĳ�ѯ��������Ϊ������������
		"""
		return self.getGroupQuest().query( player )

	def fitPlayer( self, player ):
		"""
		�ж���������Ƿ��ʺ����
		@rtype  section: bool
		"""
		return ( player.level >= self._level - self._minus_interval ) and ( player.level <= self._level + self._positive_interval )

	def getParamsDict( self ):
		"""
		"""
		return self._patternDict

	def setDecodeTemp( self, player, codeStr ):
		"""
		���ñ����ַ�����ʱ����
		"""
		for task in player.questsTable[self.getGroupID()].getTasks().itervalues():
			task.setPlayerTemp( player, codeStr )


	def removeDecodeTemp( self, player, codeStr ):
		"""
		ɾ�������ַ�����ʱ����
		"""
		for task in player.questsTable[self.getGroupID()].getTasks().itervalues():
			task.removePlayerTemp( player )

	def getRewardsDetail( self, player ):
		"""
		��ý�������ϸ��
		"""
		r = []
		for reward in self.rewards_:
			if reward.type() == csdefine.QUEST_REWARD_RANDOM_ITEMS:		# rewards_��������������͵Ľ�������������ε���������������Ҳ��������⣬����ΪĿǰû�����ã��Ȳ����� by cwl
				continue
			r.append( reward.transferForClient( player, self.getGroupID() ) )
		if self.rewardsFixedItem_:
			r.append( self.rewardsFixedItem_.transferForClient( player, self.getGroupID() ) )
		if self.rewardsChooseItem_:
			r.append( self.rewardsChooseItem_.transferForClient( player, self.getGroupID() ) )
		# �߻�˵�����������ʾ��������ҿ�����Ϊ��ֹ�Ժ���ҪҪ����ʾ������Ҫ����
		#if self.rewardsRandItem_:
		#	r.append( self.rewardsRandItem_.transferForClient( player, self.getGroupID() ) )
		return r

# $Log: not supported by cvs2svn $
# Revision 1.11  2008/07/31 09:24:08  zhangyuxing
# �޸�һ����������
#
# Revision 1.10  2008/07/30 05:54:16  zhangyuxing
# getGroupQuestDegree ����Ϊ�� getGroupCount
# getGroupQuestCount  ����Ϊ�� getSubQuestCount
#
# Revision 1.9  2008/07/28 01:11:14  zhangyuxing
# �޸�֪ͨ������ɵ�˳��
#
# Revision 1.8  2008/01/22 08:18:41  zhangyuxing
# ���ӣ���չ��ģʽ�Ĳ�����Ŀ
#
# Revision 1.7  2008/01/11 06:51:43  zhangyuxing
# ����������ʽ self._style
#
# Revision 1.6  2008/01/09 03:23:16  zhangyuxing
# ���´������������������з����͹��ܡ�
#
# Revision 1.5  2007/11/02 03:57:03  phw
# QuestTasksDataType -> QuestDataType
#
# Revision 1.4  2007/06/19 08:46:46  huangyongwei
# ����״̬�Ķ�����ԭ���� csstatus ��ת���� csdefine ��
#
# Revision 1.3  2007/06/14 09:59:20  huangyongwei
# ���������˺궨��
#
# Revision 1.2  2007/05/05 08:19:51  phw
# model removed: whrandom
#
# Revision 1.1  2006/03/27 07:39:26  phw
# no message
#
#
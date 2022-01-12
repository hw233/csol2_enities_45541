# -*- coding: gb18030 -*-
#
# $Id: QTTask.py,v 1.44 2008-09-05 01:44:30 zhangyuxing Exp $

"""
"""

import csdefine
from Time import *
import struct
from bwdebug import *
from gbref import rds
import items
import QuestTaskDataType as QTTask
import csconst
import BigWorld
import NPCDatasMgr
import StringFormat
from guis.tooluis.richtext_plugins.PL_Link import PL_Link
from LabelGather import labelGather
#from config.client.ForbidLinkIDs import forbidMonsters
#rom config.client.ForbidLinkIDs import forbidNPCs
from config.client.ForbidLinkMonsterID import Datas as forbidMonsters
from config.client.ForbidLinkNPCID import Datas as forbidNPCs

# ------------------------------------------------------------>
# QTTaskTime
# ------------------------------------------------------------>

class QTTaskTime( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""
		self.str2 = ""
		self.val1 = 0	# �����ȡʱ��		int( time.time() + self._lostTime )
		self.val2 = 0	# ����ʧ��ʱ��		int( time.time() )
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_TIME

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		ltime = self.val2 - int(Time.time())
		if ltime < 0:
			ltime = 0
			isCollapsed = True

		HH = ltime/60/60
		MM = ltime/60 - HH * 60
		SS = ltime%60

		s = ""
		if HH > 0:
			s += labelGather.getText( "QTTask:main", "miTimeHMS", HH, MM, SS )
		elif MM > 0:
			s += labelGather.getText( "QTTask:main", "miTimeMS", MM, SS )
		else:
			s += labelGather.getText( "QTTask:main", "miTimeS", SS )

		return ( self.getType(), self.index,labelGather.getText( "QTTask:main", "miTimeRemain" ), s, isCollapsed, False, "", self.showOrder, "" )

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskTime )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return int(Time.time()) - self.val2 <= 0

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		return ""




# ------------------------------------------------------------>
# QTTaskKill
# ------------------------------------------------------------>
class QTTaskKill( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# Ҫɱ����Ŀ��ID��
		self.str2 = ""	# Ҫɱ����Ŀ������
		self.val1 = 0	# ��ǰɱ������
		self.val2 = 0	# Ҫɱ��������
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_KILL

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		if linkMark: npcID = self.str1
		return ( self.getType(),  self.index, labelGather.getText( "QTTask:main", "miKill" ) + mname,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				npcID
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2 )

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskKill )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

# ------------------------------------------------------------>
# QTTaskKills
# ------------------------------------------------------------>
class QTTaskKills( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# Ҫɱ����Ŀ��ID��
		self.str2 = ""	# Ҫɱ����Ŀ������
		self.val1 = 0	# ��ǰɱ������
		self.val2 = 0	# Ҫɱ��������
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_KILLS

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		mname = self.str2
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(),  self.index, labelGather.getText( "QTTask:main", "miKill" ) + mname,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				""
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2 )

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskKills )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

# ------------------------------------------------------------>
# QTTaskKill
# ------------------------------------------------------------>
class QTTaskKillWithPet( QTTaskKill ):
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_KILL_WITH_PET

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		if linkMark: npcID = self.str1
		return ( self.getType(),  self.index, labelGather.getText( "QTTask:main", "miKillWithPet" ) + mname,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				npcID
				)




class QTTaskKillDart( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# Ҫɱ����Ŀ��ID��
		self.val1 = 0	# ��ǰɱ������
		self.val2 = 0	# Ҫɱ��������
		"""
		QTTask.QuestTaskDataType.__init__( self )
		self.str2 = labelGather.getText( "QTTask:main", "dart_%s"%self.str1 )	# Ҫɱ����Ŀ������

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_DART_KILL

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(),  self.index, labelGather.getText( "QTTask:main", "miKill" ) + self.str2,
				detail2	,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				""
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2 )

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskKillDart )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1


# ------------------------------------------------------------>
# QTTaskDeliver
# ------------------------------------------------------------>
class QTTaskDeliver( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# Ҫ�ռ�����Ʒ���
		self.str2 = ""
		self.val1 = 0	# ��ǰ�ռ�����
		self.val2 = 0	# ��Ҫ�ռ�����
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_DELIVER

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		mname = items.instance().id2name( int(self.str1) )
		linkMark = ""
		npcID = ""
		if self.str2 != "" and self.str2 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str2
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		if linkMark: npcID = self.str2
		return ( self.getType(), 	self.index,
					labelGather.getText( "QTTask:main", "miDeliver" ) + mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( items.instance().id2name( int(self.str1 )) ,min(self.val1, self.val2), self.val2 )


	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskDeliver )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

# ------------------------------------------------------------>
# QTTaskDeliverQuality
# ------------------------------------------------------------>
class QTTaskDeliverQuality( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# Ҫ�ռ�����Ʒ���
		self.str2 = ""
		self.val1 = 0	# ��ǰ�ռ�����
		self.val2 = 0	# ��Ҫ�ռ�����
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_DELIVER_QUALITY

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		name = self.getPorpertyName()
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					name,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.getPorpertyName(), min(self.val1, self.val2), self.val2 )


	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskDeliverQuality )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def getPorpertyName( self ):
		"""
		ȡ����Ҫ������
		"""
		return eval( self.str2 )[0]

# ------------------------------------------------------------>
# QTTaskEventItemUsed
# ------------------------------------------------------------>
class QTTaskEventItemUsed( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# Ҫʹ�õ���Ʒ���
		self.str2 = ""	# ����Ŀ������
		self.val1 = 0	# ��ǰʹ������
		self.val2 = 0	# ��Ҫʹ������
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_EVENT_USE_ITEM

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		if self.val2 <= 1 or self.val1 == -1:
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted(),
					self.str1,
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( items.instance().id2name( int( self.str1 )) ,min(self.val1, self.val2), self.val2 )


	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskEventItemUsed )
		self.__dict__.update( taskInstance.__dict__ )


# ------------------------------------------------------------>
# QTTaskSkillLearned
# ------------------------------------------------------------>
class QTTaskSkillLearned( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str2 = ""	# ����Ŀ������
		self.str1 = ""	# Ҫѧϰ�ļ��ܱ��1
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SKILL_LEARNED

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		if self.isCompleted():
			detail2 = "1/1"
		else:
			detail2 = "0/1"
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%d" % self.val2
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		if linkMark: npcID = self.val2
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		learnedStr = "0/1"
		if self.isCompleted():
			learnedStr = "1/1"
		msg = "%s   %s"
		return msg % ( self.str2 ,learnedStr )


	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskSkillLearned )
		self.__dict__.update( taskInstance.__dict__ )


# ------------------------------------------------------------>
# QTTaskLivingSkillLearned
# ------------------------------------------------------------>
class QTTaskLivingSkillLearned( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str2 = ""	# ����Ŀ������
		self.str1 = ""	# Ҫѧϰ�ļ��ܱ��1
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_LIVING_SKILL_LEARNED

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		if self.isCompleted():
			detail2 = "1/1"
		else:
			detail2 = "0/1"
		
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%d" % self.val2
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		if linkMark: npcID = self.val2
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		learnedStr = "0/1"
		if self.isCompleted():
			learnedStr = "1/1"
		msg = "%s   %s"
		return msg % ( self.str2 ,learnedStr )


	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskLivingSkillLearned )
		self.__dict__.update( taskInstance.__dict__ )

# ------------------------------------------------------------>
# QTTaskEventTrigger
# ------------------------------------------------------------>
class QTTaskEventTrigger( QTTask.QuestTaskDataType ):
	"""
	����Ŀ�꣺��Ʒʹ���¼�������ĳ��ʹ��һ����Ʒ��ʹ�ú��Ŀ�꼴��ɣ�
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""	# Ҫʹ�õ���Ʒ���
		self.str2 = ""	# ����Ŀ������
		self.val1 = 0	# ��ǰ���״̬����
		self.val2 = 0	# ��Ҫ���״̬����
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_EVENT_TRIGGER

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskEventTrigger )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		# ʧ�ܱ��,val1Ϊ-1ʱ,Ϊ����ʧ��
		isCollapsed = False
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		if linkMark: npcID = self.str1
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 == -1:
			return labelGather.getText( "QTTask:main", "miCollapsed", self.str2 )
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2)

# ------------------------------------------------------------>
# QTTaskOwnPet; ����ӵ������
# ------------------------------------------------------------>
class QTTaskOwnPet( QTTask.QuestTaskDataType ):
	def __init__( self, *args ):
		"""
		self.str1 = ""
		self.str2 = ""
		self.val1 = 0	# ��ǰӵ������
		self.val2 = 0	# ��Ҫӵ������

		@param args: ( int ) as petAmount
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_OWN_PET

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskOwnPet )
		self.__dict__.update( taskInstance.__dict__ )


	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 > self.val2:
			return ""
		return labelGather.getText( "QTTask:main", "miOwnPet_1", min(self.val1, self.val2), self.val2 )

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		mname = labelGather.getText( "QTTask:main", "miOwnPet_2" )
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		if linkMark: npcID = self.str1
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)
#-------------------------------------------->
#QTTaskSubmit �ύ����Ŀ��
#-------------------------------------------->
class QTTaskSubmit( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	#��ƷID
		self.str2 = ""  #��Ʒ�����Լ���ֵ
		self.val1 = 0	#���ӵ����Ʒ����
		self.val2 = 0	#������Ҫ����Ʒ����
		"""
		QTTask.questTaskDataType.__init__( self )


	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT


	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		name = items.instance().id2name( int(self.str1) ) + self.getExtraDescription()
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					name,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s %s:    %i/%i"
		return msg % (items.instance().id2name( int( self.str1 ) ), self.getPorpertyName(), min(self.val1, self.val2), self.val2 )

	def getPorpertyName( self ):
		"""
		ȡ����Ҫ������
		"""
		return eval( self.str2 )[0]


	def getPorpertyValue( self ):
		"""
		ȡ����Ҫ������ֵ
		"""
		return int(eval( self.str2 )[1])

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def getExtraDescription( self ):
		"""
		"""
		return 	self.getPorpertyName()


#-------------------------------------------->
#QTTaskTeam �������
#-------------------------------------------->
class QTTaskTeam( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""		#����ְҵ
		self.str2 = ""  	#
		self.val1 = 0		#��ְҵ��������
		self.val2 = 0		#��ְҵ������������
		"""
		QTTask.questTaskDataType.__init__( self )


	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_TEAM


	def getDetail( self ):
		"""
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					csconst.g_chs_class[ int( self.str1 ) << 4 ],
					detail2,
					isCollapsed,
					self.val1 >= self.val2,
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s    %i/%i"
		return msg % ( csconst.g_chs_class[ int( self.str1 ) << 4 ], min(self.val1, self.val2), self.val2 )


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskTeam )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		"""
		return self.val1 >= self.val2

	def getOccupation( self ):
		"""
		����������ְҵ
		"""
		return int( self.str1 ) << 4


# ------------------------------------------------------------>
# QTTaskLevel
# ------------------------------------------------------------>
class QTTaskLevel( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# Ҫ�ﵽ�ĵȼ�����
		self.val1 = 0	# ��ҵ�ǰ�ȼ���ֵ
		self.val2 = 0	# Ҫ�ﵽ�ĵȼ���ֵ
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_LEVEL

	def getDetail( self ):
		"""
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = labelGather.getText( "QTTask:main", "miLevel", BigWorld.player().level )
		return ( self.getType(),  self.index, self.str1,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				""
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2 )

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskLevel )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= BigWorld.player().level


# ------------------------------------------------------------>
# QTTaskQuestNormal
# ------------------------------------------------------------>
class QTTaskQuestNormal( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.str1 = ""	# Ҫ�ﵽ�ĵȼ�����
		self.val1 = 0	# ��ҵ�ǰ�ȼ���ֵ
		self.val2 = 0	# Ҫ�ﵽ�ĵȼ���ֵ
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_QUEST_NORMAL

	def getDetail( self ):
		"""
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		return ( self.getType(),  self.index, self.str1,
				"",
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				""
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		return self.str1

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskQuest )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2


# ------------------------------------------------------------>
# QTTaskQuest
# ------------------------------------------------------------>
class QTTaskQuest( QTTaskQuestNormal ):
	def __init__( self ):
		"""
		self.str1 = ""	# Ҫ�ﵽ�ĵȼ�����
		self.val1 = 0	# ��ҵ�ǰ�ȼ���ֵ
		self.val2 = 0	# Ҫ�ﵽ�ĵȼ���ֵ
		"""
		QTTaskQuestNormal.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_QUEST


# ------------------------------------------------------------>
# QTTaskSubmitPicture
# ------------------------------------------------------------>
class QTTaskSubmitPicture( QTTaskDeliver ):
	def __init__( self ):
		"""
		self.str1 = ""	#��ƷID
		self.str2 = ""	#NPC calssName
		self.val1 = 0	#���ӵ������
		self.val2 = 0	#��Ҫ�ύ����
		"""
		QTTaskDeliver.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_PICTURE

	def getDetail( self ):
		"""
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		mname = NPCDatasMgr.npcDatasMgr.getNPC( self.str2 ).name
		linkMark = ""
		npcID = ""
		if self.str2 != "" and self.str2 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str2
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		if linkMark: npcID = self.str2
		return ( self.getType(),  self.index, mname + labelGather.getText( "QTTask:main", "miPicture" ),
				"",
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				npcID
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s %s   %i/%i"
		return ""
		#return msg % ( items.instance()[int( self.str1 )]["name"], g_objFactory.getObject(self.str2).getName(), "�Ļ���", self.val1, self.val2 )


	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskSubmitPicture )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

# ------------------------------------------------------------>
# QTTaskSubmitChangeBody
# ------------------------------------------------------------>
class QTTaskSubmitChangeBody( QTTaskSubmitPicture ):
	def __init__( self ):
		"""
		self.str1 = ""	#��ƷID
		self.str2 = ""	#NPC calssName
		self.val1 = 0	#���ӵ������
		self.val2 = 0	#��Ҫ�ύ����
		"""
		QTTaskSubmitPicture.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_CHANGE_BODY

	def getDetail( self ):
		"""
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		return ( self.getType(),  self.index, NPCDatasMgr.npcDatasMgr.getNPC( self.str2 ).name + labelGather.getText( "QTTask:main", "miChangeBody" ),
				"",
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				""
				)

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskSubmitChangeBody )
		self.__dict__.update( taskInstance.__dict__ )

# ------------------------------------------------------------>
# QTTaskSubmitDance
# ------------------------------------------------------------>
class QTTaskSubmitDance( QTTaskSubmitPicture ):
	def __init__( self ):
		"""
		self.str1 = ""	#��ƷID
		self.str2 = ""	#NPC calssName
		self.val1 = 0	#���ӵ������
		self.val2 = 0	#��Ҫ�ύ����
		"""
		QTTaskSubmitPicture.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_DANCE

	def getDetail( self ):
		"""
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		mname = NPCDatasMgr.npcDatasMgr.getNPC( self.str2 ).name
		linkMark = ""
		npcID = ""
		if self.str2 != "" and self.str2 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str2
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		if linkMark: npcID = self.str2
		return ( self.getType(),  self.index, mname + labelGather.getText( "QTTask:main", "miDance" ),
				"",
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				npcID
				)

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskSubmitDance )
		self.__dict__.update( taskInstance.__dict__ )

# ------------------------------------------------------------>
# QTTaskDeliver
# ------------------------------------------------------------>
class QTTaskDeliverPet( QTTaskDeliver ):
	def __init__( self ):
		"""
		self.str1 = ""	# Ҫ�ռ��ĳ�����
		self.str2 = "" 	# Ҫ�ռ��ĳ�������
		self.val1 = 0	# ��ǰ�ռ�����
		self.val2 = 0	# ��Ҫ�ռ�����
		"""
		QTTask.QTTaskDeliver.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_DELIVER_PET

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		if linkMark: npcID = self.str1
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					labelGather.getText( "QTTask:main", "miDeliverPet" ) + mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2 )


	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskDeliver )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1


class QTTaskSubmit_Quality( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#��ƷID
		self.str2 = ""  #��Ʒ�����Լ���ֵ
		self.val1 = 0	#���ӵ����Ʒ����
		self.val2 = 0	#������Ҫ����Ʒ����
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_QUALITY


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_Quality )
		self.__dict__.update( taskInstance.__dict__ )


class QTTaskSubmit_Slot( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#��ƷID
		self.str2 = ""  #��Ʒ�����Լ���ֵ
		self.val1 = 0	#���ӵ����Ʒ����
		self.val2 = 0	#������Ҫ����Ʒ����
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_SLOT


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_Slot )
		self.__dict__.update( taskInstance.__dict__ )

class QTTaskSubmit_Effect( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#��ƷID
		self.str2 = ""  #��Ʒ�����Լ���ֵ
		self.val1 = 0	#���ӵ����Ʒ����
		self.val2 = 0	#������Ҫ����Ʒ����
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_EFFECT


	def getMsg( self ):
		"""
		"""
		if self.val1 == self.val2:
			return ""
		msg = "%s %s:    %i/%i"
		return msg % (items.instance().id2name( int( self.str1 ) ), self.getPorpertyName(), min(self.val1, self.val2), self.val2 )


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_Effect )
		self.__dict__.update( taskInstance.__dict__ )


class QTTaskSubmit_Level( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#��ƷID
		self.str2 = ""  #��Ʒ�����Լ���ֵ
		self.val1 = 0	#���ӵ����Ʒ����
		self.val2 = 0	#������Ҫ����Ʒ����
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_LEVEL


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_Level )
		self.__dict__.update( taskInstance.__dict__ )

class QTTaskSubmit_Empty( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#��ƷID
		self.str2 = ""  #��Ʒ�����Լ���ֵ
		self.val1 = 0	#���ӵ����Ʒ����
		self.val2 = 0	#������Ҫ����Ʒ����
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_EMPTY

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_Empty )
		self.__dict__.update( taskInstance.__dict__ )

class QTTaskNotSubmit_Empty( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#��ƷID
		self.str2 = ""  #��Ʒ�����Լ���ֵ
		self.val1 = 0	#���ӵ����Ʒ����
		self.val2 = 0	#������Ҫ����Ʒ����
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_NOT_SUBMIT_EMPTY

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskNotSubmit_Empty )
		self.__dict__.update( taskInstance.__dict__ )

class QTTaskSubmit_Yinpiao( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#��ƷID
		self.str2 = ""  #��Ʒ�����Լ���ֵ
		self.val1 = 0	#���ӵ����Ʒ����
		self.val2 = 0	#������Ҫ����Ʒ����
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_YINPIAO


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_Yinpiao )
		self.__dict__.update( taskInstance.__dict__ )

	def getMsg( self ):
		"""
		"""
		msg = "%s %s:%i    %i/%i"
		return msg % (items.instance().id2name( int( self.str1 ) ), self.getPorpertyName(), self.getPorpertyValue(), min(self.val1, self.val2), self.val2 )


class QTTaskSubmit_Binded( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#��ƷID
		self.str2 = ""  #��Ʒ�����Լ���ֵ
		self.val1 = 0	#���ӵ����Ʒ����
		self.val2 = 0	#������Ҫ����Ʒ����
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_BINDED


	def getMsg( self ):
		"""
		"""
		if self.val1 == self.val2:
			return ""
		msg = "%s %s:    %i/%i"
		return msg % (items.instance().id2name( int( self.str1 ) ), self.getPorpertyName(), min(self.val1, self.val2), self.val2 )


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_Binded )
		self.__dict__.update( taskInstance.__dict__ )


# ------------------------------------------------------------>
# QTTaskKill
# ------------------------------------------------------------>
class QTTaskPetEvent( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.index = args[0]		# index
		self.str1 = args[1]			# ��������
		self.str2 = args[2]			# ��������
		self.val2 = args[3]			# ��������
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_PET_EVENT

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(),  self.index, self.str2,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				""
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2 )

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskPetEvent )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

# ------------------------------------------------------------>
# QTTaskevolution
# ------------------------------------------------------------>
class QTTaskEvolution( QTTaskKill ):	#������� spf

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_EVOLUTION

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			npcData = rds.npcDatasMgr.getNPC( self.str2 )
			if npcData is not None:
				mname = labelGather.getText( "QTTask:main", "mibeat" ) + npcData.entityName
				linkMark = "goto:%s" % self.str2
			else:
				linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		if linkMark: npcID = linkMark.split( ":" )[1]
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(),  self.index, mname,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				npcID
				)



# ------------------------------------------------------------>
# QTTaskEventTrigger
# ------------------------------------------------------------>
class QTTaskImperialExamination( QTTask.QuestTaskDataType ):
	"""
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_IMPERIAL_EXAMINATION

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskImperialExamination )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		# ʧ�ܱ��,val1Ϊ-1ʱ,Ϊ����ʧ��
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = labelGather.getText( "QTTask:main", "miRight_1", min(self.val1, self.val2), self.val2, self.str1 )
		return ( self.getType(), 	self.index,
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 > self.val2:
			return ""
		return labelGather.getText( "QTTask:main", "miRight_2", self.str2 ,min(self.val1, self.val2), self.val2, self.str1 )


# ------------------------------------------------------------>
# QTTaskShowKaoGuan
# ------------------------------------------------------------>
from csconst import KAOGUANS
class QTTaskShowKaoGuan( QTTask.QuestTaskDataType ):
	"""
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SHOW_KAOGUAN

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskShowKaoGuan )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		
		detail = ""
		npcID = ""
		if KAOGUANS.has_key( self.val1+1 ):
			detail = KAOGUANS[self.val1+1]
			npcID = detail.split( ":" )[1].split( ";" )[0]

		if self.val1 == -1:
			isCollapsed = True	
			detail = ""
		return (self.getType(),
					self.index,
					self.str2,
					detail,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = ""
		if KAOGUANS.has_key( self.val1+1 ):
			msg = labelGather.getText( "QTTask:main", "miNextTest", self.val1 + 1 )
		return msg



# ------------------------------------------------------------>
# QTTaskQuestiong
# ------------------------------------------------------------>
class QTTaskQuestion( QTTaskEventTrigger ):
	"""
	����Ŀ�꣺��Ʒʹ���¼�������ĳ��ʹ��һ����Ʒ��ʹ�ú��Ŀ�꼴��ɣ�
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""	# Ҫʹ�õ���Ʒ���
		self.str2 = ""	# ����Ŀ������
		self.val1 = 0	# ��ǰ���״̬����
		self.val2 = 0	# ��Ҫ���״̬����
		"""
		QTTaskEventTrigger.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_QUESTION

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskQuestion )
		self.__dict__.update( taskInstance.__dict__ )
		
	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		# ʧ�ܱ��,val1Ϊ-1ʱ,Ϊ����ʧ��
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)



# ------------------------------------------------------------>
# QTTaskPetAct	��ս����	2009-07-15 14:30 SPF
# ------------------------------------------------------------>
class QTTaskPetAct( QTTaskEventTrigger ):
	"""
	����Ŀ�꣺��Ʒʹ���¼�������ĳ��ʹ��һ����Ʒ��ʹ�ú��Ŀ�꼴��ɣ�
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""	# Ҫʹ�õ���Ʒ���
		self.str2 = ""	# ����Ŀ������
		self.val1 = 0	# ��ǰ���״̬����
		self.val2 = 0	# ��Ҫ���״̬����
		"""
		QTTaskEventTrigger.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_PET_ACT

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskPetAct )
		self.__dict__.update( taskInstance.__dict__ )

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		self.str2 = labelGather.getText( "QTTask:main", "miPetAct" )
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

class QTTaskTalk( QTTaskEventTrigger ):
	"""
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTaskEventTrigger.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_TALK

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskTalk )
		self.__dict__.update( taskInstance.__dict__ )

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		# ʧ�ܱ��,val1Ϊ-1ʱ,Ϊ����ʧ��
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1 not in [item["npcID"] for item in forbidNPCs]:
			linkMark = "goto:%s" % self.str1
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		if linkMark: npcID = self.str1
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)


class QTTaskHasBuff( QTTaskEventTrigger ):
	"""
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTaskEventTrigger.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_HASBUFF

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskHasBuff )
		self.__dict__.update( taskInstance.__dict__ )

class QTTaskPotentialFinish( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		self.index = args[0]		# index
		self.str1 = args[1]			# ��������
		self.str2 = args[2]			# ��������
		self.val2 = args[3]			# ��������
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_POTENTIAL_FINISH

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(),  self.index, self.str1,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				""
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str1 ,min(self.val1, self.val2), self.val2 )

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskPotentialFinish )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1


class QTTaskSubmit_LQEquip( QTTaskSubmit ):
	def __init__( self ):
		"""
		self.str1 = ""	#��ƷID
		self.str2 = ""  #��Ʒ�����Լ���ֵ
		self.val1 = 0	#���ӵ����Ʒ����
		self.val2 = 0	#������Ҫ����Ʒ����
		"""
		QTTaskSubmit.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_LQEQUIP


	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskSubmit_LQEquip )
		self.__dict__.update( taskInstance.__dict__ )


	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		name = labelGather.getText( "QTTask:main", "miHighLevelEquip" )
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 =  "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					name,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s %s:    %i/%i"
		return msg % (labelGather.getText( "QTTask:main", "miHighLevelEquip" ), self.getPorpertyName(), min(self.val1, self.val2), self.val2 )


	def getPorpertyName( self ):
		"""
		ȡ����Ҫ������
		"""
		return ""


# ------------------------------------------------------------>
# QTTaskEventSkillUsed
# ------------------------------------------------------------>
class QTTaskEventSkillUsed( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_EVENT_USE_SKILL

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		mname = self.str1.split(":")[0]
		linkMark = ""
		npcID = ""
		if self.str2 != "" and self.str2 not in [item["monsterID"] for item in forbidMonsters]:
			linkMark = "goto:%s" % self.str2
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		if linkMark: npcID = self.str2
		if self.val2 <= 1 or self.val1 == -1:
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str1.split(":")[0] ,min(self.val1, self.val2), self.val2 )


	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskEventSkillUsed )
		self.__dict__.update( taskInstance.__dict__ )



# ------------------------------------------------------------>
# QTTaskEventUpdateSetRevivePos
# ------------------------------------------------------------>
class QTTaskEventUpdateSetRevivePos( QTTask.QuestTaskDataType ):
	def __init__( self ):
		"""
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_EVENT_REVIVE_POS

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		if self.val2 <= 1 or self.val1 == -1:
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					self.str1,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str1, min(self.val1, self.val2), self.val2 )


	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskEventUpdateSetRevivePos )
		self.__dict__.update( taskInstance.__dict__ )


class QTTaskEnterSpace( QTTask.QuestTaskDataType ):
	"""
	����ĳһ���ռ�
	"""	
	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_ENTER_SPCACE

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str1, min(self.val1, self.val2), self.val2 )

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True	
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return (self.getType(),
					self.index,
					self.str1,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskEnterSpace )
		self.__dict__.update( taskInstance.__dict__ )

class QTTaskPotential( QTTask.QuestTaskDataType ):
	"""
	Ǳ������ר��
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""
		self.str2 = ""
		self.val1 = 0
		self.val2 = 0
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_POTENTIAL

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskPotential )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		# ʧ�ܱ��,val1Ϊ-1ʱ,Ϊ����ʧ��
		isCollapsed = False
		mname = self.str2
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 == -1:
			return labelGather.getText( "QTTask:main", "miCollapsed", self.str2 )
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2 )
		
class QTTaskAddCampMorale( QTTask.QuestTaskDataType ):
	"""
	��ȡ��Ӫʿ��
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""
		self.str2 = ""
		self.val1 = 0
		self.val2 = 0
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_ADD_CAMP_MORALE

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskAddCampMorale )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		# ʧ�ܱ��,val1Ϊ-1ʱ,Ϊ����ʧ��
		isCollapsed = False
		mname = self.str1
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		if self.val1 == -1:
			return labelGather.getText( "QTTask:main", "miCollapsed", self.str1 )
		if self.val1 > self.val2:
			return ""
		msg = "%s   %i/%i"
		return msg % ( self.str1 ,min(self.val1, self.val2), self.val2 )
		
	
	
		
class QTTaskKill_CampActivity( QTTaskKill ):
	"""
	��Ӫ���ɱ��������
	"""
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_CAMP_KILL
		
	def getSpaceLabel( self ):
		"""
		���Ŀ�����ڵ�ͼ
		"""
		spaces = self.str3.split(";")
		if len( spaces ) == 0:
			return ""
		return spaces[0]
	
	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		mname = self.str2
		linkMark = ""
		npcID = ""
		
		dstPos = None
		if self.str1 != "" and self.str1 not in [item["monsterID"] for item in forbidMonsters]:
			for i in self.str3.split(";"):
				if i == "":
					continue
				dstPos = rds.npcDatasMgr.getNPCPosition( self.str1, i )
				if not dstPos:
					continue
				pos = [ dstPos[0], dstPos[1], dstPos[2] ]
				linkMark = "goto:%s*%s"%( pos, i )
				break
			if not dstPos:
				linkMark = "goto:%s" % self.str2
			mname = PL_Link.getSource( self.str2, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		if linkMark: npcID = self.str1
		return ( self.getType(),  self.index, labelGather.getText( "QTTask:main", "miKill" ) + mname,
				detail2,
				isCollapsed,
				self.isCompleted(),
				"",
				self.showOrder,
				npcID
				)
	
class QTTaskVehicleActived( QTTaskEventTrigger ):
	"""
	����ָ�����
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTaskEventTrigger.__init__( self )
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_VEHICLE_ACTIVED
	
	def isCompleted( self ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskVehicleActived )
		self.__dict__.update( taskInstance.__dict__ )

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		self.str2 = labelGather.getText( "QTTask:main", "miVehicleAct" )
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					""
				)

class QTTaskDeliver_CampActivity( QTTaskDeliver ):
	"""
	��Ӫ�������Ʒ����Ŀ��
	"""
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_CAMPACT_DELIVER
		
	def getSpaceLabel( self ):
		"""
		���Ŀ�����ڵ�ͼ
		"""
		return self.str2.split(":")[0]

	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		mname = items.instance().id2name( int(self.str1) )
		linkMark = ""
		npcID = ""
		if self.str2 != "" and self.str2.split(":")[1] not in [item["monsterID"] for item in forbidMonsters]:	# str2 like: "spaceName:NPCID"
			spaceName = self.str2.split(":")[0]
			npcClassName = self.str2.split(":")[1]
			dstPos = rds.npcDatasMgr.getNPCPosition( npcClassName, spaceName )
			if dstPos:
				pos = [ dstPos[0], dstPos[1], dstPos[2] ]
				linkMark = "goto:%s*%s"%( pos, spaceName )
			else:
				linkMark = "goto:%s" % npcClassName
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		
		if linkMark: npcID = self.str2.split(":")[1]
		return ( self.getType(), 	self.index,
					labelGather.getText( "QTTask:main", "miDeliver" ) + mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)

class QTTaskTalk_CampActivity( QTTaskTalk ):
	"""
	��Ӫ��Ի�����
	"""
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_CAMPACT_TALK
		
	def getSpaceLabel( self ):
		"""
		���Ŀ�����ڵ�ͼ
		"""
		return self.str1.split(":")[0]
		
	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		# ʧ�ܱ��,val1Ϊ-1ʱ,Ϊ����ʧ��
		mname = self.str2
		linkMark = ""
		npcID = ""
		if self.str1 != "" and self.str1.split(":")[1] not in [item["npcID"] for item in forbidNPCs]:
			spaceName = self.str1.split(":")[0]
			npcClassName = self.str1.split(":")[1]
			dstPos = rds.npcDatasMgr.getNPCPosition( npcClassName, spaceName )
			if dstPos:
				pos = [ dstPos[0], dstPos[1], dstPos[2] ]
				linkMark = "goto:%s*%s"%( pos, spaceName )
			else:
				linkMark = "goto:%s" % npcClassName
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
		
		if linkMark: npcID = self.str1.split(":")[1]
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
			detail2 = ""
		elif self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return ( self.getType(), 	self.index,
					mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					"",
					self.showOrder,
					npcID
				)


class QTTaskEventItemUsed_CampActivity( QTTaskEventItemUsed ):
	"""
	��Ӫ�ʹ����Ʒ����Ŀ��:��ָ����ͼ�ϵ�Ŀ��ʹ����Ʒ
	"""
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_CAMPACT_EVENT_USE_ITEM
		
	def getSpaceLabel( self ):
		"""
		���Ŀ�����ڵ�ͼ
		"""
		return self.str2.split(":")[0]
	
	def getDetail( self ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		className = self.str2.split(":")[1]
		mname = ""
		linkMark = ""
		npcID = ""
		if className != "" and className not in [item["npcID"] for item in forbidNPCs]:
			spaceName = self.str2.split(":")[0]
			mname = NPCDatasMgr.npcDatasMgr.getNPC( className ).name
			dstPos = rds.npcDatasMgr.getNPCPosition( className, spaceName )
			if dstPos:
				pos = [ dstPos[0], dstPos[1], dstPos[2] ]
				linkMark = "goto:%s*%s"%( pos, spaceName )
			else:
				linkMark = "goto:%s" % className
			mname = PL_Link.getSource( mname, linkMark, cfc = "c4", hfc = "c3" )	# ��������Ϣת��Ϊ�������ı�
			
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		if self.val2 <= 1 or self.val1 == -1:
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
			
		return ( self.getType(), 	self.index,
					self.str2.split(":")[2] % mname,
					detail2,
					isCollapsed,
					self.isCompleted(),
					self.str1,
					self.showOrder,
					className
				)

QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_TIME,					QTTaskTime )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_KILL,					QTTaskKill )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_KILLS,					QTTaskKills )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DART_KILL,				QTTaskKillDart )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DELIVER,				QTTaskDeliver )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVENT_USE_ITEM,		QTTaskEventItemUsed )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SKILL_LEARNED,			QTTaskSkillLearned )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_LIVING_SKILL_LEARNED,			QTTaskLivingSkillLearned )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_OWN_PET,				QTTaskOwnPet )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT,				QTTaskSubmit )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_TEAM,					QTTaskTeam )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVENT_TRIGGER,			QTTaskEventTrigger )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_LEVEL,					QTTaskLevel )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_QUEST,					QTTaskQuest )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_QUEST_NORMAL,			QTTaskQuestNormal )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_PICTURE,		QTTaskSubmitPicture)
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_CHANGE_BODY,	QTTaskSubmitChangeBody)
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_DANCE,			QTTaskSubmitDance)
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DELIVER_PET,			QTTaskDeliverPet)
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_QUALITY,		QTTaskSubmit_Quality )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_SLOT,			QTTaskSubmit_Slot )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_EFFECT,			QTTaskSubmit_Effect )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_LEVEL,			QTTaskSubmit_Level )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_BINDED,			QTTaskSubmit_Binded )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_EMPTY,			QTTaskSubmit_Empty)
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_PET_EVENT,				QTTaskPetEvent )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVOLUTION,				QTTaskEvolution )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_YINPIAO,		QTTaskSubmit_Yinpiao )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_IMPERIAL_EXAMINATION,	QTTaskImperialExamination )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_KILL_WITH_PET,			QTTaskKillWithPet )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SHOW_KAOGUAN,			QTTaskShowKaoGuan )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_QUESTION,				QTTaskQuestion )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_PET_ACT,				QTTaskPetAct )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_TALK,					QTTaskTalk )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_HASBUFF,				QTTaskHasBuff )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DELIVER_QUALITY,		QTTaskDeliverQuality )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_POTENTIAL_FINISH,		QTTaskPotentialFinish )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_LQEQUIP,		QTTaskSubmit_LQEquip )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVENT_USE_SKILL,		QTTaskEventSkillUsed )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVENT_REVIVE_POS,		QTTaskEventUpdateSetRevivePos )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_ENTER_SPCACE,			QTTaskEnterSpace )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_POTENTIAL,				QTTaskPotential )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_NOT_SUBMIT_EMPTY,		QTTaskNotSubmit_Empty )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_ADD_CAMP_MORALE,		QTTaskAddCampMorale )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_CAMP_KILL,				QTTaskKill_CampActivity )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_VEHICLE_ACTIVED,				QTTaskVehicleActived )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_CAMPACT_DELIVER,		 QTTaskDeliver_CampActivity )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_CAMPACT_TALK,		 QTTaskTalk_CampActivity )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_CAMPACT_EVENT_USE_ITEM, QTTaskEventItemUsed_CampActivity )



# $Log: not supported by cvs2svn $
# Revision 1.43  2008/08/20 01:26:25  zhangyuxing
# ���ӳ���ָ�������������Ŀ��
#
# Revision 1.42  2008/08/15 09:19:37  zhangyuxing
# �ϲ��ύ������Ʒ����Ŀ�꣬����ǿ������Ƕ��ǿ���ȼ�����Ŀ��
#
# Revision 1.41  2008/08/12 07:13:31  zhangyuxing
# �޸���Ʒ���� int , str ֮�䶯̬����
#
# Revision 1.40  2008/08/07 08:59:22  zhangyuxing
# �����ύ��������Ŀ��
#
# Revision 1.39  2008/08/04 06:30:58  zhangyuxing
# �����ύ��������Ŀ��
#
# Revision 1.38  2008/07/28 02:34:25  zhangyuxing
# ���ӵȼ���������
#
# Revision 1.37  2008/07/14 06:19:15  zhangyuxing
# ����ȼ��仯��������ɲ�ѯ
#
# Revision 1.35  2008/06/13 05:34:17  wangshufeng
# ��������������Ϣ
#
# Revision 1.34  2008/05/28 08:55:38  zhangyuxing
# no message
#
# Revision 1.33  2008/05/16 01:37:35  zhangyuxing
# no message
#
# Revision 1.32  2008/05/12 07:13:54  wangshufeng
# �޸�QTTaskEventTrigger��getDetail��if self.val2 <= 1�޸�Ϊif self.val2 < 1
#
# Revision 1.31  2008/04/26 06:43:30  zhangyuxing
# no message
#
# Revision 1.30  2008/04/15 06:51:13  zhangyuxing
# �޸�������ʾ ���Ӵ��ڷ�ĸ�����
#
# Revision 1.29  2008/01/25 09:24:59  kebiao
# modify:QTTaskEventTrigger  in COPYINSTANCE
#
# Revision 1.28  2008/01/22 08:19:44  zhangyuxing
# no message
#
# Revision 1.27  2008/01/22 02:20:26  phw
# fixed: TypeError: isCompleted() takes exactly 2 arguments (1 given)
#
# Revision 1.26  2008/01/09 03:48:46  zhangyuxing
# ��������Ŀ��
# QTTaskTeam����ӳ�ԱְҵҪ��
# QTTaskSubmitHole��������
# �޸���������Ŀ��getDetail �����ķ��أ�������������
#
# Revision 1.25  2007/12/27 02:02:20  phw
# method modified: QTTaskEventTrigger::isCompleted(), ȥ������Ĳ���player
#
# Revision 1.24  2007/12/19 03:34:39  kebiao
# ����¼��������� ӳ��
#
# Revision 1.23  2007/12/19 03:32:52  kebiao
# add:QTTaskEventTrigger �¼���������
#
# Revision 1.22  2007/12/17 11:31:27  zhangyuxing
# �����ࣺ class QTTaskSubmit( QTTaskDeliver ):
#
# Revision 1.21  2007/12/08 09:23:54  phw
# ������QTTaskKill��û����ʾ�������Ƶ�����
#
# Revision 1.20  2007/12/05 07:00:59  phw
# class added: QTTaskOwnPet
#
# Revision 1.19  2007/11/02 03:51:07  phw
# �޸ļ̳�ģʽ��ֱ�Ӽ̳���QuestTaskDataType.QuestTaskDataType����ֱ����QuestTaskDataTypeģ��ע���Լ�
#
# Revision 1.18  2007/09/19 01:19:57  phw
# method modified: QTTaskDeliver::addToStream(), QTTaskDeliver::loadFromStream(), ������"DeprecationWarning: 'L' format requires 0 <= number <= 4294967295"����ʾ
#
# Revision 1.17  2007/06/14 10:32:35  huangyongwei
# ������ȫ�ֺ궨��
#
# Revision 1.16  2007/05/18 01:56:39  kebiao
# no message
#
# Revision 1.15  2007/05/17 08:07:30  kebiao
# ����ʱ����ʾ��ʽ
#
# Revision 1.14  2007/05/15 08:33:32  kebiao
# ʹ��Time �����������ʱ��ͬ������
#
# Revision 1.13  2007/03/20 01:31:53  phw
# method modified: QTTaskTime::getDetail(), ʣ��ʱ��С��0ʱ��Ϊ0��������ʧ�ܡ�
#
# Revision 1.12  2007/03/14 03:01:04  kebiao
# ȥ��QTTASKTIME ��һ���ؽ�������ж�
# �˴����ڷ������Ϳͻ���ʱ��ͬ������ �����ؽ����
#
# Revision 1.11  2007/03/12 06:55:52  kebiao
# ��ӻ�ȡ��task״̬�ӿ�
#
# Revision 1.10  2007/03/09 06:32:23  kebiao
# ����timeTask�������
#
# Revision 1.9  2007/02/12 07:16:05  phw
# QTTaskDeliver���ʹ����ʽ��"LLLLB"��Ϊ"LLLlB"
#
# Revision 1.8  2006/09/05 09:14:57  chenzheming
# no message
#
# Revision 1.7  2006/08/09 08:31:24  phw
# ����ģ��ItemDataList��Ϊ����items
#
# Revision 1.6  2006/08/05 08:17:58  phw
# �޸Ľӿڣ�
#     QTTaskDeliver::getDetail()
#     from: name = ItemDataList.instance()[self._deliverID].name
#     to:   name = ItemDataList.instance().id2name( self._deliverID )
#
# Revision 1.5  2006/03/28 07:18:52  phw
# changed TASK_OBJECTIVE_USE_ITEM to QUEST_OBJECTIVE_ACTIVE_ITEM
#
# Revision 1.4  2006/03/28 04:47:38  phw
# change class name from QTTaskUseItem to QTTaskActiveItem
#
# Revision 1.3  2006/03/28 03:38:22  phw
# ����ʹ����Ʒ����Ŀ�꣬getDetail()��ԭ���ķ��ؼ�������Ϊ������ʽ��
# @return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
#
# Revision 1.2  2006/01/24 09:36:57  phw
# no message
#
# Revision 1.1  2006/01/24 02:19:56  phw
# no message
#
#
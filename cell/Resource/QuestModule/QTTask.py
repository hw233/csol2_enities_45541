# -*- coding: gb18030 -*-
#
# $Id: QTTask.py,v 1.66 2008-09-01 03:36:17 zhangyuxing Exp $

"""
"""

import csdefine
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *
import time
import struct
import items
import QuestTaskDataType as QTTask
from ObjectScripts.GameObjectFactory import g_objFactory
import cPickle
import csstatus
import csdefine
import csconst
import sys
import ItemTypeEnum

# ------------------------------------------------------------>
# QTTaskTime
# ------------------------------------------------------------>

class QTTaskTime( QTTask.QuestTaskDataType ):
	def __init__( self, *args ):
		"""
		self.str1 = ""
		self.str2 = ""
		self.val1 = 0	# �����ȡʱ��		int( time.time() + self._lostTime )
		self.val2 = 0	# ����ʧ��ʱ��		int( time.time() )

		@param args: ( int )
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ) > 0:
			self.index = args[0]		# index
			self._lostTime = args[1]
		else:
			self.index = -1
			self._lostTime = 0

	def init( self, section ):
		"""
		@param section: format: second
		@type  section: pyDataSection
		"""
		self.index	= section["index"].asInt
		self._lostTime = section["param1"].asInt
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_TIME

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		return ""

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		return	# û����Ҫ�������

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return int( time.time() ) - self.val2 <= 0

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return True

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		t = int( time.time() )
		datas = {"implType" : self.getType(), "str1" : "", "str2" : "", "str3" : "", "val1" : t, "val2" : t + self._lostTime, "index" : self.index, "showOrder" : self.showOrder }
		return QTTask.instance.createObjFromDict( datas )

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		ltime = self.val2 - int( time.time() )
		if ltime < 0:
			ltime = 0
			isCollapsed = True

		HH = ltime/60/60
		MM = ltime/60
		SS = ltime%60

		s = ""
		if HH > 0:
			s += cschannel_msgs.QUEST_INFO_24 % ( HH, MM, SS )
		elif MM > 0:
			s += cschannel_msgs.QUEST_INFO_25 % ( MM, SS )
		else:
			s += cschannel_msgs.QUEST_INFO_26 % SS

		return ( self.getType(), cschannel_msgs.QUEST_INFO_27, s, isCollapsed, False )

	def setFailed( self ):
		"""
		����ʧ��
		"""
		self.val2 = int( time.time() - 10 )
		# �����ȥ��10�룬��Ϊ�ˣ���Ȼ����ʧ�ܣ������õĺ�һ��û�й�ϵ����������
		# �������Ѿ�ʧ���ˣ����ͻ���ȴ����Ϊû��ʧ�ܣ������쳣
		return True

	def collapsedState( self ):
		"""
		��ʱ��ӵķ���
		��Ϊ����������û��ʧ�ܵı�ǣ����Խ�val1��-1��ʾʧ��
		"""
		self.setFailed()

	def isFailed( self, player ) :
		"""
		�����Ƿ��Ѿ�ʧ��
		"""
		return self.val2 - int( time.time() ) < 0

# ------------------------------------------------------------>
# QTTaskKill
# ------------------------------------------------------------>
class QTTaskKill( QTTask.QuestTaskDataType ):
	def __init__( self, *args ):
		"""
		self.str1 = ""	# Ҫɱ����Ŀ��ID��
		self.str2 = ""	# Ҫɱ����Ŀ������
		self.val1 = 0	# ��ǰɱ������
		self.val2 = 0	# Ҫɱ��������

		@param args: ( string, int ) as monsterID, killAmount
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ) > 0:
			self.index = args[0]# index
			self.val2 = args[2]	# Ҫɱ������
			self.str1 = args[1]	# Ҫɱ����Ŀ��
			monster = g_objFactory.getObject( self.str1 )
			if monster is None :						# 2007.12.14: modified by hyw
				self.str2 = cschannel_msgs.QUEST_INFO_28
				ERROR_MSG( "monster lost." )
			else :
				self.str2 = monster.getName()			# Ҫɱ����Ŀ������

	def init( self, section ):
		"""
		@param section: format: monsterID, killAmount
		@type  section: pyDataSection
		"""
		self.index = section["index"].asInt
		self.str1 = section["param1"].asString		# Ҫɱ����Ŀ��
		self.val2 = section["param2"].asInt			# Ҫɱ������
		monster = g_objFactory.getObject( self.str1 )
		if monster is None :
			self.str2 = cschannel_msgs.QUEST_INFO_28
			ERROR_MSG( "monster lost.className: %s "% self.str1 )
		else :
			self.str2 = monster.getName()		# Ҫɱ����Ŀ������
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_KILL

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		return	# û����Ҫ�������

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return True

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		if self.val2 > self.val1:
			self.val1 += quantity
			return True
		return False

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s   %i/%i"
		return msg % ( self.str1 ,self.val1, self.val2 )

	def getKilledName( self ):
		"""
		��ȡ��Ҫɱ���Ĺ��������
		"""
		return self.str1

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		return ( self.getType(), self.str2,
				"%i / %i" % ( min(self.val1, self.val2), self.val2 ),
				isCollapsed,
				self.isCompleted( player )
				)

class QTTaskKills( QTTask.QuestTaskDataType ):
	def __init__( self, *args ):
		"""
		self.str1 = ""	# Ҫɱ����Ŀ��ID��
		self.str2 = ""	# Ҫɱ����Ŀ������
		self.val1 = 0	# ��ǰɱ������
		self.val2 = 0	# Ҫɱ��������

		@param args: ( string, int ) as monsterID, killAmount
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ) > 0:
			self.index = args[0]# index
			self.val2 = args[2]	# Ҫɱ������
			self.str1 = args[1]	# Ҫɱ����Ŀ��
			self.str2 = arg[3]	# ������ܳ�

	def init( self, section ):
		"""
		@param section: format: monsterID, killAmount
		@type  section: pyDataSection
		"""
		self.index = section["index"].asInt
		self.str1 = section["param1"].asString		# Ҫɱ����Ŀ��
		self.val2 = section["param2"].asInt			# Ҫɱ������
		self.str2 = section["param3"].asString	# ������ܳ�
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_KILLS

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		return	# û����Ҫ�������

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return True

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "I do not support this method."

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		if self.val2 > self.val1:
			self.val1 += quantity
			return True
		return False

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,self.val1, self.val2 )

	def getKilledName( self ):
		"""
		��ȡ��Ҫɱ���Ĺ��������
		"""
		return self.str1.split("|")

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		return ( self.getType(), self.str2,
				"%i / %i" % ( min(self.val1, self.val2), self.val2 ),
				isCollapsed,
				self.isCompleted( player )
				)

class QTTaskKillRoleTypeMonster( QTTask.QuestTaskDataType ):

	def __init__( self, *args ):
		QTTask.QuestTaskDataType.__init__( self )
		self._params = {csdefine.CLASS_FIGHTER:[0,0,"",""],			#սʿ
			csdefine.CLASS_SWORDMAN:[0,0,"",""],					#����
			csdefine.CLASS_MAGE:[0,0,"",""],						#��ʦ
			csdefine.CLASS_ARCHER:[0,0,"",""]						#����
			}
		if len( args ) > 0:
			self.index = args[0]# index
			self.val2 = args[2]	# Ҫɱ������
			self.str1 = args[1]	# Ҫɱ����Ŀ��

	def init( self, section ):
		"""
		@param section: format: monsterID, killAmount
		@type  section: pyDataSection
		"""
		self.index = section["index"].asInt
		self.str1 = section["param1"].asString.split("|")		# Ҫɱ����Ŀ��
		self.val2 = section["param2"].asInt						# Ҫɱ������
		i=0
		for type in self._params:
			self.str2 = cschannel_msgs.QUEST_INFO_28
			m_id = self.str1[i]
			monster = g_objFactory.getObject( m_id )
			if monster:
				self.str2 = monster.getName()
			self._params[type] = { "val1":0, "val2":self.val2, "str1":m_id, "str2":self.str2 }
			i = i+1
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_KILL_ROLE_TYPE_MONSTER

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		return	# û����Ҫ�������

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		pass

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return True

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		pass

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self._params[ player.getClass() ].copy()
		datas["implType"] = csdefine.QUEST_OBJECTIVE_KILL
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		pass

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		pass

	def getKilledName( self ):
		"""
		��ȡ��Ҫɱ���Ĺ��������
		"""
		pass

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		pass

class QTTaskKillDart( QTTask.QuestTaskDataType ):

	def __init__( self, *args ):
		"""
		self.str1 = ""	# Ҫɱ����Ŀ��ID��
		self.str2 = ""	# Ҫɱ����Ŀ������
		self.val1 = 0	# ��ǰɱ������
		self.val2 = 0	# Ҫɱ��������

		@param args: ( string, int ) as monsterID, killAmount
		"""
		QTTask.QuestTaskDataType.__init__( self )
		self.str2 = cschannel_msgs.QUEST_INFO_29		# Ҫɱ����Ŀ������
		if len( args ) > 0:
			self.index = args[0]		# task index
			self.str1 = str( args[1] )	# Ҫɱ���ڳ������ھ�����
			self.val2 = args[2]			# Ҫ��ɱ���ڳ�������

	def init( self, section ):
		"""
		@param section: format: monsterID, killAmount
		@type  section: pyDataSection
		"""
		param1 = section["param1"].asInt
		self.index = section["index"].asInt
		self.str1 = str ( param1 )
		self.val2 = section["param2"].asInt
		if param1 == csconst.FACTION_XL:
			self.str2 = cschannel_msgs.QUEST_INFO_49
		else:
			self.str2 = cschannel_msgs.QUEST_INFO_50
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getFaction( self ):
		return int ( self.str1 )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_DART_KILL

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		return	# û����Ҫ�������

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return True

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def add( self, player, dartQuestID, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		if self.val2 > self.val1:
			self.val1 += quantity
			if self.val1 == self.val2:
				dartQuest = player.getQuest( dartQuestID )
				if dartQuest == None:
					# �Ҳ�������IDҪ������ͨ�ڴ������ܸ��ʺ�С����Ҳ����Ҫ��������������
					dartQuest = player.getQuest( 30401001 )
					player.gainMoney( dartQuest.getYaJin() / 2, csdefine.CHANGE_MONEY_QTTASKKILLDART )
				elif dartQuest.isExpensiveDart():
					player.gainMoney( dartQuest.getYaJin() * 2, csdefine.CHANGE_MONEY_QTTASKKILLDART )	# �����ڻ������Ϊ���ڳ�Ѻ���2��
				else:
					player.gainMoney( dartQuest.getYaJin() / 2, csdefine.CHANGE_MONEY_QTTASKKILLDART )	# ��ͨ�ڻ������Ϊ���ڳ�Ѻ���1/2
			return True
		return False

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,self.val1, self.val2 )

	def getKilledName( self ):
		"""
		��ȡ��Ҫɱ���Ĺ��������
		"""
		return self.str1

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		return ( self.getType(), self.str2,
				"%i / %i" % ( min(self.val1, self.val2), self.val2 ),
				isCollapsed,
				self.isCompleted( player )
				)

# ------------------------------------------------------------>
# QTTaskDeliver
# ------------------------------------------------------------>
class QTTaskDeliver( QTTask.QuestTaskDataType ):
	def __init__( self, *args ):
		"""
		self.str1 = ""	# Ҫ�ռ�����Ʒ���
		self.str2 = ""
		self.val1 = 0	# ��ǰ�ռ�����
		self.val2 = 0	# ��Ҫ�ռ�����

		@param args: ( string, int ) as itemID, deliverAmount
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ) >= 2:
			self.index = args[0] 				# index
			self.str1  = args[1].lower()		# itemID
			self.val2  = args[2]				# deliverAmount



	def init( self, section ):
		"""
		@param section: format: itemID, deliverAmount
		@type  section: pyDataSection
		"""
		self.index = section["index"].asInt
		self.str1 = str( section["param1"].asInt )		# itemID
		self.val2 = section["param2"].asInt				# deliverAmount
		self.str2 = section["param3"].asString			# ��¼������Ʒ�Ĺ���ж���Ļ�ֻ��һ����
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_DELIVER

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		playerEntity.removeItemTotal( int( self.str1 ), self.val2, csdefine.DELETE_ITEM_QTTASKDELIVER )

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		# ��������Ʒ���е���Ʒ�����Ƿ�ﵽ�����������
		return player.countItemTotal_( int( self.str1 ) ) >= self.val2

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["val1"] = player.countItemTotal_( int( self.str1 ) )	# current amount
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		self.val1 += quantity
		if self.val1 < 0:
			self.val1 = 0
		return True

	def getDeliverID( self ):
		"""
		"""
		return int( self.str1 )

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s   %i/%i"
		return msg % ( items.instance()[int( self.str1 )]["name"] ,self.val1, self.val2)

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		name = items.instance().id2name( int( self.str1 ) )
		detail2 = "%i / %i" % ( min(player.countItemTotal_( int( self.str1 ) ), self.val2), self.val2 )
		return (self.getType(),
					name,
					detail2,
					isCollapsed,
					player.countItemTotal_( int( self.str1 ) ) >= self.val2
				)

# ------------------------------------------------------------>
# QTTaskDeliverQuality
# ------------------------------------------------------------>
class QTTaskDeliverQuality( QTTaskDeliver ):
	def __init__( self, *args ):
		"""
		self.index = 0	#����Ŀ������
		self.str1 = ""	#����ȼ�
		self.str2 = ""	#��Ʒ����											����:"��Ʒ�� : 1)"
		self.val1 = 0	#���ӵ������
		self.val2 = 0	#��Ҫ�ύ����
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ) > 0:
			self.str1 = args[0]
			self.str2 = args[1]
			self.val1 = args[2]
			self.val2 = args[3]


	def init( self, section ):
		"""
		@param section: format: itemID, deliverAmount
		@type  section: pyDataSection
		"""
		self.index 	= section["index"].asInt
		self.str1 	= str(section["param1"].asInt)
		self.str2 	= section["param2"].asString
		self.val2 	= section["param3"].asInt
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_DELIVER_QUALITY

	def complete( self, player ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		amount = 0
		for i in xrange( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT + 1 ):
			if player.kitbags.has_key( i ):
				for e in player.getItems( i ):
					if e is not None and self.isFitProperty( e ):
						amount += e.amount
						player.removeItem_( e.order, e.amount, csdefine.DELETE_ITEM_QTTASKDELIVER )
						if amount >= self.val2:
							return

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		# ��������Ʒ���е���Ʒ�����Ƿ�ﵽ�����������
		return self.isCompleted( player )

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		amount = 0
		for i in xrange( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT + 1 ):
			if player.kitbags.has_key( i ):
				for e in player.getItems( i ):
					if e is not None and self.isFitProperty( e ):
						amount += e.amount
		datas["val1"] = amount
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		self.val1 += quantity
		if self.val1 < 0:
			self.val1 = 0
		return True

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s   %i/%i"
		return msg % ( self.getPorpertyName(),self.val1, self.val2)

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		name = self.getPorpertyName()
		amount = 0
		for i in xrange( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT + 1 ):
			if player.kitbags.has_key( i ):
				for e in player.getItems( i ):
					if e is not None and self.isFitProperty( e ):
						amount += e.amount

		detail2 = "%i / %i" % ( min(amount, self.val2), self.val2 )
		return (self.getType(),
					name,
					detail2,
					isCollapsed,
					amount >= self.val2
				)

	def isFitProperty( self, item ):
		"""
		"""
		return item.isEquip() and item.getType() != ItemTypeEnum.ITEM_SYSTEM_KASTONE and item.getQuality() == self.getPorpertyValue() and item.query( "reqLevel", 0 ) + 10 >= int(self.str1)

	def getPorpertyValue( self ):
		"""
		ȡ����Ҫ������ֵ
		"""
		return int(eval( self.str2 )[1])

	def getPorpertyName( self ):
		"""
		ȡ����Ҫ������
		"""
		return eval( self.str2 )[0]

# ------------------------------------------------------------>
# QTTaskEventUseItem
# ------------------------------------------------------------>
class QTTaskEventItemUsed( QTTask.QuestTaskDataType ):
	"""
	����Ŀ�꣺��Ʒʹ���¼�������ĳ��ʹ��һ����Ʒ��ʹ�ú��Ŀ�꼴��ɣ�
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""	# Ҫʹ�õ���Ʒ���
		self.str2 = ""	# ����Ŀ������
		self.val1 = 0	# ��ǰʹ������
		self.val2 = 0	# ��Ҫʹ������

		@param args: ( string, int, string ) as itemID, useAmount, describe
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ):
			self.index = args[0]	# index
			self.str1 = args[1]		# itemID
			self.str2 = args[3]		# describe
			self.val2 = args[2]		# useAmount

	def init( self, section ):
		"""
		@param section: format: itemID, amount, describe
		@type  section: pyDataSection
		���ã�
			param1: itemID
			param2: amount
			param3: describe
		"""
		self.index = section["index"].asInt
		self.str1 = section["param1"].asString		# itemID
		self.val2 = section["param2"].asInt			# section["param2"].asInt			# useAmount
		self.str2 = section["param3"].asString		# describe
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_EVENT_USE_ITEM

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		pass

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return True

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		self.val1 += quantity
		return True

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,self.val1, self.val2)

	def getItemID( self ):
		"""
		��ȡʹ����Ʒ��ID
		"""
		return int( self.str1 )

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		if self.val2 <= 1 :
			detail2 = ""
		else:
			detail2 = "%i / %i" % ( min(self.val1, self.val2), self.val2 )
		return (self.getType(),
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted( player )
				)


# ------------------------------------------------------------>
# QTTaskSkillLearned
# ------------------------------------------------------------>
class QTTaskSkillLearned( QTTask.QuestTaskDataType ):
	"""
	����Ŀ�꣺����ѧϰ������ѧ����ĳһ������֮�󣬼����Ŀ�꣩
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""	# skillID_1
		self.str2 = ""	# ����Ŀ������
		self.val1 = 0
		self.val2 = 0

		@param args: ( string, int, string ) as itemID, useAmount, describe
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ):
			self.index = args[0]	# index
			self.str1 = args[1]		# skillID
			self.str2 = args[3]
			self.val2 = args[2]

	def init( self, section ):
		"""
		@param section: format: itemID, amount, describe
		@type  section: pyDataSection
		"""
		self.index = section["index"].asInt
		self.str2 = section["param1"].asString		# describe
		self.str1 = str( section["param2"].asInt )	# skillID_1
		self.val1 = 0
		self.val2 = section["param3"].asInt
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SKILL_LEARNED

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		pass

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����
		"""
		return self.val1

	def isCompletedForNoStart( self, player ):
		"""
		"""
		return True

	def increaseState( self ):
		"""
		virtual methed.
		"""
		assert "im not support this method."

	def add( self, player, skillID ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		if skillID == int( self.str1 ):
			self.val1 = True
			return True
		return False

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		datas["val1"] = player.hasSkill( int( self.str1 ) )
		return QTTask.instance.createObjFromDict( datas )

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		learnedStr = "0/1"
		if self.val1:
			learnedStr = "1/1"
		msg = "%s   %s"
		return msg % ( self.str2 ,learnedStr )

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		detail2 = "0/1"
		if self.isCompleted( player ):
			detail2 = "1/1"
		return (self.getType(),
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted( player )
				)


# ------------------------------------------------------------>
# QTTaskLivingSkillLearned
# ------------------------------------------------------------>
class QTTaskLivingSkillLearned( QTTask.QuestTaskDataType ):
	"""
	����Ŀ�꣺����ѧϰ������ѧ����ĳһ������֮�󣬼����Ŀ�꣩
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""	# living skill id
		self.str2 = ""	# ����Ŀ������
		self.val1 = 0   # need living skill level

		@param args: ( string, int, string ) as itemID, useAmount, describe
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ):
			self.index = args[0]	# index
			self.str1 = args[1]		# ID:Level
			self.str2 = args[2]
			self.val1 = args[3]
			self.val2 = None

			self.__initSkillInfo()

	def __initSkillInfo(self):
		self.__skillInfo = tuple( [ int(i) for i in self.str1.split(":") ] )

	def init( self, section ):
		"""
		@param section: format: itemID, amount, describe
		@type  section: pyDataSection
		"""
		self.index = section["index"].asInt
		self.str2 = section["param1"].asString		# describe
		self.str1 = str( section["param2"].asString )	# ID:Level
		self.val2 = section["param3"].asInt 		# npc link
		self.__initSkillInfo()
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_LIVING_SKILL_LEARNED

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		pass

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����
		"""
		if not hasattr(self, "__skillInfo"):
			if len(self.str1) != 0 :
				self.__initSkillInfo()
			else:
				return False

		pLivingSkillLevel = player.getSkillLevel( self.__skillInfo[0] )
		if pLivingSkillLevel >= self.__skillInfo[1]:
			self.val1 = True
		else:
			self.val1 = False

		return self.val1

	def isCompletedForNoStart( self, player ):
		"""
		"""
		return True

	def increaseState( self ):
		"""
		virtual methed.
		"""
		assert "im not support this method."

	def add( self, player, skillID ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		if skillID == self.__skillInfo[0]:
			pLivingSkillLevel = player.getSkillLevel( self.__skillInfo[0] )
			if pLivingSkillLevel >= self.__skillInfo[1]:
				self.val1 = True
				return True
		return False

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		datas["val1"] = self.isCompleted(player)
		return QTTask.instance.createObjFromDict( datas )

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		learnedStr = "0/1"
		if self.val1:
			learnedStr = "1/1"
		msg = "%s   %s"
		return msg % ( self.str2 ,learnedStr )

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		detail2 = "0/1"
		if self.isCompleted( player ):
			detail2 = "1/1"
		return (self.getType(),
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted( player )
				)

# ------------------------------------------------------------>
# QTTaskEventTrigger
# ------------------------------------------------------------>
class QTTaskEventTrigger( QTTask.QuestTaskDataType ):
	"""
	����Ŀ�꣺�¼���������ĳ���ط�����ĳ������ ��:������� ���¼����1��
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""	# Ҫʹ�õ���Ʒ���
		self.str2 = ""	# ����Ŀ������
		self.val1 = 0	# ��ǰ���״̬����
		self.val2 = 0	# ��Ҫ���״̬����

		@param args: ( string, int, string ) as itemID, useAmount, describe
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ):
			self.index = args[0]	# index
			self.str2 = args[1]		# describe
			self.val2 = args[2]		# total complete of amount

	def init( self, section ):
		"""
		@param section: format: itemID, amount, describe
		@type  section: pyDataSection
		"""
		self.index = section["index"].asInt
		self.val2 = section["param2"].asInt			# total complete of amount
		self.str2 = section["param1"].asString		# describe
		self.str1 = section["param3"].asString		# ��¼Ŀ�곡����Ʒ�ı��
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_EVENT_TRIGGER

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		pass

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return True

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		self.val1 += 1

	def decreaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ���������״̬
		"""
		if self.val1 > 0:
			self.val1 = 0

	def collapsedState( self ):
		"""
		��ʱ��ӵķ���
		��Ϊ����������û��ʧ�ܵı�ǣ����Խ�val1��-1��ʾʧ��
		"""
		# ֻ��û����ɵ����������ʧ�ܴ����˾�һ������ɾ��(qilan)
		if self.val1 < self.val2:
			self.val1 = -1

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		self.val1 += quantity
		return True

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,self.val1, self.val2)

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		if self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i / %i" % ( min(self.val1, self.val2), self.val2 )
		return (self.getType(),
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted( player )
				)
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
		if len( args ) >= 2:
			self.val2 = args[2]				# amount
			self.index = args[0] 			# index

	def init( self, section ):
		"""
		@param section: format: petID, amount
		@type  section: pyDataSection
		"""
		self.index = section["index"].asInt
		self.val2 = section["param1"].asInt		# amount
		self.str1 = section["param2"].asString		# ��Ӧ������
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_OWN_PET

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		pass

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		# �������Ƿ�ӵ���㹻�ĳ�������
		return player.pcg_getPetCount() >= self.val2

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["val1"] = player.pcg_getPetCount()	# current amount
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		self.val1 += quantity
		return True

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = cschannel_msgs.QUEST_INFO_30
		return msg % ( self.val1, self.val2 )

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		detail2 = "%i / %i" % ( min(self.val1, self.val2), self.val2 )#
		return (self.getType(),
					cschannel_msgs.QUEST_INFO_31,
					detail2,
					isCollapsed,
					self.isCompleted( player )
				)



class QTTaskSubmit( QTTask.QuestTaskDataType ):
	"""
	�̳��� QTTaskDeliver��
	�ύ����Ŀ��
	"""
	def __init__( self, *args ):
		"""
		self.index = 0	#����Ŀ������
		self.str1 = ""	#��ƷID
		self.str2 = ""	#��Ʒ����											����:"��Ʒ�� : 1)"
		self.val1 = 0	#���ӵ������
		self.val2 = 0	#��Ҫ�ύ����
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ) > 0:
			self.str1 = args[0]
			self.str2 = args[1]
			self.val1 = args[2]
			self.val2 = args[3]

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT


	def complete( self, playerEntity ):
		"""
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		#kitTote = playerEntity.queryTemp( "questKitTote", None )
		order = playerEntity.queryTemp( "questOrder", -1 )
		item = playerEntity.getItem_( order )
		if item == None and item.getAmount() < self.val2:
			return
		playerEntity.removeItem_( order, self.val2, csdefine.DELETE_ITEM_COMPLETEQTTASKSUBMIT )

	def isFitProperty( self, item ):
		"""
		�Ƿ��Ƿ��ϵ���Ʒ
		"""
		return True
		#return item.id == int( self.str1 ) and item.query(self.getPorpertyName(), -1) == self.getPorpertyValue()


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


	def isCompleted( self, playerEntity ):
		"""
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		kitTote = playerEntity.queryTemp( "questKitTote", None )
		order = playerEntity.queryTemp( "questOrder", None )

		if kitTote == None and order == None:
			return self.val2 <= self.val1
		else:
			item = playerEntity.getItem_( order )
			if item is None:
				ERROR_MSG( "%s: the position in the item blacket is empty!" % (playerEntity.getName()) )
				playerEntity.statusMessage( csstatus.ROLE_QUEST_SUBMIT_NO_ITEM )
				return False
			if self.isFitProperty( item ):
				return True
			playerEntity.statusMessage( csstatus.ROLE_QUEST_SUBMIT_WRONG_TYPE )
			return False

	def isCompletedForNoStart( self, playerEntity ):
		"""
		"""
		self.isCompleted( playerEntity )

	def init( self, section ):
		"""
		@param section: format: itemID, deliverAmount
		@type  section: pyDataSection
		"""
		self.index 	= section["index"].asInt
		self.str1 	= str(section["param1"].asInt)
		self.str2 	= section["param2"].asString
		self.val2 	= section["param3"].asInt
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def newTaskBegin( self, player, tasks ):
		"""
		"""
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		amount = 0
		for i in xrange( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT ):
			if player.kitbags.has_key( i ):
				for e in player.getItems( i ):
					if e is not None and self.isFitProperty( e ):
						amount += e.amount
		datas["val1"] = amount
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		self.val1 += quantity
		return True

	def getDeliverID( self ):
		"""
		"""
		return int( self.str1 )

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s %s: %i   %i/%i"
		name = self.getPorpertyName()
		value = self.getPorpertyValue()
		return msg % ( items.instance()[int(self.str1)]["name"], name, value, self.val1, self.val2)

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		name = items.instance().id2name( int( self.str1 ) ) + self.getExtraDescription()
		amount = 0
		for i in xrange( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT + 1 ):
			if player.kitbags.has_key( i ):
				for e in player.getItems( i ):
					if e is not None and self.isFitProperty( e ):
						amount += e.amount

		detail2 = "%i / %i" % ( min(amount, self.val2), self.val2 )
		return (self.getType(),
					name,
					detail2,
					isCollapsed,
					amount >= self.val2
				)

	def getSubmitInfo( self ):
		"""
		"""
		item = items.instance().createDynamicItem( int( self.str1 ) )
		return {"ItemName":item.name(), self.getPorpertyName(): self.getPorpertyValue() , "count": self.val2}

	def getSubmitID( self ):
		"""
		"""
		return int(self.str1)

	def setPlayerTemp( self, player, codeStr ):
		"""
		"""
		player.setTemp( "questKitTote", int(self.getKeyValue( codeStr, "questKitTote")) )
		player.setTemp( "questOrder", int( self.getKeyValue( codeStr, "questOrder") ) )

	def removePlayerTemp( self, player ):
		"""
		"""
		player.removeTemp( "questKitTote" )
		player.removeTemp( "questOrder" )


	def getExtraDescription( self ):
		"""
		"""
		return 	self.getPorpertyName()
# ------------------------------------------------------------>
# QTTaskTeam
# ------------------------------------------------------------>
class QTTaskTeam( QTTask.QuestTaskDataType ):
	def __init__( self, *args ):
		"""
		self.str1 = ""		#����ְҵ
		self.str2 = ""
		self.val1 = 0		#��ְҵ��������
		self.val2 = 0		#��ְҵ������������
		"""
		QTTask.QuestTaskDataType.__init__( self )


	def init( self, section ):
		"""
		@param section: format: second
		@type  section: pyDataSection
		"""
		self.index	= section["index"].asInt
		self.str1 = section["param1"].asString				# ���ѵ�Occupation (ְҵ��
		self.val2 = section["param2"].asInt					# ��������
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_TEAM


	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		return	# û����Ҫ�������

	def isCompleted( self, playerEntity ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		if playerEntity.queryTemp( "questTeam", None ):
			if playerEntity.countTeamOccupationNear( int( self.str1 ) << 4 ) < self.val2: #����������ְҵ�Ķ���
				playerEntity.statusMessage( csstatus.ROLE_QUEST_TEAM_NOT_ENOUGH )
				return False
			else:
				return True

		return self.val1 >= self.val2

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return player.countTeamOccupationNear( self.str1 ) >= self.val2

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."


	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		self.val1 += quantity
		return True

	def getOccupation( self ):
		"""
		"""
		return int( self.str1 ) << 4

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "'%s'   %i/%i"
		return msg % ( csconst.g_chs_class[ int( self.str1 ) << 4 ], self.val1, self.val2)


	def clear( self, player):
		"""
		�����ɢ����ӵ���
		"""
		self.val1 = 0


	def getDetail( self, player ):
		"""
		ȡ���������
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		detail2 = "%i / %i" % ( min(self.val1, self.val2), self.val2 )
		return (self.getType(),
					csconst.g_chs_class[ int( self.str1 ) << 4 ],
					detail2,
					isCollapsed,
					self.val1 >= self.val2
				)



# ------------------------------------------------------------>
# QTTaskLevel
# ------------------------------------------------------------>
class QTTaskLevel( QTTask.QuestTaskDataType ):
	def __init__( self, *args ):
		"""
		self.str1 = ""	# Ҫ�ﵽ�ĵȼ�����
		self.val1 = 0	# ��ҵ�ǰ�ȼ���ֵ
		self.val2 = 0	# Ҫ�ﵽ�ĵȼ���ֵ
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ) > 0:
			self.index = args[0]# index
			self.str1 = args[1]	# Ҫ�ﵽ�ĵȼ�����
			self.val2 = args[2]	# Ҫ�ﵽ�ĵȼ���ֵ

	def init( self, section ):
		"""
		"""
		self.index = section["index"].asInt
		self.str1 = section["param1"].asString
		self.val2 = section["param2"].asInt
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_LEVEL

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		return	# û����Ҫ�������

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= player.level

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return True

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def setLevel( self, level ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		self.val1 = level
		if self.val1 >= self.val2:
			return True
		return False

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s   %i/%i"
		return msg % ( self.str1 ,self.val1, self.val2 )


	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		return ( self.getType(), self.str1,
				cschannel_msgs.QUEST_INFO_32 % player.level,
				isCollapsed,
				self.isCompleted( player )
				)



# ------------------------------------------------------------>
# QTTaskQuestNormal
# ------------------------------------------------------------>
class QTTaskQuestNormal( QTTask.QuestTaskDataType ):
	def __init__( self, *args ):
		"""
		self.str1 = ""	# ����
		self.val1 = 0	# ����ID
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ) > 0:
			self.index = args[0]# index
			self.str1 = args[1]	# ����
			self.val1 = args[2]	# ����ID

	def init( self, section ):
		"""
		param1: describe
		param2: questID
		"""
		self.index = section["index"].asInt
		self.str1 = section["param1"].asString
		self.val1 = section["param2"].asInt
		self.val2 = 0
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_QUEST_NORMAL

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		return

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return True

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s"
		return msg % ( self.str1 )


	def setQuestFinish( self, questID ):
		"""
		"""
		if questID == self.val1:
			self.val2 = 1
			return True
		return False

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		return ( self.getType(), self.str1,
				"",
				isCollapsed,
				self.isCompleted( player )
				)


# ------------------------------------------------------------>
# QTTaskQuest
# ------------------------------------------------------------>
class QTTaskQuest( QTTaskQuestNormal ):
	def __init__( self, *args ):
		"""
		self.str1 = ""	# ����
		self.val1 = 0	# ����ID
		"""
		QTTaskQuestNormal.__init__( self, *args )

	def init( self, section ):
		"""
		"""
		QTTaskQuestNormal.init( self, section )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_QUEST

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		playerEntity.questsLog.remove( self.val1 )
		return



class QTTaskSubmitPicture( QTTaskDeliver ):
	"""
	�̳��� QTTaskDeliver��
	�ύ����Ŀ��
	"""
	def __init__( self, *args ):
		"""
		self.index = 0	#����Ŀ������
		self.str1 = ""	#��ƷID
		self.str2 = ""	#NPC calssName
		self.val1 = 0	#���ӵ������
		self.val2 = 0	#��Ҫ�ύ����
		"""
		QTTask.QuestTaskDataType.__init__( self )

		if len( args ) >=2:
			self.index = args[0]
			self.str1  = args[1]
			self.str2  = args[2]
			self.val2  = args[3]


	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_PICTURE


	def complete( self, playerEntity ):
		"""
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		#kitTote = playerEntity.queryTemp( "questKitTote", None )
		order = playerEntity.queryTemp( "questOrder", None )
		item = playerEntity.getItem_( order )
		if item == None and item.getAmount() < self.val2:
			return
		playerEntity.removeItem_( order, self.val2, csdefine.DELETE_ITEM_COMPLETESUBMITPICTURE )


	def isCompleted( self, playerEntity ):
		"""
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		kitTote = playerEntity.queryTemp( "questKitTote", None )
		order = playerEntity.queryTemp( "questOrder", None )

		if kitTote == None and order == None:
			return QTTaskDeliver.isCompleted( self, playerEntity )
		else:
			item = playerEntity.getItem_( order )
			if item is None:
				playerEntity.statusMessage( csstatus.ROLE_QUEST_SUBMIT_NO_ITEM )
				ERROR_MSG( "%s: the position in the item blacket is empty!" % (playerEntity.getName()) )
				return False

			if int( self.str1 ) == item.id and self.val2 <= item.amount:
				if item.query("pictureTargetID", "" ) == self.str2:
					return True
			playerEntity.statusMessage( csstatus.ROLE_QUEST_SUBMIT_WRONG_TYPE )
			return False

	def isCompletedForNoStart( self, playerEntity ):
		"""
		"""
		self.isCompleted( playerEntity )

	def init( self, section ):
		"""
		@param section: format: itemID, deliverAmount
		@type  section: pyDataSection
		"""
		self.index = section["index"].asInt
		self.str1 = str( section["param1"].asInt )	# itemID
		self.str2 = section["param2"].asString	# #NPC calssName
		self.val2 = section["param3"].asInt		# deliverAmount
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def newTaskBegin( self, player, tasks ):
		"""
		"""
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		amount = 0
		for i in xrange( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT ):
			if player.kitbags.has_key( i ):
				for e in player.getItems( i ):
					if e is not None and e.id == int( self.str1 ):
						if e.query("pictureTargetID", "" ) == self.str2:
							amount += e.amount
		datas["val1"] = amount
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."

	def add( self, player, quantity ):
		"""
		"""
		return QTTaskDeliver.add( self, player, quantity )

	def getDeliverID( self ):
		"""
		"""
		return QTTaskDeliver.getDeliverID( self )

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s %s   %i/%i"
		return msg % ( items.instance()[int( self.str1 )]["name"], g_objFactory.getObject(self.str2).getName(), cschannel_msgs.QUEST_INFO_33, self.val1, self.val2 )

	def getNPCClassName( self ):
		"""
		@return: �����������Ʒ����
		@param:  INT32
		"""
		return self.str2

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		name = g_objFactory.getObject(self.str2).getName() + cschannel_msgs.QUEST_INFO_34
		amount = 0
		for i in xrange( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT ):
			if player.kitbags.has_key( i ):
				for e in player.getItems( i ):
					if e is not None and e.id == int( self.str1 ):
						if e.query("pictureTargetID", "" ) == self.str2:
							amount += e.amount

		detail2 = "%i / %i" % ( min(amount, self.val2), self.val2 )
		return (self.getType(),
					name,
					detail2,
					isCollapsed,
					amount >= self.val2
				)

	def getSubmitInfo( self ):
		"""
		"""
		name = g_objFactory.getObject(self.str2).getName()
		return {"ItemName":cschannel_msgs.QUEST_INFO_35,"npcName":'('+name+')', "count": self.val2}


	def setPlayerTemp( self, player, codeStr ):
		"""
		"""
		player.setTemp( "questKitTote", int(self.getKeyValue( codeStr,"questKitTote")) )
		player.setTemp( "questOrder", int( self.getKeyValue(codeStr, "questOrder") ) )

	def removePlayerTemp( self, player ):
		"""
		"""
		player.removeTemp( "questKitTote" )
		player.removeTemp( "questOrder" )


class QTTaskSubmitChangeBody( QTTaskSubmitPicture ):
	"""
	�̳��� QTTaskDeliver��
	�ύ����Ŀ��
	"""
	def __init__( self, *args ):
		"""
		self.index = 0	#����Ŀ������
		self.str1 = ""	#��ƷID
		self.str2 = ""	#NPC calssName
		self.val1 = 0	#���ӵ������
		self.val2 = 0	#��Ҫ�ύ����
		"""
		QTTaskSubmitPicture.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_CHANGE_BODY

	def isCompleted( self, playerEntity ):
		"""
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		kitTote = playerEntity.queryTemp( "questKitTote", None )
		order = playerEntity.queryTemp( "questOrder", None )

		if kitTote == None and order == None:
			return QTTaskDeliver.isCompleted( self, playerEntity )
		else:
			item = playerEntity.getItem_( order )
			if item is None:
				playerEntity.statusMessage( csstatus.ROLE_QUEST_SUBMIT_NO_ITEM )
				ERROR_MSG( "%s: the position in the item blacket is empty!" % (playerEntity.getName()) )
				return False

			if int( self.str1 ) == item.id and self.val2 <= item.amount:
				if item.query("changeBodyTargetID", "" ) == self.str2:
					return True
			playerEntity.statusMessage( csstatus.ROLE_QUEST_SUBMIT_WRONG_TYPE )
			return False

	def newTaskBegin( self, player, tasks ):
		"""
		"""
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		amount = 0
		for i in xrange( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT ):
			if player.kitbags.has_key( i ):
				for e in player.getItems( i ):
					if e is not None and e.id == int( self.str1 ):
						if e.query("changeBodyTargetID", "" ) == self.str2:
							amount += e.amount
		datas["val1"] = amount
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s %s   %i/%i"
		return msg % ( items.instance()[int( self.str1 )]["name"], g_objFactory.getObject(self.str2).getName(), cschannel_msgs.QUEST_INFO_36, self.val1, self.val2 )

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		name = g_objFactory.getObject(self.str2).getName() + cschannel_msgs.QUEST_INFO_37
		amount = 0
		for i in xrange( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT ):
			if player.kitbags.has_key( i ):
				for e in player.getItems( i ):
					if e is not None and e.id == int( self.str1 ):
						if e.query("changeBodyTargetID", "" ) == self.str2:
							amount += e.amount

		detail2 = "%i / %i" % ( min(amount, self.val2), self.val2 )
		return (self.getType(),
					name,
					detail2,
					isCollapsed,
					amount >= self.val2
				)

	def getSubmitInfo( self ):
		"""
		"""
		name = g_objFactory.getObject(self.str2).getName()
		return {"ItemName":cschannel_msgs.QUEST_INFO_38,"npcName":'('+name+')', "count": self.val2}

class QTTaskSubmitDance( QTTaskSubmitPicture ):
	"""
	�̳��� QTTaskDeliver��
	�ύ����Ŀ��
	"""
	def __init__( self, *args ):
		"""
		self.index = 0	#����Ŀ������
		self.str1 = ""	#��ƷID
		self.str2 = ""	#NPC calssName
		self.val1 = 0	#���ӵ������
		self.val2 = 0	#��Ҫ�ύ����
		"""
		QTTaskSubmitPicture.__init__( self )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_DANCE

	def isCompleted( self, playerEntity ):
		"""
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		kitTote = playerEntity.queryTemp( "questKitTote", None )
		order = playerEntity.queryTemp( "questOrder", None )

		if kitTote == None and order == None:
			return QTTaskDeliver.isCompleted( self, playerEntity )
		else:
			item = playerEntity.getItem_( order )
			if item is None:
				playerEntity.statusMessage( csstatus.ROLE_QUEST_SUBMIT_NO_ITEM )
				ERROR_MSG( "%s: the position in the item blacket is empty!" % (playerEntity.getName()) )
				return False

			if int( self.str1 ) == item.id and self.val2 <= item.amount:
				if item.query("danceTargetID", "" ) == self.str2:
					return True
			playerEntity.statusMessage( csstatus.ROLE_QUEST_SUBMIT_WRONG_TYPE )
			return False

	def newTaskBegin( self, player, tasks ):
		"""
		"""
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		amount = 0
		for i in xrange( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT ):
			if player.kitbags.has_key( i ):
				for e in player.getItems( i ):
					if e is not None and e.id == int( self.str1 ):
						if e.query("danceTargetID", "" ) == self.str2:
							amount += e.amount
		datas["val1"] = amount
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s %s   %i/%i"
		return msg % ( items.instance()[int( self.str1 )]["name"], g_objFactory.getObject(self.str2).getName(), cschannel_msgs.QUEST_INFO_39, self.val1, self.val2 )

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		name = g_objFactory.getObject(self.str2).getName() + cschannel_msgs.QUEST_INFO_40
		amount = 0
		for i in xrange( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT ):
			if player.kitbags.has_key( i ):
				for e in player.getItems( i ):
					if e is not None and e.id == int( self.str1 ):
						if e.query("danceTargetID", "" ) == self.str2:
							amount += e.amount

		detail2 = "%i / %i" % ( min(amount, self.val2), self.val2 )
		return (self.getType(),
					name,
					detail2,
					isCollapsed,
					amount >= self.val2
				)

	def getSubmitInfo( self ):
		"""
		"""
		name = g_objFactory.getObject(self.str2).getName()
		return {"ItemName":cschannel_msgs.QUEST_INFO_41,"npcName":'('+name+')', "count": self.val2}


class QTTaskDeliverPet( QTTaskDeliver ):
	def __init__( self, *args ):
		"""
		self.str1 = ""	# Ҫ�ռ��ĳ�����
		self.str2 = ""  # Ҫ�ռ��ĳ�������
		self.val1 = 0	# ��ǰ�ռ�����
		self.val2 = 0	# ��Ҫ�ռ�����

		@param args: ( string, int ) as itemID, deliverAmount
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ) >= 2:
			self.index = args[0] 			# index
			self.str1  = args[1].lower()		# ����ID
			self.str1  = args[2]				# name
			self.val2  = args[3]				# deliverAmount



	def init( self, section ):
		"""
		@param section: format: itemID, deliverAmount
		@type  section: pyDataSection
		"""
		self.index = section["index"].asInt
		self.str1 = section["param1"].asString	# ����ID
		self.str2 = section["param2"].asString	# ��������
		self.val2 = section["param3"].asInt		# deliverAmount
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_DELIVER_PET

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĳ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		for i in xrange(self.val2):
			playerEntity.base.pcg_freePet( playerEntity.queryTemp( "pet%iDBID"%i ) )

	def isCompleted( self, playerEntity ):
		"""
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		for i in xrange(self.val2):
			if playerEntity.queryTemp( "pet%iDBID"%i, None ) == None:
				return QTTaskDeliver.isCompleted( self, playerEntity )
			else:
				break
		#�ж���������Ƿ��ս
		petsID = [ pet.databaseID for pet in playerEntity.pcg_petDict.getDict().itervalues() if pet.mapMonster == self.str1 ]
		if len(petsID) < self.val2:return False
		if len(petsID) == self.val2:
			if playerEntity.pcg_actPetDBID in petsID:
				playerEntity.statusMessage( csstatus.ROLE_QUEST_PET_HAS_ACTIVE )
				return False
		#-----------------
		for i in xrange(self.val2):
			if not playerEntity.queryTemp( "pet%iDBID"%i ) in playerEntity.questsTable[playerEntity.queryTemp('completedQuestID')].query( "petDBIDs", [] ):
				playerEntity.statusMessage( csstatus.ROLE_QUEST_SUBMIT_WRONG_PET )
				return False

		return QTTaskDeliver.isCompleted( self, playerEntity )

	def isCompletedForNoStart( self, playerEntity ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		# ��������Ʒ���е���Ʒ�����Ƿ�ﵽ�����������
		assert "QTTaskDeliverPet not support this NoStart Quest."
		return False

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		amount = 0
		tasks.set( "petDBIDs", [] )
		for i in player.pcg_petDict.getDict().itervalues():
			if i.mapMonster == self.str1:
				amount += 1
				tasks.query( "petDBIDs", [] ).append( i.databaseID )

		datas["val1"] = amount
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def addPet( self, player, questID, petDBID ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		if petDBID in player.questsTable[questID].query( "petDBIDs", [] ):
			return False
		else:
			player.questsTable[questID].query( "petDBIDs", [] ).append( petDBID )
			self.val1 += 1
			return True

	def subPet( self, player, questID, petDBID ):
		"""
		"""
		if self.val1 == -1:
			return False
		self.val1 -= 1
		if self.val1 < 0:
			self.val1 = 0
		if petDBID in player.questsTable[questID].query( "petDBIDs", [] ):
			player.questsTable[questID].query( "petDBIDs", [] ).remove( petDBID )
		return True

	def getDeliverPetID( self ):
		"""
		"""
		return self.str1

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = cschannel_msgs.QUEST_INFO_42
		return msg % ( self.str2 ,self.val1, self.val2)

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		detail2 = "%i / %i" % ( min( self.val1, self.val2), self.val2 )
		return (self.getType(),
					self.str2,
					detail2,
					isCollapsed,
					self.val1 >= self.val2
				)


	def setPlayerTemp( self, player, codeStr ):
		"""
		"""
		for i in xrange( self.val2 ):
			if self.getKeyValue( codeStr, "pet%iDBID"%i) == "":
				player.setTemp( "pet%iDBID"%i, 0 )
			else:
				player.setTemp( "pet%iDBID"%i, int( self.getKeyValue( codeStr, "pet%iDBID"%i) ) )


	def removePlayerTemp( self, player ):
		"""
		"""
		for i in xrange( self.val2 ):
			player.removeTemp( "pet%iDBID"%i )


class QTTaskSubmit_Quality( QTTaskSubmit ):
	"""
	�ύ����Ʒ����Ʒ
	"""
	def __init__( self, *args ):
		QTTaskSubmit.__init__( self, *args )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_QUALITY

	def isFitProperty( self, item ):
		"""
		"""
		return item.id == int( self.str1 ) and item.getQuality() == self.getPorpertyValue()


class QTTaskSubmit_Slot( QTTaskSubmit ):
	"""
	�ύ���ʿ�����Ʒ
	"""
	def __init__( self, *args ):
		QTTaskSubmit.__init__( self, *args )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_SLOT

	def isFitProperty( self, item ):
		"""
		"""
		return item.id == int( self.str1 ) and item.getLimitSlot() == self.getPorpertyValue()


class QTTaskSubmit_Effect( QTTaskSubmit ):
	"""
	�ύ��Ƕ��Ʒ
	"""
	def __init__( self, *args ):
		QTTaskSubmit.__init__( self, *args )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_EFFECT

	def isFitProperty( self, item ):
		"""
		"""
		return item.id == int( self.str1 ) and len( item.getBjExtraEffect() ) != 0

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s %s:  %i/%i"
		name = self.getPorpertyName()
		#value = self.getPorpertyValue()
		return msg % ( items.instance()[int(self.str1)]["name"], name, self.val1, self.val2)


class QTTaskSubmit_Level( QTTaskSubmit ):
	"""
	�ύǿ���ȼ�
	"""
	def __init__( self, *args ):
		QTTaskSubmit.__init__( self, *args )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_LEVEL


	def isFitProperty( self, item ):
		"""
		"""
		return item.id == int( self.str1 ) and item.getIntensifyLevel() >= self.getPorpertyValue()

class QTTaskSubmit_Binded( QTTaskSubmit ):
	"""
	�ύ���ʰ���Ʒ
	"""
	def __init__( self, *args ):
		QTTaskSubmit.__init__( self, *args )


	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_BINDED


	def isFitProperty( self, item ):
		"""
		"""
		return item.id == int( self.str1 ) and item.isObey()

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s %s:   %i/%i"
		name = self.getPorpertyName()
		#value = self.getPorpertyValue()
		return msg % ( items.instance()[int(self.str1)]["name"], name, self.val1, self.val2)

class QTTaskSubmit_Empty( QTTaskSubmit ):
	"""
	�ύ�������Կ�λ��Ʒ
	"""
	def __init__( self, *args ):
		QTTaskSubmit.__init__( self, *args )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_EMPTY

	def isFitProperty( self, item ):
		"""
		"""
		emptyCount = -1
		if hasattr( item, "getCreateEffect" ):
			emptyCount = 0
			createEffect = item.getCreateEffect()
			for effect in createEffect:
				if effect == ( 0, 0 ):
					emptyCount += 1
		return item.id == int( self.str1 ) and emptyCount == self.getPorpertyValue()

class QTTaskNotSubmit_Empty( QTTaskSubmit_Empty ):
	"""
	�����Ƿ��к������Կ�λ��Ʒ�������ύ
	"""
	def __init__( self, *args ):
		QTTaskSubmit_Empty.__init__( self, *args )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_NOT_SUBMIT_EMPTY

	def complete( self, playerEntity ):
		"""
		"""
		pass

	def getSubmitInfo( self ):
		"""
		"""
		return {}

	def setPlayerTemp( self, player, codeStr ):
		"""
		"""
		pass

	def removePlayerTemp( self, player ):
		"""
		"""
		pass

	def isCompleted( self, playerEntity ):
		"""
		"""
		amount = 0
		for i in xrange( csdefine.KB_COMMON_ID, csdefine.KB_COMMON_ID + csdefine.KB_COUNT ):
			if playerEntity.kitbags.has_key( i ):
				for e in playerEntity.getItems( i ):
					if e is not None and self.isFitProperty( e ):
						amount += e.amount
		if amount >= self.val2:
			return True
		return False

class QTTaskSubmit_Yinpiao( QTTaskSubmit ):
	"""
	�ύ������Ʊ
	"""
	def __init__( self, *args ):
		QTTaskSubmit.__init__( self, *args )


	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_YINPIAO


	def isFitProperty( self, item ):
		"""
		"""
		return item.id == int( self.str1 ) and item.yinpiao() >= self.getPorpertyValue()

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s %s:   %i/%i"
		name = self.getPorpertyName()
		#value = self.getPorpertyValue()
		return msg % ( items.instance()[int(self.str1)]["name"], name, self.val1, self.val2)

	def complete( self, playerEntity ):
		"""
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		#kitTote = playerEntity.queryTemp( "questKitTote", None )
		order = playerEntity.queryTemp( "questOrder", None )
		item = playerEntity.getItem_( order )
		playerEntity.removeItem_( order, self.val2, csdefine.DELETE_ITEM_COMPLETESUBMIT_YINPIAO )

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if quantity > 0:
			if self.val2 > self.val1:
				self.val1 += quantity
				return True
		else:
			if self.val1 > 0:
				self.val1 += quantity
				return True
		return False

# ------------------------------------------------------------>
# QTTaskPetEvent
# ------------------------------------------------------------>
class QTTaskPetEvent( QTTask.QuestTaskDataType ):
	def __init__( self, *args ):
		"""
		#�ϳ� :	 eventType =  "combine"
		#ѱ�� :  eventType =  "joyancy"
		#ǿ�� :  eventType =  "enhance"
		#ι�� :  eventType =  "feed"
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ) > 0:
			self.index = args[0]		# index
			self.str1 = args[1]			# ��������
			self.str2 = args[2]			# ��������
			self.val2 = args[3]			# ��������

		self.val1 = 0

	def init( self, section ):
		"""
		"""
		self.index = section["index"].asInt
		self.str1 = section["param1"].asString
		self.str2 = section["param2"].asString
		self.val2 = section["param3"].asInt
		self.val1 = 0
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_PET_EVENT

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		return	# û����Ҫ�������

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return True

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )


	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,min(self.val1, self.val2), self.val2 )


	def getDetail( self, player ):
		"""
		ȡ���������
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		return ( self.getType(), self.str2,
				"%i / %i" % ( min(self.val1, self.val2), self.val2 ),
				isCollapsed,
				self.isCompleted( player )
				)
	def add( self, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		if self.val2 > self.val1:
			self.val1 += quantity
			return True
		return False

	def getEventType( self ):
		"""
		"""
		return self.str1


# ------------------------------------------------------------>
# QTTaskPetAct	��ս����	2009-07-15 14:30 SPF
# ------------------------------------------------------------>
class QTTaskPetAct( QTTaskEventTrigger ):
	"""
	��ҳ����Ƿ��ս������Ŀ��
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTaskEventTrigger.__init__( self, *args )
		self.str2 = cschannel_msgs.QUEST_INFO_43
		self.val2 = 1

	def init( self, section ):
		"""
		"""
		QTTaskEventTrigger.init( self, section )
		self.str2 = cschannel_msgs.QUEST_INFO_43
		self.val2 = 1
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_PET_ACT

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��
		@return: ����һ�����������ʵ��
		"""
		return QTTaskEventTrigger.newTaskBegin( self, player, tasks )

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		if quantity > 0:
			if self.val2 > self.val1:
				self.val1 += quantity
				return True
		else:
			if self.val1 > 0:
				self.val1 += quantity
				return True
		return False


# ------------------------------------------------------------>
# QTTaskevolution
# ------------------------------------------------------------>
class QTTaskEvolution( QTTaskKill ):	#������� spf

	def init( self, section ):
		"""
		@param section: format: monsterID, killAmount
		@type  section: pyDataSection
		"""
		QTTaskKill.init( self, section )
		self.str2 = section["param3"].asString		# Ҫɱ����Ŀ��
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_EVOLUTION

	def getEvolutClassName(self):
		"""
		��ȡ��Ҫ�����Ĺ����ID
		"""
		return self.str1

class QTTaskImperialExamination( QTTask.QuestTaskDataType ):
	"""
	����Ŀ�꣺�¼���������ĳ���ط�����ĳ������ ��:������� ���¼����1��
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""	# ��ȷ����
		self.str2 = ""	# ����
		self.val1 = 0	# ��ǰ�������
		self.val2 = 0	# ��Ҫ���״̬����

		@param args: ( string, int, string ) as itemID, useAmount, describe
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ):
			self.index = args[0]	# ����
			self.str2 = args[1]		# ����
			self.val2 = args[2]		# ��Ҫ���״̬����

	def init( self, section ):
		"""
		@param section: format: itemID, amount, describe
		@type  section: pyDataSection
		"""
		self.index = section["index"].asInt
		self.str1 = '0'
		self.str2 = section["param1"].asString		# describe
		self.val2 = section["param2"].asInt			# total complete of amount
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_IMPERIAL_EXAMINATION

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		pass

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return True



	def collapsedState( self ):
		"""
		��ʱ��ӵķ���
		��Ϊ����������û��ʧ�ܵı�ǣ����Խ�val1��-1��ʾʧ��
		"""
		# ֻ��û����ɵ����������ʧ�ܴ����˾�һ������ɾ��(qilan)
		if self.val1 < self.val2:
			self.val1 = -1

	def add( self, player, quantity, isRight ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		self.val1 += quantity
		if isRight:
			iRight = int( self.str1 ) + 1
			self.str1 = str( iRight )
			player.setTemp( "imperial_exam_right_num", int( self.str1 ) )
		return True

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		player.setTemp( "imperial_exam_total_num", self.val2 )
		return QTTask.instance.createObjFromDict( datas )

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = cschannel_msgs.KE_JU_VOICE_14
		return msg % ( self.str2 ,self.val1, self.val2, self.str1 )

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		if self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = cschannel_msgs.KE_JU_VOICE_15 % ( min(self.val1, self.val2), self.val2, self.str1 )
		return (self.getType(),
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted( player )
				)

from csconst import KAOGUANS
class QTTaskShowKaoGuan( QTTask.QuestTaskDataType ):
	"""
	����Ŀ�꣺��ʾ��ǰ����
	"""
	def __init__( self, *args ):
		"""
		self.str1 = ""	# ��ǰ���ٵ�className
		self.str2 = ""	# ����
		self.val1 = 0	# ��ǰ�������
		self.val2 = 0	# ��Ҫ���״̬����

		@param args: ( string, int, string ) as itemID, useAmount, describe
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ):
			self.index = args[0]	# ����
			self.str2 = args[1]		# ����
			self.val2 = args[2]		# ��Ҫ���״̬����

	def init( self, section ):
		"""
		@param section: format: itemID, amount, describe
		@type  section: pyDataSection
		"""
		self.index = section["index"].asInt
		self.str2 = section["param1"].asString		# describe
		self.val2 = section["param2"].asInt			# total complete of amount
		self.str1 = section["param3"].asString
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SHOW_KAOGUAN

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		pass

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return True

	def collapsedState( self ):
		"""
		��ʱ��ӵķ���
		��Ϊ����������û��ʧ�ܵı�ǣ����Խ�val1��-1��ʾʧ��
		"""
		# ֻ��û����ɵ����������ʧ�ܴ����˾�һ������ɾ��(qilan)
		if self.val1 < self.val2:
			self.val1 = -1

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		self.val1 += quantity
		return True

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = ""
		if KAOGUANS.has_key( self.val1+1 ):
			msg = cschannel_msgs.KE_JU_VOICE_16 % ( self.val1+1 )
		return msg

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		detail = ""
		if KAOGUANS.has_key( self.val1+1 ):
			detail = KAOGUANS[self.val1+1]
		return (self.getType(),
					self.str2,
					detail,
					isCollapsed,
					self.isCompleted( player )
				)


# ------------------------------------------------------------>
# QTTaskKill
# ------------------------------------------------------------>
class QTTaskKillWithPet( QTTaskKill ):
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_KILL_WITH_PET

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if not player.pcg_hasActPet() :
			return False
		if self.val2 > self.val1:
			self.val1 += quantity
			return True
		return False


# ------------------------------------------------------------>
# QTTaskQuestion
# ------------------------------------------------------------>
class QTTaskQuestion( QTTaskEventTrigger ):
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_QUESTION

	def init( self, section ):
		"""
		@param section: format: itemID, amount, describe
		@type  section: pyDataSection
		"""
		self.index = section["index"].asInt
		self.val2 = section["param2"].asInt			# total complete of amount
		self.str2 = section["param1"].asString		# describe
		self.str1 = section["param3"].asString		# describe
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16

	def add( self, player, questionType, isRight ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		if self.str1 != str(questionType):
			return False

		if isRight:
			self.val1 += 1
			if self.val1 == self.val2:
				player.removeTemp( "question_id_list" )
			return True
		else:
			player.removeTemp( "question_id_list" )
			self.val1 = 0
			return True


# ------------------------------------------------------------>
# QTTaskTalk
# ------------------------------------------------------------>
class QTTaskTalk( QTTaskEventTrigger ):
	def __init__( self, *args ):
		"""
		self.str1 = ""	# ��ǰ���ٵ�className
		self.str2 = ""	# ����
		self.val1 = 0	# ��ǰ�������
		self.val2 = 0	# ��Ҫ���״̬����

		@param args: ( string, int, string ) as itemID, useAmount, describe
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ):
			self.index = args[0]	# ����
			self.str1 = args[1]		# className
			self.val2 = args[2]		# ��Ҫ�Ի�����
			self.str2 = args[2]		# NPC����

	def init( self, section ):
		"""
		@param section: format: itemID, amount, describe
		@type  section: pyDataSection
		"""
		self.index = section["index"].asInt
		self.str1 = section["param1"].asString		# className
		self.val2 = section["param2"].asInt			# ��Ҫ�Ի�����
		self.str2 = section["param3"].asString		# NPC����
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_TALK

	def getClassName( self ):
		return self.str1

	def add( self, player, className ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		self.val1 += 1
		return True


# ------------------------------------------------------------>
# QTTaskHasBuff
# ------------------------------------------------------------>
class QTTaskHasBuff( QTTaskEventTrigger ):
	def __init__( self, *args ):
		"""
		self.str1 = ""	#
		self.str2 = ""	# ����
		self.val1 = 0	# ��ǰ�������
		self.val2 = 0	# ��Ҫ���״̬����

		@param args: ( string, int, string ) as itemID, useAmount, describe
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ):
			self.index = args[0]	# ����
			self.val2 = 1			# ӵ��buff
			self.str1 = args[1]		#
			self.str2 = args[2]		# ����Ŀ������

	def init( self, section ):
		"""
		@param section: format: itemID, amount, describe
		@type  section: pyDataSection
		"""
		self.index = section["index"].asInt
		self.val2 = 1								# ӵ��buff
		self.str1 = section["param1"].asString		# buff��ID(��12010)
		self.str2 = section["param3"].asString		# ����Ŀ������
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_HASBUFF

	def getBuffID( self ):
		"""
		"""
		return int( self.str1 )

	def add( self, buffID, val ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		if buffID == int( self.str1 ):
			if val > 0:
				self.val1 = 1
			else:
				self.val1 = 0
			return True
		return False

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��
		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		if len( player.findBuffsByBuffID( self.getBuffID() ) ) > 0:
			datas["val1"] = 1
		return QTTask.instance.createObjFromDict( datas )


# ------------------------------------------------------------>
# QTTaskPotentialFinish
# ------------------------------------------------------------>
class QTTaskPotentialFinish( QTTask.QuestTaskDataType ):
	def __init__( self, *args ):
		"""
		#�ϳ� :	 eventType =  "combine"
		#ѱ�� :  eventType =  "joyancy"
		#ǿ�� :  eventType =  "enhance"
		#ι�� :  eventType =  "feed"
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ) > 0:
			self.index = args[0]		# index
			self.str1 = args[1]			# ��������

		self.val1 = 0

	def init( self, section ):
		"""
		"""
		self.index = section["index"].asInt
		self.str1 = cschannel_msgs.POTENTIAL_VOICE1
		self.val1 = 0
		self.val2 = 1
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_POTENTIAL_FINISH

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		return	# û����Ҫ�������

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val2 <= self.val1

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return True

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )


	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s   %i/%i"
		return msg % ( self.str1 ,min(self.val1, self.val2), self.val2 )


	def getDetail( self, player ):
		"""
		ȡ���������
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		return ( self.getType(), self.str1,
				"%i / %i" % ( min(self.val1, self.val2), self.val2 ),
				isCollapsed,
				self.isCompleted( player )
				)
	def add( self, count ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		if self.val2 > self.val1:
			self.val1 += count
			return True
		return False



class QTTaskSubmit_LQEquip( QTTaskSubmit ):
	"""
	�ύһ���ȼ�Ʒ�ʵ�װ��
	"""
	def __init__( self, *args ):
		QTTaskSubmit.__init__( self, *args )


	def init( self, section ):
		"""
		@param section: format: itemID, deliverAmount
		@type  section: pyDataSection
		"""
		self.index 	= section["index"].asInt
		self.str1 	= section["param1"].asString			#Ʒ��
		self.str2 	= section["param2"].asString			#�ȼ�
		self.val2 	= 1
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_SUBMIT_LQEQUIP


	def isFitProperty( self, item ):
		"""
		"""
		return item.isEquip() and item.getQuality() >= int( self.str1 ) and item.getLevel() >= int( self.str2 )


	def isCompletedForNoStart( self, playerEntity ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		kitTote = playerEntity.queryTemp( "questKitTote", None )
		order = playerEntity.queryTemp( "questOrder", None )

		if kitTote == None and order == None:
			return True
		else:
			item = playerEntity.getItem_( order )
			if item is None:
				ERROR_MSG( "%s: the position in the item blacket is empty!" % (playerEntity.getName()) )
				playerEntity.statusMessage( csstatus.ROLE_QUEST_SUBMIT_NO_ITEM )
				return False
			if self.isFitProperty( item ):
				return True
			playerEntity.statusMessage( csstatus.ROLE_QUEST_SUBMIT_WRONG_TYPE )
			return False




	def getPorpertyName( self ):
		"""
		"""
		return cschannel_msgs.CELL_QUEST_TASK_LQ_EQUIP


	def getSubmitInfo( self ):
		"""
		"""
		return {"ItemName":cschannel_msgs.CELL_QUEST_TASK_LQ_EQUIP,"npcName":'('')', "count": self.val2}

	def complete( self, playerEntity ):
		"""
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		#kitTote = playerEntity.queryTemp( "questKitTote", None )
		order = playerEntity.queryTemp( "questOrder", -1 )
		item = playerEntity.getItem_( order )
		playerEntity.removeItem_( order, self.val2, csdefine.DELETE_ITEM_COMPLETEQTTASKSUBMIT )

# ------------------------------------------------------------>
# QTTaskEventSkillUsed
# ------------------------------------------------------------>
class QTTaskEventSkillUsed( QTTask.QuestTaskDataType ):
	"""
	����Ŀ�꣺ʹ�ü����¼�
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ):
			self.index = args[0]	# index
			self.str1 = args[1]		# des + skillID (des:skillID)
			self.str2 = args[3]		# className
			self.val2 = args[2]		# useAmount

	def init( self, section ):
		"""
		"""
		self.index = section["index"].asInt
		self.str1 = section["param1"].asString		# des + skillID (des:skillID)
		self.str2 = section["param2"].asString		# className
		self.val2 = section["param3"].asInt			# count
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_EVENT_USE_SKILL

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		pass

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return True

	def increaseState( self ):
		"""
		"""
		self.val1 += 1

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		self.val1 += quantity
		return True

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,self.val1, self.val2)

	def getSkillID( self ):
		"""
		��ȡʹ�ü��ܵ�ID
		"""
		id = 0
		try:
			id = int( self.str1.split(":")[1] )
		except:
			ERROR_MSG("QuestTask(QTTaskEventSkillUsed) param1 is not right!")

		return id


	def getClassName( self ):
		"""
		���Ŀ���className
		"""
		return self.str2

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		if self.val2 <= 1 :
			detail2 = ""
		else:
			detail2 = "%i / %i" % ( min(self.val1, self.val2), self.val2 )
		return (self.getType(),
					self.str1.split(":")[0],
					detail2,
					isCollapsed,
					self.isCompleted( player )
				)


# ------------------------------------------------------------>
# QTTaskEventUpdateSetRevivePos
# ------------------------------------------------------------>
class QTTaskEventUpdateSetRevivePos( QTTask.QuestTaskDataType ):
	"""
	����Ŀ�꣺���ð󶨵�
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTask.QuestTaskDataType.__init__( self )
		if len( args ):
			self.index = args[0]	# index
			self.str1 = args[1]		# des
			self.str2 = args[3]		# spaceName
			self.val2 = 1

	def init( self, section ):
		"""
		"""
		self.index = section["index"].asInt
		self.str1 = section["param1"].asString		# des
		self.str2 = section["param2"].asString		# spaceName
		self.val2 = 1
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_EVENT_REVIVE_POS

	def complete( self, playerEntity ):
		"""
		�������Ŀ��󱻵��ã����ڽ�����ʱ��ϵͳ��������Ŀ����صĵ��ߵȡ�

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		pass

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def isCompletedForNoStart( self, player ):
		"""
		ʵ����isCompleted()�ӿ�ͬ���Ĺ��ܣ��˽ӿ�����һЩ����Ҫ�ӵ�����
		���������Ҫ�ӣ�������Ҳ����и��������־��ֻ��ͨ��ֱ�Ӽ�����������Ŀ�����жϴ������Ƿ���ֱ����ɣ�
		Ҳ��Ϊ���磬�кܶ�����Ŀ�겢�������ڲ���Ҫ�ӵ�����

		@return: BOOL
		"""
		return True

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		self.val1 += quantity
		return True

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,self.val1, self.val2)

	def getSpaceName( self ):
		"""
		���Ŀ���className
		"""
		return self.str2

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		if self.val2 <= 1 :
			detail2 = ""
		else:
			detail2 = "%i / %i" % ( min(self.val1, self.val2), self.val2 )
		return (self.getType(),
					self.str1,
					detail2,
					isCollapsed,
					self.isCompleted( player )
				)

class QTTaskEnterSpace( QTTask.QuestTaskDataType ):
	"""
	����ĳһ���ռ�
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTask.QuestTaskDataType.__init__( self )

	def init( self, section ):
		"""
		@param args: ��ʼ������,������ʽ��ÿ��ʵ���Լ��涨
		@type  args: string
		"""
		QTTask.QuestTaskDataType.init( self, section )
		self.index = section["index"].asInt
		self.str1 = section["param1"].asString		# ����Ŀ������
		self.str2 = section["param2"].asString		# �ռ�����(��fengmingcheng)
		self.val1 = 0								# �Ƿ����������
		self.val2 = 1
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
		
	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		return self.str1

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_ENTER_SPCACE

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		detail2 = "%i / %i" % ( min(self.val1, self.val2), self.val2 )
		return (self.getType(),
					self.str1,
					detail2,
					isCollapsed,
					self.isCompleted( player )
				)

	def getNeedSpaceLabel( self ):
		"""
		"""
		return self.str2

	def arrived( self ):
		"""
		"""
		self.val1 += 1
		return True

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

	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2

	def increaseState( self ):
		"""
		"""
		self.val1 += 1

	def decreaseState( self ):
		"""
		"""
		if self.val1 > 0:
			self.val1 = 0

	def collapsedState( self ):
		"""
		��ʱ��ӵķ���
		��Ϊ����������û��ʧ�ܵı�ǣ����Խ�val1��-1��ʾʧ��
		"""
		if self.val1 < self.val2:
			self.val1 = -1

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		self.val1 += quantity
		return True

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s   %i/%i"
		return msg % ( self.str2 ,self.val1, self.val2 )

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		if self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return (self.getType(),
					self.str2,
					detail2,
					isCollapsed,
					self.isCompleted( player )
				)
				
class QTTaskAddCampMorale( QTTask.QuestTaskDataType ):
	"""
	��ȡ��Ӫʿ��
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTask.QuestTaskDataType.__init__( self )
		
	def init( self, section ):
		"""
		@param section: format: monsterID, killAmount
		@type  section: pyDataSection
		"""
		QTTask.QuestTaskDataType.init( self, section )
		self.index = section["index"].asInt
		self.str1 = section["param1"].asString		# ����Ŀ������
		self.val2 = section["param2"].asInt			# Ҫ���õĻ���
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_ADD_CAMP_MORALE
		
	def isCompleted( self, player ):
		"""
		���ص�ǰ����Ŀ���Ƿ����

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.val1 >= self.val2
		
	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		assert "im not support this method."
		
	def add( self, player, camp, amount ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		if amount <= 0 :
			return False
		if player.getCamp() != camp:
			return False
			
		self.val1 += amount
		return True
	
	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		if self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return (self.getType(),
					self.str1,
					detail2,
					isCollapsed,
					self.isCompleted( player )
				)
				
class QTTaskKill_CampActivity( QTTaskKill ):
	"""
	��Ӫ���ɱ�������� : �����ɱ�������ͼ�Ĺ���������
	"""
	def init( self, section ):
		"""
		@param section: format: monsterID, killAmount
		@type  section: pyDataSection
		"""
		QTTaskKill.init( self, section )
		self.str3 = section["param3"].asString			# Ҫ���ͼ
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_CAMP_KILL

	def add( self, player, quantity ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		if self.val2 > self.val1:
			spaces = self.str3.split(";")
			if player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) in spaces:
				self.val1 += quantity
				return True
		return False
	
	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		datas["str3"] = self.str3
		return QTTask.instance.createObjFromDict( datas )

class QTTaskVehicleActived( QTTaskEventTrigger ):
	"""
	���ָ������Ƿ񼤻������Ŀ��
	"""
	def __init__( self, *args ):
		"""
		"""
		QTTaskEventTrigger.__init__( self, *args )
		self.str2 = cschannel_msgs.QUEST_INFO_55
		self.val2 = 1

	def init( self, section ):
		"""
		"""
		QTTaskEventTrigger.init( self, section )
		self.index = section["index"].asInt
		self.str1 = section["param1"].asString	# ���ID
		self.str2 = cschannel_msgs.QUEST_INFO_55
		self.val2 = 1
		self.showOrder = section["param5"].asString	#�������Ŀ���˳��add by wuxo2012-4-16
	
	def isCompleted( self, playerEntity ):
		"""
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		currVehicleData = playerEntity.currVehicleData
		if currVehicleData is None:return False
		srcItemID = currVehicleData["srcItemID"]
		return srcItemID == int( self.str1 )

	def isCompletedForNoStart( self, playerEntity ):
		"""
		"""
		self.isCompleted( playerEntity )

	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_VEHICLE_ACTIVED

	def newTaskBegin( self, player, tasks ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��
		@return: ����һ�����������ʵ��
		"""
		datas = self.__dict__.copy()
		datas["implType"] = self.getType()
		datas["index"] = self.index
		return QTTask.instance.createObjFromDict( datas )

	def add( self, player, vehicleID ):
		"""
		@return: �����Ƿ�������޸�
		@rtype:  BOOL
		"""
		if self.val1 == -1:
			return False
		if str( vehicleID ) == self.str1:
			self.val1 += 1
			return True
		return False

	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		if self.val2 < 1 :
			detail2 = ""
		else:
			detail2 = "%i/%i" % ( min(self.val1, self.val2), self.val2 )
		return (self.getType(),
					self.str1,
					detail2,
					isCollapsed,
					self.isCompleted( player )
				)

class QTTaskDeliver_CampActivity( QTTaskDeliver ):
	"""
	��Ӫ���񽻸���Ʒ����Ŀ��: �ռ�ָ����ͼ����Ʒ
	"""
	def isValidSpace( self, playerEntity ):
		"""
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		spaceName = self.str2.split(":")[0]
		if spaceName == playerEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ):
			return True
		return False
	
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_CAMPACT_DELIVER
		
class QTTaskTalk_CampActivity( QTTaskTalk ):
	"""
	��Ӫ��Ի�����:��ָ����ͼNPC�Ի�
	��Ҫ�ǿͻ���Ѱ·��Ҫ�����Ӵ�����
	"""
	def getClassName( self ):
		return self.str1.split(":")[1]
		
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_CAMPACT_TALK

class QTTaskEventItemUsed_CampActivity( QTTaskEventItemUsed ):
	"""
	��Ӫ�ʹ����Ʒ����Ŀ��:��ָ����ͼ�ϵ�Ŀ��ʹ����Ʒ
	"""
	def getType( self ):
		return csdefine.QUEST_OBJECTIVE_CAMPACT_EVENT_USE_ITEM
		
	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		msg = "%s   %i/%i"
		return msg % ( self.getDescription() ,self.val1, self.val2)
	
	def isValidSpace( self, playerEntity ):
		"""
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		"""
		spaceName = self.str2.split(":")[0]
		if spaceName == playerEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ):
			return True
		return False
	
	def getDetail( self, player ):
		"""
		ȡ���������
		@return: (detail1, detail2, isCollapsed, isComplete) --> (string, string, bool, bool) --> ("Ұ��", "1/10", bool, bool)
		@rtype:  tuple
		"""
		isCollapsed = False
		if self.val1 == -1:
			isCollapsed = True
		if self.val2 <= 1 :
			detail2 = ""
		else:
			detail2 = "%i / %i" % ( min(self.val1, self.val2), self.val2 )
		return (self.getType(),
					self.getDescription(),
					detail2,
					isCollapsed,
					self.isCompleted( player )
				)
	def getDescription( self ):
		"""
		"""
		monster = g_objFactory.getObject( self.str2.split(":")[1] )
		if monster is None :
			ERROR_MSG( "monster lost.className: %s "% self.str1 )
			return self.str2.split(":")[2] % cschannel_msgs.QUEST_INFO_28
		else :
			return self.str2.split(":")[2] % monster.getName()		# Ҫɱ����Ŀ������

QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_TIME,				QTTaskTime )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DART_KILL,			QTTaskKillDart )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_KILL,				QTTaskKill )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_KILLS,				QTTaskKills )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_KILL_ROLE_TYPE_MONSTER,QTTaskKillRoleTypeMonster )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DELIVER,			QTTaskDeliver )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVENT_USE_ITEM,	QTTaskEventItemUsed )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_OWN_PET,			QTTaskOwnPet )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT,			QTTaskSubmit )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_TEAM,				QTTaskTeam )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVENT_TRIGGER,		QTTaskEventTrigger )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_LEVEL,				QTTaskLevel )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_QUEST,				QTTaskQuest )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_QUEST_NORMAL,		QTTaskQuestNormal )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_PICTURE,	QTTaskSubmitPicture )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DELIVER_PET,		QTTaskDeliverPet )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_QUALITY,	QTTaskSubmit_Quality )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_SLOT,		QTTaskSubmit_Slot )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_EFFECT,		QTTaskSubmit_Effect )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_LEVEL,		QTTaskSubmit_Level )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_BINDED,		QTTaskSubmit_Binded )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_EMPTY,		QTTaskSubmit_Empty )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_PET_EVENT,			QTTaskPetEvent )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVOLUTION,			QTTaskEvolution )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_YINPIAO,	QTTaskSubmit_Yinpiao )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_IMPERIAL_EXAMINATION,	QTTaskImperialExamination )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_KILL_WITH_PET,		QTTaskKillWithPet )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SHOW_KAOGUAN,		QTTaskShowKaoGuan )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_QUESTION,			QTTaskQuestion )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SKILL_LEARNED,		QTTaskSkillLearned )
QTTask.MAP_QUEST_TASK_TYPE(csdefine.QUEST_OBJECTIVE_LIVING_SKILL_LEARNED, QTTaskLivingSkillLearned)
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_PET_ACT,			QTTaskPetAct )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_TALK,				QTTaskTalk )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_HASBUFF,			QTTaskHasBuff )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DELIVER_QUALITY,	QTTaskDeliverQuality )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_CHANGE_BODY,	QTTaskSubmitChangeBody )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_DANCE,		QTTaskSubmitDance )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_POTENTIAL_FINISH,		QTTaskPotentialFinish )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SUBMIT_LQEQUIP,		QTTaskSubmit_LQEquip )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVENT_USE_SKILL,		QTTaskEventSkillUsed )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVENT_REVIVE_POS,		QTTaskEventUpdateSetRevivePos )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_ENTER_SPCACE,		QTTaskEnterSpace )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_POTENTIAL,			QTTaskPotential )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_NOT_SUBMIT_EMPTY,	QTTaskNotSubmit_Empty )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_ADD_CAMP_MORALE,	QTTaskAddCampMorale )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_CAMP_KILL,			QTTaskKill_CampActivity )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_VEHICLE_ACTIVED,		QTTaskVehicleActived )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_CAMPACT_DELIVER,	 QTTaskDeliver_CampActivity )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_CAMPACT_TALK,		 QTTaskTalk_CampActivity )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_CAMPACT_EVENT_USE_ITEM, QTTaskEventItemUsed_CampActivity )



QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskTime )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskKill )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskKills )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskKillRoleTypeMonster )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskKillDart )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskDeliver )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskEventItemUsed )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskOwnPet )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskSubmit )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskTeam )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskEventTrigger )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskLevel )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskQuest )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskQuestNormal )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskSubmitPicture )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskDeliverPet )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskSubmit_Quality )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskSubmit_Slot )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskSubmit_Effect )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskSubmit_Binded )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskSubmit_Level )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskSubmit_Empty )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskPetEvent )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskEvolution )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskSubmit_Yinpiao )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskImperialExamination )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskKillWithPet )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskShowKaoGuan )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskQuestion )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskSkillLearned )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskLivingSkillLearned )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskPetAct )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskTalk )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskHasBuff )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskDeliverQuality )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskSubmitChangeBody )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskSubmitDance )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskPotentialFinish )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskSubmit_LQEquip )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskEventSkillUsed )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskEventUpdateSetRevivePos )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskEnterSpace )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskPotential )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskNotSubmit_Empty )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskAddCampMorale )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskKill_CampActivity )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskVehicleActived )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskDeliver_CampActivity )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskTalk_CampActivity )
QTTask.MAP_QUEST_TASK_STR_TYPE( QTTaskEventItemUsed_CampActivity )
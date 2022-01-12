# -*- coding: gb18030 -*-
import csdefine
from Time import *

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

	def copyFrom( self, taskInstance ):
		"""
		"""
		assert isinstance( taskInstance, QTTaskTeam )
		self.__dict__.update( taskInstance.__dict__ )

	def isCompleted( self ):
		"""
		"""
		return self.val1 >= self.val2


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

	def copyFrom( self, taskInstance ):
		"""
		��һ������Ŀ���︴��������(���ͨ��ֻ����client)
		"""
		assert isinstance( taskInstance, QTTaskEnterSpace )
		self.__dict__.update( taskInstance.__dict__ )
		
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_TIME,					QTTaskTime )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_KILL,					QTTaskKill )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_KILLS,					QTTaskKills )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DART_KILL,				QTTaskKillDart )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_DELIVER,				QTTaskDeliver )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_EVENT_USE_ITEM,		QTTaskEventItemUsed )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_SKILL_LEARNED,			QTTaskSkillLearned )
QTTask.MAP_QUEST_TASK_TYPE( csdefine.QUEST_OBJECTIVE_LIVING_SKILL_LEARNED,	QTTaskLivingSkillLearned )
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
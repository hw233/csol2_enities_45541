# -*- coding: gb18030 -*-
#
# $Id: QuestTaskDataType.py,v 1.11 2008-08-07 09:04:25 zhangyuxing Exp $

"""
����Ŀ���������һ��ʵ���Ͷ�Ӧһ������Ŀ�ꡣ
ʵ���Զ����������ͽӿڣ�����������⡣
"""

from struct import *
from bwdebug import *
import csdefine
import new


# ӳ������Ŀ��������ʵ��������
# ��ӳ����Ҫ�����Զ������ͻ�ԭ����ʱʹ��
# key = Ŀ������: csdefine.QUEST_OBJECTIVE_*;
# value = �̳���QuestTaskDataType���࣬���ڸ�������ʵ��������Ķ���
# �����Ե�ֵ���ɼ̳���QuestTaskDataType����ģ����importʱ�Լ����
quest_task_data_type_maps = {}

# ӳ�������ַ���������ʵ��������
# ��ӳ����Ҫ���ڴ������г�ʼ������Ŀ������
# key = Ŀ�����ͣ��ַ������������ɸ������Լ�����
# value = �̳���QuestTaskDataType���࣬���ڸ�������ʵ��������Ķ���
# �����Ե�ֵ���ɼ̳���QuestTaskDataType����ģ����importʱ�Լ����
quest_task_data_str_type_maps = {}

def MAP_QUEST_TASK_TYPE( typeID, classObj ):
	"""
	ӳ������Ŀ��������ʵ��������
	"""
	quest_task_data_type_maps[typeID] = classObj

def MAP_QUEST_TASK_STR_TYPE( classObj ):
	"""
	ӳ������Ŀ��������ʵ��������
	"""
	# ʹ��classname��Ϊ������
	quest_task_data_str_type_maps[classObj.__name__] = classObj

def createTask( strType ):
	"""
	��������Ŀ��ʵ�������ڴ������г�ʼ������Ŀ��

	@return: instance of QTTask or derive from it
	@type:   QTTask
	"""
	try:
		return quest_task_data_str_type_maps[strType]()
	except KeyError:
		ERROR_MSG( "can't create instance by %s type." % strType )
		return None

class QuestTaskDataType:
	def __init__( self ):
		"""
		���������ɸ��̳�����Ծ������������
		"""
		self.str1 = ""
		self.str2 = ""
		self.str3 = ""
		self.val1 = 0
		self.val2 = 0
		self.index = 0			#ÿ������Ŀ�궼��������֧��
		self.showOrder = ""		#�������Ŀ���˳��add by wuxo 2012-4-16
		
	def getIndex( self ):
		"""
		ȡ������Ŀ��ID
		"""
		return self.index

	def getType( self ):
		"""
		virtual method.
		��������Ŀ������
		"""
		return csdefine.QUEST_OBJECTIVE_NONE

	def init( self, args ):
		"""
		@param args: ��ʼ������,������ʽ��ÿ��ʵ���Լ��涨
		@type  args: string
		"""
		pass

	def getMsg( self ):
		"""
		��ȡ���task��Ӧ�������������һ������
		"""
		pass

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
		pass

	def newTaskBegin( self, player ):
		"""
		���������ֵ���Ʋ���ʼһ���µ�����Ŀ��ʵ��

		@return: ����һ�����������ʵ��
		"""
		pass

	def increaseState( self ):
		"""
		virtual methed.
		����ӿ���������taskȥ����һ�����״̬,���ڸ���ô�����Ǹ��Բ�ͬ����task�Լ�������
		����:
			task1:����XXX����� 10��  (ÿ�ε���һ��������һ�����״̬)
		"""
		pass

	def setPlayerTemp( self, player, codeStr ):
		"""
		"""
		pass

	def removePlayerTemp( self, player ):
		"""
		"""
		pass

	def getKeyValue( self, codeStr, key ):
		"""
		"""
		keyStart = codeStr.find( key )
		if keyStart == -1:
			return ""
		valStart = codeStr.find( ':', keyStart + len( key ) ) + 1
		valEnd = codeStr.find( ',', keyStart + len( key ) )

		return codeStr[valStart:valEnd]

	##################################################################
	# BigWorld User Defined Type �Ľӿ�                              #
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		if isinstance( obj, dict ):		# ��dbmgr��������Ӧ�þ���һ���ֵ�
			return obj
		return { "str1" : obj.str1, "str2" : obj.str2, "str3" : obj.str3, "val1" : obj.val1, "val2" : obj.val2, "implType" : obj.getType(), "index" : obj.index, "showOrder" : obj.showOrder }

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		objDict = {}
		objDict.update( dict )
		objClass = quest_task_data_type_maps.get( dict["implType"], None )
		if objClass:	# ��dbmgr����ֵӦ�û�ΪNone������������沢û���κζ������Գ�ʼ����
			obj = new.instance( objClass, objDict )
			return obj
		# ��ǰ����������������dict��һ��FIXED_DICTʵ����
		# Ϊ�˱�����isSameType()�д������Ϊ��ʵ�����Ͳ���ȷ��
		# �ڴ˴���������Ϊpython�������ֵ�����
		return objDict

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		# ��dbmgr�У����objӦ����һ��dict
		return isinstance( obj, ( QuestTaskDataType, dict ) )

	def collapsedState( self ):
		"""
		Ϊ����ʧ������Ĵ�����val1��-1��ʾʧ��add by wuxo 2011-12-28
		"""
		self.val1 = -1

	def isFailed( self, player ) :
		"""
		�����Ƿ��Ѿ�ʧ��
		"""
		return self.val1 == -1

instance = QuestTaskDataType()


#
# $Log: not supported by cvs2svn $
# Revision 1.10  2007/12/19 03:40:18  kebiao
# onSetTaskComplete to increaseState
#
# Revision 1.9  2007/12/19 02:16:45  kebiao
# ��ӣ�onSetTaskComplete���ĳ������Ŀ��
#
# Revision 1.8  2007/12/19 02:12:41  kebiao
# ��ӣ�onSetQuestComplete���ĳ������Ŀ��
#
# Revision 1.7  2007/12/04 03:08:53  zhangyuxing
# 1.�����ݿ��д洢������Ŀ��ʱ��������һ������ index.
#
# Revision 1.6  2007/11/30 07:51:45  phw
# method modified: createObjFromDict(), ������new.instance()ʹ��FIXED_DICT���͵�ʵ����Ϊ������bug
#
# Revision 1.5  2007/11/30 07:38:19  phw
# method modified: createObjFromDict(), �����˷��ش������͵Ķ���ʵ�����½��̱�����bug
#
# Revision 1.4  2007/11/02 03:40:13  phw
# �޸��˴����͵Ĵ����ʽ����������Ŀ�궼�̳��ڴ�ģ�����
#
# Revision 1.3  2007/03/07 02:29:58  kebiao
# �޸���ʹ��FIXED_DICT����
#
# Revision 1.2  2006/03/22 02:34:02  phw
# ��Ӧ1.7����Զ������ͣ�����Ӧ�޸�
#
# Revision 1.1  2006/01/24 02:31:33  phw
# no message
#
#

# -*- coding: gb18030 -*-
#
# $Id: QuestTaskDataType.py,v 1.11 2008-08-07 09:04:25 zhangyuxing Exp $

"""
任务目标管理器，一个实例就对应一个任务目标。
实现自定义数据类型接口，解决传输问题。
"""

from struct import *
from bwdebug import *
import csdefine
import new


# 映射任务目标类型与实例化类型
# 此映射主要用于自定义类型还原数据时使用
# key = 目标类型: csdefine.QUEST_OBJECTIVE_*;
# value = 继承于QuestTaskDataType的类，用于根据类型实例化具体的对像；
# 此属性的值将由继承于QuestTaskDataType的类模块在import时自己填充
quest_task_data_type_maps = {}

# 映射任务字符串类型与实例化类型
# 此映射主要用于从配置中初始化任务目标类型
# key = 目标类型（字符串），内容由各类型自己定义
# value = 继承于QuestTaskDataType的类，用于根据类型实例化具体的对像；
# 此属性的值将由继承于QuestTaskDataType的类模块在import时自己填充
quest_task_data_str_type_maps = {}

def MAP_QUEST_TASK_TYPE( typeID, classObj ):
	"""
	映射任务目标类型与实例化类型
	"""
	quest_task_data_type_maps[typeID] = classObj

def MAP_QUEST_TASK_STR_TYPE( classObj ):
	"""
	映射任务目标类型与实例化类型
	"""
	# 使用classname作为类型名
	quest_task_data_str_type_maps[classObj.__name__] = classObj

def createTask( strType ):
	"""
	创建任务目标实例，用于从配置中初始化任务目标

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
		以下属性由各继承类各自决定其具体意义
		"""
		self.str1 = ""
		self.str2 = ""
		self.str3 = ""
		self.val1 = 0
		self.val2 = 0
		self.index = 0			#每个任务目标都加上索引支持
		self.showOrder = ""		#多个任务目标的顺序add by wuxo 2012-4-16
		
	def getIndex( self ):
		"""
		取得任务目标ID
		"""
		return self.index

	def getType( self ):
		"""
		virtual method.
		返回任务目标类型
		"""
		return csdefine.QUEST_OBJECTIVE_NONE

	def init( self, args ):
		"""
		@param args: 初始化参数,参数格式由每个实例自己规定
		@type  args: string
		"""
		pass

	def getMsg( self ):
		"""
		获取与该task对应的相关完成情况的一个描述
		"""
		pass

	def complete( self, playerEntity ):
		"""
		完成任务目标后被调用，用于交任务时让系统回收任务目标相关的道具等。

		@param playerEntity: 玩家entity实例
		@type  playerEntity: Entity
		"""
		pass

	def isCompleted( self, player ):
		"""
		返回当前任务目标是否完成

		@return: BOOL
		@rtype:  BOOL
		"""
		pass

	def newTaskBegin( self, player ):
		"""
		根据自身的值复制并开始一个新的任务目标实例

		@return: 返回一个复制自身的实例
		"""
		pass

	def increaseState( self ):
		"""
		virtual methed.
		这个接口是向本类型task去增加一个完成状态,至于该怎么增加是各自不同类型task自己的事情
		例子:
			task1:点亮XXX处火把 10个  (每次点亮一个就增加一个完成状态)
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
	# BigWorld User Defined Type 的接口                              #
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		if isinstance( obj, dict ):		# 在dbmgr里，这个对象应该就是一个字典
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
		if objClass:	# 在dbmgr里，这个值应该会为None，因此在那里面并没有任何东西可以初始化它
			obj = new.instance( objClass, objDict )
			return obj
		# 当前函数参数传进来的dict是一个FIXED_DICT实例，
		# 为了避免在isSameType()中错误的认为此实例类型不正确，
		# 在此处复制数据为python的内置字典类型
		return objDict

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		# 在dbmgr中，这个obj应该是一个dict
		return isinstance( obj, ( QuestTaskDataType, dict ) )

	def collapsedState( self ):
		"""
		为下线失败任务的处理，将val1置-1表示失败add by wuxo 2011-12-28
		"""
		self.val1 = -1

	def isFailed( self, player ) :
		"""
		任务是否已经失败
		"""
		return self.val1 == -1

instance = QuestTaskDataType()


#
# $Log: not supported by cvs2svn $
# Revision 1.10  2007/12/19 03:40:18  kebiao
# onSetTaskComplete to increaseState
#
# Revision 1.9  2007/12/19 02:16:45  kebiao
# 添加：onSetTaskComplete完成某个任务目标
#
# Revision 1.8  2007/12/19 02:12:41  kebiao
# 添加：onSetQuestComplete完成某个任务目标
#
# Revision 1.7  2007/12/04 03:08:53  zhangyuxing
# 1.在数据库中存储任务达成目标时，多增加一个索引 index.
#
# Revision 1.6  2007/11/30 07:51:45  phw
# method modified: createObjFromDict(), 修正了new.instance()使用FIXED_DICT类型的实例做为参数的bug
#
# Revision 1.5  2007/11/30 07:38:19  phw
# method modified: createObjFromDict(), 修正了返回错误类型的对象实例导致进程崩溃的bug
#
# Revision 1.4  2007/11/02 03:40:13  phw
# 修改了此类型的打包方式，所有任务目标都继承于此模块的类
#
# Revision 1.3  2007/03/07 02:29:58  kebiao
# 修改了使用FIXED_DICT类型
#
# Revision 1.2  2006/03/22 02:34:02  phw
# 适应1.7版的自定义类型，作相应修改
#
# Revision 1.1  2006/01/24 02:31:33  phw
# no message
#
#

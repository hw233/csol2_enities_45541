# -*- coding: gb18030 -*-

"""
用于对聊天信息中嵌入的物品、角色、宠物等对象连接的打包和解包操作
2010.03.18: writen by huangyongwei
"""

import re
import cPickle
import csdefine
from AbstractTemplates import Singleton
from AbstractTemplates import AbstractClass


# --------------------------------------------------------------------
# 变量定义
# --------------------------------------------------------------------
class ObjTypes :
	ITEM		= 0			# 道具
	SKILL		= 1			# 技能
	QUEST		= 2			# 任务
	PET			= 3			# 宠物
	ROLE		= 4			# 角色
	NPC			= 5			# NPC
	MONSTER		= 6			# 怪物
	LINK		= 7			# 链接

OBJ_COLORS = {
	ObjTypes.ITEM		: ( 255, 0, 255 ),		# 物品颜色跟质地一致
	ObjTypes.SKILL		: ( 255, 255, 255 ),	# 白色
	ObjTypes.QUEST		: ( 255, 255, 0 ),		# 黄色
	ObjTypes.PET		: ( 255, 128, 128 ),	# 粉色
	ObjTypes.ROLE		: ( 0, 255, 255 ),		# 青色
	ObjTypes.NPC		: ( 0, 255, 0 ),		# 绿色
	ObjTypes.MONSTER	: ( 255, 0, 0 ),		# 红色
	ObjTypes.LINK		: ( 0, 255, 0 ),		# 绿色
	}

g_reObjTpl = re.compile( "\[OBJ(.{6,}?)/(\d{1,2})\]", re.S )	# 信息正则模板( 析取对文本中的对象 )
_fmtMask = "[OBJ%s/%i]"											# 对象暗码格式
_fmtView = "[%s]"												# 对象明码格式

# --------------------------------------------------------------------
# 功能函数
# --------------------------------------------------------------------
def getObjMatchs( text ) :
	"""
	获取消息中消息对象的匹配
	@type			text : str
	@param			text : 消息文本
	@rtype				 : re.SRE_Match
	@return				 : 返回所有匹配对象的信息
	"""
	ms = []
	iter = g_reObjTpl.finditer( text )
	while True :
		try :
			ms.append( iter.next() )
		except StopIteration :
			break
	return ms

# -------------------------------------------
def maskObj( objType, info ) :
	"""
	格式化暗对象信息
	@type				objType  : MICRO DEFINATION
	@param				objType  : 上面定义中的其中一个
	@type				info	 : object type
	@param				info	 : 要生成暗码的对象（注意：需要支持 str 类型转换）
	@rtype						 : str
	@return						 : 返回暗码信息对象
	"""
	return _fmtMask % ( str( info ), objType )

def viewObj( objName ) :
	"""
	格式化明对象信息（在界面上显示的格式）
	@type				objName : str
	@param				objName : 要显示的对象的名称
	@rtype						: str
	@return						: 格式化后的显示信息
	"""
	return _fmtView % objName

def dumpObj( objType, obj ) :
	"""
	打包一个聊天网络传输的对象
	@type				objType : MACRO DEFINATION
	@param				objType : 上面定义中的其中一个
	@rtype						: BLOB
	@return						: 打包为一个对象参数，可以在聊天频道中作为聊天参数发送
	"""
	return cPickle.dumps( ( objType, obj ), 2 )


# --------------------------------------------------------------------
# 具体对象打包函数
# --------------------------------------------------------------------
def dumpItem( item ) :
	"""
	打包一个物品作为聊天中要发送的消息参数
	@type			item : item
	@param			item : 物品
	@rtype				 : BLOB
	@return				 : 返回打包后的物品参数
	使用方法：
			这是打包一个物品，然后夹杂在聊天信息中发送出去，因此它必需遵循某种规则，
		现在每个聊天发送/接收函数都会具带一个 blobs 参数，该参数就是各种聊天对象的
		打包列表。
			如果列表中存在 n 个聊天对象，则消息中必需包含 n 个插入对象的标记：${on}。
		例如：
			blobItems = [ChatObjParser.dumpItem( item1 ),		# item1 为百叶草
						 ChatObjParser.dumpItem( item2 ),]		# item2 为凌霄丹
			baseAppEntity.anonymityBroadcast( "ABC ${o0}，DEF ${o1} GHI", blobItems )
		则，客户端中收得的消息为：
			ABC [百叶草]，DEF [凌霄丹] GHI
	"""
	info = ( item.id, item.extra )
	return dumpObj( ObjTypes.ITEM, info )

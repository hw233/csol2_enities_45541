# -*- coding: gb18030 -*-

"""
���ڶ�������Ϣ��Ƕ�����Ʒ����ɫ������ȶ������ӵĴ���ͽ������
2010.03.18: writen by huangyongwei
"""

import re
import cPickle
import csdefine
from AbstractTemplates import Singleton
from AbstractTemplates import AbstractClass


# --------------------------------------------------------------------
# ��������
# --------------------------------------------------------------------
class ObjTypes :
	ITEM		= 0			# ����
	SKILL		= 1			# ����
	QUEST		= 2			# ����
	PET			= 3			# ����
	ROLE		= 4			# ��ɫ
	NPC			= 5			# NPC
	MONSTER		= 6			# ����
	LINK		= 7			# ����

OBJ_COLORS = {
	ObjTypes.ITEM		: ( 255, 0, 255 ),		# ��Ʒ��ɫ���ʵ�һ��
	ObjTypes.SKILL		: ( 255, 255, 255 ),	# ��ɫ
	ObjTypes.QUEST		: ( 255, 255, 0 ),		# ��ɫ
	ObjTypes.PET		: ( 255, 128, 128 ),	# ��ɫ
	ObjTypes.ROLE		: ( 0, 255, 255 ),		# ��ɫ
	ObjTypes.NPC		: ( 0, 255, 0 ),		# ��ɫ
	ObjTypes.MONSTER	: ( 255, 0, 0 ),		# ��ɫ
	ObjTypes.LINK		: ( 0, 255, 0 ),		# ��ɫ
	}

g_reObjTpl = re.compile( "\[OBJ(.{6,}?)/(\d{1,2})\]", re.S )	# ��Ϣ����ģ��( ��ȡ���ı��еĶ��� )
_fmtMask = "[OBJ%s/%i]"											# �������ʽ
_fmtView = "[%s]"												# ���������ʽ

# --------------------------------------------------------------------
# ���ܺ���
# --------------------------------------------------------------------
def getObjMatchs( text ) :
	"""
	��ȡ��Ϣ����Ϣ�����ƥ��
	@type			text : str
	@param			text : ��Ϣ�ı�
	@rtype				 : re.SRE_Match
	@return				 : ��������ƥ��������Ϣ
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
	��ʽ����������Ϣ
	@type				objType  : MICRO DEFINATION
	@param				objType  : ���涨���е�����һ��
	@type				info	 : object type
	@param				info	 : Ҫ���ɰ���Ķ���ע�⣺��Ҫ֧�� str ����ת����
	@rtype						 : str
	@return						 : ���ذ�����Ϣ����
	"""
	return _fmtMask % ( str( info ), objType )

def viewObj( objName ) :
	"""
	��ʽ����������Ϣ���ڽ�������ʾ�ĸ�ʽ��
	@type				objName : str
	@param				objName : Ҫ��ʾ�Ķ��������
	@rtype						: str
	@return						: ��ʽ�������ʾ��Ϣ
	"""
	return _fmtView % objName

def dumpObj( objType, obj ) :
	"""
	���һ���������紫��Ķ���
	@type				objType : MACRO DEFINATION
	@param				objType : ���涨���е�����һ��
	@rtype						: BLOB
	@return						: ���Ϊһ���������������������Ƶ������Ϊ�����������
	"""
	return cPickle.dumps( ( objType, obj ), 2 )


# --------------------------------------------------------------------
# �������������
# --------------------------------------------------------------------
def dumpItem( item ) :
	"""
	���һ����Ʒ��Ϊ������Ҫ���͵���Ϣ����
	@type			item : item
	@param			item : ��Ʒ
	@rtype				 : BLOB
	@return				 : ���ش�������Ʒ����
	ʹ�÷�����
			���Ǵ��һ����Ʒ��Ȼ�������������Ϣ�з��ͳ�ȥ�������������ѭĳ�ֹ���
		����ÿ�����췢��/���պ�������ߴ�һ�� blobs �������ò������Ǹ�����������
		����б�
			����б��д��� n �������������Ϣ�б������ n ���������ı�ǣ�${on}��
		���磺
			blobItems = [ChatObjParser.dumpItem( item1 ),		# item1 Ϊ��Ҷ��
						 ChatObjParser.dumpItem( item2 ),]		# item2 Ϊ������
			baseAppEntity.anonymityBroadcast( "ABC ${o0}��DEF ${o1} GHI", blobItems )
		�򣬿ͻ������յõ���ϢΪ��
			ABC [��Ҷ��]��DEF [������] GHI
	"""
	info = ( item.id, item.extra )
	return dumpObj( ObjTypes.ITEM, info )

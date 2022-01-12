# -*- coding: gb18030 -*-

# ------------------------------------------------
# from engine
import BigWorld
# ------------------------------------------------
# from python
import time
import random
# ------------------------------------------------
# from common
import csconst
from bwdebug import *
# ------------------------------------------------
# from current directory
from CopyEvent.CopyStageCondition import CopyStageCondition

# ------------------------------------------------


# --------------------------------------------------------------------
# ��������
#
# �������������Ա����ӵ�һЩ���������������
# ���Լ�������ר��������������һ�����ڹ���������Ƚ���
# �������������Ա�鿴ʹ�ã�Ҳ������
# --------------------------------------------------------------------

class CopyStageCondition_Share_spaceDataReach( CopyStageCondition ) :
	"""
	ĳ�ั���������ݴﵽһ����ֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		CopyStageCondition.__init__( self )
		self.spaceDataID = 0
		self.threshold = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.spaceDataID = section["param1"].asInt
		self.threshold = section["param2"].asInt

	def check( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		@param	params		:	�����¼��Ķ������ �� ����֧����Ϊ�˵õ������¼��Ķ�̬���� ��
		@type	params		 :	PY_DICT
		"""
		currentValue = int( BigWorld.getSpaceDataFirstForKey( spaceEntity.spaceID, self.spaceDataID ) )
		if currentValue == self.threshold :
			return True
		else :
			return False

class CopyStageCondition_Share_hasUserTimer( CopyStageCondition ) :
	"""
	��ǰ�����Ƿ���һ�û��Զ���timer
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		CopyStageCondition.__init__( self )
		self.uArg = -1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.uArg = section["param1"].asInt

	def check( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		@param	params		:	�����¼��Ķ������ �� ����֧����Ϊ�˵õ������¼��Ķ�̬���� ��
		@type	params		 :	PY_DICT
		"""
		return spaceEntity.hasUserTimer( self.uArg )

class CopyStageCondition_Share_isUserTimer( CopyStageCondition ) :
	"""
	�Ƿ���ĳһ�û��Զ���timer
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		CopyStageCondition.__init__( self )
		self.uArg = -1

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.uArg = section["param1"].asInt

	def check( self, spaceEntity, params ) :
		"""
		<virtual method>
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		@param	params		:	�����¼��Ķ������ �� ����֧����Ϊ�˵õ������¼��Ķ�̬���� ��
		@type	params		 :	PY_DICT
		"""
		return params["userArg"] == self.uArg

class CopyStageCondition_Share_isMonsterTypeDied(CopyStageCondition):
	"""
	�Ƿ���ָ�����͵Ĺ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		CopyStageCondition.__init__( self )
		self.class_name = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.class_name = section.readString("param1")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	ӵ�д���Ϊ�� event �� ����֧����Ϊ�˵õ���д CopyStageEvent �Ķ�̬���� ��
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		"""
		return self.class_name == params["monsterClassName"]


class CopyStageCondition_Share_rateLessThan(CopyStageCondition):
	"""
	�����ж�,С��ĳһ��ֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		CopyStageCondition.__init__( self )
		self.rate = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.rate = section.readFloat("param1")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	ӵ�д���Ϊ�� event �� ����֧����Ϊ�˵õ���д CopyStageEvent �Ķ�̬���� ��
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		"""
		return random.random() < self.rate


class CopyStageCondition_Share_timeModZero(CopyStageCondition):
	"""
	��ʱ���ȡģ�Ƿ�Ϊ�㣬����ʱ�����ж�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		CopyStageCondition.__init__( self )
		self.time_flag = ""
		self.mod = 1.0
		self.sensitivity = 0.5

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.time_flag = section.readString("param1")
		if section.readString("param2") != "":
			self.mod = section.readFloat("param2")
		if section.readString("param3") != "":
			self.sensitivity = section.readFloat("param3")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	ӵ�д���Ϊ�� event �� ����֧����Ϊ�˵õ���д CopyStageEvent �Ķ�̬���� ��
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		"""
		escape = time.time() - spaceEntity.queryTemp(self.time_flag)
		mod = escape % self.mod

		INFO_MSG("Time mod result: %f, mod: %f, sensitivity: %f" % (mod, self.mod, self.sensitivity))

		return (mod - 0) < self.sensitivity or (self.mod - mod) < self.sensitivity


class CopyStageCondition_Share_timeEscapeNotReach(CopyStageCondition):
	"""
	��ʱ��㾭����ʱ��ֵС��ָ��ֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		CopyStageCondition.__init__( self )
		self.time_flag = ""
		self.value = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.time_flag = section.readString("param1")
		self.value = section.readFloat("param2")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	ӵ�д���Ϊ�� event �� ����֧����Ϊ�˵õ���д CopyStageEvent �Ķ�̬���� ��
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		"""
		escape = time.time() - spaceEntity.queryTemp(self.time_flag)
		return escape < self.value


class CopyStageCondition_Share_timeEscapePass(CopyStageCondition):
	"""
	��ʱ��㾭����ʱ��ֵ����ָ��ֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		CopyStageCondition.__init__( self )
		self.time_flag = ""
		self.value = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.time_flag = section.readString("param1")
		self.value = section.readFloat("param2")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	ӵ�д���Ϊ�� event �� ����֧����Ϊ�˵õ���д CopyStageEvent �Ķ�̬���� ��
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		"""
		escape = time.time() - spaceEntity.queryTemp(self.time_flag)
		return escape > self.value


class CopyStageCondition_Share_tempFlagHasSet(CopyStageCondition):
	"""
	�ж�ָ����ʶ�Ƿ�����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		CopyStageCondition.__init__( self )
		self.temp_flag = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.temp_flag = section.readString("param1")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	ӵ�д���Ϊ�� event �� ����֧����Ϊ�˵õ���д CopyStageEvent �Ķ�̬���� ��
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		"""
		return spaceEntity.queryTemp(self.temp_flag) != None


class CopyStageCondition_Share_tempFlagNotSet(CopyStageCondition):
	"""
	�ж�ָ����ʶ�Ƿ�δ������
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		CopyStageCondition.__init__( self )
		self.temp_flag = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.temp_flag = section.readString("param1")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	ӵ�д���Ϊ�� event �� ����֧����Ϊ�˵õ���д CopyStageEvent �Ķ�̬���� ��
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		"""
		return spaceEntity.queryTemp(self.temp_flag) == None


class CopyStageCondition_Share_npcRecordLessThan(CopyStageCondition):
	"""
	�ж�ָ��NPC�����Ƿ�С��ĳ����ֵ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		CopyStageCondition.__init__( self )
		self.class_name = ""
		self.value = 0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.class_name = section.readString("param1")
		self.value = section.readInt("param2")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	ӵ�д���Ϊ�� event �� ����֧����Ϊ�˵õ���д CopyStageEvent �Ķ�̬���� ��
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		"""
		record = spaceEntity.queryTemp("NPC_AMOUNT_RECORD")
		if record is None:
			return True

		return record.get(self.class_name, 0) < self.value


class CopyStageCondition_Share_isCertainMonsters( CopyStageCondition ) :
	"""
	�Ƿ���ָ����ĳЩ��������,�����������ж������ params["monsterClassName"] ���¼�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		CopyStageCondition.__init__( self )
		self.classNames = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		classNames = section.readString("param1")
		self.classNames = classNames.split()

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	ӵ�д���Ϊ�� event �� ����֧����Ϊ�˵õ���д CopyStageEvent �Ķ�̬���� ��
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		"""
		className = params["monsterClassName"]
		return className in self.classNames


class CopyStageCondition_Share_isNotCertainMonsters( CopyStageCondition ) :
	"""
	�Ƿ���ָ����ĳЩ��������,�����������ж������ params["monsterClassName"] ���¼�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		CopyStageCondition.__init__( self )
		self.classNames = []

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		classNames = section.readString("param1")
		self.classNames = classNames.split()

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	ӵ�д���Ϊ�� event �� ����֧����Ϊ�˵õ���д CopyStageEvent �Ķ�̬���� ��
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		"""
		className = params["monsterClassName"]
		return className not in self.classNames

# --------------------------------------------------------------------
# ������������
# --------------------------------------------------------------------

# **************************************************************************************

# --------------------------------------------------------------------
# ������������ʼ
# --------------------------------------------------------------------

class CopyStageCondition_MMT_evilSoulPercent(CopyStageCondition):
	"""
	���������ж�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		CopyStageCondition.__init__( self )
		self.percent = 0
		self.total = 300.0

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.percent = section.readFloat("param1")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	ӵ�д���Ϊ�� event �� ����֧����Ϊ�˵õ���д CopyStageEvent �Ķ�̬���� ��
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		"""
		current = spaceEntity.queryTemp("YAOQI_VALUE", 0)
		return current / self.total >= self.percent

# --------------------------------------------------------------------
# ��������������
# --------------------------------------------------------------------

# **************************************************************************************

# --------------------------------------------------------------------
# ���ظ�����ʼ
# --------------------------------------------------------------------

class CopyStageCondition_FangShou_isTheArea(CopyStageCondition):
	"""
	�ж��Ƿ���ĳһ��������Ļ��ؿ���
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		CopyStageCondition.__init__( self )
		self.areaName = ""

	def init( self, section ):
		"""
		virtual method
		@param	section	: 	�洢���ݵ����ݶ�
		@type	section	:	PyDataSection
		"""
		CopyStageCondition.init( self, section )
		self.areaName = section.readString("param1")

	def check(self, spaceEntity, params):
		"""
		<virtual method>
		@param	event		:	ӵ�д���Ϊ�� event �� ����֧����Ϊ�˵õ���д CopyStageEvent �Ķ�̬���� ��
		@type	event 		:	instance of CopyStageEvent
		@param	spaceEntity :	ִ�д� CopyStageEvent �� spaceEntity
		@type	spaceEntity ��	�ռ� entity
		"""
		return params[ "areaName" ] == self.areaName


# --------------------------------------------------------------------
# ���ظ�������
# --------------------------------------------------------------------

# -*- coding: gb18030 -*-
#
# $Id: SkillLoader.py,v 1.12 2008-07-15 04:21:55 kebiao Exp $

"""
������Դ���ز��֡�
"""

import BigWorld
import Language
import csconst
from bwdebug import *
import Function
import time
from config.skill.Skill.SkillDataMgr import Datas as SKILL_DATAS

class BuffTime:
	"""
	һ��ֻ��ȡ����spellID�Լ�buff�Ƿ񱣴����Ϣ���ࡣ

	"""
	# ȫ�����ݼ���; key is BuffTime::_id and value is instance of BuffTime or derive from it.
	_instances = {}
	def __init__( self ):
		"""
		���캯����
		"""
		self._id = 0						# spell id
		self._name = ""						# spell name
		self._isSave = False				# �����Ƿ񱣴�
		self._alwayCalc = False				# ������߱��棬��ô���ߺ��Ƿ񻹼�������ʱ�䣿

	@staticmethod
	def instance( id ):
		"""
		ͨ�� action id ��ȡactionʵ��
		"""
		return BuffTime._instances[id]

	@staticmethod
	def setInstance( datas ):
		"""
		����ȫ�ֵ����ݼ��ϣ���ͨ����skill loader����

		@param datas: dict
		"""
		BuffTime._instances = datas

	def init( self, dictDat ):
		"""
		virtual method;
		��ȡ��������
		@param dictDat: ��������
		@type  dictDat: Python dict Data
		"""
		self._id = dictDat["ID"]
		self._name = dictDat[ "Name" ]
		if dictDat.has_key( "isSave" ) and dictDat["isSave"] != 0:	# ���߱��棬����ʱ
			self._isSave = True
			if dictDat[ "alwayCalc" ] != 0:
				self._alwayCalc = True

	def setSource( self, sourceSkillID, sourceIndex ):
		"""
		����Դ������Ϣ
		"""
		self._id = ( sourceSkillID * 100 ) + sourceIndex + 1 #sourceIndex + 1 ����ΪBUFF����IDʵ���Ǽ���ID+BUFF���ڵ����� �������1 ��ôskillID+0=skillID

	def getID( self ):
		"""
		"""
		return self._id

	def getName( self ):
		"""
		"""
		return self._name

	def isSave( self ):
		"""
		�ж��Ƿ���Ҫ����
		"""
		return self._isSave

	def isTimeout( self, cooldownTime ):
		"""
		�ж��Ƿ�ʱ���ѹ�

		@param cooldownTime: ��ֵ�����Ǿ���������ʹ��BigWorld.time() * ����ֵ�Ժ��ʱ��
		@type  cooldownTime: INT32
		@return: BOOL
		"""
		if cooldownTime == 0: return False		# �޳���ʱ�䣬��������
		return int( time.time() ) >= cooldownTime

	def calculateOnLoad( self, timeVal ):
		"""
		�ڼ����������ݵ�ʱ�����¼����ӳ�ֵ��
		1.��ȡʣ��ʱ��(��Ҫ�������ߺ��Ƿ��ʱ)
		2.�������ڵķ���������ʱ��

		@type  timeVal: INT32
		@return: �������µ�cooldownʱ��
		@rtype:  INT32
		"""
		if timeVal == 0: return timeVal		# �޳���ʱ�䣬������
		if self._alwayCalc:
			# ���ߺ��ʱ������ʱ������ʵʱ�䣬��Ҫ��ȥ�Ժ���ʣ��ʱ��
			timeVal -= int( time.time() )
		return int( timeVal + time.time() )		# int( (ʣ��ʱ�� + ��ǰ����ʱ��) * ����ֵ )

	def calculateOnSave( self, timeVal ):
		"""
		�ڱ����������ݵ�ʱ�����¼����ӳ�ֵ��
		1.��ȡʣ��ʱ��(��Ҫ�������ߺ��Ƿ��ʱ)
		2.����ʣ��ʱ��

		@type  timeVal: INT32
		@return: �������µ�cooldownʱ�䣻���Ǽ������д�������ֵ���Ǵ�cellData���õģ���˸�ֵ��һ��ʹ��BigWorld.time()����������
		@rtype:  INT32
		"""
		if timeVal == 0: return timeVal		# �޳���ʱ�䣬������
		# ȡ��ʣ��ʱ�䣬�����ȳ�������ֵ��ȡ������ʣ��ʱ��
		t = int( timeVal - time.time() )
		if self._alwayCalc:
			# ���ߺ��ʱ��������Ҫ��ֵ�������ʵʱ��
			t += int( time.time() )

		# ����������BUFF�ڱ����ʱ���ܷ���0
		# �����ڻָ�BUFF��ʱ��ᵼ����ʱ�����Ƶ�BUFF��������ڵ�BUFF
		if t <= 0: t = 1
		return t










class SkillLoader:
	_instance = None
	def __init__( self ):
		"""
		���캯����
		"""
		assert SkillLoader._instance is None		# ���������������ϵ�ʵ��
		self._datas = {}	# key is BuffTime::_id and value is instance of BuffTime which derive from it.
		BuffTime.setInstance( self._datas )
		SkillLoader._instance = self


	@staticmethod
	def instance():
		"""
		ͨ�� action id ��ȡactionʵ��
		"""
		if SkillLoader._instance is None:
			SkillLoader._instance = SkillLoader()
		return SkillLoader._instance

	def __getitem__( self, key ):
		"""
		ȡ��Skillʵ��
		"""
		if key in self._datas:
			return self._datas[ key ]
		return self.loadSkill( str( key ) )

	def loadSkill( self, skillID ):
		"""
		ָ������ĳ���ܻ���BUFF
		@type     skill: string
		"""
		DEBUG_MSG( "load skill %s." % skillID )
		buffID = 0
		iSkillID = int( skillID )
		if not SKILL_DATAS.has_key( iSkillID ):
			buffID = iSkillID
			iSkillID /= 100
			if not SKILL_DATAS.has_key( iSkillID ):
				ERROR_MSG( "buff config '%s' is not exist!" % iSkillID )
				return

		dictDat = SKILL_DATAS[ iSkillID ]
		instance = BuffTime()
		instance.init( dictDat )
		key = instance.getID()
		assert not self._datas.has_key( key ), "id %i is exist already in %s. reading file %i" % ( key, self._datas[key].getName(), skillID )
		self._datas[key] = instance
		#///////////////////////////////////////////////////////////////////////////////////////////
		if dictDat.has_key( "buff" ):
			index = 0
			for i in xrange( len( dictDat["buff"] ) ):
				buffInstance = BuffTime()
				try:
					buffInstance.init( dictDat["buff"][i] )
				except:
					ERROR_MSG( "Loading Buff", skillID )
					raise	# �ٴ��׳�
				buffInstance.setSource( instance.getID(), index )
				key = buffInstance.getID()
				assert not self._datas.has_key( key ), "buffID %i is exist already in %s. reading file %i" % ( key, self._datas[key].getName(), skillID )
				self._datas[key] = buffInstance
				index = index + 1
		if buffID > 0:
			return self._datas[buffID]
		return self._datas[iSkillID]


def instance():
	return SkillLoader.instance()

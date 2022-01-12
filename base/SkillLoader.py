# -*- coding: gb18030 -*-
#
# $Id: SkillLoader.py,v 1.12 2008-07-15 04:21:55 kebiao Exp $

"""
技能资源加载部分。
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
	一个只读取所有spellID以及buff是否保存的信息的类。

	"""
	# 全局数据集合; key is BuffTime::_id and value is instance of BuffTime or derive from it.
	_instances = {}
	def __init__( self ):
		"""
		构造函数。
		"""
		self._id = 0						# spell id
		self._name = ""						# spell name
		self._isSave = False				# 下线是否保存
		self._alwayCalc = False				# 如果下线保存，那么下线后是否还继续计算时间？

	@staticmethod
	def instance( id ):
		"""
		通过 action id 获取action实例
		"""
		return BuffTime._instances[id]

	@staticmethod
	def setInstance( datas ):
		"""
		设置全局的数据集合，此通过由skill loader调用

		@param datas: dict
		"""
		BuffTime._instances = datas

	def init( self, dictDat ):
		"""
		virtual method;
		读取技能配置
		@param dictDat: 配置数据
		@type  dictDat: Python dict Data
		"""
		self._id = dictDat["ID"]
		self._name = dictDat[ "Name" ]
		if dictDat.has_key( "isSave" ) and dictDat["isSave"] != 0:	# 下线保存，不计时
			self._isSave = True
			if dictDat[ "alwayCalc" ] != 0:
				self._alwayCalc = True

	def setSource( self, sourceSkillID, sourceIndex ):
		"""
		设置源技能信息
		"""
		self._id = ( sourceSkillID * 100 ) + sourceIndex + 1 #sourceIndex + 1 是因为BUFF程序ID实际是技能ID+BUFF所在的索引 如果不加1 那么skillID+0=skillID

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
		判断是否需要保存
		"""
		return self._isSave

	def isTimeout( self, cooldownTime ):
		"""
		判断是否时间已过

		@param cooldownTime: 该值必须是经过计算后的使用BigWorld.time() * 修正值以后的时间
		@type  cooldownTime: INT32
		@return: BOOL
		"""
		if cooldownTime == 0: return False		# 无持续时间，永不过期
		return int( time.time() ) >= cooldownTime

	def calculateOnLoad( self, timeVal ):
		"""
		在加载人物数据的时候重新计算延迟值。
		1.获取剩余时间(需要考虑下线后是否计时)
		2.加上现在的服务器运行时间

		@type  timeVal: INT32
		@return: 返回最新的cooldown时间
		@rtype:  INT32
		"""
		if timeVal == 0: return timeVal		# 无持续时间，不处理
		if self._alwayCalc:
			# 下线后计时，所以时间是真实时间，需要减去以后获得剩余时间
			timeVal -= int( time.time() )
		return int( timeVal + time.time() )		# int( (剩余时间 + 当前运行时间) * 修正值 )

	def calculateOnSave( self, timeVal ):
		"""
		在保存人物数据的时候重新计算延迟值。
		1.获取剩余时间(需要考虑下线后是否计时)
		2.返回剩余时间

		@type  timeVal: INT32
		@return: 返回最新的cooldown时间；我们假设所有传过来的值都是从cellData里获得的，因此该值是一个使用BigWorld.time()的整型数。
		@rtype:  INT32
		"""
		if timeVal == 0: return timeVal		# 无持续时间，不处理
		# 取得剩余时间，必须先除于修正值获取真正的剩余时间
		t = int( timeVal - time.time() )
		if self._alwayCalc:
			# 下线后计时，所以需要将值处理成真实时间
			t += int( time.time() )

		# 不是无限期BUFF在保存的时候不能返回0
		# 否则在恢复BUFF的时候会导致有时间限制的BUFF变成无限期的BUFF
		if t <= 0: t = 1
		return t










class SkillLoader:
	_instance = None
	def __init__( self ):
		"""
		构造函数。
		"""
		assert SkillLoader._instance is None		# 不允许有两个以上的实例
		self._datas = {}	# key is BuffTime::_id and value is instance of BuffTime which derive from it.
		BuffTime.setInstance( self._datas )
		SkillLoader._instance = self


	@staticmethod
	def instance():
		"""
		通过 action id 获取action实例
		"""
		if SkillLoader._instance is None:
			SkillLoader._instance = SkillLoader()
		return SkillLoader._instance

	def __getitem__( self, key ):
		"""
		取得Skill实例
		"""
		if key in self._datas:
			return self._datas[ key ]
		return self.loadSkill( str( key ) )

	def loadSkill( self, skillID ):
		"""
		指定加载某技能或者BUFF
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
					raise	# 再次抛出
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

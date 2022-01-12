# -*- coding: gb18030 -*-
#
# $Id: SkillLoader.py,v 1.15 2008-07-18 04:12:55 kebiao Exp $

"""
������Դ���ز��֡�
"""

import Language
from bwdebug import *
from SmartImport import smartImport
from Skills import SpellBase
from csdefine import *


class SkillLoader:
	_instance = None
	def __init__( self ):
		"""
		���캯����
		"""
		assert SkillLoader._instance is None		# ���������������ϵ�ʵ��
		self._datas = {}	# key is Skill::_id and value is instance of Skill which derive from it.
		SpellBase.Skill.setInstance( self )
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
		try:
			return self._datas[ key ]
		except:
			return self.loadSkill( str( key ) )
	
	def loadSkill( self, skillID ):
		"""
		ָ������ĳ���ܻ���BUFF
		@type		skillID: string
		"""
		from config.skill.Skill.SkillDataMgr import Datas as SKILL_DATA
		DEBUG_MSG( "load skill %s." % skillID )
		buffID = 0
		iskillID = int( skillID )
		print "=====>>>>>iskillID = ", iskillID
		if not SKILL_DATA.has_key( iskillID ):
			buffID = iskillID
			iskillID /= 100
			print "=====>>>>>buffID = ", buffID
			if not SKILL_DATA.has_key( iskillID ):
				raise KeyError, "skill or buff config '%s' is not exist!" % buffID
		
		dictData = SKILL_DATA[ iskillID ]
		#instance = smartImport( "Resource.Skills." + dictData["Class"] )()
		scriptName,className = dictData["Class"].split(":")
		instance = getattr( SKILL_DATA.getScript( scriptName ),className )()
		instance.init( dictData )
		iskillID = int( instance.getID() )
		assert not self._datas.has_key( iskillID ), "id: %s, class: Resource.Skills.%s is exist already " % ( iskillID, dictData["Class"] )
		self.register( iskillID, instance )
		if buffID > 0:
			return self._datas[buffID]
		return self._datas[iskillID]
		
	def has( self, skillID ):
		"""
		@type		skillID: int
		"""
		from config.skill.Skill.SkillDataMgr import Datas as SKILL_DATA
		return skillID in self._datas or SKILL_DATA.has_key( skillID )

	def register( self, key, skill ):
		"""
		"""
		self._datas[key] = skill


class BuffLimit:
	"""
	BUFF���޶����� ���� BUFF�����͵������� �� BUFF��Դ֮����໥��Լ��ϵ
	"""
	_instance = None
	def __init__( self, bufflimitPath = None ):
		"""
		���캯����
		@param configPath:	���������ļ�·��
		@type  configPath:	string
		"""
		assert BuffLimit._instance is None		# ���������������ϵ�ʵ��

		self._buffClassLimit = {} # BUFF�����ͬ���ʣ�BUFF��DEBUFF��ͬ���͵�ͬʱ���ڵ�������� { buff: {X����:������5��,...}, debuff:{...} }
		self._buffOriginLimit = {} #BUFFС��(��Դ)ͬʱ���ڵ����� {��С��: [���ɺ���С��ͬʱ����,���ɺ���С��ͬʱ���� ... ] }
		BuffLimit._instance = self

		if bufflimitPath is not None:
			self.load( bufflimitPath )

	@staticmethod
	def instance():
		"""
		ͨ�� action id ��ȡactionʵ��
		"""
		if BuffLimit._instance is None:
			BuffLimit._instance = BuffLimit()
		return BuffLimit._instance

	def load( self, filePath ):
		"""
		����BUFF�������ݡ�
		self._buffClassLimit = {} # BUFF�����ͬ���ʣ�BUFF��DEBUFF��ͬ���͵�ͬʱ���ڵ�������� { buff: {X����:������5��,...}, debuff:{...} }
		self._buffOriginLimit = {} #BUFFС��(��Դ)ͬʱ���ڵ����� {��С��: [���ɺ���С��ͬʱ����,���ɺ���С��ͬʱ���� ... ] }
		@param configPath:	���������ļ�·��
		@type  configPath:	string
		"""
		sec = Language.openConfigSection(filePath)
		if sec is None:
			raise SystemError, "Can not Load %s " % filePath

		self._buffClassLimit = {
			SKILL_EFFECT_STATE_BENIGN : {},
			SKILL_EFFECT_STATE_MALIGNANT : {},
			SKILL_EFFECT_STATE_NONE : {}
		}

		for subsec in sec["BUFF_LIMIT"].values():
			self._buffClassLimit[SKILL_EFFECT_STATE_BENIGN][ eval( subsec.name ) ] = subsec[ "BUFF" ].asInt
			self._buffClassLimit[SKILL_EFFECT_STATE_MALIGNANT][ eval( subsec.name ) ] = subsec[ "DEBUFF" ].asInt
			self._buffClassLimit[SKILL_EFFECT_STATE_NONE][ eval( subsec.name ) ] = subsec[ "XBUFF" ].asInt
		for subsec in sec["BUFF_ORIGIN_LIMIT"].values():
			self._buffOriginLimit[ eval( subsec.name ) ] = tuple( eval( '(' + subsec.asString.replace(' ','').replace('\r','').replace('\n','') + ',)' ) )

	def getBuffLimit( self, type, effectType ):
		"""
		ȡ�ø�BUFF���͵��������
		@param effectType: ���ԣ�����
		@param type����������Ч��	Ӱ����ΪЧ��	����Ч���仯	����Ч��	���������	����Ч��
		"""
		return self._buffClassLimit[ effectType ][ type ]

	def getSourceLimit( self, sourceType ):
		"""
		ȡ�ø�BUFF��Դ���������޵���������Դ����
		@param sourceType: ��Դ����
		"""
		return self._buffOriginLimit[ sourceType ]

def instance():
	return SkillLoader.instance()
def buffLimitInstance():
	return BuffLimit.instance()

g_skills = SkillLoader.instance()
g_buffLimit = BuffLimit.instance()


# -*- coding: gb18030 -*-
#
# $Id: SkillCtrl.py,v 1.11 2007-06-06 07:37:27 huangyongwei Exp $

"""
���ܵĹ���
"""

import BigWorld
import Language
import Define
from bwdebug import *

class SkillCtrl:
	"""
	���ܹ���
	@param 	skillData		: ��������
	@type  	skillData		: dict
	@param 	skills			: ����ְҵ��������
	@type  	skills			: dict
	"""
	def __init__( self, fileName ):
		self.skillData = {}
		self.skills = []
		self.loadSkill( fileName )

	def allotSkill( self, skills ):
		"""
		���似��
		@type	skills		:	list
		@param	skills		:	��������
		"""
		self.skills = []
		for name in skills:
			try:
				skillData = self.skillData[name]
				skillType = skillData["type"]
				skillKind = skillData["kind"]
				item = SkillItem( skillData )
				item.type = self.getSkillType( skillType, skillKind )
				self.skills.append( item )
			except:
				pass

	def getSkillType( self, skillType, kind ):
		"""
		ȡ���ܵ�����
		@type	skillType	:	string
		@param	skillType	:	���ܵ�����
		@type	kind		:	string
		@param	kind		:	���ܵ�����
		@rtype				:	int
		@return				:	���ܵ�����ֵ
		"""
		if skillType == "initiative" and kind == "work":
			return Define.SKILL_TYPE_ACTIVE_PROFESSION				# ְҵ�������ܡ�(�ֵܣ����� import * �˺ò��ã���)

		if skillType == "passiveness" and kind == "work":
			return Define.SKILL_TYPE_PASSIVE_PROFESSION				# ְҵ�������ܣ�Define.py

		if skillType == "initiative" and kind == "confraternity":
			return Define.SKILL_TYPE_ACTIVE_CORPS					# ������������

		if skillType == "passiveness" and kind == "confraternity":
			return Define.SKILL_TYPE_PASSIVE_CORPS					# ���ű�������

		if skillType == "initiative" and kind == "gest":
			return Define.SKILL_TYPE_ACTIVE_GEST

		if skillType == "passiveness" and kind == "gest":
			return Define.SKILL_TYPE_PASSIVE_GEST
		return None

	def loadSkill( self, fileName ):
		"""
		���ؼ�������
		@type	fileName		:	string
		@param	fileName		:	�ļ���
		"""
		fileSect = Language.openConfigSection(fileName)
		if fileSect == None:
			ERROR_MSG( "Can not Load : %s" % fileName )
			return False

		self.skillData = {}
		#ְҵ����
		workSect = fileSect._work
		self.skillData.update( self.readSkillSect( workSect._initiative, "initiative", "work" ) )
		self.skillData.update( self.readSkillSect( workSect._passiveness, "passiveness", "work" ) )

		#��Ἴ��
		confSect = fileSect._confraternity
		self.skillData.update( self.readSkillSect( confSect._initiative, "initiative", "confraternity" ) )
		self.skillData.update( self.readSkillSect( confSect._passiveness, "passiveness", "confraternity" ) )

		#���鼼��
		gestSect = fileSect._gest
		self.skillData.update( self.readSkillSect( gestSect._initiative, "initiative", "gest" ) )
		self.skillData.update( self.readSkillSect( gestSect._passiveness, "passiveness", "gest" ) )

	def readSkillSect( self, sect, skillType, skillKind ):
		"""
		��ȡ���ݶ�
		@type	sect		:	DataSection
		@param	sect		:	���ݶ�
		@type	skillType	:	string
		@param	skillType	:	����
		@type	skillKind	:	string
		@param	skillKind	:	�������
		@rtype				:	dict
		@return				:	��������
		"""
		dataList = {}
		for (name, dataSect) in sect.items():
			data = {}
			data["explain"] = dataSect._explain.asString
			data["name"] = dataSect._name.asString
			data["icon"] = dataSect._icon.asString
			data["type"] = skillType
			data["kind"] = skillKind
			data["key"] = name
			dataList[name] = data
		return dataList

class SkillItem:
	"""
	������
	"""
	def __init__( self, dict ):
		"""
		��ʼ��
		"""
		self.key = dict["key"]
		self.description = dict["explain"]
		self.name = dict["name"]
		self.icon = dict["icon"]
		self.type = ""

#
# $Log: not supported by cvs2svn $
# Revision 1.10  2007/06/06 03:29:52  huangyongwei
# �޸��˻�ȡ��������ʱ�����صļ������ඨ�壺
# ��ԭ���� Define �ж��壬��Ϊ�ŵ� Define ��
# ���޸��˺�����
#
# Revision 1.9  2006/01/07 08:57:30  huangyongwei
# ����˼������Ƽ�
#
# Revision 1.8  2005/12/19 09:56:11  panguankong
# �޸ĵ��ڲ���ȡ��ʽ
#
# Revision 1.7  2005/08/29 01:43:54  panguankong
# ɾ���˶���Ĵ���
#
# Revision 1.6  2005/08/29 01:19:59  panguankong
# �޸��˲��ִ���
#
# Revision 1.5  2005/08/25 11:20:59  panguankong
# �޸���ԭ���Ķ���
#
# Revision 1.4  2005/08/25 11:11:00  panguankong
# �޸ļ��ܼ�ֵ
#
# Revision 1.3  2005/08/25 09:34:47  panguankong
# �޸��˼��ܸ�ʽ
#
# Revision 1.2  2005/08/25 08:40:40  panguankong
# �޸��˼�����Ϊ��
#
# Revision 1.1  2005/08/24 06:39:19  panguankong
# ����˼��ܷ���
#

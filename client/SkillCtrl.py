# -*- coding: gb18030 -*-
#
# $Id: SkillCtrl.py,v 1.11 2007-06-06 07:37:27 huangyongwei Exp $

"""
技能的管理。
"""

import BigWorld
import Language
import Define
from bwdebug import *

class SkillCtrl:
	"""
	技能管理
	@param 	skillData		: 技能数据
	@type  	skillData		: dict
	@param 	skills			: 主动职业技能数据
	@type  	skills			: dict
	"""
	def __init__( self, fileName ):
		self.skillData = {}
		self.skills = []
		self.loadSkill( fileName )

	def allotSkill( self, skills ):
		"""
		分配技能
		@type	skills		:	list
		@param	skills		:	技能数据
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
		取技能的类型
		@type	skillType	:	string
		@param	skillType	:	技能的类型
		@type	kind		:	string
		@param	kind		:	技能的种类
		@rtype				:	int
		@return				:	技能的类型值
		"""
		if skillType == "initiative" and kind == "work":
			return Define.SKILL_TYPE_ACTIVE_PROFESSION				# 职业主动技能。(兄弟，别用 import * 了好不好！！)

		if skillType == "passiveness" and kind == "work":
			return Define.SKILL_TYPE_PASSIVE_PROFESSION				# 职业被动技能，Define.py

		if skillType == "initiative" and kind == "confraternity":
			return Define.SKILL_TYPE_ACTIVE_CORPS					# 军团主动技能

		if skillType == "passiveness" and kind == "confraternity":
			return Define.SKILL_TYPE_PASSIVE_CORPS					# 军团被动技能

		if skillType == "initiative" and kind == "gest":
			return Define.SKILL_TYPE_ACTIVE_GEST

		if skillType == "passiveness" and kind == "gest":
			return Define.SKILL_TYPE_PASSIVE_GEST
		return None

	def loadSkill( self, fileName ):
		"""
		加载技能数据
		@type	fileName		:	string
		@param	fileName		:	文件名
		"""
		fileSect = Language.openConfigSection(fileName)
		if fileSect == None:
			ERROR_MSG( "Can not Load : %s" % fileName )
			return False

		self.skillData = {}
		#职业技能
		workSect = fileSect._work
		self.skillData.update( self.readSkillSect( workSect._initiative, "initiative", "work" ) )
		self.skillData.update( self.readSkillSect( workSect._passiveness, "passiveness", "work" ) )

		#帮会技能
		confSect = fileSect._confraternity
		self.skillData.update( self.readSkillSect( confSect._initiative, "initiative", "confraternity" ) )
		self.skillData.update( self.readSkillSect( confSect._passiveness, "passiveness", "confraternity" ) )

		#剧情技能
		gestSect = fileSect._gest
		self.skillData.update( self.readSkillSect( gestSect._initiative, "initiative", "gest" ) )
		self.skillData.update( self.readSkillSect( gestSect._passiveness, "passiveness", "gest" ) )

	def readSkillSect( self, sect, skillType, skillKind ):
		"""
		读取数据段
		@type	sect		:	DataSection
		@param	sect		:	数据段
		@type	skillType	:	string
		@param	skillType	:	类型
		@type	skillKind	:	string
		@param	skillKind	:	技能类别
		@rtype				:	dict
		@return				:	技能数据
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
	技能类
	"""
	def __init__( self, dict ):
		"""
		初始化
		"""
		self.key = dict["key"]
		self.description = dict["explain"]
		self.name = dict["name"]
		self.icon = dict["icon"]
		self.type = ""

#
# $Log: not supported by cvs2svn $
# Revision 1.10  2007/06/06 03:29:52  huangyongwei
# 修改了获取技能类型时，返回的技能种类定义：
# 由原来在 Define 中定义，改为放到 Define 中
# 并修改了宏名称
#
# Revision 1.9  2006/01/07 08:57:30  huangyongwei
# 添加了技能名称键
#
# Revision 1.8  2005/12/19 09:56:11  panguankong
# 修改的内部读取方式
#
# Revision 1.7  2005/08/29 01:43:54  panguankong
# 删除了多余的代码
#
# Revision 1.6  2005/08/29 01:19:59  panguankong
# 修改了部分代码
#
# Revision 1.5  2005/08/25 11:20:59  panguankong
# 修改了原来的定义
#
# Revision 1.4  2005/08/25 11:11:00  panguankong
# 修改技能键值
#
# Revision 1.3  2005/08/25 09:34:47  panguankong
# 修改了技能格式
#
# Revision 1.2  2005/08/25 08:40:40  panguankong
# 修改了技能项为类
#
# Revision 1.1  2005/08/24 06:39:19  panguankong
# 添加了技能分类
#

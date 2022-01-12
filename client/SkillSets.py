# -*- coding: gb18030 -*-
"""
SkillSets for client entity
first write by wolf
"""
# $Id: SkillSets.py,v 1.3 2005-03-29 09:19:46 phw Exp $

import BigWorld

class SkillSets:
	def addSkill( self, argSkillName ):
		"""
		向技能栏里增加一个技能
		
		@param argSkillName: 技能名称
		@type  argSkillName: str
		@return:             无
		"""
		# First check whether player has this skill, for client, here cat uncheck
		if self._skillIsExist( argSkillName ):
			print "Error: skill already exist. skill name = %s" % argSkillName
			return
		self.attrSkillSets.append( argSkillName )
		return
	### end of method: addSkill() ###
	    
	def removeSkill( self, argSkillName ):
		"""
		从技能栏里删除一个技能

		@param argSkillName: 技能名称
		@type  argSkillName: str
		@return:             无
		"""
		for strSkillName in self.attrSkillSets:
			if strSkillName == argSkillName:
				# remove first occurrence of value 
				self.attrSkillSets.remove( argSkillName )
				return
		print "Error: skill not exist. skill name = %s" % argSkillName
		return
	### end of method: removeSkill() ###

	def _skillIsExist( self, argSkillName ):
		"""
		内部方法，判断一个技能是否存在
		
		@param argSkillName: 技能名称
		@type  argSkillName: str
		@return:			 True == 存在，False == 不存在
		@rtype:              bool
		@note:               this is inline function, not definition in .def file,
		                     so it can't call by other entity(include it ghosted entity)
		"""
		for strSkillName in self.attrSkillSets:
			if strSkillName == argSkillName:
				return True
		return False


# $Log: not supported by cvs2svn $

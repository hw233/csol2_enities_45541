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
		������������һ������
		
		@param argSkillName: ��������
		@type  argSkillName: str
		@return:             ��
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
		�Ӽ�������ɾ��һ������

		@param argSkillName: ��������
		@type  argSkillName: str
		@return:             ��
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
		�ڲ��������ж�һ�������Ƿ����
		
		@param argSkillName: ��������
		@type  argSkillName: str
		@return:			 True == ���ڣ�False == ������
		@rtype:              bool
		@note:               this is inline function, not definition in .def file,
		                     so it can't call by other entity(include it ghosted entity)
		"""
		for strSkillName in self.attrSkillSets:
			if strSkillName == argSkillName:
				return True
		return False


# $Log: not supported by cvs2svn $

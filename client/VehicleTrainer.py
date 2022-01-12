# -*- coding: gb18030 -*-

# this module implement the VehicleTrainer class
# written by gjx 2009-06-13
#
# ��Trainer�ٳ����VehicleTrainer���б�Ҫ�ģ��ͻ�����Ҫ
# ���ݲ�ͬ���͵�ѵ��ʦ��������Ӧ�Ľ�����֡�

from Trainer import Trainer
import skills
import BigWorld
import GUIFacade

class VehicleTrainer( Trainer ) :

	def __init__( self ) :
		Trainer.__init__( self )

	def receiveTrainInfos( self, skillIDs ):
		"""
		@param skillIDs: array of int64
		"""
		#self.attrTrainIDs = set( skillIDs )
		self.attrTrainInfo = {}
		player = BigWorld.player()

		for id in skillIDs:
			spell = skills.getSkill( id )
			#if player.hasSkill( spell.getTeach() + spell.getTeachMaxLevel() - 1 ):
			#	continue	# �����Ѿ�ѧ��ļ���
			name = spell.getName()
			type = 0	# ��ʱȫΪ0
			level = spell.getReqLevel()
			cost = spell.getCost()
			self.attrTrainInfo[id] = [name, type, level, cost]
		GUIFacade.showLearnSkillWindow( self )

	def getLearnSkillIDs( self ) :
		"""
		��ȡ����ѧϰ���ܣ���������Ϊ��赼ʦ
		����ÿ�ζ����˵����ĳ�����Ĳ����ü���
		"""
		skillIDs = self.attrTrainInfo.keys()
		count = len( skillIDs )
		for i in xrange( 1, count ):
			for ii in xrange( i ):
				iskill = skills.getSkill( skillIDs[i] )
				iiskill = skills.getSkill( skillIDs[ii] )
				if iskill.getFirstReqLevel() < iiskill.getFirstReqLevel():
					tmp = skillIDs[i]
					skillIDs[i] = skillIDs[ii]
					skillIDs[ii] = tmp
		return skillIDs
# -*- coding: gb18030 -*-
#

"""
����ϵͳģ��
"""
import BigWorld
import csstatus
from Function import switchMoney
from MessageBox import *
from config.client.msgboxtexts import Datas as mbmsgs
import skills
from LivingConfigMgr import LivingConfigMgr

lvcMgr = LivingConfigMgr.instance()

SKILLID_NAME = {
				790001001:"",
				790002001:"",
				790003001:"",
				790004001:"",
				790005001:"",
			}

class LivingSystem:
	"""
	"""
	def __init__( self ):
		"""
		��ʼ��״̬��Ҫ��Fight��ʼ��֮ǰ
		"""
		self.livingskill = {}
		self.livingskillNameInit = False


	def onClientGetLivingSkill( self, skillID, sleight, level ):
		"""
		define method
		����������ĳ������ܵ�����
		"""
		if level == 0 and self.livingskill.has_key( skillID ):
			self.livingskill.pop( skillID )
			return
		self.livingskill[skillID] = ( sleight, level )

		self.onUpdateSkill_2( skillID, skillID )

	def livingTeacherTalkResult( self, talkResult, skillID, level, param ):
		"""
		define method
		�����ѧϰ�Ի��������ȷ��
		"""
		if not self.livingskillNameInit:
			for id in SKILLID_NAME:
				skillInstance = skills.getSkill(id)
				if skillInstance is None:
					ERROR_MSG( "Living skill %s is None."%(id) )
					return
				SKILLID_NAME[id] = skillInstance.getName()

		if talkResult == 2:	# ����
			def query( rs_id ):
				if rs_id == RS_OK:
					self.cell.onTeachTalkObliveSkill( skillID )
			# �Ƿ�ȷ������%s���ܣ��ȼ�%i����
			showMessage( mbmsgs[0x00e1] % ( SKILLID_NAME[skillID], level ) ,"", MB_OK_CANCEL, query )
		elif talkResult == 3:	# ����
			level += 1
			if self.money < param:
				self.statusMessage( csstatus.LIVING_LEARN_NOT_ENOUGHT_MONEY )
				return
			money = switchMoney( param )
			def query( rs_id ):
				if rs_id == RS_OK:
					self.cell.onTeachTalkLVUPSkill( skillID, param )
			levelString = lvcMgr.getDesByLevel( skillID, level ).split( "|" )[-1]
			# �Ƿ񻨷�%s��%s����������%s��
			showMessage( mbmsgs[0x00e2]%( money, SKILLID_NAME[skillID], levelString ) ,"", MB_OK_CANCEL, query )
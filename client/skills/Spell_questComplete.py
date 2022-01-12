# -*- coding: gb18030 -*-

#edit by wuxo 2011-9-20
"""
Spell�����ࡣʵ�ֿͻ���NPC˵���������������ž�ͷ��һ��ʼ�Ϳ�����ң�
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csstatus
import csdefine
import Define
from gbref import rds
import Action
import Const
import event.EventCenter as ECenter

class Spell_questComplete( Spell ):
	def __init__( self ):
		"""
		��python dict����SkillBase
		"""
		Spell.__init__( self )
		self.playTarget = None		#Ŀ��
		self.npcs = []     #���ص�npc��classname
		self.entities = []
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict:			��������
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		if dict["param1"] == "":
			self.param1 = ()
		else:
			self.param1 = eval( dict["param1"] ) 	#NPC˵������
		if dict["param2"] == "":
			self.param2 = ()
		else:
			self.param2 = eval( dict["param2"] ) 	#NPC��������
		if dict["param3"] == "":
			self.param3 = ()
			self.npcs = []
		else:
			param3 = dict["param3"].split(";")
			self.param3 = eval( param3[0] ) 	#��ͷ���ţ��Ƿ�����NPC
			if len(param3) > 1:
				self.npcs = param3[1:]
			
	def cast( self, caster, targetObject ):
		"""
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		player = BigWorld.player()
		target = targetObject.getObject()
		self.playTarget = target
		
		#����һ��ʼ�Ϳ�����ҿͻ��˲�����Ui
		ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", 0 )
		if player:
			player.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE,Define.CONTROL_FORBID_ROLE_MOVE_CAMERA_EVENT )
			player.addControlForbid( Define.CONTROL_FORBID_ROLE_CAMERA,Define.CONTROL_FORBID_ROLE_CAMERA_EVENT )
		
		if self.playTarget != None:	#NPC˵��
			if len(self.param1) == 2 and self.param1[1] >= 0:
				BigWorld.callback(self.param1[1],self.playNPCSay)
			if len(self.param2) == 2 and self.param2[1] >= 0:
				model = self.playTarget.getModel()
				rds.actionMgr.playAction( model, self.param2[0], self.param2[1], None )
		if caster.id == player.id:	#ֻ���Լ��Ŀͻ��˲��ž�ͷ
			if len(self.param3) == 4 and self.param3[2] >= 0:
				BigWorld.callback(self.param3[2], self.playCamera)
	
	def playNPCSay(self):
		"""
		nPC˵��
		"""
		self.playTarget.onSay( self.playTarget.getName(), self.param1[0] )
		
	
	def playCamera( self ):
		"""
		���ž�ͷ
		"""
		rds.cameraEventMgr.trigger( self.param3[0] )
		p = BigWorld.player()
		for en in p.entitiesInRange( 50 ):
			if hasattr( en, "className" ) and en.className in self.npcs:
				self.entities.append(en)
		
		if self.param3[1] == 1:
			self.entities.append(p)
		
		for e in self.entities:
			e.setVisibility( False )
		
		if self.param3[3] > 0:	#���ض��
			BigWorld.callback( self.param3[3], self.showTargetModdel )	

	def showTargetModdel( self ):
		"""
		��ʾĿ��ģ��
		"""
		for e in self.entities:
			e.setVisibility( True )
			
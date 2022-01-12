# -*- coding: gb18030 -*-
#
# $Id:  Exp $


from SpellBase import *
import random
import csdefine
import csstatus
from bwdebug import *
from SpellBase.HomingSpell import ActiveHomingSpell
from Function import newUID
import Math
import VehicleHelper

class Spell_323005( ActiveHomingSpell ):
	"""
	��������1
	"""
	def __init__( self ):
		"""
		"""
		ActiveHomingSpell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		ActiveHomingSpell.init( self, dict )
		self._casterActions = dict["param4"].split(",")
		self._targetActions = dict["param5"].split(",")

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		targetEntity = target.getObject()
		if targetEntity is None: return csstatus.SKILL_UNKNOW
		if targetEntity.findBuffByBuffID( 299021 ):
			return csstatus.SKILL_RECEIVE_OBJECT_NOT_MONSTER

		return ActiveHomingSpell.useableCheck( self, caster, target )

	def cast( self, caster, target ) :
		"""
		virtual method
		ϵͳʩ�ţ�û�������壬���Զ���˲��
		"""
		ActiveHomingSpell.cast( self, caster, target )
		actionName = "swordman_combo01_1"
		if VehicleHelper.getCurrVehicleID( caster ):
			actionName = "ride_" + "swordman_combo01_1"
		#caster.allClients.onPlayAction( actionName )

	def onTick( self, caster ):
		"""
		virtual method.
		�������ܵļ����Ӧtick
		@return type: ����false����ǰ�����������
		"""

		if len( self._targetActions ):
			targetAction = self._targetActions.pop()
			#self._target.getObject().allClients.onPlayAction( targetAction )
			if targetAction == "hit_c_1":
				direction = Math.Vector3( self._target.getObject().position ) - Math.Vector3( caster.position )
				direction.normalise()
				targetPos = self._target.getObject().position + direction * 2.0
				self._target.getObject().lineToPoint( targetPos, 3.5, False )
			elif targetAction in ["hit_b_1", "hit_b_2"] and not VehicleHelper.getCurrVehicleID( caster ):
				direction = Math.Vector3( self._target.getObject().position - caster.position )
				direction.normalise()
				targetPos = self._target.getObject().position + direction * 2
				self._target.getObject().lineToPoint( targetPos, 4.0, False )


		if len( self._casterActions ):
			casterAction = self._casterActions.pop()
			if VehicleHelper.getCurrVehicleID( caster ):
				casterAction = "ride_" + casterAction
			#caster.allClients.onPlayAction( casterAction )

			if casterAction in ["swordman_combo01_2"] and not VehicleHelper.getCurrVehicleID( caster ):
				direction = Math.Vector3( self._target.getObject().position ) - Math.Vector3( caster.position )
				direction.normalise()
				dstPos = caster.position + direction * 2.0
				print dstPos, caster, self._target.getObject()
				caster.lineToPoint( dstPos, 10.0, True )

			if casterAction in ["swordman_combo01_3", "swordman_combo01_4"] and not VehicleHelper.getCurrVehicleID( caster ):
				direction = Math.Vector3( self._target.getObject().position ) - Math.Vector3( caster.position )
				direction.normalise()
				dstPos = caster.position + direction * 1.5
				print dstPos, caster, self._target.getObject()
				caster.lineToPoint( dstPos, 4.0, True )

		return ActiveHomingSpell.onTick( self, caster )

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{ "param": None }������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : {	"endTime" : self._endTime,
								"tickInterval" : self._tickInterval,
								"target" : self._target,
								"childSpellIDs": list( self._childSpellIDs ),
								"castActions" : list( self._casterActions ),
								"targetActions" : list( self._targetActions ) } }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = self.__class__()
		obj.__dict__.update( self.__dict__ )

		obj._endTime = data["param"][ "endTime" ]
		obj._tickIntervalCopy = list( data["param"][ "tickInterval" ] )
		obj._target = data["param"][ "target" ]
		obj._childSpellIDsCopy = data["param"][ "childSpellIDs" ]
		obj._casterActions = data["param"][ "castActions" ]
		obj._targetActions = data["param"][ "targetActions" ]

		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj


# -*- coding: gb18030 -*-
# --------------------------------------------------------------------
# ���Ըı������
# ��Ҫ���ѷ����ı������ȫ���ȷŵ��������У��ɹ�����ͳһ����ı�ֵ��
# �������Ըı���Ϣ��
#
# ���˼·��
# �ڷ������������ڡ���װ����������Ϊ���Ȱ�װ�����������ٴ��ϣ���������
# �����ϵı仯�������ֱ仯���Բ��ǲ߻���Ҫ�ġ�������Ҫ��ʾ�����������
# �̵ܶ�һ��ʱ�������ڣ���0.1�룩�ж�εĸı䣬 ���ǿ���Ϊ������ı��
# ��������ͬһ����Ϊ������ġ����ڴ����������ǿ����ڿͻ��˲���һ������
# ������ֵ�ı�Ĺ������� ��set_xxx()�����յ���ص���ֵ�ı�ʱ�ӵ������
# �����У��ɹ�����ͳһȥ���㲢ִ����ʾ��
# written by gjx 2009-5-15
# --------------------------------------------------------------------

from ChatFacade import chatFacade
from AbstractTemplates import Singleton
import csstatus
import BigWorld

# ���б���������ʾ����˳��
showOrder = [ "HP_Max", "MP_Max", "PHYSICS_DMG", "PHYSICS_ARMOR", "MAGIC_DMG", "MAGIC_ARMOR" ]

# ���Ա仯��ϢID
attrMaps = {
			"HP_Max_INC" : csstatus.ROLE_ATTR_HP_MAX_INC,				"HP_Max_DEC" : csstatus.ROLE_ATTR_HP_MAX_DEC,
			"MP_Max_INC" : csstatus.ROLE_ATTR_MP_MAX_INC,				"MP_Max_DEC" : csstatus.ROLE_ATTR_MP_MAX_DEC,
			"PHYSICS_DMG_INC" : csstatus.ROLE_ATTR_PHYSICS_DMG_INC,		"PHYSICS_DMG_DEC" : csstatus.ROLE_ATTR_PHYSICS_DMG_DEC,
			"PHYSICS_ARMOR_INC" : csstatus.ROLE_ATTR_PHYSICS_ARMOR_INC, "PHYSICS_ARMOR_DEC" : csstatus.ROLE_ATTR_PHYSICS_ARMOR_DEC,
			"MAGIC_DMG_INC" : csstatus.ROLE_ATTR_MAGIC_DMG_INC,			"MAGIC_DMG_DEC" : csstatus.ROLE_ATTR_MAGIC_DMG_DEC,
			"MAGIC_ARMOR_INC" : csstatus.ROLE_ATTR_MAGIC_ARMOR_INC,		"MAGIC_ARMOR_DEC" : csstatus.ROLE_ATTR_MAGIC_ARMOR_DEC,
			}


class AttrChangeMgr( Singleton ) :

	_tmp_time = 0.2								# �ڴ�ʱ��ν��յ�����ͬ���Ըı����Ϣ
												# ����Ϊͬһ�β������͵���Ϣ��
	def __init__( self ) :
		self.__attrChangeValue = {}				# { attrName: [ oldValue, newValue ] }


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def deliverAttrMsg( self, attrName, value ) :
		"""
		�������Ըı���Ϣ
		@param		attrName	: ��������
		@param		value		: ���Ըı�ֵ
		return		None
		"""
		if self.__attrChangeValue.has_key( attrName ) :
			self.__attrChangeValue[attrName][1] = value[1]
		else :
			if self.__attrChangeValue == {} :
				BigWorld.callback( self._tmp_time, self.__delayFire )
			self.__attrChangeValue[attrName] = value


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __delayFire( self ) :
		"""
		��ʱʱ�䵽ʱ,���ն����˳�������Ըı���Ϣ
		"""
		for attrName in showOrder :
			value = self.__attrChangeValue.get( attrName, [0,0] )
			value = int( value[1] ) - int( value[0] )				# �ü��㷽����Ϊ���������ʾ����һ��
			self.__fireMsg( attrName, value )
		self.__attrChangeValue = {}

	def __fireMsg( self, attrName, value ) :
		"""
		��ʱ���ͺ���,ֻ������ֵ�����˸ı�ŷ�����Ϣ
		"""
		if value > 0 :
			attrName += "_INC"
		elif value < 0 :
			attrName += "_DEC"
			value = -value
		else :
			return
		statusID = attrMaps[attrName]
		chatFacade.rcvStatusMsg( statusID, value )


attrChangeMgr = AttrChangeMgr()
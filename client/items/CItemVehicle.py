# -*- coding: gb18030 -*-

from CItemBase import CItemBase
import ItemAttrClass
import ItemTypeEnum
from config.client.labels.items import lbs_EquipEffects,lbs_vehicle
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
import time

class CItemVehicle( CItemBase ):
	"""
	����ʯ/��ͨ��走
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )
		
	def getProDescription( self, reference ):
		"""
		virtual method
		��ȡ��走ר��������Ϣ
		"""
		CItemBase.getProDescription( self, reference )
		if self.getType() != ItemTypeEnum.ITEM_VEHICLE_TURN:		#��ͨ����走
			return
		desPot = "%s %s"%( lbs_vehicle[1], self.query( "param4", 0 ) )	#�ɳ���
		desPot += PL_NewLine.getSource()
		
		desPot += "%s+%s"%( lbs_EquipEffects[3], self.query( "param5", 0 ) )	#����
		desPot += PL_NewLine.getSource()
		
		desPot += "%s+%s"%( lbs_EquipEffects[4], self.query( "param7", 0 ) )	#����
		desPot += PL_NewLine.getSource()
		
		desPot += "%s+%s"%( lbs_EquipEffects[3], self.query( "param6", 0 ) )	#����
		desPot += PL_NewLine.getSource()
		
		desPot += "%s+%s"%( lbs_EquipEffects[3], self.query( "param8", 0 ) )	#����
		desPot += PL_NewLine.getSource()
		
		fullDegree = int( self.query( "param3",0 ) )
		
		days = int ( ( fullDegree - time.time() )/( 24*60*60 ) )
		if days < 0:days = 0
		
		desPot += "%s %s%s"%( lbs_vehicle[2], days, lbs_vehicle[3] )		#������
		self.desFrame.SetDescription( "eq_extraEffect", desPot )
		
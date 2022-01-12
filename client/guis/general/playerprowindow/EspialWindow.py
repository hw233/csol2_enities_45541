# -*- coding: gb18030 -*-
#
# $Id: EspialWindow.py,v 1.00 2008/09/6 11:19:09 huangdong Exp $

import GUIFacade
import csdefine
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.Button import Button
from guis.controls.ComboBox import ComboBox
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from TargetModelRender import TargetModelRender
from TargetEquipItem import TargetEquipItem
from PropertyItem import PropertyItem
from ResistItem import ResistItem
import ItemTypeEnum as ItemType
import event.EventCenter as ECenter
import ItemTypeEnum
from ItemsFactory import ObjectItem as ItemInfo
from EspialTarget import espial
import Const

class EspialWindow( Window ):
	"""
	�۲�Է�,��ʾ�Է������UI
	"""
	__cc_itemMaps = {
	0 : ( ItemType.CEL_HEAD, labelGather.getText( "PlayerProperty:EquipPanel", "cel_head" ) ), 			# heah
	1 : ( ItemType.CEL_BODY, labelGather.getText( "PlayerProperty:EquipPanel", "cel_body" ) ), 			# jacket
	2 : ( ItemType.CEL_VOLA, labelGather.getText( "PlayerProperty:EquipPanel", "cel_vola" ) ), 			# glove
	3 : ( ItemType.CEL_RIGHTFINGER, labelGather.getText( "PlayerProperty:EquipPanel", "cel_rightfinger" ) ),	# right finger
	4 : ( ItemType.CEL_BREECH, labelGather.getText( "PlayerProperty:EquipPanel", "cel_breech" ) ), 		# trousers
#	5 : ( ItemType.CEL_TALISMAN, labelGather.getText( "PlayerProperty:EquipPanel", "cel_talisman" ) ),	 	# candidate
	6 : ( ItemType.CEL_RIGHTHAND, labelGather.getText( "PlayerProperty:EquipPanel", "cel_tighthand" ) ), 	# right hand
	7 : ( ItemType.CEL_NECK, labelGather.getText( "PlayerProperty:EquipPanel", "cel_neck" ) ),			# necklace
	8 : ( ItemType.CEL_HAUNCH, labelGather.getText( "PlayerProperty:EquipPanel", "cel_haunch" ) ), 		# haunch
	9 : ( ItemType.CEL_CUFF, labelGather.getText( "PlayerProperty:EquipPanel", "cel_cuff" ) ), 			# cuff;
	10 : ( ItemType.CEL_LEFTFINGER, labelGather.getText( "PlayerProperty:EquipPanel", "cel_leftfinger" ) ),	# left finger
	11 : ( ItemType.CEL_FEET, labelGather.getText( "PlayerProperty:EquipPanel", "cel_feet" ) ),			# shoes
	12 : ( ItemType.CEL_CIMELIA,labelGather.getText( "PlayerProperty:EquipPanel", "cel_cimelia" ) ),		# cimelia
	13 : ( ItemType.CEL_LEFTHAND, labelGather.getText( "PlayerProperty:EquipPanel", "cel_lefthand" ) ),		# left hand
	14: ( ItemType.CEL_POTENTIAL_BOOK, labelGather.getText( "PlayerProperty:EquipPanel", "cel_potential_book" ) ),	# fashion1
	15: ( ItemType.CEL_FASHION1, labelGather.getText( "PlayerProperty:EquipPanel", "cel_fashion1" ) )		# fashion1
	}
	def __init__( self ):
		"""
		��ʼ��UI
		"""
		wnd = GUI.load( "guis/general/playerprowindow/espialwindow.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_	= True
		self.target     = None
		self.__isEspFashion		= False				#�Ƿ������۲�ʱװ

		self.__triggers = {}	#ע����Ϣ
		self.__pyItems = {}		#װ���ؼ�
		self.__pyRichItems = {}	#��ʾ���ԵĿؼ�
		self.__turnModelCBID = 0    # ��תģ�͵� callback ID
		self.__registerTriggers()	#ע����Ϣ
		self.__initialize( wnd )	#��ʼ��UI��ITEMS


	def __registerTriggers( self ):
		"""
		ע����Ϣ
		"""
		self.__triggers["EVT_ON_ROLE_SHOW_TARGET_EQUIP"]	 = self.__onUpdateEquipItem		#��ʾ�Է����װ��
		self.__triggers["EVT_ON_ROLE_SHOW_TARGET_TFINFO"] 	 = self.__onUpdateOtherinfo		#��ʾ�Է���ҵİ��;���,�ȼ����ֵ���Ϣ
		self.__triggers["EVT_ON_ROLE_SHWO_TARGET_MODEL"]	 = self.__onUpdataModel			#��ʾ�Է���ҵ�ģ��
		self.__triggers["EVT_ON_ESPIAL_TARGET_FASHIONNUM_CHANGE"] = self.__onUpdataModel
		self.__triggers["EVT_ON_SHOW_TARGET"]			 	 = self.show					#��ʾ����
		self.__triggers["EVT_ON_END_SHOW_TARGET"]			 = self.__hide					#�رմ���

		for key in self.__triggers :
			ECenter.registerEvent( key, self )


	def	__initialize(self, wnd):
		"""
		��ʼ���ؼ�
		@param   wnd: ��ʾװ����gui�ϵ�section����
		@type    wnd: section
		"""
		labelGather.setLabel( wnd.lbTitle, "PlayerProperty:EspialWindow", "lbTitle" )
		self.__pyLbRoleName = StaticText( wnd.lbRoleName )	#�������
		self.__pyLbRoleInfo = StaticText( wnd.lbRoleInfo )	#ְҵ�ȼ�

		self.__pyRightBtn = Button( wnd.btnRight )			#����ת
		self.__pyRightBtn.setStatesMapping( UIState.MODE_R1C4 )
		self.__pyRightBtn.onLMouseDown.bind( self.__turnRight )

		self.__pyLeftBtn = Button( wnd.btnLeft )
		self.__pyLeftBtn.setStatesMapping( UIState.MODE_R1C4 )	#����ת
		self.__pyLeftBtn.onLMouseDown.bind( self.__turnLeft )

		self.__pyFashBtn = Button( wnd.btnFashion )			#ʱװ��
		self.__pyFashBtn.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyFashBtn, "PlayerProperty:EquipPanel", "btnFashion" )
		self.__pyFashBtn.onLMouseDown.bind( self.__changeFashion )

		self.__modelRender = TargetModelRender( wnd.modelRender )#��Ⱦ����Ŀ�
		self.__initItems( wnd )	#��ʼ����ҵ���Ϣ
		
		labelGather.setLabel( wnd.baseTitle.stTitle,"PlayerProperty:EquipPanel", "baseTitle" )
		labelGather.setLabel( wnd.privyTitle.stTitle,"PlayerProperty:EquipPanel", "privyTitle" )
		labelGather.setLabel( wnd.physTitle.stTitle,"PlayerProperty:EquipPanel", "physTitle" )
		labelGather.setLabel( wnd.magicTitle.stTitle,"PlayerProperty:EquipPanel", "magicTitle" )

	def __initItems( self, wnd ):
		"""
		��ʼ����ҵ���Ϣ
		װ����Ҫʹ��ItemsFactory�ļ��ϵ�ItemInfo���װһ�� �������ܱ�BOItem������
		@param   wnd: ��ʾװ����gui�ϵ�section����
		@type    wnd: section
		"""
		for name, item in wnd.children :			# ��ʼ�����װ����Ϣ
			if "eqItem_" in name:
				index = int( name.split( "_" )[1] )

				mapIndex, itemName = self.__cc_itemMaps[index]	#��ȡ��װ������λ�ú�����
				pyItem = TargetEquipItem( item , itemName)	#����װ�����ӿؼ�
				self.__pyItems[mapIndex] = pyItem	# ������װ��������ֵ���
			elif "rich_" in name:					# ��ʼ�����������Ϣ
				tag = name.split( "_" )[1]
				pyItem = PropertyItem( tag, item, False )
				pyItem.tag = tag
				self.__pyRichItems[tag] = pyItem
			else:
				continue

	def __onUpdateEquipItem( self, itemInfos ):
		"""
		����װ����
		@param   itemInfos: װ�����б�
		@type    itemInfos: ObjectItem(ItemInfo)��LIST
		"""
		for itemInfo in itemInfos:
			index = itemInfo.orderID
			if self.__pyItems.has_key( index ):
				if itemInfo.query("type") == ItemTypeEnum.ITEM_WEAPON_TWOSWORD:
					self.__pyItems[7].update( itemInfo,BigWorld.player() )
					self.__pyItems[8].update( itemInfo,self.BigWorld.player() )
				else:
					self.__pyItems[index].update( itemInfo,BigWorld.player() )

	def __onUpdateOtherinfo( self, otherInfo):
		"""
		��ʾ��ҵĵȼ� ������Ϣ
		@param   otherInfo: �洢��Ϣ���ֵ�
		@type    otherInfo: dictionary
		"""
		self.__pyLbRoleName.text = otherInfo["Name"]
		roleInfo = labelGather.getText( "PlayerProperty:EspialWindow", "roleInfo" )%( otherInfo["Level"], otherInfo["Pclass"] )
		self.__pyLbRoleInfo.text = roleInfo
		tongName = otherInfo["TongName"]

	def __onUpdataModel(self, target):
		"""
		��ʾ�Է���ҵ�ģ��
		@param   target: �Է���ҵ�entity
		@type    target: ROLE
		"""
		fashionNum = target.fashionNum
		self.__modelRender.resetModel( target, fashionNum )
		self.__isEspFashion = fashionNum > 0
		if fashionNum > 0:
			labelGather.setPyBgLabel( self.__pyFashBtn, "PlayerProperty:EquipPanel", "btnEquip" )
		else:
			labelGather.setPyBgLabel( self.__pyFashBtn, "PlayerProperty:EquipPanel", "btnFashion" )

	def allClear(self ):
		"""
		������еĿؼ���ֵ
		"""
		for key in self.__pyItems:
			self.__pyItems[key].clear()
		self.__pyLbRoleInfo.text = ""
		self.__pyLbRoleName.text = ""

	# -----------------------------------------------------------------
	def __onLastKeyUpEvent( self, key, mods ) :
		if key != KEY_LEFTMOUSE : return
		BigWorld.cancelCallback( self.__turnModelCBID )
		LastKeyUpEvent.detach( self.__onLastKeyUpEvent )

	def __turnRight( self ):
		"""
		����ģ������ת
		"""
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( True )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __turnLeft( self ):
		"""
		����ģ������ת
		"""
		BigWorld.cancelCallback( self.__turnModelCBID )
		self.__turnModel( False )
		LastKeyUpEvent.attach( self.__onLastKeyUpEvent )
		return True

	def __turnModel( self, isRTurn ) :
		"""
		turning model on the mirror
		"""
		self.__modelRender.yaw += ( isRTurn and -0.1 or 0.1 )
		if BigWorld.isKeyDown( KEY_LEFTMOUSE ) :
			self.__turnModelCBID = BigWorld.callback( 0.1, Functor( self.__turnModel, isRTurn ) )

	def resetModelAngle( self ) :
		"""
		turning model on the mirror
		"""
		self.__modelRender.yaw = 0
	
	def __changeFashion( self, pyBtn ):
		"""
		�л�ʱװ
		"""
		if pyBtn is None:return
		player = BigWorld.player()
		espial_id = player.espial_id				#���۲���id
		if espial_id <= 0:return
		role = BigWorld.entities.get( espial_id, None )
		if role is None:return
		fashItem = self.__pyItems[ItemType.CEL_FASHION1]
		fashionNum = role.fashionNum
		fashInfo = fashItem.itemInfo
		self.__isEspFashion =  not self.__isEspFashion
		if self.__isEspFashion:									#ʱװ��ʾ
			if fashInfo and fashionNum <= 0:					#װ������ʱװ
				baseItem = fashInfo.baseItem
				if baseItem is None:return
				fashionNum = baseItem.model()
			labelGather.setPyBgLabel( self.__pyFashBtn, "PlayerProperty:EquipPanel", "btnEquip" )
		else:													#��ͨװ����ʾ
			fashionNum = 0											
			labelGather.setPyBgLabel( self.__pyFashBtn, "PlayerProperty:EquipPanel", "btnFashion" )
		self.__modelRender.resetModel( role, fashionNum )
	
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onEnterWorld( self ) :
		self.allClear()

	def onLeaveWorld( self ) :
		self.hide()

	def show( self, target ) :
		self.target = target
		self.allClear()
		self.__modelRender.enableDrawModel()
		
		Window.show( self )

	def __hide( self ): # hide()֪ͨespial�ٷ��������е�������������������ͬһ���� --pj
		Window.hide( self )
		self.allClear()
		self.__isEspFashion = False
		self.__modelRender.disableDrawModel()

	def hide( self ):
		espial.stopEspial() # ֹͣ�۲�

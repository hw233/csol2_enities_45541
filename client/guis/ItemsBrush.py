# -*- coding: gb18030 -*-

"""
��Ʒˢʹ�õ�ǰ�������ǣ��ٶ���һ����Ʒ������������ڣ��������һ
������ת�Ƶ���һ�������ϣ�Ҳ�����κ�ʱ����� pyItem.pyTopParent
�õ���Ӧ����ͬһ������ʵ����
"""

import weakref
import BigWorld
import ItemTypeEnum
import event.EventCenter as ECenter
from bwdebug import ERROR_MSG
from Function import Functor
from VehicleHelper import isVehicleBook, isVehicleEquip

from Weaker import WeakSet
from ExtraEvents import ControlEvent
from AbstractTemplates import Singleton

CUSTOM_ITEM_TYPE_PET 		= 1
CUSTOM_ITEM_TYPE_VEHICLE 	= 2
CUSTOM_ITEM_TYPE_LVLIMIT	= 3


class ItemsBrush( Singleton ) :

	def __init__( self ) :
		self.__typesToParents = {}								# ��Ʒ���͵����ڵ�ӳ���
		self.__parentsToItems = {}								# ���ڵ���Ʒ���ӳ���
		self.__refToWindows = []								# ���ڵ��������б�

		self.__triggers = {}
		self.__registerEvents()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerEvents( self ) :
		"""
		"""
		self.__triggers["EVT_ON_PLAYER_UP_VEHICLE"] = self.__onVehicleUpdate		# �����
		self.__triggers["EVT_ON_PLAYER_DOWN_VEHICLE"] = self.__onVehicleUpdate		# �����
		self.__triggers["EVT_ON_VEHICLE_LEVEL_UPDATE"] = self.__onVehicleUpdate		# ���ȼ��ı�
		self.__triggers["EVT_ON_PET_ENTER_WORKLD"] = self.__onPetUpdate				# �ٻ�����
		self.__triggers["EVT_ON_PET_WITHDRAWED"] = self.__onPetUpdate				# �ջس���
		self.__triggers["EVT_ON_PET_LEVEL_CHANGE"] = self.__onPetUpdate				# ����ȼ��ı�
		self.__triggers["EVT_ON_ROLE_LEVEL_CHANGED"] = self.__onPlayerLevelUpdate	# ��ҵȼ��ı�
		for trigger in self.__triggers.iterkeys() :
			ECenter.registerEvent( trigger, self )

	# -------------------------------------------------
	def __onVehicleUpdate( self, *args ) :
		"""
		������͵ĵ���ˢ��
		"""
		self.__brushItems( CUSTOM_ITEM_TYPE_VEHICLE )

	def __onPetUpdate( self, *args ) :
		"""
		�������͵ĵ���ˢ��
		"""
		self.__brushItems( CUSTOM_ITEM_TYPE_PET )

	def __onPlayerLevelUpdate( self, *args ) :
		"""
		����ɫ�ȼ���صĵ���ˢ��
		"""
		self.__brushItems( CUSTOM_ITEM_TYPE_LVLIMIT )
		self.__neatenLVLimitItems()

	# -------------------------------------------------
	def __onWindowShows( self, pyWnd ) :
		"""
		�󶨵Ĵ��ڴ�ʱ����
		"""
		pyItems = self.__parentsToItems.get( id( pyWnd ) )
		if pyItems :
			for pyItem in pyItems :
				pyItem.updateUseStatus( pyItem.itemInfo.checkUseStatus() )	# ������Ʒ�Ŀ�ʹ��״̬
		elif pyItems is None :
			ERROR_MSG( "Window %s( %i ) isn't exist in the items brush!" % ( str( pyWnd ), id( pyWnd ) ) )

	def __onWindowReleases( self, parentId, weaker ) :
		"""
		�󶨵Ĵ����ͷ�ʱ����
		"""
		self.__removeWindow( parentId )
		self.__refToWindows.remove( weaker )

	# -------------------------------------------------
	def __removeWindow( self, parentId ) :
		"""
		�Ƴ���������ص�����
		"""
		pyItems = self.__parentsToItems.get( parentId )
		if pyItems is not None :
			del self.__parentsToItems[ parentId ]
		for itemType, parents in self.__typesToParents.items() :
			if parentId not in parents : continue
			parents.remove( parentId )
			if len( parents ) == 0 :
				del self.__typesToParents[ itemType ]

	# -------------------------------------------------
	def __brushItems( self, itemType ) :
		"""
		ˢ��ָ�����͵��ߵĽ������
		"""
		parents = self.__typesToParents.get( itemType )
		if parents is None : return
		for parentId in parents :
			pyItems = self.__parentsToItems.get( parentId )
			if not pyItems : continue
			pyItems = pyItems.set()										# ����ϣ��ת��Ϊ�б�
			if not pyItems[0].pyTopParent.visible : continue			# �����Ʒ���ڵĴ��ڵ�ǰ���ɼ�����ˢ��
			for pyItem in pyItems :
				if self.__convertType( pyItem ) is itemType :
					pyItem.updateUseStatus( pyItem.itemInfo.checkUseStatus() )

	def __convertType( self, pyItem ) :
		"""
		�����ߵ�����ת��Ϊ��ģ���Զ�������ͣ����磺
		������ĺ����ͳһ����Ϊ�������͵���
		"""
		baseItem = pyItem.itemInfo.baseItem
		itemType = baseItem.getType()
		if itemType in ItemTypeEnum.PET_DRUG_LIST:
				return CUSTOM_ITEM_TYPE_PET
		elif isVehicleBook( baseItem ) or isVehicleEquip( baseItem ) :
			return CUSTOM_ITEM_TYPE_VEHICLE
		elif baseItem.getReqLevel() > 1 :
			if not baseItem.queryReqClasses() or \
			BigWorld.player().getClass() in baseItem.queryReqClasses() :
				return CUSTOM_ITEM_TYPE_LVLIMIT
		return None

	# -------------------------------------------------
	def __neatenLVLimitItems( self ) :
		"""
		�����ɫ��صĵȼ�������Ʒ
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def attach( self, pyItem ) :
		"""
		�󶨵�����Ʒ����
		"""
		if pyItem.itemInfo is None :							# ��������ѱ�����
			self.detach( pyItem )								# �����Ƴ�
			return
		itemType = self.__convertType( pyItem )
		if itemType is None :									# ���������Ҫ���µĵ�������
			self.detach( pyItem )								# �����Ƴ�
			return
		# ���²����Ǳ�����Ʒ���͵����ڵ�ӳ��
		parentId = id( pyItem.pyTopParent )						# ��ȡ���ڵ�ΨһID����ʵ�����ڴ��ַ��
		parents = self.__typesToParents.get( itemType )
		if parents is None :
			self.__typesToParents[ itemType ] = set( [ parentId ] )
		else :
			parents.add( parentId )
		# ���²����Ǳ��洰�ڵ���Ʒ���ӳ��
		pyItems = self.__parentsToItems.get( parentId )
		if pyItems is None :
			showEvent = getattr( pyItem.pyTopParent, "onBeforeShow", None )
			if isinstance( showEvent, ControlEvent ) :			# �󶨴��ڴ򿪵���Ϣ���Ա��ڴ��ڴ�ʱˢ��һ��������
				showEvent.bind( self.__onWindowShows )
			self.__parentsToItems[ parentId ] = WeakSet( [ pyItem ] )
			realseCb = Functor( self.__onWindowReleases, parentId )	# �Ը�������������ã��Ա��ڴ����ͷ�ʱ�õ��ص�֪ͨ���ͷ������Դ
			self.__refToWindows.append( weakref.ref( pyItem.pyTopParent, realseCb ) )
		else :
			pyItems.add( pyItem )

	def detach( self, pyItem ) :
		"""
		�Ƴ�������Ʒ����
		"""
		parentId = id( pyItem.pyTopParent )
		pyItems = self.__parentsToItems.get( parentId )
		if pyItems is None : return
		if pyItem in pyItems :
			pyItems.remove( pyItem )							# �Ӵ��ں���Ʒ���ӳ������Ƴ�
		if len( pyItems ) == 0 :								# ����ô��ڲ�������ˢ�µ���Ʒ��
			for itemType, parents in self.__typesToParents.iteritems() :
				if parentId not in parents : continue
				parents.remove( parentId )

	def clearDataOfWindow( self, pyWnd ) :
		"""
		�ýӿ��ṩ���ⲿ���ã��ɽ�������صĵ��߸�
		�ӵ��������ݴ���Ʒˢ�����
		"""
		showEvent = getattr( pyWnd, "onBeforeShow", None )
		if isinstance( showEvent, ControlEvent ) :				# ��󴰿ڴ򿪵���Ϣ
			showEvent.unbind( self.__onWindowShows )
		self.__removeWindow( id( pyWnd ) )

	# -------------------------------------------------
	def onEvent( self, evtMacro, *args ) :
		"""
		�󶨵��¼�����ʱ����
		"""
		self.__triggers[evtMacro]( *args )


itemsBrush = ItemsBrush()


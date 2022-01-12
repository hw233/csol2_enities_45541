# -*- coding:gb18030 -*-
#
# by ganjinxing 2012-02-24
# 游戏设置管理器说明：
# 设计目标：
# 应用配置中的游戏设置方案，替换掉当前的游戏设置，
# 并可随时恢复到修改前的设置。配置可指定空间需应用的游戏设置
# 方案，当玩家进入该空间时，自动询问玩家是否应用配置方案，如
# 果玩家接受，则自动应用配置指定的方案；当玩家离开该空间时，
# 将游戏设置恢复到修改前的设置。
#
# 设计结构：
# 由两大部分组成：管理器(GameSettingMgr)和设置器(继承于SetterBase)。
# 管理器负责加载和应用游戏设置方案，设置器则负责游戏设置的具体操作。
# 可通过增加新的设置器来执行新的游戏设置项的替换和恢复操作，目前支持
# 的游戏设置项包括：
# 1、通过 BigWorld.setWatcher 来设置的游戏设置
# 2、通过 viewInfoMgr.changeSetting 来设置的游戏设置

# bigworld
import BigWorld
# common
import csstatus
import Language
from bwdebug import ERROR_MSG
# client
import Define
from MessageBox import *
from ViewInfoMgr import viewInfoMgr
# config
from config.client.msgboxtexts import Datas as mbmsgs


class GameSettingMgr :
	_inst = None

	def __init__( self ) :
		assert self.__class__._inst is None, "Invote the instance() method."
		self.__currSettingID = None							# 当前应用的配置
		self.__originSetting = {}							# 保存原始配置
		self.__customSettings = {}							# 自定义配置：{ settingID : settingSect }
		self.__spacesSettingMap = {}						# 地图对应的配置：{ spaceLabel : settingID }

	@classmethod
	def instance( CLS ) :
		if CLS._inst is None :
			CLS._inst = CLS()
		return CLS._inst

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def initSettings( self, cfgPath = "" ) :
		"""
		"""
		if cfgPath == "" :
			cfgPath = "config/client/CustomGameSetting.xml"
		sect = Language.openConfigSection( cfgPath )
		if sect is None :
			ERROR_MSG( "Open %s failed!" % cfgPath )
			return
		for sSect in sect.values() :
			settingID = sSect.asInt
			self.__customSettings[ settingID ] = sSect["options"]
			spacesLabel = sSect["spaces"].readStrings( "item" )
			for spaceLabel in spacesLabel :
				self.__spacesSettingMap[ spaceLabel ] = settingID
		Language.purgeConfig( cfgPath )

	def onPlayerEnterSpace( self ) :
		"""
		玩家进入某个空间
		注意：玩家刚进入一个空间时，调用getSpaceLabel得到的是None，
		所以要延时一下再做判断
		"""
		BigWorld.callback( 3.0, self.useCurrentSpaceSetting )

	def onPlayerLeaveSpace( self ) :
		"""
		玩家离开某个空间
		"""
		spaceLabel = BigWorld.player().getSpaceLabel()
		if self.spaceHasCustomSetting( spaceLabel ) :
			self.recoverSetting( self.getSpaceSettingID( spaceLabel ) )

	def onPlayerOffline( self ) :
		"""
		玩家掉线
		"""
		self.recoverCurrentSetting()

	# -------------------------------------------------
	# 功能实现方法
	# -------------------------------------------------
	def useCurrentSpaceSetting( self ) :
		"""
		应用当前空间的配置
		"""
		spaceLabel = BigWorld.player().getSpaceLabel()
		self.useSpaceSetting( spaceLabel )

	def useSpaceSetting( self, spaceLabel ) :
		"""
		应用指定空间的配置
		"""
		settingID = self.getSpaceSettingID( spaceLabel )
		if settingID is not None :
			self.useSettingByID( settingID )

	def useSettingByID( self, settingID, needConfirm = True ) :
		"""
		应用指定ID的配置
		"""
		self.recoverCurrentSetting()									# 同一时间只能应用一套配置，所以先把当前的应用恢复
		appSetting = self.__getApplicableOptions( settingID )
		if len( appSetting ) == 0 :
			return
		if needConfirm :
			def confirmCallback( res ) :
				if res == RS_OK :
					self.__applySetting( settingID )
			#appContent = "\n" + self.__formatContents( [ s.readString("content") for s in appSetting ] )
			#msg = mbmsgs[0x0f00] % appContent
			showMessage( mbmsgs[0x0f00], "", MB_OK_CANCEL, confirmCallback, gstStatus = Define.GST_IN_WORLD )
		else :
			self.__applySetting( settingID )

	def spaceHasCustomSetting( self, spaceLabel ) :
		"""
		检查地图是否存在自定义的游戏配置
		"""
		return self.__spacesSettingMap.has_key( spaceLabel )

	def getSpaceSettingID( self, spaceLabel ) :
		"""
		获取空间的自定义游戏配置
		"""
		return self.__spacesSettingMap.get( spaceLabel )

	def hasSetting( self, settingID ) :
		"""
		检查是否存在某个ID对应的配置
		"""
		return self.__customSettings.has_key( settingID )

	def getCurrentSettingID( self ) :
		"""
		返回当前的配置ID
		"""
		return self.__currSettingID

	def recoverCurrentSetting( self ) :
		"""
		恢复正在应用的配置为应用前的配置
		"""
		self.recoverSetting( self.__currSettingID )

	def recoverSetting( self, settingID ) :
		"""
		恢复正在应用的配置为应用前的配置
		"""
		if self.__currSettingID and self.__currSettingID == settingID :
			self.__recoverSetting( settingID )
			self.__currSettingID = None
			self.__originSetting.clear()

	def clear( self ) :
		"""
		清空所有数据
		"""
		self.recoverCurrentSetting()
		self.__customSettings.clear()
		self.__spacesSettingMap.clear()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __formatContents( self, contents ) :
		"""
		格式化表示修改内容的文本
		"""
		return "\n".join( contents )

	def __buildSetter( self, optionSect ) :
		"""
		创建设置配置的实例
		"""
		setterClass = SETTER_MAP.get( optionSect.readString( "script" ) )
		if setterClass is None :
			ERROR_MSG( "Setter %s is not existed!" % optionSect.readString( "script" ) )
			return None
		return setterClass.inst()

	def __getApplicableOptions( self, settingID ) :
		"""
		获取需应用的配置
		"""
		result = []
		settingSect = self.__customSettings.get( settingID )
		if settingSect is None :
			ERROR_MSG( "Game setting %i is not existed!" % settingID )
			return result 											# []
		for optionSect in settingSect.values() :
			setter = self.__buildSetter( optionSect )
			if setter and setter.applyCheckout( optionSect ) :		# 检查是否需要应用此配置
				result.append( optionSect )							# 把可应用项添加到列表
		return result

	def __applySetting( self, settingID ) :
		"""
		应用配置
		"""
		settingSect = self.__customSettings.get( settingID )
		if settingSect is None :
			ERROR_MSG( "Game setting %i is not existed!" % settingID )
			return
		#appContents = []
		for optionSect in settingSect.values() :
			setter = self.__buildSetter( optionSect )
			if setter and setter.applyCheckout( optionSect ) :		# 检查是否需要应用此配置
				origin = setter.apply( optionSect )
				self.__originSetting[ optionSect.asString ] = origin
		#		appContents.append( optionSect.readString("content") )
		self.__currSettingID = settingID
		#argStr = "\n" + self.__formatContents( appContents )
		#BigWorld.player().statusMessage( csstatus.GAME_SETTING_MGR_APPLY_REPORT, argStr )

	def __recoverSetting( self, settingID ) :
		"""
		恢复到之前的配置
		"""
		settingSect = self.__customSettings.get( settingID )
		if settingSect is None :
			ERROR_MSG( "Game setting %i is not existed!" % settingID )
			return
		for optionSect in settingSect.values() :
			origin = self.__originSetting.get( optionSect.asString )
			if origin is None :
				continue
			setter = self.__buildSetter( optionSect )
			if setter and setter.revertCheckout( optionSect ) :		# 检查是否需要恢复此配置
				setter.revert( optionSect, origin )


gameSettingMgr = GameSettingMgr.instance()


# --------------------------------------------------------------------
# setters
# --------------------------------------------------------------------
class SetterBase :
	__insts = {}

	def __init__( self ) :
		assert SetterBase.__insts.get( self.__class__ ) is None,\
			"Please invoke the class method inst to get instance."
		SetterBase.__insts[self.__class__] = self

	@classmethod
	def inst( CLS ) :
		if not CLS.__insts.has_key( CLS ) :
			CLS.__insts[CLS] = CLS()
		return CLS.__insts[CLS]

	@staticmethod
	def translateValue( vType, value ) :
		"""
		根据指定的数据类型，将字符串转换为对应的值
		"""
		if type( value ) is vType :
			return value
		elif vType is bool :
			return eval( value.capitalize() )
		else :
			return vType( value )

	def apply( self, optionSect ) :
		"""
		应用设定到游戏
		"""
		pass

	def revert( self, optionSect, origin ) :
		"""
		恢复设置
		"""
		pass

	def parse( self, optionSect ) :
		"""
		将配置解释为实际需要的数据
		"""
		pass

	def compare( self, optionSect ) :
		"""
		将当前值和设置值进行对比，相同则返回0，小则返回-1，大则返回1
		"""
		return 0

	def applyCheckout( self, optionSect ) :
		"""
		检查是否需要应用该配置，默认情况下，如果当前配置大于或者等于
		预设置的值，则不需要修改。
		"""
		return self.compare( optionSect ) == -1

	def revertCheckout( self, optionSect ) :
		"""
		检查是否需要恢复该配置，默认情况下，如果当前配置等于预设置的值，
		则需要恢复到修改前的值。
		"""
		return self.compare( optionSect ) == 0


class SetterWatcher( SetterBase ) :
	"""
	通过调用BigWorld.setWatcher进行设置的配置
	"""
	_SETTING_MAP = {
		"max_particles_count" : "Chunks/Particles Lod/MAX pixie count",		# 最大粒子数量
		"particles_distance" : "Chunks/Particles Lod/Distance",				# 粒子最大可视距离
	}

	def apply( self, optionSect ) :
		"""
		应用设定到游戏
		"""
		label, value, vType = self.parse( optionSect )
		origin = BigWorld.getWatcher( label )
		BigWorld.setWatcher( label, value )
		return SetterBase.translateValue( vType, origin )					# 返回设置前的值

	def revert( self, optionSect, origin ) :
		"""
		恢复设置
		"""
		label, value = self.parse( optionSect )[:2]
		if origin != value :
			BigWorld.setWatcher( label, origin )

	def parse( self, optionSect ) :
		"""
		将配置解释为实际需要的数据
		"""
		label = SetterWatcher._SETTING_MAP.get( optionSect.asString )
		vType = eval( optionSect.readString( "type" ) )
		value = optionSect.readString( "value" )
		value = SetterBase.translateValue( vType, value )
		return ( label, value, vType )

	def compare( self, optionSect ) :
		"""
		将当前值和设置值进行对比，相同则返回0，小则返回-1，大则返回1
		"""
		label, value, vType = self.parse( optionSect )
		current = BigWorld.getWatcher( label )
		current = SetterBase.translateValue( vType, current )
		return cmp( current, value )


class SetterViewInfo( SetterBase ) :
	"""
	通过调用viewInfoMgr.changeSetting进行设置的配置
	"""
	def apply( self, optionSect ) :
		"""
		应用设定到游戏
		"""
		infoKey, itemKey, value, vType = self.parse( optionSect )
		origin = viewInfoMgr.getSetting( infoKey, itemKey )
		viewInfoMgr.changeSetting( infoKey, itemKey, value )
		return SetterBase.translateValue( vType, origin )

	def revert( self, optionSect, origin ) :
		"""
		恢复设置
		"""
		infoKey, itemKey, value = self.parse( optionSect )[:3]
		if origin != value :
			viewInfoMgr.changeSetting( infoKey, itemKey, origin )

	def parse( self, optionSect ) :
		"""
		将配置解释为实际需要的数据
		"""
		infoKey, itemKey = optionSect.asString.split( "_" )
		vType = eval( optionSect.readString( "type" ) )
		value = optionSect.readString( "value" )
		value = SetterBase.translateValue( vType, value )
		return ( infoKey, itemKey, value, vType )

	def compare( self, optionSect ) :
		"""
		将当前值和设置值进行对比，相同则返回0，小则返回-1，大则返回1
		"""
		infoKey, itemKey, value, vType = self.parse( optionSect )
		current = viewInfoMgr.getSetting( infoKey, itemKey )
		return cmp( current, value )


SETTER_MAP = {
	"watcher"	: SetterWatcher,
	"viewinfo"	: SetterViewInfo,
}

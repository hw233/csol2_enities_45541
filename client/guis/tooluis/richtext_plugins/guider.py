#
# -*- coding: gb18030 -*-
# $Id: guider.py,v 1.2 2008-08-19 09:33:02 huangyongwei Exp $
#

"""
2008.05.14: writen by huangyongwei
"""

"""
插件编写注意事项说明：
一、插件目录
	① 目前默认的插件目录是：guis/tooluis/richtext_plugins
	② 可以自定义插件目录，实现 RichText 使用多组不同解释的插件。
	   自定义目录的方法是：调用 RichText 的 setPluginsPath 方法，将新目录作为参数传入。
	   如：rt = RichText()
		   rt.setPluginsPath( 插件路径 )
	   则，rt 将采用新的插件组来格式化它的文本。

二、插件命名规定
	所有插件模块名称必须以 “PL_” 开头

三、插件类
	① 所有插件必须继承于 guis.controls.RichText::BasePlugin
	② 所有插件必须在构造函数中设置自己的“esc_”属性为一个非空转义字符串，一般为某个特殊字符开头，然后接着一个字母
	③ 所有插件必须重写基类的两个方法，并提供一个获取格式化文本的静态方法：
	   第一个方法为 format，该方法负责将自己的转义字符下囊括的文本转义成自己可识别的属性信息，定义如下：
	   format( self, pyRichText, text )
	   该方法有两个参数:
			pyRichText : 请求解释文本的 RichText 控件
			text	   : 自己的转义字符下囊括的文本
			返回值	   : 返回值是一个 tuple，其第一个元素为，让以下 transform 方法可识别的各种属性信息（attrInfo）
						 第二个参数是，插件自己获取完格式化文本后的剩余文本，这些文本返回后将被 RichText 作为普通文本直接显示
						 如果格式化失败，第一个元素可以为 None，则第二个参数可以将原来传入的 text 原样返回
						 倘若用户想将格式化标记和格式化文本（括号以内的格式化内容）忽略，则可以将 text 截掉这些文本后再作为第二个元素返回
	   注意：倘若返回值的第一个元素为 None，则当粘贴文本时，下面的 transform 函数将不会被调用

	   第二个方法为 transform，该方法在 RichText 逐步粘贴文本时被调用。可以在该方法中使用 RichText 的各个 API 实现往 RichText 中粘贴 UI 元素。
	   transform( self, pyRichText, attrInfo )
			pyRichText : 请求粘贴文本信息的 RichText 控件
			attrInfo   : 该参数即为 format 返回值中的第一个元素，用可以通过这个参数来设置自己要插入 UI 元素的属性
			返回值	   : 该方法没有返回值

	   第三个方法为 getSource，该方法主是通过传入属性值，给使用 RichText 的用户提供本插件相关的格式化文本
	   @statckmethod
	   getSource( ... )
			参数	   : 该方法的参数不固定，根据不同插件的格式化属性而定

	④ 实现原理：format 法主要负责以插件来解释文本，然后将解释后的属性信息和剩余与插件无关的文本原样返回给 RichText，RichText 将会把这些信息
	   保存到一个列表中，待到所有文本被解释完毕，RichText 将会循环释放这个链表中的每个元素，并根据每个元素对应的格式化转义字符，调用相关的插
	   件中 transform 方法。这样用户只要在 transform 方法中根据自己以 format 格式化出来的属性，往 RichText 中粘贴自己想要的 UI 元素。这样则可
	   通过插件的方式自由地控制 RichText 的文本解释方式

四、RichText 插件 API
	1、RcihText 提供的一系列专给插件使用的 API：
	① getCurrLineWidth__()
		该方法是在 RichText 将要粘贴当前行 UI 元素时，获取当前粘贴到的行的宽度。

	② getCurrLineHeight__()
		该方法是在 RichText 将要粘贴当前行 UI 元素时，获取当前行的高度（即当前行中所有 UI 元素中高度最大的元素的高度值）

	④ getCurrLineSpace__()
		该方法是在 RichText 将要粘贴当前行 UI 元素时，获取当前行的剩余宽度。这样，则意味着：
		getCurrLineSpace__() + getCurrLineWidth__() == pyRichText.maxWidth

	⑤ isNewLine__()
		该方法判断在粘贴 UI 元素时，当前是否处于新起一行状态

	⑥ setTmpAlign__( mode )
		该方法设置从当前开始，后面所有将要粘贴的 UI 元素的水平对齐模式：“L”：靠左；“C”：居中；“R”：靠右

	⑦ addElement__( pyElem )
		往 RichText 将要粘贴的行元素中添加一个 UI 元素，pyElem 为 python ui

	⑧ paintCurrLine__()
		调用该方法则可将 RichText 当前在缓冲中的还没有粘贴的行元素，进行粘贴，并另起一行。

	⑨ newLine__( n = 1 )
		调用该方法可以另起一行，即插入 n 个空行，n 必须大于或等于 1
		注：调用该方法插入空行之前，不需要首先调用 paintCurrLine__ 方法

	⑩ setTemp__( key, value, added = True )
		该方法主要为插件用户往 RichText 身上绑定一个属性，这主要用于有关联的两个或多个插件之间的参数传递
		例如：当插件一 A1 解释出一个 RichText 无法识别的属性: k = v 时，则 A1 可以通过 pyRichText.setTemp__( k, v ) 设置一个临时属性给
			  它要传递到的另一个插件 A2 用，当 A2 在实现 transform 函数时，需要提取 k 来获得 v：pyRichText.getTemp__( k )
		key		: 临时变量的键
		value	: 临时变量的键值
		added	: 如果该 key 不存在，是否添加
		返回	: 如果 added 为 True，则总是返回 True，表示设置成功；如果 added 为 False，则如果 key 已经存在，设置 key 为新的 value 值
				  否则不做任何事情返回 False，表示设置失败。

	①① getTemp__( key, default = None )
		获取一个临时变量值，如果该变量的 key 不存在，则返回 default

	①② removeTemp__( key )
		该方法删除 RichText 中一个临时变量，如果该变量的 key 存在，则删除该变量返回 True，否则返回 False


	2、RcihText 提供的给插件使用的属性：
	tmpOuter__.font			当前粘贴中的字体，可以用它作插件解释失败后的默认字体，也可以设置它，使得 RichText 此后都用该字体
	tmpOuter__.fontSize		当前粘贴中的文本字体大小
	tmpOuter__.fcolor		当前粘贴中的前景色，可以用它作插件解释失败后的默认前景色，也可以设置它，使得 RichText 此后都用该前景色
	tmpOuter__.bcolor		当前粘贴中的背景色，可以用它作插件解释失败后的默认背景色，也可以设置它，使得 RichText 此后都用该背景色
	tmpOuter__.blob			当前粘贴中的文本是否是粗体
	tmpOuter__.italic		当前粘贴中的文本是否是斜体
	tmpOuter__.underline	当前粘贴中的文本是否有下划线
	tmpOuter__.strokeOut	当前粘贴中的文本是否有删除线

五、注意事项
	不要在 transform 中设置 RichText 的各种属性，和设置性的非插件友元函数（即没有 "__" 结尾的方法）。当然，可以获取 RichText 的属性值


"""
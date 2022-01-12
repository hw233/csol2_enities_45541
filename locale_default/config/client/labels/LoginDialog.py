# -*- coding: UTF-8 -*-

# 主窗口
main = {
	'stAccount': { 'color':( 255, 254, 168 ), 'text': "账号:" },
	'stPasswd': { 'color':( 255, 254, 168 ), 'text': "密码:" },
	'cbRem': { 'text': "记住" },

	'rbTel': { 'color': 0x90ff24, 'text': "使用电话" },
	'rbCard': { 'color': 0x90ff24, 'text': "使用密保卡" },
	'btnTel': { 'color': 0xFFF89E, 'text': "绑定电话密保" },
	'btnCard': { 'color': 0xFFF89E, 'text': "绑定密保卡" },
	'rtTips': { 'text': "@F{fc=ffffff}已开通电话密保的用户，请拨打@F{fc=01DB1F}免费电话：@B@F{fc=fef375;n=system_small.font}400-618-9132  400-811-8801@F{fc=ffffff}  拨打以上空闲号码，您将更快通过验证。" },
	'rbMajor': { 'text': "我已成年" },
	'rbMinor': { 'text': "我还未成年" },
	'btnQuit': { 'text': "退出游戏" },
	'btnEnter': { 'color' : (252.0, 235.0, 179.0), 'text': "进入游戏" },
	'btnReg': { 'text': "账号注册" },
	'btnCharge': { 'text': "账号充值" },
	'btnBack': { 'text': "上一步" },
	"rtAgeWarn": { 'text': "@F{fc=fef375}适龄提示：适合12岁以上玩家使用" },
	}

# 放弃排队确认窗口
FellInNotifier = {
	'btnGiveup': { 'text': "放弃排队" },
	}

# 密保窗口
guarder = {
	'title': { 'color' : (255.0, 251.0, 182.0), 'text': "密保卡验证"},
	'btnClear': { 'text': "清除" },
	'btnOk': { 'text': "确定" },
	'btnCancel': { 'text': "取消" },
	'tips': { 'text': "请根据提示坐标,按照顺序正确输入“光宇游戏密码保护卡”背面对应的编号。" },
	'advice': { 'text': "1.建议您定期更换密保卡以确保帐号安全。@B2.密保卡相关内容请访问光宇社区。" },
	}

# 角色创建界面
RoleCreator = {
	# btns text
	'btnBack'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "上一步" },	# "LoginDialog:RoleCreator", "btnBack"
	'btnOk'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "确 定" },	# "LoginDialog:RoleCreator", "btnOk"
	'btnMale'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "男" },	# "LoginDialog:RoleCreator", "btnMale"
	'btnFemale'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "女" },	# "LoginDialog:RoleCreator", "btnFemale"
	'btnArcher'		 : { 'color' : (255.0, 255.0, 255.0), 'text' : "射 手" },	# "LoginDialog:RoleCreator", "btnArcher"
	'btnMage'		 : { 'color' : (255.0, 255.0, 255.0), 'text' : "法 师" },	# "LoginDialog:RoleCreator", "btnMage"
	'btnSword'		 : { 'color' : (255.0, 255.0, 255.0), 'text' : "剑 客" },	# "LoginDialog:RoleCreator", "btnSword"
	'btnFighter'		 : { 'color' : (255.0, 255.0, 255.0), 'text' : "战 士" },	# "LoginDialog:RoleCreator", "btnFighter"
	# stext
	'stCreateTitle'		 : { 'color' : (255.0, 248.0, 158.0), 'text' : "角色创建",  'limning' : 2 },	# "LoginDialog:RoleCreator", "stCreateTitle"
	'stHead'		 : { 'color' : (251.0, 255.0, 149.0), 'text' : "头 像" },	# "LoginDialog:RoleCreator", "stHead"
	'stHair'		 : { 'color' : (251.0, 255.0, 149.0), 'text' : "发 型" },	# "LoginDialog:RoleCreator", "stHair"
	'stFace'		 : { 'color' : (251.0, 255.0, 149.0), 'text' : "脸 型" },	# "LoginDialog:RoleCreator", "stFace"
	'stPro'		 : { 'color' : (251.0, 255.0, 149.0), 'text' : "职 业" },	# "LoginDialog:RoleCreator", "stPro"
	'stGender'		 : { 'color' : (251.0, 255.0, 149.0), 'text' : "性 别" },	# "LoginDialog:RoleCreator", "stGender"
	'noCamp'		 : { 'color' : (251.0, 255.0, 149.0), 'text' : "无阵营" },	# "LoginDialog:RoleCreator", "stGender"
	'taoism'		 : { 'color' : (251.0, 255.0, 149.0), 'text' : "仙 道" },	# "LoginDialog:RoleCreator", "stGender"
	'demon'		 : { 'color' : (251.0, 255.0, 149.0), 'text' : "魔 道" },	# "LoginDialog:RoleCreator", "stGender"
	'stCamp'		 : { 'color' : (251.0, 255.0, 149.0), 'text' : "阵 营" },	# "LoginDialog:RoleCreator", "stGender"
	
}

# 阵营选择界面
CampSelector = { 
	"title"	: {"color":(255.0, 248.0, 158.0), 'text' : "阵营选择",  'limning' : 2, "fontSize":24 },
	"camp_1": {"color":(255.0, 248.0, 158.0), 'text' : "盘古仙道"},
	"camp_2": {"color":(255.0, 248.0, 158.0), 'text' : "混元魔道"},
	"btnQuit": {"color":(255.0, 248.0, 158.0), 'text' : "退 出"},
	}


# 自动激活提示界面
autoActWnd = {
	'activing': { 'text': "正在自动激活..." },
}

# 软键盘界面
keyBoard = {
	'upperSwitch' :{ 'text': "大/小写"},
}

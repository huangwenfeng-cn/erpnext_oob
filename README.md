## ERPNext Out Of Box

ERPNext Out of Box

#### License
ERPNext开箱即用，主要包括以下功能

本项目解决标准控件翻译问题参考学习了破匣求禅/EBCLocal，源项目地址 https://gitee.com/petel_zhang/EBCLocal，
在此特别感谢

主要功能

1. 界面深度汉化

1.1 维护translations目录下的zh_global.csv，类似界面上的用户翻译，会在每个页面加载，用以解决标准功未能获取相关页面待翻译文本，而无法翻译的问题（如首页左侧的Modules,Domain等)。

1.2 修正标准系统中以下自带控件不能翻译中文的问题

 1.2.1 日历控件

 1.2.2 甘特图控件

 1.2.3 表单视图顶部热力图控件

 1.2.4 数据表格控件标题列下拉菜单：排序、移除列菜单项

 1.2.5 链接字段下拉框是中文，选择择值之后也显示为中文

 1.2.6 筛选器中多选字段（包括),下拉框及显示值均支持中文

 1.2.7 数据面板及工作区中的数据卡

 1.2.8 数据面板视图标题

 1.2.9 统计图表标题及日期过滤按钮与下拉选单


2. 初始化（setup wizard）步骤简化

2.1 设置默认语言为中文，默认地区(国家)为中国

2.2 导入中国会计科目表（已添加公司表单上所需默认科目与临时开账科目）

2.3 为公司分派默认科目

2.4 为默认仓库分派默认库存科目

2.5 为默认物料组分派默认费用科目

2.6.新建税种（内销、外销、小规模纳税、一般纳税）

2.7 新建销售及采购税费模板（13%， 0%， 1%）以及税费模板分派规则

2.8 修改一词多义字段标签（如采购、销售税费明细中的税率）

2.9 隐藏本地化不适用字段，如供应商与客户主数据中的pan(印度企业实体纳税登记号） ，物料主数据中物料商场hub相关字段

2.10 修改默认系统流水码前缀-改短


3. 标准功能优化

3.1 修复bug 3.1.1 防止因网络超时无法创建有首选邮箱的联络人，取消从国外用户图像网站获取用户图像

 3.1.2 防止因SQL写入语句超二十万条被系统自动终止，避免将select语句计算在内

 3.1.3 全局智能搜索框支持多关键字(用&分隔)检索，对检索出的单据进行权限检查后返回

 3.1.4 表单表格控件

    3.1.4.1 因复制的内容最后一行是空行，进度条走不完

    3.1.4.2 文本编辑器字段内容中保留回车换行
    
    3.1.4.3 增加公用js方法erpnext_oob.utils.switch_to_excel_download，支持将下载格式由默认的csv改为excel, 创建类似下面的客户端脚本启用该功能，items是子表字段名

    frappe.ui.form.on('Sales Order', {
        onload: function(frm) {
            erpnext_oob.utils.switch_to_excel_download(frm, "items");
        },
    })

3.1.5 列表界面底部显示数值类字段总计

3.1.6 多公司场景下，支持默认公司设置在用户默认值而非全局默认值中
    
3.2 功能完善

 3.2.1 角色权限管理：用户角色及单据类型下拉框变更为下拉框变更为智能输入下拉框，支持按中文与英文关键字检索

 3.2.2 全局智能搜索框支持按中、英文检索单据类型、报表、模块等界面对象

 3.2.3 单据类型、用户角色、报表下拉框支持按中、英文关键字检索

 3.2.4 单据打印时显示制单人与审批人姓名， 在打印格式自定义html字段中 使用 {{ doc.get_owner_username() }} 和 {{ doc.get_submit_username() }}

 3.2.5 导入功能导出模板字段标题为中文，导入模板支持中文字段标题，导入主从表时连续行主表字段值相同会被自动识别为同一个单据，不需要再在Excel中通过
 工具将相同单据第一行以后的主表字段清空

4. 新功能

4.1 单据级打印格式自动默认，标准功能只支持按单据类型自动默认打印格式，新功能中在打印格式中增加了设为默认格式的条件和优先级两个字段，允许用户通过Python表达式为满足条件的单据分派默认的打印格式，如按不同的物料移动类型创建相应的打印格式。

4.2 客户单据类型增加了一个隐藏的助记码(基于客户名自动生成全拼与首字母拼，如富士康科技会生成 fushikangkeji fskkj),在输入客户链接字段时，可基于助记码，输入如fsk或shika即可自动过滤出这个客户名称
（需在定制表单中为客户单据类型在搜索字段中增加pinyin_name字段)

4.3 增加了自动从网站https://www.boc.cn/sourcedb/whpj/下载并更新货币汇率的函数sync_exchange_rate, 可新增这一行代码
frappe.call('erpnext_oob.localize.sync_exchange_rate.sync_exchange_rate')
的python 后台任务类型脚本设置自动更新，详见码云问题贴 https://gitee.com/yuzelin/erpnext-chinese-docs/issues/I4WFIJ

4.4 定制表单-自动编号格式支持基于单据过账日期字段posting_date的格式化字符串
4.4.1.定制表单-编号规则，选公式，format字符串使用如下格式化字符串（首字母分别代表截取日，月，年两位，最后首字母Y 取4位年），
例如单据过帐日期为2023-09-18，分别截取出来的编号为
d_posting_date = > 18
m_posting_date = > 09
y_posting_date = > 23
Y_posting_date = > 2023

4.5 批量销售退货
 
本人在discuss.erpnext.com及github.com官网帐号是szufisher

使用方法

先决条件

进入 bench 工作台目录；

1.新安装
1.1、获取对应版本APP

bench get-app https://gitee.com/yuzelin/erpnext_oob.git --branch version-15

1.2、安装APP(有多个站点且未设默认站点的请加--site参数）

bench install-app erpnext_oob

升级
2.1、bench update 命令

bench update --apps erpnext_oob --pull --reset

2.2 重新编译JS等资源文件

bench build --app erpnext_oob --force

2.3 通过本应用中的插件机制向打印格式单据类型中新增两个字段(同步，新安装时不需要这一步，也可运行标准的bench migrate 命令，会对所有app作升级后同步数据库表处理)
bench console
In [6]: from frappe.utils.fixtures import sync_fixtures

In [7]: sync_fixtures('erpnext_oob')

卸载
3.1 从站点卸载 

bench uninstall-app erpnext_oob

3.2 从整个bench环境卸载,移除整个应用目录

bench remove-app erpnext_oob

欢迎提交问题和反馈建议。


#### License

MIT
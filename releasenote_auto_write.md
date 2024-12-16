我现在需要一个用于自动填写Release note的python脚本，请你帮我完成这个十分详细且系统的简体中文的开发需求文档，用于给开发团队人员，文档内容中尽量用文字详细描述需求。但是不需要包含代码和具体实现。请注意，我很多的判断逻辑是必须的，请使用你的语言系统、详细、清晰的表述我的要求。而且我希望你可以详细提供高度解耦的模块化的方法，高度模块化代码，模块应该职责单一、内聚性高、耦合性低。明确的接口和职责分离，依赖注入，使用事件驱动或回调机制，使用配置等。

我的要求是开发一个专业、非常复杂、高度模块化、丰富可拓展性的在Linux环境下使用的python3.8.10脚本，代码中关键、复杂部分要有专业的英文注释。代码必须说明解释器，让用户可以直接使用*.py执行脚本，要指定编码格式，代码开头也要有详细专业英文说明用途，使用说明等内容。脚本不使用命令行参数，而是使用代码中的配置。

我现在具体的需求是：我每次release时会对三种工具管理的仓库筛选本次release时对应TAG和上次release时的TAG之间，所有更新的commit。
三种工具分别是：repo、jiri、git
jiri工具管理nebula这个整体代码项目，nebula的路径是~/grpower/workspace/nebula/
nebula的manifest文件位置相对jiri仓库的根路径是：manifest/cci/nebula-main
git管理grpower、grt、grt_be
grpower路径是~/grpower
grt的路径是~/grt
grt_be的路径是~/grt_be
repo管理alps和yocto，alps仓库根路径是~/alps，yocto仓库根路径是~/yocto
alps仓库manifest文件相对根路径的位置是.repo/manifests/mt8678/grt/1001/alps.xml
yocto仓库manifest文件相对根路径的位置是.repo/manifests/mt8678/grt/1001/yocto.xml
repo、riji仓库需要读取manifest文件中所有记录的git仓库及其路径，后续使用。

TAG的命名规范：nebula仓库release-spm.mt8678_mt8676_<日期标识>；其他所有仓库都使用：release-spm.mt8678_<日期标识>。请使用grt仓库中最新和次新TAG的日期标识比如release-spm.mt8678_2024_1114_02、release-spm.mt8678_2024_1119_01作为所有仓库最新和次新的日期标识。

我表格排序的方法期望是每次有新的release版本时，再第二行之上，第一行之间，插入匹配本次更新commit数量的行，然后在每行填入对应的commit信息。每行应该有且仅有一个commit，若一次更新多个commit请插入数量匹配的行。


我表格中需要填写的如下：
release 版本：A列，此列填入~/grt仓库下最晚创建的TAG名称

功能：B列，此列填入本次填入两个TAG间，更新的commit message信息，只取正文描述部分填入，不需要考虑作者、时间等。每行应该有且仅有一个commit。

模块：C列，grpower、nebula仓库的更新，则在模块中填入 nebula-hyper ；alps 的更新填入 alps；yocto的更新填入 yocto；~/grt仓库的更新填入thyp-sdk；~/grt_be的更新填入thyp-sdk-be。

压缩包/Patch：D列，这行期望是填入每个commit所对应的patch文件相对路径。具体做法是对除了nebula、grpower以外的仓库使用git format-patch <倒数第二新的tag>..<最新的tag>，获取本次更新commit对应的patch信息，脚本执行结束后请一一对应使用绝对路径删除对应patch文件，请不要使用类似rm *.patch或者git clean -fdx导致误删。然后判断~/grt和~/alps/vendor/mediatek/proprietary/trustzone/grt这两个仓库下，本次更新的commit 信息中是否有包含 "] thyp-sdk: "、"] nebula-sdk: "、"] tee: " 三者之一的字符，若有，这些patch应该属于nebula仓库和grpower仓库下更新的commit所对应的patch，若一个commit有多个patch对应，请在同一格内换行填入。然后请把所有patch文件的绝对路径去除路径中的 /home/nebula/ 字符，每个patch填入对应commit所在行的格子内。

示例代码/文档路径 E列 ，留空

提交信息 F列，请取~/grpower/workspace/nebula/zircon和~/grpower/workspace/nebula/garnet这两个git仓库下的最后一个commit id，填入，格式是：
zircon: zircon的commit id
garnet: garnet的commit id，请把这些信息在同一个格子换行填入，谢谢。

测试负责人 / 修改人 / MTK owner ： G列，这里的内容作为参数，使用脚本代码中配置的默认值，建议实际在脚本中定义为三个参数。这三个内容应该是同一列中在同一格子，使用拼接的方式写入。如：高宇轩 / 武阳 / 金春阳

提交时间 ：H列，使用配置的参数。

是否想另外一个平台移植？：I列，使用配置的参数。

是否已经移植和测试？：J列，使用配置的参数。

是否Release客户及客户名：K列，使用配置的参数，默认为空。

change ID / commit ID title：L列，使用配置的参数，默认为空。

MTK合入日期：M列，使用配置的参数，默认为空。

MTK 注册情况：N列，使用配置的参数，默认为空。

commit信息：O列，这一行填写 本行commit 所对应的commit id。

其他列如果我没有提需求的话，请保持空白不填入，我可以后续自己改excel表格。

其次，我脚本要保持使用FastAPI 上传、下载、删除文件的能力，默认都以代码仓库的根目录路径为准，这个根目录路径作为配置选项保存，上传下载删除所使用的路径均为相对路径。网络ip和端口是100.64.0.5和4151。

改脚本应该支持使用FastAPI启动执行任务，这个项目不需要并发，有多的任务排队执行即可。应该支持搜索当前所有任务的状态、停止任务、删除任务。执行任务完成后应该合理标记任务状态。
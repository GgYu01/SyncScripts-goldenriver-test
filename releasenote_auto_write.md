我现在需要一个用于自动填写Release note的python脚本，请你帮我完成这个十分详细且系统的简体中文的开发需求文档，用于给开发团队人员，文档内容中尽量用文字详细描述需求和实现方法。但是不需要包含代码。请注意，我很多的判断逻辑是必须的，请使用你的语言系统、详细、清晰的表述我的要求。

我的要求是开发一个专业、非常复杂、高度模块化、丰富可拓展性的在Linux环境下使用的python3.8.10脚本，其中涉及到可修改的参数、变量部分不需要作为命令行参数而是使用专门的数据结构让使用者修改源码中的内容。涉及到参数返回值等内容必须同时使用说明、冒号、箭头等方式全面保障可维护性可读性，代码中关键、复杂部分要有专业的英文注释。代码必须说明解释器，让用户可以直接使用*.py执行脚本，要指定编码格式，代码开头也要有详细专业英文说明用途，使用说明等内容。

我现在具体的需求是：我需要写一个基于每次更新commit时，要填写的Release note Excel表格，我只需要基于之前我写过的表格，新加入内容即可，不要对之前的内容做修改。其中，每次更新内容时，应该从第二行之上，第一行之下开始逐渐插入新的行，让最新的内容保持在第二行，表格越靠后的行应该是越老的信息，这样打开表格即可看到最新内容。每行对应我git仓库中一笔更新的commit，一行应该有且仅有一个commit，若有多个commit请使用对应数量的行描述。

我表格中需要填写的如下：
release 版本	功能	模块	压缩包/Patch	示例代码/文档路径	提交信息	测试负责人 / 修改人 /MTK owner	提交时间	是否想另外一个平台移植？	是否已经移植和测试？	是否Release客户及客户名	change ID / commit ID title	MTK合入日期	MTK 注册情况	commit信息

其中，我会对所有仓库打tag，~/grpower、~/grt、~/grt_be是三个git仓库的路径，~/alps、~/yocto、~/grpower/workspace/nebula目录及其子目录下有很多git仓库。请排除.repo和.jiri路径及其所有子路径。
我所有仓库更新tag都是同步的，其中~/grpower/workspace/nebula及其所有子路径下的git仓库tag命名的规则是：
release-spm.mt8678_mt8676_2024_1107_04，2024_1107_04这一段是包含日期的版本标识，前面的是前缀；而其他git仓库tag命名规则：release-spm.mt8678_2024_1107_04，2024_1107_04这一段依然是包含日期的版本标识，前面的是前缀。版本标识在所有仓库中是一致的。
我需要你以~/grt仓库为例，获取仓库最新和次新的tag中的版本标识，并以此拼接出适用于不同仓库的最新和次新的tag。
然后判断拼接构建出的最新和次新的tag之间在~/grt和~/alps/vendor/mediatek/proprietary/trustzone/grt仓库下是否有提交，若有，判断commit信息中是否包含有完全符合"] thyp-sdk: "、"] nebula-sdk: "、"] tee: " 三者之一的信息，若有，请使用git format-patch <倒数第二新的tag>..<最新的tag> 生成patch后，判断哪个patch属于这个特殊的提交然后，获取这些patch的绝对路径并去除/home/nebula/。

release版本应该填入的信息为：~/grt仓库下最晚创建的TAG名称

功能 应该取~/grpower、~/grpower/workspace/nebula、~/alps、~/yocto、~/grt、~/grt_be 下，所有git仓库中，判断之前构建出最新和次新的tag之间是否有提交，若有提交，则提取其git log 中这些commit message信息，只取正文描述部分填入，不需要考虑作者、时间等。

模块中 若是~/grpower、~/grpower/workspace/nebula下的更新，则在模块中填入 nebula-hyper ；~/alps 下的更新填入 alps；~/yocto下的更新填入 yocto；~/grt仓库下的更新填入thyp-sdk；~/grt_be下的更新填入thyp-sdk-be。

压缩包/Patch 这一列要填写的信息是： 若commit更新来自~/grpower、~/grpower/workspace/nebula仓库下，则每一个commit都请在本栏填入之前获取到的包含有特殊信息patch，去除/home/nebula/的路径信息，比如alps/vendor/mediatek/proprietary/trustzone/grt/0001-<对应内容>.patch，若本行有多个patch对应，请在同一格内换行填入。；若commit更新来自其他路径，则请在有更新的仓库下执行git format-patch <倒数第二新的tag>..<最新的tag>生成patch后，获取每个commit所对应的patch文件的绝对路径，然后去掉路径中的 /home/nebula/ 字符，把后续的字符填入。请务必注意每一行只能有一个commit及对应的patch文件，请保障对~/grt、~/alps/vendor/mediatek/proprietary/trustzone/grt这两个仓库的特殊处理，非特殊的commit可以和其他路径仓库一样正常填入。我希望表格内commit对应的.patch文件路径可以和git format-patch <倒数第二新的tag>..<最新的tag>中排序和命名是完全一致的。

提交信息 请取~/grpower/workspace/nebula/zircon和~/grpower/workspace/nebula/garnet这两个git仓库下的最后一个commit id，填入，格式是：
zircon: zircon的commit id
garnet: garnet的commit id，请把这些信息在同一个格子换行填入，谢谢。

测试负责人 / 修改人 /MTK owner ： 这里的内容作为参数，优先使用命令行参数，若无命令行参数使用脚本代码中的默认值，建议实际在脚本中定义为三个参数。这三个内容应该是同一列中在同一格子，使用拼接的方式写入。如：高宇轩 / 武阳 / 金春阳

是否想另外一个平台移植？ 这里填写的内容作为参数，优先使用命令行参数，若无命令行参数使用脚本代码中的默认值。

是否已经移植和测试？ 这里填写的内容作为参数，优先使用命令行参数，若无命令行参数使用脚本代码中的默认值。

是否Release客户及客户名 这里填写的内容作为参数，优先使用命令行参数，若无命令行参数使用脚本代码中的默认值。

commit信息 这一行填写 本行commit 所对应的commit id。

其他列如果我没有提需求的话，请保持空白不填入，我可以后续自己改excel表格。
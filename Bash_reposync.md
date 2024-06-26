我需要同步4个版本库中的代码，我需要一个非常专业、高度模块化的 python3.12.3 脚本代码，用于在 Ubuntu24 中运行：

/mnt/sst/one_78/alps 中的代码同步命令有两步，如下：

repo init -u "ssh://gaoyx@www.goldenriver.com.cn:29420/manifest" -b release-spm.mt8678_2024_0524 -m alps.xml 
repo sync -j2048

/mnt/sso/one_78/yocto 中的代码同步命令有两步，如下：

repo init -u "ssh://gaoyx@www.goldenriver.com.cn:29420/manifest" -b release-spm.mt8678_2024_0524 -m yocto.xml
repo sync -j2048

/mnt/sso/one_78/ 还需要同步两个git仓库的代码，命令如下：

git clone --branch release-spm.mt8678_2024_0524 "ssh://gaoyx@www.goldenriver.com.cn:29420/yocto/src/hypervisor/grt"
git clone --branch release-spm.mt8678_2024_0524 "ssh://gaoyx@www.goldenriver.com.cn:29420/yocto/src/hypervisor/grt_be"

/mnt 是我所有代码存储磁盘所在的基本目录，sso sst hdo等是我的磁盘挂载路径，根据我对性能优化需求会把不同代码仓库放在不同的磁盘中。alps yocto grt grt_be 等是我的代码仓库名同时也会作为存储各代码仓库的路径参数，one_78 是整个代码同步项目的名称，作为路径参数。不同版本库可能会使用 repo/git/JIRI 等方式同步代码。

所有代码仓库同步的分支是完全一致的，仓库名和同步的url、manifest一定有关系，所有repo仓库的manifest是同一个，git仓库有大量一致的信息。所有仓库同步使用的用户、代码仓库域名、端口都是一致的，只是远端仓库下项目名略有差距。

所有代码仓库的同步操作需要独立并发异步执行，当手动停止脚本程序时，所有同步动作均退出。

使用无限循环的方式保证代码同步成功。

同步repo仓库时，需要检查是否有对应路径，若没有则需要输出信息并等待 10 秒，如此重复六次，然后创建 alps 和 yocto 存储路径。。需要首先检查路径下是否已经repo init成功，则直接循环执行repo sync而不执行repo init。若代码仓库已经repo sync成功，则直接退出本仓库的代码同步。若repo init失败，则循环执行repo init直至成功为止，后续循环中将不再执行repo init，再执行repo sync的循环。

同步git仓库时，考虑到git clone会自动创建子路径，所以不需要创建文件夹，但是需要检查路径下是否有已经成功同步的git仓库，若有则直接说明同步成功并退出本仓库代码同步，若有失败的同步git仓库则删除.git路径的父亲目录，并重新执行git同步。

这四个仓库中的代码同步命令需要在一个无限循环中执行。当同步命令在循环中执行成功时，它会输出一条信息并停止循环。如果失败，则继续执行循环，只有在同步所有资源库的代码后，才会输出成功信息并退出脚本。

在终端分割四个区域用于显示每个仓库的同步输出信息，每个版本库的同步日志都保存在相应版本库的同步日志文件中。

以下是我对脚本代码的要求。
1. 书写请保持工整规范，排版合理，代码结构逻辑专业，高度模块化，明确函数的参数和返回值，有专业的声明、说明和注释 ，并且请考虑到以后有需要添加的更多种类的功能模块来做对应的代码设计。请使用英文做专业的函数方法描述说明，说明每个方法的作用、参数、返回值。返回值不仅使用英文说明，也要用->，可以使用装饰器和类优化整篇代码结构，保证逻辑清晰严谨
2. 需要加入详细完整的执行过程判断，并且输出信息说明脚本执行步骤是正确通过还是错误。完成美观的脚本运行、信息输出界面和及warnning、error信息输出界面。请使用rich、Urwid、 Asciimatics这三种库优化界面输出和错误异常追踪。
3. 请书写高级、结构复杂的测试代码.尽可能多使用高级的数据结构、程序架构、数据处理、代码组织、编程范式、装饰器、库等高级的Python特性，减少重复和简单的内容。使用类、装饰器优化代码。优先使用高级、复杂、流行、新的第三方库完成功能。相似的内容请通过程序架构、数据结构减少重复。作用相同的变量或者含有相同字符的参数、路径等请减少重复。
4. 代码完全不需要考虑内存和资源占用。
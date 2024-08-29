# docker 
https://linux.cn/article-14871-1.html

要在 Ubuntu 22 中使用 GPT 分区格式格式化两个物理磁盘并合并成一个大磁盘，但不使用 RAID 0，并且尽量减少对 CPU 的影响，你可以考虑使用 LVM（逻辑卷管理器）。这种方法不会像 RAID 0 那样需要额外的计算来分配数据，从而可以减少 CPU 负担。下面是详细的步骤：

### 1. 确保所有工具都已安装
首先，确保你的系统安装了 `lvm2` 包。可以通过以下命令安装：
```bash
sudo apt update
sudo apt install lvm2
```

感谢你指出错误，我们可以根据你提供的 `gdisk` 帮助信息来重新整理步骤，确保正确创建 GPT 分区和处理。以下是修正后的步骤：

### 2. 格式化磁盘并创建 GPT 分区
对每个磁盘使用 `gdisk` 工具来创建 GPT 分区表和新分区：

1. **启动 gdisk**
   打开终端并输入以下命令来开始对 `nvme0n1` 磁盘操作：
   ```bash
   sudo gdisk /dev/nvme0n1
   ```
   使用 'd' 删除分区
2. **创建一个新的 GPT 分区表**
   - 在 `gdisk` 提示符下，输入 `o` 来创建一个新的空的 GPT 分区表。
   - 确认操作，通常需要输入 `y`。

3. **添加一个新分区**
   - 输入 `n` 来添加一个新分区。
   - 对于分区号、起始扇区和结束扇区的提示，如果希望使用默认值，可以直接按 Enter。通常，默认值会使用整个磁盘。
   - 设置分区类型，如果是 Linux 文件系统，可以使用 `8300` 作为类型代码。

4. **写入更改并退出**
   - 输入 `w` 来写入更改到磁盘。
   - 确认写入操作。

重复以上步骤对 `nvme1n1` 进行操作。


### 3. 创建物理卷
创建完分区后，使用以下命令将这些分区设置为 LVM 物理卷（PV）：
```bash
sudo pvcreate /dev/nvme0n1p1
sudo pvcreate /dev/nvme1n1p1
```

### 4. 创建卷组
然后，你可以创建一个卷组（VG），将这两个物理卷加入同一个卷组：
```bash
sudo vgcreate myvg /dev/nvme0n1p1 /dev/nvme1n1p1
```

### 5. 创建逻辑卷
最后，创建一个逻辑卷（LV）来合并这些空间：
```bash
sudo lvcreate -l 100%FREE -n mylv myvg
```
这将创建一个逻辑卷，使用 `myvg` 卷组中的所有可用空间。

### 6. 格式化并挂载逻辑卷
你可以选择任何文件系统来格式化逻辑卷。例如，使用 ext4：
```bash
sudo mkfs.ext4 /dev/myvg/mylv
```
然后，你可以挂载这个逻辑卷：
```bash
sudo mkdir /mnt/sso
sudo mount /dev/myvg/mylv /mnt/sso
```

这样，你就有了一个大磁盘空间，而且由于没有使用 RAID 0，对 CPU 的影响非常小。












要将这两个磁盘合并成一个大磁盘，你可以使用 Linux 的逻辑卷管理器（LVM）来创建一个包含这两个磁盘的逻辑卷组。在这个过程中，所有原有的分区将被清除。




### 步骤 1: 清除原有分区

首先，使用 `gdisk` 或 `fdisk` 工具清除磁盘上的所有分区。

```bash
sudo gdisk /dev/nvme1n1
```

然后，依次执行以下操作：
1. 输入 `x` 进入专家模式。
2. 输入 `z` 来擦除 GPT 表并创建一个新的保护性 MBR。
3. 输入 `y` 来确认擦除 GPT。
4. 输入 `y` 来确认擦除数据。

对于第二个磁盘，重复上述步骤：

```bash
sudo gdisk /dev/nvme0n1
```

### 步骤 2: 创建物理卷 (PV)

在清除分区后，使用 `pvcreate` 命令将每个磁盘初始化为 LVM 的物理卷。

```bash
sudo pvcreate /dev/nvme1n1
sudo pvcreate /dev/nvme0n1
```

### 步骤 3: 创建卷组 (VG)

创建一个新的卷组，并将这两个物理卷添加到卷组中。

```bash
sudo vgcreate my_vg /dev/nvme1n1 /dev/nvme0n1
```

`my_vg` 是卷组的名称，你可以根据需要修改。

### 步骤 4: 创建逻辑卷 (LV)

接下来，创建一个逻辑卷，它将跨越这两个物理卷。

```bash
sudo lvcreate -l 100%FREE -n my_lv my_vg
```

这里，`my_lv` 是逻辑卷的名称，`my_vg` 是你在上一步中创建的卷组的名称。

### 步骤 5: 格式化逻辑卷

格式化逻辑卷为你所需要的文件系统，比如 ext4。

```bash
sudo mkfs.ext4 /dev/my_vg/my_lv
```

### 步骤 6: 挂载逻辑卷

最后，创建一个挂载点并挂载逻辑卷。

```bash
sudo mkdir /mnt/sso
sudo mount /dev/my_vg/my_lv /mnt/sso
```

现在，你的两个磁盘已经被合并成一个大的逻辑卷，并且可以作为一个单一的大存储空间使用。

### 可选：自动挂载

如果你希望在系统启动时自动挂载这个逻辑卷，你可以将其添加到 `/etc/fstab` 中。

首先，找到逻辑卷的 UUID：

```bash
sudo blkid /dev/my_vg/my_lv
```

然后编辑 `/etc/fstab` 并添加如下行：

```bash
UUID=你的UUID /mnt/my_storage ext4 defaults 0 0
```

保存并退出编辑器，确保在下次启动时自动挂载逻辑卷。

这样，你就成功地将两个 NVMe 磁盘合并成了一个大的逻辑卷，并将其挂载到系统中。
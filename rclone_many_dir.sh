#!/bin/bash

###############################################################################
# batch_rclone_copy.sh
#
# Description:
#   批量并发拷贝多个本地文件夹到远端存储，使用 rclone 工具。
#   支持多个源目录匹配模式，详细的错误处理，
#   并记录每个拷贝任务的日志和执行时间。
#
# Usage:
#   ./batch_rclone_copy.sh
#
# Requirements:
#   - rclone 已安装并配置
#   - Bash 版本 >= 4
#
# Author:
#   OpenAI ChatGPT
#
# Date:
#   2024-04-27
###############################################################################

# ------------------------------- 全局变量 -------------------------------

# 源目录匹配模式数组（可根据需要添加多个模式）
SOURCE_PATTERNS=("auto8678p1_64_hyp_gpu_06*" "auto8678p1_64_hyp_gpu_07*" "auto8678p1_64_hyp_gpu_08*")

# 目标根目录
DEST_ROOT="/mnt/seaweedfs"

# 并发执行的最大任务数（根据系统资源调整）
MAX_CONCURRENT_JOBS=64

# 日志目录
LOG_DIR="./logs"

# 全局数组，用于保存子进程的 PID
declare -a pids=()

# 全局关联数组，用于记录每个任务的状态（成功/失败）
declare -A task_status

# 开始时间
start_time=$(date +%s)

# ----------------------------- 函数定义 -------------------------------

# 初始化环境
initialize() {
    # 创建日志目录
    mkdir -p "$LOG_DIR"

    # 检查 rclone 是否安装
    if ! command -v rclone &> /dev/null; then
        echo "Error: rclone 未安装。请安装 rclone 并进行配置。"
        exit 1
    fi

    # 检查 Bash 版本
    if (( BASH_VERSINFO[0] < 4 )); then
        echo "Error: 本脚本需要 Bash 版本 4 或更高。"
        exit 1
    fi
}

# 清理函数，用于中断时终止所有子进程
cleanup() {
    echo ""
    echo "脚本被中断，正在停止所有 rclone 进程..."
    for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            echo "已终止 PID: $pid"
        fi
    done
    echo "所有 rclone 进程已终止。"
    exit 1
}

# 捕获中断信号
trap cleanup SIGINT SIGTERM

# 拷贝单个目录的函数
copy_dir() {
    local src_dir="$1"
    local dest_dir="$2"
    local log_file="$3"

    local task_start_time=$(date +%s)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始拷贝: $src_dir 到 $dest_dir" | tee -a "$log_file"

    # 执行 rclone copy 命令
    if rclone copy "$src_dir" "$dest_dir" --transfers=16 >> "$log_file" 2>&1; then
        local task_end_time=$(date +%s)
        local duration=$((task_end_time - task_start_time))
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 完成拷贝: $src_dir 到 $dest_dir，耗时: ${duration}秒" | tee -a "$log_file"
        task_status["$src_dir"]="成功"
    else
        local task_end_time=$(date +%s)
        local duration=$((task_end_time - task_start_time))
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 拷贝失败: $src_dir 到 $dest_dir，耗时: ${duration}秒" | tee -a "$log_file"
        task_status["$src_dir"]="失败"
    fi
}

# 启动拷贝任务
start_copy_task() {
    local src_dir="$1"
    local dest_dir="$2"
    local log_file="$3"

    # 启动拷贝任务并记录 PID
    copy_dir "$src_dir" "$dest_dir" "$log_file" &
    local pid=$!
    pids+=("$pid")
}

# 记录整体执行时间
record_total_time() {
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    echo "所有拷贝操作已完成，整体耗时: ${duration}秒。"
}

# 主函数
main() {
    initialize

    echo "开始批量拷贝任务..."

    local src_dirs=()

    # 收集所有匹配的源目录
    for pattern in "${SOURCE_PATTERNS[@]}"; do
        for dir in $pattern; do
            if [ -d "$dir" ]; then
                src_dirs+=("$dir")
            else
                echo "警告: 跳过非目录项: $dir"
            fi
        done
    done

    local total_tasks=${#src_dirs[@]}
    if (( total_tasks == 0 )); then
        echo "Error: 没有找到匹配的源目录。请检查源目录匹配模式。"
        exit 1
    fi

    # 启动拷贝任务
    for src_dir in "${src_dirs[@]}"; do
        local dest_dir="$DEST_ROOT/$src_dir"
        local log_file="$LOG_DIR/${src_dir}.log"

        # 启动任务
        start_copy_task "$src_dir" "$dest_dir" "$log_file"

        # 并发控制
        while (( ${#pids[@]} >= MAX_CONCURRENT_JOBS )); do
            # 等待任意一个子进程完成
            wait -n
            # 清理已完成的 PID
            for i in "${!pids[@]}"; do
                if ! kill -0 "${pids[i]}" 2>/dev/null; then
                    unset 'pids[i]'
                fi
            done
        done
    done

    # 等待所有子进程完成
    wait

    # 记录整体执行时间
    record_total_time

    # 输出任务总结
    echo "任务总结:"
    for src in "${!task_status[@]}"; do
        echo "  - $src : ${task_status[$src]}"
    done
}

# 执行主函数
main

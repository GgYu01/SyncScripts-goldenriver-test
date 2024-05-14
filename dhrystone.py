import os
import subprocess
import pandas as pd
from itertools import combinations

# 定义CPU核心参数代号
cpu_codes = {
    'cpu0': 1, 'cpu1': 2, 'cpu2': 4, 'cpu3': 8,
    'cpu4': 10, 'cpu5': 20, 'cpu6': 40, 'cpu7': 80
}

# 定义CPU组合
cpu_combinations = [
    ('cpu0', 'cpu3'), ('cpu0', 'cpu1'), ('cpu0', 'cpu4', 'cpu5'),
    ('cpu1', 'cpu2'), ('cpu0', 'cpu4', 'cpu1', 'cpu2'),
    ('cpu1', 'cpu2', 'cpu3'), ('cpu0', 'cpu4', 'cpu5', 'cpu6'),
    ('cpu1', 'cpu2', 'cpu3', 'cpu7'), ('cpu0', 'cpu1', 'cpu2', 'cpu3', 'cpu4', 'cpu5', 'cpu6', 'cpu7')
]

# 测试轮次
test_rounds = 5

# 系统类型参数（需要手动更新）
system_type = 'system_type_placeholder'

# 执行测试并记录结果
def run_test(system_type, cpu_combo, round_num):
    # 计算CPU参数代号
    cpu_param = sum(cpu_codes[cpu] for cpu in cpu_combo)
    # 构建命令
    command = f"adb shell '/data/dhry/ceshi.sh {cpu_param} 500000000'"
    # 执行命令并记录日志
    log_file_name = f"{system_type}{''.join(cpu_combo)}round{round_num}.log"
    with open(log_file_name, 'w') as log_file:
        process = subprocess.Popen(command, shell=True, stdout=log_file, stderr=log_file)
        process.wait()
    return log_file_name

# 解析日志文件并提取数据
def parse_log(log_file_name):
    with open(log_file_name, 'r') as log_file:
        lines = log_file.readlines()
        dhrystone_score = float(lines[-3].split()[-1])
        real_time = float(lines[-1].split()[1][2:])
        user_time = float(lines[-1].split()[3][2:])
        sys_time = float(lines[-1].split()[5][2:])
    return dhrystone_score, real_time, user_time, sys_time

# 主函数
def main():
    results = []
    for cpu_combo in cpu_combinations:
        for round_num in range(1, test_rounds + 1):
            log_file_name = run_test(system_type, cpu_combo, round_num)
            dhrystone_score, real_time, user_time, sys_time = parse_log(log_file_name)
            results.append({
                'System Type': system_type,
                'CPU Combination': '+'.join(cpu_combo),
                'Round': round_num,
                'Dhrystone Score': dhrystone_score,
                'Real Time': real_time,
                'User Time': user_time,
                'Sys Time': sys_time,
                'KDMIPS': dhrystone_score / 1757
            })
            print(f"Completed: {system_type} {'+'.join(cpu_combo)} Round {round_num}")

    # 创建DataFrame并保存到Excel
    df = pd.DataFrame(results)
    df.to_excel('Dhrystonetestresult.xlsx', index=False)

if __name__ == "__main__":
    main()

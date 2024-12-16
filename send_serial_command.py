import serial
import time

def send_command(port='/dev/ttyUSB0',
                baudrate=921600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1):
    try:
        # 打开串口
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout,
            xonxoff=False,    # 软件流控
            rtscts=False,     # 硬件流控
            dsrdtr=False
        )
        
        if ser.isOpen():
            print(f"成功打开串口: {port}")
        else:
            ser.open()
            print(f"打开串口: {port}")
        
        # 等待串口稳定
        time.sleep(2)

        # 要发送的命令
        command = "/data/susp.sh\n"  # 根据需要添加换行符

        # 发送命令
        ser.write(command.encode('utf-8'))
        print(f"发送命令: {command.strip()}")

        # 等待设备响应（可选）
        time.sleep(1)
        if ser.in_waiting:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print("收到响应:")
            print(response)
        else:
            print("没有收到响应。")
        
        # 关闭串口
        ser.close()
        print("串口已关闭。")

    except serial.SerialException as e:
        print(f"串口错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    send_command()
#!/bin/bash

# Define directories
ALPS_DIR=~/alps
YOCTO_DIR=~/yocto

# Log files
LOG_DIR=~/compile_logs
mkdir -p "$LOG_DIR"
ALPS_LOG_SYS="$LOG_DIR/alps_sys.log"
ALPS_LOG_HAL="$LOG_DIR/alps_hal.log"
ALPS_LOG_KRN="$LOG_DIR/alps_krn.log"
ALPS_LOG_VEXT="$LOG_DIR/alps_vext.log"
YOCTO_LOG="$LOG_DIR/yocto.log"

# Start time
start_time=$(date +%s)

# Function to log messages with timestamp
log_message() {
  local message=$1
  local log_type=$2
  echo "$(date '+%Y-%m-%d %H:%M:%S') - [$log_type] - $message"
}

# Function to check command success
check_command() {
  local status=$1
  local step=$2
  if [ $status -ne 0 ]; then
    log_message "Error in step: $step" "ERROR"
  else
    log_message "Successfully completed step: $step" "INFO"
  fi
}

# ALPS compilation function
compile_alps() {
  (
    cd "$ALPS_DIR" || {
      log_message "Failed to change directory to $ALPS_DIR" "ERROR"
      return 1
    }
    log_message "Starting ALPS sys_images compilation" "INFO"
    source build/envsetup.sh && export OUT_DIR=out_sys && lunch sys_mssi_auto_64_cn_armv82-userdebug && make sys_images &> "$ALPS_LOG_SYS"
    check_command $? "ALPS sys_images compilation"
  ) &
  
  (
    cd "$ALPS_DIR" || {
      log_message "Failed to change directory to $ALPS_DIR" "ERROR"
      return 1
    }
    log_message "Starting ALPS hal_images compilation" "INFO"
    source build/envsetup.sh && export OUT_DIR=out_hal && lunch hal_mgvi_auto_64_armv82_wifi_vm-userdebug && make hal_images &> "$ALPS_LOG_HAL"
    check_command $? "ALPS hal_images compilation"
  ) &
  
  (
    cd "$ALPS_DIR" || {
      log_message "Failed to change directory to $ALPS_DIR" "ERROR"
      return 1
    }
    log_message "Starting ALPS krn_images compilation" "INFO"
    source build/envsetup.sh && export OUT_DIR=out_krn && lunch krn_mgk_64_k61_auto_vm-userdebug && make krn_images &> "$ALPS_LOG_KRN"
    check_command $? "ALPS krn_images compilation"
  ) &
  
  (
    cd "$ALPS_DIR" || {
      log_message "Failed to change directory to $ALPS_DIR" "ERROR"
      return 1
    }
    log_message "Starting ALPS vext_images compilation" "INFO"
    source build/envsetup.sh && export OUT_DIR=out && lunch vext_auto8678p1_64_bsp_vm-userdebug && make vext_images &> "$ALPS_LOG_VEXT"
    check_command $? "ALPS vext_images compilation"
  ) &
  
  # Wait for all ALPS compilations to finish
  wait

  # Execute final python script
  log_message "Starting final Python script execution" "INFO"
  python out_sys/target/product/mssi_auto_64_cn_armv82/images/split_build.py \
    --system-dir out_sys/target/product/mssi_auto_64_cn_armv82/images \
    --vendor-dir out_hal/target/product/mgvi_auto_64_armv82_wifi_vm/images \
    --kernel-dir out_krn/target/product/mgk_64_k61_auto_vm/images \
    --vext-dir out/target/product/auto8678p1_64_bsp_vm/images \
    --output-dir out/target/product/auto8678p1_64_bsp_vm/merged
  check_command $? "Final Python script execution"
}

# YOCTO compilation function
compile_yocto() {
  (
    cd "$YOCTO_DIR" || {
      log_message "Failed to change directory to $YOCTO_DIR" "ERROR"
      return 1
    }
    log_message "Starting YOCTO compilation" "INFO"
    export TEMPLATECONF=${PWD}/meta/meta-mediatek-mt8678/conf/base/auto8678p1_64_kde_hyp
    source meta/poky/oe-init-build-env
    ln -s /proj/srv_gerrit_central_mirror/lib/sources/kirkstone/site.conf conf/site.conf
    bitbake mtk-core-image-auto8678-kde-hyp &> "$YOCTO_LOG"
    check_command $? "YOCTO compilation"
  ) &
}

# Execute both compile functions concurrently
compile_alps &
compile_yocto &

# Wait for all processes to complete
wait

# End time
end_time=$(date +%s)
elapsed_time=$(( end_time - start_time ))

# Output the time taken
log_message "Total time: $elapsed_time seconds" "INFO"

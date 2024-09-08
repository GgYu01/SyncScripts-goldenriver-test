rclone copy downloads.tar laptop:D:/78images/testtool -vv \
--transfers 128 \
--checkers 256 \
--tpslimit 10 \
--tpslimit-burst 10 \
--retries 3 \
--low-level-retries 10 \
--stats 1s \
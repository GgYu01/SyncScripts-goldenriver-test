rclone copy 4K-30fps.mp4 laptop:D:/78images/testtool -vv \
--transfers 16 \
--checkers 32 \
--tpslimit 10 \
--tpslimit-burst 10 \
--retries 3 \
--low-level-retries 10 \
--stats 1s \
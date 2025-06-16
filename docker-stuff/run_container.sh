docker run -it --rm --mount type=bind,src=/mnt/d/working,dst=/project \
 --mount type=bind,src=/mnt/d/.cache,dst=/root/.cache \
 --mount type=bind,src=/mnt/d/working/EditBench/generation_mnt,dst=/root/project/generation_mnt \
 --mount type=bind,src=/home/rshar/hf_editbench,dst=/root/hf_editbench \
 editbench:latest /bin/bash

#  --tmpfs /home:rw,size=2g \
# replace /mnt/d/working with path right before the repo (in this case, EditBenchEval is at /mnt/d/working/EditBenchEvaluation)
# replace /mnt/d/.cache with path to your cache directory (e.g., ~/.cache) to avoid out of space errors
# replace /mnt/d/EditBench_generations with path to your generation directory (e.g., ~/.cache) otherwise generations will not be saved 


docker run -it --rm \
    --mount type=bind,src=/Users/rshar/school/cmu/research/EditBench/,dst=/project \
 editbench:latest /bin/bash
# <PATH_TO_THIS_REPO_PARENT>
#  --mount type=bind,src=/home/rshar/hf_editbench,dst=/root/editbench_sandboxes \
#  --mount type=bind,src=/mnt/d/working/EditBench/generation_mnt,dst=/root/project/generation_mnt \
#  --mount type=bind,src=/mnt/d/.cache,dst=/root/.cache \
#  --tmpfs /home:rw,size=2g \
# replace /mnt/d/working with path right before the repo (in this case, EditBenchEval is at /mnt/d/working/EditBenchEvaluation)
# replace /mnt/d/.cache with path to your cache directory (e.g., ~/.cache) to avoid out of space errors
# replace /mnt/d/EditBench_generations with path to your generation directory (e.g., ~/.cache) otherwise generations will not be saved 


#!/usr/bin/env bash
### SLURM FROM WITHIN THE CONTAINER VIA SSH

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME sacct "$@"' >> /usr/local/bin/sacct

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME sacctmgr "$@"' >> /usr/local/bin/sacctmgr

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME salloc "$@"' >> /usr/local/bin/salloc

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME sattach "$@"' >> /usr/local/bin/sattach

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME sbatch "$@"' >> /usr/local/bin/sbatch

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME sbcast "$@"' >> /usr/local/bin/sbcast

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME scancel "$@"' >> /usr/local/bin/scancel

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME scontrol "$@"' >> /usr/local/bin/scontrol

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME sdiag "$@"' >> /usr/local/bin/sdiag

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME sgather "$@"' >> /usr/local/bin/sgather

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME sinfo "$@"' >> /usr/local/bin/sinfo

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME smap "$@"' >> /usr/local/bin/smap

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME sprio "$@"' >> /usr/local/bin/sprio

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME squeue "$@"' >> /usr/local/bin/squeue

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME sreport "$@"' >> /usr/local/bin/sreport

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME srun "$@"' >> /usr/local/bin/srun

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME sshare "$@"' >> /usr/local/bin/sshare

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME sstat "$@"' >> /usr/local/bin/sstat

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME strigger "$@"' >> /usr/local/bin/strigger

echo '#!/usr/bin/env bash
ssh `id -nu`@$HOSTNAME sview "$@"' >> /usr/local/bin/sview

cd /usr/local/bin
chmod 755 sacct salloc sbatch scancel sdiag sinfo sprio sreport sshare strigger sacctmgr sattach sbcast scontrol sgather smap squeue srun sstat sview

cd ~


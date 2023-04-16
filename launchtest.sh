#!/bin/bash
#SBATCH -o slurm.%A.out #STDOUT
#SBATCH -e slurm.%A.out #STDERR
#SBATCH --mem=16G
#SBATCH --partition=ultrasound
#SBATCH --exclude=dcc-ultrasound-01
#SBATCH --cpus-per-task=8
date
hostname
module load Python/3.8.1
module load LS-DYNA/R12.0.0
source /work/wew12/elasticity/.venv/bin/activate
python runq5.py

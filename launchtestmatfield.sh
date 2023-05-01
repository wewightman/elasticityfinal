#!/bin/bash
#SBATCH -o runfem.out
#SBATCH -e runfem.out
#SBATCH --mem=16G
#SBATCH --partition=ultrasound
#SBATCH --exclude=dcc-ultrasound-01
#SBATCH --cpus-per-task=8
date
hostname
module load Python/3.8.1
module load LS-DYNA/R12.0.0
module load Matlab/R2022a
source /work/wew12/elasticity/.venv/bin/activate
python runit.py

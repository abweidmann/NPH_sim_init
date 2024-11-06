#!/bin/bash
#!/usr/bin/env python
#PBS -N NPH_BUILD
#PBS -q serial
#PBS -l select=1:ncpus=1
#PBS -l walltime=1:00:00
#PBS -e erro_BUILD
#PBS -o saida_BUILD
#PBS -j eo
#PBS -m abe
#PBS -M weidmann@usp.br

cd $PBS_O_WORKDIR

### Configura ambiente para execucao do GROMACS ###

module load gromacs/2021.2-gcc-9.4.0
source ./../../meuambiente/bin/activate

export OMP_NUM_THREADS=1

csv=ice_prd.csv #$1

echo "Job has started"
chmod +x python_codes/1_NPH_temp_frame.py
python python_codes/1_NPH_temp_frame.py --csv $csv
wait
gmx_command=$(<NPH_gen_out/FRAME.txt)
wait
eval "$gmx_command"
wait
chmod +x python_codes/2_NPH_vbt.py
python python_codes/2_NPH_vbt.py --csv $csv
wait
gmx_command=$(<NPH_gen_out/VBT.txt)
wait
eval "$gmx_command"
wait
chmod +x python_codes/3_NPH_final_report.py
python python_codes/3_NPH_final_report.py --csv $csv
wait
echo "Job has finished!"

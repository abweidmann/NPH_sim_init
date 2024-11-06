import glob
import os
import subprocess
import pandas as pd
import click

def replace_line(file_name, line_text, text):
    lines = open(file_name, 'r').readlines()
    for i,line in enumerate(lines):
        if line_text in line:
            line_num = i
            continue
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()

@click.command()
@click.option('--csv',default='NPH.csv',type=str,help='input simulation data file')

def main(csv):

    # INPUT PARAMETERS

    df = pd.read_csv(f'./{csv}', skiprows=0)
    simlist      = df['SIM']
    prdlist      = df['PRD']
    eqllist      = df['EQL']
    presslist    = df['P[bar]']
    templist     = df['T[K]']
    eqlframelist = df['eql_conf_time[ns]']
    timestep = df['timestep[fs]'][0]
    steplist = eqlframelist*1e6/timestep

    batch_VBT_header = f"""
"""

    with open(f"./NPH_gen_out/VBT.txt","w") as bashfile:
        bashfile.write(batch_VBT_header)

    #  Get VBT values from slurm output
    if os.path.exists("./NPH_gen_out/slurm_out.txt"):
        os.remove("./NPH_gen_out/slurm_out.txt")
    with open('./NPH_gen_out/slurm_out.txt','a') as saidah:
        for sim,prd,press,temp in zip(simlist,prdlist,presslist,templist):
            output=subprocess.run(f'grep "verlet-buffer-tolerance" \
                                  ./NPH_gen_out/vbt_tests/vbt_test_{sim}_{prd}_{press}_{temp}.txt \
                                    | grep -m 1 -o "...e-.."',
                                    shell=True,stdout=saidah,text=True)

    vbt_list = []
    with open('./NPH_gen_out/slurm_out.txt','r') as saidah:
        for line in saidah:
            vbt_list.append(float(line))

    with open('./reports/old_vbt_report.txt','a') as saidah:
        for sim,prd,press,temp in zip(simlist,prdlist,presslist,templist):
            output=subprocess.run(f'grep "verlet-buffer-tolerance" \
                                  ./NPH_gen_out/vbt_tests/vbt_test_{sim}_{prd}_{press}_{temp}.txt \
                                    | grep -m 1 -o "...e-.."',
                                    shell=True,stdout=saidah,text=True)

    #  Create copy of mdp files with VBT values
    for sim,prd,eql,press,temp,vbt in zip(simlist,prdlist,eqllist,presslist,templist,vbt_list):
        replace_line(f'./../{sim}/mdp/{prd}_{press}_{temp}.mdp', 'verlet-buffer-tolerance',
                     f'verlet-buffer-tolerance  = {vbt}\n')
        batch_frame = f"""mpirun -np 1 gmx_d grompp -f ./../{sim}/mdp/{prd}_{press}_{temp}.mdp \
                      -o ./../{sim}/{prd}_{press}_{temp} -pp ./../{sim}/{prd}_{press}_{temp} \
                      -p ./../{sim}/topol.top -po ./../{sim}/{prd}_{press}_{temp} \
                      -c ./../{sim}/frame_{eql}_{press}_{temp}.gro \
                      > ./NPH_gen_out/vbt_tests/vbt_out_{sim}_{prd}_{press}_{temp}.txt 2>&1
"""

        with open(f"./NPH_gen_out/VBT.txt","a") as bashfile:
            bashfile.write(batch_frame)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

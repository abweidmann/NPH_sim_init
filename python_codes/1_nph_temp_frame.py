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

    if os.path.exists("./NPH_gen_out/"):
        print('')
    else:
        os.mkdir("./NPH_gen_out/")

    batch_frame_header = """
"""

    with open("./NPH_gen_out/FRAME.txt","w") as bashfile:
        bashfile.write(batch_frame_header)

    for sim,prd,eql,press,temp,step in zip(simlist,prdlist,eqllist,presslist,templist,steplist):

        replace_line('./../{sim}/mdp/{prd}_{press}_{temp}.mdp', 'verlet-buffer-tolerance', 
                     ';verlet-buffer-tolerance  = 1.0e-7 \n')

        with open('./NPH_gen_out/out.txt','w') as saidah:
            output=subprocess.run(f'grep "step {int(step-1)} \
                                  " ./../{sim}/{eql}_{press}_{temp}.log -B 200 -A 200',
                                  shell=True,stdout=saidah,text=True)

        with open("./NPH_gen_out/out.txt", "r") as data:
            with open('./NPH_gen_out/temp.txt', "w") as temp_data:
                temp_v = 0
                for line in data.readlines():
                    if temp_v ==1:
                        temp_data.write(line)
                    temp_v = 0
                    if "Temperature" in line:
                        temp_v = 1

        with open("./NPH_gen_out/out.txt", "r") as data:
            with open('./NPH_gen_out/times.txt', "w") as temp_data:
                time_v = 0
                for line in data.readlines():
                    if time_v == 1:
                        temp_data.write(line)
                    time_v = 0
                    if "Time" in line:
                        time_v = 1

        times_names  = ['Steps', 'Time']
        temp_names = ['Kinetic En.','Total Energy','Conserved En.','Temperature','Pressure']

        dftemp = pd.read_csv(f'./NPH_gen_out/temp.txt', skiprows=0, header=None, \
                           delim_whitespace=True, names=temp_names)

        dftimes = pd.read_csv(f'./NPH_gen_out/times.txt', skiprows=0, header=None, \
                           delim_whitespace=True, names=times_names)

        df_total = pd.concat([dftimes,dftemp], axis=1, join='outer')
        df_final = df_total.dropna()

        # Chose frame with closest temperature to desired value
        df_closest = df_final.iloc[(df_final['Temperature']-temp).abs().argsort()[:1]]
        initial_frame = (df_closest['Time'].tolist())[0]
        initial_temp  = (df_closest['Temperature'].tolist())[0]

        #  Right batch file to export frame to .gro file
        batch_frame = f"""mpirun -np 1 gmx_d trjconv -f ./../{sim}/{eql}_{press}_{temp}.trr \
                      -o ./../{sim}/frame_{eql}_{press}_{temp}.gro \
                      -s ./../{sim}/{eql}_{press}_{temp}.tpr  -dump {initial_frame} <<E0F
0
E0F

mpirun -np 1 gmx_d grompp -f ./../{sim}/mdp/{prd}_{press}_{temp}.mdp \
-o ./../{sim}/{prd}_{press}_{temp} -pp ./../{sim}/{prd}_{press}_{temp} -p ./../{sim}/topol.top \
-po ./../{sim}/{prd}_{press}_{temp} -c ./../{sim}/frame_{eql}_{press}_{temp}.gro \
> ./NPH_gen_out/vbt_tests/vbt_test_{sim}_{prd}_{press}_{temp}.txt 2>&1 \n
"""

        with open(f"./NPH_gen_out/FRAME.txt","a") as bashfile:
            bashfile.write(batch_frame)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

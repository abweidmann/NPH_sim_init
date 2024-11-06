
import glob
import os
import subprocess
import pandas as pd
import click

@click.command()
@click.option('--csv',default='NPH.csv',type=str,help='input simulation data file')

def main(csv):
    # INPUT PARAMETERS
    df = pd.read_csv(f'./{csv}', skiprows=0)
    simlist	 = df['SIM']
    prdlist	 = df['PRD']
    eqllist	 = df['EQL']
    presslist    = df['P[bar]']
    templist     = df['T[K]']
    eqlframelist = df['eql_conf_time[ns]']
    timestep = df['timestep[fs]'][0]
    steplist = eqlframelist*1e6/timestep

    if os.path.exists("./reports/vbt_report.txt"):
        os.remove("./reports/vbt_report.txt")
    with open('./reports/vbt_report.txt','a') as saidah:
        for sim,prd,press,temp in zip(simlist,prdlist,presslist,templist):
            output=subprocess.run(f'grep "verlet-buffer-tolerance" \
                                  ./NPH_gen_out/vbt_tests/vbt_out_{sim}_{prd}_{press}_{temp}.txt \
                                    | grep -m 1 -o "...e-.."',
                                    shell=True,stdout=saidah,text=True)

    if os.path.exists("./reports/init_temp_report.txt"):
        os.remove("./reports/init_temp_report.txt")
    with open('./reports/init_temp_report.txt','a') as saidah:
        for sim,prd,press,temp in zip(simlist,prdlist,presslist,templist):
            output=subprocess.run(f'grep "NVE simulation: will use the initial temperature of" \
                                  NPH_gen_out/vbt_tests/vbt_test_{sim}_{prd}_{press}_{temp}.txt \
                                    | grep -m 1 -o "....... K"',
                                    shell=True,stdout=saidah,text=True)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

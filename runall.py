from string import Template
import os
workdir = '/work/wew12/elasticity/finalfixed/'
repodir = '/hpc/group/ultrasound/wew12/repos/elasticityfinal/'

E_bgs = [5000, 10000, 50000, 100000, 200000]#[100, 1000, 5000, 10000, 50000]
E_fbs = [5000, 10000, 50000, 100000, 200000]#[100, 1000, 5000, 10000, 50000]
polarities = ['along', 'across']
modes = ['cross', 'dotcross']
dvoxs = [0.1, 0.05]

with open("field_temp.py", "r") as f:
    template = Template(f.read())

for mode in modes:
    modedir = f"{workdir}mode_{mode}/"
    for dvox in dvoxs:
        voxdir = f"{modedir}dvox_{dvox:0.03f}/"
        for E_bg in E_bgs:
            bgdir = f"{voxdir}Ebg_{E_bg:0.03f}/"
            for E_fb in E_fbs:
                fbdir = f"{bgdir}Efb_{E_fb:0.03f}/"
                for polarity in polarities:
                    poldir = f"{fbdir}polarity_{polarity}/"
                    if not os.path.exists(poldir): os.makedirs(poldir)
                    os.chdir(poldir)
                    with open("runit.py", 'w') as f:
                        f.write(template.substitute(
                            dvox = dvox,
                            E_bg = E_bg,
                            E_fb = E_fb,
                            polarity = polarity,
                            savedir = poldir,
                            mode = mode
                        ))
                    command = f"cp {repodir}launchtestmatfield.sh {poldir}\n"
                    command += f"cp {repodir}genandlaunch.py {poldir}\n"
                    command += f"cp {repodir}make_fixed_grid.py {poldir}\n"
                    command += "sbatch launchtestmatfield.sh"
                    os.system(command)


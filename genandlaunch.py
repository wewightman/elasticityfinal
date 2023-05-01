from os import environ, system, getcwd, chdir
from time import ctime
from string import Template
import make_fixed_grid as mfg

from fem.mesh import bc
from fem.post.create_disp_dat import create_dat as create_disp_dat
from fem.post.create_res_sim import run as create_res_sim

def def_cross(refdir, workdir, shape, dvox, polarity, E_bg, E_fb, template="fieldpush_temp.dyn"):
    """Generate a simple cross fiber set"""
    retdir = getcwd()
    chdir(workdir)

    mfg.genAndLoadFibers(dvox, shape, mode="cross", polarity=polarity)
    partstr = "*PART\nBACKGROUND\n1,1,1,0,0,0,0\n*PART\nFibers\n2,1,2,0,0,0,0\n"

    print("COPYING DYNADECK TEMPLATE")
    with open(refdir+template, 'r') as f:
        dyntemp = Template(f.read())

    filled = dyntemp.substitute(
        pntload="$pntload",
        title="boopboopbedoop",
        savedir=workdir,
        E_bg = f"{int(E_bg):d}",
        E_fb = f"{int(E_fb):d}",
        fiber_defs = partstr
    )

    with open(workdir+"deck.dyn", 'w') as f:
        f.write(filled)
    
    # make it full symetery fixing only the bottom plane
    face_constraints = (('0,0,0,0,0,0', '0,0,0,0,0,0'),
                        ('0,0,0,0,0,0', '0,0,0,0,0,0'),
                        ('0,0,1,1,1,1', '0,0,0,0,0,0'))
    bc.apply_face_bc_only(face_constraints)

    chdir(retdir)
    return partstr

def def_dotcross(refdir, workdir, shape, dvox, polarity, E_bg, E_fb, template="fieldpush_temp.dyn"):
    retdir = getcwd()
    chdir(workdir)

    mfg.genAndLoadFibers(dvox, shape, mode="cross", polarity=polarity)
    partstr = "*PART\nBACKGROUND\n1,1,1,0,0,0,0\n*PART\nFibers\n2,1,2,0,0,0,0\n"

    print("COPYING DYNADECK TEMPLATE")
    with open(refdir+template, 'r') as f:
        dyntemp = Template(f.read())

    filled = dyntemp.substitute(
        pntload="$pntload",
        title="boopboopbedoop",
        savedir=workdir,
        E_bg = f"{int(E_bg):d}",
        E_fb = f"{int(E_fb):d}",
        fiber_defs = partstr
    )

    with open(workdir+"deck.dyn", 'w') as f:
        f.write(filled)

    # make it full symetery fixing only the bottom plane
    face_constraints = (('0,0,0,0,0,0', '0,0,0,0,0,0'),
                        ('0,0,0,0,0,0', '0,0,0,0,0,0'),
                        ('0,0,1,1,1,1', '0,0,0,0,0,0'))
    bc.apply_face_bc_only(face_constraints)

    chdir(retdir)
    return partstr

def runfield(Inorm, ncycles, dnode, fempath, fieldpath, repopath):
    """Interface with matlab to generate fieldII parameters
    NOTE: Assumes matlab is loaded to path

    Parameters:
    ----
    Inorm: the normalization 
    """

    # copy necessary files from repo dir to working dir
    # copy l74 parameter file
    command = f"cp {repopath}l74.json l74.json"
    system(command)

    # copy field sim parameter file
    command = f"cp {repopath}field_params.json field_params.json"
    system(command)
    
    # launch field simulation
    command = "matlab -nodisplay -nosplash -singleCompThread -r \"addpath('"
    +repopath+"'); runfield("+str(Inorm)+","+str(ncycles)+","+str(dnode)+",'"
    +fempath+"','"+fieldpath+"','n');exit;\""
    system(command)

def calldyna(workdir, curdeck="deck.dyn"):
    """Run dyna on the parameters"""

    print("Starting simulation")

    # load the name of the generated pointloads
    from glob import glob
    pntload = glob("PointLoads*")[0]

    with open(workdir + curdeck, 'r') as f:
        template = Template(f.read())

    filled = template.substitute(
        pntload = pntload
    )

    with open(workdir + curdeck, 'w') as f:
        f.write(filled)

    NTASKS = environ.get('SLURM_NTASKS', '8')

    system(('singularity exec -p -B {} /opt/apps/staging/ls-dyna-singularity/ls-dyna.sif ls-dyna-d ncpu={} i={} memory = 600000000'.format(workdir, NTASKS, curdeck)))

    create_disp_dat()

    create_res_sim(curdeck)

    print('FINISHED: {}'.format(ctime()))



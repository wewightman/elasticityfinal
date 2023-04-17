#!/bin/env python
#SBATCH --mem=8G
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --partition=ultrasound
##SBATCH --mail-user=wew12@duke.edu
##SBATCH --mail-type=END

from os import environ, system, getcwd, chdir
from socket import gethostname
from time import ctime
from string import Template
import numpy as np

from fem.mesh import GenMesh, bc
from fem.mesh.TopLoad import generate_loads
from fem.post.create_disp_dat import create_dat as create_disp_dat
from fem.post.create_res_sim import run as create_res_sim


from fem.mesh.CreateStructure import define_struct_type, findStructNodeIDs, findStructElemIDs, write_struct_elems

def def_hex_grid(refdir, workdir, dvox, shape, dfiber, rfibperp, rfibpar, E_bg, E_fb):
    """generate a muscle-like mesh in a hexagonally packked manner in the transverse plane
    
    Parameters:
    ----
    `refdir`: the directory containing all template scripts
    `workdir`: the directory to store all output files
    `dvox`: the dimesnion of each square voxel in cnm
    `shape`: the (x,y,z) shape of the symmetry model
    `dfiber`: the spacing between the centers of each fiber
    `rfiberperp`: radius of fiber perpendicular to the axis of symmetry
    `rfiberpar`: radius of the fiber along the fiber direction
    """
    print('STARTED MESHGENERATION: {}'.format(ctime()))
    print('HOST: {}'.format(gethostname()))
    retdir = getcwd()
    chdir(workdir)

    Nshape = [int(np.ceil(dim/dvox)) for dim in shape]
    shape = [n*dvox for n in Nshape]

    # generate the corners of the grid
    xxyyzz = (-shape[0], 0,  0, shape[1],  -shape[2], 0)
    GenMesh.run(xxyyzz, Nshape)

    # Prepare to generate collection of elipsoids
    struct_type ="ellipsoid"
    sopts = [
        0, 0, 0,                        # center coordinate in X,Y,Z - will be replaced in loop
        rfibperp, rfibpar, rfibperp,    # major axis extent from origin of elipse in X, Y Z direction 
        0, 0, 0                         # euler angles - Transform from material coordinates of X,Y,Z to x,y,z
    ]

    # spacing between fibers
    dlat = dfiber*np.cos(np.pi/6)
    dax = dfiber
    
    Nlat = int(shape[0] // dlat)
    Nax = int(shape[2] // dax)

    partstr = ""
    inde=2
    for ilat in range(Nlat):
        print(f"  {ilat:04d}|", end='')
        for iax in range(Nax):
            print("-", end='')
            try:
                # update location of elipsoid
                sopts[0] = -ilat * dlat
                sopts[2] = -(iax + (ilat%2)/2)* dax
                print(sopts[0], sopts[2])

                # find nodes and elements that correspond to this fiber and update element file
                structNodeIDs = findStructNodeIDs('nodes.dyn', struct_type, sopts)
                (elems, structElemIDs) = findStructElemIDs('elems.dyn', structNodeIDs)
                write_struct_elems('elems.dyn', inde, elems, structNodeIDs, structElemIDs)

                # make dyn definitions for each fiber
                partstr += f"*PART\nFIBER{inde-1:d}\n{inde},1,2,0,0,0,0\n"
                inde+=1
            except Exception as e:
                print(f"Skipping lat:{ilat}, ax:{iax}")
        print("|", end='\n')

    # cuttoff last newline
    partstr = partstr[:-1]

    print("COPYING DYNADECK TEMPLATE")
    with open(refdir+"maindyn_temp.dyn", 'r') as f:
        dyntemp = Template(f.read())

    filled = dyntemp.substitute(
        title="boopboopbedoop",
        E_bg = f"{int(E_bg):d}",
        E_fb = f"{int(E_fb):d}",
        fiber_defs = partstr
    )

    # make it quarter symmetry
    face_constraints = (('0,0,0,0,0,0', '1,0,0,1,1,1'),
                        ('0,1,0,1,1,1', '0,0,0,0,0,0'),
                        ('0,0,1,1,1,1', '0,0,0,0,0,0'))
    bc.apply_face_bc_only(face_constraints)

    with open(workdir+"deck.dyn", 'w') as f:
        f.write(filled)

    chdir(retdir)

def run_compression(workdir, dynadeck):
    print("Starting compression")
    chdir(workdir)
    # apply displacement condition to the zmax face
    generate_loads(loadtype='disp', direction=2, amplitude=-0.015,
                top_face=(0, 0, 0, 0, 0, 1), lcid=1)
    
    NTASKS = environ.get('SLURM_NTASKS', '8')

    system(('singularity exec -p -B {} /opt/apps/staging/ls-dyna-singularity/ls-dyna.sif ls-dyna-d ncpu={} i={} memory = 600000000'.format(workdir, NTASKS, dynadeck)))

    create_disp_dat()

    create_res_sim(dynadeck)

    print('FINISHED: {}'.format(ctime()))

def runfield(Inorm, ncycles, dnode, fempath, fieldpath, repopath):
    """Interface with matlab to generate fieldII parameters
    NOTE: Assumes matlab is loaded to path

    Parameters:
    ----
    Inorm: the normalization 
    """
    command = "matlab -nodisplay -nosplash -singleCompThread -r \"addpath('"
    +repopath+"'); runfield("+str(Inorm)+","+str(ncycles)+","+str(dnode)+",'"
    +fempath+"','"+fieldpath+"');exit;\""
    
    system(command)

import genandlaunch as gal
import os

dvox = 0.05

srcdir = "/hpc/group/ultrasound/wew12/repos/elasticityfinal/"
savedir = "/work/wew12/elasticity/finalproject/data/pushit/"
fieldpath = "/hpc/group/ultrasound/wew12/modules/field_ii_pro_matlab/m_files/"
fempath = "/hpc/group/ultrasound/wew12/modules/fem/fem/field/"

if not os.path.exists(savedir): os.makedirs(savedir)
os.chdir(savedir)

genparams = {
    'refdir':srcdir,
    'workdir':savedir,
    'dvox':dvox,
    'shape':[3, 3, 3],
    'dfiber':0.4,
    'rfibperp':0.05,
    'rfibpar':5,
    'E_bg':10,
    'E_fb':100,
    'template':"fieldpush_temp.dyn"
}

fiber_def = gal.def_hex_grid_full(**genparams)

fieldparams = {
    'Inorm':1000,
    'ncycles':400,
    'dnode':dvox,
    'fempath':fempath,
    'fieldpath':fieldpath,
    'repopath':srcdir,
    'sym':'n',
    'probe':"l74.json"
}

gal.runfield(**fieldparams)

dynaparams = {
    'workdir':savedir,
    'curdeck':"deck.dyn",
    'fiber_def':fiber_def,
    'E_bg':10,
    'E_fb':100,
    'template':"fieldpush_temp.dyn"
}

gal.calldyna(dynaparams)

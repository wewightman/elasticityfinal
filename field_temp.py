import genandlaunch as gal
import os

dvox = $dvox
E_bg = $E_bg
E_fb = $E_fb
polarity = $polarity
savedir = $savedir

srcdir = "/hpc/group/ultrasound/wew12/repos/elasticityfinal/"
fieldpath = "/hpc/group/ultrasound/wew12/modules/field_ii_pro_matlab/m_files/"
fempath = "/hpc/group/ultrasound/wew12/modules/fem/fem/field/"

if not os.path.exists(savedir): os.makedirs(savedir)
os.chdir(savedir)

genparams = {
    'refdir':srcdir,
    'workdir':savedir,
    'polarity':polarity,
    'dvox':dvox,
    'shape':[3, 3, 3],
    'E_bg':E_bg,
    'E_fb':E_fb,
    'template':"fieldpush_temp.dyn"
}

fiber_def = gal.def_$mode(**genparams)

fieldparams = {
    'Inorm':1000,
    'ncycles':400,
    'dnode':dvox,
    'fempath':fempath,
    'fieldpath':fieldpath,
    'repopath':srcdir,
    'probe':"l74.json"
}

gal.runfield(**fieldparams)

dynaparams = {
    'workdir':savedir,
    'curdeck':"deck.dyn"
}

gal.calldyna(dynaparams)

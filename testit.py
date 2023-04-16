import genandlaunch as gal

srcdir = "/home/wren/Documents/phdprojects/modules/elasticityfinal/"
savedir = "/home/wren/Documents/phdprojects/data/elasticity/"
shape = [1.5, 1.5, 3]

genparams = {
    'refdir':srcdir,
    'workdir':savedir,
    'dvox':0.05,
    'shape':shape,
    'dfiber':0.4,
    'rfibperp':0.075,
    'rfibpar':5,
    'E_bg':10,
    'E_fb':100
}

gal.def_hex_grid(**genparams)

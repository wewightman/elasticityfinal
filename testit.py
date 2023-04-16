import genandlaunch as gal

srcdir = "/work/wew12/elasticity/finalproject/manyfibers/"
savedir = "/work/wew12/elasticity/finalproject/data/prelimtest/"

genparams = {
    'refdir':srcdir,
    'workdir':savedir,
    'dvox':0.05,
    'shape':[1.5, 1.5, 3],
    'dfiber':0.4,
    'rfibperp':0.075,
    'rfibpar':5,
    'E_bg':10,
    'E_fb':100
}

gal.def_hex_grid(**genparams)
gal.run_compression(savedir, "deck.dyn")

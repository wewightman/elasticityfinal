import numpy as np
from fem.mesh import GenMesh

def genAndLoadFibers(dvox, extent, mode, polarity):
    Nx, Ny, Nz = [int(2*(ex/2//dvox)) for ex in extent]
    extent = [dvox*n for n in [Nx, Ny, Nz]]

    xyz = (-extent[0]/2, extent[0]/2, -extent[1]/2, extent[1]/2, -extent[2], 0.0)
    numElem = (Nx, Ny, Nz)
    GenMesh.run(xyz,numElem)

    with open("nodes.dyn", 'r') as f:
        a = f.readlines()

    aprime = a[2:-1]
    del a

    nodes = {}
    coords = []
    for a in aprime:
        splits = a[:-1].split(",")
        label = splits[0]
        coord = [float(A) for A in splits[1:]]
        nodes[label] = np.array(coord)
        coords.append(coord)

    coords = np.array(coords)
    x = np.unique(coords[:,0])
    x.sort()
    y = np.unique(coords[:,1])
    y.sort()
    z = np.unique(coords[:,2])
    z[::-1].sort()
    del coords

    with open("elems.dyn", 'r') as f:
        a = f.readlines()

    aprime = a[2:-1]
    del a

    elems = {}
    for a in aprime:
        # removed the newline and split the node definitions
        splits = a[:-1].split(",")
        elem = {
            'matid' : splits[1],
            'nodes' : splits[2:]
        }

        centroid = 0
        for node_id in elem['nodes']:
            centroid += nodes[node_id]/len(elem['nodes'])

        
        elem['centroid'] = centroid

        # save the element structure
        elems[splits[0]] = elem

    if mode == 'dotcross':
        if polarity == 'along':
            # Define multiple materials
            elemmap = np.ones((Nx,Ny,Nz))

            astep = 4
            scale0 = 4
            for inda in range(0, Nx-2, astep):
                scale = int(((inda/astep) % 2) * scale0)
                for inde in range(0, Nz-2, 8):
                    # cross
                    elemmap[(inda):(inda+4), :, (inde+1+scale):(inde+3+scale)] = 2
                    elemmap[(inda+1):(inda+3), :, (inde+scale):(inde+4+scale)] = 2

                    # dot
                    elemmap[(inda+1):(inda+3), :, (inde+1+scale+4):(inde+3+scale+4)] = 2
            elemmap[0,:,:] = 2

        elif polarity == 'across':
            # Define multiple materials
            elemmap = np.ones((Nx,Ny,Nz))

            astep = 4
            scale0 = 4
            for inda in range(0, Ny-2, astep):
                scale = int(((inda/astep) % 2) * scale0)
                for inde in range(0, Nz-2, 8):
                    # cross
                    elemmap[:, (inda):(inda+4), (inde+1+scale):(inde+3+scale)] = 2
                    elemmap[:, (inda+1):(inda+3), (inde+scale):(inde+4+scale)] = 2

                    # dot
                    elemmap[:, (inda+1):(inda+3), (inde+1+scale+4):(inde+3+scale+4)] = 2
            elemmap[:,0,:] = 2
        else:
            raise Exception("Failed polarity selection")
    elif mode == "cross":
        if polarity == 'along':
            # Define multiple materials
            elemmap = np.ones((Nx,Ny,Nz))

            for inda in range(0, Nx-2, 3):
                scale = int(((inda/3) % 2) * 2)
                for inde in range(0, Nz-2, 4):
                    elemmap[(inda):(inda+3), :, inde+1+scale] = 2
                    elemmap[inda+1, :, (inde+scale):(inde+3+scale)] = 2

            elemmap[0,:,:] = 2

        elif polarity == 'across':
            # Define multiple materials
            elemmap = np.ones((Nx,Ny,Nz))

            for inda in range(0, Nx-2, 3):
                scale = int(((inda/3) % 2) * 2)
                for inde in range(0, Nz-2, 4):
                    elemmap[:, (inda):(inda+3), inde+1+scale] = 2
                    elemmap[:, inda+1, (inde+scale):(inde+3+scale)] = 2
            elemmap[:,0,:] = 2
        else:
            raise Exception("Failed polarity selection")
    else:
        raise Exception("Failed mode selection")
    
    for key in elems.keys():
        xind = np.argmax(x > elems[key]['centroid'][0])-1
        yind = np.argmax(y > elems[key]['centroid'][1])-1
        zind = np.argmax(z < elems[key]['centroid'][2])-1
    
        elems[key]['matid'] = f"{int(elemmap[xind, yind, zind])}"
    
    with open("elems.dyn", 'w') as f:
        f.write("")
    with open("elems.dyn", 'a') as f:
        lines = "$ Written with custom fiber mapping\n*ELEMENT_SOLID\n"
        f.write(lines)
        for key in elems.keys():
            lines = f"{key},{elems[key]['matid']},"
            for node in elems[key]['nodes']:
                lines += node + ","
            lines = lines[:-1]
            lines += '\n'
            f.write(lines)
        lines = "*END\n"
        f.write(lines)

if __name__ == '__main__':
    genAndLoadFibers(0.05, [4, 4, 4], "dotcross", "along")

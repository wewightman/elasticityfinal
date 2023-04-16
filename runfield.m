function runfield(Inorm, ncycles, dnode, fempath, fieldpath)
    %% q2 script
    %addpath("/hpc/group/ultrasound/wew12/modules/fem/fem/field/");
    %addpath("/hpc/group/ultrasound/wew12/modules/field_ii_matlab/");
    addpath(fempath);
    addpath(fieldpath);
    
    %% Generate dyna files
    field2dyna('nodes.dyn', 'field_params.json', 'elems.dyn');
    
    %% Generate loads from field sims
    desiredfiles = dir("dyna-I*");
    % InputName,NormName,IsppaNorm,PulseDuration,cv,ElementVolume,sym,LCID,
    makeLoadsTemps(desiredfiles(1).name, desiredfiles(1).name, Inorm, ncycles, 4.2, dnode^3, 'q', 1);
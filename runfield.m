function runfield(Inorm, ncycles, dnode, fempath, fieldpath, sym)
    %% q2 script
    addpath(fempath);
    addpath(fieldpath);
    
    %% Generate dyna files
    field2dyna('nodes.dyn', 'field_params.json', 'elems.dyn');
    
    %% Generate loads from field sims
    desiredfiles = dir("dyna-I*");
    % InputName,NormName,IsppaNorm,PulseDuration,cv,ElementVolume,sym,LCID,
    makeLoadsTemps(desiredfiles(1).name, desiredfiles(1).name, Inorm, ncycles, 4.2, dnode^3, sym, 1);
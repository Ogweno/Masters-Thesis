%ProcessTraces
% Script to load up sac files, extract out some info, p-value etc
% Rotate traces, deconvolve traces -> then off to be stacked.

loadtools;
thresh = 0;
%% 1) Filter Event Directories
%
printinfo = 0; % On and off flag to print out processing results
dlist = filterEventDirs(workingdir,printinfo);
%% 2)  Convert sac file format, filter bad picks
%
picktol  = 2; % The picks should be more than PICKTOL seconds apart, or something may be wrong
[ptrace,strace,header,pslows,badpicks] = ...
    ConvertFilterTraces(dlist,pfile,sfile,picktol,printinfo);
fclose('all'); % Close all open files from reading
%% 3) Bin by p value (build pIndex)
%
npb = 2; % Average number of traces per bin
numbin = round((1/npb) * size(ptrace, 1));
pbinLimits = linspace(.035, .08, numbin);
checkind = 1;
[pIndex, pbin] = pbinIndexer(pbinLimits, pslows, checkind);
Pslow = pbin(any(pIndex)); % Strip out pbins with no traces
pIndex = pIndex(:,any(pIndex)); % Strip out indices with no traces
nbins = length(Pslow); % Number of bins we now have.
clear numbin pbinLimits checkind
%% 4) Normalize
dt = header{1}.DELTA;
ptrace = diag(1./max(ptrace,[],2)) * ptrace;
strace = diag(1./max(strace,[],2)) * strace;
%% Setup parallel toolbox
if ~matlabpool('size')
    workers = 4;
    matlabpool('local', workers)
end
%% 5)  Window with Taper and fourier transform signal.
adj = 0.1; % This adjusts the Tukey window used.
[wft, vft] = TaperWindowFFT(ptrace,strace,header,adj,0);
clear adj
%% 5) Impulse Response: Stack & Deconvolve
% prep all signals to same length N (power of 2)
% FFT windowed traces and stack in by appropriate pbin
% Build up spectral stack, 1 stack for each p (need to sort traces by
% p and put them into bins, all need to be length n
% Now fft windowed traces
discardBad = 1;
rec = zeros(nbins,size(wft,2));
parfor ii = 1:nbins
    [r,~,betax(ii)] = simdecf(wft(pIndex(:,ii),:), vft(pIndex(:,ii),:), -1); %#ok<PFBNS>
    rec(ii,:) = real(ifft(r));
end
% if discardBad flag set simdecf will return Nan arrays where it did not
% find a minimum, the following strips NaNs out and strips out appropriate
% Pslow indices.
if discardBad
    ind = isinf(betax);
    rec( ind  , : ) = [];
    pslow( ind ) = [];
end
%% 6) Filter Impulse Response
if 0
    fLow = db.filterLow;
    fHigh = db.filterHigh;
else
    fLow = 0.04;
    fHigh = 3;
end  
numPoles = 3;
brec = fbpfilt(rec, dt, fLow, fHigh, numPoles, 0);
%% Rescale by slowness
% Scale by increasing p value
pscale = wrev(1./pslow.^2)';
brec =  diag( pscale ./ max(abs(brec(:,1:1200)), [], 2)) * brec;
%% 7) MB Processing
if strcmp(method, 'bostock')
    % Get Newton method nonlinear regression and select Tps points
    [brec, pslow, tps, Tps, t1, t2] = nlregression(brec, pslow, tps);

    [ results ] = gridsearchMB(brec(:,1:round(45/dt)), Tps', dt, pslow);

    [bootVp, bootR, bootH, bootVpRx, bootHx] = ...
    bootstrapMB(brec(:,1:round(45/dt)), Tps, dt, pslow, 1024);

%% Kanamori Processing
elseif strcmp(method, 'kanamori')
    
    % Get Newton method nonlinear regression and select Tps points
    [brec, pslow, tps, Tps, t1, t2] = nlregression(brec, pslow, tps);
    
    [ results ] = gridsearchKan(brec(:,1:round(45/dt)), dt, pslow);
    
    [bootR, bootH, bootRHx] =  bootstrapKan(brec(:,1:round(45/dt)), dt, pslow, 1024);
end
%% Close parallel system
%matlabpool close

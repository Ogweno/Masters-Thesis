%ProcessTraces
% Script to load up sac files, extract out some info, p-value etc
% Rotate traces, deconvolve traces -> then off to be stacked.

loadtools;
thresh = 0;
%% 1) Filter Event Directories
%
printinfo = 1; % On and off flag to print out processing results
savelist  = 0;
dlist = filterEventDirs(workingdir,printinfo);
%% 2)  Convert sac file format, filter bad picks
%
picktol  = 2; % The picks should be more than PICKTOL seconds apart, or something may be wrong
[ptrace,strace,header,pslows,badpicks] = ...
    ConvertFilterTraces(dlist,pfile,sfile,picktol,printinfo);
fclose('all'); % Close all open files from reading
%% 3) Bin by p value (build pIndex)
%
if loadflag
    npb = db(end).npb;
else
    npb = 2; % Average number of traces per bin
end
numbin = round((1/npb)*size(ptrace,1));
pbinLimits = linspace(.035,.08,numbin);
checkind = 1;
[pIndex,pbin] = pbinIndexer(pbinLimits,pslows,checkind);
pslow = pbin(any(pIndex)); % Strip out pbins with no traces
pIndex = pIndex(:,any(pIndex)); % Strip out indices with no traces
nbins = length(pslow); % Number of bins we now have.
%% 4) Normalize
dt = header{1}.DELTA;

if true
    modratio = zeros(1,size(ptrace,1));
    
    for ii = 1:size(ptrace,1)
        t1 = round( (header{ii}.T1 - header{ii}.B) / dt);
        t3 = round( (header{ii}.T3 - header{ii}.B) / dt);
        t0 = t1 - round(20/dt);
        if t0 < 1
            t0 = 1;
        end
        m1 = var(ptrace(ii,  t1 : t3 ));
        m0 = var(ptrace(ii, t0 : t1 - round(2/dt)));
        modratio(ii) = m1/m0;

    end

    modratio(modratio < 20) = 1;
    modratio( (modratio < 100) & (modratio > 1) ) = 2;
    modratio(modratio < 500 & modratio > 2) = 3;
    modratio(modratio > 5) = 4;

    ptrace = diag(modratio) * diag(1./max(ptrace,[],2)) * ptrace;
    strace = diag(modratio) * diag(1./max(strace,[],2)) * strace;
end

%% 5)  Window with Taper and fourier transform signal.
%
viewtaper  = 0;
adj = 0.1; % This adjusts the Tukey window used.
[wft,vft,WIN] = TaperWindowFFT(ptrace,strace,header,adj,viewtaper);
%}

%% 5) Impulse Response: Stack & Deconvolve
% prep all signals to same length N (power of 2)
% FFT windowed traces and stack in by appropriate pbin
% Build up spectral stack, 1 stack for each p (need to sort traces by
% p and put them into bins, all need to be length n
% Now fft windowed traces
ind = 1;
viewFncs = 0;
h = waitbar(0,'Deconvolving...');
rec = zeros(nbins,size(wft,2));
for ii = 1:nbins
    [r,~,~] = simdecf(wft(pIndex(:,ii),:),vft(pIndex(:,ii),:),-1,viewFncs);
    % Take complex conjugate and reverse 1st half to recomplete fft
    %rtrace(ind,:) = real(ifft([r,conj(r(end-1:-1:2))]));
    rec(ii,:) = real(ifft(r));
    waitbar(ii/nbins,h)
end
close(h)

%% 6) Filter Impulse Response
if loadflag
    fLow = db(end).filterLow;
    fHigh = db(end).filterHigh;
else
    fLow = 0.04;
    fHigh = 1.5;
end    
numPoles = 2;
brec = fbpfilt(rec,dt,fLow,fHigh,numPoles,0);
brec = rec;
% Scale by increasing p value
pscale = (pslow + min(pslow)).^2;
pscale = pscale/max(pscale);

for ii=1:size(brec,1);
    brec(ii,:) = brec(ii,:)/(max(abs(brec(ii,1:1200))) + 0.0001) * (pscale(ii));
    %brec(ii,:)=brec(ii,:)/pslow(ii)^.2;    
end


%% Curvelet Denoise
thresh = 0.1;
brec = performCurveletDenoise(brec,dt,thresh);

%% Select tps
if loadflag
    t1 = db(end).t1; 
    t2 = db(end).t2;
else
    t1 = 4.5;
    t2 = 5.2;
end
[~,it] = max(brec(:,round(t1/dt) + 1: round(t2/dt)) + 1,[],2);
tps = (it + round(t1/dt)-1)*dt;

%}
%% 7) IRLS Newtons Method to find regression Tps
%

viewfit = 1; %View newton fit (0 is off)
H = 35; % Starting guesses for physical paramaters
alpha = 6.5;
beta = 3.5;
tol = 1e-4;  % Tolerance on interior linear solve is 10x of Newton solution
itermax = 300; % Stop if we go beyond this iteration number
damp = 0.2;

[ Tps,H,alpha,beta ] = newtonFit(H,alpha,beta,pslow',tps,itermax,tol,damp,viewfit);



%% 8) Grid and Line Search
%[ results ] = GridSearch(brec,Tps',dt,pslow);

[ results ] = GsearchKanamori(brec,dt,pslow);
%% Viewers
%{
    
    figure(567)
    bar(pbin,sum(pIndex,1))
    title(sprintf('pvalue histogram from station %s',station))
    xlabel('pvalue')
    ylabel('number of traces in pbin')
%}
%%
% View Earth Response
%{
t = [1:size(brec,2)] * dt;
    for ii = 1:size(brec,1)
        figure(5)
        plot(brec(ii,round(t1/dt) + 1: round(t2/dt)))
        title(sprintf('trace %i',ii))
        %hold on
        %plot(brtrace(ii,:))
        pause(1)
    end
%}



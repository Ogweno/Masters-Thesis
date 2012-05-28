%ProcessTraces
% Script to load up sac files, extract out some info, p-value etc
% Rotate traces, deconvolve traces -> then off to be stacked.

loadtools;

%% 1) Filter Event Directories
%
printinfo = 1; % On and off flag to print out processing results
savelist  = 0;
%listname  = [station,'_Dlist'];
dlist = filterEventDirs(workingdir,printinfo);
%}
%% 2)  Convert sac file format, filter bad picks
%
picktol  = 2; % The picks should be more than PICKTOL seconds apart, or something may be wrong
[ptrace,strace,header,pslows,badpicks] = ...
    ConvertFilterTraces(dlist,rfile,zfile,picktol,printinfo);
fclose('all'); % Close all open files from reading
%}
%% 3) Bin by p value (build pIndex)
%
npb = 2; % Average number of traces per bin
numbin = round((1/npb)*size(ptrace,1));
pbinLimits = linspace(.035,.08,numbin);
checkind = 1;
[pIndex,pbin] = pbinIndexer(pbinLimits,pslows,checkind);
pslow = pbin(any(pIndex)); % Strip out pbins with no traces
pIndex = pIndex(:,any(pIndex)); % Strip out indices with no traces
nbins = length(pslow); % Number of bins we now have.
%}
%% 4) Normalize
dt = header{1}.DELTA;
ext = round(20/dt);
%{
for ii = 1:size(ptrace,1)
    T1 = round((header{1}.T1 - header{1}.B)/dt);
    normnoise = norm(ptrace(ii, 1 : ext));
    normP = norm(ptrace(ii, T1 : T1 + ext ));
    nr = (normP/normnoise) *sqrt(normP);
    P(ii,:) = (ptrace(ii,:)) .* nr;
    S(ii,:) = (strace(ii,:)) .* nr;
end
ptrace = P;
strace = S;
%}
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

%% Delete bad entries
%{
while true
    fig = figure(1111);
    csection(rec(:,1:round(26/dt)),0,dt);
    [X,Y] = ginput(1);
    usr = input('Are you finished? "y" for yes, any other key to keep deleting: ','s');
    X = floor(X);
    rec(X,:) = [];
    pslow(X) = [];
    
    if strcmp(usr,'y')
       figure(1111);
        csection(rec(:,1:round(26/dt)),0,dt);
        break
       
    else
        continue
    end
end
close(fig)
%}
%% 6) Filter Impulse Response
fLow = 0.04;
fHigh = 1.4;
numPoles = 2;
%brec = fbpfilt(rec,dt,fLow,fHigh,numPoles,0);
brec = rec;
% Scale by increasing p value
pscale = (pslow + min(pslow)).^2;
pscale = pscale/max(pscale);


for ii=1:size(brec,1);
    brec(ii,:) = brec(ii,:)/(max(abs(brec(ii,1:1200))) + 0.0001) * (pscale(ii));
    %brec(ii,:)=brec(ii,:)/pslow(ii)^.2;    
end


%% Select tps
%if exist('db','var')
%    t1 = db(1).t1; % Search max between these two windows (in secs after p arrival)
%    t2 = db(1).t2;
%else
    t1 = 3.9;
    t2 = 4.7;
%end
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

%% Curvelet Denoise
thresh = 0.6;
% Set curvelet options
brec = performCurveletDenoise(brec,dt,thresh);

%% 8) Grid and Line Search
[ results ] = GridSearch(brec,Tps',dt,pslow);

%[ results ] = GsearchKanamori(brec,dt,pslow);
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





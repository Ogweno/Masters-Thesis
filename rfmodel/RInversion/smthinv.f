c
c  smthinv - a smoothness suite receiver function inversion program
c
c  VERSION 2.1 George Randall and Chuck Ammon 1997
c
c     This version uses the Poisson's Ratio of the Initial Model
c
      program smthinv
      parameter(nlmax = 45, ntmax = 520, nsmax = 2, ndat = ntmax*nsmax+
&      2*nlmax)
c     dimension alpha(nlmax),beta(nlmax),rho(nlmax),thiki(nlmax)
      character*32 modela,title
      real minsigma,maxsigma,dsigma
      integer inunit,ounit,oun2,icount
      logical porsv
      character*24 todays_date
      common /seismo/ seis(ntmax,nsmax), dt(nsmax), dura(nsmax), dly(
&      nsmax),gauss(nsmax),p(nsmax),nt(nsmax),porsv(nsmax)
      common /imodel/alpha(nlmax),beta(nlmax),thiki(nlmax),rho(nlmax),
&      nlyrs
      common /innout/ inunit,ounit
      real tfraction
      real fmin
      integer npasses
      logical hpfilter, yesno
      common /filter/ fmin, npasses, hpfilter
c
      inunit = 5
      ounit = 6
      oun2 = 8
c
c**********************************************************************************************
c     Where to place blame
      write(ounit,'(/)')
      write(ounit,*) 
&      '**********************************************************'
      write(ounit,*)'smthinv - Receiver function inversion program.'
      write(ounit,*)'          VERSION 2.1 July 1997'
      write(ounit,*)'    Charles J. Ammon and George Randall.'
      write(ounit,*)
&      'Additional routines by George Zandt and Tom Owens.'
      write(ounit,*) 
&      '**********************************************************'
c**********************************************************************************************
      call fdate(todays_date)
      write(ounit,*) 'Inversion run on: ',todays_date
      write(ounit,*) 
&      '**********************************************************'
      write(ounit,*)'Maximum Number of points in each waveform = 512'
      write(ounit,*) 
&      '**********************************************************'
c**********************************************************************************************
c
      do 23000 i = 1,nlmax 
         alpha(i) = 0.
         beta(i) = 0.
         rho(i) = 0.
         thiki(i) = 0.
23000    continue
c
c************************************************************************************************
c      p = true
c      sv = false
c************************************************************************************************
c
      do 23002 i = 1,nsmax
         porsv(i) = .true.
23002    continue
c
c************************************************************************************************
      write(ounit,*)'input velocity model:'
      read(inunit,'(a)')modela
      write(ounit,*)'Enter the max number of iterations per inversion'
      read(inunit,*) maxiter
      write(ounit,*)'Enter the minimum smoothing trade-off parameter'
      read(inunit,*) minsigma
      write(ounit,*)'Enter the maximum smoothing trade-off parameter'
      read(inunit,*) maxsigma
      write(ounit,*)'Enter Singular Value truncation fraction'
      read(inunit,*) tfraction
      hpfilter = yesno('Apply a high-pass filter to waveforms? ')
      if(.not.(hpfilter))goto 23004
         write(ounit,*)'Enter the corner frequency.'
         read(inunit,*) fmin
         write(ounit,*) 'Enter the number of filter passes (1 or 2).'
         read(inunit,*) npasses
c
c************************************************************************************************
c - - read in the waveform for the inversions
c************************************************************************************************
c
23004 continue
      call getseis(ns,seis,ntmax,nsmax,dt,dura,dly,gauss,p,nt,porsv)
c************************************************************************************************
c     loop over the smoothing paramter: sigmab
c************************************************************************************************
c
      icount = 1
      dsigma = (maxsigma - minsigma)/10
c
c     while
23006 if(.not.(sigjmpb .le. maxsigma))goto 23007
         sigjmpb = minsigma + (icount-1)*dsigma
c************************************************************************************************
         write(ounit,*) ' '
         write(ounit,*) 
&         '**********************************************************'
         write(ounit,*)'Smoothness trade-off parameter = ', sigjmpb
         write(ounit,*) 
&         '**********************************************************'
         write(ounit,*) ' '
c
c************************************************************************************************
c - - read in the initial velocity model
c************************************************************************************************
c
         open(unit=oun2,file=modela)
         rewind=oun2
         read(oun2,100)nlyrs,title
100      format(i3,1x,a32)
         do 23008 i1 = 1,nlyrs 
            read(oun2,110)idum,alpha(i1),beta(i1),rho(i1),thiki(i1),
&            dum1,dum2,dum3,dum4,dum5
23008       continue
110      format(i3,1x,9f8.4)
         close(unit=oun2)
c
c************************************************************************************************
c        invert the waveform
c************************************************************************************************
         invnum = icount
c
         call jinv(sigjmpb,maxiter,ns,invnum,tfraction)
c************************************************************************************************
c
         icount = icount + 1
         goto 23006
c     endwhile
23007 continue
      stop
      end

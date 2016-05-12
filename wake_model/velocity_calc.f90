! module load python/2/7
! module load compiler_gnu/4.9.2
! f2py -c  --opt=-O2 -m _velcalc velocity_calc.f90

subroutine overlay(xt,ys,coef,fun)
  implicit none
  integer, parameter :: dp = kind(0.d0)
  ! in
  real(dp), intent(in) :: xt,ys
  real(dp), dimension(10), intent(in) :: coef
  ! out
  real(dp), intent(out) :: fun
  ! local

  fun = coef(1) + coef(2)*xt + coef(3)*ys + coef(4)*xt**2 + coef(5)*xt*ys + &
  coef(6)*ys**2 + coef(7)*xt**3 + coef(8)*xt**2*ys + coef(9)*xt*ys**2 + &
  coef(10)*ys**3

end subroutine overlay


subroutine veldist(dn,lat,men,sdv1,sdv2,sdv3,sdv4,rat,tns,spr1,spr2,spr3,spr4,&
  scl1,scl2,scl3,sdv_gom,spr_gom,vel)
  implicit none
  integer, parameter :: dp = kind(0.d0)
  ! in
  real(dp), intent(in) :: dn,lat,men,sdv1,sdv2,sdv3,sdv4,rat,tns
  real(dp), intent(in) :: spr1,spr2,spr3,spr4,scl1,scl2,scl3,sdv_gom,spr_gom
  ! out
  real(dp), intent(out) :: vel
  ! local
  real(dp) :: sdv_v,spr_v,f1,f2,pi
  intrinsic exp
  intrinsic sqrt
  intrinsic abs
  ! constants
  pi = 3.1415926535897932_dp

  if (sdv_gom == 0.0_dp) then
    sdv_v = sdv3*sdv2*sdv1*exp(sdv2*dn)*exp(-sdv1*exp(sdv2*dn))+sdv4
    if (sdv_v < 1.0e-8_dp) then
      sdv_v = 1.0e-8_dp
    end if
  else if (sdv_gom == 1.0_dp) then
    sdv_v = sdv1
    if (sdv_v < 1.0e-8_dp) then
      sdv_v = 1.0e-8_dp
    end if
  end if

  if (spr_gom == 0.0_dp) then
    spr_v = spr3*spr2*spr1*exp(spr2*dn)*exp(-spr1*exp(spr2*dn))!+spr4
    if (spr_v < 1.0e-8_dp) then
      spr_v = 1.0e-8_dp
    end if
  else if (spr_gom == 1.0_dp) then
    spr_v = 1.0_dp
  end if

  f1 = -1.0_dp/(sdv_v*sqrt(2.0_dp*pi))*exp(-((lat/spr_v)-men)**2/(2.0_dp*sdv_v**2))&
  *(1.0_dp/(1.0_dp+exp(rat*abs((lat/spr_v))-tns)))
  f2 = scl3*scl2*scl1*exp(scl2*dn)*exp(-scl1*exp(scl2*dn))

  vel = f1*f2 + 1.0_dp

end subroutine veldist


subroutine sheet(ndata,xttr,ystr,posdn,poslt,coef0,coef1,coef2,coef3,coef4,coef5,coef6,&
  coef7,coef8,coef9,coef10,coef11,coef12,coef13,sdv_gom,spr_gom,vel)
  implicit none
  integer, parameter :: dp = kind(0.d0)
  ! in
  integer, intent(in) :: ndata
  real(dp), intent(in) :: sdv_gom,spr_gom
  real(dp), dimension(10), intent(in) :: coef0,coef1,coef2,coef3,coef4,coef5,coef6,coef7,coef8
  real(dp), dimension(10), intent(in) :: coef9,coef10,coef11,coef12,coef13
  real(dp), dimension(ndata), intent(in) :: xttr,ystr,posdn,poslt
  ! out
  real(dp), dimension(ndata), intent(out) :: vel
  ! local
  integer :: i
  real(dp) :: men,sdv1,sdv2,sdv3,sdv4,rat,tns
  real(dp) :: spr1,spr2,spr3,spr4,scl1,scl2,scl3

  do i = 1,ndata
    call overlay(xttr(i),ystr(i),coef0,men)
    call overlay(xttr(i),ystr(i),coef1,sdv1)
    call overlay(xttr(i),ystr(i),coef2,sdv2)
    call overlay(xttr(i),ystr(i),coef3,sdv3)
    call overlay(xttr(i),ystr(i),coef4,sdv4)
    call overlay(xttr(i),ystr(i),coef5,rat)
    call overlay(xttr(i),ystr(i),coef6,tns)
    call overlay(xttr(i),ystr(i),coef7,spr1)
    call overlay(xttr(i),ystr(i),coef8,spr2)
    call overlay(xttr(i),ystr(i),coef9,spr3)
    call overlay(xttr(i),ystr(i),coef10,spr4)
    call overlay(xttr(i),ystr(i),coef11,scl1)
    call overlay(xttr(i),ystr(i),coef12,scl2)
    call overlay(xttr(i),ystr(i),coef13,scl3)

    if (sdv1 < 0.0_dp) then
      sdv1 = 0.0_dp
    end if
    if (sdv2 < 0.0_dp) then
      sdv2 = 0.0_dp
    end if
    ! if (sdv3 < 0.0_dp) then
    !   sdv3 = 0.0_dp
    ! end if
    ! if (sdv4 < 0.0_dp) then
    !   sdv4 = 0.0_dp
    ! end if
    if (rat < 0.0_dp) then
      rat = 0.0_dp
    end if
    if (tns < 0.0_dp) then
      tns = 0.0_dp
    end if
    if (spr1 < 0.0_dp) then
      spr1 = 0.0_dp
    end if
    if (spr2 < 0.0_dp) then
      spr2 = 0.0_dp
    end if
    ! if (spr3 < 0.0_dp) then
    !   spr3 = 0.0_dp
    ! end if
    ! if (spr4 < 0.0_dp) then
    !   spr4 = 0.0_dp
    ! end if
    if (scl1 < 0.0_dp) then
      scl1 = 0.0_dp
    end if
    if (scl2 < 0.0_dp) then
      scl2 = 0.0_dp
    end if
    if (scl3 < 0.0_dp) then
      scl3 = 0.0_dp
    end if

    call veldist(posdn(i),poslt(i),men,sdv1,sdv2,sdv3,sdv4,rat,tns,spr1,spr2,spr3,spr4,&
      scl1,scl2,scl3,sdv_gom,spr_gom,vel(i))

  end do

end subroutine sheet

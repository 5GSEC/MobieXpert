#!/bin/csh -f
# $Header: /project/emerald/emerald_devel_v6/share/RCS/get_os_syms.csh,v 1.1.1.2 2008/03/07 23:05:05 skinner Exp mwfong $

#set echo

set _OS_SYSN          = `uname -s | tr "-" "_"`
set _OS_VERS          = `uname -r | cut -d. -f1-2 | cut -d- -f1`
set _OS_VERS_STR      = `uname -r | cut -d. -f1-2 | cut -d- -f1 | tr '.' '_'`
set _OS_ARCH          = `uname -m | sed 's/ /_/g'`
set _OS_NAME          = $_OS_SYSN-$_OS_VERS
set _OS_NAME_ARCH     = $_OS_SYSN-$_OS_ARCH/$_OS_VERS
set _OS_NAME_FULL     = $_OS_NAME_ARCH
set _LINUX_VARIANT    = ""
set _LINUX_SUBVARIANT = ""

if (-r /etc/fedora-release) then

  # [root@orange root]# cat /etc/fedora-release 
  # Fedora Core release 1.90 (FC2 Test 1)
  # -sh-3.00# cat /etc/fedora-release 
  # Fedora Core release 3 (Heidelberg)
  # [mwfong@kittyhawk ~]$ cat /etc/fedora-release 
  # Fedora Core release 4 (Stentz)

  set _LINUX_SUBVARIANT = `egrep '.*\(FC[0-9].*' /etc/fedora-release`
  if ("$_LINUX_SUBVARIANT" != "") then
     set _LINUX_SUBVARIANT = `cat /etc/fedora-release | sed 's/.*(\(.*\)).*/\1/'`
  else
     set _LINUX_SUBVARIANT = FC`cat /etc/fedora-release | sed -E 's/.+release ([0-9.]+).*/\1/'`
  endif

  set _LINUX_SUBVARIANT = `echo $_LINUX_SUBVARIANT | sed 's/ /_/g'`

  set _OS_NAME_FULL = $_OS_SYSN-$_OS_ARCH/$_LINUX_SUBVARIANT-$_OS_VERS
  set _LINUX_VARIANT = FedoraCore

else if (-r /etc/redhat-release) then

  # [mwfong@orion ~]$ cat /etc/redhat-release 
  # Red Hat Linux release 7.3 (Valhalla)

  set _LINUX_SUBVARIANT = RH`cat /etc/redhat-release | sed -e 's/.*release \(.*\) .*/\1/' -e 's/ /_/g'`
  set _OS_NAME_FULL = $_OS_SYSN-$_OS_ARCH/$_LINUX_SUBVARIANT-$_OS_VERS
  set _LINUX_VARIANT = RedHat

else if (-e /etc/debian_version) then

  set _LINUX_VARIANT = Debian
  set _OS_NAME_FULL = $_OS_SYSN-$_OS_ARCH/$_LINUX_VARIANT-$_OS_VERS

else if (-r /etc/SuSE-release) then

  set _LINUX_VARIANT = SuSE
  set _OS_NAME_FULL = $_OS_SYSN-$_OS_ARCH/$_LINUX_VARIANT-$_OS_VERS

else if (-r /etc/gentoo-release) then

  set _LINUX_VARIANT = Gentoo
  set _OS_NAME_FULL = $_OS_SYSN-$_OS_ARCH/$_LINUX_VARIANT-$_OS_VERS

endif

if ( ("$_LINUX_SUBVARIANT" == "") && ("$_LINUX_VARIANT" != "") ) then
  set _LINUX_SUBVARIANT = "$_LINUX_VARIANT"
endif

set _fHaveError = 0

if ($#argv != 1) then
  set _fHaveError = 1
else
  set _option = $1

  switch ($_option)
    case OS_SYSN:
      echo $_OS_SYSN
      breaksw

    case OS_VERS:
      echo $_OS_VERS
      breaksw

    case OS_VERS_STR:
      echo $_OS_VERS_STR
      breaksw

    case OS_ARCH:
      echo $_OS_ARCH
      breaksw

    case OS_NAME:
      echo $_OS_NAME
      breaksw

    case OS_NAME_ARCH:
      echo $_OS_NAME_ARCH
      breaksw

    case OS_NAME_FULL:
      echo $_OS_NAME_FULL
      breaksw

    case LINUX_VARIANT:
      echo $_LINUX_VARIANT
      breaksw

    case LINUX_SUBVARIANT:
      echo $_LINUX_SUBVARIANT
      breaksw

    default
      echo "Unrecognized option: $_option"
      set _fHaveError = 1
      breaksw
  endsw
endif

if ($_fHaveError) then
  echo "`basename $0` <symbol>"

cat <<EOF
  where <symbol> must be
    OS_SYSN             name of the operating system                        $_OS_SYSN
    OS_VERS             operating system release level                      $_OS_VERS
    OS_VERS_STR         same as above, but suitable for cpp -D definition   $_OS_VERS_STR
    OS_ARCH             machine hardware name (class)                       $_OS_ARCH
    OS_NAME             OS + version                                        $_OS_NAME
    OS_NAME_ARCH        OS + version + architecture                         $_OS_NAME_ARCH
    OS_NAME_FULL        OS [+ OS release] + version + architecture          $_OS_NAME_FULL
    LINUX_VARIANT       "", FedoraCore, RedHat, Debian, SuSE, Gentoo        $_LINUX_VARIANT
    LINUX_SUBVARIANT    "", FC<n>, RH<n>, Debian, SuSE, Gentoo              $_LINUX_SUBVARIANT
EOF
  exit 1
endif

exit 0

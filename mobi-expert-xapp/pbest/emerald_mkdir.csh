#!/bin/csh -f
# $Header: /project/emerald/emerald_devel_v6/share/RCS/emerald_mkdir.csh,v 1.1.1.2 2006/03/30 00:11:38 skinner Exp $

#set echo

set _fHaveError = 0

if ($#argv == 0) then
  set _fHaveError = 1
else
  if      ($#argv == 1) then
    set _dir = $1
  else if ($#argv == 2) then
    set _dir = `echo $2/$1 | sed 's/\/\//\//'`
  else
    echo "Error: too many arguments"
    set _fHaveError = 1
  endif
endif

if ($_fHaveError) then
  echo "`basename $0` [<prefix>] <dir>"
  exit 1
endif

if ( ! -d $_dir) then

  # Find the first missing directory
  set _pdir  = $_dir
  set _ppdir = `dirname $_pdir`
  while ( ! -d $_ppdir )
    set _pdir  = $_ppdir
    set _ppdir = `dirname $_pdir`
  end

  mkdir -p $_dir
  set _eGroup = "`grep emerald /etc/group`"
  if ("$_eGroup" != "") then
    chgrp -R emerald $_pdir 
  endif
  chmod -R g+s     $_pdir 
endif

exit 0

POWSPEC=/Users/changhyun/heasoft-6.27.2/x86_64-apple-darwin19.3.0/bin/powspec
HOME=/Users/changhyun/suzaku/research/data/403044020_timing/xis/event_cl
PS2PDF=/usr/local/bin/ps2pdf

cd $HOME

for BINSIZE in {2..200}
do
  echo $BINSIZE
  $POWSPEC <<EOF
ae403044020xi0_0_3x3n090a_cl.evt.gz
/Users/changhyun/heasoft-6.27.2/x86_64-apple-darwin19.3.0/xrdefaults/default_win.wi
$BINSIZE
INDEF
INDEF
2
default
yes
/xw
log x
log y
plot
hardcopy bin$BINSIZE.ps/cps
EOF

  $PS2PDF bin$BINSIZE.ps

done

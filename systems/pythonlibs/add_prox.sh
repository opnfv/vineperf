VINEPERFENV_DIR="$HOME/vsperfenv"
VINEPERF_DIR="$HOME/vineperf"

if [ ! -d "$VINEPERFENV_DIR" ] ; then
    echo "Directory $VINEPERFENV_DIR should exists. Please complete normal installation process"
    exit
fi

(source "$VINEPROXENV_DIR"/bin/activate
git clone https://gerrit.opnfv.org/gerrit/samplevnf /tmp/samplevnf
cd /tmp/samplevnf/VNFs/DPPD-PROX/helper-scripts/rapid
python setup.py build
python setup.py install
rm -rf /tmp/samplevnf)

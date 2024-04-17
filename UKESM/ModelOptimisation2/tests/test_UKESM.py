import pytest
from pathlib import Path

from ModelOptimisation2.UKESM import UKESM

CONFIG = \
"""
[file:ATMOSCNTL]
source=namelist:configid namelist:nlstcgen namelist:nlst_mpp namelist:run_track namelist:run_calc_pmsl namelist:lbc_options namelist:run_nudging namelist:run_sl namelist:run_diffusion namelist:run_cosp namelist:radfcdia namelist:r2swclnl namelist:r2lwclnl namelist:clmchfcg namelist:acp namelist:acdiag namelist:jules_nvegparm namelist:jules_pftparm namelist:jules_triffid namelist:jules_elevate (namelist:jules_urban2t_param) namelist:iau_nl namelist:tuning_segments (namelist:nlstcall_pp(:)) (namelist:nlstcall_nc(:)) namelist:nlstcall_nc_options

[namelist:iau_nl]
diagcloud_applycomplimits=.true.
diagcloud_nummaxloops=150
diagcloud_qn_compregimelimit={diagcloud_qn_compregimelimit}
diagcloud_tol_fm=0.00000
diagcloud_tol_q=0.00000
!!iau_apexmin=0
!!iau_cutoff_period=
iau_endmin=0
iau_filtertype=1
iau_nontrop_max_p={iau_nontrop_max_p}
!!iau_nontrop_max_q=3.0000e-6
!!iau_nontrop_max_rh=0.100
!!iau_nontrop_min_q=1.0000e-6
iau_qlimitscallfreq=2
!!iau_sbe_period=0

[namelist:items(37619932)]
ancilfilename='$UM_INSTALL_DIR/ancil/atmos/n48e/aerosol_clims/sslt/v2/qrclim.sslt70'
domain=1
!!interval=1
l_ignore_ancil_grid_check=.false.
!!netcdf_varname='unset','unset'
!!period=1
source=2
stash_req=357,358
update_anc=.false.
!!user_prog_ancil_stash_req=
!!user_prog_rconst=0.0

"""


@pytest.fixture
def rundir(tmpdir_factory):
    res = tmpdir_factory.mktemp("UKESM")
    return res


def model_setup(rundir):
    outdir = Path(rundir, "app", "um")
    outdir.mkdir(parents=True)
    with open(outdir / 'rose-app.conf', 'w') as cfg:
        cfg.write(CONFIG.format(
            iau_nontrop_max_p='4.0000e+4',
            diagcloud_qn_compregimelimit='20.000'))


def test_UKESM_fail(rundir):
    model = UKESM(rundir)

    with pytest.raises(LookupError):
        model.write_params({'ZZ': 'fail'})


def test_UKESM(rundir):
    model_setup(rundir)
    model = UKESM(Path(rundir))

    params = {'iau_nontrop_max_p': 50000.,
              'diagcloud_qn_compregimelimit': 30.}

    model.write_params(params)

    outdir = Path(rundir, "app", "um")
    assert (outdir / 'rose-app.conf~').exists()

    assert (outdir / 'rose-app.conf').read_text() == \
        CONFIG.format(
            iau_nontrop_max_p=50000.,
            diagcloud_qn_compregimelimit=30.)

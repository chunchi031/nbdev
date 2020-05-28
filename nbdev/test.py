# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04_test.ipynb (unless otherwise specified).

__all__ = ['get_all_flags', 'get_cell_flags', 'NoExportPreprocessor', 'test_nb']

# Cell
from .imports import *
from .sync import *
from .export import *
from .export import _mk_flag_re

from nbconvert.preprocessors import ExecutePreprocessor

# Cell
class _ReTstFlags():
    "Provides test flag matching regular expressions"
    def __init__(self, all_flag): self.all_flag = all_flag

    def findall(self, source):
        "Compile at first use but not before since patterns need `Config().tst_flags`"
        if not hasattr(self, '_re'):
            tst_flags = Config().get('tst_flags', '')
            _re_all, _re_magic_all = ('all_', '[ \t]+all') if self.all_flag else ('', '')
            self._re = _mk_flag_re(False, f"{_re_all}({tst_flags})", 0,
                "Matches any line with a test flag and catches it in a group")
            self._re_magic = _mk_flag_re(True, f"({tst_flags})_test{_re_magic_all}", 0,
                "Matches any line with a magic test flag and catches it in a group")
        return self._re.findall(source) + self._re_magic.findall(source)

# Cell
_re_all_flag = _ReTstFlags(True)

# Cell
def get_all_flags(cells):
    "Check for all test flags in `cells`"
    if len(Config().get('tst_flags',''))==0: return []
    result = []
    for cell in cells:
        if cell['cell_type'] == 'code': result.extend(_re_all_flag.findall(cell['source']))
    return set(result)

# Cell
_re_flags = _ReTstFlags(False)

# Cell
def get_cell_flags(cell):
    "Check for any special test flag in `cell`"
    if cell['cell_type'] != 'code' or len(Config().get('tst_flags',''))==0: return []
    return _re_flags.findall(cell['source'])

# Cell
class NoExportPreprocessor(ExecutePreprocessor):
    "An `ExecutePreprocessor` that executes cells that don't have a flag in `flags`"
    def __init__(self, flags, **kwargs):
        self.flags = flags
        super().__init__(**kwargs)

    def preprocess_cell(self, cell, resources, index):
        if 'source' not in cell or cell['cell_type'] != "code": return cell, resources
        for f in get_cell_flags(cell):
            if f not in self.flags:  return cell, resources
        res = super().preprocess_cell(cell, resources, index)
        return res

# Cell
def test_nb(fn, flags=None):
    "Execute tests in notebook in `fn` with `flags`"
    os.environ["IN_TEST"] = '1'
    if flags is None: flags = []
    try:
        nb = read_nb(fn)
        for f in get_all_flags(nb['cells']):
            if f not in flags: return
        ep = NoExportPreprocessor(flags, timeout=600, kernel_name='python3')
        pnb = nbformat.from_dict(nb)
        ep.preprocess(pnb)
    finally: os.environ.pop("IN_TEST")
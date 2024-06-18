
from dataclasses import dataclass
import typing
import typing_extensions

from flytekit.core.annotation import FlyteAnnotation

from latch.types.metadata import NextflowParameter
from latch.types.file import LatchFile
from latch.types.directory import LatchDir, LatchOutputDir

# Import these into your `__init__.py` file:
#
# from .parameters import generated_parameters

generated_parameters = {
    'input': NextflowParameter(
        type=LatchFile,
        default=None,
        section_title='Input/output options',
        description='Input raw / mzML files listed in a tsv file (see help for details)',
    ),
    'outdir': NextflowParameter(
        type=typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})],
        default=None,
        section_title=None,
        description='The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure.',
    ),
    'email': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Email address for completion summary.',
    ),
    'multiqc_title': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='MultiQC report title. Printed as page header, used for filename if not otherwise specified.',
    ),
    'fasta': NextflowParameter(
        type=str,
        default=None,
        section_title='Database Options',
        description='Input FASTA protein database',
    ),
    'skip_decoy_generation': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Add this parameter when you want to skip the generation of the decoy database.',
    ),
    'run_centroidisation': NextflowParameter(
        type=typing.Optional[bool],
        default=False,
        section_title='Spectrum preprocessing',
        description='Include the flag when the specified ms level is not centroided (default=false). ',
    ),
    'pick_ms_levels': NextflowParameter(
        type=typing.Optional[int],
        default=2,
        section_title=None,
        description='Specify the MS levels for which the peak picking is applied (unless you use `--run_centroidisation`).',
    ),
    'filter_mzml': NextflowParameter(
        type=typing.Optional[bool],
        default=False,
        section_title=None,
        description='Clean up spectrum files and remove artificial charge 0 peptides.',
    ),
    'activation_method': NextflowParameter(
        type=typing.Optional[str],
        default='ALL',
        section_title='Database Search Settings',
        description='Specify which fragmentation method was used in the MS acquisition',
    ),
    'digest_mass_range': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Specify the mass range in Dalton that peptides should fulfill to be considered for peptide spectrum matching.',
    ),
    'prec_charge': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Specify the precursor charge range that peptides should fulfill to be considered for peptide spectrum matching.',
    ),
    'precursor_mass_tolerance': NextflowParameter(
        type=typing.Optional[int],
        default=5,
        section_title=None,
        description='Specify the precursor mass tolerance to be used for the Comet database search.',
    ),
    'precursor_error_units': NextflowParameter(
        type=typing.Optional[str],
        default='ppm',
        section_title=None,
        description='Specify the unit of the precursor mass tolerance to be used for the Comet database search.',
    ),
    'fragment_mass_tolerance': NextflowParameter(
        type=typing.Optional[float],
        default=0.01,
        section_title=None,
        description='Specify the fragment mass tolerance to be used for the comet database search.',
    ),
    'number_mods': NextflowParameter(
        type=typing.Optional[int],
        default=3,
        section_title=None,
        description='Specify the maximum number of modifications that should be contained in a peptide sequence match.',
    ),
    'fixed_mods': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Specify which fixed modifications should be applied to the database search',
    ),
    'variable_mods': NextflowParameter(
        type=typing.Optional[str],
        default='Oxidation (M)',
        section_title=None,
        description='Specify which variable modifications should be applied to the database search',
    ),
    'num_hits': NextflowParameter(
        type=typing.Optional[int],
        default=1,
        section_title=None,
        description='Specify the number of hits that should be reported for each spectrum.',
    ),
    'use_x_ions': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Include x ions into the peptide spectrum matching',
    ),
    'use_z_ions': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Include z ions into the peptide spectrum matching',
    ),
    'use_a_ions': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Include a ions into the peptide spectrum matching',
    ),
    'use_c_ions': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Include c ions into the peptide spectrum matching',
    ),
    'use_NL_ions': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Include NL ions into the peptide spectrum matching',
    ),
    'remove_precursor_peak': NextflowParameter(
        type=typing.Optional[bool],
        default=False,
        section_title=None,
        description='Include if you want to remove all peaks around precursor m/z',
    ),
    'rescoring_engine': NextflowParameter(
        type=typing.Optional[str],
        default='percolator',
        section_title='Rescoring settings',
        description='Specify the rescoring engine that should be used for rescoring. Either percolator or mokapot',
    ),
    'feature_generators': NextflowParameter(
        type=typing.Optional[str],
        default='deeplc,ms2pip',
        section_title=None,
        description='Specify the feature generator that should be used for rescoring. One or multiple of basic,ms2pip,deeplc,ionmob',
    ),
    'ms2pip_model': NextflowParameter(
        type=typing.Optional[str],
        default='Immuno-HCD',
        section_title=None,
        description='Specify the MS²PIP model that should be used for rescoring. Checkout the MS²PIP documentation for available models.',
    ),
    'fdr_level': NextflowParameter(
        type=typing.Optional[str],
        default='peptide_level_fdrs',
        section_title=None,
        description='Specify the level at which the false discovery rate should be computed.',
    ),
    'fdr_threshold': NextflowParameter(
        type=typing.Optional[float],
        default=0.01,
        section_title=None,
        description='Specify the false discovery rate threshold at which peptide hits should be selected.',
    ),
    'quantify': NextflowParameter(
        type=typing.Optional[bool],
        default=False,
        section_title='Quantification Options',
        description='Turn on quantification mode',
    ),
    'max_rt_alignment_shift': NextflowParameter(
        type=typing.Optional[int],
        default=300,
        section_title=None,
        description='Set a maximum retention time shift for the linear RT alignment',
    ),
    'peptide_min_length': NextflowParameter(
        type=typing.Optional[int],
        default=8,
        section_title='Post Processing',
        description='Specify the minimum length of peptides to be considered after processing',
    ),
    'peptide_max_length': NextflowParameter(
        type=typing.Optional[int],
        default=12,
        section_title=None,
        description='Specify the maximum length of peptides to be considered after processing',
    ),
    'annotate_ions': NextflowParameter(
        type=typing.Optional[bool],
        default=False,
        section_title=None,
        description='Create tsv files containing information about the MS2 ion annotations after processing.',
    ),
    'multiqc_methods_description': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title='Generic options',
        description='Custom MultiQC yaml file containing HTML including a methods description.',
    ),
}


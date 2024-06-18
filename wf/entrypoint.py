from dataclasses import dataclass
from enum import Enum
import os
import subprocess
import requests
import shutil
from pathlib import Path
import typing
import typing_extensions

from latch.resources.workflow import workflow
from latch.resources.tasks import nextflow_runtime_task, custom_task
from latch.types.file import LatchFile
from latch.types.directory import LatchDir, LatchOutputDir
from latch.ldata.path import LPath
from latch_cli.nextflow.workflow import get_flag
from latch_cli.nextflow.utils import _get_execution_name
from latch_cli.utils import urljoins
from latch.types import metadata
from flytekit.core.annotation import FlyteAnnotation

from latch_cli.services.register.utils import import_module_by_path

meta = Path("latch_metadata") / "__init__.py"
import_module_by_path(meta)
import latch_metadata

@custom_task(cpu=0.25, memory=0.5, storage_gib=1)
def initialize() -> str:
    token = os.environ.get("FLYTE_INTERNAL_EXECUTION_ID")
    if token is None:
        raise RuntimeError("failed to get execution token")

    headers = {"Authorization": f"Latch-Execution-Token {token}"}

    print("Provisioning shared storage volume... ", end="")
    resp = requests.post(
        "http://nf-dispatcher-service.flyte.svc.cluster.local/provision-storage",
        headers=headers,
        json={
            "storage_gib": 100,
        }
    )
    resp.raise_for_status()
    print("Done.")

    return resp.json()["name"]






@nextflow_runtime_task(cpu=4, memory=8, storage_gib=100)
def nextflow_runtime(pvc_name: str, input: LatchFile, outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})], email: typing.Optional[str], multiqc_title: typing.Optional[str], fasta: str, skip_decoy_generation: typing.Optional[bool], digest_mass_range: typing.Optional[str], prec_charge: typing.Optional[str], fixed_mods: typing.Optional[str], use_x_ions: typing.Optional[bool], use_z_ions: typing.Optional[bool], use_a_ions: typing.Optional[bool], use_c_ions: typing.Optional[bool], use_NL_ions: typing.Optional[bool], multiqc_methods_description: typing.Optional[str], run_centroidisation: typing.Optional[bool], pick_ms_levels: typing.Optional[int], filter_mzml: typing.Optional[bool], activation_method: typing.Optional[str], precursor_mass_tolerance: typing.Optional[int], precursor_error_units: typing.Optional[str], fragment_mass_tolerance: typing.Optional[float], number_mods: typing.Optional[int], variable_mods: typing.Optional[str], num_hits: typing.Optional[int], remove_precursor_peak: typing.Optional[bool], rescoring_engine: typing.Optional[str], feature_generators: typing.Optional[str], ms2pip_model: typing.Optional[str], fdr_level: typing.Optional[str], fdr_threshold: typing.Optional[float], quantify: typing.Optional[bool], max_rt_alignment_shift: typing.Optional[int], peptide_min_length: typing.Optional[int], peptide_max_length: typing.Optional[int], annotate_ions: typing.Optional[bool]) -> None:
    try:
        shared_dir = Path("/nf-workdir")



        ignore_list = [
            "latch",
            ".latch",
            "nextflow",
            ".nextflow",
            "work",
            "results",
            "miniconda",
            "anaconda3",
            "mambaforge",
        ]

        shutil.copytree(
            Path("/root"),
            shared_dir,
            ignore=lambda src, names: ignore_list,
            ignore_dangling_symlinks=True,
            dirs_exist_ok=True,
        )

        cmd = [
            "/root/nextflow",
            "run",
            str(shared_dir / "main.nf"),
            "-work-dir",
            str(shared_dir),
            "-profile",
            "docker",
            "-c",
            "latch.config",
                *get_flag('input', input),
                *get_flag('outdir', outdir),
                *get_flag('email', email),
                *get_flag('multiqc_title', multiqc_title),
                *get_flag('fasta', fasta),
                *get_flag('skip_decoy_generation', skip_decoy_generation),
                *get_flag('run_centroidisation', run_centroidisation),
                *get_flag('pick_ms_levels', pick_ms_levels),
                *get_flag('filter_mzml', filter_mzml),
                *get_flag('activation_method', activation_method),
                *get_flag('digest_mass_range', digest_mass_range),
                *get_flag('prec_charge', prec_charge),
                *get_flag('precursor_mass_tolerance', precursor_mass_tolerance),
                *get_flag('precursor_error_units', precursor_error_units),
                *get_flag('fragment_mass_tolerance', fragment_mass_tolerance),
                *get_flag('number_mods', number_mods),
                *get_flag('fixed_mods', fixed_mods),
                *get_flag('variable_mods', variable_mods),
                *get_flag('num_hits', num_hits),
                *get_flag('use_x_ions', use_x_ions),
                *get_flag('use_z_ions', use_z_ions),
                *get_flag('use_a_ions', use_a_ions),
                *get_flag('use_c_ions', use_c_ions),
                *get_flag('use_NL_ions', use_NL_ions),
                *get_flag('remove_precursor_peak', remove_precursor_peak),
                *get_flag('rescoring_engine', rescoring_engine),
                *get_flag('feature_generators', feature_generators),
                *get_flag('ms2pip_model', ms2pip_model),
                *get_flag('fdr_level', fdr_level),
                *get_flag('fdr_threshold', fdr_threshold),
                *get_flag('quantify', quantify),
                *get_flag('max_rt_alignment_shift', max_rt_alignment_shift),
                *get_flag('peptide_min_length', peptide_min_length),
                *get_flag('peptide_max_length', peptide_max_length),
                *get_flag('annotate_ions', annotate_ions),
                *get_flag('multiqc_methods_description', multiqc_methods_description)
        ]

        print("Launching Nextflow Runtime")
        print(' '.join(cmd))
        print(flush=True)

        env = {
            **os.environ,
            "NXF_HOME": "/root/.nextflow",
            "NXF_OPTS": "-Xms2048M -Xmx8G -XX:ActiveProcessorCount=4",
            "K8S_STORAGE_CLAIM_NAME": pvc_name,
            "NXF_DISABLE_CHECK_LATEST": "true",
        }
        subprocess.run(
            cmd,
            env=env,
            check=True,
            cwd=str(shared_dir),
        )
    finally:
        print()

        nextflow_log = shared_dir / ".nextflow.log"
        if nextflow_log.exists():
            name = _get_execution_name()
            if name is None:
                print("Skipping logs upload, failed to get execution name")
            else:
                remote = LPath(urljoins("latch:///your_log_dir/nf_nf_core_mhcquant", name, "nextflow.log"))
                print(f"Uploading .nextflow.log to {remote.path}")
                remote.upload_from(nextflow_log)



@workflow(metadata._nextflow_metadata)
def nf_nf_core_mhcquant(input: LatchFile, outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})], email: typing.Optional[str], multiqc_title: typing.Optional[str], fasta: str, skip_decoy_generation: typing.Optional[bool], digest_mass_range: typing.Optional[str], prec_charge: typing.Optional[str], fixed_mods: typing.Optional[str], use_x_ions: typing.Optional[bool], use_z_ions: typing.Optional[bool], use_a_ions: typing.Optional[bool], use_c_ions: typing.Optional[bool], use_NL_ions: typing.Optional[bool], multiqc_methods_description: typing.Optional[str], run_centroidisation: typing.Optional[bool] = False, pick_ms_levels: typing.Optional[int] = 2, filter_mzml: typing.Optional[bool] = False, activation_method: typing.Optional[str] = 'ALL', precursor_mass_tolerance: typing.Optional[int] = 5, precursor_error_units: typing.Optional[str] = 'ppm', fragment_mass_tolerance: typing.Optional[float] = 0.01, number_mods: typing.Optional[int] = 3, variable_mods: typing.Optional[str] = 'Oxidation (M)', num_hits: typing.Optional[int] = 1, remove_precursor_peak: typing.Optional[bool] = False, rescoring_engine: typing.Optional[str] = 'percolator', feature_generators: typing.Optional[str] = 'deeplc,ms2pip', ms2pip_model: typing.Optional[str] = 'Immuno-HCD', fdr_level: typing.Optional[str] = 'peptide_level_fdrs', fdr_threshold: typing.Optional[float] = 0.01, quantify: typing.Optional[bool] = False, max_rt_alignment_shift: typing.Optional[int] = 300, peptide_min_length: typing.Optional[int] = 8, peptide_max_length: typing.Optional[int] = 12, annotate_ions: typing.Optional[bool] = False) -> None:
    """
    nf-core/mhcquant

    Sample Description
    """

    pvc_name: str = initialize()
    nextflow_runtime(pvc_name=pvc_name, input=input, outdir=outdir, email=email, multiqc_title=multiqc_title, fasta=fasta, skip_decoy_generation=skip_decoy_generation, run_centroidisation=run_centroidisation, pick_ms_levels=pick_ms_levels, filter_mzml=filter_mzml, activation_method=activation_method, digest_mass_range=digest_mass_range, prec_charge=prec_charge, precursor_mass_tolerance=precursor_mass_tolerance, precursor_error_units=precursor_error_units, fragment_mass_tolerance=fragment_mass_tolerance, number_mods=number_mods, fixed_mods=fixed_mods, variable_mods=variable_mods, num_hits=num_hits, use_x_ions=use_x_ions, use_z_ions=use_z_ions, use_a_ions=use_a_ions, use_c_ions=use_c_ions, use_NL_ions=use_NL_ions, remove_precursor_peak=remove_precursor_peak, rescoring_engine=rescoring_engine, feature_generators=feature_generators, ms2pip_model=ms2pip_model, fdr_level=fdr_level, fdr_threshold=fdr_threshold, quantify=quantify, max_rt_alignment_shift=max_rt_alignment_shift, peptide_min_length=peptide_min_length, peptide_max_length=peptide_max_length, annotate_ions=annotate_ions, multiqc_methods_description=multiqc_methods_description)


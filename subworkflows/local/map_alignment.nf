/*
 * Perform the quantification of the samples when the parameter --skip_quantification is not provided
 */

include { OPENMS_FALSEDISCOVERYRATE }                                       from '../../modules/local/openms_falsediscoveryrate'
include { OPENMS_IDFILTER as OPENMS_IDFILTER_FOR_ALIGNMENT }                from '../../modules/local/openms_idfilter'
include { OPENMS_MAPALIGNERIDENTIFICATION }                                 from '../../modules/local/openms_mapaligneridentification'
include {
    OPENMS_MAPRTTRANSFORMER as OPENMS_MAPRTTRANSFORMERMZML
    OPENMS_MAPRTTRANSFORMER as OPENMS_MAPRTTRANSFORMERIDXML }               from '../../modules/local/openms_maprttransformer'


workflow MAP_ALIGNMENT {
    take:
        indexed_hits
        mzml_files

    main:

        mzml_files.toList().size().view()
        ch_versions = Channel.empty()
        // Calculate fdr for id based alignment
        OPENMS_FALSEDISCOVERYRATE(indexed_hits)
        ch_versions = ch_versions.mix(OPENMS_FALSEDISCOVERYRATE.out.versions.first().ifEmpty(null))
        // Filter fdr for id based alignment
        OPENMS_IDFILTER_FOR_ALIGNMENT(OPENMS_FALSEDISCOVERYRATE.out.idxml
                                        .flatMap { it -> [tuple(it[0], it[1], null)]})
        ch_versions = ch_versions.mix(OPENMS_IDFILTER_FOR_ALIGNMENT.out.versions.first().ifEmpty(null))

        // Group samples together if they are replicates
        ch_grouped_fdr_filtered = OPENMS_IDFILTER_FOR_ALIGNMENT.out.idxml
            .map {
                meta, raw ->
                    [[id:meta.sample + "_" + meta.condition, sample:meta.sample, condition:meta.condition, ext:meta.ext], raw]
                }
            .groupTuple(by: [0])
        // Compute alignment rt transformation
        OPENMS_MAPALIGNERIDENTIFICATION(ch_grouped_fdr_filtered)
        ch_versions = ch_versions.mix(OPENMS_MAPALIGNERIDENTIFICATION.out.versions.first().ifEmpty(null))
        // Intermediate step to join RT transformation files with mzml and idxml channels

        // TODO: somehow, there are files lost during the analyses
        // 605 -> 582 -> 590

        OPENMS_MAPALIGNERIDENTIFICATION.out.trafoxml
        .transpose()
        .flatMap {
            meta, trafoxml ->
                ident = trafoxml.baseName.split('_-_')[0]
                [[[id:ident, sample:meta.sample, condition:meta.condition, ext:meta.ext], trafoxml]]
        }.toList().size().view()

        mzml_files
        .join(
            OPENMS_MAPALIGNERIDENTIFICATION.out.trafoxml
                .transpose()
                .flatMap {
                    meta, trafoxml ->
                        ident = trafoxml.baseName.split('_-_')[0]
                        [[[id:ident, sample:meta.sample, condition:meta.condition, ext:meta.ext], trafoxml]]
                }, by: [0] )
        .set { joined_trafos_mzmls }

        joined_trafos_mzmls.toList().size().view()

        indexed_hits
        .join(
            OPENMS_MAPALIGNERIDENTIFICATION.out.trafoxml
                .transpose()
                .flatMap {
                    meta, trafoxml ->
                        ident = trafoxml.baseName.split('_-_')[0]
                        [[[id:ident, sample:meta.sample, condition:meta.condition, ext:meta.ext], trafoxml]]
                })
        .set { joined_trafos_ids }

        // Align mzML files using trafoXMLs
        OPENMS_MAPRTTRANSFORMERMZML(joined_trafos_mzmls)
        ch_versions = ch_versions.mix(OPENMS_MAPRTTRANSFORMERMZML.out.versions.first().ifEmpty(null))
        // Align unfiltered idXMLfiles using trafoXMLs
        OPENMS_MAPRTTRANSFORMERIDXML(joined_trafos_ids)
        ch_versions = ch_versions.mix(OPENMS_MAPRTTRANSFORMERIDXML.out.versions.first().ifEmpty(null))
        ch_proceeding_idx = OPENMS_MAPRTTRANSFORMERIDXML.out.aligned
            .map {
                meta, raw ->
                [[id:meta.sample + "_" + meta.condition, sample:meta.sample, condition:meta.condition, ext:meta.ext], raw]
            }
            .groupTuple(by: [0])

    emit:
        // Define the information that is returned by this workflow
        versions = ch_versions
        ch_proceeding_idx
        aligned_idfilter = OPENMS_IDFILTER_FOR_ALIGNMENT.out.idxml
        aligned_mzml = OPENMS_MAPRTTRANSFORMERMZML.out.aligned
}

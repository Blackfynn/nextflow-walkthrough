#!/usr/bin/env nextflow

process split_slide {
    container = "blackfynn/vips"

    input:
    file(image) from file("./pathology-slide.svs")

    output:
    file "*.jpeg" into tiles mode flatten

    script:
    """
    vips dzsave $image slide

    DIR=\$(ls slide_files/ | sort -n | tail -1)
    mv slide_files/\$DIR/* .
    """
}

process cell_detection {
    container = "cell-detection"

    input:
    file(tile) from tiles

    output:
    file "*_binary.jpeg" into binary_files

    script:
    """
    python /app/cell_detection.py $tile .
    """
}

process rejoin_tiles {
    container = "blackfynn/vips"

    input:
    file "*.jpeg" from binary_files.collect()

    script:
    """
    vips arrayjoin "`echo *.jpeg`" output.jpeg --across 9
    """
}

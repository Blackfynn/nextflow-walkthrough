# Simple Cell Detection with Docker, Nextflow, and AWS Batch

## About
This repository contains code for a walkthrough of a simple computational pipeline for cell-detection using [Nextflow](https://www.nextflow.io/), [Docker](https://www.docker.com/), and [AWS Batch](https://aws.amazon.com/batch/)

## Getting Started

In order to get started you'll need to have the following installed:

* [Java 8 or higher](http://www.oracle.com/technetwork/java/javase/downloads/index.html)
* [Nextflow](https://www.nextflow.io/docs/latest/getstarted.html#installation)
* [Docker](https://docs.docker.com/install/) (if running on MacOSX [Docker For Mac](https://www.docker.com/docker-mac) is recommended)

#### Optional (for running the pipeline in AWS Batch)
* [AWS Account](https://aws.amazon.com/account/)
* [AWS credentials](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html) setup locally
* [AWS Command-line interface (CLI)](https://aws.amazon.com/cli/)

## Cell Detection with Docker

Once you have Docker installed you'll need two Docker images, one to run [VIPS](http://jcupitt.github.io/libvips/API/current/) and the other, a Python image with [SciPy](https://www.scipy.org/) and [Pillow](http://python-pillow.org/) and build a Docker image for performing cell detection using the provided script:

```
$ docker pull blackfynn/vips
$ docker pull blackfynn/python3.6-scipy-pillow
$ cd cell-detection-image && docker build -t cell-detection . && cd -
```

First we'll need to segment the original image into tiles. To do so we'll mount the original pathology image into our VIPS Docker image and use the `vips dsave` command as follows:

```
$ docker run -it -v $PWD/pathology-slide.svs:/input/pathology-slide.svs -v $PWD/output:/output blackfynn/vips vips dzsave /input/pathology-slide.svs /output/slide
```

This will save the output of the `vips dsave` command to a local `output/slide_files/` directory.

Next we'll use the largest segementation of tiles as input to our simple cell-detection algorithm:

```
ls $PWD/output/slide_files/ | sort -n | tail -1 | xargs -I {} docker run -v $PWD/output/slide_files/{}/:/input -v $PWD/output/binary_data/:/output cell-detection python /app/cell_detection.py /input /output
```

Finally we'll reconstruct the image from the binary output of our cell detection algorithm using our VIPS image and the command `vips arrayjoin`:

```
docker run -v $PWD/output/binary_data/:/input/ -v $PWD/output/:/output/ blackfynn/vips bash -c 'vips arrayjoin "$(echo /input/*.jpeg)" /output/output.jpeg --across 9'
```

You should now have a file `output/output.jpeg` that represents a black and white rendering of the original image with the detected cells marked in black!


## Cell Detection with Nextflow (local)
Now we'll take the same computational pipeline above, and use Nextflow's data-driven language to write a workflow to execute each step for us, including fanning out to run the cell-detection algorithm on individual tiles in parallel.

First, we'll need to enable Docker execution for Nextflow. To do this, notice the following line has been added to the top of the `nextflow.config` file.

```
docker.enabled = true
```

The Nextflow computational workflow has already been written to the file `cell_detection.nf`.

In that file, you'll notice the three steps from above broken into seperate processes. To perform the tiling segmentation we use the following process definition to define our inputs and outputs and run the `vips dsave` command (as above)

```
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
```

We can then perform parallel computation on each of the generated tiles with our cell detection algorithm using the following process definition:

```
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
```

Finally, we can collect the results from the parallel computation and reconstruct the image with the VIPS Docker image and the `vips arrayjoin` command

```
process rejoin_tiles {
    container = "blackfynn/vips"

    input:
    file "*.jpeg" from binary_files.collect()

    script:
    """
    vips arrayjoin "`echo *.jpeg`" output.jpeg --across 9
    """
}
```
## Cell Detection with Nextflow (AWS Batch)

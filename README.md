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
$ docker run -it -v $PWD/pathology-slide.svs:/input/pathology-slide.svs -v $PWD/output:/output blackfynn/etl-vips vips dzsave /input/pathology-slide.svs /output/slide
```

This will save the output of the `vips dsave` command to a local `output/slide_files/` directory.

Next we'll use the largest segementation of tiles as input to our simple cell-detection algorithm:

```
ls $PWD/output/slide_files/ | sort -n | tail -1 | xargs -I {} docker run -v $PWD/output/slide_files/{}/:/input -v $PWD/output/binary-data/:/output cell-detection python /app/cell_detection.py /input /output
```

Finally we'll reconstruct the image from the binary output of our cell detection algorithm using our VIPS image and the command `vips arrayjoin`:

```
docker run -v $PWD/output/binary/:/input/ -v $PWD/output/:/output/ blackfynn/etl-vips bash -c 'vips arrayjoin "$(echo /input/*.jpeg)" /output/output.jpeg --across 9'
```

You should now have a file `output/output.jpeg` that represents a black and white rendering of the original image with the detected cells marked in black!


## Cell Detection with Nextflow (local)


## Cell Detection with Nextflow (AWS Batch)

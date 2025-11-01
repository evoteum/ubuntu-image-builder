[//]: # (STANDARD README)
[//]: # (https://github.com/RichardLitt/standard-readme)
[//]: # (----------------------------------------------)
[//]: # (Uncomment optional sections as required)
[//]: # (----------------------------------------------)

[//]: # (Title)
[//]: # (Match repository name)
[//]: # (REQUIRED)

# ubuntu-image-builder

[//]: # (Banner)
[//]: # (OPTIONAL)
[//]: # (Must not have its own title)
[//]: # (Must link to local image in current repository)


[//]: # (Badges)
[//]: # (OPTIONAL)
[//]: # (Must not have its own title)


[//]: # (Short description)
[//]: # (REQUIRED)
[//]: # (An overview of the intentions of this repo)
[//]: # (Must not have its own title)
[//]: # (Must be less than 120 characters)
[//]: # (Must match GitHub's description)

Builds custom Ubuntu images with ubuntu-image and Python tooling

[//]: # (Long Description)
[//]: # (OPTIONAL)
[//]: # (Must not have its own title)
[//]: # (A detailed description of the repo)

Generates custom cloud-init configurations from YAML templates, then uses https://github.com/canonical/ubuntu-image to
build unique images for each Ubuntu server.


## Table of Contents

[//]: # (REQUIRED)
[//]: # (Delete as appropriate)

1. [Security](#security)
1. [Background](#background)
1. [Install](#install)
1. [Usage](#usage)
1. [Any extra sections as required]
1. [Documentation](#documentation)
1. [Repository Configuration](#repository-configuration)
1. [API](#api)
1. [Maintainers](#maintainers)
1. [Thanks](#thanks)
1. [Contributing](#contributing)
1. [License](#license)

## Security
[//]: # (OPTIONAL)
[//]: # (May go here if it is important to highlight security concerns.)

`ubuntu-image`
[requires root privileges](https://github.com/canonical/ubuntu-image#:~:text=run%20it%20with%20root%20privileges), so
`USER root` is intentionally included in the Containerfile.

## Background
[//]: # (OPTIONAL)
[//]: # (Explain the motivation and abstract dependencies for this repo)

Since we run hardware nodes, we cannot escape some level of "metal pets". We have, however, aimed to make nodes as
expendable and rebuildable as possible.

Although NixOS provides a delightful level of repeatability, it still suffers from the first boot problem; you need to
tell it what hostname and IP address to operate on at first boot, before a flake has had a chance to run.

Additionally, Ubuntu is still the most popular server distro across the industry, so we chose to stick with Ubuntu.

This reads the metal config from [estate-config/metal/config.yaml](https://github.com/evoteum/estate-config/blob/69096ce1533c2a27d0acf961158f09885acc0f5a/metal/config.yaml)

## Install

[//]: # (Explain how to install the thing.)
[//]: # (OPTIONAL IF documentation repo)
[//]: # (ELSE REQUIRED)

Nothing to install, just pull the container.


## Usage
[//]: # (REQUIRED)
[//]: # (Explain what the thing does. Use screenshots and/or videos.)


### 0. Ensure config is correct

Check [estate-config/metal/config.yaml](https://github.com/evoteum/estate-config/blob/69096ce1533c2a27d0acf961158f09885acc0f5a/metal/config.yaml)
to ensure that,
- your username is correct
- your public ssh key is correct
- the host(s) you need to image are present and correct.

### 1. Building Operating System Images

To build all images, run

```shell
podman run --rm -it \
  -v "$PWD/estate-config/metal/config.yaml:/workspace/config.yaml" \
  -v "$PWD/templates:/workspace/templates" \
  -v "$PWD/output:/workspace/output" \
  ubuntu-image-builder \
  --config /workspace/config.yaml --dry-run --fleet lab
```



To build a single image,
- note the ID of the node you wish to rebuild.
- ensure its entry in [ubuntu-image/config.yaml](ubuntu-image/build_images.py) is correct.
- run `python3 ubuntu-image/build_images.py --id [node id]`

### 2. Get the image on to the box

How you do this will depend on the model of the node. For example, if it is a Raspberry Pi, you can use the Raspberry Pi
Imager to flash the NVMe drive.

### 3. Rack the box

Because we are not animals.


[//]: # (Extra sections)
[//]: # (OPTIONAL)
[//]: # (This should not be called "Extra Sections".)
[//]: # (This is a space for ≥0 sections to be included,)
[//]: # (each of which must have their own titles.)



## Documentation

Further documentation is in the [`docs`](docs/) directory.

## Repository Configuration

> [!WARNING]  
> This repo is controlled by OpenTofu in the [estate-repos](https://github.com/evoteum/estate-repos) repository.  
>  
> Manual configuration changes will be overwritten the next time OpenTofu runs.


[//]: # (## API)
[//]: # (OPTIONAL)
[//]: # (Describe exported functions and objects)



[//]: # (## Maintainers)
[//]: # (OPTIONAL)
[//]: # (List maintainers for this repository)
[//]: # (along with one way of contacting them - GitHub link or email.)



[//]: # (## Thanks)
[//]: # (OPTIONAL)
[//]: # (State anyone or anything that significantly)
[//]: # (helped with the development of this project)



## Contributing
[//]: # (REQUIRED)
If you need any help, please log an issue and one of our team will get back to you.

PRs are welcome.


## License
[//]: # (REQUIRED)

### Code

All source code in this repository is licenced under the [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.en.html). A copy of this is provided in the [LICENSE](LICENSE).

### Non-code content

All non-code content in this repository, including but not limited to images, diagrams or prose documentation, is licenced under the [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/) licence.

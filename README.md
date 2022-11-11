# Welcome to LCBDtools

[Read the Docs](https://lcbdpreprocessing.readthedocs.io/en/latest/)

LCBDtools is the central code repository for all neuroimaging and related code, written by Clayton Schneider. The purpose of this toolbox is to automate, streamline, and advance the analytics techniques used by the Laboratory for Child Brain Development. Its usage relies heavily on the LCBD compute platforms described on the [LCBD Wiki](https://childbrainlab.github.io).

## Scripts
Scripts is the main user-facing branch of this code repository, and is split into 3 main categories:

- Behavioral analysis (Beh)
- functional near-infrared spectroscopy (NIRS)
- magnetic resonance imaging (MRI)

In each of these sub-folders, a combination of bash and Python scripts can be found which handle various processes, as well as a "notebooks" folder where applicable, containing IPython code designed to be used modularly with confugration variables throughout.

## Stimuli
The 'Stimuli' module coontains code for processing various LCBD experimental task data, usually implemented in Psychopy. E.g., the source code for the Flanker object and its TaskReader are contained there. These are not scripts, meant to be executed, but code which contains classes designed to generate data objects with details about stimuli, evaluating metrics such as flanker accuracy and IES, and synchronizing the timing of NIRStar systems and Psychopy output files.

## Src
The 'Src' module is also a source module containing various classes to aid in statistical analysis, especially that of time-series signal analysis. The TimeSeries class is used for analyzing NIRS data, processing the output of continuous-rating tasks such as ATV / Free-Viewing, etc.

## WUSTL-Snyder
This module is a direct copy of Avi Snyder's neuroimaging code from the WUSTL server, stored alongside the toolbox in case it needs to be referenced or accessed by any of our modules. 

## docs
Docs for this toolbox are automatically generated using [Sphinx-RTD](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/build-the-docs.html), and hosted [here](https://lcbdpreprocessing.readthedocs.io/en/latest/).

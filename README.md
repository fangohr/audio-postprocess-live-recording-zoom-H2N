[![CI](https://github.com/fangohr/audio-postprocess-live-recording-zoom-H2N/actions/workflows/ci.yaml/badge.svg)](https://github.com/fangohr/audio-postprocess-live-recording-zoom-H2N/actions/workflows/ci.yaml)

# Polishing of live recordings

## Installation

clone this repository, for example

```console
git clone https://github.com/fangohr/audio-postprocess-live-recording-zoom-h2n.git
```


Then create an environment in which this package is installed and the relevant script can be executed. (You need to install pixi.sh first.):

```
cd audio-postprocess-live-recording-zoom-h2n
pixi shell
```

## Usage

```console
audio-postprocess-live-recording input.mp3
```
to create `processed-input.mp3`.

Or define the prefix (which defaults to `processed-`):
```console
audio-postprocess-live-recording song.mp3 --prefix 2025-10-09-
```
so that the processed version of `song.mp3` is stored as `2025-10-09-song.mp3`.

More than one filename can be provided, for example
```console
audio-postprocess-live-recording song1.mp3 song2.mp3 --prefix 2025-10-09-
```

## More information: context, design and implementation

Scenario: 
- band rehearsal in small room
- recorded with [Zoom H2N](https://zoomcorp.com/en/de/handheld-recorders/handheld-recorders/h2n-handy-recorder/)
- want to improve sound quality 

Input:
- taken recording as mp3
- ask Logic Pro to run Mastering Assistant over it. This, roughly, recommends to 
  - boost frequencies between 20 and 100 Hz by 5 db
  - reduce frequences between 100 and 500 Hz 5 db
  
Implementation:
- use this EQ recommendation in the attached script
- additionnally:
  - high pass filter at the beginning to reduce rumble (20Hz)
  - normalise recording to have somewhat standard amplitude
  - if desired, push low frequences a bit further (probably mostly making up for poor speakers: at rehearsal time and when listening)
- Details are in [src/audio_postprocess_live_recording_zoom_h2n/cli.py](src/audio_postprocess_live_recording_zoom_h2n/cli.py) and can be modified according to taste.

## Visualising effect of the applied filters

The command `audio-postprocess-frequency-plot` shows a spectrum which indicates which frequences are boosted and reduced.

Details:
- 10 seconds of white noise are generated
- the file is processed as if it was a recording
- a plot is created showing the white noise spectrum (power as function of frequency) together with the spectrum of the processed white noise. 
- as the white noise data is (effectively) effectively a flat line as a function of frequency, the changes can be seen somewhat easily.

----

## Ideas for additional features

- debug option to save a number of mp3s, each with only one filter applied (or have cumulative use of filters)
- logging of parameters:
  - together with the processed files, save the parameters given to ffmpeg (i.e. the dictionaries for each effect) in some log file format. This would help to reproduce the post processing as it would record the chosen parameters.
  - if this is implemented, the script should also be able to read this log file format.

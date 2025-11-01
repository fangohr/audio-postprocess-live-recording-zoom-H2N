import argparse
import os

import ffmpeg

# Use ffmpeg's audio filters to post-process Zoom H2N records
#
# Documentation: https://ffmpeg.org/ffmpeg-filters.html#Audio-Filters


def process_file(in_file: str, out_file: str):
    stream = ffmpeg.input(in_file)

    # High-pass filter to remove sub-bass rumble
    # ---- High-pass filter (30 Hz, ~12 dB/oct) ----
    highpass = {"f": 20, "t": "q", "width": 0.7}
    stream = ffmpeg.filter(stream, "highpass", **highpass)

    # EQ:
    # Suggestions from Logic Pro for Zoom H2N recordings:
    # 1) +4 dB boost centered at 75 Hz with Q=1.0 (covers roughly 50–100 Hz)
    # 2) -5 dB cut centered at 350 Hz with Q=1.0 (covers roughly 200–500 Hz)
    eq1 = {"f": 75, "t": "q", "w": 1.0, "g": 5}
    eq2 = {"f": 350, "t": "q", "w": 1.0, "g": -5}
    stream = ffmpeg.filter(stream, "equalizer", **eq1)
    stream = ffmpeg.filter(stream, "equalizer", **eq2)

    # could compress if needed
    # threshold -18 dBFS, ratio 3:1, moderate attack/release, a bit of makeup gain
    comp = {  # noqa: F841
        "threshold": "-18dB",
        "ratio": 3,
        "attack": 20,  # ms
        "release": 250,  # ms
        "makeup": 1,  # dB
    }

    # stream = ffmpeg.filter(stream, 'acompressor', **comp)

    # ---- Bass fattening (choose ONE or use both lightly) ----
    # Option A: Low-shelf boost (smooth, musical)
    low_shelf = {  # noqa: F841
        "g": 3.0,
        "f": 90,
        "t": "q",
        "w": 0.7,
    }  # +3 dB shelf below ~90 Hz  # noqa: F841

    # Option B: Focused bump around 100 Hz (adds punch)
    bass_bump = {  # noqa: F841
        "f": 100,
        "t": "q",
        "w": 1.0,
        "g": 3.0,
    }  # +3 dB @100 Hz, Q=1.0   # noqa: F841

    # ---- Pick ONE (or keep both with smaller gains) ----
    # A) Low-shelf boost (recommended starting point)
    stream = ffmpeg.filter(stream, "bass", **low_shelf)

    # B) Extra punch around 100 Hz (uncomment to add or replace the shelf)
    # stream = ffmpeg.filter(stream, 'equalizer', **bass_bump)

    # Loudness normalization (EBU R128)
    loudnorm = {
        "I": -14,  # target integrated loudness in LUFS (-16 normal,
                   # -14 spotify loudness)
        "TP": -1.5,  # true peak limit (dBFS)
        "LRA": 11,  # target loudness range
    }

    stream = ffmpeg.filter(stream, "loudnorm", **loudnorm)
    stream = ffmpeg.output(stream, out_file, acodec="libmp3lame", audio_bitrate="192k")

    # for debugging: run synchronishly and check output
    out, err = ffmpeg.run(
        stream, overwrite_output=True, capture_stdout=True, capture_stderr=True
    )
    # Can print output if desired:
    # Seems that all output goes to stderro by default, and stdout is empty.
    # print(err.decode())
    # print(out.decode())


def do_parse_arguments():
    parser = argparse.ArgumentParser(
        prog="audio-live-record-postprocess-file",
        description="Apply postprocessing (EQ, compression, normalization, etc.)" + \
            "to audio files.",
    )
    parser.add_argument(
        "--prefix",
        default="processed-",
        help="Prefix for output filenames (default: %(default)s)",
    )
    parser.add_argument(
        "filenames", nargs="+", help="List of input audio files to process"
    )

    args = parser.parse_args()

    # prefix = args.prefix
    # filenames = args.filenames

    return args


def audio_live_record_postprocess_file():
    args = do_parse_arguments()
    prefix = args.prefix
    filenames = args.filenames

    # Example: show what would be done
    for in_file in filenames:
        dirname, basename = os.path.split(in_file)
        out_file = os.path.join(dirname, prefix + basename)
        print(f"Processing {in_file} → {out_file}")
        process_file(in_file=in_file, out_file=out_file)

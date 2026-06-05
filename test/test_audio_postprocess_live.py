import pathlib
import pytest
import ffmpeg

from audio_postprocess_live_recording_zoom_h2n.cli import (
    do_parse_arguments,
    print_conversion_settings,
    process_file,
)


#
# @pytest.fixture
# def white_noise():
#
#     # 1 second white noise @ 44.1 kHz, mono
#     ffmpeg.input("anoisesrc=d=1:c=white:r=44100", f="lavfi") \
#           .filter("loudnorm", I=-14, TP=-1.5, LRA=11) \
#           .output("white_noise.mp3", acodec="libmp3lame", audio_bitrate="192k") \
#           .overwrite_output() \
#           .run(quiet=True)
#
# def test_process_file(white_noise):
#     output = pathlib.Path('processed.mp3')
#     assert not output.exists(),  "Test setup error: processed.mp3 already exists."
#
#     process_file(in_file="white_noise.mp3", out_file="processed.mp3")
#
#     assert output.exists(), "process_file() did not create output.mp3."
#
@pytest.fixture
def white_noise_file(tmp_path: pathlib.Path) -> pathlib.Path:
    """Create a temporary 1-second white_noise.mp3 file and return its path."""
    inpath = tmp_path / "white_noise.mp3"

    (
        ffmpeg.input("anoisesrc=d=1:c=white:r=44100", f="lavfi")
        .filter("loudnorm", I=-14, TP=-1.5, LRA=11)
        .output(str(inpath), acodec="libmp3lame", audio_bitrate="192k")
        .overwrite_output()
        .run(quiet=True)
    )

    # Make sure file really exists before returning
    assert inpath.exists(), "Fixture failed: white_noise.mp3 was not created."
    return inpath


def test_process_file(white_noise_file: pathlib.Path, tmp_path: pathlib.Path):
    """Ensure process_file() creates the expected output file."""
    output = tmp_path / "processed.mp3"
    print(f"Working in {tmp_path=}")

    # Confirm test starts clean
    assert not output.exists(), "Test setup error: processed.mp3 already exists."

    # Run the processing function
    process_file(in_file=str(white_noise_file), out_file=str(output))

    # Verify output created
    assert output.exists(), "process_file() did not create processed.mp3."

    # (Optional) sanity check: ensure file size > 0 bytes
    assert output.stat().st_size > 0, "Output file is empty."


def test_process_file_wav_output(
    white_noise_file: pathlib.Path, tmp_path: pathlib.Path
):
    """Ensure process_file() can create WAV output when requested."""
    output = tmp_path / "processed.wav"

    assert not output.exists(), "Test setup error: processed.wav already exists."

    process_file(
        in_file=str(white_noise_file), out_file=str(output), output_format="wav"
    )

    assert output.exists(), "process_file() did not create processed.wav."
    assert output.stat().st_size > 0, "WAV output file is empty."


@pytest.mark.parametrize("processing_switch", ["ebass", "loudness"])
def test_process_file_processing_modes(
    white_noise_file: pathlib.Path, tmp_path: pathlib.Path, processing_switch: str
):
    """Ensure each optional processing mode creates an MP3 output file."""
    output = tmp_path / f"processed-{processing_switch}.mp3"
    kwargs = {processing_switch: True}

    process_file(in_file=str(white_noise_file), out_file=str(output), **kwargs)

    assert output.exists(), f"{processing_switch} mode did not create output."
    assert output.stat().st_size > 0, f"{processing_switch} output is empty."


def test_parse_arguments_defaults_to_mp3():
    args = do_parse_arguments(["input.wav"])

    assert args.wav is False
    assert args.ebass is False
    assert args.loudness is False
    assert args.prefix == "processed-"
    assert args.filenames == ["input.wav"]


def test_parse_arguments_allows_wav():
    args = do_parse_arguments(["--wav", "input.wav"])

    assert args.wav is True
    assert args.filenames == ["input.wav"]


def test_parse_arguments_allows_ebass():
    args = do_parse_arguments(["--ebass", "input.wav"])

    assert args.ebass is True
    assert args.loudness is False
    assert args.filenames == ["input.wav"]


def test_parse_arguments_allows_loudness():
    args = do_parse_arguments(["--loudness", "input.wav"])

    assert args.ebass is False
    assert args.loudness is True
    assert args.filenames == ["input.wav"]


def test_print_conversion_settings(capsys):
    args = do_parse_arguments(["--ebass", "--loudness", "input.wav"])

    print_conversion_settings(args, "mp3")

    output = capsys.readouterr().out
    assert "Conversion settings:" in output
    assert "output format: mp3" in output
    assert "processing: ebass, loudness" in output

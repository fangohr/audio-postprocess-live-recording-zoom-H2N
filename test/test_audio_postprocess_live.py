import pathlib
import pytest
import ffmpeg

from audio_postprocess_live_recording_zoom_h2n.cli import process_file


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

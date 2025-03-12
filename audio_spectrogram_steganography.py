import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import cv2
import soundfile as sf
import os

def get_valid_file(prompt, file_type):
    """Prompt the user for a valid file path and check existence."""
    while True:
        file_path = input(prompt).strip()
        if os.path.isfile(file_path):
            return file_path
        print(f"Error: The specified {file_type} file does not exist. Try again.")

def embed_image_in_spectrogram(audio_file, image_file, output_audio, scale_factor=0.01, img_size=(256, 256)):
    """Embeds a grayscale image in the spectrogram of an audio file."""
    # Load the audio file
    y, sr = librosa.load(audio_file, sr=None)

    # Compute the spectrogram
    D = librosa.stft(y)
    magnitude, phase = np.abs(D), np.angle(D)

    # Load and resize the image
    img = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, img_size)

    # Normalize image (scaled to reduce impact on sound)
    img_normalized = (img / 255.0) * np.max(magnitude) * scale_factor

    # Embed the image into high frequencies (top-right of spectrogram)
    h, w = img.shape
    mag_h, mag_w = magnitude.shape
    top, left = mag_h - h, mag_w - w  # Position in the high-frequency region

    magnitude[top:, left:] += img_normalized  # Embed in a small high-frequency region

    # Reconstruct the audio
    modified_D = magnitude * np.exp(1j * phase)
    modified_y = librosa.istft(modified_D)

    # Save the modified audio
    sf.write(output_audio, modified_y, sr)
    print(f"\n Image successfully embedded in {output_audio} with minimal distortion.\n")

# Get file paths from user
audio_file = get_valid_file("Enter the path to the input audio file: ", "audio")
image_file = get_valid_file("Enter the path to the image file: ", "image")
output_audio = input("Enter the path for the output audio file: ").strip()

# Run the function
embed_image_in_spectrogram(audio_file, image_file, output_audio)

# Load audio for spectrogram display
audio, sample_rate = sf.read(output_audio)

# Convert to mono if stereo
if len(audio.shape) == 2:
    audio = audio.mean(axis=1)

# Plot Spectrogram
plt.figure(figsize=(10, 4))
plt.specgram(audio, Fs=sample_rate)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.title('Spectrogram with Embedded Image')
plt.colorbar(format='%+2.0f dB')
plt.show()
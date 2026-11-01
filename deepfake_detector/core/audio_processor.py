import numpy as np
from scipy.fft import fft, fftfreq


class AudioProcessor:

    def extract_audio_from_video(self, video_path: str):
        """OpenCV does not support audio extraction; returns None gracefully."""
        return None, None

    def analyze_frequency_spectrum(self, audio_data: np.ndarray, sample_rate: int) -> dict:
        if audio_data is None or len(audio_data) == 0:
            return {"low_freq_energy": 0, "high_freq_energy": 0, "freq_ratio": 0, "has_artifacts": False}

        N = len(audio_data)
        spectrum = np.abs(fft(audio_data))[:N // 2]
        freqs = fftfreq(N, 1 / sample_rate)[:N // 2]

        cutoff = sample_rate // 8
        low_mask = freqs < cutoff
        high_mask = freqs >= cutoff

        low_energy = float(np.sum(spectrum[low_mask] ** 2))
        high_energy = float(np.sum(spectrum[high_mask] ** 2))
        total = low_energy + high_energy + 1e-9
        freq_ratio = high_energy / total
        has_artifacts = freq_ratio > 0.6 or freq_ratio < 0.05

        return {
            "low_freq_energy": low_energy,
            "high_freq_energy": high_energy,
            "freq_ratio": round(freq_ratio, 4),
            "has_artifacts": has_artifacts,
        }

    def detect_audio_artifacts(self, audio_data: np.ndarray) -> dict:
        if audio_data is None or len(audio_data) == 0:
            return {"clipping": False, "silence_ratio": 0, "unnatural_periodicity": False}

        clipping = bool(np.mean(np.abs(audio_data) > 0.98) > 0.01)
        silence_ratio = float(np.mean(np.abs(audio_data) < 0.001))

        chunk = min(4096, len(audio_data))
        autocorr = np.correlate(audio_data[:chunk], audio_data[:chunk], mode="full")
        mid = len(autocorr) // 2
        side = autocorr[mid + 50: mid + chunk]
        unnatural_periodicity = bool(np.max(np.abs(side)) > 0.9 * autocorr[mid])

        return {
            "clipping": clipping,
            "silence_ratio": round(silence_ratio, 4),
            "unnatural_periodicity": unnatural_periodicity,
        }

    def get_audio_score(self, audio_data: np.ndarray, sample_rate: int) -> float:
        if audio_data is None:
            return 0.0

        freq_result = self.analyze_frequency_spectrum(audio_data, sample_rate)
        artifact_result = self.detect_audio_artifacts(audio_data)

        score = 0.0
        if freq_result["has_artifacts"]:
            score += 0.4
        if artifact_result["clipping"]:
            score += 0.2
        if artifact_result["unnatural_periodicity"]:
            score += 0.3
        if artifact_result["silence_ratio"] > 0.3:
            score += 0.1

        return min(1.0, score)
